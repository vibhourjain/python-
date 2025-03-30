import streamlit as st
import duckdb
import pandas as pd
import oracledb
from datetime import datetime
import logging
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

DB_PATH = r"C:\Users\vibho\ado-0001\python-\capacity_planning_v3.duckdb"


def get_duckdb_schema(conn, table_name):
    """Retrieve DuckDB table schema with column order."""
    schema = {}
    try:
        query = f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE lower(table_name) = '{table_name.lower()}'
            ORDER BY ordinal_position
        """
        result = conn.execute(query).fetchdf()
        schema = dict(zip(result['column_name'].str.lower(), result['data_type']))
        logger.info(f"Schema for {table_name}: {schema}")
    except Exception as e:
        logger.error(f"Schema fetch error: {str(e)}")
    return schema


def convert_date_column(df, column_name):
    """Convert date column to standard format."""
    try:
        if pd.api.types.is_integer_dtype(df[column_name]):
            df[column_name] = pd.to_datetime(df[column_name].astype(str), format='%Y%m%d', errors='coerce')
        else:
            df[column_name] = pd.to_datetime(df[column_name],  errors='coerce')
        return df[column_name]
    except Exception as e:
        logger.error(f"Date conversion failed for {column_name}: {str(e)}")
        raise


def fetch_and_execute_query(app_name, user_start_date, user_end_date):
    """Fetch data from Oracle and store it in DuckDB."""
    conn = duckdb.connect(DB_PATH)

    try:
        # Fetch metadata for the selected application
        result = conn.execute(
            "SELECT table_name, sql_query FROM metadata WHERE application_name = ?", (app_name,)
        ).fetchone()

        if not result:
            st.error("Application not found in metadata.")
            return

        table_name, sql_query = result
        logger.info(f"Using table: {table_name}")

        # Get DuckDB schema with column order
        duckdb_schema = get_duckdb_schema(conn, table_name)
        duckdb_columns = list(duckdb_schema.keys())

        # Connect to Oracle
        dsn = oracledb.makedsn("localhost", 1521, service_name="xepdb1")
        with oracledb.connect(user="hr", password="hr", dsn=dsn) as oracle_conn:
            with oracle_conn.cursor() as oracle_cursor:
                # Execute Oracle query
                params = {
                    "start_date": user_start_date.strftime('%Y-%m-%d'),
                    "end_date": user_end_date.strftime('%Y-%m-%d')
                }
                logger.info(f"Executing Oracle query: {sql_query} with params {params}")
                oracle_cursor.execute(sql_query, params)

                # Fetch data
                columns = [col[0].lower() for col in oracle_cursor.description]  # Ensure lowercase columns
                result_data = oracle_cursor.fetchall()

                # Check if data is available
                if not result_data:
                    st.warning("No data found for the given date range.")
                    return

                result_df = pd.DataFrame(result_data, columns=columns)
                logger.info(f"Fetched {len(result_df)} rows from Oracle")

                # Validate and reorder columns
                missing_cols = set(duckdb_columns) - set(result_df.columns)
                if missing_cols:
                    st.error(f"Missing columns in results: {', '.join(missing_cols)}")
                    return

                # Reorder DataFrame to match DuckDB schema
                result_df = result_df[duckdb_columns]

                # Convert date columns
                for col in duckdb_columns:
                    if duckdb_schema[col] == 'DATE' and col in result_df.columns:
                        result_df[col] = convert_date_column(result_df, col)

                # Insert data into DuckDB
                conn.register("oracle_result", result_df)
                conn.execute(f"INSERT INTO {table_name} SELECT * FROM oracle_result")
                logger.info(f"Data inserted into {table_name} successfully")

                # Display data
                st.success("Operation completed successfully!")
                st.dataframe(result_df)

                # Provide Excel/CSV download options
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    result_df.to_excel(writer, index=False)

                st.download_button(
                    label="Download Excel",
                    data=output.getvalue(),
                    file_name=f"{app_name}_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                st.download_button(
                    label="Download CSV",
                    data=result_df.to_csv(index=False).encode(),
                    file_name=f"{app_name}_data.csv",
                    mime="text/csv"
                )

    except duckdb.ConversionException as e:
        logger.error(f"Conversion error: {str(e)}")
        st.error(f"Data type mismatch error: {str(e)}")
        logger.debug(f"Problematic data sample:\n{result_df.head().to_dict()}")

    except Exception as e:
        logger.exception("Critical error occurred:")
        st.error(f"Operation failed: {str(e)}")

    finally:
        conn.close()


def main():
    """Streamlit UI for user interaction."""
    st.title("Data Management System")

    # Fetch available applications
    conn = duckdb.connect(DB_PATH)
    apps = conn.execute("SELECT application_name FROM metadata").fetchdf()["application_name"].tolist()
    conn.close()

    if not apps:
        st.error("No applications found in metadata.")
        return

    selected_app = st.selectbox("Select Application", apps)
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("Execute"):
        if start_date > end_date:
            st.error("Invalid date range: Start date must be before end date")
        else:
            fetch_and_execute_query(selected_app, start_date, end_date)


if __name__ == "__main__":
    main()
