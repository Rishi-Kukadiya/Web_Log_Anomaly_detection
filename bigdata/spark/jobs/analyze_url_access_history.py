from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    percentile_approx,
    min as spark_min,
    max as spark_max,
    avg,
    unix_timestamp
)

spark = (
    SparkSession.builder
    .appName("AnalyzeURLAccessHistory")
    .getOrCreate()
)

INPUT_PATH = (
    "hdfs://node1:9000/data/url_access_aggregation/"
    "url_access_5min.parquet"
)

df = spark.read.parquet(INPUT_PATH)

# ---------------------------------------------------------
# Build per-IP history
# ---------------------------------------------------------

ip_history = (
    df
    .groupBy("ip")
    .agg(
        count("*").alias("observation_count"),
        spark_min("window_start").alias("first_seen"),
        spark_max("window_start").alias("last_seen")
    )
)

print("\n=== URL COUNT FOR IPS WITH >= 5 OBSERVATIONS ===")

history_ips = (
    df
    .join(
        ip_history
        .filter(col("observation_count") >= 5)
        .select("ip"),
        on="ip",
        how="inner"
    )
)

(
    history_ips
    .select(
        percentile_approx("unique_url_count", 0.50, 10000).alias("p50"),
        percentile_approx("unique_url_count", 0.75, 10000).alias("p75"),
        percentile_approx("unique_url_count", 0.90, 10000).alias("p90"),
        percentile_approx("unique_url_count", 0.95, 10000).alias("p95"),
        percentile_approx("unique_url_count", 0.99, 10000).alias("p99"),
        percentile_approx("unique_url_count", 0.999, 10000).alias("p99.9"),
        spark_max("unique_url_count").alias("max"),
        avg("unique_url_count").alias("mean")
    )
    .show(truncate=False)
)

print("\n=== HISTORY SPAN FOR IPS WITH >= 5 OBSERVATIONS ===")

(
    ip_history
    .filter(col("observation_count") >= 5)
    .withColumn(
    "history_span_hours",
    (
        unix_timestamp(col("last_seen"))
        - unix_timestamp(col("first_seen"))
    ) / 3600.0
)
    .select(
        percentile_approx("history_span_hours", 0.50, 10000).alias("p50"),
        percentile_approx("history_span_hours", 0.75, 10000).alias("p75"),
        percentile_approx("history_span_hours", 0.90, 10000).alias("p90"),
        percentile_approx("history_span_hours", 0.95, 10000).alias("p95"),
        percentile_approx("history_span_hours", 0.99, 10000).alias("p99"),
        spark_max("history_span_hours").alias("max")
    )
    .show(truncate=False)
)

print("\n=== URL COUNT DISTRIBUTION FOR FREQUENT IPS ===")

for threshold in [5, 10, 20]:
    subset = df.join(
        ip_history
        .filter(col("observation_count") >= threshold)
        .select("ip"),
        on="ip",
        how="inner"
    )

    print(f"\nIPs with >= {threshold} observations:")

    (
        subset
        .select(
            percentile_approx(
                "unique_url_count", 0.50, 10000
            ).alias("p50"),
            percentile_approx(
                "unique_url_count", 0.90, 10000
            ).alias("p90"),
            percentile_approx(
                "unique_url_count", 0.99, 10000
            ).alias("p99"),
            spark_max("unique_url_count").alias("max")
        )
        .show(truncate=False)
    )

spark.stop()
