from flask import Flask, request, jsonify
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
namespace = os.getenv('POD_NAMESPACE')
pod_name = os.getenv('POD_NAME')

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

    # Update status back to AVAILABLE once done
    return jsonify({"status": 200, "msg": ""})

@app.route('/livenessCheck', methods=['GET'])
def livenessCheck():
    return 'pod is healthy', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
