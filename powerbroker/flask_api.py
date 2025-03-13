from flask import Flask, request, jsonify
from utils_unix import run_powerbroker_command

app = Flask(__name__)

@app.route("/run_command", methods=["GET"])
def execute_powerbroker():
    # Extract parameters from API call
    hostname = "your-hostname"  # Replace with the actual PowerBroker server
    username = request.args.get("username")
    password = request.args.get("password")
    security_code = request.args.get("otp")  # OTP is the security code
    pbrun_command = request.args.get("powerbrokerCommand")
    client_id = request.args.get("clientID")

    # Validate required parameters
    if not all([username, password, security_code, pbrun_command]):
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    try:
        # Execute PowerBroker Command
        output, error = run_powerbroker_command(hostname, username, password, pbrun_command, security_code)

        if error:
            return jsonify({"status": "error", "message": error}), 500
        else:
            return jsonify({"status": "success", "output": output})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
