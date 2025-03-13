import streamlit as st
from utils_email import send_email
import urllib.parse

# API Endpoint
API_BASE_URL = "http://your-server-ip:5000/run_command"

def page_power_broker_email():
    st.title("PowerBroker Request Approval")

    # User Input Fields
    application = st.selectbox("Application:", ["Storage", "Kitchen"])
    task_description = st.text_area("Task Description:", "Need to perform the recovery steps")
    service_accounts = st.text_area("Service Account(s):")
    users = st.text_area("User(s):", "Vibhour (zkajghh)")
    work_order_number = st.text_input("Work-Order Number:").upper()
    powerbrokerCommand = st.text_area("PowerBroker Command:")
    clientID = st.text_input("Client ID:")

    # Email Details
    to_list = ["vibhourjain@gmail.com"]
    cc_list = ["vibhourjain@gmail.com"]

    # Generate API link (User will manually enter Username, Password & OTP before clicking)
    api_link = (
        f"{API_BASE_URL}?username=XXXX&password=YYYY&otp=ZZZZ"
        f"&powerbrokerCommand={urllib.parse.quote(powerbrokerCommand)}&clientID={clientID}"
    )

    # Email Body with API Link
    email_body = f"""
    <p>Hi Team,</p>
    <p>Request review and approval for the following task:</p>
    <p><b>Application:</b> {application}</p>
    <p><b>Task Description:</b> {task_description}</p>
    <p><b>Service Accounts:</b> {service_accounts}</p>
    <p><b>Users:</b> {users}</p>

    <p><b>To Execute the Command, Click the Link Below (Replace XXXX, YYYY, ZZZZ with Your Credentials):</b></p>
    <a href="{api_link}">{api_link}</a>

    <p>Regards,<br>PowerBroker System</p>
    """

    # Send Email Button
    if st.button("Send Email"):
        subject = f"PowerBroker Approval Required - {work_order_number}"
        send_email(to_list, cc_list, subject, email_body)
        st.success("Email Sent Successfully!")

