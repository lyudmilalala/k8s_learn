## 4.1

整体部署过程基本和流程一样，没什么好说的，贴一些查找表示跑起来了

网络插件之前试用`calico`启动失败过，换`flannel`后就好了，所以先这么用，`calico`可以慢慢再研究一下

```
$ kubectl get nodes
NAME            STATUS   ROLES                  AGE    VERSION
mila-master    Ready    control-plane,master   111m   v1.21.14
mila-worker1   Ready    <none>                 73m    v1.21.14
mila-worker2   Ready    <none>                 73m    v1.21.14
$ kubectl get pods -A       # on master
NAMESPACE     NAME                                   READY   STATUS             RESTARTS   AGE
kube-system   coredns-59d64cd4d4-7vvmf               1/1     Running            0          108m
kube-system   coredns-59d64cd4d4-qwqzj               1/1     Running            0          108m
kube-system   etcd-spinq-master                      1/1     Running            36         109m
kube-system   kube-apiserver-spinq-master            1/1     Running            36         108m
kube-system   kube-controller-manager-spinq-master   1/1     Running            24         109m
kube-system   kube-flannel-ds-ptlb7                  1/1     Running            0          105m
kube-system   kube-flannel-ds-wpr2p                  1/1     Running            0          71m
kube-system   kube-proxy-22h2k                       1/1     Running            0          108m
kube-system   kube-proxy-5m79w                       1/1     Running            0          71m
kube-system   kube-scheduler-spinq-master            1/1     Running            52         109m
$ kubectl get svc -A
NAMESPACE     NAME         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                  AGE
default       kubernetes   ClusterIP   10.96.0.1        <none>        443/TCP                  109m
kube-system   kube-dns     ClusterIP   10.96.0.10       <none>        53/UDP,53/TCP,9153/TCP   109m
$ kubectl get deploy -A
NAMESPACE     NAME      READY   UP-TO-DATE   AVAILABLE   AGE
kube-system   coredns   2/2     2            2           108m
```

## 4.2

根据教程指示生成`configmap`并部署`envoy`
```
$ kubectl create configmap envoy-config --from-file=envoy.yaml
configmap/envoy-config created
$ kubectl create -f envoy-deploy.yaml
deployment.apps/envoy created
$ kubectl get deploy -A
NAMESPACE     NAME      READY   UP-TO-DATE   AVAILABLE   AGE
default       envoy     1/1     1            1           8m20s
kube-system   coredns   2/2     2            2           128m
$ kubectl get pods -n default
NAME                    READY   STATUS    RESTARTS   AGE
envoy-fb5d77cc9-cpnwq   1/1     Running   0          18m
$ kubectl get rs -n default
NAME              DESIRED   CURRENT   READY   AGE
envoy-fb5d77cc9   1         1         1       18m
```

暴露服务

```
$ kubectl expose deploy envoy --selector run=envoy --port=10000 --type=NodePort
service/envoy exposed
$ kubectl get svc -A
NAMESPACE     NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                  AGE
default       envoy        NodePort    10.108.101.95   <none>        10000:32150/TCP          4s
default       kubernetes   ClusterIP   10.96.0.1        <none>        443/TCP                  133m
kube-system   kube-dns     ClusterIP   10.96.0.10       <none>        53/UDP,53/TCP,9153/TCP   133m
$ curl localhost:32150
no healthy upstream
```

尝试扩容

