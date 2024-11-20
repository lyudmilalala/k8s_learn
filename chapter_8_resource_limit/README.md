## 7. Resource Limit

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
    resources:
      requests:
        cpu: "100m"
        memory: "100Mi"
      limits:
        cpu: "100m"
        memory: "200Mi"
```

Here the `requests.cpu` is the minimum cpu required for starting the pod successfully. `limits.cpu` is the maximum cpu this pod can occupied during executing.

You can also set the maximum cpu and memory allowed by a namespace as below, to avoid the service in a single workspace to occupy all resources. 

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: as-rq
  namespace: as-test-ns
spec:
  hard:
    pods: "10"
    requests.cpu: "1"
    requests.memory: "500Mi"
    limits.cpu: "1"
    limits.memory: "500Mi"
```

P.S. If `limit` in `ResourceQuota`，then the `limit` configurations in the pod config file mush be filled.

We can test the update of workspace resource limit by continuously creating pods with resource `requests`, as shown below.

```shell
$ kubectl apply -f .\podConfig.yml
pod/nginx-pod-1 created
$ kubectl apply -f .\podConfig.yml
pod/nginx-pod-2 created
$ kubectl apply -f .\podConfig.yml
Error from server (Forbidden): error when creating ".\\podConfig.yml": pods "nginx-pod-3" is forbidden: exceeded quota: test-rq, requested: limits.memory=200Mi,requests.memory=200Mi, used: limits.memory=400Mi,requests.memory=400Mi, limited: limits.memory=500Mi,requests.memory=500Mi
```

We can update the `ResourceQuota` of a namespace with the following command.

```shell
$ kubectl patch resourcequota as-rq -n as-test-ns --type='json' -p="[{'op': 'replace', 'path': '/spec/hard/requests.memory', 'value': '300Mi'}]"
resourcequota/test-rq patched
```

Update `ResourceQuota` will not scale down the pods that already exist. It is only used in the validation for new pod creation.