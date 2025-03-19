from flask import Flask, request, render_template_string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Unix group and hostname mappings
unix_groups = {
    'pb1a': ['cosmos', 'opec'],
    'pb2a': ['sify'],
    'pb3a': ['jap', 'aus']
}

hostnames = {
    'pb1a': 'host1',
    'pb2a': 'host2',
    'pb3a': 'host3'
}

def get_unix_group(service_account):
    for group, accounts in unix_groups.items():
        if service_account in accounts:
            return group
    return None

def get_hostname(unix_group):
    return hostnames.get(unix_group, 'unknown_host')

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
    <form action="/execute_pbrun" method="post">
        <label>Username:</label> <input type="text" name="username" required><br>
        <label>Password:</label> <input type="password" name="password" required><br>
        <label>Security Code:</label> <input type="text" name="security_code" required><br>
        <input type="hidden" name="powerbrokerCommand" value="{{ powerbrokerCommand }}">
        <input type="hidden" name="user_id" value="{{ user_id }}">
        <button type="submit">Run Command</button>
    </form>
</body>
</html>
"""

@app.route('/initiate_pbrun', methods=['GET'])
def initiate_pbrun():
    service_account = request.args.get('service_account')
    users = request.args.get('user_id')
    
    if not service_account or not users:
        logging.warning("Missing service_account or user_id in request")
        return "Error: Missing service_account or user_id"
    
    unix_group = get_unix_group(service_account)
    if not unix_group:
        logging.error(f"Invalid service account: {service_account}")
        return "Error: Invalid service account"
    
    power_broker_grantee = users[:7]  # Extract first 7 characters of user_id
    powerbroker_command = f"pbrun {unix_group} initbreakglass-{service_account} {power_broker_grantee}"
    logging.info(f"Generated powerbroker command: {powerbroker_command}")
    
    return render_template_string(html_form, powerbrokerCommand=powerbroker_command, user_id=power_broker_grantee)

@app.route('/execute_pbrun', methods=['POST'])
def execute_pbrun():
    service_account = request.form['service_account']
    users = request.form['user_id']
    username = request.form['username']
    password = request.form['password']
    security_code = request.form['security_code']
    powerbroker_command = request.form['powerbrokerCommand']
    
    logging.info(f"Executing PowerBroker command for user ID: {users}")
    
    output, error = ("output", "error")  # Placeholder for command execution
    # output, error = utils_unix.run_powerbroker_command(hostname, username, password, powerbroker_command, security_code)
    
    if error:
        logging.error(f"Error executing command: {error}")
        return f"Output: {output}<br>Error: {error}"
    else:
        logging.info("Command executed successfully")
        return f"Success! Output: {output}"

@app.route('/health')
def health_check():
    return "API is running", 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
