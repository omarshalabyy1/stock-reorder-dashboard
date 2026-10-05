"""The daily run, in four steps: load -> forecast -> rules -> alert.

Airflow runs one step per task on the client's schedule (dags/stock_reorder.py). By hand, from the
repo root with the warehouse up:  python pipeline.py

"Today" is the last day in the warehouse. Every client value comes from load_config().
"""
import os
import smtplib
from email.message import EmailMessage
from io import StringIO
from pathlib import Path

import pandas as pd
import psycopg

from config import load_config

ROOT = Path(__file__).parent
OUT = ROOT / "out"
CFG = load_config()
# input key in config/client.yaml -> (warehouse table, the columns loaded; extra columns are ignored)
INPUTS = {
    "items": ("item", ["item", "unit_cost", "lead_days"]),
    "sales": ("sales", ["date", "store", "item", "units_sold"]),
    "stock": ("stock", ["date", "store", "item", "units_received", "on_hand", "on_order"]),
}


def connect():
    w = CFG["warehouse"]
    return psycopg.connect(host=w["host"], port=w["port"], dbname=w["database"], user=w["user"], password=w["password"])


def run_sql(file):
    """Run one SQL file with the client's rules set as client.<key> for it to read."""
    with connect() as conn:
        for key, value in CFG["rules"].items():
            conn.execute("SELECT set_config(%s, %s, false)", [f"client.{key}", str(value)])
        conn.execute((ROOT / "sql" / file).read_text())


def check_inputs():
    """Stop with one line if an input file or one of its columns is missing."""
    for key, (_, columns) in INPUTS.items():
        path = CFG["input_dir"] / CFG["inputs"][key]
        if not path.exists():
            raise SystemExit(f"missing input file data/input/{path.name} (inputs.{key} in config/client.yaml)")
        missing = [c for c in columns if c not in pd.read_csv(path, nrows=0).columns]
        if missing:
            raise SystemExit(f"data/input/{path.name} is missing column(s): {', '.join(missing)}")


def load():
    """Add the new rows of each input file to the warehouse; rows already there are skipped."""
    check_inputs()
    run_sql("01_tables.sql")
    with connect() as conn:
        try:
            for key, (table, columns) in INPUTS.items():
                rows = pd.read_csv(CFG["input_dir"] / CFG["inputs"][key], usecols=columns, dtype=str)[columns]
                cols = ", ".join(columns)
                conn.execute(f"CREATE TEMP TABLE new_{table} (LIKE {table})")
                with conn.cursor().copy(f"COPY new_{table} ({cols}) FROM STDIN WITH (FORMAT csv, HEADER)") as copy:
                    copy.write(rows.to_csv(index=False))
                added = conn.execute(f"INSERT INTO {table} ({cols}) SELECT {cols} FROM new_{table} "
                                     "ON CONFLICT DO NOTHING").rowcount
                print(f"{table}: {added:,} new rows")
        except psycopg.errors.IntegrityError as error:  # an item missing from the items file, a negative count
            raise SystemExit(error.diag.message_detail or error.diag.message_primary)

        # Every stock row needs its sales row, and no day may be missing (the forecast counts rows as days).
        no_sales = conn.execute("""SELECT count(*) FROM stock LEFT JOIN sales USING (date, store, item)
                                   WHERE sales.date IS NULL""").fetchone()[0]
        gaps = conn.execute("""SELECT count(*) FROM (SELECT store, item FROM sales GROUP BY store, item
                               HAVING count(*) <> max(date) - min(date) + 1) AS g""").fetchone()[0]
        if no_sales:
            raise SystemExit(f"{no_sales} stock rows have no sales row")
        if gaps:
            raise SystemExit(f"{gaps} store-items have a missing day in the sales file")


def forecast():
    run_sql("02_forecast.sql")


def rules():
    run_sql("03_rules.sql")


def alert(day=None):
    """Email this morning's reorder list, or a past day's: alert("YYYY-MM-DD"). The email is always
    saved to out/; it is sent only when GMAIL_USER and GMAIL_APP_PASSWORD are set (.env)."""
    with connect() as conn:
        today = conn.execute("SELECT coalesce(%s::date, max(date)) FROM stock_rule", [day]).fetchone()[0]
        rows = conn.execute("""SELECT store, item, on_hand, on_order, days_of_cover, reorder_point, order_qty
                               FROM stock_rule WHERE date = %s AND order_qty > 0
                               ORDER BY store, days_of_cover, item""", [today]).fetchall()

    c = CFG["report"]["colours"]
    cell = f'style="padding:6px 10px;border-bottom:1px solid {c["line"]};text-align:right"'
    lines = "".join(f"<tr><td {cell}>{store}</td><td {cell}>{item}</td><td {cell}>{on_hand:,}</td>"
                    f"<td {cell}>{on_order:,}</td><td {cell}>{cover}</td><td {cell}>{point:,.0f}</td>"
                    f"<td {cell}><b>{qty:,}</b></td></tr>"
                    for store, item, on_hand, on_order, cover, point, qty in rows)
    head = "".join(f'<th style="padding:6px 10px;text-align:right">{h}</th>'
                   for h in ["Store", "Item", "On hand", "On order", "Days left", "Reorder point", "Order"])
    subject = f"{CFG['client']['name']}: reorder today, {len(rows)} items ({today:%d %b %Y})"
    after = CFG["rules"]["cover_days_after_delivery"]
    html = (f'<div style="font-family:Segoe UI,Arial,sans-serif;color:{c["text"]}">'
            f'<h2 style="margin:0 0 4px">{subject}</h2>'
            f'<p style="margin:0 0 16px;color:{c["muted"]}">Stock at closing on {today:%A %d %B %Y}. '
            f'Each item below, counting what is already on order, is at or under its reorder point. '
            f'Order the amount shown and it lasts until the delivery and {after} days after it.</p>'
            f'<table style="border-collapse:collapse;font-size:14px"><tr style="background:{c["text"]};color:{c["page"]}">'
            f'{head}</tr>{lines}</table></div>')

    OUT.mkdir(exist_ok=True)
    (OUT / f"reorder-{today}.html").write_text(html, encoding="utf-8")
    print(subject, "-> saved to out/")

    user, password = os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD")
    if user and password:
        mail = EmailMessage()
        mail["Subject"], mail["From"], mail["To"] = subject, user, CFG["alert"]["mail_to"] or user
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
