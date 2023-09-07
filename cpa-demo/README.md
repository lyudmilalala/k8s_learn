### Test Flask server

In the `/scaler` folder, run `python app.py`

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
docker build . -t lyudmilalala/cpa-app-img:1.0.0 
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

Create deployment and service

```
$ kubectl apply -f .\deployment.yml
deployment.apps/as-test-deploy unchanged
service/as-test-svc created
$ curl -X POST http://localhost:30050/compute -H "Content-Type: application/json" -d "{\"request_id\": \"1ds3hf\", \"mem_cost\": 2, \"t_cost\": 5}"
{
  "msg": "",
  "status": 200
}
```

### Add CPA

In the `/scaler` folder, build CPA scaler image by the following line.

```
docker build . -t lyudmilalala/cpa-scaler-img:1.0.0
```

Start the autoscaler

```
kubectl apply -f .\cpa.yaml 
```

Everything starts up, and after a few seconds, number of pods in `as-test-deploy` will change from 2 to 4.

```
$ kubectl get pods -n default   
NAME                                              READY   STATUS    RESTARTS   AGE
as-test-deploy-fd54c9d6f-9z9qv                    1/1     Running   0          98m
as-test-deploy-fd54c9d6f-g9fkk                    1/1     Running   0          98m
as-test-deploy-fd54c9d6f-jd2zl                    1/1     Running   0          17m
as-test-deploy-fd54c9d6f-rbshc                    1/1     Running   0          17m
cpa-demo                                          1/1     Running   0          2m40s
custom-pod-autoscaler-operator-64b79f9b57-qnr56   1/1     Running   0          81m
```