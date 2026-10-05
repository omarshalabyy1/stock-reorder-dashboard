"""The one place client values come from: config/client.yaml, plus the secrets in .env."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).parent
REQUIRED = [
    "client.name", "client.currency",
    "warehouse.host", "warehouse.port", "warehouse.database", "warehouse.user",
    "inputs.sales", "inputs.stock", "inputs.items",
    "rules.forecast_days", "rules.service_z", "rules.cover_days_after_delivery",
    "rules.overstock_days", "rules.warning_window_days",
    "schedule.cron", "schedule.timezone", "alert.mail_to",
    "report.title", "report.best_sellers", "report.check_days", "report.check_shelf",
    "report.colours.data", "report.colours.text", "report.colours.muted",
    "report.colours.page", "report.colours.line", "report.colours.danger",
]


def load_config():
    try:
        cfg = yaml.safe_load((ROOT / "config" / "client.yaml").read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        line = error.problem_mark.line + 1 if getattr(error, "problem_mark", None) else "?"
        raise SystemExit(f"config/client.yaml is not valid YAML near line {line} (quote a value with # or :)")
    for key in REQUIRED:
        node = cfg
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                raise SystemExit(f"config/client.yaml is missing {key}")
            node = node[part]

    load_dotenv(ROOT / ".env")
    if not os.environ.get("DB_PASSWORD"):
        raise SystemExit(".env is missing DB_PASSWORD (copy .env.example to .env)")

    # Inside the Docker network the warehouse is reached by its service name, not 127.0.0.1;
    # docker-compose.yml sets these two for the Airflow container.
    w = cfg["warehouse"]
    w["host"] = os.environ.get("WAREHOUSE_HOST", w["host"])
    w["port"] = int(os.environ.get("WAREHOUSE_PORT", w["port"]))
    w["password"] = os.environ["DB_PASSWORD"]
    cfg["input_dir"] = ROOT / "data" / "input"
    return cfg
