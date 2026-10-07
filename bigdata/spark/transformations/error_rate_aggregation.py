from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, sum, when , window


def aggregate_error_rate(df: DataFrame) -> DataFrame:
    """
    Aggregate HTTP error statistics by IP address
    and fixed 5-minute windows.
    """

    error_rate_df = (
        df
        .groupBy(
            col("ip"),
            window(col("timestamp"), "5 minutes")
        )
        .agg(
            count("*").alias("total_requests"),
            sum(
                when(col("status_code") >= 400, 1).otherwise(0)
            ).alias("error_requests")
        )
        .select(
            col("ip"),
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("total_requests"),
            col("error_requests")
        )
        .withColumn(
            "error_rate",
            col("error_requests") / col("total_requests")
        )
    )

    return error_rate_df