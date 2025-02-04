import os
from pyspark.sql import SparkSession

host_ip = '15.168.221.131'
DATABASE = 'sample'
user_id = 'lab13'
user_password = 'lab13'

# 환경변수 설정
os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars /usr/local/lib/mysql-connector-java-5.1.49-bin.jar pyspark-shell'

ss = SparkSession\
            .builder\
            .appName('MySQL')\
            .config('spark.executor.memory', '6g')\
            .config('spark.driver.memory', '6g')\
            .getOrCreate()

mysql_url = f'jdbc:mysql://{host_ip}:3306/{DATABASE}?useSSL=false&allowPublicKeyRetrieval=true'
df = ss.read.format('jdbc')\
            .options(
                url = mysql_url
                , driver = 'com.mysql.jdbc.Driver'
                , dbtable = 'tbSample'
                , user = user_id
                , password = user_password
                    )\
        .load()\


print(df.count())