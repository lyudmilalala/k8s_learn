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

- set `deploymentMode` to `SingleBinary`, set the corresponding `singleBinary.replicas` to 1, and other modes' `replicas` to 0.
- set `auth_enabled` to `false`, to make it easier to be connected with our Grafana at this time.
- point the storage to `filesystem`, this will let loki store its data to the filesystem in the container, neither memory nor a remote s3 server. Also currently we set the `singleBinary.persistence.enabled` to false to simplify the demo.
- expose the loki service on a node port `30102`.

Install Loki to the K8s cluster with the configuration file `loki3-values.yaml`.

```shell
helm install loki ./loki-6.24.0.tgz --values loki3-values.yaml -n monitor --create-namespace
```

Here we already download the helm chart to local, so we install it as `helm install loki ./loki-6.24.0`. You can directly install the remote chart as `helm install loki grafana/loki`.

Result will be something like this 

```shell
NAME: loki
LAST DEPLOYED: Sun May  4 19:25:44 2025
NAMESPACE: monitor
STATUS: deployed
REVISION: 1
NOTES:
***********************************************************************
 Welcome to Grafana Loki
 Chart version: 6.24.0
 Chart Name: loki
 Loki version: 3.3.2
***********************************************************************

** Please be patient while the chart is being deployed **

Tip:

  Watch the deployment status using the command: kubectl get pods -w --namespace monitor

If pods are taking too long to schedule make sure pod affinity can be fulfilled in the current cluster.

***********************************************************************
Installed components:
***********************************************************************
* loki

Loki has been deployed as a single binary.
This means a single pod is handling reads and writes. You can scale that pod vertically by adding more CPU and memory resources.


***********************************************************************
Sending logs to Loki
***********************************************************************

Loki has been configured with a gateway (nginx) to support reads and writes from a single component.

You can send logs from inside the cluster using the cluster DNS:

http://loki-gateway.monitor.svc.cluster.local/loki/api/v1/push

You can test to send data from outside the cluster by port-forwarding the gateway to your local machine:

  kubectl port-forward --namespace monitor svc/loki-gateway 3100:80 &

And then using http://127.0.0.1:3100/loki/api/v1/push URL as shown below:

```
curl -H "Content-Type: application/json" -XPOST -s "http://127.0.0.1:3100/loki/api/v1/push"  \
--data-raw "{\"streams\": [{\"stream\": {\"job\": \"test\"}, \"values\": [[\"$(date +%s)000000000\", \"fizzbuzz\"]]}]}"
```

Then verify that Loki did received the data using the following command:

```
curl "http://127.0.0.1:3100/loki/api/v1/query_range" --data-urlencode 'query={job="test"}' | jq .data.result
```

***********************************************************************
Connecting Grafana to Loki
***********************************************************************

If Grafana operates within the cluster, you'll set up a new Loki datasource by utilizing the following URL:

http://loki-gateway.monitor.svc.cluster.local/
```

The following new pods and services should have been created.

```shell
# kubectl get pods -n monitor
NAME                            READY   STATUS    RESTARTS   AGE
loki-0                          2/2     Running   0          103s
loki-canary-5b624               1/1     Running   0          104s
loki-chunks-cache-0             2/2     Running   0          104s
loki-gateway-545f6777b4-ccqdk   1/1     Running   0          104s
loki-results-cache-0            2/2     Running   0          104s
$ kubectl get svc -n monitor
NAME                 TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)              AGE
loki                 ClusterIP   10.99.207.194    <none>        3100/TCP,9095/TCP    111s
loki-canary          ClusterIP   10.111.253.150   <none>        3500/TCP             111s
loki-chunks-cache    ClusterIP   None             <none>        11211/TCP,9150/TCP   111s
loki-gateway         NodePort    10.110.67.213    <none>        80:30102/TCP         111s
loki-headless        ClusterIP   None             <none>        3100/TCP             111s
loki-memberlist      ClusterIP   None             <none>        7946/TCP             111s
loki-results-cache   ClusterIP   None             <none>        11211/TCP,9150/TCP   111s
```

To test the running Loki, run the following command on a k8s node

```shell
curl -H "Content-Type: application/json" -XPOST -s "http://127.0.0.1:30102/loki/api/v1/push"  \
--data-raw "{\"streams\": [{\"stream\": {\"job\": \"test\"}, \"values\": [[\"$(date +%s)000000000\", \"fizzbuzz\"]]}]}"
```

Then verify that Loki did received the data using the following command, and you will see some similar result.

```shell
$ curl "http://127.0.0.1:30102/loki/api/v1/query_range" --data-urlencode 'query={job="test"}' | jq .data.result
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  2848    0  2820  100    28    98k    996 --:--:-- --:--:-- --:--:--  103k
[
  {
    "stream": {
      "detected_level": "unknown",
      "job": "test",
      "service_name": "test"
    },
    "values": [
      [
        "1746358195000000000",
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
NAME: promtail
LAST DEPLOYED: Sun May  4 19:31:27 2025
NAMESPACE: monitor
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
***********************************************************************
 Welcome to Grafana Promtail
 Chart version: 6.16.6
 Promtail version: 3.0.0
***********************************************************************

Verify the application is working by running these commands:
* kubectl --namespace monitor port-forward daemonset/promtail 3101
* curl http://127.0.0.1:3101/metrics
```

