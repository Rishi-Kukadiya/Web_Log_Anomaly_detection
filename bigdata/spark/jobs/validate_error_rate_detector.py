from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    min as spark_min,
    max as spark_max,
    avg,
    count
)

from anomaly_detection.error_rate.error_rate_detector import (
    detect_error_rate_anomalies
)


spark = (
    SparkSession.builder
    .appName("ValidateErrorRateDetector")
    .config(
        "spark.hadoop.fs.defaultFS",
        "hdfs://node1:9000"
    )
    .getOrCreate()
)

INPUT_PATH = (
    "hdfs://node1:9000/data/error_rate_aggregation/"
    "error_rate_5min.parquet"
)

df = spark.read.parquet(INPUT_PATH)

result = detect_error_rate_anomalies(df)

anomalies = result.filter(
    col("is_error_rate_anomaly") == True
)

print("\n=== ANOMALY COUNT ===")
print(anomalies.count())

print("\n=== ANOMALY REQUEST VOLUME ===")
(
    anomalies
    .select(
        spark_min("total_requests").alias("min_requests"),
        avg("total_requests").alias("avg_requests"),
        spark_max("total_requests").alias("max_requests")
    )
    .show()
)

print("\n=== ANOMALY ERROR RATE ===")
(
    anomalies
    .select(
        spark_min("error_rate").alias("min_error_rate"),
        avg("error_rate").alias("avg_error_rate"),
        spark_max("error_rate").alias("max_error_rate")
    )
    .show()
)

print("\n=== ANOMALY HISTORY COUNT ===")
(
    anomalies
    .select(
        spark_min("history_count").alias("min_history"),
        spark_max("history_count").alias("max_history")
    )
    .show()
)

print("\n=== ANOMALY HISTORY AGE ===")
(
    anomalies
    .select(
        spark_min("history_age_hours").alias("min_age_hours"),
        spark_max("history_age_hours").alias("max_age_hours")
    )
    .show()
)

print("\n=== ZERO-MAD ANOMALIES ===")

(
    anomalies
    .filter(col("mad") == 0)
    .select(
        count("*").alias("zero_mad_anomalies")
    )
    .show()
)

print("\n=== ROBUST-Z ANOMALIES ===")

(
    anomalies
    .filter(col("mad") > 0)
    .select(
        count("*").alias("robust_z_anomalies"),
        spark_min("robust_z_score").alias("min_z"),
        spark_max("robust_z_score").alias("max_z")
    )
    .show()
)

spark.stop()
