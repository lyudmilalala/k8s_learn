## Logging - Loki

### 使用`loki-stack`一键式安装到K8s集群

[需要使用helm](https://helm.sh/docs/intro/install/)

[helm repo](https://artifacthub.io/packages/helm/grafana/loki-stack)

[帮不了什么忙的values.yaml example](https://github.com/grafana/helm-charts/blob/main/charts/loki-stack/values.yaml)

通过helm安装

```
helm install loki-stack ./loki-stack-2.9.11/loki-stack -n loki-logging --create-namespace  --values loki-local-values.yaml
```

若下载镜像遭遇GFW，可使用如下

```shell
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/grafana:8.3.5
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/grafana:8.3.5  docker.io/grafana/grafana:8.3.5
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki:2.6.1
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki:2.6.1  docker.io/grafana/loki:2.6.1
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/promtail:2.8.3
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/promtail:2.8.3  docker.io/grafana/promtail:2.8.3
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/k8s.gcr.io/kube-state-metrics/kube-state-metrics:v2.3.0
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/k8s.gcr.io/kube-state-metrics/kube-state-metrics:v2.3.0  k8s.gcr.io/kube-state-metrics/kube-state-metrics:v2.3.0
```

通过loki-stack-grafana服务的NodePort访问Grafana控制台，即可查看log

```
$ kubectl get svc -n loki-logging
NAME                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
loki-stack              ClusterIP   10.106.15.34    <none>        3100/TCP       20m
loki-stack-grafana      NodePort    10.98.210.213   <none>        80:32298/TCP   20m
loki-stack-headless     ClusterIP   None            <none>        3100/TCP       20m
loki-stack-memberlist   ClusterIP   None            <none>        7946/TCP       20m
```
zhvHpoNl5tgUVer8gCQPFjzsAgLqKGQQd3yQ4oYj

32298

则可以通过<host_ip>:31364访问grafana


用户名为admin

Grafana密码通过`kubectl get secret -n loki-logging loki-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode`获取，然后需要base64解码

powershell执行`[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(<secret_val>))`

卸载

```
helm uninstall loki-stack -n loki-logging
```

### Write log in application

Update the `app.py` to add logger. Pack changes into a new image.

```shell
$ docker build -t crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:4.2.0 .
$ docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-test:4.2.0
$ kubectl apply -f flask-deployment.yaml 
$ kubectl get pods -n flask-ns
NAME                            READY   STATUS    RESTARTS   AGE
flask-deploy-7f5c58d55f-9dxgx   1/1     Running   0          6s
flask-deploy-7f5c58d55f-qppd7   1/1     Running   0          6s
flask-deploy-7f5c58d55f-vfb2p   1/1     Running   0          6s
```

Send request again, and then check the log of the pod which is used to run the task. You should see the logs you wrote in `app.py`.

```shell
$ curl -X POST 'http://47.106.149.128:30050/run' --header 'Content-Type: application/json' --data-raw '{"name": "task1", "time_cost": 10,"mem_cost": 50}'
{"current_queue_size": 0, "msg": "Pod flask-deploy-7f5c58d55f-qppd7 starts processing task = task1", "pod_name": "flask-deploy-7f5c58d55f-qppd7", "status": 200}
$ kubectl logs flask-deploy-7f5c58d55f-qppd7 -n flask-ns
 * Serving Flask app 'app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
WARNING:werkzeug: * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
INFO:werkzeug: * Running on http://172.16.122.223:8080/ (Press CTRL+C to quit)
INFO:werkzeug: * Restarting with stat
WARNING:werkzeug: * Debugger is active!
INFO:werkzeug: * Debugger PIN: 294-244-223
INFO:root:[LOG 2025-02-11 17:20:15.839] Start task = task1, time_cost = 10, mem_cost = 50
INFO:werkzeug:172.16.167.128 - - [11/Feb/2025 17:20:15] "POST /run HTTP/1.1" 200 -
INFO:root:[LOG 2025-02-11 17:20:25.882] End task = task1
```

### View log in Grafana

## Monitor - Prometheus