from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    sum,
    avg,
    min,
    max,
    percentile_approx,
    when
)

spark = (
    SparkSession.builder
    .appName("AnalyzeErrorRate")
    .config("spark.hadoop.fs.defaultFS", "hdfs://node1:9000")
    .getOrCreate()
)

INPUT_PATH = (
    "hdfs://node1:9000/data/error_rate_aggregation/"
    "error_rate_5min.parquet"
)

df = spark.read.parquet(INPUT_PATH)

print("\n=== BASIC INFORMATION ===")
print(f"Total records: {df.count()}")

print("\n=== SCHEMA ===")
df.printSchema()

print("\n=== ERROR RATE DISTRIBUTION ===")

df.select(
    min("error_rate").alias("min"),
    percentile_approx("error_rate", 0.50, 10000).alias("p50"),
    percentile_approx("error_rate", 0.75, 10000).alias("p75"),
    percentile_approx("error_rate", 0.90, 10000).alias("p90"),
    percentile_approx("error_rate", 0.95, 10000).alias("p95"),
    percentile_approx("error_rate", 0.99, 10000).alias("p99"),
    percentile_approx("error_rate", 0.999, 10000).alias("p99_9"),
    max("error_rate").alias("max")
).show(truncate=False)

print("\n=== ERROR RATE BUCKETS ===")

df.select(
    sum(when(col("error_rate") == 0, 1).otherwise(0))
        .alias("zero_error_rate"),
    sum(
        when(
            (col("error_rate") > 0) & (col("error_rate") < 0.25),
            1
        ).otherwise(0)
    ).alias("0_to_25_percent"),
    sum(
        when(
            (col("error_rate") >= 0.25) &
            (col("error_rate") < 0.50),
            1
        ).otherwise(0)
    ).alias("25_to_50_percent"),
    sum(
        when(
            (col("error_rate") >= 0.50) &
            (col("error_rate") < 0.75),
            1
        ).otherwise(0)
    ).alias("50_to_75_percent"),
    sum(
        when(
            (col("error_rate") >= 0.75) &
            (col("error_rate") < 1.0),
            1
        ).otherwise(0)
    ).alias("75_to_99_percent"),
    sum(
        when(col("error_rate") == 1.0, 1).otherwise(0)
    ).alias("100_percent")
).show()

print("\n=== REQUEST COUNT DISTRIBUTION ===")

df.select(
    min("total_requests").alias("min_requests"),
    percentile_approx("total_requests", 0.50, 10000).alias("p50"),
    percentile_approx("total_requests", 0.75, 10000).alias("p75"),
    percentile_approx("total_requests", 0.90, 10000).alias("p90"),
    percentile_approx("total_requests", 0.95, 10000).alias("p95"),
    percentile_approx("total_requests", 0.99, 10000).alias("p99"),
    max("total_requests").alias("max")
).show(truncate=False)

print("\n=== ERROR REQUEST DISTRIBUTION ===")

df.select(
    min("error_requests").alias("min_errors"),
    percentile_approx("error_requests", 0.50, 10000).alias("p50"),
    percentile_approx("error_requests", 0.75, 10000).alias("p75"),
    percentile_approx("error_requests", 0.90, 10000).alias("p90"),
    percentile_approx("error_requests", 0.95, 10000).alias("p95"),
    percentile_approx("error_requests", 0.99, 10000).alias("p99"),
    max("error_requests").alias("max")
).show(truncate=False)

print("\n=== ERROR RATE WITH REQUEST VOLUME ===")

(
    df
    .filter(col("error_rate") > 0)
    .orderBy(
        col("error_rate").desc(),
        col("total_requests").desc()
    )
    .select(
        "ip",
        "window_start",
        "total_requests",
        "error_requests",
        "error_rate"
    )
    .show(20, truncate=False)
)

print("\n=== INVALID RECORDS ===")

invalid = df.filter(
    (col("error_rate") < 0) |
    (col("error_rate") > 1) |
    (col("error_requests") < 0) |
    (col("error_requests") > col("total_requests")) |
    (col("total_requests") <= 0)
).count()

print(f"Invalid records: {invalid}")

spark.stop()
