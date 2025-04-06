import pyodbc
import pandas as pd
import streamlit as st
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Connect to Sybase Function (as per ConnectSybase_test.py)
# -----------------------------
def connect_to_database(instance, db_username, db_password):
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
        USERNAME = db_username
        PASSWORD = db_password
        DRIVER = "Adaptive Server Enterprise"

        connection_strings = f"""
                DRIVER={{{DRIVER}}};
                SERVER={SERVER};
                PORT={PORT};
                DATABASE={DATABASE};
                UID={USERNAME};
                PWD={PASSWORD};
                EncryptPassword=yes ;
                charset=sjis
                """

        conn = pyodbc.connect(connection_strings)
        logger.info(f"Connected to {instance}")
        return conn
    except Exception as e:
        st.error(f"Failed to connect to {instance}: {e}")
        logger.error(f"Failed to connect to {instance}: {e}")
        return None


# -----------------------------
# Execute Query Function
# -----------------------------
def execute_query(conn, query, params=()):
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        logger.info(f"Query executed: {query} | Params: {params}")
        return df
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        st.error("Query failed. Check logs for details.")
        return pd.DataFrame()
    finally:
        conn.close()
        logger.info("Database connection closed.")


# -----------------------------
# Prepare SQL Function
# -----------------------------
def prepare_sql(sql_template, replacements=None, in_clause_values=None, in_clause_key=None):
    """
    Handles:
    - Positional SQL parameters (?, ?, ?)
    - IN clauses using {IN_clause}
    - Date & other values via 'replacements' for ? substitution

    :param sql_template: SQL with `{IN_clause}` and `?` placeholders
    :param replacements: Dict like {"start_date": "2024-01-01"}
    :param in_clause_values: List of values for IN
    :param in_clause_key: Placeholder in template like "IN_clause"
    :return: (prepared_sql, tuple_of_params)
    """
    try:
        sql = sql_template
        params = []

        # Handle IN clause
        if in_clause_values and in_clause_key:
            cleaned = [v.strip() for v in in_clause_values if v.strip()]
            placeholders = ", ".join(["?"] * len(cleaned))
            sql = sql.replace(f"{{{in_clause_key}}}", placeholders)
            params.extend(cleaned)
        elif in_clause_key:
            sql = sql.replace(f"{{{in_clause_key}}}", "NULL")

        # Add replacements for other parameters in order of appearance of ?
        if replacements:
            param_keys = list(replacements.keys())
            for key in param_keys:
                params.append(replacements[key])

        logger.info(f"Prepared SQL: {sql}")
        logger.info(f"With parameters: {params}")
        return sql, tuple(params)
    except Exception as e:
        logger.error(f"Error preparing SQL: {e}")
        st.error(f"Error preparing SQL: {e}")
        return None, None
