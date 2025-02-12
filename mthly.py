11--app.py
import streamlit as st
from pages import page_sql, page_ssh, page_monthly_task, page_add_sql_data

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["SQL Query Runner", "Remote Unix Command Executor", "Monthly Task", "Add SQL Data"])

    if page == "SQL Query Runner":
        page_sql.page_sql()  # Call SQL page
    elif page == "Remote Unix Command Executor":
        page_ssh.page_ssh()  # Call SSH page
    elif page == "Monthly Task":
        page_monthly_task.page_monthly_task()  # Call Monthly Task page
    elif page == "Add SQL Data":
        page_add_sql_data.page_add_sql_data()  # Call Add SQL Data page

if __name__ == "__main__":
    main()


222---pages/page_add_sql_data.py
import streamlit as st
import pandas as pd
from utils.db_utils import connect_to_sybase, execute_query
from utils.excel_utils import add_sheet_to_excel

def page_add_sql_data():
    st.title("Add SQL Data to Excel")

    # Upload Excel file
    uploaded_file = st.file_uploader("Upload Excel File", type="xlsx")

    if uploaded_file:
        # Load the Excel file
        excel_df = pd.read_excel(uploaded_file, sheet_name=None)
        sheet_names = list(excel_df.keys())
        st.write(f"Sheet Names in Uploaded File: {sheet_names}")

        # Input fields for SQL query and sheet name
        sql_query = st.text_area("Enter SQL Query:")
        sheet_name = st.text_input("Enter Sheet Name to Add:")
        instance = st.selectbox("Choose Sybase Instance", ["Instance 1", "Instance 2", "Instance 3", "Instance 4", "Instance 5"])

        # Button to add data
        if st.button("Run SQL and Add Data"):
            if sql_query and sheet_name and instance:
                with st.spinner("Running SQL Query and Adding Data to Excel..."):
                    # Connect to the selected instance
                    conn = connect_to_sybase(instance)
                    if conn:
                        # Execute SQL query and get the result as a dataframe
                        df = execute_query(conn, sql_query)
                        if df is not None:
                            # Add the data as a new sheet in the Excel file
                            updated_file = add_sheet_to_excel(uploaded_file, df, sheet_name)

                            # Provide the option to download the updated file
                            st.success(f"Data added to sheet '{sheet_name}' successfully!")
                            st.download_button(
                                label="Download Updated Excel",
                                data=updated_file,
                                file_name="updated_data.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
            else:
                st.warning("Please fill in all the required fields.")

22---pages/page_sql.py
import streamlit as st
import pandas as pd
from utils.db_utils import connect_to_sybase, execute_query
import openpyxl

def page_sql():
    st.title("SQL Query Runner")

    start_date = st.date_input("Select Start Date")
    end_date = st.date_input("Select End Date")

    instance_map = {
        "Instance 1": "query1.sql",
        "Instance 2": "query2.sql",
        "Instance 3": "query3.sql",
        "Instance 4": "query4.sql",
        "Instance 5": "query5.sql",
    }

    selected_instance = st.radio("Select an instance", list(instance_map.keys()))

    if st.button("Run Query"):
        sql_file = f"sql_queries/{instance_map[selected_instance]}"
        
        with open(sql_file, "r") as file:
            sql_query = file.read()
        
        sql_query = sql_query.replace("{start_date}", start_date.strftime('%Y-%m-%d'))
        sql_query = sql_query.replace("{end_date}", end_date.strftime('%Y-%m-%d'))

        conn = connect_to_sybase(selected_instance)
        if conn:
            df = execute_query(conn, sql_query)
            if df is not None:
                st.success("Query executed successfully!")
                st.dataframe(df.head(10))
                st.session_state["result_df"] = df

    if "result_df" in st.session_state:
        file_name = st.text_input("Enter file name", "output")
        if st.button("Save to Excel"):
            with pd.ExcelWriter(f"{file_name}.xlsx", engine="openpyxl") as writer:
                st.session_state["result_df"].to_excel(writer, sheet_name=selected_instance, index=False)
            st.success(f"Results saved to {file_name}.xlsx")

33--pages/page_ssh.py
import streamlit as st
from utils.ssh_utils import execute_ssh_command

def page_ssh():
    st.title("Remote Unix Host Command Executor")

    hostname = st.text_input("Hostname")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    command = st.text_area("Enter command")

    if st.button("Execute Command"):
        if not hostname or not username or not password or not command:
            st.warning("Please fill in all fields.")
        else:
            output, error = execute_ssh_command(hostname, username, password, command)
            if output:
                st.success("Command executed successfully!")
                st.code(output)
            if error:
                st.error("Error occurred:")
                st.code(error)

44---utils/db_utils.py
import pyodbc
import streamlit as st

connection_strings = {
    "Instance 1": "DSN=SybaseInstance1;UID=username;PWD=password",
    "Instance 2": "DSN=SybaseInstance2;UID=username;PWD=password",
    "Instance 3": "DSN=SybaseInstance3;UID=username;PWD=password",
    "Instance 4": "DSN=SybaseInstance4;UID=username;PWD=password",
    "Instance 5": "DSN=SybaseInstance5;UID=username;PWD=password",
}

def connect_to_sybase(instance):
    try:
        conn = pyodbc.connect(connection_strings[instance])
        return conn
    except Exception as e:
        st.error(f"Failed to connect to {instance}: {e}")
        return None

def execute_query(conn, sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None
55---utils/ssh_utils.py
import paramiko

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


XXXXX---
import streamlit as st
from utils.db_utils import connect_to_sybase, execute_query

def page_monthly_task():
    st.title("Monthly Task")

    # Sidebar to select subpage
    task_page = st.sidebar.radio("Select a Report", ["Cash Report", "Journal Report"])

    if task_page == "Cash Report":
        cash_report()
    elif task_page == "Journal Report":
        journal_report()

# Cash Report Page
def cash_report():
    st.subheader("Cash Report")

    # Date input for cash report
    date = st.date_input("Select Date for Cash Report")

    if st.button("Run Cash Report"):
        sql_query = """
        SELECT *
        FROM cash_report
        WHERE report_date = '{date}';
        """.format(date=date.strftime('%Y-%m-%d'))
        
        conn = connect_to_sybase("Instance 1")  # You can choose the instance
        if conn:
            df = execute_query(conn, sql_query)
            if df is not None:
                st.success("Cash Report executed successfully!")
                st.dataframe(df)

# Journal Report Page
def journal_report():
    st.subheader("Journal Report")

    # Parameters for journal report
    journal_id = st.text_input("Enter Journal ID")
    start_date = st.date_input("Start Date for Journal Report")
    end_date = st.date_input("End Date for Journal Report")

    if st.button("Run Journal Report"):
        if journal_id and start_date and end_date:
            sql_query = """
            SELECT *
            FROM journal_report
            WHERE journal_id = '{journal_id}'
            AND report_date BETWEEN '{start_date}' AND '{end_date}';
            """.format(
                journal_id=journal_id,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            conn = connect_to_sybase("Instance 2")  # You can choose the instance
            if conn:
                df = execute_query(conn, sql_query)
                if df is not None:
                    st.success("Journal Report executed successfully!")
                    st.dataframe(df)
        else:
            st.warning("Please provide all inputs for the Journal Report.")
#555---utils/excel_utils.py
import pandas as pd
from io import BytesIO
import openpyxl

def add_sheet_to_excel(uploaded_file, df, sheet_name):
    # Load the existing Excel file into a Pandas dataframe
    excel_data = pd.ExcelFile(uploaded_file)
    
    # Create a BytesIO object to save the updated Excel file
    output = BytesIO()

    # Create a writer object to write to Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write existing sheets to the writer
        for sheet in excel_data.sheet_names:
            temp_df = pd.read_excel(excel_data, sheet_name=sheet)
            temp_df.to_excel(writer, sheet_name=sheet, index=False)
        
        # Write the new dataframe (SQL result) to the new sheet
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Seek to the beginning of the BytesIO object before returning it
    output.seek(0)
    return output.getvalue()

## GraphQL
streamlit_app/
│── app.py              # Main entry point
│── pages/
│   │── page_sql.py     # SQL Query Runner page
│   │── page_ssh.py     # Remote Unix Command Executor page
│   │── page_monthly_task.py  # Monthly Task page
│   │── page_add_sql_data.py  # Add SQL Data page
│── utils/
│   │── db_utils.py     # Database connection & execution logic
│   │── excel_utils.py  # Excel file handling logic
│   │── ssh_utils.py    # SSH command execution logic
│── sql_queries/
│   │── query1.sql
│   │── query2.sql
│   │── query3.sql
│   │── query4.sql
│   │── query5.sql
│── requirements.txt    # Python dependencies


