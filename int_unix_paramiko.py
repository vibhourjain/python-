import paramiko
import time

def paramiko_powerbroker_flow(
    hostname,
    username,
    password,
    pbrun_command,
    otp
):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        chan = client.invoke_shell()
        
        # Wait for initial prompt
        while not chan.recv_ready():
            time.sleep(0.5)
        chan.recv(1024)  # Clear buffer
        
        # Send pbrun command
        chan.send(f"{pbrun_command}\n")
        
        # Handle password prompt
        while True:
            resp = chan.recv(1024).decode()
            if "Password:" in resp:
                chan.send(f"{password}\n")
                break
            time.sleep(0.5)
        
        # Handle OTP prompt
        while True:
            resp = chan.recv(1024).decode()
            if "Security Code:" in resp:
                chan.send(f"{otp}\n")
                break
            time.sleep(0.5)
        
        # Get final output
        time.sleep(1)  # Wait for command execution
        output = chan.recv(65535).decode()
        return output
        
    finally:
        client.close()
