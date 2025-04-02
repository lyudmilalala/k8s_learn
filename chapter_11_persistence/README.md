## Presistence

### Prepare a test application

Create a test flask app `app.py` with a write file function, a read file function, and a list file function.

Build it as usual, `docker build -t crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/storage-app:1.0.0 .`

Test it locally, use `-v` to bind to a local directory.

```shell
docker run -d -p 8080:8080 -v "D:\projects\k8s_learn\chapter_11_persistence\tmp:/opt" --name storage-app1 crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/storage-app:1.0.0
```

Some test samples.

```shell
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test1.txt", "content": "Hello, World!"}' http://192.168.1.4:8080/write
{"message": "File test1.txt written successfully"}
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test2.txt", "content": "Good morning!"}' http://192.168.1.4:8080/write
{"message": "File test2.txt written successfully"}
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test3.txt", "content": "Good evening!"}' http://192.168.1.4:8080/write
{"message": "File test2.txt written successfully"}
$ curl http://localhost:8080/list
{
  "files": [
    "test.txt",
    "test2.txt",
    "test3.txt"
  ]
}
$ curl http://localhost:8080/read?filename=test2.txt
{
  "content": "Good morning!",
  "filepath": "/opt/test2.txt"
}
```

Push the image do your repository.

```shell
docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/storage-app:1.0.0
```

### Use NFS as the Storage

Install a NFS server on an extra server with IP `192.168.1.250`.

```shell
sudo apt-get install -y nfs-kernel-server
```

Config a shared file and reload the NFS server.

```shell
$ echo "/data/nfs 192.168.1.0/24(rw,sync,no_root_squash,no_subtree_check)" >> /etc/exports
$ sudo systemctl restart nfs-kernel-server
$ sudo exportfs -ra
$ sudo systemctl enable nfs-kernel-server
```

Install NFS client on echo node in the K8s cluster, and test remote directory connection.

```shell
$ sudo apt-get install -y nfs-common
$ showmount -e 192.168.1.250
Export list for 192.168.1.250:
/data/nfs 192.168.1.0/24
```

```shell
$ kubectl apply -f nfs-storage.yaml
storageclass.storage.k8s.io/nfs-sc created
persistentvolume/nfs-pv created
$ kubectl get sc
NAME     PROVISIONER                                   RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
nfs-sc   k8s-sigs.io/nfs-subdir-external-provisioner   Retain          Immediate           false     
$ kubectl get pv
NAME     CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   REASON   AGE
nfs-pv   3Gi        RWX            Retain           Available           nfs-sc                  2m21s
```

```shell
$ kubectl apply -f nfs-app-deployment.yaml
$ kubectl get pv
NAME     CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                     STORAGECLASS   REASON   AGE
nfs-pv   3Gi        RWX            Retain           Bound    storage-demo-ns/nfs-pvc   nfs-sc                  7m41s
$ kubectl get pvc -n storage-demo-ns
NAME      STATUS   VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
nfs-pvc   Bound    nfs-pv   3Gi        RWX            nfs-sc         24m
$ kubectl get pod -n storage-demo-ns
NAME                                   READY   STATUS    RESTARTS   AGE
storage-demo-deploy-784fdf68bf-jgmt8   1/1     Running   0          34m
storage-demo-deploy-784fdf68bf-n7ct4   1/1     Running   0          34m
storage-demo-deploy-784fdf68bf-wzkch   1/1     Running   0          34m
```

Do some tests, and if you see the logs of the pods, you can see that, files are written and read by different pods, but each pod can see the contents in the shared volume `/data/nfs`.

```shell
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test1.txt", "content": "Hello, World!"}' http://192.168.1.248:30090/write
{"message": "File test1.txt written successfully"}
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test2.txt", "content": "Good morning!"}' http://192.168.1.248:30090/write
{"message": "File test2.txt written successfully"}
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test3.txt", "content": "Good evening!"}' http://192.168.1.248:30090/write
{"message": "File test2.txt written successfully"}
$ curl 192.168.1.248:30090/list
{
  "files": [
    "test.txt",
    "test2.txt",
    "test3.txt"
  ]
}
$ curl http://192.168.1.248:30090/read?filename=test2.txt
{
  "content": "Good morning!",
  "filepath": "/opt/test2.txt"
}
```

