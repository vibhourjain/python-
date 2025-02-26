import pyodbc
import pandas as pd
import streamlit as st
import logging

# Configure Logging
logging.basicConfig(
    filename="database_operations.log",  # Log file
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Example connection strings (Update with actual credentials)
connection_strings = {
    "sybase_instance": "DRIVER={Adaptive Server Enterprise};SERVER=myserver;DATABASE=mydb;UID=user;PWD=password"
}

def connect_to_database(instance):
    """Establish a connection to a given database instance."""
    try:
        if instance not in connection_strings:
            error_msg = f"Instance {instance} not found in connection strings."
            logging.error(error_msg)
            st.error(error_msg)
            return None
        
        logging.info(f"Attempting to connect to instance: {instance}")
        conn = pyodbc.connect(connection_strings[instance])
        logging.info(f"Successfully connected to {instance}")
        return conn
    except Exception as e:
        error_msg = f"Failed to connect to {instance}: {e}"
        logging.error(error_msg)
        st.error(error_msg)
        return None

def prepare_sql(sql_template, replacements=None, params=None):
    """
    Prepare an SQL query by replacing placeholders and formatting parameters.
    
    :param sql_template: SQL query with `{placeholders}`.
    :param replacements: Dictionary for text-based replacements.
    :param params: Tuple or list of query parameters.
    :return: Processed SQL query and params tuple.
    """
    try:
        if replacements:
            for key, value in replacements.items():
                sql_template = sql_template.replace(f"{{{key}}}", value)
        
        logging.info(f"Prepared SQL Query: {sql_template}")
        logging.info(f"Query Parameters: {params if params else 'None'}")
        return sql_template, params or ()
    
    except Exception as e:
        logging.error(f"Error preparing SQL: {e}")
        st.error(f"Error preparing SQL: {e}")
        return None, None

def execute_query(conn, instance, sql, params=None):
    """
    Execute an SQL query and return a DataFrame.
    
    :param conn: Database connection.
    :param instance: Database instance name.
    :param sql: SQL query to execute.
    :param params: Tuple of parameters for the query.
    :return: Pandas DataFrame with results.
    """
    try:
        logging.info(f"Executing query on instance: {instance}")
        logging.info(f"SQL: {sql}")
        logging.info(f"Parameters: {params if params else 'None'}")
        
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            df = pd.DataFrame.from_records(rows, columns=columns)
        
        logging.info(f"Query executed successfully on {instance}")
        return df
    except Exception as e:
        error_msg = f"Error executing query on {instance}: {e}"
        logging.error(error_msg)
        st.error(error_msg)
        return None
    finally:
        conn.close()
        logging.info(f"Connection to {instance} closed.")
