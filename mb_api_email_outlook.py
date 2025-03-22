from flask import Flask, request, render_template_string
import win32com.client  # Requires pywin32 (install with: pip install pywin32)
from utils_unix import run_powerbroker_command

app = Flask(__name__)

# Fixed Parameters (Replace with your values)
HOSTNAME = "your_hostname"
USERNAME = "your_username"
PBRUN_COMMAND = "your_command"
MANAGER_EMAIL = "manager@company.com"

def send_execution_email():
    """Sends email via Outlook desktop client."""
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0 = MailItem
    
    # Replace with your server's URL
    url = "http://your-server-ip:5000/execute"  
    body = f"Click the link to execute the command: {url}"
    
    mail.Subject = "Action Required: Execute Server Command"
    mail.To = MANAGER_EMAIL
    mail.Body = body
    
    # Send email (Outlook must be logged in and configured)
    mail.Send()
    print("[+] Email sent via Outlook desktop client.")

@app.route('/execute', methods=['GET', 'POST'])
def handle_execution():
    """Handles form submission (same logic as before)."""
    if request.method == 'POST':
        password = request.form.get('password')
        otp = request.form.get('otp')
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
    send_execution_email()  # Developer sends email via Outlook
    app.run(host='0.0.0.0', port=5000)