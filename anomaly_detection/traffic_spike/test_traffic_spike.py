from pyspark.sql import SparkSession
from anomaly_detection.traffic_spike.traffic_spike_detector import (
    detect_traffic_spikes
)
from pyspark.sql.functions import col

INPUT_PATH = "data/processed/traffic_aggregation/traffic_5min.parquet"


def main():
    spark = (
        SparkSession.builder
        .appName("TestTrafficSpike")
        .master("local[*]")
        .getOrCreate()
    )

    df = spark.read.parquet(INPUT_PATH)

    result = detect_traffic_spikes(df)

    print("\n=== TRAFFIC SPIKE SCHEMA ===")
    result.printSchema()

    print("\n=== SAMPLE RESULTS ===")
    (
        result
        .orderBy("window_start", "ip")
        .show(20, truncate=False)
    )

    print("\n=== RECORD COUNTS ===")
    print(f"Total records: {result.count()}")

    print("\n=== HISTORY SUFFICIENCY ===")
    result.selectExpr(
        "sum(CASE WHEN history_count >= 5 THEN 1 ELSE 0 END) AS sufficient_history",
        "sum(CASE WHEN history_count < 5 THEN 1 ELSE 0 END) AS insufficient_history"
    ).show()

    print("\n=== TRAFFIC SPIKE COUNTS ===")
    result.selectExpr(
        "sum(CASE WHEN is_traffic_spike = true THEN 1 ELSE 0 END) AS anomalies",
        "sum(CASE WHEN is_traffic_spike = false THEN 1 ELSE 0 END) AS normal"
    ).show()

    print("\n=== TOP TRAFFIC SPIKES ===")
    (
        result
        .filter("is_traffic_spike = true")
        .orderBy(col("robust_z_score").desc())
        .show(20, truncate=False)
    )
    print("\n=== ANOMALY HISTORY AGE ===")

    (
        result
        .filter("is_traffic_spike = true")
        .selectExpr(
            "sum(CASE WHEN history_age_hours <= 1 THEN 1 ELSE 0 END) AS within_1_hour",
            "sum(CASE WHEN history_age_hours > 1 AND history_age_hours <= 6 THEN 1 ELSE 0 END) AS 1_to_6_hours",
            "sum(CASE WHEN history_age_hours > 6 AND history_age_hours <= 12 THEN 1 ELSE 0 END) AS 6_to_12_hours",
            "sum(CASE WHEN history_age_hours > 12 THEN 1 ELSE 0 END) AS over_12_hours"
        )
        .show(truncate=False)
    )

    spark.stop()


if __name__ == "__main__":
    main()
