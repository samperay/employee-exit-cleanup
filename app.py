#!/usr/bin/env python3

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
from pathlib import Path
import os

app = Flask(__name__)

# Set the (relative) path to the scripts directory
# so we can easily use a different one.
SCRIPTS_DIR = 'scripts'

auth = HTTPBasicAuth()

users = {
    "hr": generate_password_hash("secretpassword"),
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False



@app.route('/offboard', methods=['POST'])
@auth.login_required

def offboard():
    employee_email = request.json.get('employeeEmail')
    print("Running offboarding for employee {} ...".format(employee_email))

    statuses = {}

    for script in os.listdir(SCRIPTS_DIR):
        # The pathlib.Path object is a really elegant way to construct paths
        # in a way that works cross-platform (IMO!)
        path = Path(SCRIPTS_DIR) / script
        print('  Running {}'.format(path))

        # This is where we call out to the script and store the exit code.
        statuses[script] = subprocess.run([str(path), employee_email]).returncode

    return statuses


if __name__ == "__main__":
    # Running the Flask server in threaded mode allows multiple
    # users to connect at once. For a consumer-facing app,
    # we would not use the Flask development server, but we expect low traffic!
    app.run(threaded=True)
