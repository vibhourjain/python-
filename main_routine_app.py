import streamlit as st
import win32com.client as win32
import re

# Initialize session state for popup and email data
if "show_popup" not in st.session_state:
    st.session_state.show_popup = False
if "email_data" not in st.session_state:
    st.session_state.email_data = {"to": "", "cc": "", "subject": "", "body": ""}

# Function to send email using Outlook
def send_email(to, cc, subject, body):
    try:
        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = to
        mail.CC = cc
        mail.Subject = subject
        mail.HTMLBody = body
        mail.Send()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Function to validate email domain
def validate_email_list(email_list):
    if not email_list:
        return True  # Allow empty CC field
    emails = [email.strip() for email in email_list.split(",")]
    return all(re.match(r"^[a-zA-Z0-9._%+-]+@jpmc\.com$", email) for email in emails)

# Main UI
st.title("Latent Request Approval Form")

# List of applications for dropdown
application_names = sorted(["OSCAR", "PETA", "MADMACS"])

# Form fields
user_inputs = {}
user_inputs["Incident Details"] = st.text_input("Incident Details")

# Dropdown for Impacted Application
user_inputs["Impacted Application"] = st.selectbox("Impacted Application", application_names)

user_inputs["Issue Summary"] = st.text_input("Issue Summary")

# Editable MAPS Lead Approval with default value
user_inputs["MAPS Lead Approval"] = st.text_input("MAPS Lead Approval", value="sachin.patil@jpmc.com")

user_inputs["Reviewed by CIO Dev Lead"] = st.text_input("Reviewed by CIO Dev Lead")
user_inputs["Incident Number"] = st.text_input("Incident Number")
user_inputs["Incident Priority"] = st.text_input("Incident Priority")

# Automatically generate subject based on Incident Number
incident_number = user_inputs["Incident Number"]
generated_subject = f"{incident_number} - Latent Approval Request" if incident_number else "Latent Approval Request"

# Button to trigger the email popup
if st.button("Seek Approval"):
    st.session_state.show_popup = True

# Pop-up section
if st.session_state.show_popup:
    st.subheader("Send Email")

    # Preserve user input in session state
    to_input = st.text_input("To", value=st.session_state.email_data["to"])
    cc_input = st.text_input("CC", value=st.session_state.email_data["cc"])
    
    # Subject auto-filled based on Incident Number
    st.session_state.email_data["subject"] = st.text_input("Subject", value=generated_subject, disabled=True)

    # Generate email table with entered values
    email_body = "<p><b>Latent Request Approval:</b></p><table border='1' style='border-collapse: collapse;'>"
    email_body += "<tr><th colspan='2' style='background-color: #D3D3D3; text-align: center;'>Latent Request Approval</th></tr>"
    for key, value in user_inputs.items():
        email_body += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
    email_body += "</table>"

    # Store the generated body
    st.session_state.email_data["body"] = email_body

    # Display email preview
    st.markdown(email_body, unsafe_allow_html=True)

    # Validate email domain
    is_to_valid = validate_email_list(to_input)
    is_cc_valid = validate_email_list(cc_input)

    if not is_to_valid:
        st.error("Invalid email in 'To' field. Only emails ending with '@jpmc.com' are allowed.")
    if not is_cc_valid:
        st.error("Invalid email in 'CC' field. Only emails ending with '@jpmc.com' are allowed.")

    # Send Email button (enabled only if validation passes)
    if is_to_valid and is_cc_valid:
        if st.button("Send Email"):
            send_email(to_input, cc_input, st.session_state.email_data["subject"], st.session_state.email_data["body"])

    # Close pop-up button
    if st.button("Close"):
        st.session_state.show_popup = False
