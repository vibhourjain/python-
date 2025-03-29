📌 How It Works
1. User runs Streamlit app (power_broker_email.py)
	1.1 Selects PowerBroker command & Client ID
	1.2 Email is sent to approvers with an API link

2. User opens the email & clicks the link
	2.1 They replace XXXX, YYYY, ZZZZ with Username, Password, OTP
	2.2 API is triggered 🚀 instantly

3. Flask API executes run_powerbroker_command
	3.1 Returns command output or an error message
	3.2 Runs within 10-15 seconds.
	
	
✅ Security Considerations
No authentication delay → Instant execution
Email-based approval → Ensures only authorized users trigger the command
Minimal user input on mobile → Just replace Username, Password & OTP
