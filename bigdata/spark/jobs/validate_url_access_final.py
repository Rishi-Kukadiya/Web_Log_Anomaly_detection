from pyspark.sql import SparkSession
from pyspark.sql.functions import col, greatest


spark = (
    SparkSession.builder
    .appName("ValidateURLAccessFinal")
    .getOrCreate()
)

PATH = (
    "hdfs://node1:9000/data/anomaly_detection/"
    "url_access"
)

df = spark.read.parquet(PATH)


# =========================================================
# 1. NULL / INVALID FIELDS
# =========================================================

invalid_fields = (
    df.filter(
        col("ip").isNull()
        | col("window_start").isNull()
        | col("window_end").isNull()
        | col("unique_url_count").isNull()
        | col("history_count").isNull()
        | col("baseline_median").isNull()
        | col("mad").isNull()
        | col("history_age_hours").isNull()
        | col("is_url_access_anomaly").isNull()
    )
)

print("\n=== INVALID / NULL FIELD ROWS ===")
print(invalid_fields.count())


# =========================================================
# 2. HISTORY COUNT VALIDATION
# =========================================================

invalid_history_count = (
    df.filter(
        (col("history_count") < 0)
        | (col("history_count") > 5)
    )
)

print("\n=== INVALID HISTORY COUNT ===")
print(invalid_history_count.count())


# =========================================================
# 3. HISTORY AGE VALIDATION
# =========================================================

invalid_history_age = (
    df.filter(
        (col("history_age_hours") < 0)
        | (col("history_age_hours") > 24)
    )
)

print("\n=== INVALID HISTORY AGE ===")
print(invalid_history_age.count())


# =========================================================
# 4. ANOMALY RULE CONSISTENCY
# =========================================================

invalid_anomalies = (
    df
    .filter(col("is_url_access_anomaly") == True)
    .filter(
        (col("history_count") < 5)
        |
        (col("history_age_hours") > 24)
        |
        (
            (col("mad") > 0)
            &
            (
                col("robust_z_score").isNull()
                |
                (col("robust_z_score") < 3.5)
            )
        )
        |
        (
            (col("mad") == 0)
            &
            (
                col("unique_url_count")
                <
                greatest(
                    3 * col("baseline_median"),
                    col("baseline_median") + 5
                )
            )
        )
    )
)

print("\n=== ANOMALIES VIOLATING DETECTION RULE ===")
print(invalid_anomalies.count())


# =========================================================
# FINAL SUMMARY
# =========================================================

total_records = df.count()

anomaly_count = (
    df
    .filter(col("is_url_access_anomaly") == True)
    .count()
)

normal_count = (
    df
    .filter(col("is_url_access_anomaly") == False)
    .count()
)

print("\n=== FINAL VALIDATION SUMMARY ===")
print("Total records:", total_records)
print("Anomalies:", anomaly_count)
print("Normal:", normal_count)


spark.stop()