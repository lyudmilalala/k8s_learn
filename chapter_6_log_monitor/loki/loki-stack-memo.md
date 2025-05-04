## Loki-stack

[The helm repository of loki-stack is here.](https://artifacthub.io/packages/helm/grafana/loki-stack)

[values.yaml example of the helm chart of loki-stack.](https://github.com/grafana/helm-charts/blob/main/charts/loki-stack/values.yaml)

`Loki-stack` is a project that integrates Loki, Promtail, Grafana, and Prometheus, enabling one-click deployment of a logging and monitoring system. Its latest version is still based on **Loki 2** and only includes the singleBinary implementation of Loki, Redundant resource files and parameters have been eliminated.

`Loki-stack` is deprecated. Its documentation is insufficient, and its configuration has significantly diverged from the latest versions of Loki and Grafana. To fully manage this project, you need to read the `values.yaml` and template files of each module in carefully. On the other hand, going through its source files serves as an excellent example for learning to build Helm charts.

The `loki-stack-values.yaml` shows a bsic configuration file that you can use for deploying a helm release of `loki-stack` with Loki, Promtail, Grafana, and Prometheus, butt without any persistence.

```shell
helm install loki-stack ./loki-stack-2.9.11/loki-stack -n loki-logging --create-namespace  --values loki-stack-values.yaml
```

If you have difficuilties to download images from the official repositories, use the following substitutions.

```shell
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/grafana:8.3.5
$ docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/grafana:8.3.5  docker.io/grafana/grafana:8.3.5
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki:2.6.1
$ docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki:2.6.1  docker.io/grafana/loki:2.6.1
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/promtail:2.8.3
$ docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/promtail:2.8.3  docker.io/grafana/promtail:2.8.3
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/k8s.gcr.io/kube-state-metrics/kube-state-metrics:v2.3.0
$ docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/k8s.gcr.io/kube-state-metrics/kube-state-metrics:v2.3.0  k8s.gcr.io/kube-state-metrics/kube-state-metrics:v2.3.0
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/prom/pushgateway:v1.9.0
$ docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/prom/pushgateway:v1.9.0  docker.io/prom/pushgateway:v1.9.0
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/jimmidyson/configmap-reload:v0.5.0
$ docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/jimmidyson/configmap-reload:v0.5.0  docker.io/jimmidyson/configmap-reload:v0.5.0
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/alertmanager:v0.27.0
$ docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/alertmanager:v0.27.0  quay.io/prometheus/alertmanager:v0.27.0
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/prometheus:v2.54.1
$ docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/prometheus:v2.54.1  quay.io/prometheus/prometheus:v2.54.1
```

Services in namespace `loki-logging` will be as below.

```
$ kubectl get svc -n loki-logging
NAME                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
loki-stack              ClusterIP   10.106.15.34    <none>        3100/TCP       20m
loki-stack-grafana      NodePort    10.98.210.213   <none>        80:32298/TCP   20m
loki-stack-headless     ClusterIP   None            <none>        3100/TCP       20m
loki-stack-memberlist   ClusterIP   None            <none>        7946/TCP       20m
```

Log into the Grafana at `<host_ip>:32298`, click the "Explore" on the left side collapse menu to see the log page.

![Home page of Grafana](https://github.com/user-attachments/assets/8cb20d99-a75d-4d20-866d-35ab95c06b11)

Logs in Loki are grouped by tags, and you can only find corresponding logs by tags. Thus, we first choose to group by namespaces, then pick the namespace we are interested in, which is `flask-ns`.

![Choose tags](https://github.com/user-attachments/assets/c039e2e5-42d4-46fe-b819-40689127f42d)

After click the "Show logs" button, you can see logs in namespace `flask-ns`.

![See logs](https://github.com/user-attachments/assets/69725f31-5947-44c5-abe8-26b07d694237)

You can further filter the logs by interested time range as shown below.

![Filter by time range](https://github.com/user-attachments/assets/48ebe9a1-6b49-4712-9e2c-5c246b7ff31d)

## Uninstall

If you want to uninstall loki-stack. Run `helm uninstall loki-stack -n loki-logging`

## Choose the deployment mode in Loki 2

Loki 2 determines the deployment mode of the service by `loki.isUsingObjectStorage` in `values.yaml`. Related logic in Loki 2 is at line 26 in `templates/_helpers.tpl` as below.

```tpl
{{/*
Return if deployment mode is simple scalable
*/}}
{{- define "loki.deployment.isScalable" -}}
  {{- eq (include "loki.isUsingObjectStorage" . ) "true" }}
{{- end -}}

{{/*
Return if deployment mode is single binary
*/}}
{{- define "loki.deployment.isSingleBinary" -}}
  {{- eq (include "loki.isUsingObjectStorage" . ) "false" }}
{{- end -}}
```