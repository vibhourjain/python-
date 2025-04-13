def insert_metrics_to_duckdb(con, table_name, app_name, reference_date):
    sql = f"""
    DELETE FROM capacity_planning.metrics_summary
    WHERE application_name = '{app_name}' AND reference_date = DATE '{reference_date}';

    WITH
    baseline AS (
        SELECT
            application_type AS app_type,
            MAX(volume) OVER(PARTITION BY application_type) AS base_data_max_vol,
            ABS(ROUND(AVG(volume) OVER(PARTITION BY application_type), 0)) AS base_data_avg_vol,
            ROW_NUMBER() OVER(PARTITION BY application_type ORDER BY 1) AS base_data_row
        FROM {table_name}
        WHERE Period >= (DATE '{reference_date}' - INTERVAL 13 MONTH + INTERVAL 1 DAY)
        QUALIFY base_data_row = 1
    ),
    current_qtr AS (
        SELECT
            application_type AS app_type,
            MAX(volume) OVER(PARTITION BY application_type) AS curr_qtr_max_vol,
            ABS(ROUND(AVG(volume) OVER(PARTITION BY application_type), 0)) AS curr_qtr_avg_vol,
            ROW_NUMBER() OVER(PARTITION BY application_type ORDER BY 1) AS curr_qtr_row
        FROM {table_name}
        WHERE Period >= (DATE '{reference_date}' - INTERVAL 3 MONTH + INTERVAL 1 DAY)
        QUALIFY curr_qtr_row = 1
    ),
    previous_qtr AS (
        SELECT
            application_type AS app_type,
            MAX(volume) OVER(PARTITION BY application_type) AS prev_qtr_max_vol,
            ABS(ROUND(AVG(volume) OVER(PARTITION BY application_type), 0)) AS prev_qtr_avg_vol,
            ROW_NUMBER() OVER(PARTITION BY application_type ORDER BY 1) AS prev_qtr_row
        FROM {table_name}
        WHERE Period >= (DATE '{reference_date}' - INTERVAL 6 MONTH + INTERVAL 1 DAY)
          AND Period < (DATE '{reference_date}' - INTERVAL 3 MONTH + INTERVAL 1 DAY)
        QUALIFY prev_qtr_row = 1
    )

    INSERT INTO capacity_planning.metrics_summary
    SELECT '{app_name}' AS application_name, '{reference_date}' AS reference_date, t.*
    FROM (
        SELECT b.app_type,
            'Avg' AS metric,
            base_data_avg_vol AS baseline_13m,
            curr_qtr_avg_vol AS current_qtr,
            CASE WHEN base_data_avg_vol = 0 THEN 0.00 ELSE ROUND(((curr_qtr_avg_vol - base_data_avg_vol) / base_data_avg_vol) * 100, 1) END AS diff_baseline_pct,
            prev_qtr_avg_vol AS previous_qtr,
            CASE WHEN prev_qtr_avg_vol = 0 THEN 0.00 ELSE ROUND(((curr_qtr_avg_vol - prev_qtr_avg_vol) / prev_qtr_avg_vol) * 100, 1) END AS diff_qoq_pct
        FROM baseline b
        LEFT JOIN current_qtr c ON b.app_type = c.app_type
        LEFT JOIN previous_qtr p ON b.app_type = p.app_type

        UNION ALL

        SELECT b.app_type,
            'Peak' AS metric,
            base_data_max_vol AS baseline_13m,
            curr_qtr_max_vol AS current_qtr,
            CASE WHEN base_data_max_vol = 0 THEN 0.00 ELSE ROUND(((curr_qtr_max_vol - base_data_max_vol) / base_data_max_vol) * 100, 1) END AS diff_baseline_pct,
            prev_qtr_max_vol AS previous_qtr,
            CASE WHEN prev_qtr_max_vol = 0 THEN 0.00 ELSE ROUND(((curr_qtr_max_vol - prev_qtr_max_vol) / prev_qtr_max_vol) * 100, 1) END AS diff_qoq_pct
        FROM baseline b
        LEFT JOIN current_qtr c ON b.app_type = c.app_type
        LEFT JOIN previous_qtr p ON b.app_type = p.app_type
    ) t
    ORDER BY app_type, metric;
    """
    con.execute(sql)


def insert_peaks_to_duckdb(con, table_name, app_name, reference_date):
    sql = f"""
    DELETE FROM capacity_planning.peak_summary
    WHERE application_name = '{app_name}' AND reference_date = DATE '{reference_date}';

    INSERT INTO capacity_planning.peak_summary
    SELECT
        '{app_name}' AS application_name,
        '{reference_date}' AS reference_date,
        CONCAT('Peak - ', application_type, ' = ', volume, ' (', period, ')') AS PK_ROW
    FROM (
        SELECT application_type, volume, period,
            ROW_NUMBER() OVER(PARTITION BY application_type ORDER BY volume DESC) AS rnum_peak
        FROM {table_name}
        QUALIFY rnum_peak = 1
    )
    """
    con.execute(sql)
