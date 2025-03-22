import streamlit as st
import pandas as pd
import pyodbc
import paramiko
import io
from datetime import datetime

# **Define SQL file paths, instances, and sheet names**
sql_files = {
    "Instance 1": {"file": "query1.sql", "sheet_name": "Sheet1"},
    "Instance 2": {"file": "query2.sql", "sheet_name": "Sheet2"},
    "Instance 3": {"file": "query3.sql", "sheet_name": "Sheet3"},
    "Instance 4": {"file": "query4.sql", "sheet_name": "Sheet4"},
    "Instance 5": {"file": "query5.sql", "sheet_name": "Sheet5"},
}

# **Define Sybase connection strings**
connection_strings = {
    "Instance 1": "DSN=SybaseInstance1;UID=username;PWD=password",
    "Instance 2": "DSN=SybaseInstance2;UID=username;PWD=password",
    "Instance 3": "DSN=SybaseInstance3;UID=username;PWD=password",
    "Instance 4": "DSN=SybaseInstance4;UID=username;PWD=password",
    "Instance 5": "DSN=SybaseInstance5;UID=username;PWD=password",
}

# **Function to connect to Sybase**
def connect_to_sybase(instance):
    try:
        conn = pyodbc.connect(connection_strings[instance])
        return conn
    except Exception as e:
        st.error(f"Failed to connect to {instance}: {e}")
        return None

# **Function to execute SQL query**
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

# **Function to execute SSH command**
def execute_ssh_command(hostname, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        return output, error
    except Exception as e:
        return None, str(e)

# **Page 1: SQL Query Runner**
def page_sql():
    st.title("SQL Query Runner")

    sql_query = st.text_area("Paste your SQL query here:", height=150)

    instance_buttons = ["Instance 1", "Instance 2", "Instance 3", "Instance 4", "Instance 5"]
    selected_instance = st.radio("Select an instance", instance_buttons)

    if st.button("Run Query"):
        if sql_query.strip() == "":
            st.warning("Please enter a SQL query.")
        else:
            with st.spinner(f"Running query on {selected_instance}..."):
                conn = connect_to_sybase(selected_instance)
                if conn:
                    df = execute_query(conn, sql_query, "2024-01-01", "2024-12-31")
                    if df is not None:
                        st.success("Query executed successfully!")
                        st.write(f"Top 10 results from {selected_instance}:")
                        st.dataframe(df.head(10))
                        conn.close()
                        st.session_state["result_df"] = df

    if "result_df" in st.session_state:
        st.write("### Save Results to Excel")
        file_name = st.text_input("Enter the file name (without extension):", "output")
        if st.button("Write to Excel"):
            if file_name.strip() == "":
                st.warning("Please enter a file name.")
            else:
                file_path = f"{file_name}.xlsx"
                try:
                    st.session_state["result_df"].to_excel(file_path, index=False)
                    st.success(f"Results saved to **{file_path}**!")
                except Exception as e:
                    st.error(f"Error saving file: {e}")

# **Page 2: SSH Command Executor**
def page_ssh():
    st.title("Remote Unix Host Command Executor")

    hostname = st.text_input("Hostname (e.g., example.com):")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    command = st.text_area("Enter the command to execute:", height=100)

    if st.button("Execute Command"):
        if not hostname or not username or not password or not command:
            st.warning("Please fill in all fields.")
        else:
            with st.spinner("Executing command..."):
                output, error = execute_ssh_command(hostname, username, password, command)
                if output:
                    st.success("Command executed successfully!")
                    st.write("### Output:")
                    st.code(output)
                if error:
                    st.error("Error occurred:")
                    st.code(error)

# **Page 3: Multi-SQL Execution & Excel Export**
def page_multi_sql():
    st.title("Run Multiple SQL Files and Export to Excel")

    start_date = st.date_input("Select Start Date")
    end_date = st.date_input("Select End Date")

    if st.button("Run Queries"):
        if not start_date or not end_date:
            st.error("Please select both start and end dates.")
        else:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                for instance, details in sql_files.items():
                    sql_file_path = details["file"]
                    sheet_name = details["sheet_name"]

                    st.write(f"Executing SQL for **{instance}**...")

                    try:
                        with open(sql_file_path, "r") as file:
                            sql_query = file.read()

                        conn = connect_to_sybase(instance)
                        if conn:
                            df = execute_query(conn, sql_query, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                            if df is not None:
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                                st.success(f"Results saved for {instance} ✅")
                            conn.close()

                    except Exception as e:
                        st.error(f"Error processing {instance}: {e}")

            st.download_button(
                label="Download Excel File",
                data=excel_buffer.getvalue(),
                file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# **Main Navigation**
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["SQL Query Runner", "Remote Unix Command Executor", "Multi-SQL Execution & Export"])

    if page == "SQL Query Runner":
        page_sql()
    elif page == "Remote Unix Command Executor":
        page_ssh()
    elif page == "Multi-SQL Execution & Export":
        page_multi_sql()

# **Run the app**
if __name__ == "__main__":
    main()
