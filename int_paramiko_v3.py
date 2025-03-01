import paramiko
import time
import re
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='pbrun_execution.log',
    filemode='a'
)
logger = logging.getLogger('pbrun_runner')

def run_pbrun(
    hostname,
    username,
    password,
    pbrun_command,
    security_code,
    timeout=120
):
    """
    Logs into a UNIX server via SSH, executes a `pbrun` command, and handles interactive prompts.
    
    Parameters:
        hostname (str): Target server.
        username (str): SSH username.
        password (str): SSH password.
        pbrun_command (str): Command to execute via `pbrun`.
        security_code (str): 6-digit security code for authentication.
        timeout (int): Total timeout in seconds.
    
    Returns:
        str: Command output or error message.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    start_time = datetime.now()
    output = ''
    stage = 0  # 0 = Waiting for password, 1 = Waiting for security code, 2 = Execution complete
    
    try:
        # Connect to SSH
        logger.info(f"Connecting to {hostname} as {username}")
        client.connect(hostname, username=username, password=password, timeout=15)
        logger.info("SSH connection established")

        # Open an interactive shell session
        chan = client.invoke_shell()
        chan.settimeout(10)  # Set a per-operation timeout
        logger.info("Opened interactive shell")

        # Send the `pbrun` command
        chan.send(f"{pbrun_command}\n")
        time.sleep(1)  # Allow time for prompt to appear

        while datetime.now() - start_time < timedelta(seconds=timeout):
            if chan.recv_ready():
                chunk = chan.recv(4096).decode('utf-8', 'ignore')
                output += chunk
                logger.debug(f"Received chunk: {chunk.strip()}")

                # Handle password prompt
                if stage == 0 and re.search(r'[Pp]assword:\s*$', output):
                    chan.send(f"{password}\n")
                    time.sleep(1)  # Allow server to process
                    output = ''  # Clear buffer after sending password
                    stage = 1
                    logger.info("Password submitted")
                    continue

                # Handle security code prompt
                if stage == 1 and re.search(r'Security [Cc]ode:\s*$', output):
                    chan.send(f"{security_code}\n")
                    time.sleep(1)  # Allow server to process
                    output = ''
                    stage = 2
                    logger.info("Security code submitted")
                    continue

                # Detect authentication success
                if stage == 2 and re.search(r'(successfully|authorized|granted|Welcome)', output, re.I):
                    logger.info("Authentication successful")
                    break

            # Check if process exited
            if chan.exit_status_ready():
                logger.info("Process completed")
                break

            time.sleep(0.5)

        # Capture final output
        time.sleep(1)
        while chan.recv_ready():
            output += chan.recv(4096).decode('utf-8', 'ignore')

        return output

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        return f"Error: {str(e)}"

    finally:
        try:
            # Gracefully close the connection
            if chan and chan.active:
                chan.send('\x03')  # Send Ctrl+C to terminate any running command
                time.sleep(0.5)
            client.close()
            logger.info("Connection closed")
        except Exception:
            pass


# Usage Example
if __name__ == "__main__":
    try:
        result = run_pbrun(
            hostname="your-server.com",
            username="your_username",
            password="your_password",
            pbrun_command="pbrun /bin/bash",
            security_code="123456"
        )
        print("Execution Result:\n", result)
    except Exception as e:
        print("Failed:", str(e))
