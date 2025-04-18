import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.io as pio
from datetime import datetime, timedelta
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

DB_PATH = r"C:\Users\vibho\ado-0001\python-\capacity_planning_v3.duckdb"


def get_duckdb_schema(table_name):
    """Retrieve table schema from DuckDB"""
    schema = {}
    conn = duckdb.connect(DB_PATH)
    try:
        result = conn.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """).fetchdf()
        schema = dict(zip(result['column_name'], result['data_type']))
        logger.info(f"Schema for {table_name}: {schema}")
    except Exception as e:
        logger.error(f"Schema fetch error: {str(e)}")
        st.error(f"Schema fetch error: {str(e)}")
    finally:
        conn.close()
    return schema


def fetch_last_13_months_data(table_name, date_column, reference_date):
    """Retrieve data from DuckDB for the last 13 months"""
    conn = duckdb.connect(DB_PATH)
    start_date = reference_date - timedelta(days=13 * 30)
    try:
        query = f"""
            SELECT * FROM {table_name}
            WHERE {date_column} BETWEEN '{start_date}' AND '{reference_date}'
            ORDER BY {date_column} ASC
        """
        df = conn.execute(query).fetchdf()
        date_columns = [col for col in df.columns if df[col].dtype in('time' or 'timestamp_ns') or 'date' in str(df[col].dtype).lower()]
        logger.info(f"Fetched {len(df)} rows from {table_name}")
        return df
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()


def generate_cap_plan_visual():
    st.title("Interactive Data Visualization")

    conn = duckdb.connect(DB_PATH)
    apps = conn.execute("SELECT distinct application FROM capacity_planning.query_metadata where is_active ='Y' order by application ").fetchdf()["application"].tolist()
    conn.close()
    logger.info(f"now fetching apps name: {apps}")

    selected_app = st.selectbox("Select Application", apps)
    if selected_app:
        conn = duckdb.connect(DB_PATH)
        try:
            table_name = \
            conn.execute(f"SELECT MAX(target_table) target_table FROM capacity_planning.query_metadata WHERE 1=1 and is_active = 'Y' AND application = '{selected_app}'").fetchone()[0]
        except Exception as e:
            logger.error(f"Error fetching table name: {str(e)}")
            st.error(f"Error fetching table name: {str(e)}")
            return
        finally:
            conn.close()

        schema = get_duckdb_schema(table_name)
        date_columns = [col for col, dtype in schema.items() if dtype.lower() in ["timestamp_ns","date","time"]]

        if not date_columns:
            st.error("No date columns found in the table.")
            return

        selected_date_column = st.selectbox("Select Date Column", date_columns)
        reference_date = st.date_input("Select Reference Date", datetime.today())
        data_key = f"data_{selected_app}"
        if st.button("Fetch Data"):
            st.session_state[data_key] = fetch_last_13_months_data(table_name, selected_date_column, reference_date)

        if data_key in st.session_state:
            df = st.session_state[data_key]

            if df.empty:
                st.warning("No data found for the selected filters.")
                return

            filter_columns = [col for col in df.columns if col not in date_columns]
            for col in filter_columns:
                unique_vals = df[col].unique()
                selected_vals = st.multiselect(f"Filter by {col} (Optional)", unique_vals)
                if selected_vals:
                    df = df[df[col].isin(selected_vals)]

            aggregation_options = {"None": None, "Day": "D", "Month": "ME", "Quarter": "Q", "Year": "Y"}
            selected_aggregation = st.selectbox("Aggregate By (Optional)", list(aggregation_options.keys()))

            if selected_aggregation != "None":
                df[selected_date_column] = pd.to_datetime(df[selected_date_column])
                df = df.resample(aggregation_options[selected_aggregation], on=selected_date_column).sum().reset_index()

            graph_types = {"Line Chart": "line", "Bar Chart": "bar", "Scatter Plot": "scatter"}
            selected_graph_type = st.selectbox("Select Graph Type", list(graph_types.keys()))
            x_column = st.selectbox("Select X-Axis Column", df.columns, index=df.columns.get_loc(selected_date_column))
            y_columns = st.multiselect("Select Y-Axis Column(s)", df.columns, default=[df.columns[1]])
            color_column=st.selectbox("Select Graphs Hues", df.columns)

            fig = px.__getattribute__(graph_types[selected_graph_type])(df, x=x_column, y=y_columns, color=color_column,
                                                                        title=f"{selected_app} - {selected_graph_type}")
            tick_values = [df[x_column].min()] + df[x_column].iloc[::6].to_list()[1:]
            fig.update_layout(
                xaxis = dict(
                    tick0=df[x_column].min(),
                    tickvals=tick_values
                )
            )
            st.plotly_chart(fig)
