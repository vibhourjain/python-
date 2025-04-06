import streamlit as st
import pyodbc
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def connect_to_database(instance, db_username,db_password):
    INSTANCES = {
        "SD1": {"SERVER": "localhost", "PORT": "57810", "DATABASE": "avgpr"},
        "SD2": {"SERVER": "localhost", "PORT": "57811", "DATABASE": "avgpr"},
        "SD3": {"SERVER": "localhost", "PORT": "57812", "DATABASE": "avgpr"},
        "SD4": {"SERVER": "localhost", "PORT": "57813", "DATABASE": "avgpr"},
        "SD5": {"SERVER": "localhost", "PORT": "57814", "DATABASE": "avgpr"}
    }

    try:
        if instance not in INSTANCES:
            st.error(f"Instance {instance} not found!")
            logger.error(f"Instance {instance} not found in connection mappings.")
            return None

        SERVER = INSTANCES[instance]['SERVER']
        PORT = INSTANCES[instance]['PORT']
        DATABASE = INSTANCES[instance]['DATABASE']
        USERNAME= db_username
        PASSWORD = db_password
        DRIVER = "Adaptive Server Enterprise"

        connection_strings = f"""
        DRIVER={{{DRIVER}}};
        SERVER={SERVER};
        PORT={PORT};
        DATABASE={DATABASE};
        UID={USERNAME};
        PWD={PASSWORD};
        EncryptPassword=yes;
        charset=sjis
"""

        conn = pyodbc.connect(connection_strings)
        logger.info(f"Connected to {instance}")
        return conn
    except Exception as e:
        st.error(f"Failed to connect to {instance}: {e}")
        logger.info(f"Failed to connect to {instance}: {e}")
        return None


def execute_query(conn, sql, params=None):
    logger.info(f"Query executed: {sql} | Params: {params}")
    try:
        cursor = conn.cursor()
        cursor.execute(sql,params)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        logger.info(f"Query Executed: {sql} | Params: {params}")
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        logger.error(f"Error executing query: {e}")
        return None
    finally:
        conn.close()
        logger.error(f"Database connection closed.")


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

        logger.info(f"Prepared SQL Query: {sql_template}")
        logging.info(f"Query Parameters: {params if params else 'None'}")
        return sql_template, params or ()

    except Exception as e:
        logging.error(f"Error preparing SQL: {e}")
        st.error(f"Error preparing SQL: {e}")
        return None, None