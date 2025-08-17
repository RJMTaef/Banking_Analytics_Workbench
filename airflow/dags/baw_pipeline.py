from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="baw_pipeline",
    start_date=datetime(2025,1,1),
    schedule="@daily",
    catchup=False,
    tags=["baw"]
) as dag:
    gen = BashOperator(task_id="generate_data", bash_command="python scripts/generate_data.py")
    load = BashOperator(task_id="load_to_duckdb", bash_command="python scripts/load_to_duckdb.py")
    dbt_deps = BashOperator(task_id="dbt_deps", bash_command="dbt deps")
    dbt_run = BashOperator(task_id="dbt_run", bash_command="dbt run")
    dbt_test = BashOperator(task_id="dbt_test", bash_command="dbt test")
    fraud = BashOperator(task_id="fraud", bash_command="python scripts/fraud_isoforest.py")
    churn = BashOperator(task_id="churn", bash_command="python scripts/churn_baseline.py")
    atm = BashOperator(task_id="atm", bash_command="python scripts/atm_forecast.py")
    gen >> load >> dbt_deps >> dbt_run >> dbt_test >> [fraud, churn, atm]
