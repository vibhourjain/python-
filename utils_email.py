import streamlit as st
import win32com.client as win32
import pythoncom
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

def validate_email_domain(email_list, domain="homecbinet.com"):
            invalid_emails = [email.strip() for email in email_list if not email.strip().endswith(f"@{domain}")]
            if invalid_emails:
                st.error(f"The following emails are not from the {domain} domain: {', '.join(invalid_emails)}")
                return False
            return True
            
            
def validate_email_domain_v2(email_list, list_type, domain="homecbinet.com"):
    if list_type == 'to' and not email_list:
        st.error(f"No E-Mail specified in To-list")
        return False
        
    if list_type == 'cc' and not email_list:
        st.write(f"No cc-list")
        return False
        
        
    invalid_emails = [email.strip() for email in email_list if not email.lower().strip().endswith(f"@{domain}")]
    if invalid_emails:
        st.error(f"The following emails are not from the {domain} domain: {', '.join(invalid_emails)}")
        return False
    return True

def send_email(to_list, cc_list, subject, email_body):
    logger.info("Working on sending E-Mail")
    try:
        pythoncom.CoInitialize()
        # Create Outlook application object
        outlook = win32.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)  # 0 represents an email item

        # Set email properties
        mail.Subject = subject
        mail.BodyFormat = 2  # 2 = HTML format
        mail.HTMLBody = email_body
        mail.To = "; ".join(to_list)  # Use semicolon as separator for multiple recipients
        mail.CC = "; ".join(cc_list)  # Use semicolon as separator for CC recipients
        # mail.Sender = from_email

        # Send the email
        mail.Send()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        logger.info(f"Failed to send email: {e}")

def send_mailto_email(to_list, cc_list, subject, email_body):
    subject = subject
    to_email = "; ".join(to_list)

    encoded_body = quote(email_body)

    mailto_link = f"mailto:{to_email}?subject={quote(subject)}&body={encoded_body}"
    st.markdown(f'<a href="{mailto_link}" target="_blank">Click here to send email</a>', unsafe_allow_html=True)
    
def list_outlook_mailboxes():
    try:
        # Connect to Outlook
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")

        # Get all mailboxes
        mailboxes = [namespace.Folders.Item(i+1).Name for i in range(namespace.Folders.Count)]

        print("Configured Mailboxes in Outlook:")
        for idx, mailbox in enumerate(mailboxes, start=1):
            print(f"{idx}. {mailbox}")

    except Exception as e:
        print(f"Error: {e}")