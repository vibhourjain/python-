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

'''
instance = "sybase_instance"
sql_template = "SELECT * FROM {table_name} WHERE trade_date BETWEEN ? AND ?"
replacements = {"table_name": "trades_table"}
params = ("2024-01-01", "2024-02-01")

conn = connect_to_database(instance)
if conn:
    sql, params = prepare_sql(sql_template, replacements, params)
    df = execute_query(conn, instance, sql, params)
    
    if df is not None:
        st.dataframe(df)  # Display in Streamlit

'''

import streamlit as st
import pyodbc
import pandas as pd
import logging

# Configure logging
logging.basicConfig(filename="app_query.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Mapping of applications to database instances
app_instance_mapping = {
    "App1": "instance_abc",
    "App2": "instance_xyz",
    "App3": "instance_pqr",
    "App4": "instance_def",
    "App5": "instance_ghi",
    "App6": "instance_jkl",
}

# Corresponding SQL queries
app_sql_mapping = {
    "App1": "SELECT * FROM db1..userole WHERE uid = ?",
    "App2": "SELECT * FROM db2..user_permissions WHERE user_id = ?",
    "App3": "SELECT * FROM db3..access_control WHERE user = ?",
    "App4": "SELECT * FROM db4..roles WHERE user_name = ?",
    "App5": "SELECT * FROM db5..privileges WHERE uid = ?",
    "App6": "SELECT * FROM db6..user_access WHERE user_id = ?",
}

# Connection strings for different instances
connection_strings = {
    "instance_abc": "DRIVER={Adaptive Server Enterprise};SERVER=server_abc;DATABASE=db1;UID=user;PWD=password",
    "instance_xyz": "DRIVER={Adaptive Server Enterprise};SERVER=server_xyz;DATABASE=db2;UID=user;PWD=password",
    "instance_pqr": "DRIVER={Adaptive Server Enterprise};SERVER=server_pqr;DATABASE=db3;UID=user;PWD=password",
    "instance_def": "DRIVER={Adaptive Server Enterprise};SERVER=server_def;DATABASE=db4;UID=user;PWD=password",
    "instance_ghi": "DRIVER={Adaptive Server Enterprise};SERVER=server_ghi;DATABASE=db5;UID=user;PWD=password",
    "instance_jkl": "DRIVER={Adaptive Server Enterprise};SERVER=server_jkl;DATABASE=db6;UID=user;PWD=password",
}

connection_strings = {
    "instance_abc": "DRIVER={Adaptive Server Enterprise};SERVER=server_abc;DATABASE=db1;UID=user;PWD=password;CHARSET=utf8;ENCRYPTEDPASSWORD=yes",
    "instance_xyz": "DRIVER={Adaptive Server Enterprise};SERVER=server_xyz;DATABASE=db2;UID=user;PWD=password;CHARSET=utf8;ENCRYPTEDPASSWORD=yes",
    "instance_pqr": "DRIVER={Adaptive Server Enterprise};SERVER=server_pqr;DATABASE=db3;UID=user;PWD=password;CHARSET=utf8;ENCRYPTEDPASSWORD=yes",
    "instance_def": "DRIVER={Adaptive Server Enterprise};SERVER=server_def;DATABASE=db4;UID=user;PWD=password;CHARSET=utf8;ENCRYPTEDPASSWORD=yes",
    "instance_ghi": "DRIVER={Adaptive Server Enterprise};SERVER=server_ghi;DATABASE=db5;UID=user;PWD=password;CHARSET=utf8;ENCRYPTEDPASSWORD=yes",
    "instance_jkl": "DRIVER={Adaptive Server Enterprise};SERVER=server_jkl;DATABASE=db6;UID=user;PWD=password;CHARSET=utf8;ENCRYPTEDPASSWORD=yes",
}

def connect_to_database(instance):
    """Establish a connection to the database."""
    try:
        if instance not in connection_strings:
            st.error(f"Instance {instance} not found!")
            logging.error(f"Instance {instance} not found in connection mappings.")
            return None
        
        conn = pyodbc.connect(connection_strings[instance])
        logging.info(f"Connected to {instance}")
        return conn
    except Exception as e:
        st.error(f"Failed to connect to {instance}: {e}")
        logging.error(f"Connection failed for {instance}: {e}")
        return None

def execute_query(conn, sql, params):
    """Execute the SQL query and return results."""
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        logging.info(f"Query executed: {sql} | Params: {params}")
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        logging.error(f"SQL Execution Error: {e}")
        return None
    finally:
        conn.close()
        logging.info("Database connection closed.")

# Streamlit UI
st.title("Application User Query")

# User inputs
application = st.selectbox("Select Application:", list(app_instance_mapping.keys()))
user_id = st.text_input("Enter User ID:")

if st.button("Fetch Data"):
    if application and user_id:
        instance = app_instance_mapping[application]
        sql = app_sql_mapping[application]

        conn = connect_to_database(instance)
        if conn:
            df = execute_query(conn, sql, (user_id,))
            if df is not None:
                st.dataframe(df)
    else:
        st.error("Please select an application and enter a User ID.")
