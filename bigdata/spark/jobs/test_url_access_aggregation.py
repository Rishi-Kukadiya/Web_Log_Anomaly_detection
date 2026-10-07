from pyspark.sql import SparkSession

from bigdata.spark.transformations.url_access_aggregation import (
    aggregate_url_access
)


def main():
    spark = (
        SparkSession.builder
        .appName("TestURLAccessAggregation")
        .master("local[*]")
        .getOrCreate()
    )

    input_path = "data/processed/access_logs/access_logs.parquet"

    print("\n=== Reading Access Logs ===")
    df = spark.read.parquet(input_path)

    print(f"Input records: {df.count()}")

    print("\n=== Aggregating URL Access ===")
    result = aggregate_url_access(df)

    print("\n=== URL Access Schema ===")
    result.printSchema()

    print("\n=== Sample URL Access Records ===")
    (
        result
        .orderBy("window_start", "ip")
        .show(20, truncate=False)
    )

    print("\n=== Aggregated Record Count ===")
    print(result.count())

    print("\n=== URL Access Validation ===")

    invalid_counts = result.filter(
        result.unique_url_count < 1
    ).count()

    duplicate_groups = (
        result
        .groupBy("ip", "window_start", "window_end")
        .count()
        .filter("count > 1")
        .count()
    )

    print("Invalid unique URL count rows:", invalid_counts)
    print("Duplicate IP-window groups:", duplicate_groups)

    spark.stop()


if __name__ == "__main__":
    main()