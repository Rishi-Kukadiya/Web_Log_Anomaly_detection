from pyspark.sql import SparkSession

from bigdata.spark.transformations.error_rate_aggregation import (
    aggregate_error_rate
)


INPUT_PATH = "data/processed/access_logs/access_logs.parquet"


def main():
    spark = (
        SparkSession.builder
        .appName("TestErrorRateAggregation")
        .master("local[*]")
        .getOrCreate()
    )

    df = spark.read.parquet(INPUT_PATH)

    print("\n=== Input Records ===")
    print(df.count())

    result = aggregate_error_rate(df)

    print("\n=== Schema ===")
    result.printSchema()

    print("\n=== Total Aggregated Rows ===")
    print(result.count())

    print("\n=== Sample ===")
    result.orderBy("window_start", "ip").show(
        20,
        truncate=False
    )

    print("\n=== Error Rate Range ===")
    result.selectExpr(
        "min(error_rate) as min_error_rate",
        "max(error_rate) as max_error_rate"
    ).show()
    
    print("\n=== Error Rate Validation ===")

    invalid_rates = result.filter(
        (result.error_rate < 0) | (result.error_rate > 1)
    ).count()

    invalid_counts = result.filter(
        result.error_requests > result.total_requests
    ).count()

    print("Invalid error_rate rows:", invalid_rates)
    print("Invalid error count rows:", invalid_counts)

    spark.stop()


if __name__ == "__main__":
    main()