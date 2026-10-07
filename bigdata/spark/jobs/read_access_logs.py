from pyspark.sql import SparkSession


def main():
    spark = (
        SparkSession.builder
        .appName("ReadAccessLogs")
        .master("local[*]")
        .getOrCreate()
    )

    input_path = "data/processed/access_logs/access_logs.parquet"

    df = spark.read.parquet(input_path)

    print("\n=== Schema ===")
    df.printSchema()

    print("\n=== Total Records ===")
    print(df.count())

    print("\n=== Sample Records ===")
    df.show(10, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()