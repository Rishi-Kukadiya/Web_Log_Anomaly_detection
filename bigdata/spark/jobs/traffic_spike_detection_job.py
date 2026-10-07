from pyspark.sql import SparkSession

from anomaly_detection.traffic_spike.traffic_spike_detector import (
    detect_traffic_spikes
)


INPUT_PATH = (
    "hdfs://node1:9000/data/traffic_aggregation/"
    "traffic_5min.parquet"
)

OUTPUT_PATH = (
    "hdfs://node1:9000/data/anomaly_detection/"
    "traffic_spike"
)


def main():
    spark = (
        SparkSession.builder
        .appName("TrafficSpikeDetection")
        .getOrCreate()
    )

    print("\n=== Reading Traffic Aggregation ===")

    df = spark.read.parquet(INPUT_PATH)

    print(f"Input records: {df.count()}")

    print("\n=== Detecting Traffic Spikes ===")

    result = detect_traffic_spikes(df)

    print("\n=== Detection Schema ===")
    result.printSchema()

    print("\n=== Traffic Spike Counts ===")

    result.selectExpr(
        "sum(CASE WHEN is_traffic_spike = true THEN 1 ELSE 0 END) AS anomalies",
        "sum(CASE WHEN is_traffic_spike = false THEN 1 ELSE 0 END) AS normal"
    ).show()

    print("\n=== Top Traffic Spikes ===")

    (
        result
        .filter("is_traffic_spike = true")
        .orderBy("robust_z_score", ascending=False)
        .show(20, truncate=False)
    )

    print("\n=== Writing Output ===")

    (
        result
        .write
        .mode("overwrite")
        .parquet(OUTPUT_PATH)
    )

    print(f"Output written to: {OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()
