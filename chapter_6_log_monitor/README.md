## Logging - Loki

### Instll `loki-stack`

[First install helm, refer to this link.](https://helm.sh/docs/intro/install/)

[The helm repository of loki-stack is here.](https://artifacthub.io/packages/helm/grafana/loki-stack)

[values.yaml example of the helm chart of loki-stack.](https://github.com/grafana/helm-charts/blob/main/charts/loki-stack/values.yaml)

Install `loki-stack` by helm. Here I have a local copy of helm resource and configuration file.

```shell
helm install loki-stack ./loki-stack-2.9.11/loki-stack -n loki-logging --create-namespace  --values loki-local-values.yaml
```

If images failed to download because of GFW, use the following substitutions.

```shell
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/grafana:8.3.5
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/grafana:8.3.5  docker.io/grafana/grafana:8.3.5
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki:2.6.1
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki:2.6.1  docker.io/grafana/loki:2.6.1
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/promtail:2.8.3
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/promtail:2.8.3  docker.io/grafana/promtail:2.8.3
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/k8s.gcr.io/kube-state-metrics/kube-state-metrics:v2.3.0
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/k8s.gcr.io/kube-state-metrics/kube-state-metrics:v2.3.0  k8s.gcr.io/kube-state-metrics/kube-state-metrics:v2.3.0
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/prom/pushgateway:v1.9.0
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/prom/pushgateway:v1.9.0  docker.io/prom/pushgateway:v1.9.0
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/jimmidyson/configmap-reload:v0.5.0
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/jimmidyson/configmap-reload:v0.5.0  docker.io/jimmidyson/configmap-reload:v0.5.0
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/alertmanager:v0.27.0
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/alertmanager:v0.27.0  quay.io/prometheus/alertmanager:v0.27.0
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/prometheus:v2.54.1
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/prometheus:v2.54.1  quay.io/prometheus/prometheus:v2.54.1
```

Check if the pods and services in namespace `loki-logging` are ready.

```
$ kubectl get svc -n loki-logging
NAME                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
loki-stack              ClusterIP   10.106.15.34    <none>        3100/TCP       20m
loki-stack-grafana      NodePort    10.98.210.213   <none>        80:32298/TCP   20m
loki-stack-headless     ClusterIP   None            <none>        3100/TCP       20m
loki-stack-memberlist   ClusterIP   None            <none>        7946/TCP       20m
```

We use the NodePort of service `loki-stack-grafana` to access Grafana. Indeed, here we can access Grafana by visiting `<host_ip>:31364`.

To uninstall, run

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

通过<host_ip>:31364访问grafana

Access the Grafana dashboard by `<host_ip>:31364`.

Username is `admin`. Password is got by running `kubectl get secret -n loki-logging loki-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode`.

If you use Windows Powershell, run `[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(<secret_val>))`.

After logging in, click the "Explore" on the left side collapse menu to see the log page.

![Home page of Grafana](https://github.com/user-attachments/assets/8cb20d99-a75d-4d20-866d-35ab95c06b11)

Logs in Loki are grouped by tags, and you can only find corresponding logs by tags. Thus, we first choose to group by namespaces, then pick the namespace we are interested in, which is `flask-ns`.

![Choose tags](https://github.com/user-attachments/assets/c039e2e5-42d4-46fe-b819-40689127f42d)

After click the "Show logs" button, you can see logs in namespace `flask-ns`.

![See logs](https://github.com/user-attachments/assets/69725f31-5947-44c5-abe8-26b07d694237)

You can further filter the logs by interested time range as shown below.

![Filter by time range](https://github.com/user-attachments/assets/48ebe9a1-6b49-4712-9e2c-5c246b7ff31d)

## Monitor - Prometheus

In our example, promethus is installed to the cluster together with loki and grafana if you set `prometheus.enabled: true` in the `loki-local-values.yaml`.

If you do not use loki-stack, you may install prometheus and grafana by the following way.

```shell
$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
"prometheus-community" has been added to your repositories
$ helm repo update
$ kubectl create namespace monitoring
kubectl create namespace monitoring
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.15.0
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.15.0  registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.15.0
$ helm install prometheus prometheus-community/prometheus -n monitoring --set alertmanager.persistentVolume.enabled="false" --set server.persistentVolume.enabled="false"
$ helm install prometheus prometheus-community/prometheus -n monitoring --set alertmanager.enabled=false --set server.persistentVolume.existingClaim=prometheus-pvc --set server.persistentVolume.subPath=prometheus
NAME: prometheus
LAST DEPLOYED: Wed Apr  2 12:37:38 2025
NAMESPACE: monitoring
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
The Prometheus server can be accessed via port 80 on the following DNS name from within your cluster:
prometheus-server.monitoring.svc.cluster.local


Get the Prometheus server URL by running these commands in the same shell:
  export POD_NAME=$(kubectl get pods --namespace monitoring -l "app.kubernetes.io/name=prometheus,app.kubernetes.io/instance=prometheus" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace monitoring port-forward $POD_NAME 9090


#################################################################################
######   WARNING: Pod Security Policy has been disabled by default since    #####
######            it deprecated after k8s 1.25+. use                        #####
######            (index .Values "prometheus-node-exporter" "rbac"          #####
###### .          "pspEnabled") with (index .Values                         #####
######            "prometheus-node-exporter" "rbac" "pspAnnotations")       #####
######            in case you still need it.                                #####
#################################################################################


The Prometheus PushGateway can be accessed via port 9091 on the following DNS name from within your cluster:
prometheus-prometheus-pushgateway.monitoring.svc.cluster.local


Get the PushGateway URL by running these commands in the same shell:
  export POD_NAME=$(kubectl get pods --namespace monitoring -l "app=prometheus-pushgateway,component=pushgateway" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace monitoring port-forward $POD_NAME 9091

For more information on running Prometheus, visit:
https://prometheus.io/
$ kubectl get pods -n monitoring
NAME                                                READY   STATUS    RESTARTS   AGE
prometheus-kube-state-metrics-64ddf8d686-h4n9v      1/1     Running   0          32s
prometheus-prometheus-node-exporter-qxlwl           1/1     Running   0          32s
prometheus-prometheus-node-exporter-rz86w           1/1     Running   0          32s
prometheus-prometheus-pushgateway-dd66df54d-vscvc   1/1     Running   0          32s
prometheus-server-9c759f67-f5ksz                    1/2     Running   0          32s
$ kubectl get svc -n monitoring
NAME                                  TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
prometheus-kube-state-metrics         ClusterIP   10.106.187.200   <none>        8080/TCP   26m
prometheus-prometheus-node-exporter   ClusterIP   10.101.99.88     <none>        9100/TCP   26m
prometheus-prometheus-pushgateway     ClusterIP   10.108.161.4     <none>        9091/TCP   26m
prometheus-server                     ClusterIP   10.105.36.97     <none>        80/TCP     26m
```

[Helm chart source](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus)

[prometheus config yaml sample](https://github.com/prometheus-community/helm-charts/blob/main/charts/prometheus/values.yaml)

[Bind to pvc](https://medium.com/@gayatripawar401/deploy-prometheus-and-grafana-on-kubernetes-using-helm-5aa9d4fbae66)

[Another tutorial](https://medium.com/@akilblanchard09/monitoring-a-kubernetes-cluster-using-prometheus-and-grafana-8e0f21805ea9)

See the prometheus UI...

### Add a new Dashboard to Grafana

**NOTICE:** If we do not choose a presistence storage type for loki-stack, all configurations we made will be lost after restart the service or cluster.

Visit the [Grafana Dashboard](https://grafana.com/grafana/dashboards/) website to search for a desired dashboard.

![Grafana Dashboard Home Page](https://github.com/user-attachments/assets/d89af14d-6e4f-45b8-b702-6cac396d6635)

Here are some useful dashboards to monitor your k8s cluster with the help of promethus.

- 12740 - Kubernetes monitoring dashboard
- 15282 - Kubernetes cluster monitoring

Click the desired dashboard to see its detail, and copy its dashboard ID.

![Copy Id from the Dashboard Detail](https://github.com/user-attachments/assets/b5d3cf71-1f12-4a3a-a035-ecc8b8ad5405)

Go back to your Grafana, choose Create -> Import, and then fill in the dashboard ID in the shown up page. 

![Initialize Dashboard Configuration 1](https://github.com/user-attachments/assets/be6d45ba-ba3a-4810-8ae4-5ec152d9fe70)

Continue for more configuration, choose `Promethus` to be the data source.

![Initialize Dashboard Configuration 1](https://github.com/user-attachments/assets/01dd9ac1-ffb8-4b3e-960f-fcee20e0ca41)

Then you will see the dashboard shown up.

![New Dashboard](https://github.com/user-attachments/assets/72c88c5b-7703-4f34-a7d2-c17925c4ae96)


### Edit the Dashboard in Grafana

Here we take dashboard No.

After create the dashboard, we can find out that the graph does not show the CPU usage of each pod as it announced. 

So we select the graph, right-click on it, and choose Edit to see what is wrong.

Here we can see the prometheus query (PromQL) used to draw this graph.

![Customize an element](https://github.com/user-attachments/assets/3243dfb8-c10a-4069-9352-cb11041f321c)

Simply change to the "podName" in the sentence by "pod", and you will see the CPU usage of all pods grouped by their names shows up.

You can also create your own dashboards using customized PromQL. A collection of useful prometheus alert rules can be found at [Awesome Prometheus Alerts](https://github.com/asifMuzammil/awesome-prometheus-alerts).

The Loki dashboard on grafana is crated by some similar queries called LogQL.

## Presist Data
