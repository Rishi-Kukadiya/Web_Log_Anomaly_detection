from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, unix_timestamp


INPUT_PATH = "data/processed/traffic_aggregation/traffic_5min.parquet"


def main():
    spark = (
        SparkSession.builder
        .appName("ValidateTrafficAggregation")
        .master("local[*]")
        .getOrCreate()
    )

    df = spark.read.parquet(INPUT_PATH)

    print("\n=== Schema ===")
    df.printSchema()

    total_rows = df.count()

    print("\n=== Total Aggregated Rows ===")
    print(total_rows)

    # 1. Validate request_count
    invalid_counts = df.filter(col("request_count") < 1).count()

    print("\n=== Request Count Validation ===")
    print(f"Invalid request_count rows: {invalid_counts}")

    # 2. Validate 5-minute windows
    invalid_windows = (
        df.filter(
            (
                unix_timestamp("window_end")
                - unix_timestamp("window_start")
            ) != 300
        )
        .count()
    )

    print("\n=== Window Validation ===")
    print(f"Invalid window rows: {invalid_windows}")

    # 3. Validate duplicate IP + window combinations
    duplicate_groups = (
        df.groupBy("ip", "window_start")
        .agg(count("*").alias("group_count"))
        .filter(col("group_count") > 1)
        .count()
    )

    print("\n=== Duplicate Validation ===")
    print(f"Duplicate (ip, window) groups: {duplicate_groups}")

    # 4. Overall result
    print("\n=== Validation Result ===")

    if (
        invalid_counts == 0
        and invalid_windows == 0
        and duplicate_groups == 0
    ):
        print("PASS: Traffic aggregation is valid")
    else:
        print("FAIL: Traffic aggregation has validation errors")

    spark.stop()


if __name__ == "__main__":
    main()