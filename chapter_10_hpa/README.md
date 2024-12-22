## HPA

### Use k8s Metrics Server to see resource utilization

[Reference 1](https://github.com/nonai/k8s-example-files.git)

Apply the metrics server in the k8s cluster by `kubectl apply -f components.yaml`. It is downloaded from [Metrics Server Config](https://github.com/lyudmilalala/k8s_learn/blob/master/module11/components.yaml).

If you cannot download the image `cncamp/metrics-server` because of the GFW. You can work around by:

```shell
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/cncamp/metrics-server:v0.5.0
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/cncamp/metrics-server:v0.5.0  docker.io/cncamp/metrics-server:v0.5.0
```

Use `top` to see utilization

```
$ kubectl top pod -n async-simu-sm-ns
NAME                              CPU(cores)   MEMORY(bytes)   
as-test-deploy-57bfc86b65-6z8xg   1m           38Mi
as-test-deploy-57bfc86b65-lxthk   1m           38Mi
as-test-deploy-57bfc86b65-xv9mr   1m           38Mi
```

After a longer request (5s request is too short), can see the memory increases, then drops down after a while.

```
$ curl -X POST http://localhost:30050/compute -H "Content-Type: application/json" -d "{\"request_id\": \"1ds3hf\", \"mem_cost\": 2, \"t_cost\": 10}"
{
  "msg": "",
  "status": 200
}
$ kubectl top pod -n as-test-ns
NAME                              CPU(cores)   MEMORY(bytes)   
as-test-deploy-57bfc86b65-6z8xg   1m           38Mi
as-test-deploy-57bfc86b65-lxthk   1m           38Mi
as-test-deploy-57bfc86b65-xv9mr   1m           42Mi
```

### Use HPA to scale up and down

Apply config, notice the `apiVersion` of autoscaling

```
kubectl apply -f .\scaler.yml
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