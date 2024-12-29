## HPA

### Use k8s Metrics Server to see resource utilization

[Reference 1](https://github.com/nonai/k8s-example-files.git)

Apply the metrics server in the k8s cluster by `kubectl apply -f metrics_server/components.yaml`. It is downloaded from [Metrics Server Config](https://github.com/lyudmilalala/k8s_learn/blob/master/module11/components.yaml).

If you cannot download the image `cncamp/metrics-server` because of the GFW. You can work around by:

```shell
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/cncamp/metrics-server:v0.5.0
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/cncamp/metrics-server:v0.5.0  docker.io/cncamp/metrics-server:v0.5.0
```

The default interval at which the metrics server periodically collects performance metrics is 30s, which is too long for triggering our scaler to handle a rapid increase in requests on time. Therefore, we need to adjust the `--metric-resolution` in the `components.yaml` to collect metric information more frequently.

The successful deployment of the metrics server should give a pod like the following.

```shell
$ kubectl get pods -A | grep "metrics"
kube-system     metrics-server-76857dbb45-d7bdg           1/1     Running            0    6h
```

Create a `flask-app:4.0.0` container image. This image version remove the `readinessProbe` rely on a status variable. A flask server can now handle multiple requests concurrently. Test, build, and deploy the service as we have done before.

```shell
$ docker build -t crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:4.0.0 .
$ docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:4.0.0
$ kubectl apply -f flask-deployment.yaml 
```

Then use `top` to check its resource utilization

```shell
$ kubectl top pod -n flask-ns
NAME                            CPU(cores)   MEMORY(bytes)   
flask-deploy-669dd4776f-66d4r   4m           39Mi            
flask-deploy-669dd4776f-9f9n5   4m           39Mi            
flask-deploy-669dd4776f-qjmkx   4m           39Mi      
```

After a longer request (5s request is too short), can see the memory increases, then drops down after a while.

```shell
$ curl -X POST 'http://47.106.149.128:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task1", "time_cost": 10,"mem_cost": 50}'
{"current_queue_size": 0, "msg": "Pod flask-deploy-669dd4776f-qjmkx starts processing task = task1", "pod_name": "flask-deploy-669dd4776f-qjmkx", "status": 200}
$ kubectl top pod -n flask-ns
NAME                            CPU(cores)   MEMORY(bytes)   
flask-deploy-669dd4776f-66d4r   4m           39Mi            
flask-deploy-669dd4776f-9f9n5   4m           39Mi            
flask-deploy-669dd4776f-qjmkx   4m           89Mi      
```

### Use HPA to scale up and down

Apply the scaler config, notice the `apiVersion` of autoscaling

```shell
$ kubectl apply -f scaler.yaml
horizontalpodautoscaler.autoscaling/flask-hpa created
```

In the config, `spec.behavior.scaleUp` defines the condition to satisfy for scale up. If the replica set satisfy the `spec.metrics` for at least a period equals to `stabilizationWindowSeconds`, it will scale up. 

`spec.behavior.scaleDown` defines the scale down manner of a replica set in its `policies` section, which is not existed in the `spec.behavior.scaleUp` configuration. If `type` equals `Pods`, it will decrease a specific number of pods in a time window with length equals `periodSeconds`. If `type` equals `Percent`, it will decrease a specific ratio of current alive pods in a time window with length equals `periodSeconds`.

Use python script `scaler_test.py` to send multiple requests concurrently. 

Check the pod list, and you can see new pods are created.

```shell
$ kubectl top pod -n flask-ns
NAME                            CPU(cores)   MEMORY(bytes)   
flask-deploy-669dd4776f-2c78h   22m          140Mi           
flask-deploy-669dd4776f-66d4r   19m          141Mi           
flask-deploy-669dd4776f-77trm   20m          140Mi           
flask-deploy-669dd4776f-9f9n5   26m          141Mi           
flask-deploy-669dd4776f-hb6zw   22m          140Mi           
flask-deploy-669dd4776f-qjmkx   38m          141Mi    
$ kubectl get pods -n flask-ns
NAME                            READY   STATUS    RESTARTS   AGE
flask-deploy-669dd4776f-2c78h   1/1     Running   0          40s
flask-deploy-669dd4776f-66d4r   1/1     Running   0          3m59s
flask-deploy-669dd4776f-77trm   1/1     Running   0          40s
flask-deploy-669dd4776f-9f9n5   1/1     Running   0          3m58s
flask-deploy-669dd4776f-hb6zw   1/1     Running   0          40s
flask-deploy-669dd4776f-nlgrt   1/1     Running   0          40s
flask-deploy-669dd4776f-qjmkx   1/1     Running   0          3m57s      
```

After the requests are finished for a long while, the replica numbers drops back to the `minReplicas` value in the `scaler.yaml`.

```shell
$ kubectl top pod -n flask-ns
NAME                            CPU(cores)   MEMORY(bytes)   
flask-deploy-669dd4776f-66d4r   4m           39Mi            
flask-deploy-669dd4776f-9f9n5   4m           39Mi 
```

**NOTICE**: The memory may not drop back immediately due to the garbage collection logic in python.

We can use `controller.kubernetes.io/pod-deletion-cost` control the order of pod deletion. However, the official team suggests a more [suitable approach](https://github.com/kubernetes/kubernetes/issues/107598).
