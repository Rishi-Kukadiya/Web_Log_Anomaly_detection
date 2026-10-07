from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    min,
    max,
    sum,
    when
)

spark = (
    SparkSession.builder
    .appName("VerifyTrafficSpike")
    .config("spark.hadoop.fs.defaultFS", "hdfs://node1:9000")
    .getOrCreate()
)

PATH = "hdfs://node1:9000/data/anomaly_detection/traffic_spike"

df = spark.read.parquet(PATH)

print("\n=== ROW COUNT ===")
print(df.count())

print("\n=== SCHEMA ===")
df.printSchema()

print("\n=== ANOMALY SUMMARY ===")
df.select(
    count("*").alias("total_records"),
    sum(when(col("is_traffic_spike"), 1).otherwise(0)).alias("anomalies"),
    sum(when(~col("is_traffic_spike"), 1).otherwise(0)).alias("normal")
).show()

print("\n=== VALUE VALIDATION ===")
df.select(
    min("request_count").alias("min_request_count"),
    max("request_count").alias("max_request_count"),
    min("history_count").alias("min_history_count"),
    max("history_count").alias("max_history_count"),
    min("mad").alias("min_mad"),
    max("mad").alias("max_mad")
).show()

print("\n=== INVALID ROWS ===")

invalid = df.filter(
    (col("request_count") < 1) |
    (col("history_count") < 0) |
    (col("mad") < 0) |
    col("robust_z_score").isNull()
).count()

print(f"Invalid rows: {invalid}")

print("\n=== DUPLICATE IP-WINDOW GROUPS ===")

duplicates = (
    df.groupBy("ip", "window_start", "window_end")
    .count()
    .filter(col("count") > 1)
    .count()
)

print(f"Duplicate groups: {duplicates}")

print("\n=== TOP ANOMALIES ===")

(
    df
    .filter(col("is_traffic_spike") == True)
    .orderBy(col("robust_z_score").desc())
    .show(10, truncate=False)
)

spark.stop()
