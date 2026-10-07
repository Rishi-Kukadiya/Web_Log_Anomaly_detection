from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    abs,
    col,
    count,
    expr,
    lit,
    percentile_approx,
    when
)
from pyspark.sql.window import Window


MIN_HISTORY = 5
ROBUST_Z_THRESHOLD = 3.5
MAX_HISTORY_AGE_HOURS = 24


def detect_traffic_spikes(df: DataFrame) -> DataFrame:
    """
    Detect traffic spikes using an IP-specific historical baseline.

    Requirements:
    - At least 5 previous observations.
    - Historical observations must be within the previous 24 hours.
    - Median and MAD are used for robust outlier detection.
    - Special handling is used when MAD is zero.
    """

    # Previous 5 observed windows for each IP.
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
            count("request_count").over(history_window)
        )
        .withColumn(
            "baseline_median",
            percentile_approx(
                "request_count",
                0.5,
                10000
            ).over(history_window)
        )
        .withColumn(
            "oldest_history_window",
            expr(
                "min(window_start) OVER "
                "(PARTITION BY ip ORDER BY window_start "
                "ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING)"
            )
        )
    )

    # How old is the oldest observation used in the baseline?
    result = result.withColumn(
        "history_age_hours",
        (
            expr(
                "unix_timestamp(window_start) - "
                "unix_timestamp(oldest_history_window)"
            ) / 3600.0
        )
    )

    # Absolute deviation from historical median.
    result = result.withColumn(
        "absolute_deviation",
        abs(col("request_count") - col("baseline_median"))
    )

    # Median absolute deviation.
    result = result.withColumn(
        "mad",
        percentile_approx(
            "absolute_deviation",
            0.5,
            10000
        ).over(history_window)
    )

    # Robust Z-score.
    result = result.withColumn(
        "robust_z_score",
        when(
            col("mad") > 0,
            (
                col("request_count") - col("baseline_median")
            ) / (lit(1.4826) * col("mad"))
        ).otherwise(
            lit(0.0)
        )
    )

    # Zero-MAD fallback:
    # require a meaningful absolute increase.
    zero_mad_spike = (
        (col("mad") == 0) &
        (
            col("request_count") >=
            expr("GREATEST(baseline_median * 3, baseline_median + 5)")
        )
    )

    normal_mad_spike = (
        (col("mad") > 0) &
        (col("robust_z_score") >= ROBUST_Z_THRESHOLD)
    )

    sufficient_history = (
        (col("history_count") >= MIN_HISTORY) &
        (col("history_age_hours") <= MAX_HISTORY_AGE_HOURS)
    )

    result = result.withColumn(
        "is_traffic_spike",
        when(
            sufficient_history &
            (zero_mad_spike | normal_mad_spike),
            lit(True)
        ).otherwise(lit(False))
    )

    return result.select(
        "ip",
        "window_start",
        "window_end",
        "request_count",
        "history_count",
        "baseline_median",
        "mad",
        "history_age_hours",
        "robust_z_score",
        "is_traffic_spike"
    )