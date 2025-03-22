import paramiko
import time
import re
import logging
import socket
import select
from datetime import datetime, timedelta
from paramiko.ssh_exception import AuthenticationException, SSHException

logger = logging.getLogger(__name__)

def run_pbrun(hostname, username, password, pbrun_command, security_code, timeout=30):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=timeout)
    output = ''
    stage = 0  
    password_attempts = 0
    security_attempts = 0
    chan = None  # Ensure 'chan' is always defined

    try:
        logger.info(f"Connecting to {hostname} as {username}")
        client.connect(hostname, username=username, password=password, timeout=15)
        logger.info("SSH connection established")

        chan = client.invoke_shell()  
        chan.settimeout(10)
        logger.info("Opened interactive shell")

        chan.send(f"{pbrun_command}\n")
        time.sleep(1)

        while datetime.now() < end_time:
            if client.get_transport() is None or not client.get_transport().is_active():
                logger.error("SSH connection lost, aborting")
                break

            ready, _, _ = select.select([chan], [], [], 1)  # Efficiently wait for input
            if ready:
                chunk = chan.recv(4096).decode('utf-8', 'ignore')
                output += chunk
                logger.debug(f"Received chunk: {chunk.strip()}")

                if stage == 0 and re.search(r'[Pp]assword:\s*$', output):
                    if password_attempts > 1:
                        logger.error("Password prompt repeated, stopping execution")
                        break
                    chan.send(f"{password}\n")
                    time.sleep(1)
                    output = ''
                    stage = 1
                    password_attempts += 1
                    continue

                if stage == 1 and re.search(r'Security [Cc]ode:\s*$', output):
                    if security_attempts > 1:
                        logger.error("Security code prompt repeated, stopping execution")
                        break
                    chan.send(f"{security_code}\n")
                    time.sleep(1)
                    output = ''
                    stage = 2
                    security_attempts += 1
                    continue

        return output

    except AuthenticationException:
        logger.error("Authentication failed, please check credentials.")
        return "Error: Authentication failed"
    
    except SSHException as e:
        logger.error(f"SSH error: {str(e)}")
        return f"Error: SSH error - {str(e)}"
    
    except socket.timeout:
        logger.error("Connection timed out")
        return "Error: Connection timed out"
    
    except OSError as e:
        logger.error(f"Network error: {str(e)}")
        return f"Error: Network issue - {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Error: Unexpected issue - {str(e)}"

    finally:
        try:
            if chan is not None:
                chan.send("exit\n")
                time.sleep(0.5)
                chan.close()
            client.close()
            logger.info("Connection closed")
        except Exception:
            pass  # Avoid logging errors from cleanup operations
