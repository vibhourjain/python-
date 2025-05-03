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
        time.sleep(1)

        while datetime.now() < end_time:
            if client.get_transport() is None or not client.get_transport().is_active():
                error = "SSH connection lost, aborting"
                logger.error(error)
                return "", error  # Return empty output with error message

            ready, _, _ = select.select([chan], [], [], 1)
            if ready:
                chunk = chan.recv(4096).decode('utf-8', 'ignore')
                output += chunk
                logger.debug(f"Received chunk: {chunk.strip()}")

                if stage == 0 and re.search(r'[Pp]assword:\s*$', output):
                    if password_attempts > 1:
                        error = "Password prompt repeated, stopping execution"
                        logger.error(error)
                        return "", error
                    chan.send(f"{password}\n")
                    time.sleep(1)
                    output = ''
                    stage = 1
                    password_attempts += 1
                    continue

                if stage == 1 and re.search(r'Security [Cc]ode:\s*$', output):
                    if security_attempts > 1:
                        error = "Security code prompt repeated, stopping execution"
                        logger.error(error)
                        return "", error
                    chan.send(f"{security_code}\n")
                    time.sleep(1)
                    output = ''
                    stage = 2
                    security_attempts += 1
                    continue

        return output, None  # Return output with no error

    except AuthenticationException:
        error = "Authentication failed, please check credentials."
        logger.error(error)
        return "", error

    except SSHException as e:
        error = f"SSH error: {str(e)}"
        logger.error(error)
        return "", error

    except socket.timeout:
        error = "Connection timed out"
        logger.error(error)
        return "", error

    except OSError as e:
        error = f"Network error: {str(e)}"
        logger.error(error)
        return "", error

    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        logger.error(error)
        return "", error

    finally:
        try:
            if chan is not None:
                chan.send("exit\n")
                time.sleep(0.5)
                chan.close()
            client.close()
            logger.info("Connection closed")
        except Exception:
            pass

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