To test the running Promtail, first expose the Promtail container port to node port by `kubectl --namespace monitor port-forward daemonset/promtail 3101`.

Then in another session window of the same node, run `curl http://127.0.0.1:3101/metrics`.

You will see logs of pods on this node being pushed into loki like this 

```shell
promtail_file_bytes_total{path="/var/log/pods/kube-system_calico-node-hkhjb_b51fb727-b70c-4896-b711-46ef42e4bdf0/calico-node/45.log"} 802034
promtail_file_bytes_total{path="/var/log/pods/kube-system_calico-node-hkhjb_b51fb727-b70c-4896-b711-46ef42e4bdf0/calico-node/46.log"} 471060
promtail_file_bytes_total{path="/var/log/pods/kube-system_calico-node-hkhjb_b51fb727-b70c-4896-b711-46ef42e4bdf0/install-cni/1.log"} 8403
promtail_file_bytes_total{path="/var/log/pods/kube-system_calico-node-hkhjb_b51fb727-b70c-4896-b711-46ef42e4bdf0/mount-bpffs/0.log"} 1313
promtail_file_bytes_total{path="/var/log/pods/kube-system_calico-node-hkhjb_b51fb727-b70c-4896-b711-46ef42e4bdf0/upgrade-ipam/0.log"} 751
promtail_file_bytes_total{path="/var/log/pods/kube-system_kube-proxy-hlcvd_6fbbc14e-5d62-49d7-ab87-dd98f7fd73c3/kube-proxy/45.log"} 3386
promtail_file_bytes_total{path="/var/log/pods/kube-system_kube-proxy-hlcvd_6fbbc14e-5d62-49d7-ab87-dd98f7fd73c3/kube-proxy/46.log"} 3384
```

## View logs in Grafana

First add Loki as a data source in your Grafana.

From the home page, visit Connections -> Data sources -> Add data source

Choose Loki as the data source type, then input url `http://loki-gateway.monitor.svc.cluster.local/` in the **Connection** text input box as guided by the helm installation output. Here we also change our data source **Name** to "myLoki". We keep other configurations as default, and click the **Save & Test** button at the bottom of the page.

![Add data source 1](https://github.com/user-attachments/assets/92857534-3375-4393-a590-038538852809)

![Add data source 2](https://github.com/user-attachments/assets/3b305aec-9849-4de8-b3d5-d2d9cbb50931)

![Add data source 3](https://github.com/user-attachments/assets/3929b600-a129-44ad-ba85-7b46ef34c999)

After successfully adding the data source, go back to the Connections -> Data sources page, click the **Explore** button at the right side of our Loki data source.

![Test Loki connection to Grafana 1](https://github.com/user-attachments/assets/34df0cb1-5818-4eb0-918b-9febb265840e)

In the **Label filters** drop down box, you should see a bunch of choices, such as app, container, namespace. Here we choose namespace as an example, and choose **kube-system** as the value.

Remember to remove the **Line contains** box. Then click the **Run Query** button at the right upper corner of the page.

![Test Loki connection to Grafana 2](https://github.com/user-attachments/assets/b7042939-b14a-49b9-ade4-35ae6ea67953)

You will see logs appears on the page.

![Test Loki connection to Grafana 3](https://github.com/user-attachments/assets/49b2e0f5-f4d9-4efe-8b5a-fce8762ef5cd)

Then visit the [Grafana Dashboard](https://grafana.com/grafana/dashboards/) website to search for a desired dashboard.

Here we choose dashboard No.15141 as an example. Click into its detail, and copy its dashboard ID.

![Copy Id from the Dashboard Detail](https://github.com/user-attachments/assets/b5d3cf71-1f12-4a3a-a035-ecc8b8ad5405)

![image](https://github.com/user-attachments/assets/29fe55b8-8b93-438e-83f5-fa87d99a2bf6)

Go back to your Grafana, choose Dashboards -> **New** button at the right side of the page -> Import, and then fill in the dashboard ID in the shown up page. 

![Initialize Dashboard Configuration 1](https://github.com/user-attachments/assets/49b06c77-9210-4013-9648-d950bb6e1118)

![image](https://github.com/user-attachments/assets/813d9290-28cd-4bf7-ac0f-a872a0b25449)

Continue for more configuration, choose Loki to be the data source.

![image](https://github.com/user-attachments/assets/fe672b38-6828-4b41-bb12-f42e7e1879ed)

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
pvc-44f6ba7c-b4d7-4262-a2c8-8ac2a5e20f73   10Gi       RWO            Retain           Bound    monitor/storage-loki-0      loki-sc                  8m
$ kubectl get pvc -n monitor
storage-loki-0      Bound    pvc-44f6ba7c-b4d7-4262-a2c8-8ac2a5e20f73   10Gi       RWO            loki-sc         8m
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
