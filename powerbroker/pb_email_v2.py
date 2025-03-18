import streamlit as st
from utils_email import send_email
import logging

BASE_API_URL = "http://fastapi-server:8000/run-pbrun"

# Dictionary for unix-group to functional account mapping
d1 = {'ug1': "functional_account1", 'ug2': "functional_account2"}

logger = logging.getLogger(__name__)

def page_power_broker_email():
    st.title("PowerBroker Request Approval")

    # Dropdown for Impacted Applications
    application_name = ["Storage", "Kitchen"]
    application_name.sort()
    application = st.selectbox("Application:", application_name)

    task_description = st.text_area("Task Description:", "Need to perform the recovery steps")
    service_accounts = st.text_input("Service Account(s) (comma-separated):")
    users = st.text_input('Enter Users (NBKID-FirstName, comma-separated):', 'nbk12345-Vibhour')

    work_order_number = st.text_input("Work-Order Number:").upper()

    with st.expander("Email Details"):
        to_list = ["approver@example.com"]
        cc_list = ["cc@example.com"]

    if st.button("Send Email"):
        if not service_accounts or not users:
            st.error("Please enter both service accounts and users.")
            return
        
        service_accounts_list = [acc.strip() for acc in service_accounts.split(",")]
        users_list = [user.strip() for user in users.split(",")]

        # Generate API URLs
        api_links = []
        for user in users_list:
            nbk_id, username = user.split("-")
            for service_account in service_accounts_list:
                unix_group = next((ug for ug, fa in d1.items() if fa == service_account), "unknown")
                url = f"{BASE_API_URL}?user_id={nbk_id}&username={username}&service_account={service_account}&unix_group={unix_group}"
                api_links.append(f'<a href="{url}">{username} - {service_account}</a>')

        email_body = f"""
        <html>
        <body>
            <p>Hi Team,</p>
            <p>Please approve the following access requests:</p>
            <ul>
                {''.join(f'<li>{link}</li>' for link in api_links)}
            </ul>
            <p>Regards,<br>Automation Team</p>
        </body>
        </html>
        """

        subject = f"Breakglass Approval Request - {work_order_number}"
        send_email(to_list, cc_list, subject, email_body)
        st.success("Email sent with approval links!")