### Use SeaweedFS as the Storage

#### Install SeaweedFS on an extra server

In this example, storage server has IP `192.168.1.250`. We deploy a one master, one volume, one filer system in this demo. The master server listens to port `9333`. The volume server listens to port `8081`. The filer server listens to port `7333`. 

Put the three files in directory `seaweedfs-svc` into `/etc/systemd/system`. Then enable and start them.

#### Install seaweedfs-csi-driver

On our K8s cluster, install `seaweedfs-csi-driver`.

```shell
$ git clone git@github.com:seaweedfs/seaweedfs-csi-driver.git
$ helm install --set seaweedfsFiler=192.168.1.250:7333 seaweedfs-csi-driver ./seaweedfs-csi-driver/deploy/helm/seaweedfs-csi-driver
```

As usual, if you fail to pull down some of the official images, here is a substitution solution.

As swr does not accept the label "latest", we may need to grab `chrislusf/seaweedfs-csi-driver:latest` through VPN by our own.

```shell
$ docker tag chrislusf/seaweedfs-csi-driver:latest crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/seaweedfs-csi-driver:latest
$ docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/seaweedfs-csi-driver:latest
$ docker tag crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/seaweedfs-csi-driver:latest chrislusf/seaweedfs-csi-driver:latest
```

#### Create PV and PVC

PV and PVC are one to one mapped.

Create PV and PVC that binds to this specific PV as below.

```shell
$ kubectl apply -f seaweedfs-pvc.yaml 
persistentvolume/seaweedfs-static created
persistentvolumeclaim/seaweedfs-pvc created
```

Verify that they are binded correctly.

```shell
$ kubectl get pv
NAME               CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                           STORAGECLASS   REASON   AGE
nfs-app-pv         5Gi        RWX            Retain           Bound       storage-demo-ns/nfs-pvc          nfs-sc                  4d2h
seaweedfs-static   3Gi        RWX            Retain           Bound       storage-demo-ns/seaweedfs-pvc                           9s
$ kubectl get pvc -n storage-demo-ns
NAME            STATUS   VOLUME             CAPACITY   ACCESS MODES   STORAGECLASS   AGE
seaweedfs-pvc   Bound    seaweedfs-static   3Gi        RWX                           36s
```

#### Mount PVC to the application pods

We only change the `volumes` part and the service node port of the deployment yaml.

It takes about 10s for the pods to be ready.

```shell
$  kubectl get pod -n storage-demo-ns
NAME                                   READY   STATUS    RESTARTS   AGE
storage-demo-deploy-746bc7f7b6-fd95k   1/1     Running   0          13s
storage-demo-deploy-746bc7f7b6-vthqm   1/1     Running   0          13s
storage-demo-deploy-746bc7f7b6-xvhzv   1/1     Running   0          13s
```

For the first time a pod mount to a pv, a pv directory will be created on the k8s worker at path ``.

Logs similar as below will be generated by this event. You can use they for debugging.

Logs generated by pod `seaweedfs-csi-driver-node`.

