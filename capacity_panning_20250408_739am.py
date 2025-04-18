import streamlit as st
import duckdb
from datetime import datetime, timedelta
from ConnectSybase_Generic import connect_to_database, prepare_sql, execute_query_1
from ConnectSybase import execute_query
import logging
from capacity_planning_visual_v1 import capacity_planning_visual_v1
from capacity_planning_all_graphs_cg_v32 import gen_one_click_capacity_report
from Capacity_planning_pre_requiste import setup_duckdb_objects

logger = logging.getLogger(__name__)

DUCKDB_PATH = "sybase_data.duckdb"
METADATA_TABLE = "capacity_planning.query_metadata"
APPLICATION_TABLE = "capacity_planning.application"

def initialize_duckdb():
    setup_duckdb_objects()

def metadata_manager():
    st.header("Metadata Table Setup")
    st.subheader("Insert New SQL Metadata")
    query_name = st.text_input("Query Name")
    sql_file = st.file_uploader("Upload .sql file", type=["sql"])
    sql_text = sql_file.read().decode("utf-8") if sql_file else st.text_area("SQL Text")
    report_frequency = st.text_input("Report Frequency")
    target_table = st.text_input("Target DuckDB Table")
    source_database = st.text_input("Sybase Instance (e.g., SD1)")
    application = st.text_input("Application Name")
    app_capacity = st.text_input("Enter Application Capacity")
    metric_sql = st.text_area("Enter Metric SQL")
    peak_sql = st.text_area("Enter Peak SQL")
    execution_order = st.number_input("Execution Order", min_value=1, value=1)

    if st.button("Insert Metadata") and sql_text:
        with duckdb.connect(DUCKDB_PATH) as conn:
            max_id = conn.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {METADATA_TABLE}").fetchone()[0]
            conn.execute(f"""
                INSERT INTO {METADATA_TABLE} (id, query_name, sql_text, frequency, target_table, source_database, application, execution_order, metric_sql, peak_sql, app_capacity, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,'Y')
            """, (max_id, query_name, sql_text, report_frequency, target_table, source_database, application, execution_order,metric_sql, peak_sql, app_capacity))
            st.success("Metadata inserted!")

    st.subheader("Existing Metadata")
    with duckdb.connect(DUCKDB_PATH) as conn:
        df = conn.execute(f"SELECT * FROM {METADATA_TABLE}").fetchdf()
        st.dataframe(df)

def metadata_editor():
    st.header("Edit Metadata")

    with duckdb.connect(DUCKDB_PATH) as conn:
        ids = conn.execute(f"SELECT id FROM {METADATA_TABLE}").fetchdf()["id"].tolist()

    selected_id = st.selectbox("Select Metadata Query Id to Edit", ids)

    if selected_id:
        with duckdb.connect(DUCKDB_PATH) as conn:
            row = conn.execute(f"SELECT * FROM {METADATA_TABLE} WHERE id = ?", (selected_id,)).fetchone()

        query_name = st.text_input("Query Name", row[1])
        frequency = st.text_input("Report Frequency", row[2])
        sql_text = st.text_area("SQL Text", row[3])
        target_table = st.text_input("Target DuckDB Table", row[4])
        source_database = st.text_input("Sybase Instance", row[5])
        application = st.text_input("Application Name", row[6])
        execution_order = st.text_input("Execution Order", row[7])
        metric_sql = st.text_area("Metric SQL", row[8])
        peak_sql = st.text_area("Peak SQL", row[9])
        app_capacity = st.text_input("Application Capacity", row[10])
        is_active = st.text_input("Is Active SQL", row[11])

        if st.button("Update Metadata"):
            with duckdb.connect(DUCKDB_PATH) as conn:
                conn.execute(f"""
                    UPDATE {METADATA_TABLE}
                    SET query_name = ?, frequency = ?, sql_text = ?, target_table = ?, source_database = ?, application = ?, execution_order = ?,
                    metric_sql = ?, peak_sql = ?, app_capacity=?, is_active = ?
                    WHERE id = ?
                """, (query_name, frequency, sql_text, target_table,
                      source_database, application, execution_order, metric_sql, peak_sql, app_capacity, is_active, selected_id))
                st.success("Metadata updated successfully!")

