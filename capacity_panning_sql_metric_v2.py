
def insert_metrics_to_duckdb(con, table_name, app_name, reference_date):

    sql = f"""
    WITH
baseline AS
(
    SELECT
        application_type AS application_type_b,
        MAX(volume) OVER( PARTITION BY application_type ORDER BY 1 DESC) AS base_data_max_vol,
        ABS(ROUND(AVG(volume) OVER( PARTITION BY application_type ORDER BY 1),0)) AS base_data_avg_vol,
        ROW_NUMBER() OVER( PARTITION BY application_type ORDER BY 1) AS base_data_row
    FROM {table_name}
    WHERE 1=1
    AND Period = (DATE '{reference_date}' - INTERVAL 13 MONTH + INTERVAL 1 DAY)
    QUALIFY base_data_row = 1
),
current_qtr AS
(
    SELECT
        application_type AS application_type_c,
        MAX(volume) OVER( PARTITION BY application_type ORDER BY 1 DESC) AS curr_qtr_max_vol,
        ABS(ROUND(AVG(volume) OVER( PARTITION BY application_type ORDER BY 1),0)) AS curr_qtr_avg_vol,
        ROW_NUMBER() OVER( PARTITION BY application_type ORDER BY 1) AS curr_qtr_row
    FROM {table_name}
    WHERE 1=1
    AND Period >= (DATE '{reference_date}' - INTERVAL 3 MONTH + INTERVAL 1 DAY)
    QUALIFY curr_qtr_row = 1
),
previous_qtr AS
(
    SELECT
        application_type AS application_type_p,
        MAX(volume) OVER( PARTITION BY application_type ORDER BY 1 DESC) AS prev_qtr_max_vol,
        ABS(ROUND(AVG(volume) OVER( PARTITION BY application_type ORDER BY 1),0)) AS prev_qtr_avg_vol,
        ROW_NUMBER() OVER( PARTITION BY application_type ORDER BY 1) AS prev_qtr_row
    FROM {table_name}
    WHERE 1=1
    AND Period >= (DATE '{reference_date}' - INTERVAL 6 MONTH + INTERVAL 1 DAY)
    AND Period < (DATE '{reference_date}' - INTERVAL 3 MONTH + INTERVAL 1 DAY)
    QUALIFY prev_qtr_row = 1
)
INSERT INTO capacity_planning.metrics_summary
SELECT '{app_name}' AS application_name, '{reference_date}' AS reference_date, t.*
FROM (
    SELECT application_type_b AS "Type",
        'Avg' AS "Metric",
        base_data_avg_vol AS "Baseline(13 Month)",
        curr_qtr_avg_vol AS "Current Qtr",
        CASE WHEN base_data_avg_vol = 0 THEN 0.00 ELSE ROUND(((curr_qtr_avg_vol - base_data_avg_vol) / base_data_avg_vol) * 100, 1) END AS "% Diff Baseline",
        prev_qtr_avg_vol AS "Previous Qtr",
        CASE WHEN prev_qtr_avg_vol = 0 THEN 0.00 ELSE ROUND(((curr_qtr_avg_vol - prev_qtr_avg_vol) / prev_qtr_avg_vol) * 100, 1) END AS "% Diff QoQ"
    FROM baseline b
    LEFT JOIN current_qtr c ON (b.application_type_b = c.application_type_c)
    LEFT JOIN previous_qtr p ON (b.application_type_b = p.application_type_p)

    UNION ALL

    SELECT application_type_b AS "Type",
        'Peak' AS "Metric",
        base_data_max_vol AS "Baseline(13 Month)",
        curr_qtr_max_vol AS "Current Qtr",
        CASE WHEN base_data_max_vol = 0 THEN 0.00 ELSE ROUND(((curr_qtr_max_vol - base_data_max_vol) / base_data_max_vol) * 100, 1) END AS "%Diff Baseline",
        prev_qtr_max_vol AS "Previous Qtr",
        CASE WHEN prev_qtr_max_vol = 0 THEN 0.00 ELSE ROUND(((curr_qtr_max_vol - prev_qtr_max_vol) / prev_qtr_max_vol) * 100, 1) END AS "% Diff QoQ"
    FROM baseline b
    LEFT JOIN current_qtr c ON (b.application_type_b = c.application_type_c)
    LEFT JOIN previous_qtr p ON (b.application_type_b = p.application_type_p)
) t
ORDER BY "Type", "Metric" 
    """
    con.execute(sql)

def insert_peaks_to_duckdb(con, table_name, app_name, reference_date):

    sql = f"""
        INSERT INTO capacity_planning.peak_summary
        SELECT
        '{app_name}' AS application_name, '{reference_date}' AS reference_date,
        CONCAT('Peak - ',application_type, ' = ',volume,' (',period,')') AS PK_ROW FROM(
SELECT application_type, volume, period, ROW_NUMBER() 
OVER (PARTITION BY application_type ORDER BY volume DESC) AS rnum_peak
from {table_name}
qualify rnum_peak=1)
"""
    con.execute(sql)
