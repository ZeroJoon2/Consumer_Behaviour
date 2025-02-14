from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta

from danawa_preprocessing import main


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'danawa_preprocessing',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    danawa_preprocessing_task = PythonOperator(
        task_id='danawa_preprocessing'
        , python_callable=main
        , dag=dag
    )



danawa_preprocessing_task

