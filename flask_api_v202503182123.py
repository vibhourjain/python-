from flask import Flask, request, render_template_string
# import utils_unix

app = Flask(__name__)

# Unix group and hostname mappings
unix_groups = {
    'pb1a': ['cosmos', 'opec'],
    'pb2a': ['sify'],
    'pb3a': ['jap', 'aus']
}

hostnames = {
    'pb1a': 'host1',
    'pb2a': 'host2',
    'pb3a': 'host3'
}


def get_unix_group(service_account):
    for group, accounts in unix_groups.items():
        if service_account in accounts:
            return group
    return None


def get_hostname(unix_group):
    return hostnames.get(unix_group, 'unknown_host')


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

    unix_group = get_unix_group(service_account)
    if not unix_group:
        return "Error: Invalid service account"

    hostname = get_hostname(unix_group)
    pbrun_command = f"pbrun {unix_group} initbreakglass-{service_account} {user_id}"
    print("pbrun_command:",pbrun_command)

    output, error = ("output","error")
    # output, error = utils_unix.run_powerbroker_command(
    #     hostname, username, password, pbrun_command, security_code
    # )

    return f"Output: {output}<br>Error: {error}" if error else f"Success! Output: {output}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)