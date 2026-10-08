from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    min,
    max,
    sum as spark_sum,
    percentile_approx,
    avg,
    unix_timestamp
)

spark = (
    SparkSession.builder
    .appName("AnalyzeErrorRateHistory")
    .config("spark.hadoop.fs.defaultFS", "hdfs://node1:9000")
    .getOrCreate()
)

INPUT_PATH = (
    "hdfs://node1:9000/data/error_rate_aggregation/"
    "error_rate_5min.parquet"
)

df = spark.read.parquet(INPUT_PATH)

# ---------------------------------------------------------
# 1. Number of observations per IP
# ---------------------------------------------------------

print("\n=== OBSERVATIONS PER IP ===")

ip_history = (
    df
    .groupBy("ip")
    .agg(
        count("*").alias("observation_count")
    )
)

ip_history.select(
    percentile_approx("observation_count", 0.50, 10000).alias("p50"),
    percentile_approx("observation_count", 0.75, 10000).alias("p75"),
    percentile_approx("observation_count", 0.90, 10000).alias("p90"),
    percentile_approx("observation_count", 0.95, 10000).alias("p95"),
    percentile_approx("observation_count", 0.99, 10000).alias("p99"),
    max("observation_count").alias("max")
).show(truncate=False)

# ---------------------------------------------------------
# 2. Number of IPs with enough history
# ---------------------------------------------------------

print("\n=== HISTORY AVAILABILITY ===")

ip_history.select(
    count("*").alias("unique_ips"),
).show()

for threshold in [1, 3, 5, 10, 20]:
    count_ips = (
        ip_history
        .filter(col("observation_count") >= threshold)
        .count()
    )

    print(
        f"IPs with >= {threshold} observations: "
        f"{count_ips}"
    )

# ---------------------------------------------------------
# 3. Error-rate behavior for IPs with >= 5 observations
# ---------------------------------------------------------

print("\n=== ERROR RATE FOR IPS WITH >= 5 OBSERVATIONS ===")

eligible_ips = (
    ip_history
    .filter(col("observation_count") >= 5)
    .select("ip")
)

eligible_df = df.join(
    eligible_ips,
    on="ip",
    how="inner"
)

eligible_df.select(
    percentile_approx("error_rate", 0.50, 10000).alias("p50"),
    percentile_approx("error_rate", 0.75, 10000).alias("p75"),
    percentile_approx("error_rate", 0.90, 10000).alias("p90"),
    percentile_approx("error_rate", 0.95, 10000).alias("p95"),
    percentile_approx("error_rate", 0.99, 10000).alias("p99"),
    max("error_rate").alias("max")
).show(truncate=False)

# ---------------------------------------------------------
# 4. How many IPs have errors in their history?
# ---------------------------------------------------------

print("\n=== IP ERROR HISTORY ===")

ip_error_history = (
    eligible_df
    .groupBy("ip")
    .agg(
        count("*").alias("windows"),
        avg("error_rate").alias("avg_error_rate"),
        max("error_rate").alias("max_error_rate"),
        spark_sum(
    (col("error_requests") > 0).cast("int")
).alias("windows_with_errors")
    )
)

ip_error_history.select(
    percentile_approx(
        "windows_with_errors", 0.50, 10000
    ).alias("p50"),
    percentile_approx(
        "windows_with_errors", 0.75, 10000
    ).alias("p75"),
    percentile_approx(
        "windows_with_errors", 0.90, 10000
    ).alias("p90"),
    percentile_approx(
        "windows_with_errors", 0.95, 10000
    ).alias("p95"),
    percentile_approx(
        "windows_with_errors", 0.99, 10000
    ).alias("p99"),
    max("windows_with_errors").alias("max")
).show(truncate=False)

# ---------------------------------------------------------
# 5. Historical error-rate examples
# ---------------------------------------------------------

print("\n=== IPS WITH HIGH HISTORICAL ERROR RATES ===")

(
    ip_error_history
    .filter(col("windows_with_errors") > 0)
    .orderBy(
        col("max_error_rate").desc(),
        col("windows_with_errors").desc()
    )
    .show(20, truncate=False)
)

# ---------------------------------------------------------
# 6. Validate history recency
# ---------------------------------------------------------

print("\n=== HISTORY RECENCY ===")

ip_time = (
    eligible_df
    .groupBy("ip")
    .agg(
        min("window_start").alias("first_window"),
        max("window_start").alias("last_window")
    )
    .withColumn(
        "history_span_hours",
        (
            unix_timestamp("last_window")
            - unix_timestamp("first_window")
        ) / 3600
    )
)

ip_time.select(
    percentile_approx(
        "history_span_hours", 0.50, 10000
    ).alias("p50"),
    percentile_approx(
        "history_span_hours", 0.75, 10000
    ).alias("p75"),
    percentile_approx(
        "history_span_hours", 0.90, 10000
    ).alias("p90"),
    percentile_approx(
        "history_span_hours", 0.95, 10000
    ).alias("p95"),
    percentile_approx(
        "history_span_hours", 0.99, 10000
    ).alias("p99"),
    max("history_span_hours").alias("max")
).show(truncate=False)

spark.stop()
