from flask import Flask, request, jsonify
import time
import os
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

pod_name = os.getenv('POD_NAME', '<unset>')  # get the pod name from environment variable    

@app.route('/compute', methods=['POST'])
def compute():
    data = request.get_json()
    request_id = data.get('request_id')
    mem_cost = int(data.get('mem_cost')) # in MB
    t_cost = float(data.get('t_cost'))   # in seconds
    logging.info(f'Received compute request with request_id = {request_id}, mem_cost = {mem_cost}, t_cost = {t_cost} on pod {pod_name}')

    # Dummy variable to simulate memory usage
    dummy_mem = 'a' * (mem_cost * 1024 * 1024)
    
    # Sleep to simulate CPU time cost
    time.sleep(t_cost)
    return jsonify({"status": 200, "msg": ""})

@app.route('/status', methods=['GET'])
def get_status():
    global status
    logging.info(f'status on pod {pod_name} = {status}')
    return jsonify({"status": 200, "msg": status})

@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": 200, "msg": ''})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)