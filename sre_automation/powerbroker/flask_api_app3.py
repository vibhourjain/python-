from fastapi import FastAPI, Query
import subprocess

app = FastAPI()

@app.get("/run-pbrun")
def run_pbrun(
    user_id: str = Query(...),
    username: str = Query(...),
    service_account: str = Query(...),
    unix_group: str = Query(...)
):
    """
    Executes the pbrun command using provided parameters.
    """
    # Define hostname mapping
    d2 = {"k1": ('ug1', 'ug2'), "k2": ('ug3', 'ug4')}
    hostname = next((key for key, groups in d2.items() if unix_group in groups), "default_host")

    # Construct the pbrun command
    command = f"pbrun {unix_group} initbreakglass-{service_account} {user_id}"

    try:
        # Execute the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "success", "message": f"pbrun executed for {username} on {service_account}"}
        else:
            return {"status": "error", "message": result.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}
