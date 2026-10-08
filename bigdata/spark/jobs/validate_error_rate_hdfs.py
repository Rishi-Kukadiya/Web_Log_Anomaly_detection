from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    sum as spark_sum
)


spark = (
    SparkSession.builder
    .appName("ValidateErrorRateHDFS")
    .getOrCreate()
)

INPUT_PATH = (
    "hdfs://node1:9000/data/anomaly_detection/"
    "error_rate"
)

df = spark.read.parquet(INPUT_PATH)


print("\n=== HDFS ROW COUNT ===")
total = df.count()
print(total)


print("\n=== HDFS ANOMALY SUMMARY ===")

(
    df
    .groupBy("is_error_rate_anomaly")
    .count()
    .orderBy("is_error_rate_anomaly")
    .show()
)


print("\n=== INVALID ERROR RATE ===")

invalid_error_rate = (
    df
    .filter(
        (col("error_rate") < 0)
        | (col("error_rate") > 1)
        | col("error_rate").isNull()
    )
    .count()
)

print(invalid_error_rate)


print("\n=== INVALID REQUEST COUNTS ===")

invalid_counts = (
    df
    .filter(
        (col("total_requests") <= 0)
        | (col("error_requests") < 0)
        | (col("error_requests") > col("total_requests"))
    )
    .count()
)

print(invalid_counts)


print("\n=== DUPLICATE IP-WINDOW GROUPS ===")

duplicate_groups = (
    df
    .groupBy("ip", "window_start")
    .count()
    .filter(col("count") > 1)
    .count()
)

print(duplicate_groups)

print("\n=== HISTORY VALIDATION ===")

# history_count must be between 0 and 5
invalid_history_count = (
    df
    .filter(
        (col("history_count") < 0)
        | (col("history_count") > 5)
    )
    .count()
)

print("Invalid history_count:", invalid_history_count)


# History age must never be negative
negative_history_age = (
    df
    .filter(
        col("history_age_hours").isNotNull()
        & (col("history_age_hours") < 0)
    )
    .count()
)

print("Negative history age:", negative_history_age)


# Anomalies must satisfy the history requirements
invalid_anomalies = (
    df
    .filter(
        col("is_error_rate_anomaly")
        &
        (
            (col("history_count") < 5)
            |
            (col("history_age_hours") > 24)
            |
            (col("total_requests") < 5)
        )
    )
    .count()
)

print("Anomalies violating detection conditions:", invalid_anomalies)

print("\n=== VALIDATION COMPLETE ===")

spark.stop()
