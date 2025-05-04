## Before All

In thie tutorial we install **Loki 3** and Promtail from their latest official helm chart independently. 

Some tutorials about deploying Loki on Kubernetes use the third-party project `loki-stack`, which relies on **Loki 2** and has been proven to be deprecated. If you encounter issues in your usage of `loki-stack`, it is difficult to get help from the latest official documentation. Therefore, we will not include `loki-stack` in the scope of discussion in this tutorial. We do have a simple analysis of `loki-stack` and **Loki 2**, derived from my limited experience with it, which will be placed in `loki-stack-memo.md`.

Before pulling resource, you need to add the grafana repository.

```shell
$ helm repo add grafana https://grafana.github.io/helm-charts 
$ helm repo update
```

## Official documentations

[Helm repo of Loki](https://artifacthub.io/packages/helm/grafana/loki)

[Helm repo of Promtail](https://artifacthub.io/packages/helm/grafana/promtail)

## Install Loki

if you have difficuilties to download images from the official repositories, use the following substitutions.

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki-canary:3.3.2
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki-canary:3.3.2 docker.io/grafana/loki-canary:3.3.2
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki:3.3.2
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/loki:3.3.2 docker.io/grafana/loki:3.3.2
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nginxinc/nginx-unprivileged:1.27-alpine
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nginxinc/nginx-unprivileged:1.27-alpine docker.io/nginxinc/nginx-unprivileged:1.27-alpine
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/prom/memcached-exporter:v0.15.0
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/prom/memcached-exporter:v0.15.0 docker.io/prom/memcached-exporter:v0.15.0
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/memcached:1.6.33-alpine
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/memcached:1.6.33-alpine docker.io/memcached:1.6.33-alpine
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/kiwigrid/k8s-sidecar:1.28.0 && \
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/kiwigrid/k8s-sidecar:1.28.0  docker.io/kiwigrid/k8s-sidecar:1.28.0
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/agent-operator:v0.25.1 && \
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/agent-operator:v0.25.1  docker.io/grafana/agent-operator:v0.25.1
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/agent:v0.25.1 && \
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/agent:v0.25.1  docker.io/grafana/agent:v0.25.1s
```

Then we create a customized configuration file `loki3-values.yaml`. The modifications are mainly:

- set `auth_enabled` to `false`, to make it easier to be connected with our Grafana at this time
- point the storage to `filesystem`, this will let loki store its data to the filesystem in the container, neither memory nor a remote s3 server
- expose the loki service on a node port `30102`

Install Loki to the K8s cluster with the configuration file `loki3-values.yaml`.

```shell
helm install loki ./loki-6.24.0 --values loki3-values.yaml -n monitor --create-namespace
```

Here we already download the helm chart to local, so we install it as `helm install loki ./loki-6.24.0`. You can directly install the remote chart as `helm install loki grafana/loki`.

Result will be something like this 

```shell
```

To test the running Loki, run the following command on a k8s node

```shell
curl -H "Content-Type: application/json" -XPOST -s "http://127.0.0.1:30102/loki/api/v1/push"  \
--data-raw "{\"streams\": [{\"stream\": {\"job\": \"test\"}, \"values\": [[\"$(date +%s)000000000\", \"fizzbuzz\"]]}]}" -H X-Scope-OrgId:foo
```

Then verify that Loki did received the data using the following command, and you will see some similar result.

```shell
$ curl "http://127.0.0.1:30102/loki/api/v1/query_range" --data-urlencode 'query={job="test"}' -H X-Scope-OrgId:foo | jq .data.result
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  2845    0  2817  100    28  91292    907 --:--:-- --:--:-- --:--:-- 94833
[
  {
    "stream": {
      "detected_level": "unknown",
      "job": "test",
      "service_name": "test"
    },
    "values": [
      [
        "1746201587000000000",
        "fizzbuzz"
      ]
    ]
  }
]
```

## Install Promtail

If you have difficuilties to download images from the official repositories, use the following substitutions.

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/promtail:3.0.0 && \
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/promtail:3.0.0  docker.io/grafana/promtail:3.0.0
```

Install Promtail to the K8s cluster as below. 

Please ensure it is in the same namespace as Loki. Promtail run as a stateful set, an the pod on each node collects data and forwards them to `http://loki-gateway.monitoring.svc.cluster.local/` by default. This default loki gateway configuration only works when Loki and Promtail are in the same namespace.

Also, a customized configuration sample is shown in `promtail-values.yaml`.

```shell
helm install promtail ./promtail-6.16.6.tgz -n monitor --create-namespace
```

Here we already download the helm chart to local, so we install it as `helm install promtail ./promtail-6.16.6.tgz`. You can directly install the remote chart as `helm install promtail grafana/promtail`.

Result will be something like this 

```shell
```

To test the running Promtail, first expose the container port by `kubectl --namespace monitor port-forward daemonset/promtail 3101`.

Then in another session window of the same node, run `curl http://127.0.0.1:3101/metrics`.

You will see logs being pushed into loki like this 

```shell
```

## View logs in Grafana

First add Loki as a data source in your Grafana.

From the home page, visit connection -> data source -> Add

Then visit the [Grafana Dashboard](https://grafana.com/grafana/dashboards/) website to search for a desired dashboard.

Here we choose dashboard No.XXX as an example. Click into its detail, and copy its dashboard ID.

![Copy Id from the Dashboard Detail](https://github.com/user-attachments/assets/b5d3cf71-1f12-4a3a-a035-ecc8b8ad5405)

Go back to your Grafana, choose Create -> Import, and then fill in the dashboard ID in the shown up page. 

![Initialize Dashboard Configuration 1](https://github.com/user-attachments/assets/be6d45ba-ba3a-4810-8ae4-5ec152d9fe70)

Continue for more configuration, choose Loki to be the data source.

![Initialize Dashboard Configuration 1](https://github.com/user-attachments/assets/01dd9ac1-ffb8-4b3e-960f-fcee20e0ca41)

Then you will see the dashboard shown up.

![New Dashboard](https://github.com/user-attachments/assets/72c88c5b-7703-4f34-a7d2-c17925c4ae96)

## Add persistence

Currently data in Loki is not persistent. If we reboot the k8s servers. we will lose the existing log data. To avoid this situation, we need to mount a persistent storage to Loki.

We first scratch a `StorageClass` for grafana in `loki-sc.yaml`, and use `kubectl apply -f loki-sc.yaml` to create it in the k8s cluster.

*Here we use seaweedfs as the storage component, and assume you have already had the seaweedfs-csi-driver in your cluster. You can use NFS, or other storage as your choice. For more about the storage in k8s, please refer to [chapter 11: persistence](https://github.com/lyudmilalala/k8s_learn/tree/master/chapter_11_persistence).*

Then we bind the existing grafana release to this `StorageClass`.  We modify the `persistence` section in `loki3-values.yaml` to below:

```yaml
persistence:
  type: pvc
  enabled: true
  storageClassName: loki-sc
  size: 10Gi
```

To rolling outdated presistent data to avoid running out of disk space...

We upgrade our release with the new configuration file.

```shell
helm upgrade loki ./loki-6.24.0 -n monitor --values loki3-values.yaml
```

We can see a pv and a pvc have been dynamically created for Loki. Now even when rebooting your k8s server now, the log data will not be lost.

```shell
$ kubectl get pv

$ kubectl get pvc -n monitor

```

Unlike Grafana and Prometheus, Loki cannot choose to be mounted to an existing pvc.

## Choose the deployment mode in Loki 3

Besides `SingleBinary`, you can also choose the deployment mode of your Loki applicatioin to be `SimpleScalable` or `Distributed` by `deploymentMode` in `values.yaml`. Related logic in Loki 3 is at line 49 in `templates/_helpers.tpl` as below.

```tpl
{{/*
Return if deployment mode is simple scalable
*/}}
{{- define "loki.deployment.isScalable" -}}
  {{- and (eq (include "loki.isUsingObjectStorage" . ) "true") (or (eq .Values.deploymentMode "SingleBinary<->SimpleScalable") (eq .Values.deploymentMode "SimpleScalable") (eq .Values.deploymentMode "SimpleScalable<->Distributed")) }}
{{- end -}}

{{/*
Return if deployment mode is single binary
*/}}
{{- define "loki.deployment.isSingleBinary" -}}
  {{- or (eq .Values.deploymentMode "SingleBinary") (eq .Values.deploymentMode "SingleBinary<->SimpleScalable") }}
{{- end -}}

{{/*
Return if deployment mode is distributed
*/}}
{{- define "loki.deployment.isDistributed" -}}
  {{- and (eq (include "loki.isUsingObjectStorage" . ) "true") (or (eq .Values.deploymentMode "Distributed") (eq .Values.deploymentMode "SimpleScalable<->Distributed")) }}
{{- end -}}
```

## Uninstall

If you want to uninstall loki. Run `helm uninstall loki -n monitor`

If you want to uninstall promtail. Run `helm uninstall promtail -n monitor`