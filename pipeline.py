"""The daily run, in four steps: load -> forecast -> rules -> alert.

Airflow runs one step per task every morning (dags/stock_reorder.py). By hand, from the repo root
with the warehouse up:  python pipeline.py

"Today" is the last day in the warehouse: the history ends on 2017-12-31, so that day stands in for
this morning's data.
"""
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

import psycopg

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "out"
# Local only (docker-compose.yml binds it to 127.0.0.1) and holding public and generated data,
# so the password is a plain one. Inside Docker the host is "warehouse" on port 5432.
WAREHOUSE = dict(host=os.getenv("WAREHOUSE_HOST", "localhost"), port=os.getenv("WAREHOUSE_PORT", "5447"),
                 dbname="stock", user="stock", password="stock")


def run_sql(file):
    with psycopg.connect(**WAREHOUSE) as conn:
        conn.execute((ROOT / "sql" / file).read_text())


def load():
    """Add the new rows of each export to the warehouse; rows already there are skipped."""
    run_sql("01_tables.sql")
    with psycopg.connect(**WAREHOUSE) as conn:
        for table in ["item", "sales", "stock"]:
            conn.execute(f"CREATE TEMP TABLE new_{table} (LIKE {table})")
            with conn.cursor().copy(f"COPY new_{table} FROM STDIN WITH (FORMAT csv, HEADER)") as copy:
                copy.write((RAW / f"{table}.csv").read_bytes())
            added = conn.execute(f"INSERT INTO {table} SELECT * FROM new_{table} ON CONFLICT DO NOTHING").rowcount
            print(f"{table}: {added:,} new rows")

        # Every stock row needs its sales row, and no day may be missing (the forecast counts rows as days).
        no_sales = conn.execute("""SELECT count(*) FROM stock LEFT JOIN sales USING (date, store, item)
                                   WHERE sales.date IS NULL""").fetchone()[0]
        gaps = conn.execute("""SELECT count(*) FROM (SELECT store, item FROM sales GROUP BY store, item
                               HAVING count(*) <> max(date) - min(date) + 1) AS g""").fetchone()[0]
        assert no_sales == 0, f"{no_sales} stock rows have no sales row"
        assert gaps == 0, f"{gaps} store-items have a missing day"


def forecast():
    run_sql("02_forecast.sql")


def rules():
    run_sql("03_rules.sql")


def alert(day=None):
    """Email this morning's reorder list, or a past day's: alert("2017-07-16"). The email is always
    saved to out/; it is sent only when GMAIL_USER and GMAIL_APP_PASSWORD are set (.env)."""
    with psycopg.connect(**WAREHOUSE) as conn:
        today = conn.execute("SELECT coalesce(%s::date, max(date)) FROM stock_rule", [day]).fetchone()[0]
        rows = conn.execute("""SELECT store, item, on_hand, on_order, days_of_cover, reorder_point, order_qty
                               FROM stock_rule WHERE date = %s AND order_qty > 0
                               ORDER BY store, days_of_cover, item""", [today]).fetchall()

    cell = 'style="padding:6px 10px;border-bottom:1px solid #E2E8F0;text-align:right"'
    lines = "".join(f"<tr><td {cell}>{store}</td><td {cell}>{item}</td><td {cell}>{on_hand:,}</td>"
                    f"<td {cell}>{on_order:,}</td><td {cell}>{cover}</td><td {cell}>{point:,.0f}</td>"
                    f"<td {cell}><b>{qty:,}</b></td></tr>"
                    for store, item, on_hand, on_order, cover, point, qty in rows)
    head = "".join(f'<th style="padding:6px 10px;text-align:right">{h}</th>'
                   for h in ["Store", "Item", "On hand", "On order", "Days left", "Reorder point", "Order"])
    subject = f"Reorder today: {len(rows)} items ({today:%d %b %Y})"
    html = (f'<div style="font-family:Segoe UI,Arial,sans-serif;color:#0F172A">'
            f'<h2 style="margin:0 0 4px">{subject}</h2>'
            f'<p style="margin:0 0 16px;color:#475569">Stock at closing on {today:%A %d %B %Y}. '
            f'Each item below, counting what is already on order, is at or under its reorder point. '
            f'Order the amount shown and it lasts until the delivery and a week after it.</p>'
            f'<table style="border-collapse:collapse;font-size:14px"><tr style="background:#0E1630;color:#fff">'
            f'{head}</tr>{lines}</table></div>')

    OUT.mkdir(exist_ok=True)
    (OUT / f"reorder-{today}.html").write_text(html, encoding="utf-8")
    print(subject, "-> saved to out/")

    user, password = os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD")
    if user and password:
        mail = EmailMessage()
        mail["Subject"], mail["From"], mail["To"] = subject, user, os.getenv("MAIL_TO") or user
        mail.set_content(f"{subject}. Open this email as HTML to see the list.")
        mail.add_alternative(html, subtype="html")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(user, password)
            smtp.send_message(mail)
        print("sent to", mail["To"])


if __name__ == "__main__":
    for step in [load, forecast, rules, alert]:
        print(f"--- {step.__name__}")
        step()