```
$ kubectl logs seaweedfs-csi-driver-node-q2xld -n default -c csi-seaweedfs-plugin 
I0402 03:16:53.992477 nodeserver.go:34 node stage volume dfs-test to /var/lib/kubelet/plugins/kubernetes.io/csi/pv/seaweedfs-monitor-pv1/globalmount
I0402 03:16:53.992577 mounter_seaweedfs.go:45 mounting [192.168.1.250:7333] /monitor to /var/lib/kubelet/plugins/kubernetes.io/csi/pv/seaweedfs-monitor-pv1/globalmount
W0402 03:16:53.992615 mounter_seaweedfs.go:139 VolumeContext 'path' ignored
I0402 03:16:53.992646 mounter.go:53 Mounting fuse with command: weed and args: [-logtostderr=true mount -dirAutoCreate=true -umask=000 -dir=/var/lib/kubelet/plugins/kubernetes.io/csi/pv/seaweedfs-monitor-pv1/globalmount -localSocket=/tmp/seaweedfs-mount-652315751.sock -cacheDir=/var/cache/seaweedfs/dfs-test -concurrentWriters=32 -collection=monitor -filer=192.168.1.250:7333 -replication=000 -filer.path=/monitor -cacheCapacityMB=0]
mount point owner uid=0 gid=0 mode=drwxrwxrwx
current uid=0 gid=0
I0402 03:16:54.032279 leveldb_store.go:47 filer store dir: /var/cache/seaweedfs/dfs-test/3925d786/meta
I0402 03:16:54.032318 file_util.go:27 Folder /var/cache/seaweedfs/dfs-test/3925d786/meta Permission: -rwxr-xr-x
I0402 03:16:54.042115 mount_std.go:282 mounted 192.168.1.250:7333/monitor to /var/lib/kubelet/plugins/kubernetes.io/csi/pv/seaweedfs-monitor-pv1/globalmount
I0402 03:16:54.042148 mount_std.go:283 This is SeaweedFS version 30GB 3.85  linux amd64
I0402 03:16:54.055948 nodeserver.go:92 orchestration system is not compatible with the k8s api, error is: persistentvolumes "dfs-test" not found
I0402 03:16:54.055989 nodeserver.go:96 volume dfs-test successfully staged to /var/lib/kubelet/plugins/kubernetes.io/csi/pv/seaweedfs-monitor-pv1/globalmount
I0402 03:16:54.063632 nodeserver.go:106 node publish volume dfs-test to /var/lib/kubelet/pods/fe2c80bb-d237-413d-b4bb-b5afbef4a941/volumes/kubernetes.io~csi/seaweedfs-monitor-pv1/mount
I0402 03:16:54.065378 nodeserver.go:140 volume dfs-test successfully published to /var/lib/kubelet/pods/fe2c80bb-d237-413d-b4bb-b5afbef4a941/volumes/kubernetes.io~csi/seaweedfs-monitor-pv1/mount
I0402 03:16:54.085049 nodeserver.go:106 node publish volume dfs-test to /var/lib/kubelet/pods/99745b35-23ec-46ea-b6f6-b3ee340c4a45/volumes/kubernetes.io~csi/seaweedfs-monitor-pv1/mount
I0402 03:16:54.086869 nodeserver.go:140 volume dfs-test successfully published to /var/lib/kubelet/pods/99745b35-23ec-46ea-b6f6-b3ee340c4a45/volumes/kubernetes.io~csi/seaweedfs-monitor-pv1/mount
I0402 03:16:54.188058 nodeserver.go:106 node publish volume dfs-test to /var/lib/kubelet/pods/92823ff2-00b5-4c4e-8ca6-c40f92d739d0/volumes/kubernetes.io~csi/seaweedfs-monitor-pv1/mount
I0402 03:16:54.189704 nodeserver.go:140 volume dfs-test successfully published to /var/lib/kubelet/pods/92823ff2-00b5-4c4e-8ca6-c40f92d739d0/volumes/kubernetes.io~csi/seaweedfs-monitor-pv1/mount
```

Logs generated by kubelet on which the application pods are generated.

