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
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test.txt", "content": "Hello, World!"}' http://192.168.1.4:8080/write
{"message": "File test.txt written successfully"}
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

### Use SeaweedFS as the Storage

First we need to have SeaweedFS installed on an extra server. Here this storage server has IP `192.168.1.250`.

We deploy a one master, one volume, one filer system in this demo. The master server listens to port `9333`. The volume server listens to port `8081`. The filer server listens to port `7333`.

On our K8s cluster, first install `seaweedfs-csi-driver`.

```shell
$ git clone git@github.com:seaweedfs/seaweedfs-csi-driver.git
$ helm install --set seaweedfsFiler=192.168.1.250:7333 seaweedfs-csi-driver ./seaweedfs-csi-driver/deploy/helm/seaweedfs-csi-driver
```

As usual, if you fail to pull down some of the official images, here is a substitution solution.

```shell

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

```shell
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test1.txt", "content": "Hello, World!"}' http://192.168.1.128:30090/write
{"message": "File test.txt written successfully"}
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test2.txt", "content": "Good morning!"}' http://192.168.1.128:30090/write
{"message": "File test2.txt written successfully"}
$ curl -X POST -H "Content-Type: application/json" -d '{"filename": "test3.txt", "content": "Good evening!"}' http://192.168.1.128:30090/write
{"message": "File test2.txt written successfully"}
$ curl 192.168.1.128:30090/list
{
  "files": [
    "test.txt",
    "test2.txt",
    "test3.txt"
  ]
}
$ curl http://192.168.1.128:30090/read?filename=test2.txt
{
  "content": "Good morning!",
  "filepath": "/opt/test2.txt"
}
```