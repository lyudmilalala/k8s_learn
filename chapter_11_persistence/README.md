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

Use weed shell on `192.168.1.250`, we can see volumes with a collection called `collection1` has been created. 

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
