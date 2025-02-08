from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from danawa_crawling_Fold_Flip import main as fold_flip_main
from danawa_crawling_S24_Iphone import main as S24_Iphone_main

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


    danawa_crawling_fold_flip = PythonOperator(
            task_id = 'danawa_crawling_fold_flip',
            python_callable = fold_flip_main,

            )

    danawa_crawling_S24_Iphone = PythonOperator(
            task_id = 'danawa_crawling_S24_Iphone',
            python_callable = S24_Iphone_main,

            )


    danawa_to_hdfs = BashOperator(
            task_id = 'danawa_to_hdfs'
            , bash_command = '''
            hdfs dfs -rm -r /danawa_data/* &&
            cd ~/airflow/danawa_data &&
            hdfs dfs -put -f *.parquet /danawa_data
            '''
            ,  trigger_rule = 'all_success'
            )

    [danawa_crawling_fold_flip, danawa_crawling_S24_Iphone] >> danawa_to_hdfs

