from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.models import Variable
from youtube_api_function import send_failure_email, send_success_email

# HDFS 적재 Task
# 데이터는 /youtube_data/에 저장!
def upload_to_hdfs_task(**kwargs):
    parquet_filename = kwargs['params']['parquet_filename']
    hdfs_dir = kwargs['params']['hdfs_dir']
    bash_command = f"hdfs dfs -put {parquet_filename} {hdfs_dir}"
    return bash_command

# DAG 정의
with DAG('hdfs_upload_dag', 
         default_args={
             'owner': 'airflow',
             'start_date': datetime(2025, 2, 4),
             'retries': 1,
             'email_on_failure': True, 
             'email_on_retry': False,
             'email': ['comboy8231@gmail.com'],
             'on_failure_callback': send_failure_email,  
             'on_success_callback': send_success_email,  
         }, 
         schedule_interval='0 0 1 * *') as dag: 
    
    # 명령어 생성 Task 
    generate_bash_command = PythonOperator(
        task_id='generate_bash_command',
        python_callable=upload_to_hdfs_task,
        params={
            "parquet_filename": Variable.get("parquet_filename", default_var="youtube_i16_1.parquet"),
            "hdfs_dir": Variable.get("hdfs_dir", default_var="/youtube_data/")  
        },
    )
    
    # HDFS 업로드 Task 
    upload_to_hdfs = BashOperator(
        task_id='upload_to_hdfs_task',
        bash_command="{{ task_instance.xcom_pull(task_ids='generate_bash_command') }}",  # XCom을 통해 명령어 사용
        env={
            "HADOOP_HOME": "/home/ubuntu/hadoop-3.3.6", 
            "HADOOP_CONF_DIR": "/home/ubuntu/hadoop-3.3.6/etc/hadoop",
            "PATH": "/home/ubuntu/hadoop-3.3.6/bin:$PATH"
        }
    )

    # Task 순서
    generate_bash_command >> upload_to_hdfs

