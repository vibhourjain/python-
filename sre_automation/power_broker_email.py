import streamlit as st
from utils_email import validate_email_domain, send_email, send_mailto_email
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

    <p><b>First Responders KB:</b> Approve PowerBroker Break-Glass access for L2 members -
    <a href="mailto:vibhourjain@gmail.com">vibhourjain@gmail.com</a>;
    <a href="mailto:vibhourjain@yahoo.com">vibhourjain@yahoo.com</a></p>





    <p>Regards,</p>

    <p class="footer">This E-Mail is sent from App.</p>

</body>
</html>
"""

    # Dropdown for Impacted Applications
    application_name = ["Storage","Kitchen"]















    application_name.sort()
    application = st.selectbox("Application:", application_name)

    task_description = st.text_area("Task Description:","Need to perform the recovery steps")
    service_account = st.text_input("Service Account(s):")
    users = st.text_input('Enter Users (nbk-FirstName) comma "," separated:', 'zkajghh-Vibhour')
    power_broker_grantee = users[:7]

    work_order_number = st.text_input("Work-Order Number:")
    logger.info(f"application:{application})

    work_order_number = work_order_number.upper()

    with st.expander("Email Details"):
        # to_list = ["vibhourjain@gmail.com"]
        # cc_list = ["vibhourjain@gmail.com"]
        to_list = ["vibhourjain@gmail.com"]
        cc_list = ["vibhourjain@gmail.com"]


    # Send email functionality
    if st.button("Send Email"):
        # Validate email domains

        print("send-to_list", to_list)
        print("send-cc_list", cc_list)
        if to_list:
            # st.success("Success")
            # Generate email subject
            subject = f"Breakglass Approval Japan Post-Trade - PowerBroker - {work_order_number}"

            # Replace placeholders with user input
            email_body = html_template.format(
                application=application,
                task_description=task_description,
                service_account=service_account,
                users=users
            )

            # Send email using win32client
            send_email(to_list, cc_list, subject, email_body)
