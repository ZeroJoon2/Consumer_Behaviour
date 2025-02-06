from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.utils.email import send_email
from youtube_api_function import search_videos, get_all_comments, save_comments_to_parquet

# Variable은 airflow UI에서 설정해야함
# youtube_search_query: "아이폰 16 리뷰" (기본값)
# youtube_published_after: "2024-09-10T00:00:00Z" (기본값)
# parquet_filename: "youtube_i16_1.parquet" (기본값)

# 이메일 알림 : 성공 & 실패 알림
def send_failure_email(context):
    subject = f"DAG {context['dag'].dag_id} 실행 실패!"
    message = f"DAG 실패: {context['exception']}"
    send_email(to='comboy8231@gmail.com', subject=subject, html_content=message)

def send_success_email(context):
    subject = f"DAG {context['dag'].dag_id} 실행 성공!"
    message = "DAG이 성공적으로 실행되었습니다."
    send_email(to='comboy8231@gmail.com', subject=subject, html_content=message)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 2, 4),
    'retries': 1,
    'email_on_failure': True, 
    'email_on_retry': False,   
    'email': ['comboy8231@gmail.com'], 
    'on_failure_callback': send_failure_email, 
    'on_success_callback': send_success_email   
}

# 비디오 검색
# 갤럭시 S24 : '2024-01-17T00:00:00Z'
# 아이폰 16 : '2024-09-10T00:00:00Z'
# 갤럭시 Z 폴드 6/플립 6 : '2024-07-10T00:00:00Z'
# search_query, published_after은 Variable로 설정!
def video_search_task(**kwargs):
    search_query = Variable.get("youtube_search_query", default_var="아이폰 16 리뷰")
    published_after = Variable.get("youtube_published_after", default_var="2024-09-10T00:00:00Z").strip('"') 
    video_data, _ = search_videos(search_query, published_after)
    kwargs['ti'].xcom_push(key='video_data', value=video_data)

# 댓글 수집 
def comment_collection_task(**kwargs):
    video_data = kwargs['ti'].xcom_pull(key='video_data', task_ids='video_search_task')
    all_comments = {}
    for video in video_data:
        video_id = video['video_id']
        comments = get_all_comments(video_id)
        all_comments[video_id] = {
            'title': video['title'],
            'published_at': video['published_at'],
            'channel_title': video['channel_title'],
            'comments': comments
        }
    kwargs['ti'].xcom_push(key='all_comments', value=all_comments)

# 댓글 parquet 저장 
def save_comments_task(**kwargs):
    all_comments = kwargs['ti'].xcom_pull(key='all_comments', task_ids='comment_collection_task')
    
    # parquet 파일 이름은 Variable로 설정!
    parquet_filename = Variable.get("parquet_filename", default_var="youtube_i16_1.parquet")
    save_comments_to_parquet(all_comments, filename=parquet_filename)


# DAG 정의
# 매달 1일에 실행하도록 일단 설정!
with DAG('youtube_comments_dag', default_args=default_args, schedule_interval='0 0 1 * *') as dag:
    # 비디오 검색 Task
    video_search = PythonOperator(
        task_id='video_search_task',
        python_callable=video_search_task,
        provide_context=True  
    )

    # 댓글 수집 Task
    comment_collection = PythonOperator(
        task_id='comment_collection_task',
        python_callable=comment_collection_task,
        provide_context=True
    )

    # 댓글 저장 Task
    save_comments = PythonOperator(
        task_id='save_comments_task',
        python_callable=save_comments_task,
        provide_context=True
    )

    # HDFS 적재 Task
    # 데이터는 /youtube_data/에 저장!
    upload_to_hdfs = BashOperator(
    task_id='upload_to_hdfs_task',
    bash_command='hdfs dfs -put {{ params.parquet_filename }} {{ params.hdfs_dir }}', 
    params={
        "parquet_filename": Variable.get("parquet_filename", default_var="youtube_i16_1.parquet"),
        "hdfs_dir": Variable.get("hdfs_dir", default_var="/youtube_data/")  
    },
    env={
        "HADOOP_HOME": "/home/ubuntu/hadoop-3.3.6", 
        "HADOOP_CONF_DIR": "/home/ubuntu/hadoop-3.3.6/etc/hadoop",
        "PATH": "/home/ubuntu/hadoop-3.3.6/bin:$PATH"
    }
)
    # Task 순서
    video_search >> comment_collection >> save_comments >> upload_to_hdfs
