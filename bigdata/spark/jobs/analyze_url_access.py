from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    percentile_approx,
    min as spark_min,
    max as spark_max,
    avg
)


spark = (
    SparkSession.builder
    .appName("AnalyzeURLAccess")
    .getOrCreate()
)


INPUT_PATH = (
    "hdfs://node1:9000/data/url_access_aggregation/"
    "url_access_5min.parquet"
)


# ---------------------------------------------------------
# Read data
# ---------------------------------------------------------

df = spark.read.parquet(INPUT_PATH)


print("\n=== TOTAL RECORDS ===")
print(df.count())


print("\n=== SCHEMA ===")
df.printSchema()


# ---------------------------------------------------------
# Global unique URL distribution
# ---------------------------------------------------------

print("\n=== UNIQUE URL COUNT DISTRIBUTION ===")

(
    df
    .select(
        spark_min("unique_url_count").alias("min"),
        percentile_approx(
            "unique_url_count",
            0.50,
            10000
        ).alias("p50"),
        percentile_approx(
            "unique_url_count",
            0.75,
            10000
        ).alias("p75"),
        percentile_approx(
            "unique_url_count",
            0.90,
            10000
        ).alias("p90"),
        percentile_approx(
            "unique_url_count",
            0.95,
            10000
        ).alias("p95"),
        percentile_approx(
            "unique_url_count",
            0.99,
            10000
        ).alias("p99"),
        percentile_approx(
            "unique_url_count",
            0.999,
            10000
        ).alias("p99.9"),
        spark_max("unique_url_count").alias("max"),
        avg("unique_url_count").alias("mean")
    )
    .show(truncate=False)
)


# ---------------------------------------------------------
# Per-IP observation history
# ---------------------------------------------------------

ip_history = (
    df
    .groupBy("ip")
    .agg(
        count("*").alias("observation_count")
    )
)


print("\n=== IP OBSERVATION DISTRIBUTION ===")

(
    ip_history
    .select(
        percentile_approx(
            "observation_count",
            0.50,
            10000
        ).alias("p50"),
        percentile_approx(
            "observation_count",
            0.75,
            10000
        ).alias("p75"),
        percentile_approx(
            "observation_count",
            0.90,
            10000
        ).alias("p90"),
        percentile_approx(
            "observation_count",
            0.95,
            10000
        ).alias("p95"),
        percentile_approx(
            "observation_count",
            0.99,
            10000
        ).alias("p99"),
        spark_max("observation_count").alias("max")
    )
    .show(truncate=False)
)


print("\n=== IPS WITH SUFFICIENT HISTORY ===")

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


spark.stop()
