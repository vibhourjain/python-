import streamlit as st
import pyodbc
import pandas as pd
import logging

logger = logging.getLogger(__name__)
def connect_to_sybase(instance, db_username, db_password):
    INSTANCES = {
        "SD1": {"SERVER": "localhost", "PORT": "57810", "DATABASE": "avgpr"},
        "SD2": {"SERVER": "localhost", "PORT": "57811", "DATABASE": "avgpr"},
        "SD3": {"SERVER": "localhost", "PORT": "57812", "DATABASE": "avgpr"},
        "SD4": {"SERVER": "localhost", "PORT": "57813", "DATABASE": "avgpr"},
        "SD5": {"SERVER": "localhost", "PORT": "57814", "DATABASE": "avgpr"}
    }
    SERVER = INSTANCES[instance]['SERVER']
    PORT = INSTANCES[instance]['PORT']
    DATABASE = INSTANCES[instance]['DATABASE']
    USERNAME = db_username
    PASSWORD = db_password
    DRIVER = "Adaptive Server Enterprise"

    # Establish connection
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

    try:
        conn = pyodbc.connect(connection_strings)
        return conn
    except Exception as e:
        st.error(f"Failed to connect to {instance}: {e}")
        return None

def execute_query(conn, sql, start_date, end_date):
    try:
        cursor = conn.cursor()
        sql = sql.replace("{start_date}", start_date).replace("{end_date}", end_date)
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None
    finally:
        conn.close()
