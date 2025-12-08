# Simple Flask app with a couple of insecure patterns to trigger Semgrep
from flask import Flask, request
import subprocess, os

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_command():
    # insecure: using shell=True with user input (Semgrep will flag)
    cmd = request.form.get('cmd', 'echo hello')
    subprocess.check_output(cmd, shell=True)
    return 'ran', 200

@app.route('/format', methods=['POST'])
def insecure_format():
    # insecure use of eval (Semgrep will flag this pattern)
    data = request.form.get('data', '1+1')
    res = eval(data)
    return str(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