```
$ journalctl -u kubelet
Apr 02 11:16:45 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:45.922223   86204 reconciler.go:238] "operationExecutor.VerifyControllerAttachedVolume started for volume \"kube-api-access-gwblv\" (UniqueName: \"kubernetes.io/projected/fe2c80bb-d237-413d-b4bb-b5afbef4a941-kube-api-access-gwblv\") pod \"storage-demo-deploy-84dbb4bbb7-khrrv\" (UID: \"fe2c80bb-d237-413d-b4bb-b5afbef4a941\") " pod="monitoring/storage-demo-deploy-84dbb4bbb7-khrrv"
Apr 02 11:16:46 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:46.023337   86204 reconciler.go:238] "operationExecutor.VerifyControllerAttachedVolume started for volume \"kube-api-access-xgcmj\" (UniqueName: \"kubernetes.io/projected/99745b35-23ec-46ea-b6f6-b3ee340c4a45-kube-api-access-xgcmj\") pod \"storage-demo-deploy-84dbb4bbb7-nm77g\" (UID: \"99745b35-23ec-46ea-b6f6-b3ee340c4a45\") " pod="monitoring/storage-demo-deploy-84dbb4bbb7-nm77g"
Apr 02 11:16:46 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:46.828487   86204 reconciler.go:238] "operationExecutor.VerifyControllerAttachedVolume started for volume \"kube-api-access-4l7cm\" (UniqueName: \"kubernetes.io/projected/92823ff2-00b5-4c4e-8ca6-c40f92d739d0-kube-api-access-4l7cm\") pod \"storage-demo-deploy-84dbb4bbb7-l7t6l\" (UID: \"92823ff2-00b5-4c4e-8ca6-c40f92d739d0\") " pod="monitoring/storage-demo-deploy-84dbb4bbb7-l7t6l"
Apr 02 11:16:53 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:53.875816   86204 reconciler.go:238] "operationExecutor.VerifyControllerAttachedVolume started for volume \"seaweedfs-monitor-pv1\" (UniqueName: \"kubernetes.io/csi/seaweedfs-csi-driver^dfs-test\") pod \"storage-demo-deploy-84dbb4bbb7-khrrv\" (UID: \"fe2c80bb-d237-413d-b4bb-b5afbef4a941\") " pod="monitoring/storage-demo-deploy-84dbb4bbb7-khrrv"
Apr 02 11:16:53 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:53.879166   86204 operation_generator.go:1594] "Controller attach succeeded for volume \"seaweedfs-monitor-pv1\" (UniqueName: \"kubernetes.io/csi/seaweedfs-csi-driver^dfs-test\") pod \"storage-demo-deploy-84dbb4bbb7-khrrv\" (UID: \"fe2c80bb-d237-413d-b4bb-b5afbef4a941\") device path: \"\"" pod="monitoring/storage-demo-deploy-84dbb4bbb7-khrrv"
Apr 02 11:16:53 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:53.977068   86204 operation_generator.go:631] "MountVolume.WaitForAttach entering for volume \"seaweedfs-monitor-pv1\" (UniqueName: \"kubernetes.io/csi/seaweedfs-csi-driver^dfs-test\") pod \"storage-demo-deploy-84dbb4bbb7-khrrv\" (UID: \"fe2c80bb-d237-413d-b4bb-b5afbef4a941\") DevicePath \"\"" pod="monitoring/storage-demo-deploy-84dbb4bbb7-khrrv"
Apr 02 11:16:53 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:53.986715   86204 operation_generator.go:641] "MountVolume.WaitForAttach succeeded for volume \"seaweedfs-monitor-pv1\" (UniqueName: \"kubernetes.io/csi/seaweedfs-csi-driver^dfs-test\") pod \"storage-demo-deploy-84dbb4bbb7-khrrv\" (UID: \"fe2c80bb-d237-413d-b4bb-b5afbef4a941\") DevicePath \"csi-2f07e39179f2f0a8cafac714fe02f9d41092f9fe10354d03365823e9327a1d1a\"" pod="monitoring/storage-demo-deploy-84dbb4bbb7-khrrv"
Apr 02 11:16:54 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:54.056294   86204 operation_generator.go:674] "MountVolume.MountDevice succeeded for volume \"seaweedfs-monitor-pv1\" (UniqueName: \"kubernetes.io/csi/seaweedfs-csi-driver^dfs-test\") pod \"storage-demo-deploy-84dbb4bbb7-khrrv\" (UID: \"fe2c80bb-d237-413d-b4bb-b5afbef4a941\") device mount path \"/var/lib/kubelet/plugins/kubernetes.io/csi/pv/seaweedfs-monitor-pv1/globalmount\"" pod="monitoring/storage-demo-deploy-84dbb4bbb7-khrrv"
Apr 02 11:16:54 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:54.077303   86204 operation_generator.go:631] "MountVolume.WaitForAttach entering for volume \"seaweedfs-monitor-pv1\" (UniqueName: \"kubernetes.io/csi/seaweedfs-csi-driver^dfs-test\") pod \"storage-demo-deploy-84dbb4bbb7-nm77g\" (UID: \"99745b35-23ec-46ea-b6f6-b3ee340c4a45\") DevicePath \"csi-2f07e39179f2f0a8cafac714fe02f9d41092f9fe10354d03365823e9327a1d1a\"" pod="monitoring/storage-demo-deploy-84dbb4bbb7-nm77g"
Apr 02 11:16:54 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:54.079929   86204 operation_generator.go:641] "MountVolume.WaitForAttach succeeded for volume \"seaweedfs-monitor-pv1\" (UniqueName: \"kubernetes.io/csi/seaweedfs-csi-driver^dfs-test\") pod \"storage-demo-deploy-84dbb4bbb7-nm77g\" (UID: \"99745b35-23ec-46ea-b6f6-b3ee340c4a45\") DevicePath \"csi-2f07e39179f2f0a8cafac714fe02f9d41092f9fe10354d03365823e9327a1d1a\"" pod="monitoring/storage-demo-deploy-84dbb4bbb7-nm77g"
Apr 02 11:16:54 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:54.178132   86204 operation_generator.go:631] "MountVolume.WaitForAttach entering for volume \"seaweedfs-monitor-pv1\" (UniqueName: \"kubernetes.io/csi/seaweedfs-csi-driver^dfs-test\") pod \"storage-demo-deploy-84dbb4bbb7-l7t6l\" (UID: \"92823ff2-00b5-4c4e-8ca6-c40f92d739d0\") DevicePath \"csi-2f07e39179f2f0a8cafac714fe02f9d41092f9fe10354d03365823e9327a1d1a\"" pod="monitoring/storage-demo-deploy-84dbb4bbb7-l7t6l"
Apr 02 11:16:54 iZwz97gkqaffbssf7e28fcZ kubelet[86204]: I0402 11:16:54.181402   86204 operation_generator.go:641] "MountVolume.WaitForAttach succeeded for volume \"seaweedfs-monitor-pv1\" (UniqueName: \"kubernetes.io/csi/seaweedfs-csi-driver^dfs-test\") pod \"storage-demo-deploy-84dbb4bbb7-l7t6l\" (UID: \"92823ff2-00b5-4c4e-8ca6-c40f92d739d0\") DevicePath \"csi-2f07e39179f2f0a8cafac714fe02f9d41092f9fe10354d03365823e9327a1d1a\"" pod="monitoring/storage-demo-deploy-84dbb4bbb7-l7t6l"
```

