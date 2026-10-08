from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from anomaly_detection.url_access.url_access_detector import (
    detect_url_access_anomalies
)


spark = (
    SparkSession.builder
    .appName("TestURLAccessDetector")
    .master("local[*]")
    .getOrCreate()
)
INPUT_PATH = (
    "hdfs://node1:9000/data/url_access_aggregation/"
    "url_access_5min.parquet"
)

df = spark.read.parquet(INPUT_PATH)

result = detect_url_access_anomalies(df)

print("\n=== TOTAL RECORDS ===")
print(result.count())

print("\n=== ANOMALY COUNTS ===")
result.groupBy("is_url_access_anomaly").count().show()

print("\n=== ANOMALIES ===")
(
    result
    .filter("is_url_access_anomaly = true")
    .orderBy("robust_z_score", ascending=False)
    .show(20, truncate=False)
)

print("\n=== ANOMALY STATISTICS ===")
(
    result
    .filter("is_url_access_anomaly = true")
    .select(
        "unique_url_count",
        "history_count",
        "baseline_median",
        "mad",
        "history_age_hours",
        "robust_z_score"
    )
    .summary()
    .show()
)

print("\n=== ANOMALY TYPE BREAKDOWN ===")

(
    result
    .filter("is_url_access_anomaly = true")
    .withColumn(
        "anomaly_type",
        when(
            col("mad") > 0,
            "ROBUST_Z_SCORE"
        ).otherwise(
            "ZERO_MAD_FALLBACK"
        )
    )
    .groupBy("anomaly_type")
    .count()
    .show()
)

spark.stop()

