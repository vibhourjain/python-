import streamlit as st
from datetime import datetime
import win32com.client

st.set_page_config(page_title="Polaris Release Email Generator", layout="centered")
st.title("Polaris Application Release Email Generator")

# === Form UI ===
with st.form("release_form"):
    notification_type = st.text_input("Notification Type", "Application Release")
    line_of_business = st.text_input("Line of Business", "GMOT Securities – Global")
    affected_app = st.text_input("Affected Application(s) or Service(s)", "Polaris -- 69135")
    crq_number = st.text_input("CRQ Reference Number(s)", "CRQ000014442086")
    
    start_time = st.datetime_input("Maintenance Window Start Time", datetime(2025, 5, 9, 17, 0))
    end_time = st.datetime_input("Maintenance Window End Time", datetime(2025, 5, 14, 0, 0))
    
    region = st.text_input("Region(s) Affected", "EMEA")
    impact = st.text_input("Impact", "EMEA")
    additional_details = st.text_input("Additional Details", "Polaris Strange Net logic in BME adapter")
    impacted_lob = st.text_input("Impacted LOB", "EMEA - Securities - Trades Processing")
    actions_required = st.text_input("Actions Required by Users", "None")
    escalation_contacts = st.text_input("Escalation Contacts", "DG MAPS Polaris")

    recipient = st.text_input("To (comma-separated emails)", "")

    submitted = st.form_submit_button("Generate Email")

# === Email HTML Construction ===
if submitted:
    email_html = f"""
    <div style="font-family: Arial, sans-serif; color: #000;">
        <h2 style="margin-bottom: 0;">Markets Application Production Services</h2>
        <p style="font-size: 16px;"><strong>A message from MAPS GMOT</strong></p>
        <h3 style="color: red; font-weight: bold;">POLARIS Prod Application Release</h3>

        <table style="border-collapse: collapse; width: 100%; font-size: 15px;">
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Notification Type</b></td><td style="border: 1px solid #ccc; padding: 6px;">{notification_type}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Line of Business</b></td><td style="border: 1px solid #ccc; padding: 6px;">{line_of_business}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Affected Application(s) or Service(s)</b></td><td style="border: 1px solid #ccc; padding: 6px;">{affected_app}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>CRQ Reference Number(s)</b></td><td style="border: 1px solid #ccc; padding: 6px;">{crq_number}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Maintenance Window Start Time</b></td><td style="border: 1px solid #ccc; padding: 6px;">{start_time.strftime('%m/%d/%Y %I:%M:%S %p IST')}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Maintenance Window End Time</b></td><td style="border: 1px solid #ccc; padding: 6px;">{end_time.strftime('%m/%d/%Y %I:%M:%S %p IST')}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Region(s) Affected</b></td><td style="border: 1px solid #ccc; padding: 6px;">{region}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Impact</b></td><td style="border: 1px solid #ccc; padding: 6px;">{impact}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Additional Details</b></td><td style="border: 1px solid #ccc; padding: 6px;">{additional_details}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Impacted LOB</b></td><td style="border: 1px solid #ccc; padding: 6px;">{impacted_lob}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Actions Required by Users</b></td><td style="border: 1px solid #ccc; padding: 6px;">{actions_required}</td></tr>
            <tr><td style="border: 1px solid #ccc; padding: 6px;"><b>Escalation Contacts</b></td><td style="border: 1px solid #ccc; padding: 6px;">{escalation_contacts}</td></tr>
        </table>
    </div>
    """

    st.markdown("### Preview:")
    st.markdown(email_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        send_now = st.button("Send Email via Outlook")
    with col2:
        save_draft = st.button("Save as Draft in Outlook")

    if send_now or save_draft:
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)
            mail.Subject = "POLARIS Prod Application Release"
            mail.To = recipient.strip()
            mail.HTMLBody = email_html

            if send_now:
                mail.Send()
                st.success("Email sent successfully.")
            elif save_draft:
                mail.Save()
                st.info("Email saved as a draft. Please review it in Outlook.")

        except Exception as e:
            st.error(f"Outlook operation failed: {str(e)}")