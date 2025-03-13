from flask import Flask, request, render_template_string, jsonify
from utils_unix import run_powerbroker_command

app = Flask(__name__)

# HTML Form Template
html_form = """
<!DOCTYPE html>
<html>
<head>
    <title>Run PowerBroker Command</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; }
        h2 { color: #333; }
        form { width: 300px; padding: 20px; border: 1px solid #ddd; background: #f9f9f9; }
        input { width: 100%; padding: 8px; margin: 5px 0; }
        button { background: #4CAF50; color: white; padding: 10px; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h2>Enter Your Credentials</h2>
    <form action="/execute_command" method="post">
        <label>Username:</label> <input type="text" name="username" required><br>
        <label>Password:</label> <input type="password" name="password" required><br>
        <label>OTP:</label> <input type="text" name="otp" required><br>
        <input type="hidden" name="powerbrokerCommand" value="{{ powerbrokerCommand }}">
        <input type="hidden" name="clientID" value="{{ clientID }}">
        <button type="submit">Run Command</button>
    </form>
</body>
</html>
"""

@app.route("/run_command", methods=["GET"])
def show_form():
    # Extract command details from the URL
    powerbrokerCommand = request.args.get("powerbrokerCommand")
    clientID = request.args.get("clientID")

    # Render the HTML form where the user enters credentials
    return render_template_string(html_form, powerbrokerCommand=powerbrokerCommand, clientID=clientID)

@app.route("/execute_command", methods=["POST"])
def execute_powerbroker():
    # Extract user inputs from form submission
    hostname = "your-hostname"  # Replace with actual PowerBroker server hostname
    username = request.form.get("username")
    password = request.form.get("password")
    security_code = request.form.get("otp")  # OTP is the security code
    pbrun_command = request.form.get("powerbrokerCommand")
    client_id = request.form.get("clientID")

    # Validate required parameters
    if not all([username, password, security_code, pbrun_command]):
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    try:
        # Execute PowerBroker command
        output, error = run_powerbroker_command(hostname, username, password, pbrun_command, security_code)

        if error:
            return f"<h3 style='color:red;'>Error: {error}</h3>"
        else:
            return f"<h3 style='color:green;'>Success! Output:<br><pre>{output}</pre></h3>"

    except Exception as e:
        return f"<h3 style='color:red;'>Unexpected Error: {str(e)}</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

