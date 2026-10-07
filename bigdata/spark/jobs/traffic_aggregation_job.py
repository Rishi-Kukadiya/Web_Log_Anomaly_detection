from pyspark.sql import SparkSession

from bigdata.spark.transformations.traffic_aggregation import aggregate_traffic


INPUT_PATH = "hdfs://node1:9000/data/access_logs/access_logs.parquet"
OUTPUT_PATH = "hdfs://node1:9000/data/traffic_aggregation/traffic_5min.parquet"


def main():
    spark = (
    SparkSession.builder
    .appName("TrafficAggregation")
    .getOrCreate()
)

    print("\n=== Reading Access Logs ===")

    df = spark.read.parquet(INPUT_PATH)

    print(f"Input records: {df.count()}")

    print("\n=== Aggregating Traffic ===")

    traffic_df = aggregate_traffic(df)

    print("\n=== Traffic Aggregation Schema ===")
    traffic_df.printSchema()

    print("\n=== Sample Aggregated Records ===")
    traffic_df.orderBy("window_start", "ip").show(20, truncate=False)

    print("\n=== Aggregated Record Count ===")
    print(traffic_df.count())

    print("\n=== Writing Output ===")

    traffic_df.write.mode("overwrite").parquet(OUTPUT_PATH)

    print(f"Output written to: {OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()