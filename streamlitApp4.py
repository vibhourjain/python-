import streamlit as st
import pandas as pd
import pyodbc
import paramiko
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
    # (Existing functionality remains unchanged)

# **Page 2: SSH Command Executor**
def page_ssh():
    st.title("Remote Unix Host Command Executor")
    # (Existing functionality remains unchanged)

# **Page 3: Multi-SQL Execution & Excel Export**
def page_multi_sql():
    st.title("Run Multiple SQL Files and Export to Excel")
    # (Existing functionality remains unchanged)

# **Page 4: Seek Approval Functionality**
def send_email(to_list, cc_list, subject, from_email, email_body):
    try:
        smtp_server = "smtp.office365.com"
        smtp_port = 587
        sender_email = from_email
        sender_password = "your_password"

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(to_list)
        msg["CC"] = ", ".join(cc_list)
        msg["Subject"] = subject
        msg.attach(MIMEText(email_body, "html"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_list + cc_list, msg.as_string())
        server.quit()

        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")


def page_seek_approval():
    st.title("Seek Approval Form")

    field_values = {}
    for i in range(1, 10):
        field_values[f"Field {i}"] = st.text_input(f"Enter value for Field {i}:")

    if st.button("Seek Approval"):
        with st.expander("Email Details"):
            to_list = st.text_area("To (comma-separated):").split(",")
            cc_list = st.text_area("CC (comma-separated):").split(",")
            from_email = st.text_input("From (your email):")
            subject = st.text_input("Subject:")
            email_body = "<h3>Approval Request</h3><table border='1'>" + "".join(
                f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in field_values.items()
            ) + "</table>"

            st.write("Preview of Email Body:")
            st.markdown(email_body, unsafe_allow_html=True)

            if st.button("Send Email"):
                send_email(to_list, cc_list, subject, from_email, email_body)

# **Main Navigation**
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "SQL Query Runner", 
        "Remote Unix Command Executor", 
        "Multi-SQL Execution & Export",
        "Seek Approval"
    ])

    if page == "SQL Query Runner":
        page_sql()
    elif page == "Remote Unix Command Executor":
        page_ssh()
    elif page == "Multi-SQL Execution & Export":
        page_multi_sql()
    elif page == "Seek Approval":
        page_seek_approval()

# **Run the app**
if __name__ == "__main__":
    main()
