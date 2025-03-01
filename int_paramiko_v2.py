import paramiko
import time
import re
import logging
from datetime import datetime, timedelta

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='pbrun_execution.log',
    filemode='a'
)

def run_pbrun(
    hostname,
    username,
    password,
    pbrun_command,
    pb_password,
    security_code,
    timeout=120  # 2 minutes total timeout
):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    logger = logging.getLogger('pbrun_runner')
    start_time = datetime.now()
    
    try:
        # Connect with timeout
        client.connect(
            hostname,
            username=username,
            password=password,
            timeout=15  # Separate connection timeout
        )
        logger.info(f"Connected to {hostname}")

        chan = client.invoke_shell()
        chan.settimeout(15)  # Per-operation timeout
        logger.info("Interactive shell opened")

        # Send pbrun command
        chan.send(f"{pbrun_command}\n")
        logger.debug("Sent pbrun command")

        output = ''
        stage = 0
        auth_attempted = False
        success = False

        while datetime.now() - start_time < timedelta(seconds=timeout):
            if chan.recv_ready():
                chunk = chan.recv(4096).decode('utf-8', 'ignore')
                output += chunk
                logger.debug(f"Received chunk: {chunk.strip()}")

                # Detect authentication failure
                if re.search(r'(authentication failed|invalid credentials)', output, re.I):
                    logger.error("Authentication failure detected")
                    raise ValueError("Authentication failed")

                # Password prompt handling
                if stage == 0 and re.search(r'[Pp]assword:\s*$', output):
                    if auth_attempted:
                        logger.error("Duplicate password prompt - likely incorrect credentials")
                        raise ValueError("Invalid credentials")
                        
                    chan.send(f"{pb_password}\n")
                    logger.info("Password submitted")
                    auth_attempted = True
                    output = ''
                    stage = 1
                    continue

                # Security code handling
                if stage == 1 and re.search(r'Security [Cc]ode:\s*$', output):
                    chan.send(f"{security_code}\n")
                    logger.info("Security code submitted")
                    output = ''
                    stage = 2
                    continue

                # Success detection
                if stage == 2 and re.search(r'(successfully|authorized)', output, re.I):
                    logger.info("Authentication successful")
                    success = True
                    break

            # Check for exit conditions
            if chan.exit_status_ready():
                break

            time.sleep(0.1)

        if not success:
            logger.error("Process timed out or failed")
            raise TimeoutError("Operation did not complete within 2 minutes")

        # Final output collection
        time.sleep(1)
        while chan.recv_ready():
            output += chan.recv(4096).decode('utf-8', 'ignore')

        return output

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        raise  # Re-raise exception for caller handling
    finally:
        try:
            # Send Ctrl+C if still connected
            if chan.active:
                chan.send('\x03')
                time.sleep(0.5)
            client.close()
            logger.info("Connection closed")
        except:
            pass

# Usage
try:
    result = run_pbrun(
        hostname="your-server.com",
        username="user",
        password="ssh_pass",
        pbrun_command="pbrun /bin/bash",
        pb_password="pb_pass",
        security_code="123456"
    )
    print("Success:", result)
except Exception as e:
    print("Failed:", str(e))
