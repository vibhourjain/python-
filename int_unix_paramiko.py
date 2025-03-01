import paramiko
import time
import re

def run_pbrun(
    hostname,
    username,
    password,
    pbrun_command,
    pb_password,
    security_code,
    timeout=10
):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to host
        client.connect(
            hostname,
            username=username,
            password=password,
            timeout=timeout
        )
        
        # Create an interactive shell with PTY
        chan = client.invoke_shell(width=200, height=50)
        chan.settimeout(timeout)

        # Send pbrun command
        chan.send(f"{pbrun_command}\n")
        
        output = ''
        stage = 0  # 0=waiting for password, 1=waiting for security code, 2=done
        
        while not chan.exit_status_ready():
            if chan.recv_ready():
                chunk = chan.recv(4096).decode('utf-8', 'ignore')
                output += chunk
                
                # Debug logging
                print("RECEIVED:", chunk)
                
                # Detect password prompt
                if stage == 0 and re.search(r'[Pp]assword:\s*$', output):
                    chan.send(f"{pb_password}\n")
                    output = ''
                    stage = 1
                    print("SENT PASSWORD")
                    continue
                    
                # Detect security code prompt
                if stage == 1 and re.search(r'Security [Cc]ode:\s*$', output):
                    chan.send(f"{security_code}\n")
                    output = ''
                    stage = 2
                    print("SENT SECURITY CODE")
                    continue
                    
            # Exit condition
            if stage == 2 and not chan.recv_ready():
                time.sleep(1)  # Wait for final output
                break
                
        # Get remaining output
        while chan.recv_ready():
            output += chan.recv(4096).decode('utf-8', 'ignore')

        return output

    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        client.close()

# Usage example
result = run_pbrun(
    hostname="your-server.com",
    username="your_username",
    password="your_ssh_password",
    pbrun_command="pbrun /bin/bash",  # Your actual pbrun command
    pb_password="powerbroker_password",
    security_code="123456"
)

print("Final output:", result)
