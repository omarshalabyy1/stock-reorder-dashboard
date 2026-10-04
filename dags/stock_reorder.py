"""stock_reorder: every morning at 7am Cairo time, load -> forecast -> rules -> alert.

Each task is one step of pipeline.py (the repo is mounted at /opt/stock-reorder), imported inside the
task so that parsing this file stays fast. A laptop asleep at 7am runs it once it wakes (catchup
off); Trigger (top right in Airflow) runs it now. A re-run adds nothing twice: the load skips rows
already in the warehouse, and the forecast and rules are rebuilt from scratch.
"""
import sys

import pendulum
from airflow.sdk import dag, task

sys.path.insert(0, "/opt/stock-reorder")


@dag(schedule="0 7 * * *", start_date=pendulum.datetime(2026, 10, 1, tz="Africa/Cairo"),
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
