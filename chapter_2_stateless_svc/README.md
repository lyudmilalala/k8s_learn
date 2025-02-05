## 2. Create a simple stateless service

### Busybox

`busybox` is an image implements a busy running shell script. It is useful in k8s development works where the contents of pods are not important, for example scaler.

It can be got by pulling image `busybox:1.36`.  

### Build a deployment

A `deployment` is a cluster of duplicated pods.

We can create a `deployment` with the following script `busybox-deployment.yaml`.

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
        image: ubuntu:22.04
        imagePullPolicy: IfNotPresent
        command: ["/bin/bash", "-c", "while true; do echo 'hello in loop'; sleep 10;done"]
```

Then you can see a cluster of pods created in the k8s cluster.

### A simple Flask app

We can create a simple flask server for testing http api running in the scalable cluster. Later, we will add more api into the server.

The script of server is in `app.py`

```python
from flask import Flask, request, json
app = Flask(__name__)

@app.route('/sum', methods=['POST'])
def sum():
    global status
    data = request.get_json()
    sum = int(data['a']) + int(data['b'])
    return json.dumps({"status": 200, "msg": f"sum = {sum}"})

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
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir Flask==2.0.2 requests==2.26.0 Werkzeug==2.0.2

# Make port 5000 available to the world outside this container
EXPOSE 8080

# Run server.py when the container launches
CMD ["python", "app.py"]
```

Build the docker image by `docker build -t <image_name>:<image_tag> .`, here we use `crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:1.0.0` as the image name and tag (it is a image in the aliyun person image repository).

You can run a docker server at local for debugging by 

```shell
docker run -itd --name flask-app -p 18080:8080 crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:1.0.0
```

While the server is running, make a request as 

```shell
curl -X POST 'http://localhost:18080/sum' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 2}'
```

will give a result similar to `{"msg": "sum = 9", "status": 200}`.

Push your new docker image after ensuring everything is correct by

```shell
docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:1.0.0
```

### Build a deployment and a service

A is how you expose the ports of pods in the `deployment` cluster to external users. 

We can create a `deployment` and a `service` of the Flask server with the following script `flask-deployment.yaml`.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: flask-ns
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-deploy
  namespace: flask-ns
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
      - name: flask-pod
        image: crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: flask-svc
  namespace: flask-ns
spec:
  type: NodePort
  ports:
  - port: 8080
    protocol: TCP
    nodePort: 30050
  selector:
    app: flask-app
```

```shell
$ kubectl apply -f deployment.yaml
$ kubectl get pods -n flask-ns
NAME                            READY   STATUS    RESTARTS   AGE
flask-deploy-6f54b5cbff-7kq6j   1/1     Running   0          14s
flask-deploy-6f54b5cbff-v5wzb   1/1     Running   0          14s
flask-deploy-6f54b5cbff-xmglp   1/1     Running   0          14s
```

Make request to the ip address of your k8s master server (in our example, it is `47.119.148.12`) and the service port `30050`. It should be something similar to the following.

```shell
$ curl -X POST 'http://47.119.148.12:30050/sum' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "sum = 22", "status": 200}
```