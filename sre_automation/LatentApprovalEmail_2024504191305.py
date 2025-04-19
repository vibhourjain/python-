import streamlit as st
from utils_email import validate_email_domain, send_email, get_formatted_text
import logging
import os

logger = logging.getLogger(__name__)

def fn_latent_approval():
    st.title("Latent Request Approval Form")

    html_template = """
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        table {{ width: 60%; margin: 0 auto; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; color: #333; }}
        .header {{ background-color: #ACF450; font-size: 24px; text-align: center; }}
        .sub-header {{ font-size: 18px; font-weight: bold; color: #333; text-align: center; }}
        .field {{ font-weight: bold; }}
        .value {{ font-weight: normal; }}
    </style>
    </head>
    <body>

    <p style="color:black; text-align:left; font-weight:normal; white-space:pre-line;">
    Hi Vibhour,
    </p>

    <p style="color:black; text-align:left; font-weight:normal; white-space:pre-line;">
    Need your approval, detail follows:
    </p>

    <table>
        <tr><th colspan="2" class="header">Latent Request Approval Template</th></tr>
        <tr><th colspan="2" class="sub-header">Incident Details</th></tr>
        <tr><td class="field">Impacted Applications</td><td class="value">{impacted_applications}</td></tr>
        <tr><td class="field">Issue Summary</td><td class="value">{issue_summary}</td></tr>
        <tr><td class="field">MAPS Lead Approval</td><td class="value">{maps_lead_approval}</td></tr>
        <tr><td class="field">Reviewed by CIO Dev Lead</td><td class="value">{cio_dev_lead_review}</td></tr>
        <tr><td class="field">Known Issue references (Jira/TechDebt/PKE)</td><td class="value">{known_issue_reference}</td></tr>
        <tr><td class="field">Incident Number</td><td class="value">{incident_number}</td></tr>
        <tr><td class="field">Incident Priority</td><td class="value">{incident_priority}</td></tr>
        <tr><td class="field">Incident Urgency</td><td class="value">{incident_urgency}</td></tr>
        <tr><td class="field">Reason for Latent Fix</td><td class="value">{reason_for_latent_fix}</td></tr>
        <tr><td class="field">Impacted Location(s)</td><td class="value">{impacted_locations}</td></tr>
        <tr><td class="field">Business Impacted (Risk of Not Implementing)</td><td class="value">{business_impact}</td></tr>
        <tr><th colspan="2" class="sub-header">Remediation</th></tr>
        <tr><td class="field">Steps Need to be Performed for Remediation</td><td class="value">{remediation_steps}</td></tr>
    </table>

    <p>Regards<br>{request_input_by}</p>

    <div class="footer-note">
        <p>This E-Mail is sent from TaskConquer.</p>
    </div>

    </body>
    </html>
    """

    application_name = [
        "OSCAR", "PETA", "MADMACS", "Settlement Platform (Saturn)",
        "BANMADACS-710945", "MADMACS-21064", "OSCAR-24156",
        "Cash Control Management System (CCMS)-26022", "Tokyo Books and Records (TBAR)-24115",
        "COCOA-22582", "CASH_BRIDGE-28759", "Tokyo TPS-35430",
        "L-Share-29164", "BAIHO-25585", "JXL-26098", "JPD-25015",
        "BANMADMACS-71095", "MRFR-24037", "KUKUSAI-25692", "QDEC-25539",
        "Niagara-70390", "Polaris-69135", "Jet-67346"
    ]
    application_name.sort()

    request_input_by = st.text_input("Enter Your Name:")
    impacted_applications = st.text_input("Impacted Applications:")
    issue_summary = get_formatted_text("Issue Summary:")
    maps_lead_approval = st.text_input("MAPS Lead Approval:", "Shreyas Ganu")
    cio_dev_lead_review = st.text_input("Reviewed by CIO Dev Lead:")
    known_issue_reference = st.text_input("Known Issue references (Jira/TechDebt/PKE): Leave Blank if not Applicable")

    incident_number = st.text_input("Incident Number:").upper()
    incident_priority = st.text_input("Incident Priority:", "P3-L")
    incident_urgency = st.text_input("Incident Urgency:", "Medium")
    reason_for_latent_fix = get_formatted_text("Reason for Latent Fix:")
    impacted_locations = st.text_input("Impacted Location(s):", "Japan")
    business_impact = get_formatted_text("Business Impact (Risk of Not Implementing):")
    remediation_steps = get_formatted_text("Steps Needed for Remediation:")

    # File uploader
    uploaded_file = st.file_uploader("Attach Outlook Email or Other File", type=["msg", "pdf", "txt", "csv", "xlsx", "docx"])
    attachment_path = None
    if uploaded_file is not None:
        attachment_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(attachment_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    field_values = {
        "Impacted Application": impacted_applications,
        "Issue Summary": issue_summary,
        "MAPS Lead Approval": maps_lead_approval,
        "Reviewed by CIO Dev Lead": cio_dev_lead_review,
        "Known Issue references": known_issue_reference,
        "Incident Number": incident_number,
        "Incident Priority": incident_priority,
        "Incident Urgency": incident_urgency,
        "Reason for Latent Fix": reason_for_latent_fix,
        "Impacted Location(s)": impacted_locations,
        "Business Impacted": business_impact,
        "Steps Needed for Remediation": remediation_steps
    }

    email_body = "<h3>Latent Request Approval</h3><table border='1'>" + "".join(
        f"<tr><td><b>{key}</b></td><td>{value}</td></tr>" for key, value in field_values.items()
    ) + "</table>"

    st.write("***Enter Recipients & Verify the E-Mail Details before send***")
    with st.expander("Email Details"):
        task_description = st.text_area("Task Description:", "Need to perform the recovery steps")
        to_list = st.text_area("***Must Enter To*** (comma-separated):", "shreyas.ganu@bofa.com").split(',')
        cc_list = st.text_area("***Must Enter CC*** (comma-separated):").split(',')
        st.write("Preview of EMail Body")
        st.markdown(email_body, unsafe_allow_html=True)

    if st.button("Send Email"):
        if validate_email_domain(to_list, list_type='to'):
            subject = f"{incident_number} - Latent Approval Request-TechDebt: {known_issue_reference}" if known_issue_reference else f"{incident_number} - Latent Approval Request"
            email_final_body = html_template.format(
                incident_number=incident_number,
                incident_priority=incident_priority,
                incident_urgency=incident_urgency,
                reason_for_latent_fix=reason_for_latent_fix,
                impacted_locations=impacted_locations,
                business_impact=business_impact,
                issue_summary=issue_summary,
                maps_lead_approval=maps_lead_approval,
                cio_dev_lead_review=cio_dev_lead_review,
                known_issue_reference=known_issue_reference,
                remediation_steps=remediation_steps,
                impacted_applications=impacted_applications,
                request_input_by=request_input_by
            )

            null_fields = [k for k, v in field_values.items() if k != "Known Issue references" and not v]
            if null_fields:
                st.warning(f"The following fields are empty: {', '.join(null_fields)}")
            else:
                send_email(to_list, cc_list, subject, email_final_body, attachment_path=attachment_path)
                st.success("Email sent successfully!")

                if attachment_path and os.path.exists(attachment_path):
                    os.remove(attachment_path)
