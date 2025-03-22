import pexpect

def run_powerbroker_command(host, user, initial_password, pb_command, pb_password, otp, actual_command):
    # Start an SSH session
    ssh_cmd = f"ssh {user}@{host}"
    child = pexpect.spawn(ssh_cmd, encoding='utf-8', timeout=30)

    # Expect the initial login prompt and send the password.
    child.expect("password:")
    child.sendline(initial_password)

    # Wait for the shell prompt (this may vary depending on your system).
    child.expect(r'\$')

    # Run the Power Broker command
    child.sendline(pb_command)

    # Now expect the prompt asking for Power Broker credentials.
    child.expect("Enter your Power Broker password:")
    child.sendline(pb_password)

    child.expect("Enter your 2FA OTP:")
    child.sendline(otp)

    # Wait for the prompt after the power broker command completes.
    child.expect(r'\$')

    # Finally, run your actual command.
    child.sendline(actual_command)
    child.expect(r'\$')

    # Capture and return the command output.
    output = child.before
    child.sendline("exit")
    child.close()
    return output

# Example usage:
host = "your.unix.host"
user = "username"
initial_password = "your_initial_password"
pb_command = "powerbroker_command"  # Replace with the actual command that triggers Power Broker
pb_password = "powerbroker_password"
otp = "your_2fa_code"
actual_command = "ls -l /some/path"  # Replace with your actual command

output = run_powerbroker_command(host, user, initial_password, pb_command, pb_password, otp, actual_command)
print(output)

import streamlit as st

host = st.text_input("Unix Host")
user = st.text_input("Username")
initial_password = st.text_input("Initial SSH Password", type="password")
pb_password = st.text_input("Power Broker Password", type="password")
otp = st.text_input("2FA OTP")
actual_command = st.text_input("Command to Execute")

if st.button("Run Command"):
    output = run_powerbroker_command(host, user, initial_password, "powerbroker_command", pb_password, otp, actual_command)
    st.text_area("Command Output", output, height=300)