import streamlit as st
from sre_automation.utils_email import validate_email_domain, send_email, get_formatted_text
import logging
import duckdb
from datetime import datetime

logger = logging.getLogger(__name__)

def store_latent_approval_in_duckdb(data: dict):
    db_path = "sre_database.duckdb"
    table_name = "latent_approvals"

    schema = """
        request_input_by TEXT,
        impacted_applications TEXT,
        issue_summary TEXT,
        maps_lead_approval TEXT,
        cio_dev_lead_review TEXT,
        known_issue_reference TEXT,
        incident_number TEXT,
        incident_priority TEXT,
        incident_urgency TEXT,
        reason_for_latent_fix TEXT,
        impacted_locations TEXT,
        business_impact TEXT,
        remediation_steps TEXT,
        submitted_at TIMESTAMP
    """

    conn = duckdb.connect(db_path)
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")

    placeholders = ", ".join(["?"] * (len(data) + 1))
    insert_sql = f"""
        INSERT INTO {table_name} VALUES ({placeholders})
    """

    conn.execute(insert_sql, list(data.values()) + [datetime.now()])
    conn.close()

def reset_form():
    for key in [
        "request_input_by", "impacted_applications", "issue_summary", "maps_lead_approval",
        "cio_dev_lead_review", "known_issue_reference", "incident_number", "incident_priority",
        "incident_urgency", "reason_for_latent_fix", "impacted_locations", "business_impact",
        "remediation_steps", "task_description", "to_list", "cc_list"
    ]:
        st.session_state[key] = ""

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

    request_input_by = st.text_input("Enter Your Name:", key="request_input_by")
    impacted_applications = st.text_input("Impacted Applications:", key="impacted_applications")
    issue_summary = get_formatted_text("Issue Summary:", key="issue_summary")
    maps_lead_approval = st.text_input("MAPS Lead Approval:", "Shreyas Ganu", key="maps_lead_approval")
    cio_dev_lead_review = st.text_input("Reviewed by CIO Dev Lead:", key="cio_dev_lead_review")
    known_issue_reference = st.text_input("Known Issue references (Jira/TechDebt/PKE): Leave Blank if not Applicable", key="known_issue_reference")

    incident_number = st.text_input("Incident Number:", key="incident_number").upper()
    incident_priority = st.text_input("Incident Priority:", "P3-L", key="incident_priority")
    incident_urgency = st.text_input("Incident Urgency:", "Medium", key="incident_urgency")
    reason_for_latent_fix = get_formatted_text("Reason for Latent Fix:", key="reason_for_latent_fix")
    impacted_locations = st.text_input("Impacted Location(s):", "Japan", key="impacted_locations")
    business_impact = get_formatted_text("Business Impact (Risk of Not Implementing):", key="business_impact")
    remediation_steps = get_formatted_text("Steps Needed for Remediation:", key="remediation_steps")

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
        task_description = st.text_area("Task Description:", "Need to perform the recovery steps", key="task_description")
        to_list = st.text_area("***Must Enter To*** (comma-separated):", "shreyas.ganu@bofa.com", key="to_list").split(',')
        cc_list = st.text_area("***Must Enter CC*** (comma-separated):", key="cc_list").split(',')
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
                send_email(to_list, cc_list, subject, email_final_body)
                store_latent_approval_in_duckdb({
                    "request_input_by": request_input_by,
                    "impacted_applications": impacted_applications,
                    "issue_summary": issue_summary,
                    "maps_lead_approval": maps_lead_approval,
                    "cio_dev_lead_review": cio_dev_lead_review,
                    "known_issue_reference": known_issue_reference,
                    "incident_number": incident_number,
                    "incident_priority": incident_priority,
                    "incident_urgency": incident_urgency,
                    "reason_for_latent_fix": reason_for_latent_fix,
                    "impacted_locations": impacted_locations,
                    "business_impact": business_impact,
                    "remediation_steps": remediation_steps
                })
                reset_form()
                st.success("Email sent successfully!")
