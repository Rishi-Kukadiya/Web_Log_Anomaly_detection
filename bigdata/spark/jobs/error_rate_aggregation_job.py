from pyspark.sql import SparkSession

from bigdata.spark.transformations.error_rate_aggregation import (
    aggregate_error_rate
)


INPUT_PATH = "hdfs://node1:9000/data/access_logs/access_logs.parquet"
OUTPUT_PATH = "hdfs://node1:9000/data/error_rate_aggregation/error_rate_5min.parquet"


def main():
    spark = (
        SparkSession.builder
        .appName("ErrorRateAggregation")
        .getOrCreate()
    )

    print("\n=== Reading Access Logs ===")

    df = spark.read.parquet(INPUT_PATH)

    print(f"Input records: {df.count()}")

    print("\n=== Aggregating HTTP Error Rate ===")

    error_rate_df = aggregate_error_rate(df)

    print("\n=== Error Rate Schema ===")
    error_rate_df.printSchema()

    print("\n=== Sample Error Rate Records ===")

    (
        error_rate_df
        .orderBy("window_start", "ip")
        .show(20, truncate=False)
    )

    print("\n=== Aggregated Record Count ===")
    print(error_rate_df.count())

    print("\n=== Writing Output ===")

    (
        error_rate_df
        .write
        .mode("overwrite")
        .parquet(OUTPUT_PATH)
    )

    print(f"Output written to: {OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()