```
$ kubectl scale deploy envoy --replicas=3
deployment.apps/envoy scaled
$ kubectl get pod -n default
NAME                    READY   STATUS              RESTARTS   AGE
envoy-fb5d77cc9-8wh2j   0/1     ContainerCreating   0          49s
envoy-fb5d77cc9-bz6qr   1/1     Running             0          49s
envoy-fb5d77cc9-cpnwq   1/1     Running             0          11m
$ kubectl get deploy -n default
NAMESPACE     NAME      READY   UP-TO-DATE   AVAILABLE   AGE
default       envoy     2/3     3            2           11m
# wait for a while
$ kubectl get pod -n default
NAME                    READY   STATUS    RESTARTS   AGE
envoy-fb5d77cc9-8wh2j   1/1     Running   0          2m7s
envoy-fb5d77cc9-bz6qr   1/1     Running   0          2m7s
envoy-fb5d77cc9-cpnwq   1/1     Running   0          13m
$ kubectl get deploy -n default
NAMESPACE     NAME      READY   UP-TO-DATE   AVAILABLE   AGE
default       envoy     3/3     3            3           13m
$ kubectl get rs -n default
NAME              DESIRED   CURRENT   READY   AGE
envoy-fb5d77cc9   3         3         3       13m
```

如果直接删除`deployment`里的`pod`或`ReplicaSet`，k8s会自动重新添加

```
$ kubectl delete pod envoy-fb5d77cc9-8wh2j
pod "envoy-fb5d77cc9-8wh2j" deleted
$ kubectl get pod -n default
NAME                    READY   STATUS              RESTARTS   AGE
envoy-fb5d77cc9-bz6qr   1/1     Running             0          6m4s
envoy-fb5d77cc9-cpnwq   1/1     Running             0          6m4s
envoy-fb5d77cc9-m9tjj   0/1     ContainerCreating   0          4s
$ kubectl delete rs envoy-fb5d77cc9
replicaset.apps "envoy-fb5d77cc9" deleted
$ kubectl get rs -n default
NAME              DESIRED   CURRENT   READY   AGE
envoy-fb5d77cc9   3         3         0       3s
$ kubectl get pod -n default
NAME                    READY   STATUS              RESTARTS   AGE
envoy-fb5d77cc9-bnrd8   0/1     ContainerCreating   0          10s
envoy-fb5d77cc9-tlv92   0/1     ContainerCreating   0          10s
envoy-fb5d77cc9-wthhk   0/1     ContainerCreating   0          10s
```

删除资源

```
$ kubectl delete svc envoy
service "envoy" deleted
$ kubectl get svc -A
NAMESPACE     NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
default       kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP                  148m
kube-system   kube-dns     ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   148m
$ kubectl delete deploy envoy
deployment.apps "envoy" deleted
$ kubectl get deploy -A
NAMESPACE     NAME      READY   UP-TO-DATE   AVAILABLE   AGE
kube-system   coredns   2/2     2            2           148m
```

修改`envoy.yaml`里的端口

```yaml
static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address: { address: 0.0.0.0, port_value: 10050 }
```

同时还修改了`envoy-deploy.yaml`里的`replicas`做更多尝试

```yaml
spec:
  replicas: 3
  selector:
    matchLabels:
      run: envoy
```

删除并重建configmap

```
$ kubectl delete cm envoy-config
configmap "envoy-config" deleted
$ kubectl create configmap envoy-config --from-file=envoy.yaml
configmap/envoy-config created
```

重新部署集群并暴露服务

```
$ kubectl create -f envoy-deploy.yaml
deployment.apps/envoy created
$ kubectl expose deploy envoy --selector run=envoy --port=10050 --type=NodePort
service/envoy exposed
$ kubectl get deploy -n default
NAME    READY   UP-TO-DATE   AVAILABLE   AGE
envoy   2/3     3            3           84s
$ kubectl get pod -n default
NAME                    READY   STATUS    RESTARTS   AGE
envoy-fb5d77cc9-4kc8h   1/1     Running   0          100s
envoy-fb5d77cc9-m9tjj   1/1     Running   0          100s
envoy-fb5d77cc9-qlk5v   1/1     Running   0          100s
$ kubectl get rs -n default
NAME              DESIRED   CURRENT   READY   AGE
envoy-fb5d77cc9   3         3         3       100s
$ kubectl get svc
NAME         TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)           AGE
envoy        NodePort    10.97.17.51   <none>        10050:31504/TCP   86s
kubernetes   ClusterIP   10.96.0.1     <none>        443/TCP           12d
$ curl localhost:31504
no healthy upstream
```

