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
loki-stack-grafana      NodePort    10.98.210.213   <none>        80:31364/TCP   20m
loki-stack-headless     ClusterIP   None            <none>        3100/TCP       20m
loki-stack-memberlist   ClusterIP   None            <none>        7946/TCP       20m
```

则可以通过<host_ip>:31364访问grafana

用户名为admin

Grafana密码通过`kubectl get secret -n loki-logging loki-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode`获取，然后需要base64解码

powershell执行`[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(<secret_val>))`

卸载

```
helm uninstall loki-stack -n loki-logging
```

## Monitor - Prometheus