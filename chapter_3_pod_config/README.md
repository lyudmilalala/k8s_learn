## 3. Useful pod configurations

### 3.1 Environment variables

Set environment variables to a pod as below.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: as-test-pod
  namespace: as-test-ns
spec:
  containers:
  - name: as-test-pod
    image: crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:2.0.0
    imagePullPolicy: IfNotPresent
    env:
    - name: APP_NAME
      value: "Jerry-learning"
```

Pod information can be exposed to the functions in container by the following way.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: as-test-pod
  namespace: as-test-ns
spec:
  containers:
  - name: as-test-pod
    image: crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:2.0.0
    imagePullPolicy: IfNotPresent
    env:
      - name: NODE_NAME
        valueFrom:
          fieldRef:
            fieldPath: spec.nodeName
      - name: POD_NAME
        valueFrom:
          fieldRef:
            fieldPath: metadata.name
      - name: POD_NAMESPACE
        valueFrom:
          fieldRef:
            fieldPath: metadata.namespace
      - name: POD_IP
        valueFrom:
          fieldRef:
            fieldPath: status.podIP
```

Then in your code, you can get their value as below:

```python
pod_name = os.getenv('POD_NAME')
```

Update our flask http response by these environment variables.

```python
import os
pod_name = os.getenv('POD_NAME')
app_name = os.getenv('APP_NAME')

@app.route('/sum', methods=['POST'])
def sum():
    global status
    data = request.get_json()
    sum = int(data['a']) + int(data['b'])
    return json.dumps({"status": 200, "msg": f"[{app_name}-{pod_name}] sum = {sum}"})
```

And now we can distinguish the responser of each request. Rebuild the docker image and reapply the `deployment.yaml` file in k8s. You will get the following response at this time.

```shell
$ curl -X POST 'http://47.119.148.12:30050/sum' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "[Jerry-learning-flask-deploy-c4948b89f-6htc2] sum = 22", "status": 200}
```

### 3.2 Liveness, Readiness and Startup Probe

A liveness probe can determine whether a pod requires to be restarted.

A readiness probe is used to check whether a pod is ready to accept traffics. A service's ingress load balancer will not direct requests to pods that are not ready. Indeed, we can sometimes set pod to not ready on purpose when it is overwhelming.

A startup probes is used to check when a container application has started. If such a probe is configured, liveness and readiness probes do not start until it succeeds. It helps slow starting pods to avoid being killed during startup.

We can set up health check and readiness probe as a shell script or an api in the http server. 

Sample code for using shell command as a liveness probe. It use the file status of `/tmp/healthy`. After deleting the file, the pod will become unhealthy.

```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    test: liveness
  name: liveness-exec
spec:
  containers:
  - name: liveness
    image: registry.k8s.io/busybox
    imagePullPolicy: IfNotPresent
    args:
    - /bin/sh
    - -c
    - touch /tmp/healthy; sleep 30; rm -f /tmp/healthy; sleep 600
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/healthy
      initialDelaySeconds: 5
      periodSeconds: 5
      failureThreshold: 3
```

Sample code for using http api as a readiness probe.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: as-test-pod
  namespace: as-test-ns
spec:
  containers:
  - name: as-test-pod
    image: flask-test-img:1.0.0
    imagePullPolicy: IfNotPresent
    readinessProbe:
        httpGet:
          path: /readinessCheck
          port: 5000
        initialDelaySeconds: 5
        periodSeconds: 2
        failureThreshold: 3
```

To use this configure, you must already have an api in your server to determine readiness. For example, as the code below.

```python
@app.route('/readinessCheck', methods=['GET'])
def readinessCheck():
    if status == "BUSY":
        return 'pod is busy', 502
    else:
        return 'pod is available', 200
