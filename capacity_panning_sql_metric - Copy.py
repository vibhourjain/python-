import pandas as pd

def insert_metrics_to_duckdb(con, table_name, app_name, reference_date):
    start_baseline = reference_date - pd.DateOffset(months=13)
    start_current_qtr = reference_date - pd.DateOffset(months=3)
    start_prev_qtr = reference_date - pd.DateOffset(months=6)

    sql = f"""
    WITH 
    base AS (
        SELECT * FROM {table_name}
        WHERE Period BETWEEN DATE '{start_baseline.date()}' AND DATE '{reference_date}'
    ),
    curr_qtr AS (
        SELECT * FROM {table_name}
        WHERE Period BETWEEN DATE '{start_current_qtr.date()}' AND DATE '{reference_date}'
    ),
    prev_qtr AS (
        SELECT * FROM {table_name}
        WHERE Period BETWEEN DATE '{start_prev_qtr.date()}' AND DATE '{start_current_qtr.date()}' - INTERVAL 1 DAY
    ),
    stats AS (
        SELECT 
            MAX(base.Volume) AS baseline_max,
            AVG(base.Volume) AS baseline_avg,
            MAX(curr_qtr.Volume) AS current_max,
            AVG(curr_qtr.Volume) AS current_avg,
            MAX(prev_qtr.Volume) AS previous_max,
            AVG(prev_qtr.Volume) AS previous_avg
        FROM base, curr_qtr, prev_qtr
    ),
    metrics AS (
        SELECT '{app_name}' AS application, DATE '{reference_date}' AS reference_date,
            'Baseline AVG' AS metric_name, ROUND(baseline_avg, 0)::TEXT AS metric_value FROM stats
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', 'Current QTR MAX', ROUND(current_max, 0)::TEXT FROM stats
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', 'Current QTR AVG', ROUND(current_avg, 0)::TEXT FROM stats
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', 'Previous QTR MAX', ROUND(previous_max, 0)::TEXT FROM stats
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', 'Previous QTR AVG', ROUND(previous_avg, 0)::TEXT FROM stats
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', '% Diff (Base MAX vs Curr MAX)', 
            CASE WHEN baseline_max = 0 THEN '0.0%' ELSE ROUND(((current_max - baseline_max) / baseline_max) * 100, 1)::TEXT || '%' END 
        FROM stats
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', '% Diff (Base MAX vs Curr AVG)', 
            CASE WHEN baseline_max = 0 THEN '0.0%' ELSE ROUND(((current_avg - baseline_max) / baseline_max) * 100, 1)::TEXT || '%' END 
        FROM stats
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', '% Diff (Prev MAX vs Curr MAX)', 
            CASE WHEN previous_max = 0 THEN '0.0%' ELSE ROUND(((current_max - previous_max) / previous_max) * 100, 1)::TEXT || '%' END 
        FROM stats
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', '% Diff (Prev AVG vs Curr AVG)', 
            CASE WHEN previous_avg = 0 THEN '0.0%' ELSE ROUND(((current_avg - previous_avg) / previous_avg) * 100, 1)::TEXT || '%' END 
        FROM stats
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', 'Baseline MAX', 
            (SELECT ROUND(Volume, 0)::TEXT || ' (' || strftime(Period, '%Y-%m') || ')' 
             FROM {table_name}
             WHERE Period BETWEEN DATE '{start_baseline.date()}' AND DATE '{reference_date}'
             ORDER BY Volume DESC LIMIT 1)
        UNION ALL
        SELECT '{app_name}', DATE '{reference_date}', 'Peak', 
            (SELECT ROUND(Volume, 0)::TEXT || ' (' || strftime(Period, '%Y-%m') || ')' 
             FROM {table_name}
             WHERE Period BETWEEN DATE '{start_baseline.date()}' AND DATE '{reference_date}'
             ORDER BY Volume DESC LIMIT 1)
    )
    INSERT INTO capacity_planning.metrics_summary
    SELECT * FROM metrics
    """
    con.execute(sql)
