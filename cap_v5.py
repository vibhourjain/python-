import streamlit as st
import duckdb
import json
import os
from datetime import datetime
import pandas as pd
from ConnectSybase_Generic import connect_to_database, prepare_sql, execute_query

# Constants
DUCKDB_PATH = "sybase_data.duckdb"
SYBASE_CONFIG_PATH = "sybase_instances.json"
METADATA_TABLE = "capacity_planning.query_metadata"

# Load Sybase instance config from JSON
def load_sybase_config():
    with open(SYBASE_CONFIG_PATH, "r") as f:
        return {entry["sybase_instance"]: entry for entry in json.load(f)}

# Create necessary metadata table and schema
def initialize_duckdb():
    with duckdb.connect(DUCKDB_PATH) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS capacity_planning;")
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {METADATA_TABLE} (
                id BIGINT,
                query_name TEXT,
                sql_text TEXT,
                target_table TEXT,
                source_database TEXT,
                application TEXT
            )
        """)

# UI to insert new metadata records and upload .sql file
def metadata_manager():
    st.header("Metadata Table Setup")
    initialize_duckdb()

    st.subheader("Insert New SQL Metadata")
    query_name = st.text_input("Query Name")
    sql_file = st.file_uploader("Upload .sql file", type=["sql"])
    sql_text = sql_file.read().decode("utf-8") if sql_file else st.text_area("SQL Text")
    target_table = st.text_input("Target DuckDB Table")
    source_database = st.text_input("Sybase Instance (e.g., SD1)")
    application = st.text_input("Application Name")

    if st.button("Insert Metadata") and sql_text:
        with duckdb.connect(DUCKDB_PATH) as conn:
            max_id = conn.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {METADATA_TABLE}").fetchone()[0]
            conn.execute(f"""
                INSERT INTO {METADATA_TABLE} (id, query_name, sql_text, target_table, source_database, application)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (max_id, query_name, sql_text, target_table, source_database, application))
            st.success("Metadata inserted!")

    st.subheader("Existing Metadata")
    with duckdb.connect(DUCKDB_PATH) as conn:
        df = conn.execute(f"SELECT * FROM {METADATA_TABLE}").fetchdf()
        st.dataframe(df)

# Execute queries based on metadata

def data_loader():
    st.header("Run Monthly SQL Jobs")
    initialize_duckdb()

    start_date = st.date_input("Start Date", value=datetime.today())
    end_date = st.date_input("End Date", value=datetime.today())

    if st.button("Run Queries"):
        sybase_config = load_sybase_config()

        with duckdb.connect(DUCKDB_PATH) as duckdb_conn:
            metadata = duckdb_conn.execute(f"SELECT * FROM {METADATA_TABLE}").fetchdf()

            for _, row in metadata.iterrows():
                sql_template = row["sql_text"]
                instance = row["source_database"]
                target_table = row["target_table"]

                st.write(f"Running {row['query_name']} against {instance}...")

                conn = connect_to_database(instance, db_username="your_user", db_password="your_pass")
                if conn is None:
                    continue

                try:
                    sql, params = prepare_sql(
                        sql_template,
                        replacements={"start_date": str(start_date), "end_date": str(end_date)}
                    )

                    df = execute_query(conn, sql, params)
                    duckdb_conn.register("df", df)
                    duckdb_conn.execute(f"CREATE TABLE IF NOT EXISTS {target_table} AS SELECT * FROM df LIMIT 0")
                    duckdb_conn.execute(f"INSERT INTO {target_table} SELECT * FROM df")

                    csv_file = f"output_{row['query_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    df.to_csv(csv_file, index=False)
                    st.success(f"Loaded {len(df)} rows into {target_table}. Exported to {csv_file}")

                except Exception as e:
                    st.error(f"Error processing {row['query_name']}: {e}")

# Free SQL Runner Page
def duckdb_sql_runner():
    st.header("Run Custom SQL on DuckDB")
    initialize_duckdb()

    sql_input = st.text_area("Enter your DuckDB SQL:")

    if st.button("Run SQL"):
        try:
            with duckdb.connect(DUCKDB_PATH) as conn:
                df = conn.execute(sql_input).fetchdf()
                st.dataframe(df)
                csv_name = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(csv_name, index=False)
                st.success(f"Result exported to {csv_name}")
        except Exception as e:
            st.error(f"SQL execution error: {e}")

# Streamlit navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Metadata Setup", "Run Queries", "DuckDB SQL Runner"])

if page == "Metadata Setup":
    metadata_manager()
elif page == "Run Queries":
    data_loader()
elif page == "DuckDB SQL Runner":
    duckdb_sql_runner()
