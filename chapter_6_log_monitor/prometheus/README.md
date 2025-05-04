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

## View metrics in Prometheus

First add Loki as a data source in your Grafana.

From the home page, visit connection -> data source -> Add

Then visit the [Grafana Dashboard](https://grafana.com/grafana/dashboards/) website to search for a desired dashboard.

Some useful dashboards are

- 12740 - Kubernetes monitoring dashboard
- 15282 - Kubernetes cluster monitoring

Here we choose dashboard No. 12740 as an example. Click into its detail, and copy its dashboard ID.

![Copy Id from the Dashboard Detail](https://github.com/user-attachments/assets/b5d3cf71-1f12-4a3a-a035-ecc8b8ad5405)

Go back to your Grafana, choose Create -> Import, and then fill in the dashboard ID in the shown up page. 

![Initialize Dashboard Configuration 1](https://github.com/user-attachments/assets/be6d45ba-ba3a-4810-8ae4-5ec152d9fe70)

Continue for more configuration, choose Loki to be the data source.

![Initialize Dashboard Configuration 1](https://github.com/user-attachments/assets/01dd9ac1-ffb8-4b3e-960f-fcee20e0ca41)

Then you will see the dashboard shown up.

![New Dashboard](https://github.com/user-attachments/assets/72c88c5b-7703-4f34-a7d2-c17925c4ae96)

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
