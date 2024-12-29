from flask import Flask, request, json
from datetime import datetime
app = Flask(__name__)

import os
pod_name = os.getenv('POD_NAME')
app_name = os.getenv('APP_NAME')

def format_log_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

@app.route('/sum', methods=['POST'])
def sum():
    global status
    data = request.get_json()
    sum = int(data['a']) + int(data['b'])
    return json.dumps({"status": 200, "msg": f"[{app_name}-{pod_name}] sum = {sum}"})

@app.route('/livenessCheck', methods=['GET'])
def livenessCheck():
    return 'pod is healthy', 200

from concurrent.futures import ThreadPoolExecutor
import time

# readiness check sample

DEVICE_STATUS_BUSY = 'BUSY'
DEVICE_STATUS_IDLE = 'IDLE'
status = DEVICE_STATUS_IDLE # Global variable to hold the status
executor = ThreadPoolExecutor(max_workers=5)

def async_task(task_name, time_cost):
    global status
    print(f"[LOG {format_log_time()}] Start task = {task_name}")
    status = DEVICE_STATUS_BUSY
    time.sleep(time_cost)  
    status = DEVICE_STATUS_IDLE
    print(f"[LOG {format_log_time()}] End task = {task_name}")

@app.route('/run', methods=['POST'])
def runTask():
    global status
    data = request.get_json()
    task_name = data['name']
    time_cost = int(data['time_cost'])
    executor.submit(async_task, task_name, time_cost)
    queue_size = executor._work_queue.qsize()  
    return json.dumps({"status": 200, "msg": f"Pod {pod_name} starts processing task = {task_name}", "pod_name": pod_name, "current_queue_size": queue_size})

@app.route('/status', methods=['GET'])
def get_status():
    global status
    return json.dumps({"status": 200, "msg": status, "pod_name": pod_name})

@app.route('/readinessCheck', methods=['GET'])
def readinessCheck():
    if status == DEVICE_STATUS_BUSY:
        return 'pod is busy', 502
    else:
        return 'pod is idle', 200

# start up probe sample

import asyncio

keys = []

async def init_keys():
    for i in range(3):
        time.sleep(2) 
        keys.append(f'Key{i}')
        print(f"[LOG {format_log_time()}] Add Key{i}")

@app.route('/startCheck', methods=['GET'])
def startCheck():
    if len(keys) >= 3:
        return 'pod is healthy', 200
    else:
        return 'pod is healthy', 500

if __name__ == "__main__":
    asyncio.run(init_keys())
    app.run(host='0.0.0.0', port=8080, debug=True)