import streamlit as st
import win32com.client as win32
import pythoncom

def send_email(to_list, cc_list, subject, from_email, email_body):
    try:
        # Initialize the COM system
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
        mail.Sender = from_email

        # Send the email
        mail.Send()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")
    finally:
        # Uninitialize the COM system
        pythoncom.CoUninitialize()

def page_seek_approval():
    st.title("Seek Approval Form")
    # Add your form fields and logic here
    if st.button("Send Email"):
        send_email(
            to_list=["recipient1@jpmc.com"],
            cc_list=["manager@jpmc.com"],
            subject="Test Email",
            from_email="your.email@jpmc.com",
            email_body="<h3>This is a test email</h3>"
        )

def main():
    page_seek_approval()

if __name__ == "__main__":
    main()
