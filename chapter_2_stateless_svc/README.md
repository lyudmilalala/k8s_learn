## 2. Create a simple stateless service

### Busybox

`busybox` is an image implements a busy running shell script. It is useful in k8s development works where the contents of pods are not important, for example scaler.

It can be got by pulling image `busybox:1.36`.  

### Build a deployment and a service

A `deployment` is a cluster of duplicated pods.

We can create a `deployment` with the following script.

```yaml

apiVersion: v1
kind: Namespace
metadata:
  name: busybox-ns

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: busybox-deploy
  namespace: busybox-ns
  labels:
    app: busybox
spec:
  replicas: 2
  selector:
    matchLabels:
      app: busybox-app
  template:
    metadata:
      labels:
        app: busybox-app
    spec:
      containers:
      - name: busybox
        image: busybox:1.36
        imagePullPolicy: IfNotPresent
        command: ["/bin/sh", "-c", "while true; do echo 'hello in loop'; sleep 10;done"]
```

Then you can visit the `localhost:30050` to call the functions on pod port 5000.

### A simple Flask app

We can create a simple flask server for testing http api running in the scalable cluster. Later, we will add more api into the server.

The script of server

```python
from flask import Flask, request, jsonify
import os
import logging
import random

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
status = "AVAILABLE" # Global variable to hold the status

@app.route('/getRandomNum', methods=['GET'])
def getRandomNum():
    value = random.randint(1, 10)
    return str(value)

@app.route('/updateStatus', methods=['POST'])
def updateStatus():
    global status
    data = request.get_json()
    status = data['status']
    return jsonify({"status": 200, "msg": f"Update status to {status}", "pod_name": pod_name})

@app.route('/status', methods=['GET'])
def get_status():
    global status
    msg = f'status on pod {pod_name} = {status}'
    logging.info(msg)
    return jsonify({"status": 200, "msg": status, "pod_name": pod_name})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
```

Use the following Dockerfile to pack the flask server into a docker image

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD app.py /app

# Install any needed packages specified in requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir Flask==2.0.2

# Make port 5000 available to the world outside this container
EXPOSE 8080

# Run server.py when the container launches
CMD ["python", "app.py"]
```

Build the docker image by `docker build -t <image_name>:<image_tag>`, here we use `flask-test-img:1.0.0` as the image name and tag.

### Build a deployment and a service

A is how you expose the ports of pods in the `deployment` cluster to external users. 

We can create a `deployment` and a `service` of the Flask server with the following script.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: as-test-deploy
  namespace: as-test-ns
spec:
  replicas: 1
  selector:
    matchLabels:
      app: as-test-app
  template:
    metadata:
      labels:
        app: as-test-app
      annotations:
        controller.kubernetes.io/pod-deletion-cost: '1'
    spec:
      containers:
      - name: as-test-pod
        image: flask-test-img:1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
      
---
apiVersion: v1
kind: Service
metadata:
  name: as-test-svc
  namespace: as-test-ns
spec:
  type: NodePort
  ports:
  - port: 8080
    protocol: TCP
    nodePort: 30050
  selector:
    app: as-test-app
```