def data_loader():
    st.header("Run Monthly SQL Jobs")

    end_date = st.date_input("End Date", value=datetime.today())

    if st.button("Run Queries"):

        with duckdb.connect(DUCKDB_PATH) as duckdb_conn:
            metadata = duckdb_conn.execute(f"SELECT * FROM {METADATA_TABLE} WHERE IS_ACTIVE = 'Y' ORDER BY execution_order").fetchdf()

            for _, row in metadata.iterrows():
                sql_template = row["sql_text"]
                instance = row["source_database"]
                target_table = row["target_table"]
                app_name = row["application"]
                query_name = row["query_name"]

                result = duckdb_conn.execute(f"SELECT COALESCE(MAX(end_date), DATE '2023-12-01') FROM {APPLICATION_TABLE} WHERE query_name = ?", (query_name,)).fetchone()
                start_date = result[0] + timedelta(days=1)

                st.write(f"Running {row['query_name']} for {app_name} from {start_date} to {end_date}...")

                conn = connect_to_database(instance, db_username="your_user", db_password="your_pass")
                if conn is None:
                    continue

                try:
                    sql, params = prepare_sql(
                        sql_template,
                        replacements={"start_date": start_date.strftime('%Y-%m-%d'), "end_date": end_date.strftime('%Y-%m-%d')}
                    )
                    df = execute_query(
                        conn,
                        sql_template,
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d')
                    )
                    datetime_columns = df.select_dtypes(include=['datetime64']).columns
                    for column in datetime_columns:
                        df[column] = df[column].dt.date

                    duckdb_conn.register("df", df)
                    duckdb_conn.execute(f"CREATE TABLE IF NOT EXISTS {target_table} AS SELECT * FROM df LIMIT 0")
                    duckdb_conn.execute(f"INSERT INTO {target_table} SELECT * FROM df")
                    st.success(f"Loaded {len(df)} rows into {target_table}.")
                    duckdb_conn.execute(f"""
                        INSERT INTO {APPLICATION_TABLE} (query_name, app_type, bv_date, count_rec, start_date, end_date)
                        VALUES (?, 'monthly', ?, ?, ?, ?)
                    """, (query_name, datetime.now().date(), len(df), start_date, end_date))
                    st.success(f"Capacity Planning Stage 1 Completed Data Insertion")

                except Exception as e:
                    st.error(f"Error processing {row['query_name']}: {e}")

def duckdb_sql_runner():
    st.header("Run Custom SQL on DuckDB")
    sql_input = st.text_area("Enter your DuckDB SQL:")

    if st.button("Run SQL"):
        try:
            with duckdb.connect(DUCKDB_PATH) as conn:
                df = conn.execute(sql_input).fetchdf()
                st.dataframe(df)
                st.success(f"Query Finished")
        except Exception as e:
            st.error(f"SQL execution error: {e}")

"""
Task Conquer
"""

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go To", ["Pre-Requisite Setup", "Metadata Configuration", "Metadata Editor", "Run Queries", "DuckDB SQL Runner", "Generate Visuals", "Generate Capacity Reports"])

if page == "Pre-Requisite Setup":
    initialize_duckdb()
elif page == "Metadata Configuration":
    metadata_manager()
elif page == "Metadata Editor":
    metadata_editor()
elif page == "Run Queries":
    data_loader()
elif page == "DuckDB SQL Runner":
    duckdb_sql_runner()
elif page == "Generate Visuals":
    generate_cap_plan_visual()
elif page == "Generate Capacity Reports":
    gen_one_click_capacity_report()
