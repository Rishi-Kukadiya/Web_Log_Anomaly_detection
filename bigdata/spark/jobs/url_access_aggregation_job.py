from pyspark.sql import SparkSession

from bigdata.spark.transformations.url_access_aggregation import (
    aggregate_url_access
)

INPUT_PATH = "hdfs://node1:9000/data/access_logs/access_logs.parquet"
OUTPUT_PATH = "hdfs://node1:9000/data/url_access_aggregation/url_access_5min.parquet"


def main():
    spark = (
        SparkSession.builder
        .appName("URLAccessAggregation")
        .getOrCreate()
    )

    print("\n=== Reading Access Logs ===")
    df = spark.read.parquet(INPUT_PATH)

    print(f"Input records: {df.count()}")

    print("\n=== Aggregating URL Access ===")
    url_access_df = aggregate_url_access(df)

    print("\n=== URL Access Schema ===")
    url_access_df.printSchema()

    print("\n=== Sample URL Access Records ===")
    (
        url_access_df
        .orderBy("window_start", "ip")
        .show(20, truncate=False)
    )

    print("\n=== Aggregated Record Count ===")
    print(url_access_df.count())

    print("\n=== Writing Output ===")
    (
        url_access_df
        .write
        .mode("overwrite")
        .parquet(OUTPUT_PATH)
    )

    print(f"Output written to: {OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()