from flask import Flask, request, jsonify
import os
import logging
import random
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)

DEVICE_STATUS_BUSY = 'BUSY'
DEVICE_STATUS_IDLE = 'IDLE'
executor = ThreadPoolExecutor(max_workers=5)
# Set up logging
logging.basicConfig(level=logging.INFO)

status = DEVICE_STATUS_IDLE # Global variable to hold the status
namespace = os.getenv('POD_NAMESPACE')
pod_name = os.getenv('POD_NAME')

def async_task(task_name, time_cost):
    logging.info(f"Start task = {task_name}")
    time.sleep(time_cost)  
    logging.info(f"End task = {task_name}")

@app.route('/getRandomNum', methods=['GET'])
def getRandomNum():
    value = random.randint(1, 10)
    return str(value)

@app.route('/processTask', methods=['POST'])
def updateStatus():
    global status
    data = request.get_json()
    task_name = data['name']
    time_cost = int(data['time_cost'])
    executor.submit(async_task, task_name, time_cost)
    queue_size = executor._work_queue.qsize()  
    return jsonify({"status": 200, "msg": f"Pod {pod_name} starts processing task = {task_name}", "pod_name": pod_name, "current_queue_size": queue_size})

@app.route('/readinessCheck', methods=['GET'])
def readinessCheck():
    if status == DEVICE_STATUS_BUSY:
        return 'pod is busy', 502
    else:
        return 'pod is idle', 200

@app.route('/livenessCheck', methods=['GET'])
def livenessCheck():
    return 'pod is healthy', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
