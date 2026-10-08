from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

spark = (
    SparkSession.builder
    .appName("ValidateURLAccessDuplicates")
    .getOrCreate()
)

PATH = (
    "hdfs://node1:9000/data/anomaly_detection/"
    "url_access"
)

df = spark.read.parquet(PATH)

duplicates = (
    df
    .groupBy("ip", "window_start")
    .agg(count("*").alias("count"))
    .filter(col("count") > 1)
)

print("\n=== DUPLICATE IP-WINDOW GROUPS ===")
print(duplicates.count())

spark.stop()
