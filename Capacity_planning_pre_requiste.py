import duckdb
import streamlit as st

CREATE TABLE IF NOT EXISTS capacity_planning.metrics_summary (
    application TEXT,
    reference_date DATE,
    metric_name TEXT,
    metric_value TEXT
);

CREATE TABLE IF NOT EXISTS capacity_planning.metrics_summary (
    application_name TEXT,
    reference_date DATE,
    app_type TEXT,
    metric TEXT,
    baseline_13m DOUBLE,
    current_qtr DOUBLE,
    diff_baseline_pct DOUBLE,
    previous_qtr DOUBLE,
    diff_qoq_pct DOUBLE
);

CREATE TABLE IF NOT EXISTS capacity_planning.peak_summary (
    application_name TEXT,
    reference_date DATE,
    PK_ROW TEXT
);