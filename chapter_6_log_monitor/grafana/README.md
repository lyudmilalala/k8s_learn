## Official documentations

[Helm repo of Grafana](https://artifacthub.io/packages/helm/grafana/grafana)

[Helm chart source of Grafana](https://github.com/grafana/helm-charts/tree/main/charts/grafana)

[Docs for configuring default data sources and dashboards](https://grafana.com/docs/grafana/latest/administration/provisioning/#datasources)

## Install a Grafana release

In this instruction, we use grafana helm chart version 8.8.2. A copy of the source code is attached for reference.

Before pulling resource, you need to add the grafana repository.

```shell
$ helm repo add grafana https://grafana.github.io/helm-charts 
$ helm repo update
```

Also, if you have difficulties pulling docker images from the official repositories, use the following substitutions.

```shell
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/grafana:11.4.0
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/grafana/grafana:11.4.0  docker.io/grafana/grafana:11.4.0
# need for mount to pvc, if not mount to a volume, no need to pull it
$ docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/curlimages/curl:8.9.1
$ docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/curlimages/curl:8.9.1  docker.io/curlimages/curl:8.9.1
```

Install Grafana to the K8s cluster.

```shell
helm install grafana ./grafana-8.8.2.tgz -n monitor --create-namespace --set service.type=NodePort --set service.port=3000 --set service.nodePort=30101
```

Here we already download the helm chart to local, so we install it as `helm install grafana ./grafana-8.8.2.tgz`. You can directly install the remote chart as `helm install grafana grafana/grafana`.

We add service configuration in the install command, in order to directly visit the dashboard by a port on node.

Result will be something like this 

```shell
NAME: grafana
LAST DEPLOYED: Sat May  3 16:08:07 2025
NAMESPACE: monitor
STATUS: deployed
REVISION: 1
NOTES:
1. Get your 'admin' user password by running:

   kubectl get secret --namespace monitor grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo


2. The Grafana server can be accessed via port 3000 on the following DNS name from within your cluster:

   grafana.monitor.svc.cluster.local

   Get the Grafana URL to visit by running these commands in the same shell:
     export NODE_PORT=$(kubectl get --namespace monitor -o jsonpath="{.spec.ports[0].nodePort}" services grafana)
     export NODE_IP=$(kubectl get nodes --namespace monitor -o jsonpath="{.items[0].status.addresses[0].address}")
     echo http://$NODE_IP:$NODE_PORT

3. Login with the password from step 1 and the username: admin
#################################################################################
######   WARNING: Persistence is disabled!!! You will lose your data when   #####
######            the Grafana pod is terminated.                            #####
#################################################################################
```

And a k8s pod and a k8s service has been created.

```shell
$ kubectl get pods -n monitor
NAME                       READY   STATUS    RESTARTS   AGE
grafana-7c5fb9f8fc-gkbdh   1/1     Running   0          2m19s
$ kubectl get svc -n monitor
NAME      TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
grafana   NodePort   10.109.24.249   <none>        3000:30101/TCP   2m25s
```

Then we can access the Grafana dashboard by `<node_ip>:30101`.

If you forget to set up the NodePort service when installing, you can expose the exsiting ClusterIP service later like this.

```shell
kubectl expose service grafana -n monitor --type=NodePort --target-port=80 --port=30101 --name=grafana-ext
```

Username is `admin`. Password is got by `kubectl get secret --namespace monitor grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo`.

*If you use Windows Powershell, get poassword by `[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(<secret_val>))`.*

![Grafana Login Page](https://github.com/user-attachments/assets/d8307bc4-15ef-482a-983b-9b731d84c4e3)

![Grafana Home Pag](https://github.com/user-attachments/assets/c02f3d67-5137-48b5-a6c9-00155a3f3828)

## Add persistence

Currently data in grafana is not persistent. If we add some dashboards to grafana, and then reboot the k8s servers. The dashboards we just added will disappear.

To avoid this situation, we need to mount a persistent storage to grafana.

To achieve this target, we first scratch a `StorageClass` for grafana in `grafana-sc.yaml`, and use `kubectl apply -f grafana-sc.yaml` to create it in the k8s cluster.

*Here we use seaweedfs as the storage component, and assume you have already had the seaweedfs-csi-driver in your cluster. You can use NFS, or other storage as your choice. For more about the storage in k8s, please refer to [chapter 11: persistence](https://github.com/lyudmilalala/k8s_learn/tree/master/chapter_11_persistence).*

Then we bind the existing grafana release to this `StorageClass`. As the customized configuration becomes long, we summarize them into a self-defined `grafana-values.yaml`. For customized the storage, we modify the `persistence` section to below:

```yaml
persistence:
  type: pvc
  enabled: true
  storageClassName: grafana-sc
  size: 10Gi
```

Then we apply the configuration change to the existing grafana release (the change in `service` section is also included in `grafana-values.yaml`).

```shell
helm upgrade grafana ./grafana-8.8.2.tgz -n monitor --values grafana-values.yaml
```

We can see a pv and a pvc have been dynamically created for grafana. If you reboot your k8s server now, the dashboards you have already added to grafana will not be lost.

```shell
$ kubectl get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM             STORAGECLASS   REASON   AGE
pvc-65118c8c-6d79-442c-aacb-cefdd71bf15a   10Gi       RWO            Retain           Bound    monitor/grafana   grafana-sc              8s
$ kubectl get pvc -n monitor
NAME      STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
grafana   Bound    pvc-65118c8c-6d79-442c-aacb-cefdd71bf15a   10Gi       RWO            grafana-sc     18s
```

Instead of binding to a `StorageClass`, you can also choose to bind your grafana to a specific existing pvc as below.

```yaml
persistence:
  type: pvc
  enabled: true
#   comment the storageClassName line
#   storageClassName: grafana-sc
  size: 10Gi
#   you can even include a subPath
  subPath: "grafana"
  existingClaim: grafana-pvc
  accessModes:
    - ReadWriteOnce
```

## Initialize with dashboards and data sources

**You would better go through this section after you have learned to deploy Loki or Prometheus in your k8s cluster.**

If you want to initialize your grafana platform with specific datasources and dashboards, you should modify the `datasources` and `dashboards` in `grafana-values.yaml`.

**NOTICE**: To use  `dashboards`,  `dashboardProviders` should also be set.


## Edit the Dashboard in Grafana

**You would better go through this section after you have learned to deploy Loki or Prometheus in your k8s cluster.**

Here we take dashboard No.XXX as an example. It requires Prometheus as the data source. 

After create the dashboard, we can find out that the graph does not show the CPU usage of each pod as it announced. 

So we select the graph, right-click on it, and choose Edit to see what is wrong.

Here we can see the prometheus query (PromQL) used to draw this graph.

![Customize an element](https://github.com/user-attachments/assets/3243dfb8-c10a-4069-9352-cb11041f321c)

Simply change to the "podName" in the sentence by "pod", and you will see the CPU usage of all pods grouped by their names shows up.

## Uninstall

If you want to uninstall grafana. Run `helm uninstall grafana -n monitor`
