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

os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars /usr/local/lib/mysql-connector-java-5.1.49.jar pyspark-shell'

mysql_url = f"jdbc:mysql://{os.getenv('host_ip')}:3306/{os.getenv('DATABASE')}?useSSL=false&allowPublicKeyRetrieval=true&useUnicode=true&characterEncoding=UTF-8"

convert_cols = ['comment_publish_date', 'publish_date']

def build_spark():
    # SparkSession 생성
    spark = SparkSession.builder \
        .appName("HDFS to MySQL") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
        .getOrCreate()
    return spark

def load_hdfs_files(spark):
    # HDFS에 있는 모든 Parquet 파일 로드
    df = spark.read.parquet("hdfs:///data/")
    return df

def df_preprocessing(df, convert_cols):
    ## 시간 형식 수정(yyyy.mm.dd HH:MM:SS)
    for c in convert_cols:
        df = df.withColumn(c
                        , to_timestamp(col('comment_publish_date'), "yyyy-MM-dd'T'HH:mm:ss'Z'")
                        )
    ## 결측치 제거
    df = df.dropna()

    return df

def truncate_table():
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
    return print('테이블 날렸습니다.')

def save_to_sql(df):
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
    return print('save success in mysql~!')

def main():
    spark = build_spark()
    df = load_hdfs_files(spark)
    df = df_preprocessing(df, convert_cols)
    truncate_table()
    save_to_sql(df)
    spark.stop()

if __name__ == '__main__':
    main()