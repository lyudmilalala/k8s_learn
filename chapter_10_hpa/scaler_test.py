import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time, json

url = 'http://47.106.149.128:30050/run'

# send a single request
def send_post_request(task_id):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"name": f"task{task_id}", "time_cost": 2, "mem_cost": 20})
    response = requests.post(url, headers=headers, data=data)
    return response.status_code

# send concurrent requests
def concurrent_requests(max_workers, duration):
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task_id = {executor.submit(send_post_request, i): i for i in range(1, max_workers + 1)}

        while time.time() - start_time < duration + 10:
            for future in as_completed(future_to_task_id, timeout=1):
                task_id = future_to_task_id[future]
                try:
                    result = future.result()
                    print(f"Task {task_id} completed with status code: {result}")
                except Exception as exc:
                    print(f"Task {task_id} generated an exception: {exc}")
                finally:
                    # delete a completed task
                    del future_to_task_id[future]
                    # submit a new task
                    if time.time() - start_time < duration:
                        new_task_id = task_id + max_workers
                        future_to_task_id[executor.submit(send_post_request, new_task_id)] = new_task_id

if __name__ == "__main__":
    max_workers = 10  # max concurrent thread number
    duration = 50  # keep running time lengths
    concurrent_requests(max_workers, duration)