import streamlit as st
from utils_email import send_email
import urllib.parse

# API Endpoint (Opens Web Form Instead of Executing Immediately)
API_BASE_URL = "http://your-server-ip:5000/run_command"

def page_power_broker_email():
    st.title("PowerBroker Request Approval")

    # User Input Fields
    powerbrokerCommand = st.text_area("PowerBroker Command:")
    clientID = st.text_input("Client ID:")

    # Generate API Link (Pre-filled with Command & ClientID)
    api_link = f"{API_BASE_URL}?powerbrokerCommand={urllib.parse.quote(powerbrokerCommand)}&clientID={clientID}"

    # Email Body with API Link
    email_body = f"""
    <p>Hi Team,</p>
    <p>To execute the command, click the link below and enter your credentials:</p>
    <a href="{api_link}">{api_link}</a>
    <p>Regards,<br>PowerBroker System</p>
    """

    if st.button("Send Email"):
        send_email(["user@example.com"], [], "PowerBroker Approval", email_body)
        st.success("Email Sent Successfully!")
