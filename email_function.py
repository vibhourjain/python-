import streamlit as st
import win32com.client as win32

# Function to send email using win32client
def send_email(to_list, cc_list, subject, from_email, email_body):
    try:
        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.Subject = subject
        mail.BodyFormat = 2  # 2 = HTML format
        mail.HTMLBody = email_body
        mail.To = "; ".join(to_list)
        mail.CC = "; ".join(cc_list)
        mail.Sender = from_email
        mail.Send()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Function to validate email domains
def validate_email_domain(email_list, domain="jpmc.com"):
    invalid_emails = [email.strip() for email in email_list if not email.strip().endswith(f"@{domain}")]
    if invalid_emails:
        st.error(f"The following emails are not from the {domain} domain: {', '.join(invalid_emails)}")
        return False
    return True

# Latent Request Approval Page
def page_latent_approval():
    st.title("Latent Request Approval Form")

    # Define the HTML template
    html_template = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 60%; margin: 0 auto; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; color: #333; }
            .header { color: #4CAF50; font-size: 24px; margin-bottom: 20px; text-align: center; }
            .footer { margin-top: 30px; font-size: 12px; color: #555; text-align: center; }
        </style>
    </head>
    <body>
        <div class="header">Latent Request Approval Template</div>

        <table>
            <tr>
                <th colspan="2">Incident Details</th>
            </tr>
            <tr>
                <td><strong>Incident Number</strong></td>
                <td>{incident_number}</td>
            </tr>
            <tr>
                <td><strong>Incident Priority</strong></td>
                <td>{incident_priority}</td>
            </tr>
            <tr>
                <td><strong>Incident Urgency</strong></td>
                <td>{incident_urgency}</td>
            </tr>
            <tr>
                <td><strong>Reason for Latent Fix</strong></td>
                <td>{reason_for_latent_fix}</td>
            </tr>
            <tr>
                <td><strong>Impacted Location(s)</strong></td>
                <td>{impacted_locations}</td>
            </tr>
            <tr>
                <td><strong>Business Impacted (Risk of Not Implementing)</strong></td>
                <td>{business_impact}</td>
            </tr>

            <tr>
                <th colspan="2">Impacted Applications</th>
            </tr>
            <tr>
                <td colspan="2">{impacted_applications}</td>
            </tr>

            <tr>
                <th colspan="2">Issue Summary</th>
            </tr>
            <tr>
                <td colspan="2">{issue_summary}</td>
            </tr>

            <tr>
                <th colspan="2">MAPS Lead Approval</th>
            </tr>
            <tr>
                <td colspan="2">{maps_lead_approval}</td>
            </tr>

            <tr>
                <th colspan="2">Reviewed by CIO Dev Lead</th>
            </tr>
            <tr>
                <td colspan="2">{cio_dev_lead_review}</td>
            </tr>

            <tr>
                <th colspan="2">Remediation</th>
            </tr>
            <tr>
                <td colspan="2">{remediation_steps}</td>
            </tr>
        </table>

        <div class="footer">
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </body>
    </html>
    """

    # Streamlit form to collect input
    incident_number = st.text_input("Incident Number:")
    incident_priority = st.selectbox("Incident Priority:", ["P1-S1", "P1-S2", "P2-U1"])
    incident_urgency = st.selectbox("Incident Urgency:", ["High", "Medium", "Low"])
    reason_for_latent_fix = st.text_area("Reason for Latent Fix:")
    impacted_locations = st.text_input("Impacted Location(s):")
    business_impact = st.text_area("Business Impacted (Risk of Not Implementing):")
    
    # Dropdown for Impacted Applications
    application_name = ["OSCAR", "PETA", "MADMACS"]
    application_name.sort()  # Sort alphabetically
    impacted_applications = st.selectbox("Impacted Application:", application_name)
    
    issue_summary = st.text_area("Issue Summary:")
    
    # MAPS Lead Approval with default value
    maps_lead_approval = st.text_input("MAPS Lead Approval:", "sachin.patil@jpmc.com")
    
    cio_dev_lead_review = st.text_input("Reviewed by CIO Dev Lead:")
    remediation_steps = st.text_area("Steps Needed for Remediation:")

    # Email details
    with st.expander("Email Details"):
        to_list = st.text_area("To (comma-separated):").split(",")
        cc_list = st.text_area("CC (comma-separated):").split(",")
        from_email = st.text_input("From (your email):")

    # Replace placeholders with user input
    if st.button("Preview Email"):
        email_body = html_template.format(
            incident_number=incident_number,
            incident_priority=incident_priority,
            incident_urgency=incident_urgency,
            reason_for_latent_fix=reason_for_latent_fix,
            impacted_locations=impacted_locations,
            business_impact=business_impact,
            impacted_applications=impacted_applications,
            issue_summary=issue_summary,
            maps_lead_approval=maps_lead_approval,
            cio_dev_lead_review=cio_dev_lead_review,
            remediation_steps=remediation_steps,
        )
        st.markdown(email_body, unsafe_allow_html=True)

    # Send email functionality
    if st.button("Send Email"):
        # Validate email domains
        if validate_email_domain(to_list) and validate_email_domain(cc_list):
            # Generate email subject
            subject = f"{incident_number} - Latent Approval Request"

            # Replace placeholders with user input
            email_body = html_template.format(
                incident_number=incident_number,
                incident_priority=incident_priority,
                incident_urgency=incident_urgency,
                reason_for_latent_fix=reason_for_latent_fix,
                impacted_locations=impacted_locations,
                business_impact=business_impact,
                impacted_applications=impacted_applications,
                issue_summary=issue_summary,
                maps_lead_approval=maps_lead_approval,
                cio_dev_lead_review=cio_dev_lead_review,
                remediation_steps=remediation_steps,
            )

            # Send email using win32client
            send_email(to_list, cc_list, subject, from_email, email_body)
