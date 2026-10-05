"""stock_reorder: load -> forecast -> rules -> alert, on the client's schedule.

The run time is schedule.cron in schedule.timezone (config/client.yaml), read when Airflow parses
this file. Each task is one step of pipeline.py (the repo is mounted at /opt/stock-reorder),
imported inside the task so that parsing stays fast. A laptop asleep at run time runs it once it
wakes (catchup off); Trigger (top right in Airflow) runs it now. A re-run adds nothing twice: the
load skips rows already in the warehouse, and the forecast and rules are rebuilt from scratch.
"""
import sys

import pendulum
from airflow.sdk import dag, task

sys.path.insert(0, "/opt/stock-reorder")
from config import load_config  # noqa: E402

SCHEDULE = load_config()["schedule"]


@dag(schedule=SCHEDULE["cron"], start_date=pendulum.datetime(2026, 10, 1, tz=SCHEDULE["timezone"]),
     catchup=False, max_active_runs=1, is_paused_upon_creation=False)
def stock_reorder():
    @task
    def load():
        import pipeline
        pipeline.load()

    @task
    def forecast():
        import pipeline
        pipeline.forecast()

    @task
    def rules():
        import pipeline
        pipeline.rules()

    @task
    def alert():
        import pipeline
        pipeline.alert()

    load() >> forecast() >> rules() >> alert()


stock_reorder()
