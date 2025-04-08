import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.io as pio
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database Path
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
    start_date = reference_date - timedelta(days=13 * 30)  # Approx 13 months
    try:
        query = f"""
            SELECT * FROM {table_name}
            WHERE {date_column} BETWEEN '{start_date}' AND '{reference_date}'
            ORDER BY {date_column} ASC
        """
        df = conn.execute(query).fetchdf()

        # Convert date columns explicitly
        date_columns = [col for col in df.columns if df[col].dtype == 'object' or 'date' in str(df[col].dtype).lower()]
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception as e:
                logger.error(f"Error converting column {col} to datetime: {str(e)}")
                st.error(f"Error converting column {col} to datetime: {str(e)}")

        logger.info(f"Fetched {len(df)} rows from {table_name}")
        return df
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()


def main():
    st.title("Interactive Data Visualization")

    conn = duckdb.connect(DB_PATH)
    apps = conn.execute("SELECT application_name FROM metadata").fetchdf()["application_name"].tolist()
    conn.close()

    selected_app = st.selectbox("Select Application", apps)
    if selected_app:
        conn = duckdb.connect(DB_PATH)
        try:
            table_name = \
            conn.execute(f"SELECT table_name FROM metadata WHERE application_name = '{selected_app}'").fetchone()[0]
        except Exception as e:
            logger.error(f"Error fetching table name: {str(e)}")
            st.error(f"Error fetching table name: {str(e)}")
            return
        finally:
            conn.close()

        schema = get_duckdb_schema(table_name)
        date_columns = [col for col, dtype in schema.items() if "date" in dtype.lower()]

        if not date_columns:
            st.error("No date columns found in the table.")
            return

        selected_date_column = st.selectbox("Select Date Column", date_columns)
        reference_date = st.date_input("Select Reference Date", datetime.today())

        data_key = f"data_{selected_app}"
        if st.button("Fetch Data") or data_key in st.session_state:
            if data_key not in st.session_state:
                st.session_state[data_key] = fetch_last_13_months_data(table_name, selected_date_column, reference_date)
            df = st.session_state[data_key]

            if df.empty:
                st.warning("No data found for the selected filters.")
                return

            # Filters
            filter_columns = [col for col in df.columns if col not in date_columns]
            for col in filter_columns:
                unique_vals = df[col].unique()
                selected_vals = st.multiselect(f"Filter by {col} (Optional)", unique_vals)
                if selected_vals:
                    df = df[df[col].isin(selected_vals)]

            # Date Aggregation (Optional)
            aggregation_options = {"None": None, "Day": "D", "Month": "M", "Quarter": "Q", "Year": "Y"}
            selected_aggregation = st.selectbox("Aggregate By (Optional)", list(aggregation_options.keys()))

            if selected_aggregation != "None":
                df[selected_date_column] = pd.to_datetime(df[selected_date_column])
                df = df.resample(aggregation_options[selected_aggregation], on=selected_date_column).sum().reset_index()

            # Graph Configuration
            graph_types = {"Line Chart": "line", "Bar Chart": "bar", "Scatter Plot": "scatter"}
            selected_graph_type = st.selectbox("Select Graph Type", list(graph_types.keys()))
            x_column = st.selectbox("Select X-Axis Column", df.columns, index=df.columns.get_loc(selected_date_column))
            y_columns = st.multiselect("Select Y-Axis Column(s)", df.columns, default=[df.columns[1]])

            # Generate Plotly Chart
            fig = px.__getattribute__(graph_types[selected_graph_type])(df, x=x_column, y=y_columns,
                                                                        title=f"{selected_app} - {selected_graph_type}")
            st.plotly_chart(fig)

            # Summary Statistics
            st.subheader("Summary Statistics")
            st.write(df.describe())

            # Export Graph as Image
            img_bytes = pio.to_image(fig, format="png")
            st.download_button("Download Graph", data=img_bytes, file_name="graph.png", mime="image/png")


if __name__ == "__main__":
    main()
