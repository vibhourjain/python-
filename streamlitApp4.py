import streamlit as st
import pandas as pd
import pyodbc
import paramiko
import io
import win32com.client
from datetime import datetime

# **Function to send email via Outlook**
def send_email(to_list, cc_list, subject, body):
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 = Mail Item
        mail.To = to_list
        mail.CC = cc_list
        mail.Subject = subject
        mail.HTMLBody = body
        mail.Send()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# **Function to display the 'Seek Approval' form**
def page_seek_approval():
    st.title("Seek Approval")

    # User inputs for 9 fields
    field_values = {}
    for i in range(1, 10):
        field_values[f"Field {i}"] = st.text_input(f"Enter value for Field {i}")

    # Button to open email popup
    if st.button("Seek Approval"):
        with st.expander("Enter Email Details", expanded=True):
            to_list = st.text_input("To (comma-separated emails)")
            cc_list = st.text_input("CC (comma-separated emails)")
            subject = st.text_input("Subject")
            email_body = """<h3>Approval Request</h3>
            <table border='1'>
            <tr><th>Field</th><th>Value</th></tr>"""
            for field, value in field_values.items():
                email_body += f"<tr><td>{field}</td><td>{value}</td></tr>"
            email_body += "</table>"

            # Button to send email
            if st.button("Send Email"):
                send_email(to_list, cc_list, subject, email_body)

# **Main Navigation**
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["SQL Query Runner", "Remote Unix Command Executor", "Multi-SQL Execution & Export", "Seek Approval"])

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
