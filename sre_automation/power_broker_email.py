import streamlit as st
from utils_email import send_email, get_formatted_text
import logging

logger = logging.getLogger(__name__)

def page_power_broker_email():
    st.title("PowerBroker Request Approval")
    html_template = """
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        table {{ width: 70%; margin: 20px auto; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; }} /* Reduced padding */
        th {{ background-color: #f2f2f2; font-weight: bold; padding: 4px 10px; }} /* Reduced padding for header */
        .header {{ font-size: 22px; font-weight: bold; text-align: center; color: #4CAF50; }}
        .footer {{ margin-top: 20px; text-align: center; font-size: 12px; color: gray; }}

        /* Styling for the first column */
        td:first-child {{
            background-color: #80b3ff; /* Lighter blue, not too dark */
            font-weight: bold;
        }}
    </style>
</head>
<body>

    <p>Hi Team,</p>

    <p>Request review and approval on this access request to Japan server break-glass accounts.</p>

    <table>
        <tr>
            <th colspan="3" class="header">Request Review and Approval</th>
        </tr>
        <tr>
            <td><b>Application</b></td>
            <td>{application}</td>
            <td>Primary impacted Application or AIT</td>
        </tr>
        <tr>
            <td><b>Task Description</b></td>
            <td>{task_description}</td>
            <td>Description of why the break-glass is needed.
                Must be detailed enough for non-SME to understand and make an informed decision on whether or not to Approve access
            </td>
        </tr>
        <tr>
            <td><b>Service Account(s)</b></td>
            <td>{service_account}</td>
            <td>Break-glass service account(s) needed</td>
        </tr>
        <tr>
            <td><b>User(s)</b></td>
            <td>{users}</td>
            <td>Who needs the break-glass access??</td>
        </tr>
    </table>
    
    {api_links}
    
    <p><b>First Responders KB:</b> Approve PowerBroker Break-Glass access for L2 members -
    <a href="mailto:vibhourjain@gmail.com">vibhourjain@gmail.com</a>;
    <a href="mailto:vibhourjain@yahoo.com">vibhourjain@yahoo.com</a></p>
    
    <p>Regards,</p>

    <p class="footer">This E-Mail is sent from App.</p>

</body>
</html>
"""

    request_input_by = st.text_input("Enter Your Name:")
    application_name = ["Storage","Kitchen"]
    application_name.sort()
    application = st.multiselect("Application:", application_name)
    task_description = get_formatted_text("Task Description:", "Need to perform the recovery steps")
    service_account = st.text_input("Service Account(s):")
    users = st.text_input('Enter User SID (e.g.: zkajghh-Vibhour)')
    work_order_number = st.text_input("Work-Order Number:")
    work_order_number = work_order_number.upper()

    service_accounts = [sa.strip() for sa in service_account.split(',')]
    users_list = [u.strip() for u in users.split(',')]

    api_links = []
    for sa in service_accounts:
        for user in users_list:
            url = f"http://192.168.1.3:5000/initiate_pbrun?service_account={sa}&user_id={user}"
            api_links.append(f'<li><a href="{url}">Execute {sa} for {user}</a></li>')

    api_links_section = f"""
        <h3>Approval Links:</h3>
        <ul>{"".join(api_links)}</ul>
        """

    with st.expander("Email Details"):
        # to_list = ["vibhourjain@gmail.com"]
        # cc_list = ["vibhourjain@gmail.com"]
        to_list = ["vibhourjain@gmail.com"]
        cc_list = ["vibhourjain@gmail.com"]


    if st.button("Send Email"):

        if to_list:
            subject = f"Breakglass Approval Japan Post-Trade - PowerBroker - {work_order_number}"

            email_body = html_template.format(
                application=application,
                task_description=task_description,
                service_account=service_account,
                users=users,
                api_links=api_links_section,
                request_input_by=request_input_by
            )

            send_email(to_list, cc_list, subject, email_body)
