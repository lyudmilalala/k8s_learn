## HPA

### Use k8s Metrics Server to see resource utilization

[Reference 1](https://github.com/nonai/k8s-example-files.git)

Apply the metrics server in the k8s cluster by `kubectl apply -f metrics_server/components.yaml`. It is downloaded from [Metrics Server Config](https://github.com/lyudmilalala/k8s_learn/blob/master/module11/components.yaml).

If you cannot download the image `cncamp/metrics-server` because of the GFW. You can work around by:

```shell
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/cncamp/metrics-server:v0.5.0
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/cncamp/metrics-server:v0.5.0  docker.io/cncamp/metrics-server:v0.5.0
```

The successful deployment of the metrics server should give a pod like the following.

```shell
$ kubectl get pods -A | grep "metrics"
kube-system     metrics-server-76857dbb45-d7bdg           1/1     Running            0    6h
```

Deploy a `flask-app:4.0.0` replica set. Notice this image version remove the `readinessProbe` rely on a status variable. A flask server can handle multiple requests concurrently.

```shell
$ kubectl apply -f flask-deployment.yaml 
namespace/flask-ns unchanged
deployment.apps/flask-deploy created
service/flask-svc created
```

Then use `top` to check its resource utilization

```shell
$ kubectl top pod -n flask-ns
NAME                            CPU(cores)   MEMORY(bytes)   
flask-deploy-7f5c54ccf6-89cjn   6m           42Mi            
flask-deploy-7f5c54ccf6-lgxkt   6m           41Mi            
flask-deploy-7f5c54ccf6-tv8hs   6m           41Mi
```

After a longer request (5s request is too short), can see the memory increases, then drops down after a while.

```shell
$ curl -X POST 'http://47.106.149.128:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task1", "time_cost": 10,"mem_cost": 50}'
{"current_queue_size": 1, "msg": "Pod flask-deploy-7f5c54ccf6-tv8hs starts processing task = task1", "pod_name": "flask-deploy-7f5c54ccf6-tv8hs", "status": 200}
$ kubectl top pod -n flask-ns
NAME                            CPU(cores)   MEMORY(bytes)   
flask-deploy-7f5c54ccf6-89cjn   6m           42Mi            
flask-deploy-7f5c54ccf6-lgxkt   6m           41Mi            
flask-deploy-7f5c54ccf6-tv8hs   8m           91Mi
```

### Use HPA to scale up and down

Apply the scaler config, notice the `apiVersion` of autoscaling

```
kubectl apply -f scaler.yaml
```

Use JMeter to request multiple times concurrently. Check the pod list can see more items than before.

```
$ kubectl top pod -n as-test-ns
NAME                              CPU(cores)   MEMORY(bytes)   
as-test-deploy-57bfc86b65-6z8xg   1m           38Mi
as-test-deploy-57bfc86b65-99h44   1m           38Mi
as-test-deploy-57bfc86b65-hz6wh   1m           38Mi
as-test-deploy-57bfc86b65-lxthk   1m           38Mi
as-test-deploy-57bfc86b65-q964m   1m           38Mi
as-test-deploy-57bfc86b65-qs4lp   1`m           38Mi
as-test-deploy-57bfc86b65-rj7zc   1m           40Mi
as-test-deploy-57bfc86b65-tpbg9   1m           38Mi
as-test-deploy-57bfc86b65-xv9mr   1m           40Mi
as-test-deploy-57bfc86b65-zkjxx   1m           38Mi
```

We can use `controller.kubernetes.io/pod-deletion-cost` control the order of pod deletion. However, the official team suggests a more [suitable approach](https://github.com/kubernetes/kubernetes/issues/107598).
