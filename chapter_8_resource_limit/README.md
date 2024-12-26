## 7. Resource Limit

### 7.1 Pod Resource Limit

The CPU and memory required by a pod can be set in `flask-pod.yaml` file as:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-deploy
  namespace: flask-ns
spec:
  replicas: 1
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
        image: crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:3.0.0
        resources:
          requests:
            cpu: "10m"
            memory: "10Mi"
          limits:
            cpu: "100m"
            memory: "20Mi"
```

Here the `requests.cpu` is the minimum cpu required for starting the pod successfully. `limits.cpu` is the maximum cpu this pod can occupied during executing.

To test the resource limit configuration, we modify the `app.py` script to let our tasks to occupy a specific amount of memory. Then test, build, and deploy the service as we have done before.

```shell
$ docker build -t crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:3.0.0 .
$ docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:3.0.0
$ kubectl apply -f flask-pod.yaml
```

First test some requests that qualify our limit. Output will be similar to the following:

```shell
$ curl -X POST 'http://112.74.60.37:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task1", "time_cost": 1,"mem_cost": 2}'
{"current_queue_size": 0, "msg": "Pod dummy_pod starts processing task = task1", "pod_name": "dummy_pod", "status": 200}
$ curl -X POST 'http://112.74.60.37:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task2", "time_cost": 1,"mem_cost": 2}'
{"current_queue_size": 0, "msg": "Pod dummy_pod starts processing task = task1", "pod_name": "dummy_pod", "status": 200}
```

And if you check logs of the pod, you will see something like this:

```shell
192.168.65.1 - - [26/Dec/2024 23:35:11] "POST /sum HTTP/1.1" 200 -
Start task = task1, time_cost = 1, mem_cost = 2
192.168.65.1 - - [26/Dec/2024 23:37:19] "POST /run HTTP/1.1" 200 -
End task = task1
192.168.65.1 - - [26/Dec/2024 23:37:32] "POST /run HTTP/1.1" 200 -
Start task = task2, time_cost = 1, mem_cost = 2
End task = task2
```

Then send a request with `mem_cost` higher than the memory limits.

```shell
curl -X POST 'http://47.119.132.211:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task1","time_cost": 20,"memo_cost": 30}'
```

### 7.2 Namespace Resource Limit

You can also set the maximum cpu and memory allowed by a namespace as below, to avoid the service in a single workspace to occupy all resources. 

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: flask-rq
  namespace: flask-ns
spec:
  hard:
    pods: "10"
    requests.cpu: "1"
    requests.memory: "500Mi"
    limits.cpu: "1"
    limits.memory: "500Mi"
```

P.S. If `limit` in `ResourceQuota`，then the `limit` configurations in the pod config file must be filled.

We can test the update of workspace resource limit by continuously creating pods with resource `requests`, as shown below.

```shell
$ kubectl apply -f .\podConfig.yaml
pod/nginx-pod-1 created
$ kubectl apply -f .\podConfig.yaml
pod/nginx-pod-2 created
$ kubectl apply -f .\podConfig.yaml
Error from server (Forbidden): error when creating ".\\podConfig.yml": pods "nginx-pod-3" is forbidden: exceeded quota: test-rq, requested: limits.memory=200Mi,requests.memory=200Mi, used: limits.memory=400Mi,requests.memory=400Mi, limited: limits.memory=500Mi,requests.memory=500Mi
```

We can update the `ResourceQuota` of a namespace with the following command.

```shell
$ kubectl patch resourcequota flask-rq -n flask-ns --type='json' -p="[{'op': 'replace', 'path': '/spec/hard/requests.memory', 'value': '300Mi'}]"
resourcequota/test-rq patched
```

Update `ResourceQuota` will not scale down the pods that already exist. It is only used in the validation for new pod creation.