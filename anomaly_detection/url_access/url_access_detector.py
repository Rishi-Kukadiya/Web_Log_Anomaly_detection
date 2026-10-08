from pyspark.sql import DataFrame, Window
from pyspark.sql.functions import (
    col,
    count,
    min,
    percentile_approx,
    when,
    abs as spark_abs,
    unix_timestamp
)

MIN_HISTORY = 5
ROBUST_Z_THRESHOLD = 3.5
MAX_HISTORY_AGE_HOURS = 24


def detect_url_access_anomalies(df: DataFrame) -> DataFrame:

    history_window = (
        Window
        .partitionBy("ip")
        .orderBy("window_start")
        .rowsBetween(-MIN_HISTORY, -1)
    )

    result = (
        df
        .withColumn(
            "history_count",
            count("*").over(history_window)
        )
        .withColumn(
            "baseline_median",
            percentile_approx(
                "unique_url_count",
                0.5,
                10000
            ).over(history_window)
        )
        .withColumn(
            "oldest_history",
            min("window_start").over(history_window)
        )
    )

    result = result.withColumn(
        "history_age_hours",
        (
            unix_timestamp(col("window_start"))
            - unix_timestamp(col("oldest_history"))
        ) / 3600.0
    )

    result = result.withColumn(
        "absolute_deviation",
        spark_abs(
            col("unique_url_count") - col("baseline_median")
        )
    )

    result = result.withColumn(
        "mad",
        percentile_approx(
            "absolute_deviation",
            0.5,
            10000
        ).over(history_window)
    )

    result = result.withColumn(
        "robust_z_score",
        when(
            col("mad") > 0,
            (
                col("unique_url_count")
                - col("baseline_median")
            ) / (1.4826 * col("mad"))
        )
    )

    sufficient_history = (
        col("history_count") >= MIN_HISTORY
    )

    recent_history = (
        col("history_age_hours") <= MAX_HISTORY_AGE_HOURS
    )

    robust_anomaly = (
        (col("mad") > 0)
        &
        (col("robust_z_score") >= ROBUST_Z_THRESHOLD)
    )

    # Zero-MAD fallback.
    # Require a substantial increase over the historical median.
    zero_mad_threshold = when(
        col("baseline_median") * 3
        > col("baseline_median") + 5,
        col("baseline_median") * 3
    ).otherwise(
        col("baseline_median") + 5
    )

    zero_mad_anomaly = (
        (col("mad") == 0)
        &
        (
            col("unique_url_count")
            >= zero_mad_threshold
        )
    )

    result = result.withColumn(
        "is_url_access_anomaly",
        sufficient_history
        & recent_history
        & (
            robust_anomaly
            | zero_mad_anomaly
        )
    )

    return result.select(
        "ip",
        "window_start",
        "window_end",
        "unique_url_count",
        "history_count",
        "baseline_median",
        "mad",
        "history_age_hours",
        "robust_z_score",
        "is_url_access_anomaly"
    )