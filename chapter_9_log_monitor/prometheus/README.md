## Official documentations

[Helm repo of Prometheus](https://artifacthub.io/packages/helm/prometheus-community/prometheus)

[Helm chart source of Prometheus](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus)

[Prometheus config yaml sample](https://github.com/prometheus-community/helm-charts/blob/main/charts/prometheus/values.yaml)

## Install Prometheus

Before pulling resource, you need to add the Prometheus repository.

```shell
$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
$ helm repo update
```

if you have difficuilties to download images from the official repositories, use the following substitutions.

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.15.0 && \
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.15.0  registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.15.0
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/node-exporter:v1.9.0 && \
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/quay.io/prometheus/node-exporter:v1.9.0  quay.io/prometheus/node-exporter:v1.9.0
```

Install Prometheus to the K8s cluster. We 

```shell
helm install prometheus ./prometheus-27.5.1.tgz --set alertmanager.persistentVolume.enabled="false" --set server.persistentVolume.enabled="false" -n monitor --create-namespace
```

Here we already download the helm chart to local, so we install it as `helm install prometheus ./prometheus-27.5.1.tgz`. You can directly install the remote chart as `helm install prometheus prometheus-community/prometheus`.

We also disable the alert manager and the persistence in our command to simplify the demo.

Result will be something like this 

```shell
NAME: prometheus
LAST DEPLOYED: Sun May  4 20:49:48 2025
NAMESPACE: monitor
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
The Prometheus server can be accessed via port 80 on the following DNS name from within your cluster:
prometheus-server.monitor.svc.cluster.local


Get the Prometheus server URL by running these commands in the same shell:
  export NODE_PORT=$(kubectl get --namespace monitor -o jsonpath="{.spec.ports[0].nodePort}" services prometheus-server)
  export NODE_IP=$(kubectl get nodes --namespace monitor -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT


#################################################################################
######   WARNING: Pod Security Policy has been disabled by default since    #####
######            it deprecated after k8s 1.25+. use                        #####
######            (index .Values "prometheus-node-exporter" "rbac"          #####
###### .          "pspEnabled") with (index .Values                         #####
######            "prometheus-node-exporter" "rbac" "pspAnnotations")       #####
######            in case you still need it.                                #####
#################################################################################


The Prometheus PushGateway can be accessed via port 9091 on the following DNS name from within your cluster:
prometheus-prometheus-pushgateway.monitor.svc.cluster.local


Get the PushGateway URL by running these commands in the same shell:
  export POD_NAME=$(kubectl get pods --namespace monitor -l "app=prometheus-pushgateway,component=pushgateway" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace monitor port-forward $POD_NAME 9091

For more information on running Prometheus, visit:
https://prometheus.io/
```

Check for the pods and services created by Prometheus.

```shell
$ kubectl get pods -n monitor
NAME                                                READY   STATUS    RESTARTS   AGE
prometheus-kube-state-metrics-64ddf8d686-tsxdv      1/1     Running   0          2m40s
prometheus-prometheus-node-exporter-g5wxm           1/1     Running   0          2m40s
prometheus-prometheus-node-exporter-xzspt           1/1     Running   0          2m40s
prometheus-prometheus-pushgateway-dd66df54d-c5s8c   1/1     Running   0          2m40s
prometheus-server-6997876587-c8f6d                  2/2     Running   0          2m40s
$ kubectl get svc -n monitor
NAME                                  TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)              AGE
prometheus-kube-state-metrics         ClusterIP   10.96.91.146     <none>        8080/TCP             2m53s
prometheus-prometheus-node-exporter   ClusterIP   10.105.23.246    <none>        9100/TCP             2m53s
prometheus-prometheus-pushgateway     ClusterIP   10.107.136.83    <none>        9091/TCP             2m53s
prometheus-server                     NodePort    10.100.127.170   <none>        80:30103/TCP         2m53s
```

If you visit `http://$NODE_IP:$NODE_PORT`, in our case is `http://$NODE_IP:30101`, by browser, you should also see the Prometheus dashboard.

![image](https://github.com/user-attachments/assets/4f23b236-3ec3-4304-a5eb-54f3e70cfb66)

## View k8s metrics in Prometheus

First add Prometheus as a data source in your Grafana.

From the home page, visit Connections -> Data sources -> Add data source

Choose Prometheus as the data source type, then input url http://prometheus-server.monitor.svc.cluster.local/ in the Connection text input box as guided by the helm installation output. Here we also change our data source Name to "myPrometheus". We keep other configurations as default, and click the Save & Test button at the bottom of the page.

![Add data source 1](https://github.com/user-attachments/assets/92857534-3375-4393-a590-038538852809)

![Add data source 2](https://github.com/user-attachments/assets/b842444e-9720-4696-bc67-7f9364f10e87)

![Add data source 3](https://github.com/user-attachments/assets/5524d19d-c342-4846-9368-eaa0c7bba5f2)

After successfully adding the data source, go to the **Explore** page. Choose our Prometheus data source as the **Outline**. 

Then randomly choose some **Metrics** and **Label Filters** (you should see a bunch of options in a dropdown list when clicking into the input boxes), and click the **Run query** button at the right upper corner of the page.

![Test Prometheus connection to Grafana 1](https://github.com/user-attachments/assets/65403c23-62b2-494f-b23a-b589774f0d01)

## Import a wonderful Dashboard

Unlike logs, we want to see all different kinds of queries at one time. It will cost a lot of work if we create them all by ourselves. Fortunately, Grafana offers some dashboards created by the community. You can visit the [Grafana Dashboard](https://grafana.com/grafana/dashboards/) website to search for a desired dashboard.

Some useful dashboards are

- 12740 - Kubernetes monitoring dashboard
- 15282 - Kubernetes cluster monitoring

Here we choose dashboard No. 12740 as an example. Click into its detail, and copy its dashboard ID.

![Copy Id from the Dashboard Detail](https://github.com/user-attachments/assets/b5d3cf71-1f12-4a3a-a035-ecc8b8ad5405)

Go back to your Grafana, choose Dashboards -> **New** button at the right side of the page -> Import.

![Initialize Dashboard 1](https://github.com/user-attachments/assets/a71bdc9b-f490-4e22-87f8-9f478b6987ad)

Fill in the dashboard ID in the shown up page. 

![Initialize Dashboard 2](https://github.com/user-attachments/assets/19a279f4-b1c5-408d-9a47-28bf8b81b24f)

Continue for more configuration, choose your prometheus data source to be the data source.

![Initialize Dashboard 3](https://github.com/user-attachments/assets/e4690849-dd7b-4898-95ae-7aea01a427b7)

Then you will see the dashboard shown up.

![New Dashboard](https://github.com/user-attachments/assets/5fb60c1d-78c8-4aad-8979-02965642fe58)

You can also create your own dashboards using customized PromQL. A collection of useful prometheus alert rules can be found at [Awesome Prometheus Alerts](https://github.com/asifMuzammil/awesome-prometheus-alerts).

## Add persistence

Currently data in Prometheus is not persistent. If we reboot the k8s servers. we will lose the exsiting performance metrics data. To avoid this situation, we need to mount a persistent storage to Prometheus.

We first scratch a `StorageClass` for grafana in `prometheus-sc.yaml`, and use `kubectl apply -f prometheus-sc.yaml` to create it in the k8s cluster.

*Here we use seaweedfs as the storage component, and assume you have already had the seaweedfs-csi-driver in your cluster. You can use NFS, or other storage as your choice. For more about the storage in k8s, please refer to [chapter 11: persistence](https://github.com/lyudmilalala/k8s_learn/tree/master/chapter_11_persistence).*

Then we bind the existing grafana release to this `StorageClass`.  We modify the `persistence` section in `prometheus-values.yaml` to below:

```yaml
server:
  persistentVolume:
      enabled: false
      storageClass: "prometheus-sc"
      size: 10Gi
```

If you want to discard the outdated logs, add the `server.retention` config.

```yaml
server:
    retention: "2d"
```

To rolling outdated presistent data to avoid running out of disk space...

We upgrade our release with the new configuration file.

```shell
helm upgrade prometheus ./prometheus-27.5.1.tgz -n monitor --values prometheus-values.yaml
```

We can see a pv and a pvc have been dynamically created for Prometheus. Now even when rebooting your k8s server now, the performance metrics data will not be lost.

```shell
$ kubectl get pv
pvc-e8e26372-23e8-4b0a-95f2-3007f57a903e   10Gi       RWO            Retain           Bound    monitor/prometheus-server   prometheus-sc            4m8s
$ kubectl get pvc -n monitor
prometheus-server   Bound    pvc-e8e26372-23e8-4b0a-95f2-3007f57a903e   10Gi       RWO            prometheus-sc   4m35s
```

Instead of binding to a `StorageClass`, you can also choose to bind your Prometheus to a specific existing pvc as below.

```yaml
server:
  persistentVolume:
      enabled: false
#   comment the storageClassName line
#   storageClass: "prometheus-sc"
      existingClaim: "prometheus-pvc"
#   you can even include a subPath
      subPath: /prometheus
      size: 10Gi
```

**References**

[A tutorial about bind to pvc](https://medium.com/@gayatripawar401/deploy-prometheus-and-grafana-on-kubernetes-using-helm-5aa9d4fbae66)

[Another tutorial](https://medium.com/@akilblanchard09/monitoring-a-kubernetes-cluster-using-prometheus-and-grafana-8e0f21805ea9)

## Uninstall

If you want to uninstall prometheus. Run `helm uninstall prometheus -n monitor`

## Collect server node metrics by Prometheus and show them on Grafana

For collecting server metrics, you need the tool **Node Exporter**.

Prometheus on K8s automatically creates a node exporter deamon set, which ensures a node exporter pod is deployed on each K8s node. Thus if you just want to monitor servers in the K8s cluster, directly go for importing aashboard No. 1860. You will see a comprehensive dashboard as below.

![image](https://github.com/user-attachments/assets/3f8a25dc-6ae5-4b08-8bdb-cf07829bbc34)

If you also want to monitor some servers outside the K8s cluster, install **Node Exporter** on each of these server. Ensure `/usr/local/bin` is in your `$PATH`.

```shell
$ wget https://github.com/prometheus/node_exporter/releases/download/v1.8.1/node_exporter-1.8.1.linux-amd64.tar.gz
$ tar xvf node_exporter-*.tar.gz
$ chown root:root node_exporter-1.8.1.linux-amd64/node_exporter 
$ cp node_exporter-1.8.1.linux-amd64/node_exporter /usr/local/bin
$ node_exporter --version
node_exporter, version 1.8.1 (branch: HEAD, revision: 400c3979931613db930ea035f39ce7b377cdbb5b)
  build user:       root@7afbff271a3f
  build date:       20240521-18:36:22
  go version:       go1.22.3
  platform:         linux/amd64
  tags:             unknown
```

Then create a systemd service for the node exporter, and start it as below.

```shell
$ cat <<EOF | sudo tee /etc/systemd/system/node-exporter.service
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
ExecStart=/usr/local/bin/node_exporter \
  --web.listen-address=:9100 \
  --collector.systemd \
  --collector.filesystem.ignored-mount-points="^/(sys|proc|dev|run)($|/)" 

Restart=always

[Install]
WantedBy=multi-user.target
EOF
$ sudo useradd -rs /bin/false node_exporter
$ sudo systemctl daemon-reload
$ sudo systemctl enable node-exporter
$ sudo systemctl start node-exporter
```

Test whether it works properly.

```shell
curl -s http://localhost:9100/metrics | grep node_
```

Update the Prometheus `values.yaml`, add the config below

```yaml
extraScrapeConfigs: |
  - job_name: 'external-nodes'
      static_configs:
        - targets:
            - '192.168.1.250:9100'
          labels:
            cluster: 'external'  
      relabel_configs:
        - source_labels: [__address__]
          regex: '([^:]+):\d+'
          target_label: 'instance'
          replacement: '$1'
          action: replace
```

Upgrade the Prometheus helm release in the K8s cluster.

```shell
helm upgrade prometheus ./prometheus-27.5.1.tgz --values prometheus-values.yaml -n monitor
```

Visit `http://$NODE_IP:30101/targets` in browser to ensure it has a tab called **external-nodes**.

![image](https://github.com/user-attachments/assets/d4ec49ed-0e15-40c3-a6e6-72fea3a032a9)

Then return back to the grafana dashboard No. 1860, change the job to **external-nodes** and you should be able to see data of the new external server.

![image](https://github.com/user-attachments/assets/5da01dbe-6f9e-4765-9150-5d5a1a82f220)

## Collect MySQL server metrics by Prometheus and show them on Grafana

For collecting server metrics, you need the tool **MySQL Exporter**, install **MySQL Exporter** on each of your host with a mysql server. Ensure `/usr/local/bin` is in your `$PATH`.

```shell
$  wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.15.0/mysqld_exporter-0.15.0.linux-amd64.tar.gz
$ tar xvf mysqld_exporter-*.tar.gz
$ chown root:root mysqld_exporter-0.15.0.linux-amd64/mysqld_exporter
$ cp mysqld_exporter-0.15.0.linux-amd64/mysqld_exporter /usr/local/bin
$ mysqld_exporter --version
mysqld_exporter, version 0.15.0 (branch: HEAD, revision: 6ca2a42f97f3403c7788ff4f374430aa267a6b6b)
  build user:       root@c4fca471a5b1
  build date:       20230624-04:09:04
  go version:       go1.20.5
  platform:         linux/amd64
  tags:             netgo
```

Create a MySQL user with enough permission.

```sql
CREATE USER 'replica'@'localhost' IDENTIFIED BY 'YourSecurePassword123!' WITH MAX_USER_CONNECTIONS 3;
grant process, replication slave, replication client, select on  *.* to 'replica'@'%' with grant option;
FLUSH PRIVILEGES;
```

Create a `.my.cnf` file at the current directory, put your mysql user name and password in there.

```shell
$ echo '[client]
user=replica
password=YourSecurePassword123!' > .my.cnf
```

Then create a systemd service for the node exporter, and start it as below.

```shell
$ cat <<EOF | sudo tee /etc/systemd/system/mysql-exporter.service
[Unit]
Description=MySQL Prometheus Exporter
After=network.target

[Service]
User=mysql
Group=mysql
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/mysqld_exporter \
  --config.my-cnf=$(pwd)/.my.cnf \
  --collect.info_schema.processlist \
  --collect.info_schema.innodb_metrics \
  --collect.perf_schema.eventsstatements \
  --collect.perf_schema.eventswaits \
  --collect.perf_schema.indexiowaits \
  --collect.perf_schema.tableiowaits \
  --collect.slave_status

Restart=always

[Install]
WantedBy=multi-user.target
EOF
$ sudo systemctl daemon-reload
$ sudo systemctl enable mysql-exporter
$ sudo systemctl start mysql-exporter
```

Test whether it works properly.

```shell
$ curl -s http://localhost:9104/metrics | grep 'mysql_up'
# Check for slave connection info
$ curl -s http://localhost:9104/metrics | grep 'mysql_slave_status_slave'
```

Update the Prometheus `values.yaml`, add the config below

```yaml
extraScrapeConfigs: |
  - job_name: 'mysql-master'
    static_configs:
      - targets: ['192.168.1.248:9104']
        labels:
          instance: mysql-master
          role: master
  - job_name: 'mysql-slave'
    static_configs:
      - targets: ['192.168.1.249:9104']
        labels:
          instance: mysql-slave
          role: slave
```

Upgrade the Prometheus helm release in the K8s cluster.

```shell
helm upgrade prometheus ./prometheus-27.5.1.tgz --values prometheus-values.yaml -n monitor
```

Visit `http://$NODE_IP:30101/targets` in browser to ensure it has a tab called **mysql-master** and another tabl called **mysql-slave**.

![image](https://github.com/user-attachments/assets/7d9a8817-eda1-40d9-ac83-7c79a2f8afdb)

Add dashboard No. 7362 to Grafana, then you can see MySQL dashbaord as below.

![image](https://github.com/user-attachments/assets/2583b2ce-17f3-46c5-a6f4-157f6a46e71b)

Based on your Prometheus configuration and directory structure, let me explain the contents and retention behavior:

## Directory Structure Explanation

Each directory with the format `01Kxxxxxx` represents a **TSDB block** containing time-series data for a specific time range:

- **chunks/**: Contains compressed time-series data files (000001, 000002, etc.)
- **index**: Index file for fast querying of the time-series data
- **meta.json**: Metadata about the block including time range, stats, and compaction level
- **tombstones**: Records of deleted time-series data
- **wal/**: Write-ahead log containing recent data not yet committed to blocks
- **chunks_head**: Head chunks containing the most recent data

## Answers to Your Questions

### 1. Automatic Deletion with 90d Retention

Yes, files will be automatically deleted after 90 days. Specifically:

- **Complete TSDB blocks** older than 90 days will be deleted entirely
- This includes the entire directory structure: chunks/, index, meta.json, and tombstones
- Blocks are deleted when their entire time range is older than the retention period
- The WAL and head chunks are not subject to the 90d retention as they contain recent data

The retention works at the block level - if a block's time range is completely outside the 90-day window, the entire block directory gets removed.

### 2. Manual Deletion Methods

Yes, you can manually delete data:

**Method A: Using Prometheus Admin API**
```bash
# Delete data for specific series
curl -X POST \
  -g 'http://192.168.9.116:30103/api/v1/admin/tsdb/delete_series?match[]={job=~".+"}&start=2024-01-01T00:00:00Z&end=2024-02-01T00:00:00Z'

# Clean up the tombstones after deletion
curl -X POST \
  http://192.168.9.116:30103/api/v1/admin/tsdb/clean_tombstones
```

**Method B: Direct File System Deletion (NOT recommended)**
Manually delete entire block directories, but this requires Prometheus restart and can cause issues.

**Method C: Reduce Retention Temporarily**
Change retention to a shorter period, restart Prometheus, then change it back.

### 3. Safe Files for Deletion

For safe operation with Prometheus+Grafana:

**Safe to Delete:**
- Complete TSDB block directories (01Kxxxxxx) that are older than your required data period
- Individual tombstone files after cleaning with the API

**Never Delete:**
- **wal/** directory - contains recent unwritten data
- **chunks_head/** directory - contains current head chunks
- **lock** file - prevents concurrent access issues
- **queries.active** - tracks active queries
- Any block that contains data within your retention period that you still need

## Recommendations

1. **Use the Admin API** for safe data deletion rather than direct file manipulation
2. **Monitor disk usage** with your existing Prometheus setup
3. **Test retention behavior** by temporarily setting a shorter retention period to verify it works as expected
4. **Backup critical data** before any manual deletion operations

## Example Cleanup Script (Use with Caution)
```bash
# Check current disk usage
kubectl exec -it prometheus-server-0 -n monitor -- du -sh /data

# Use Admin API for safe deletion instead of direct file manipulation
```

The key is to let Prometheus handle retention automatically through its built-in mechanisms rather than manual file deletion to avoid data corruption or service interruption.

Based on your Prometheus configuration and the development log showing your experience with monitoring systems, let me explain how Prometheus works and how it interacts with Loki for log storage and retrieval.

## Prometheus Architecture and Data Storage

### TSDB (Time Series Database) Structure

Prometheus uses a custom TSDB with the following structure:

1. **WAL (Write-Ahead Log)**
   - Stores recent data that hasn't been committed to persistent blocks yet
   - Located in the `wal/` directory with segment files (00000378, 00000379, etc.)
   - Provides durability in case of crashes
   - Checkpoint directories contain consolidated WAL data

2. **Blocks**
   - Time-partitioned data stored in directories like `01K05JP5W5X447HNQT54DWE4XP`
   - Each block contains:
     - `chunks/`: Compressed time series samples
     - `index`: Index for fast querying
     - `meta.json`: Block metadata including time range
     - `tombstones`: Deleted data records

3. **Data Flow**
   ```
   Incoming Metrics → WAL (in-memory) → WAL Files → Blocks (every 2h) → Retention Cleanup
   ```

### WAL and TSDB Operation

When Prometheus collects metrics:

1. **Write Process**:
   - Data first written to in-memory WAL buffer
   - Flushed to WAL files on disk
   - Periodically compacted into blocks (every 2 hours)
   - Head chunks (`chunks_head/`) store most recent data

2. **Read Process**:
   - Queries check both recent data (WAL/head chunks) and historical data (blocks)
   - Index files enable fast lookups by labels and time ranges
   - Tombstones mark deleted data

## Loki Log Storage and Retrieval

Based on your development log showing Loki experience, here's how Loki works:

### Log Storage Structure

Loki uses a similar approach but for logs:

1. **Log Streams**:
   - Logs grouped into streams by labels (job, instance, etc.)
   - Each stream stored as chunks in object storage or filesystem

2. **Index**:
   - Stores label pairs and references to chunks
   - Enables fast lookup of relevant chunks for queries

3. **Data Flow**:
   ```
   Logs → Distributor → Ingester (WAL) → Chunk Storage → Compaction
   ```

### Query Process for Log Retrieval

When you query logs in Grafana for a specific time period:

1. **Query Parsing**:
   ```
   {job="mysql-servers"} |= "error" | timestamp >= "2023-01-01" <= "2023-01-02"
   ```

2. **Index Lookup**:
   - Loki queries its index for streams matching the label selector (`job="mysql-servers"`)
   - Returns list of chunks that may contain relevant logs

3. **Chunk Filtering**:
   - Filters chunks based on time range
   - Eliminates chunks that don't overlap with query time period

4. **Log Retrieval**:
   - Loads relevant chunks from storage
   - Applies additional filters (e.g., `|= "error"`)
   - Returns results to Grafana

5. **Result Processing**:
   - Results sorted by timestamp
   - Formatted according to Grafana panel requirements

## Integration with Your Setup

Based on your configuration:

1. **Prometheus Metrics Collection**:
   - Scrapes MySQL servers every 30s
   - Stores metrics with 90-day retention
   - Accessible via NodePort 30103

2. **Loki Integration**:
   - Likely configured as a separate service (as seen in your development log)
   - Grafana connects to both Prometheus (metrics) and Loki (logs)
   - Correlation possible through shared labels

## Performance Considerations

1. **Prometheus**:
   - Blocks are immutable, optimized for reads
   - WAL ensures no data loss during crashes
   - Retention policy automatically cleans old data

2. **Loki**:
   - Uses log labels efficiently for indexing
   - Avoids indexing log content (unlike traditional logging systems)
   - Horizontal scaling through multiple ingesters

When you query logs in Grafana, Loki efficiently locates the relevant log chunks through its label-based index, filters by time range, and returns the matching log entries without needing to scan through all stored logs.

Great question! Let me explain the WAL (Write-Ahead Log) data format and storage mechanism in both Loki and Prometheus.

# What is WAL (Write-Ahead Log)

WAL stands for Write-Ahead Log. It's a log-like structure that stores all the data points that Prometheus receives. It's a way to ensure that data is not lost in case of a crash or other unexpected shutdown.

## WAL in Prometheus

### Physical Storage
- **Location**: Stored on disk as binary files in the `wal/` directory
- **Not in memory**: While there's an in-memory buffer for performance, the WAL is primarily a disk-based persistence mechanism
- **Not in TSDB blocks**: WAL is separate from TSDB blocks - it's a temporary storage before data is compacted into blocks

### Data Format
The WAL uses a **binary format**, not JSON. It consists of:

1. **Segments**: Sequential numbered files (00000000, 00000001, etc.)
2. **Records**: Each segment contains a series of records with this structure:
   ```
   +------------------------------------+
   | Length (4 bytes)                   |
   +------------------------------------+
   | CRC32 Checksum (4 bytes)           |
   +------------------------------------+
   | Data (variable length)             |
   +------------------------------------+
   ```

3. **Record Types**:
   - **Series records**: Store metric metadata (labels)
   - **Samples records**: Store actual metric values with timestamps
   - **Tombstone records**: Mark deleted time series
   - **Exemplar records**: Store exemplar data (tracing information)

### Example WAL Content Structure
```bash
# WAL directory structure
wal/
├── 00000000          # Segment file
├── 00000001          # Next segment
├── checkpoint.000001 # Checkpoint (compacted WAL)
└── checkpoint.000002
```

The binary format is optimized for:
- Fast sequential writing
- Efficient crash recovery
- Compact storage

## WAL in Loki

### Physical Storage
- **Location**: Stored on disk in the `wal/` directory
- **Also disk-based**: Like Prometheus, primarily stored on disk for durability
- **Separate from chunks**: WAL is temporary storage before logs are flushed to chunk storage

### Data Format
Loki's WAL also uses a **binary format**, not JSON:

1. **Segments**: Sequential numbered files
2. **Entries**: Each entry contains:
   - Stream labels
   - Log line content
   - Timestamp
   - Additional metadata

### Example WAL Structure in Loki
```bash
# Loki WAL directory
wal/
├── 00007060          # WAL segment
├── 00007061          # Next segment
└── checkpoint.007059 # Checkpoint
```

## Key Differences Between Prometheus and Loki WAL

| Aspect | Prometheus WAL | Loki WAL |
|--------|----------------|----------|
| **Purpose** | Store time-series metrics temporarily | Store log entries temporarily |
| **Data Type** | Numeric samples with timestamps | Text log lines with metadata |
| **Label Handling** | Series records store metric labels | Stream labels associated with log entries |
| **Format** | Binary format optimized for metrics | Binary format optimized for logs |
| **Compaction** | Checkpoints created periodically | Checkpoints for flushed data |

## WAL Processing Flow

### Prometheus Flow:
```
1. Metrics received → 
2. Written to in-memory buffer → 
3. Flushed to WAL segment files → 
4. Processed and stored in memory (head chunks) → 
5. Compacted into TSDB blocks every 2 hours → 
6. WAL segments deleted after compaction
```

### Loki Flow:
```
1. Log entries received → 
2. Written to in-memory buffer → 
3. Flushed to WAL segment files → 
4. Batched and compressed into chunks → 
5. Chunks uploaded to storage → 
6. WAL segments deleted after successful upload
```

## Why Binary Format Instead of JSON?

1. **Performance**: Binary format is much faster to write and parse
2. **Space Efficiency**: Significantly smaller than text-based formats
3. **Reliability**: Structured format with checksums prevents corruption
4. **Streaming**: Efficient for sequential reading during recovery

## WAL Recovery Process

When Prometheus/Loki restarts:

1. **Read WAL segments**: Sequentially read all segment files
2. **Reconstruct state**: Rebuild in-memory state from WAL records
3. **Continue operation**: Resume normal operation with recovered data

This ensures no data loss even in case of unexpected shutdowns.

## Summary

- **WAL is disk-based**, not memory-only
- **Uses binary format**, not JSON
- **Stored separately** from TSDB (Prometheus) or chunk storage (Loki)
- **Optimized for durability and performance**
- **Automatically managed** by the system with periodic cleanup

The binary format is specifically designed for the high-throughput, reliable storage needs of time-series data and logs, making it much more efficient than text-based formats like JSON.