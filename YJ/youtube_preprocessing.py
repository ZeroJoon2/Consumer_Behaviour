from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp
import os
from dotenv import load_dotenv

import pymysql
# 상위 폴더(../)에 있는 `.env` 파일 로드

dotenv_path = os.path.abspath(os.path.join(os.getcwd(), "..", ".env"))
load_dotenv(dotenv_path)
## mysql 연결
os.getenv('user_id')
os.getenv('user_password')

mysql_url = f"jdbc:mysql://{os.getenv('host_ip')}:3306/{os.getenv('DATABASE')}?useSSL=false&allowPublicKeyRetrieval=true&useUnicode=true&characterEncoding=UTF-8"

# SparkSession 생성
spark = SparkSession.builder \
    .appName("HDFS to MySQL") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .getOrCreate()

# HDFS에 있는 모든 Parquet 파일 로드
df = spark.read.parquet("hdfs:///data/")
print(df.count())

## 시간 형식 수정(yyyy.mm.dd HH:MM:SS)
convert_cols = ['comment_publish_date', 'publish_date']
for c in convert_cols:
    df = df.withColumn(c
                     , to_timestamp(col('comment_publish_date'), "yyyy-MM-dd'T'HH:mm:ss'Z'")
                     )
## 결측치 제거
df = df.dropna()

# PyMySQL로 MySQL 연결 (SQL 실행을 위해)
conn = pymysql.connect(
    host=os.getenv('host_ip'),
    user=os.getenv('user_id'),
    password=os.getenv('user_password'),
    database=os.getenv('DATABASE'),
)

cursor = conn.cursor()

# ✅ MySQL 테이블 `TRUNCATE`
truncate_query = "TRUNCATE TABLE tbCrawled_Youtube"
cursor.execute(truncate_query)

conn.commit()
cursor.close()
conn.close()

os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars /usr/local/lib/mysql-connector-java-5.1.49-bin.jar pyspark-shell'
df.write.format('jdbc')\
    .options(
        url = mysql_url
        , driver = 'com.mysql.jdbc.Driver'
        , dbtable = 'tbCrawled_Youtube'
        , user = os.getenv('user_id')
        , password = os.getenv('user_password')
    )\
    .mode('append')\
    .save()
spark.stop()