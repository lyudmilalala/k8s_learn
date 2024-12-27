## 8. Resource Limit

### 8.1 Pod Resource Limit

The CPU and memory required by a pod can be set in `flask-pod.yaml` file as:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: flask-pod
  namespace: flask-ns
  labels:
    app: flask-app
spec:
  containers:
  - name: flask-pod
    image: crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:3.0.0
    imagePullPolicy: IfNotPresent
    ports:
    - name: liveness-port
      containerPort: 8080
    resources:
      requests:
        cpu: "100m"
        memory: "10Mi"
      limits:
        cpu: "1000m"
        memory: "100Mi"
```

Here the `requests.cpu` is the minimum cpu required for starting the pod successfully. `limits.cpu` is the maximum cpu this pod can occupied during executing. `1000m` means 1000 millicore, which euqals to 1 cpu core.

Similary, `requests.memory` is the minimum memory required for starting the pod successfully. `limits.memory` is the maximum memory this pod can occupied during executing, in bytes. Thus `100Mi` is 100MB.

To test the resource limit configuration, we modify the `app.py` script to let our tasks to occupy a specific amount of memory. Then test, build, and deploy the service as we have done before.

```shell
$ docker build -t crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:3.0.0 .
$ docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:3.0.0
$ kubectl apply -f flask-pod.yaml
```

First test some requests that qualify our limit. Output will be similar to the following:

```shell
$ curl -X POST 'http://112.74.60.37:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task1", "time_cost": 1,"mem_cost": 2}'
{"current_queue_size": 0, "msg": "Pod flask-pod starts processing task = task1", "pod_name": "flask-pod", "status": 200}
$ curl -X POST 'http://112.74.60.37:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task2", "time_cost": 1,"mem_cost": 2}'
{"current_queue_size": 1, "msg": "Pod flask-pod starts processing task = task2", "pod_name": "flask-pod", "status": 200}
```

Add python date log

```
def format_log_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
```

And if you check logs of the pod, you will see something like this:

```shell
Start task = task1, time_cost = 1, mem_cost = 2
172.16.167.128 - - [27/Dec/2024 09:39:11] "POST /run HTTP/1.1" 200 -
End task = task1
172.16.167.128 - - [27/Dec/2024 09:39:21] "POST /run HTTP/1.1" 200 -
Start task = task2, time_cost = 1, mem_cost = 2
End task = task2
```

Then send a request with `mem_cost` higher than the memory limits. You will see the pod be killed because of `OOMKilled`, then quickly be restarted.

```shell
$ kubectl get pods -n flask-ns
NAME        READY   STATUS    RESTARTS   AGE
flask-pod   1/1     Running   0          9m57s
$ curl -X POST 'http://112.74.60.37:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task1", "time_cost": 1,"mem_cost": 110}'
$ kubectl get pods -n flask-ns
NAME        READY   STATUS      RESTARTS   AGE
flask-pod   0/1     OOMKilled   0          10m
$ kubectl get pods -n flask-ns
NAME        READY   STATUS    RESTARTS     AGE
flask-pod   1/1     Running   1 (4s ago)   10m
```

### 8.2 Namespace Resource Limit

You can also set the maximum cpu and memory allowed by a namespace in a `flask-rq.yaml` as below, to avoid the service in a single workspace to occupy all resources. 

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
    requests.memory: "100Mi"
    limits.cpu: "3"
    limits.memory: "300Mi"
```

P.S. If `limit` in `ResourceQuota`，then the `limit` configurations in the pod config file must be filled.

We can test the update of workspace resource limit by continuously creating pods with resource `requests`, as shown below.

`flask-pod-2.yaml`, `flask-pod-3.yaml`, and `flask-pod-4.yaml` are configure files similar to `flask-pod.yaml`, with only the `kind: Pod` part, and being only different in `metadata.name` and `containers.name`. Here we only display `flask-pod-2.yaml` as an example. Change the `metadata.name` and `containers.name` in the file can convert it to  `flask-pod-N.yaml`.

```shell
$ kubectl apply -f flask-rq.yaml 
resourcequota/flask-rq created
$ kubectl apply -f flask-pod-2.yaml 
pod/flask-pod-2 created
$ kubectl apply -f flask-pod-3.yaml 
pod/flask-pod-3 created
$ kubectl apply -f flask-pod-4.yaml 
Error from server (Forbidden): error when creating "flask-pod-4.yaml": pods "flask-pod-4" is forbidden: exceeded quota: flask-rq, requested: limits.cpu=1,limits.memory=100Mi, used: limits.cpu=3,limits.memory=300Mi, limited: limits.cpu=3,limits.memory=300Mi
$ kubectl get pods -n flask-ns
NAME          READY   STATUS    RESTARTS      AGE
flask-pod     1/1     Running   1 (18m ago)   28m
flask-pod-2   1/1     Running   0             4m49s
flask-pod-3   1/1     Running   0             117s
```

We can update the `ResourceQuota` of a namespace with the following command.

```shell
$ kubectl patch resourcequota flask-rq -n flask-ns --type='json' -p="[{'op': 'replace', 'path': '/spec/hard/requests.memory', 'value': '300Mi'}]"
resourcequota/test-rq patched
```

Update `ResourceQuota` will not scale down the pods that already exist. It is only used in the validation for new pod creation.