```

In subdirectory `3_2`, we update the flask server by adding a liveness check, a readiness check, and a start up probe check interface in it.

For the liveness check, simply check if the interface can be visited.

For the start probe check, we simulate an asynchronous application initialization process. It simulates the situation where we must load data from databases or file storages before starting the server. Only after all data are loaded, the start up probe returns true. In this case, the pods should turn to ready later than before, as it takes 6s to pass the start up probe.

For the readiness part, we simulate an asynchronous task execution process. We set the task running time cost by an input parameter. When a task is running, turn the pod to not ready to avoid extra task being sent to this pod.

After sending a task to the request, the pod received the task will be not ready very soon, and turn back to ready after a while, 20s in this case.

```shell
$ curl -X POST 'http://47.119.148.12:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task1","time_cost": 20}'
{"current_queue_size": 0, "msg": "Pod flask-deploy-7b69c565c-ckq6m starts processing task = task1", "pod_name": "flask-deploy-7b69c565c-ckq6m", "status": 200}
$ kubectl get pods -n flask-ns
NAME                           READY   STATUS    RESTARTS   AGE
flask-deploy-7b69c565c-5gm59   1/1     Running   0          83s
flask-deploy-7b69c565c-7ccbc   1/1     Running   0          52s
flask-deploy-7b69c565c-ckq6m   0/1     Running   0          68s
```

If you grab the status of the server running the task (you may try multiple times to approach it, as requests are forwarded to each pod by equal chance), you will see `BUSY` instead of `IDLE`.

```shell
$ curl 'http://47.119.148.12:30050/status' 
{"msg": "BUSY", "pod_name": "flask-deploy-84564c5dfc-tx5qq", "status": 200}
```

### 3.3 Deletion cost

We can use the annotation `controller.kubernetes.io/pod-deletion-cost` to manage the pod deletion order. Pod with lower deletion cost will be deleted first.

NOTICE: By default, a pod is not ready is always deleted before the ready pods, regardless of its pod deletion cost.

Create a replica set by applying the `deployment.yaml` file in `3_3` directory.

Update the `controller.kubernetes.io/pod-deletion-cost` for each pod to a different number.

```shell
$ kubectl annotate pod --overwrite -n busybox-ns busybox-deploy-1-7c7c67959c-9h76p controller.kubernetes.io/pod-deletion-cost=70
pod/busybox-deploy-1-7c7c67959c-9h76p annotated
$ kubectl annotate pod --overwrite -n busybox-ns busybox-deploy-1-7c7c67959c-sr26b controller.kubernetes.io/pod-deletion-cost=10
pod/busybox-deploy-1-7c7c67959c-sr26b annotated
$ kubectl annotate pod --overwrite -n busybox-ns busybox-deploy-1-7c7c67959c-tghmx controller.kubernetes.io/pod-deletion-cost=100
pod/busybox-deploy-1-7c7c67959c-tghmx annotated
$ kubectl annotate pod --overwrite -n busybox-ns busybox-deploy-1-7c7c67959c-tmwlx controller.kubernetes.io/pod-deletion-cost=50
pod/busybox-deploy-1-7c7c67959c-tmwlx annotated
```

Then if you `kubectl describe` the pod, it will show the latest`pod-deletion-cost` annotation.

```shell
$ kubectl describe pod busybox-ns busybox-deploy-1-7c7c67959c-9h76p -n busybox-ns
Name:                 busybox-deploy-1-7c7c67959c-9h76p
Namespace:            busybox-ns
Priority:             100000
Priority Class Name:  spinq-critical
Node:                 izwz9brbcf157u3s0rr0p0z/192.168.1.249
Start Time:           Fri, 19 Sep 2025 00:57:04 +0800
Labels:               app=busybox-app-1
                      pod-template-hash=7c7c67959c
Annotations:          cni.projectcalico.org/containerID: 85d5b272092a86dc3a0c5be59f590abeb58f2567dbd9108464612baf8ccaf2e2
                      cni.projectcalico.org/podIP: 172.16.220.123/32
                      cni.projectcalico.org/podIPs: 172.16.220.123/32
                      controller.kubernetes.io/pod-deletion-cost: 70
Status:               Running
......
```

Then we scale down the deployment one pod at a time. The pod with the lowest deletion cost will always be deleted first.

```shell
$ kubectl scale deployment busybox-deploy-1 --replicas=3 -n busybox-ns
deployment.apps/busybox-deploy-1 scaled
$ kubectl get pods -n busybox-ns
NAME                                READY   STATUS        RESTARTS   AGE
busybox-deploy-1-7c7c67959c-9h76p   1/1     Running       0          7m29s
busybox-deploy-1-7c7c67959c-sr26b   1/1     Terminating   0          7m29s
busybox-deploy-1-7c7c67959c-tghmx   1/1     Running       0          7m31s
busybox-deploy-1-7c7c67959c-tmwlx   1/1     Running       0          7m31s
$ kubectl scale deployment busybox-deploy-1 --replicas=2 -n busybox-ns
deployment.apps/busybox-deploy-1 scaled
$ kubectl get pods -n busybox-ns
NAME                                READY   STATUS        RESTARTS   AGE
busybox-deploy-1-7c7c67959c-9h76p   1/1     Running       0          8m14s
busybox-deploy-1-7c7c67959c-tghmx   1/1     Running       0          8m16s
busybox-deploy-1-7c7c67959c-tmwlx   1/1     Terminating   0          8m16s
$ kubectl scale deployment busybox-deploy-1 --replicas=1 -n busybox-ns
deployment.apps/busybox-deploy-1 scaled
$ kubectl get pods -n busybox-ns
NAME                                READY   STATUS        RESTARTS   AGE
busybox-deploy-1-7c7c67959c-9h76p   1/1     Terminating   0          8m35s
busybox-deploy-1-7c7c67959c-tghmx   1/1     Running       0          8m37s
```

### 3.4 Priority

We use `priority` to control the order and preemption behavior while pod scheduling. Higher priority pods can preempt (evict) lower priority pods when available resources is not enough during scheduling,

`Priority` does not guarantee the pods will be scheduled.

`Priority` does not influence the pod deletion order.