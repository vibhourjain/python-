from flask import Flask, request, render_template_string
import smtplib
from email.mime.text import MIMEText
from utils_unix import run_powerbroker_command

app = Flask(__name__)

# Fixed Parameters (Replace with your values)
HOSTNAME = "your_hostname"
USERNAME = "your_username"
PBRUN_COMMAND = "your_command"

# Email Configuration (Replace with your SMTP details)
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
EMAIL_USER = "developer@company.com"
EMAIL_PASSWORD = "email_password"
MANAGER_EMAIL = "manager@company.com"

def send_execution_email():
    """Sends email to manager with the execution link."""
    url = "http://your-server-ip:5000/execute"  # Update with your server IP
    body = f"Click the link to execute the command: {url}"
    
    msg = MIMEText(body)
    msg['Subject'] = "Action Required: Execute Server Command"
    msg['From'] = EMAIL_USER
    msg['To'] = MANAGER_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
    print("[+] Email sent to manager.")

@app.route('/execute', methods=['GET', 'POST'])
def handle_execution():
    """Handles form display and command execution."""
    if request.method == 'POST':
        password = request.form.get('password')
        otp = request.form.get('otp')
        # Execute the command
        output, error = run_powerbroker_command(
            HOSTNAME, USERNAME, password, PBRUN_COMMAND, otp
        )
        return "Command executed. Check server logs for details."
    # Show input form for GET requests
    form = """
    <h3>Enter Credentials</h3>
    <form method="POST">
      Password: <input type="password" name="password" required><br><br>
      OTP: <input type="text" name="otp" required><br><br>
      <input type="submit" value="Execute">
    </form>
    """
    return render_template_string(form)

if __name__ == '__main__':
    send_execution_email()  # Developer sends email on startup
    app.run(host='0.0.0.0', port=5000)  # Accessible from all interfaces
	
