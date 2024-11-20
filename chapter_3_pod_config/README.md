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
    image: flask-test-img:1.0.0
    imagePullPolicy: IfNotPresent
    env:
    - name: DEMO_GREETING
      value: "Hello from the environment"
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
    image: flask-test-img:1.0.0
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

Then in code, you can get their value as below:

```python
namespace = os.getenv('POD_NAMESPACE')
pod_name = os.getenv('POD_NAME')
```

### 3.2 Resource Limit

The CPU and memory required by a pod can be set in its config file as:

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
    resources:
      requests:
        cpu: "100m"
        memory: "100Mi"
      limits:
        cpu: "100m"
        memory: "200Mi"
```

### 3.3 Liveness, Readiness and Startup Probe

A liveness probe can determine whether a pod requires to be restarted.

A readiness probe is used to check whether a pod is ready to accept traffics. A service's ingress load balancer will not direct requests to pods that are not ready. Indeed, we can sometimes set pod to not ready on purpose when it is overwhelming.

A startup probes is used to check when a container application has started. If such a probe is configured, liveness and readiness probes do not start until it succeeds. It helps slow starting pods to avoid being killed during startup.

We can set up health check and readiness probe as a shell script or an api in the http server. 

Sample code for using shell command as a liveness probe. It use the file status of `/tmp/healthy`

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

### 3.4 Deletion cost

A deployment annotation. Pod with lower deletion cost will be deleted first.

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
```

NOTICE: By default, a pod is not ready is always deleted before the ready pods, regardless of its pod deletion cost.

### 3.5 Priority