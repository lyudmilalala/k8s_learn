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

If you want to discard the outdated logs, update the `compactor` and `limits_config` config.

```yaml
 compactor:
    working_directory: /tmp/loki/retention
    compaction_interval: 10m
    retention_enabled: true
    retention_delete_delay: 2h
    delete_request_store: filesystem
limits_config:
    allow_structured_metadata: true
    volume_enabled: true
    retention_period: 48h

```

We upgrade our release with the new configuration file.

```shell
helm upgrade loki ./loki-6.24.0.tgz -n monitor --values loki3-values.yaml
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

## Loki Definitions

### 1. Tenant（租户）
- 定义：Loki 的多租户机制，每个 tenant 拥有独立的数据和查询空间。
- 作用：隔离不同用户或系统的数据，防止互相访问和干扰。
- 标识：通过 HTTP Header `X-Scope-OrgID` 或配置指定，单租户模式下通常为 `fake`。

### 2. Stream（日志流）
- 定义：一组具有相同 label（标签）组合的日志数据集合。
- 作用：Loki 按 label 组织日志，label 唯一确定一个 stream。
- 标识：如 `{job="app", instance="1"}`，每种 label 组合对应一个 stream。

### 3. Chunk（数据块）
- 定义：stream 内一段时间范围内的日志数据的压缩存储单元。
- 作用：提升存储和查询效率，chunk 是 Loki 存储的最小单位。
- 标识：每个 chunk 有唯一 ID，包含 stream 的部分日志（如 1h 或 2MB）。

---

简要总结：
- tenant：数据隔离空间
- stream：标签唯一确定的日志流
- chunk：日志流内的压缩数据块
# Loki

## Loki Directory Structure Explanation

1. **`rules/`** - Contains recording rules and alerting rules configuration files
2. **`tsdb-shipper-active/multitenant/`** - Active TSDB index files organized by time periods (loki_index_20270 through loki_index_20308)
3. **`tsdb-shipper-active/per_tenant/`** - Tenant-specific configurations (empty in your case)
4. **`tsdb-shipper-active/scratch/`** - Temporary working directory for index operations
5. **`tsdb-shipper-active/uploader/`** - Files being prepared for upload to storage
6. **`tsdb-shipper-active/wal/`** - Write-ahead logs for index operations
7. **`tsdb-shipper-cache/`** - Cached TSDB files, likely compacted segments
8. **`wal/`** - Main write-ahead logs containing recent log entries not yet flushed to chunks

9. **`chunks/`** - 存储实际日志数据块（chunk），每个 chunk 代表一段时间内某个 label stream 的日志。结构为 `chunks/<tenant>/<stream_id>/<chunk_id>`，文件为压缩二进制格式。
10. **`retention/`** - Loki compactor 用于数据保留和删除的工作目录，包括删除请求、标记文件和 retention 相关的元数据。

## Answers to Your Questions

### 1. Will files be automatically deleted after 90 days with retention_period: 90d?

Yes, with your configuration:
```yaml
compactor:
  retention_enabled: true
  retention_delete_delay: 24h
limits_config:
  retention_period: 90d
```

Files older than 90 days will be automatically deleted. Specifically:
- **Index files** in `tsdb-shipper-active/multitenant/loki_index_*` directories
- **Chunk files** in `/tmp/loki/chunks` (though not visible in your directory listing)
- **TSDB files** in `tsdb-shipper-cache/` 
- Associated **WAL files** that are older than the retention period

The deletion process works as follows:
1. Compactor identifies data older than 90 days
2. Marks them for deletion with a 24-hour delay (`retention_delete_delay`)
3. Actually removes the files after the delay period

### 2. Can you manually delete files older than a certain time?

Yes, but it's not recommended to manually delete files directly. Instead, use the proper API approach:

```bash
# Using curl to set retention for a specific tenant (replace with your tenant ID or use "fake" for single tenant)
curl -X POST "http://<loki-gateway>:30102/loki/api/v1/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "selector": "{job=~\".*\"}",
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-06-01T00:00:00Z"
  }'

