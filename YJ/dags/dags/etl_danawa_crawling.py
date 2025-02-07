from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from danawa_crawling import main

# DAG 정의
with DAG(
    dag_id='etl_danawa_crawling',
    default_args={
        'owner': 'airflow',
        'depends_on_past' : False,
        'start_date': datetime(2025, 2, 1),
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    },
    schedule_interval='0 0 1 * *',
    catchup=False
) as dag:

    # danawa 크롤링 task
    # danawa_crawling = BashOperator(
    #        task_id = 'danawa_crawling',
    #        bash_command = 'python danawa_crawling.py',
    #        )


    danawa_crawling = PythonOperator(
            task_id = 'danawa_crawling',
            python_callable = main,

            )



    danawa_crawling

