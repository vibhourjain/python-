import streamlit as st
from utils_unix import find_files_in_remote_path, gzip_files_on_remote_host

def page_ssh_file_operations():
    st.title("Remote File Operations")

    # Inputs for connection details
    hostname = st.text_input("Hostname (e.g., example.com):")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    # Input for first command to run
    command_1 = st.text_area("First Command (Any arbitrary command):", height=100)

    # Input for second command to find files
    path = st.text_input("Path to search for files:")
    file_criteria = st.text_input("File criteria (e.g., -name '*.log' or -type f):")

    # Button to execute commands
    if st.button("Execute Commands"):
        if not hostname or not username or not password:
            st.warning("Please fill in the connection details.")
        elif not command_1 or not path or not file_criteria:
            st.warning("Please provide all the necessary inputs.")
        else:
            with st.spinner("Executing commands..."):
                # First command execution
                output, error = execute_ssh_command(hostname, username, password, command_1)
                if error:
                    st.error(f"Error executing command 1: {error}")
                else:
                    st.success("First command executed successfully!")
                    st.write(f"Command 1 Output: {output}")

                # Second command to find files
                files, error = find_files_in_remote_path(hostname, username, password, path, file_criteria)
                if error:
                    st.error(f"Error finding files: {error}")
                else:
                    st.success("Files found successfully!")
                    st.write(f"Files found: {files}")

                    # Select files to gzip
                    selected_files = st.multiselect("Select files to Gzip", files)

                    # Button to gzip selected files
                    if st.button("Gzip Selected Files"):
                        if selected_files:
                            gzip_result = gzip_files_on_remote_host(hostname, username, password, selected_files)
                            st.success(gzip_result)
                        else:
                            st.warning("Please select at least one file to gzip.")
