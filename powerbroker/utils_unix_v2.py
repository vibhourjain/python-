import paramiko
import time
import re
import logging
import socket
import select
from datetime import datetime, timedelta
from paramiko.ssh_exception import AuthenticationException, SSHException

logger = logging.getLogger(__name__)

def execute_ssh_command(hostname, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        return output, error
    except Exception as e:
        return None, str(e)

def run_powerbroker_command(hostname, username, password, pbrun_command, security_code, timeout=30):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=timeout)
    output = ''
    error = None
    stage = 0
    password_attempts = 0
    security_attempts = 0
    chan = None

    try:
        logger.info(f"Connecting to {hostname} as {username}")
        client.connect(hostname, username=username, password=password, timeout=15)
        logger.info("SSH connection established")

        chan = client.invoke_shell()
        chan.settimeout(10)
        logger.info("Opened interactive shell")

        chan.send(f"{pbrun_command}\n")
        start_pbrun_time = time.time()
        logger.info("Sent PowerBroker command")

        while datetime.now() < end_time:
            if client.get_transport() is None or not client.get_transport().is_active():
                error = "SSH connection lost, aborting"
                logger.error(error)
                return "", error  

            ready, _, _ = select.select([chan], [], [], 0.2)
            if ready:
                chunk = chan.recv(4096).decode('utf-8', 'ignore')
                output += chunk
                logger.debug(f"Received chunk: {chunk.strip()}")

                if stage == 0 and re.search(r'[Pp]assword:\s*$', output):
                    password_time = time.time()
                    logger.info(f"Password prompt received after {password_time - start_pbrun_time:.2f} seconds")
                    if password_attempts > 1:
                        error = "Password prompt repeated, stopping execution"
                        logger.error(error)
                        return "", error
                    chan.send(f"{password}\n")
                    output = ''
                    stage = 1
                    password_attempts += 1
                    continue

                if stage == 1 and re.search(r'Security [Cc]ode:\s*$', output):
                    if security_attempts > 1:
                        error = "Security code prompt repeated, stopping execution"
                        logger.error(error)
                        return "", error                    
                    security_time = time.time()
                    logger.info(f"Security code prompt received after {security_time - password_time:.2f} seconds")
                    chan.send(f"{security_code}\n")
                    output = ''
                    stage = 2
                    security_attempts += 1
                    continue

                if "Expected Output Pattern" in output:  # Change this based on expected end condition
                    end_time = time.time()
                    logger.info(f"Command completed in {end_time - start_pbrun_time:.2f} seconds")
                    break

        return output, None

    except Exception as e:
        error = f"Error: {str(e)}"
        logger.error(error)
        return "", error

    finally:
        try:
            if chan:
                chan.send("exit\n")
                time.sleep(0.2)
                chan.close()
                client.close()
                logger.info("Connection closed")
