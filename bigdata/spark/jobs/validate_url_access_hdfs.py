from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("ValidateURLAccessAnomalyDetection")
    .getOrCreate()
)

PATH = (
    "hdfs://node1:9000/data/anomaly_detection/"
    "url_access"
)

df = spark.read.parquet(PATH)

print("\n=== TOTAL RECORDS ===")
print(df.count())

print("\n=== ANOMALY COUNTS ===")
df.groupBy("is_url_access_anomaly").count().show()

print("\n=== SCHEMA ===")
df.printSchema()

spark.stop()

