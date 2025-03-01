import smtplib
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Outlook SMTP Configuration
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
OUTLOOK_EMAIL = "your_outlook_email@example.com"  # Replace with your Outlook email
OUTLOOK_PASSWORD = "your_password"  # Use an App Password if 2FA is enabled
print("hello")
def send_email_outlook(sender, recipients, cc, subject, body, attachment=None, filename=None):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg["CC"] = ", ".join(cc) if cc else ""
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach the file if provided
        if attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

        # Connect to Outlook SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
        server.sendmail(sender, recipients + cc, msg.as_string())
        server.quit()
        
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"
