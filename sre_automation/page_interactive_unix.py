import streamlit as st
from utils_unix import run_powerbroker_command


def page_interactive_broker():
    st.title("Interactive Unix Host Command Executor")

    hostname = st.text_input("Hostname (e.g., example.com):")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    actual_command = st.text_input("Enter the command to execute:")
    otp = st.text_input("2FA OTP")
    
    

    if st.button("Run Command"):
        if not hostname or not username or not password or not actual_command or not otp:
            st.warning("Please fill in all fields.")
        else:
            with st.spinner("Executing command..."):
                output, error = run_powerbroker_command(hostname, username, password, actual_command, otp)
                if output:
                    st.success("Command executed successfully!")
                    st.write("### Output:")
                    st.code(output)
                if error:
                    st.error("Error occurred:")
                    st.code(error)