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
        # Connect to host
        client.connect(hostname, username=username, password=password)
        chan = client.invoke_shell()

        # Wait for initial prompt
        output = ''
        while not chan.recv_ready():
            time.sleep(0.1)
        output += chan.recv(1024).decode()

        # Send pbrun command
        chan.send(f"{pbrun_command}\n")

        # Handle password prompt
        while True:
            if chan.recv_ready():
                output += chan.recv(1024).decode()
                if "Password:" in output:
                    chan.send(f"{password}\n")
                    break
            time.sleep(0.1)

        # Handle OTP prompt
        output = ''
        while True:
            if chan.recv_ready():
                output += chan.recv(1024).decode()
                if "Security Code:" in output:
                    chan.send(f"{otp}\n")
                    break
            time.sleep(0.1)

        # Get final output
        time.sleep(1)
        while chan.recv_ready():
            output += chan.recv(4096).decode()

        return output

    finally:
        client.close()
