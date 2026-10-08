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


# ---------------------------------------------------------
# Detection Parameters
# ---------------------------------------------------------

MIN_HISTORY = 5
ROBUST_Z_THRESHOLD = 3.5
MAX_HISTORY_AGE_HOURS = 24
MIN_REQUESTS = 5
MIN_ERROR_RATE_INCREASE = 0.20


def detect_error_rate_anomalies(df: DataFrame) -> DataFrame:

    # ---------------------------------------------------------
    # Previous 5 observed windows for each IP
    # ---------------------------------------------------------

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
                "error_rate",
                0.5,
                10000
            ).over(history_window)
        )
        .withColumn(
            "oldest_history",
            min("window_start").over(history_window)
        )
    )

    # ---------------------------------------------------------
    # Age of oldest historical observation
    #
    # Spark 4.1.3 compatible approach:
    # convert timestamps to Unix seconds and calculate difference
    # ---------------------------------------------------------

    result = result.withColumn(
        "history_age_hours",
        (
            unix_timestamp(col("window_start"))
            - unix_timestamp(col("oldest_history"))
        ) / 3600.0
    )

    # ---------------------------------------------------------
    # Absolute deviation from historical median
    # ---------------------------------------------------------

    result = result.withColumn(
        "absolute_deviation",
        spark_abs(
            col("error_rate") - col("baseline_median")
        )
    )

    # ---------------------------------------------------------
    # Median Absolute Deviation (MAD)
    # ---------------------------------------------------------

    result = result.withColumn(
        "mad",
        percentile_approx(
            "absolute_deviation",
            0.5,
            10000
        ).over(history_window)
    )

    # ---------------------------------------------------------
    # Robust Z-score
    #
    # robust_z =
    # (current_error_rate - historical_median)
    # / (1.4826 * MAD)
    # ---------------------------------------------------------

    result = result.withColumn(
        "robust_z_score",
        when(
            col("mad") > 0,
            (
                col("error_rate")
                - col("baseline_median")
            ) / (1.4826 * col("mad"))
        )
    )

    # ---------------------------------------------------------
    # Detection Conditions
    # ---------------------------------------------------------

    # At least 5 previous observations
    sufficient_history = (
        col("history_count") >= MIN_HISTORY
    )

    # Historical data must be recent enough
    recent_history = (
        col("history_age_hours") <= MAX_HISTORY_AGE_HOURS
    )

    # Avoid treating 1 request + 1 error as an anomaly
    sufficient_volume = (
        col("total_requests") >= MIN_REQUESTS
    )

    # ---------------------------------------------------------
    # Case 1: MAD > 0
    # ---------------------------------------------------------

    robust_anomaly = (
        (col("mad") > 0)
        &
        (col("robust_z_score") >= ROBUST_Z_THRESHOLD)
    )

    # ---------------------------------------------------------
    # Case 2: MAD == 0
    #
    # Prevent division by zero.
    #
    # Threshold:
    # max(
    #     3 * historical median,
    #     historical median + 0.20
    # )
    # ---------------------------------------------------------

    zero_mad_threshold = when(
        col("baseline_median") * 3
        >
        col("baseline_median") + MIN_ERROR_RATE_INCREASE,

        col("baseline_median") * 3

    ).otherwise(
        col("baseline_median")
        + MIN_ERROR_RATE_INCREASE
    )

    zero_mad_anomaly = (
        (col("mad") == 0)
        &
        (
            col("error_rate")
            >= zero_mad_threshold
        )
    )

    # ---------------------------------------------------------
    # Final anomaly decision
    # ---------------------------------------------------------

    result = result.withColumn(
        "is_error_rate_anomaly",
        (
            sufficient_history
            &
            recent_history
            &
            sufficient_volume
            &
            (
                robust_anomaly
                |
                zero_mad_anomaly
            )
        )
    )

    # ---------------------------------------------------------
    # Final Output Schema
    # ---------------------------------------------------------

    return result.select(
        "ip",
        "window_start",
        "window_end",
        "total_requests",
        "error_requests",
        "error_rate",
        "history_count",
        "baseline_median",
        "mad",
        "history_age_hours",
        "robust_z_score",
        "is_error_rate_anomaly"
    )