# Or modify the retention period temporarily in your config and restart
```

If you absolutely must manually delete files:
1. Stop the Loki pod first
2. Delete files older than your desired time
3. Restart the Loki pod

### 3. Which files can be deleted without affecting Loki+Grafana operation?

Files that can be safely deleted (oldest first):
1. **WAL checkpoint files** - Older checkpoint directories in `wal/`
2. **Old WAL segments** - Log segments in `wal/` that have been flushed to persistent storage
3. **TSDB index directories** - Older `loki_index_*` directories in `tsdb-shipper-active/multitenant/`
4. **Cached TSDB files** - Files in `tsdb-shipper-cache/` corresponding to old periods

Files that should NOT be deleted:
1. **Active WAL files** - Recent segments in `wal/` that haven't been flushed yet
2. **Current index directories** - The most recent `loki_index_*` directories
3. **Configuration files** - Anything in `rules/` that you actively use
4. **Active TSDB shipper directories** - `scratch/`, `uploader/`, and current `wal/` directories under `tsdb-shipper-active/`

## Recommendation

Instead of manual deletion, rely on Loki's built-in retention mechanism. Your current configuration with `retention_enabled: true` and `retention_period: 90d` should automatically handle cleanup. If you need shorter retention, simply adjust the `retention_period` value in your config and redeploy.

# Loki Working Mechanism: TSDB and WAL Explained

## Overview of Loki Architecture

Loki is a horizontally scalable, highly available log aggregation system inspired by Prometheus. It works differently from traditional log systems by indexing only metadata (labels) rather than full log content, making it more efficient for Kubernetes and cloud-native environments.

## Core Components and Data Flow

### 1. Write Path (Log Ingestion)

#### WAL (Write-Ahead Log)
- **Purpose**: Ensures durability of incoming log entries before they are flushed to persistent storage
- **Location**: Stored in `wal/` directory in your deployment
- **Structure**: Contains segments like `00007060`, `00007061` and checkpoints like `checkpoint.007059`
- **Function**: 
  - Receives incoming log streams
  - Temporarily stores log entries in sequential files
  - Provides crash recovery mechanism (if Loki crashes, it can replay from WAL)
  - Periodically creates checkpoints to compact older entries

#### TSDB Shipper Active Directory
- **Purpose**: Manages indexing of log entries for efficient querying
- **Location**: `tsdb-shipper-active/` directory
- **Structure**:
  - `multitenant/loki_index_*`: Index files organized by time periods
  - `wal/`: Write-ahead logs for index operations
  - `scratch/`: Temporary working directory for index processing

### 2. Storage Layer

#### Chunk Storage
- **Location**: `/tmp/loki/chunks` (in your filesystem configuration)
- **Content**: Compressed log chunks containing actual log content
- **Organization**: Grouped by tenant and time period
- **Format**: Binary format optimized for compression and retrieval

#### Index Storage
- **Location**: `tsdb-shipper-active/multitenant/loki_index_*` directories
- **Content**: Index entries mapping labels and time ranges to chunk locations
- **Format**: TSDB (Time Series Database) format similar to Prometheus

## Read Path (Log Querying)

When you query logs in Grafana for a specific time period, here's what happens:

### 1. Query Processing
```
Grafana Query → Loki Query Frontend → Loki Querier
```

### 2. Index Lookup
1. **Label Matching**: Loki first identifies which series match your label selectors (e.g., `{job="nginx"}`)
2. **Time Range Filtering**: Filters index entries to only those within your specified time range
3. **Index Scanning**: Scans TSDB index files in `tsdb-shipper-active/multitenant/loki_index_*` directories
4. **Chunk Identification**: Retrieves references to chunks that contain matching log entries

### 3. Chunk Retrieval
1. **Chunk Location Resolution**: Uses index data to determine which chunks contain relevant logs
2. **Chunk Fetching**: Retrieves compressed chunks from filesystem storage
3. **Decompression**: Decompresses chunks in memory
4. **Filtering**: Applies any additional filtering (regex, etc.) to the decompressed log lines

### 4. Result Assembly
1. **Sorting**: Orders results chronologically
2. **Limiting**: Applies limits if specified in the query
3. **Return**: Sends results back to Grafana for display

## Detailed TSDB and WAL Interaction

### WAL Processing Flow:
1. Incoming logs are written to WAL (`wal/` directory)
2. Logs are periodically batched and compressed into chunks
3. Chunks are uploaded to persistent storage
4. Index entries are created in TSDB format
5. TSDB entries are written to shipper WAL (`tsdb-shipper-active/wal/`)
6. Index files are periodically flushed to persistent storage
7. WAL segments are cleaned up after data is successfully persisted

### TSDB Index Structure:
- **Time-based Sharding**: Index files are organized by time periods (visible as `loki_index_20270` through `loki_index_20308`)
- **Label Indexing**: Each index contains mappings from label combinations to chunk references
- **Series Chunks**: Each series (unique label combination) has associated chunks with time range information

## Example Query Flow

When you query logs for the last 1 hour in Grafana:

1. **Query Parsing**: Grafana sends query with time range and label selectors to Loki
2. **Index Scan**: Loki scans relevant TSDB index files (based on time range)
3. **Series Matching**: Finds all series that match your label selectors
4. **Chunk Discovery**: Identifies which chunks contain logs in the time range
5. **Chunk Retrieval**: Fetches matching chunks from filesystem
6. **Log Extraction**: Decompresses and extracts individual log lines
7. **Filtering/Sorting**: Applies any additional filters and sorts results
8. **Response**: Returns logs to Grafana for display

## Retention and Cleanup Process

Your retention configuration works as follows:
1. **Compactor Component**: Runs periodically (every 10 minutes based on your config)
2. **Age Detection**: Identifies chunks and indexes older than 90 days
3. **Mark for Deletion**: Marks old data for deletion with 24-hour delay
4. **Physical Deletion**: Removes actual files after delay period
5. **Index Cleanup**: Updates TSDB indexes to remove references to deleted chunks

This approach ensures that Grafana queries for recent data remain fast and efficient while automatically managing storage space through retention policies.

## 如何使用loki-gateway删除日志？