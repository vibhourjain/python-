import streamlit as st

# Define the HTML template
html_template = """
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        table {{ width: 60%; margin: 0 auto; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; color: #333; }}
        .header {{ color: #4CAF50; font-size: 24px; margin-bottom: 20px; text-align: center; }}
        .sub-header {{ font-size: 18px; font-weight: bold; color: #333; }}
        .field {{ font-weight: bold; }}
        .value {{ font-weight: normal; }}
    </style>
</head>
<body>
    <div class="header">Latent Request Approval Template</div>

    <table>
        <!-- Main Header -->
        <tr>
            <th colspan="2" class="header">Latent Request Approval Template</th>
        </tr>

        <!-- Incident Details (Sub-Header) -->
        <tr>
            <th colspan="2" class="sub-header">Incident Details</th>
        </tr>
        <tr>
            <td class="field">Incident Number</td>
            <td class="value">{incident_number}</td>
        </tr>
        <tr>
            <td class="field">Incident Priority</td>
            <td class="value">{incident_priority}</td>
        </tr>
        <tr>
            <td class="field">Incident Urgency</td>
            <td class="value">{incident_urgency}</td>
        </tr>
        <tr>
            <td class="field">Reason for Latent Fix</td>
            <td class="value">{reason_for_latent_fix}</td>
        </tr>
        <tr>
            <td class="field">Impacted Location(s)</td>
            <td class="value">{impacted_locations}</td>
        </tr>
        <tr>
            <td class="field">Business Impacted (Risk of Not Implementing)</td>
            <td class="value">{business_impact}</td>
        </tr>

        <!-- Impacted Applications -->
        <tr>
            <td class="field">Impacted Applications</td>
            <td class="value">{impacted_applications}</td>
        </tr>

        <!-- Issue Summary -->
        <tr>
            <td class="field">Issue Summary</td>
            <td class="value">{issue_summary}</td>
        </tr>

        <!-- MAPS Lead Approval -->
        <tr>
            <td class="field">MAPS Lead Approval</td>
            <td class="value">{maps_lead_approval}</td>
        </tr>

        <!-- Reviewed by CIO Dev Lead -->
        <tr>
            <td class="field">Reviewed by CIO Dev Lead</td>
            <td class="value">{cio_dev_lead_review}</td>
        </tr>

        <!-- Remediation (Sub-Header) -->
        <tr>
            <th colspan="2" class="sub-header">Remediation</th>
        </tr>
        <tr>
            <td class="field">Steps Need to be Performed for Remediation</td>
            <td class="value">{remediation_steps}</td>
        </tr>
    </table>

    <div class="footer">
        <p>This is an automated email. Please do not reply.</p>
    </div>
</body>
</html>
"""

# Streamlit form to collect input
st.title("Latent Request Approval Form")

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
remediation_steps = st.text_area("Steps Need to be Performed for Remediation:")

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
    # Render the HTML
    st.markdown(email_body, unsafe_allow_html=True)
