### Test Flask server

```
curl -X POST http://localhost:5000/compute -H 'Content-Type: application/json' -d '{"request_id": "1ds3hf", "mem_cost": 2, "t_cost": 5}'
```

If Windows, use

```
curl -X POST http://localhost:5000/compute -H "Content-Type: application/json" -d "{\"request_id\": \"1ds3hf\", \"mem_cost\": 2, \"t_cost\": 5}"
```

### Test Docker image

Build docker image

```
docker build . -t lyudmilalala/as-test-img:1.0.0
```

Start docker container

```
$ docker run -itd --name as-test -p 5090:5000 lyudmilalala/as-test-img:1.0.0
b6877fa028c665cc99536eee1c42fe4c1ae6741834867a2c1c7ee3cba40f8fd1
$ curl -X POST http://localhost:5090/compute -H "Content-Type: application/json" -d "{\"request_id\": \"1ds3hf\", \"mem_cost\": 2, \"t_cost\": 5}"
{
  "msg": "",
  "status": 200
}
```

### Test k8s cluster

应用deployment和service

```
$ kubectl create namespace as-test-ns
namespace/as-test-ns created
$ kubectl apply -f .\deployment.yml
deployment.apps/as-test-deploy unchanged
service/as-test-svc created
$ curl -X POST http://localhost:30050/compute -H "Content-Type: application/json" -d "{\"request_id\": \"1ds3hf\", \"mem_cost\": 2, \"t_cost\": 5}"
{
  "msg": "",
  "status": 200
}
```

### Use k8s Metrics Server to see resource utilization

Download [Metrics Server Config](https://github.com/lyudmilalala/k8s_learn/blob/master/module11/components.yaml) and `kubectl apply -f components.yaml`

Use `top` to see utilization

```
$ kubectl top pod -n as-test-ns
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
as-test-deploy-57bfc86b65-qs4lp   1m           38Mi
as-test-deploy-57bfc86b65-rj7zc   1m           40Mi
as-test-deploy-57bfc86b65-tpbg9   1m           38Mi
as-test-deploy-57bfc86b65-xv9mr   1m           40Mi
as-test-deploy-57bfc86b65-zkjxx   1m           38Mi
```