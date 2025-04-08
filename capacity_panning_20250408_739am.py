import streamlit as st
import duckdb
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from ConnectSybase_Generic import connect_to_database, prepare_sql, execute_query

# Constants
DUCKDB_PATH = "sybase_data.duckdb"
SYBASE_CONFIG_PATH = "sybase_instances.json"
METADATA_TABLE = "capacity_planning.query_metadata"
APPLICATION_TABLE = "capacity_planning.application"

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
                application TEXT,
                execution_order INTEGER
            )
        """)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {APPLICATION_TABLE} (
                app_name TEXT,
                app_type TEXT,
                bv_date DATE,
                count_rec INTEGER,
                start_date DATE
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
    execution_order = st.number_input("Execution Order", min_value=1, value=1)

    if st.button("Insert Metadata") and sql_text:
        with duckdb.connect(DUCKDB_PATH) as conn:
            max_id = conn.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {METADATA_TABLE}").fetchone()[0]
            conn.execute(f"""
                INSERT INTO {METADATA_TABLE} (id, query_name, sql_text, target_table, source_database, application, execution_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (max_id, query_name, sql_text, target_table, source_database, application, execution_order))
            st.success("Metadata inserted!")

    st.subheader("Existing Metadata")
    with duckdb.connect(DUCKDB_PATH) as conn:
        df = conn.execute(f"SELECT * FROM {METADATA_TABLE}").fetchdf()
        st.dataframe(df)

# Execute queries based on metadata

def data_loader():
    st.header("Run Monthly SQL Jobs")
    initialize_duckdb()

    end_date = st.date_input("End Date", value=datetime.today())

    if st.button("Run Queries"):
        sybase_config = load_sybase_config()

        with duckdb.connect(DUCKDB_PATH) as duckdb_conn:
            metadata = duckdb_conn.execute(f"SELECT * FROM {METADATA_TABLE} ORDER BY execution_order").fetchdf()

            for _, row in metadata.iterrows():
                sql_template = row["sql_text"]
                instance = row["source_database"]
                target_table = row["target_table"]
                app_name = row["application"]

                result = duckdb_conn.execute(f"SELECT COALESCE(MAX(start_date), DATE '2000-01-01') FROM {APPLICATION_TABLE} WHERE app_name = ?", (app_name,)).fetchone()
                start_date = result[0] + timedelta(days=1)

                st.write(f"Running {row['query_name']} for {app_name} from {start_date} to {end_date}...")

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

                    duckdb_conn.execute(f"""
                        INSERT INTO {APPLICATION_TABLE} (app_name, app_type, bv_date, count_rec, start_date)
                        VALUES (?, 'monthly', ?, ?, ?)
                    """, (app_name, datetime.now().date(), len(df), start_date))

                except Exception as e:
                    st.error(f"Error processing {row['query_name']}: {e}")

# Page to edit metadata

def metadata_editor():
    st.header("Edit Metadata")
    initialize_duckdb()

    # id,
    # query_name,
    # sql_text,
    # target_table,
    # source_database,
    # application,
    # execution_order,

    with duckdb.connect(DUCKDB_PATH) as conn:
        ids = conn.execute(f"SELECT query_name FROM {METADATA_TABLE}").fetchdf()["id"].tolist()

    selected_query_name = st.selectbox("Select Metadata Query Name to Edit", ids)

    if selected_query_name:
        with duckdb.connect(DUCKDB_PATH) as conn:
            row = conn.execute(f"SELECT * FROM {METADATA_TABLE} WHERE id = ?", (selected_query_name,)).fetchone()

        query_name = st.text_input("Query Name", row[1])
        sql_text = st.text_area("SQL Text", row[2])
        target_table = st.text_input("Target DuckDB Table", row[3])
        source_database = st.text_input("Sybase Instance", row[4])
        application = st.text_input("Application Name", row[5])

        if st.button("Update Metadata"):
            with duckdb.connect(DUCKDB_PATH) as conn:
                conn.execute(f"""
                    UPDATE {METADATA_TABLE}
                    SET query_name = ?, sql_text = ?, target_table = ?, source_database = ?, application = ?
                    WHERE query_name = ?
                """, (query_name, sql_text, target_table, source_database, application, selected_query_name))
                st.success("Metadata updated successfully!")

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
page = st.sidebar.radio("Go to", ["Metadata Setup", "Metadata Editor","Run Queries", "DuckDB SQL Runner"])

if page == "Metadata Setup":
    metadata_manager()
elif page == "Run Queries":
    data_loader()
elif page == "DuckDB SQL Runner":
    duckdb_sql_runner()
elif page == "Metadata Editor":
    metadata_editor()
