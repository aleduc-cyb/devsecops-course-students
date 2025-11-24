import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Disable Flask default logging
log = logging.getLogger('werkzeug')
log.disabled = True

# Configure custom logging
logging.basicConfig(
    filename='api.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_request(endpoint, a, b, ip, status, result):
    logging.info(f"Endpoint: {endpoint}, Inputs: ({a}, {b}), IP: {ip}, HTTP Code: {status}, Result: {result}")

def safe_float(value):
    try:
        return float(value)
    except ValueError:
        return None

@app.route('/add')
def add():
    a = safe_float(request.args.get('a'))
    b = safe_float(request.args.get('b'))
    ip = request.remote_addr
    if a is None or b is None:
        log_request('add', request.args.get('a'), request.args.get('b'), ip, 500, 'Invalid input')
        return jsonify(error='Invalid input'), 500
    result = a + b
    log_request('add', a, b, ip, 200, result)
    return jsonify(result=result)

@app.route('/subtract')
def subtract():
    a = safe_float(request.args.get('a'))
    b = safe_float(request.args.get('b'))
    ip = request.remote_addr
    if a is None or b is None:
        log_request('subtract', request.args.get('a'), request.args.get('b'), ip, 500, 'Invalid input')
        return jsonify(error='Invalid input'), 500
    result = a - b
    log_request('subtract', a, b, ip, 200, result)
    return jsonify(result=result)

@app.route('/multiply')
def multiply():
    a = safe_float(request.args.get('a'))
    b = safe_float(request.args.get('b'))
    ip = request.remote_addr
    if a is None or b is None:
        log_request('multiply', request.args.get('a'), request.args.get('b'), ip, 500, 'Invalid input')
        return jsonify(error='Invalid input'), 500
    result = a * b
    log_request('multiply', a, b, ip, 200, result)
    return jsonify(result=result)

@app.route('/divide')
def divide():
    a = safe_float(request.args.get('a'))
    b = safe_float(request.args.get('b'))
    ip = request.remote_addr
    if a is None or b is None:
        log_request('divide', request.args.get('a'), request.args.get('b'), ip, 500, 'Invalid input')
        return jsonify(error='Invalid input'), 500
    if b == 0:
        log_request('divide', a, b, ip, 500, 'Division by zero')
        return jsonify(error='Division by zero'), 500
    result = a / b
    log_request('divide', a, b, ip, 200, result)
    return jsonify(result=result)

@app.errorhandler(404)
def not_found(e):
    ip = request.remote_addr
    logging.info(f"Endpoint: {request.path}, IP: {ip}, HTTP Code: 404, Result: Not Found")
    return jsonify(error='Endpoint not found'), 404

if __name__ == '__main__':
    app.run(debug=True)