Logs generated by seaweedfs filer.

```
$ journalctl -u weed_f7333.service 
Apr 02 11:16:54 iZwz93pba29abkuicbm3ryZ weed_f7333[2111]: I0402 11:16:54.043903 filer_grpc_server_sub_meta.go:314 +  listener mount@192.168.1.249:53231 clientId 1886142360 clientEpoch 2
Apr 02 11:16:54 iZwz93pba29abkuicbm3ryZ weed_f7333[2111]: I0402 11:16:54.043938 filer_grpc_server_sub_meta.go:43  mount@192.168.1.249:53231 starts to subscribe /monitor/ from 2025-04-02 03:16:54.042073589 +0000 UTC
```

Do some tests

```shell
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test1.txt", "content": "Hello, World!"}' http://192.168.1.248:30091/write
{"message": "File test1.txt written successfully"}
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test2.txt", "content": "Good morning!"}' http://192.168.1.248:30091/write
{"message": "File test2.txt written successfully"}
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test3.txt", "content": "Good evening!"}' http://192.168.1.248:30091/write
{"message": "File test2.txt written successfully"}
$ curl 192.168.1.248:30091/list
{
  "files": [
    "test.txt",
    "test2.txt",
    "test3.txt"
  ]
}
$ curl http://192.168.1.248:30091/read?filename=test2.txt
{
  "content": "Good morning!",
  "filepath": "/opt/test2.txt"
}
```

