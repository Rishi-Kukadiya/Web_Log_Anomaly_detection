from pyspark.sql import DataFrame
from pyspark.sql.functions import col, countDistinct, window


def aggregate_url_access(df: DataFrame) -> DataFrame:
    """
    Aggregate unique URL/resource access by IP address
    and fixed 5-minute windows.
    """

    url_access_df = (
        df
        .groupBy(
            col("ip"),
            window(col("timestamp"), "5 minutes")
        )
        .agg(
            countDistinct("url").alias("unique_url_count")
        )
        .select(
            col("ip"),
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("unique_url_count")
        )
    )

    return url_access_df