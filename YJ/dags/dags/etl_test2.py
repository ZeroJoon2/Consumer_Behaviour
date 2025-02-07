from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from youtube_api_function import send_failure_email, send_success_email

# Airflow Variable 사용
parquet_file_path = Variable.get("parquet_file_path")
hdfs_dir = Variable.get("hdfs_dir")

# DAG 정의
with DAG(
    dag_id='tmp_hdfs_upload_dag',
    default_args={
        'owner': 'airflow',
        'start_date': datetime(2025, 2, 4),
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    },
    schedule_interval='0 0 1 * *',
    catchup=False
) as dag:

    # HDFS 업로드 Task
    tmp_upload_to_hdfs = BashOperator(
        task_id='tmp_hdfs',
        bash_command=f"hdfs dfs -put {parquet_file_path} {hdfs_dir}",
    )

    tmp_upload_to_hdfs