If you check the filer dashboard at `192.168.1.250:7333`, you will see the directory `/data/seaweedfs/csi/demo1` bas been created, and the files we created by HTTP api are there.

Use weed shell on `192.168.1.250`, we can see volumes with a collection called `collection1` has been created.  The volumes will be created after the first file has been written to it.

```shell
$ weed shell
master: localhost:9333 filer: 
I0331 17:46:41.232920 masterclient.go:228 master localhost:9333 redirected to leader 192.168.1.250:9333
.master: localhost:9333 filers: [192.168.1.250:7333]
> volume.list
Topology volumeSizeLimit:1024 MB hdd(volume:8/20 active:8 free:12 remote:0) ssd(volume:0/0 active:0 free:0 remote:0)
  DataCenter DefaultDataCenter hdd(volume:8/20 active:8 free:12 remote:0) ssd(volume:0/0 active:0 free:0 remote:0)
    Rack DefaultRack hdd(volume:8/20 active:8 free:12 remote:0)
      DataNode 192.168.1.250:8081 hdd(volume:8/20 active:8 free:12 remote:0)
        Disk hdd(volume:8/20 active:8 free:12 remote:0)
          volume id:23  size:8  collection:"collection1"  version:3  modified_at_second:1743415022 
          volume id:19  size:544  file_count:1  version:3  modified_at_second:1743415089 
          volume id:20  size:8  version:3  modified_at_second:1743412229 
          volume id:13  size:2544  file_count:3  version:3  modified_at_second:1743415029 
          volume id:21  size:128  collection:"collection1"  file_count:1  version:3  modified_at_second:1743415030 
          volume id:14  size:1200  file_count:1  version:3  modified_at_second:1743414249 
          volume id:15  size:248  collection:"collection1"  file_count:2  version:3  modified_at_second:1743414993 
          volume id:22  size:8  collection:"collection1"  version:3  modified_at_second:1743415022 
        Disk hdd total size:4688 file_count:8 
      DataNode 192.168.1.250:8081 total size:4688 file_count:8 
    Rack DefaultRack total size:4688 file_count:8 
  DataCenter DefaultDataCenter total size:4688 file_count:8 
total size:4688 file_count:8 
```

```
root@iZwz988bno1q7yrktwo0auZ:~/k8s_learning/chapter_11_persistence# kubectl get pvc -n monitoring
NAME             STATUS   VOLUME                  CAPACITY   ACCESS MODES   STORAGECLASS           AGE
grafana-pvc      Bound    seaweedfs-monitor-pv2   3Gi        RWX            seaweedfs-monitor-sc   22s
monitor-pvc      Bound    nfs-monitor-pv          10Gi       RWX            nfs-sc                 4d4h
prometheus-pvc   Bound    seaweedfs-monitor-pv1   3Gi        RWX            seaweedfs-monitor-sc   22s
root@iZwz988bno1q7yrktwo0auZ:~/k8s_learning/chapter_11_persistence# kubectl get pv
NAME                    CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                           STORAGECLASS           REASON   AGE
nfs-app-pv              5Gi        RWX            Retain           Available                                   nfs-sc                          4d4h
nfs-monitor-pv          10Gi       RWX            Retain           Bound       monitoring/monitor-pvc          nfs-sc                          4d4h
seaweedfs-monitor-pv1   3Gi        RWX            Retain           Bound       monitoring/prometheus-pvc       seaweedfs-monitor-sc            6m35s
seaweedfs-monitor-pv2   3Gi        RWX            Retain           Bound       monitoring/grafana-pvc          seaweedfs-monitor-sc            6m35s
seaweedfs-static        3Gi        RWX            Retain           Bound       storage-demo-ns/seaweedfs-pvc                                   84m
```
