from flask import Flask, request, render_template_string
# import utils_unix
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Unix group and hostname mappings
d_host_unix_role = {
    'pb1a': ['cosmos', 'opec'],
    'pb2a': ['sify'],
    'pb3a': ['jap', 'aus']
}

d_role_hostname = {
    'host1': ('pb1a','pb2a')
    'host2': 'pb3a'
}


def get_key_from_value(dict1, field):
    for key1, value1 in dict1.items():
        if field in value1:
            return key1
    return None


@app.route('/initiate_pbrun', methods=['GET'])
def initiate_pbrun():
    service_account = request.args.get('service_account')
    user_id = request.args.get('user_id')

    form_html = f'''
    <form action="/execute_pbrun" method="post">
        <input type="hidden" name="service_account" value="{service_account}">
        <input type="hidden" name="user_id" value="{user_id}">
        Username: <input type="text" name="username" required><br>
        Password: <input type="password" name="password" required><br>
        Security Code: <input type="text" name="security_code" required><br>
        <input type="submit" value="Execute">
    </form>
    '''
    return render_template_string(form_html)


@app.route('/execute_pbrun', methods=['POST'])
def execute_pbrun():
    service_account = request.form['service_account']
    user_id = request.form['user_id']
    username = request.form['username']
    password = request.form['password']
    security_code = request.form['security_code']
    user_id=user_id[:7]
    unix_group = get_key_from_value(d_host_unix_role,service_account)

    logging.info(f"Value retrieved for service_account:{service_account}")

    if not unix_group:
        return "Error: Invalid service account"
    else:
        hostname = get_key_from_value(d_role_hostname,unix_group)

    hostname = get_hostname(unix_group)
    pbrun_command = f"pbrun {unix_group} initbreakglass-{service_account} {user_id}"
    logging.info(f"Value retrieved for hostname:{hostname};username:{username};security_code:{security_code};
    pbrun_command:{pbrun_command}")

    output, error = ("output","error")
    # output, error = utils_unix.run_powerbroker_command(
    #     hostname, username, password, pbrun_command, security_code
    # )

    if error:
        return f"Output: {output} <br>Error: {error}"
    else:
        return f"Success! Output: {output}"

    return f"Output: {output}<br>Error: {error}" if error else f"Success! Output: {output}"

@app.route('/health')
def health_check():
    return "Welcome ! API for Power Broker is running and healthy !", 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
