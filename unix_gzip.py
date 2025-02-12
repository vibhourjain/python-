#ssh_utils.py
import paramiko
import os

def execute_ssh_command(hostname, username, password, command):
    """Execute a command on a remote server via SSH and return output."""
    try:
        # Set up SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)

        # Execute the first user command
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        ssh.close()
        
        if error:
            return None, error
        return output, None
    except Exception as e:
        return None, str(e)

def find_files_in_remote_path(hostname, username, password, path, file_criteria):
    """Find files on the remote host based on criteria in the given path."""
    find_command = f"find {path} {file_criteria}"
    output, error = execute_ssh_command(hostname, username, password, find_command)
    
    if error:
        return None, error
    else:
        # Return list of files found
        return output.splitlines(), None

def gzip_files_on_remote_host(hostname, username, password, files):
    """Gzip the given list of files on the remote host."""
    for file in files:
        gzip_command = f"gzip {file}"
        output, error = execute_ssh_command(hostname, username, password, gzip_command)
        if error:
            return f"Error compressing file {file}: {error}"
    
    return "Files successfully compressed."


##page_ssh.py
import streamlit as st
from utils.ssh_utils import find_files_in_remote_path, gzip_files_on_remote_host

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

if __name__ == "__main__":
    page_ssh_file_operations()


streamlit_app/
│── app.py              # Main entry point
│── pages/
│   │── page_sql.py     # SQL Query Runner page
│   │── page_ssh.py     # Remote Unix Command Executor page
│   │── page_ssh_file_operations.py  # SSH File Operations (new)
│   │── page_monthly_task.py  # Monthly Task page
│── utils/
│   │── ssh_utils.py    # SSH utility functions (new)
│── requirements.txt    # Python dependencies
