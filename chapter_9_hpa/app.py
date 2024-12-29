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

executor = ThreadPoolExecutor(max_workers=5)

def async_task(task_name, time_cost, mem_cost):
    print(f"[LOG {format_log_time()}] Start task = {task_name}, time_cost = {time_cost}, mem_cost = {mem_cost}")
    # Dummy variable to simulate memory usage
    dummy_mem = 'a' * (mem_cost * 1024 * 1024)
    time.sleep(time_cost)  
    print(f"[LOG {format_log_time()}] End task = {task_name}")

@app.route('/run', methods=['POST'])
def runTask():
    data = request.get_json()
    task_name = data['name']
    time_cost = int(data.get('time_cost', 1)) # in seconds
    mem_cost = int(data.get('mem_cost', 1)) # in MB
    executor.submit(async_task, task_name, time_cost, mem_cost)
    queue_size = executor._work_queue.qsize()  
    return json.dumps({"status": 200, "msg": f"Pod {pod_name} starts processing task = {task_name}", "pod_name": pod_name, "current_queue_size": queue_size})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)