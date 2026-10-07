from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, window


def aggregate_traffic(df: DataFrame) -> DataFrame:
    """
    Aggregate web requests by IP address and fixed 5-minute windows.
    """

    traffic_df = (
        df
        .groupBy(
            col("ip"),
            window(col("timestamp"), "5 minutes")
        )
        .agg(
            count("*").alias("request_count")
        )
        .select(
            col("ip"),
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("request_count")
        )
    )

    return traffic_df