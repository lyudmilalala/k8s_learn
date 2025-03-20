## Call an external service from inside the pod

Say now we have an API at `http://192.168.1.250:7333/demo`, which is implemented on a server in the same LAN as the K8s cluster, but outside the K8s cluster.

All servers in the LAN are approachable to each other, and we can successfully ping `192.168.1.250` as well as request by `curl http://192.168.1.250:7333/demo` from a K8s node server.

Enter a pod container in the K8s cluster, here we take a busybox based on `ubuntu:22.04` as an example. Enter the container terminal by:

kubectl exec -it busybox /bin/bash -n flask-ns

Then install `ping` and `curl` for test.

apt-get update
apt-get install -y curl inetutils-ping

Then ping `192.168.1.250` or curl `http://192.168.1.250:7333/demo`, and you may get stuck until timeout.

To solve this problem, create an `Endpoint`.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: out-svc
  namespace: flask-ns
spec:
  ports:
  - protocol: TCP
    port: 10000
    targetPort: 10000
 
---

apiVersion: v1     
kind: Endpoints
metadata:
 name: out-svc
 namespace: flask-ns
subsets:
- addresses:
  - ip: 192.168.9.112
  ports:
  - port: 10000
```

When call in pod, use `curl out-svc.flask-ns:7333/demo`