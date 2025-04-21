import streamlit as st
import win32com.client as win32
import pythoncom
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

def get_formatted_text(label: str, value: str = "", key=None):
    text = st.text_area(label, value=value, key=key)
    return text.replace('\n', '<br>') if text else ""


def validate_email_domain(email_list, list_type, domain="bofa.com"):
    if list_type == 'to' and not email_list:
        st.error("No E-Mail specified in To list")
        return False
    if list_type == 'cc' and not email_list:
        st.write("No cc")
        return False
    invalid_emails = [email.strip() for email in email_list if not email.lower().strip().endswith(f"@{domain}")]
    if invalid_emails:
        st.error(f"The following emails are not from the domain {domain}: {', '.join(invalid_emails)}")
        return False
    return True

def send_email(to_list, cc_list, subject, email_body):
    try:
        pythoncom.CoInitialize()
        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.Subject = subject
        mail.BodyFormat = 2
        mail.HTMLBody = email_body
        mail.To = ";".join(to_list)
        mail.CC = ";".join(cc_list)
        mail.Send()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

def send_mailto_email(to_list, cc_list, subject, email_body):
    subject = subject
    to_email = ",".join(to_list)
    encoded_body = quote(email_body)
    mailto_link = f"mailto:{to_email}?subject={quote(subject)}&body={encoded_body}"
    st.markdown(f'<a href="{mailto_link}" target="_blank">Click here to send email</a>', unsafe_allow_html=True)

def list_outlook_mailboxes():
    outlook = win32.Dispatch("Outlook.Application").GetNamespace("MAPI")
    mailboxes = [outlook.Folders.Item(i).Name for i in range(outlook.Folders.Count)]
    return mailboxes
