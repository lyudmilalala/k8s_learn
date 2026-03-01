## K8s v1.34 Deployment

### 1. Check config

```shell
# close swapoff
sudo swapoff -a
```

### 2. Install Containerd

```shell
sudo apt-get update
sudo apt-get install -y containerd
```

Run `sudo ctr version` to see containerd is installed successfully. Result should be as following.

```shell
Client:
  Version:  1.7.28
  Revision: 
  Go version: go1.23.1

Server:
  Version:  1.7.28
  Revision: 
  UUID: a1f45b84-2d58-4cfc-8664-5d3248d27d35
```

Check the status of containerd by `sudo systemctl status containerd`, it should be active

The default configuration file should be create automatically at `/etc/containerd/config.toml`, if not, create it.

Run the following command to initialize the configuration of containerd.

```shell
containerd config default | sudo tee /etc/containerd/config.toml
```

Check the config file, to ensure

```toml
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
  SystemdCgroup = true
```

If it is not true, update this parameter and restart the systemd service.

### 3. Install K8s

```shell
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
# if /etc/apt/keyrings does not exist, run the following line
# sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
# addd the apt repo of k8s v1.34 (this repo is specific for this version)
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

Config the containerd command line tool for k8s. Create a file `/etc/crictl.yaml` and input the following lines.

```
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
```

### 4. Start the cluster

First find out all images required for the k8s system.

```shell
$ kubeadm config images list --kubernetes-version=v1.34.0
registry.k8s.io/kube-apiserver:v1.34.0
registry.k8s.io/kube-controller-manager:v1.34.0
registry.k8s.io/kube-scheduler:v1.34.0
registry.k8s.io/kube-proxy:v1.34.0
registry.k8s.io/coredns/coredns:v1.12.1
registry.k8s.io/pause:3.10.1
registry.k8s.io/etcd:3.6.5-0
```

Check `/etc/containerd/config.toml`, if the `pause` image in this parameter is not the same as the one required by k8s, change it to the k8s one.

```shell
[plugins."io.containerd.grpc.v1.cri"]
  sandbox_image = "registry.k8s.io/pause:3.8"
```

If you are blocked by the GFW, you would probably want to download these images manually before starting the cluster.

```shell
crictl pull registry.aliyuncs.com/google_containers/kube-apiserver:v1.34.0
crictl pull registry.aliyuncs.com/google_containers/kube-controller-manager:v1.34.0
crictl pull registry.aliyuncs.com/google_containers/kube-scheduler:v1.34.0
crictl pull registry.aliyuncs.com/google_containers/kube-proxy:v1.34.0
crictl pull registry.aliyuncs.com/google_containers/pause:3.10.1
crictl pull registry.aliyuncs.com/google_containers/etcd:3.6.5-0
crictl pull registry.aliyuncs.com/google_containers/coredns:v1.12.1

ctr --namespace k8s.io image tag registry.aliyuncs.com/google_containers/kube-apiserver:v1.34.0 registry.k8s.io/kube-apiserver:v1.34.0
ctr --namespace k8s.io image tag registry.aliyuncs.com/google_containers/kube-controller-manager:v1.34.0 registry.k8s.io/kube-controller-manager:v1.34.0
ctr --namespace k8s.io image tag registry.aliyuncs.com/google_containers/kube-scheduler:v1.34.0 registry.k8s.io/kube-scheduler:v1.34.0
ctr --namespace k8s.io image tag registry.aliyuncs.com/google_containers/kube-proxy:v1.34.0 registry.k8s.io/kube-proxy:v1.34.0
ctr --namespace k8s.io image tag registry.aliyuncs.com/google_containers/pause:3.10.1 registry.k8s.io/pause:3.10.1
ctr --namespace k8s.io image tag registry.aliyuncs.com/google_containers/etcd:3.6.5-0 registry.k8s.io/etcd:3.6.5-0
ctr --namespace k8s.io image tag registry.aliyuncs.com/google_containers/coredns:v1.12.1 registry.k8s.io/coredns/coredns:v1.12.1
```

When you list images you can see something like this.

```shell
$ crictl images
IMAGE                                                             TAG                 IMAGE ID            SIZE
registry.aliyuncs.com/google_containers/coredns                   v1.12.1             52546a367cc9e       22.4MB
registry.k8s.io/coredns/coredns                                   v1.12.1             52546a367cc9e       22.4MB
registry.aliyuncs.com/google_containers/etcd                      3.6.5-0             a3e246e9556e9       22.9MB
registry.aliyuncs.com/google_containers/kube-apiserver            v1.34.0             90550c43ad2bc       27.1MB
registry.k8s.io/kube-apiserver                                    v1.34.0             90550c43ad2bc       27.1MB
registry.aliyuncs.com/google_containers/kube-controller-manager   v1.34.0             a0af72f2ec6d6       22.8MB
registry.aliyuncs.com/google_containers/kube-proxy                v1.34.0             df0860106674d       26MB
registry.k8s.io/kube-proxy                                        v1.34.0             df0860106674d       26MB
registry.aliyuncs.com/google_containers/kube-scheduler            v1.34.0             46169d968e920       17.4MB
registry.k8s.io/kube-scheduler                                    v1.34.0             46169d968e920       17.4MB
registry.aliyuncs.com/google_containers/pause                     3.10.1              cd073f4c5f6a8       320kB
registry.k8s.io/pause                                             3.10.1              cd073f4c5f6a8       320kB
```

Run preflight before real start up. If there shows an error, we should fix it before the real start up.

```shell
kubeadm init phase preflight 
```

[ERROR FileContent--proc-sys-net-ipv4-ip_forward]: /proc/sys/net/ipv4/ip_forward contents are not set to 1
sudo tee -a /etc/sysctl.d/99-kubernetes.conf << EOF
net.ipv4.ip_forward = 1
EOF
sudo sysctl --system

After fixing all errors, start up the cluster.

```shell
kubeadm init --kubernetes-version=v1.21.14  --image-repository registry.aliyuncs.com/google_containers --apiserver-advertise-address=192.168.1.111 --pod-network-cidr=10.244.0.0/12 --ignore-preflight-errors=Swap
```

You may initialize the cluster with a config file instead of inline parameters.

```shell
kubeadm init --config init-config.yaml
```

config files can be initialized in this way.

```shell
kubeadm config print init-config.yaml    # config for init the cluster
kubeadm config print join-config.yaml    # config for worker join the cluster
# suffix of the file can be .yaml, .conf, .yaml
```

When the cluster starts, you would see something like this

```shell
Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.1.249:6443 --token abcdef.0123456789abcdef \
        --discovery-token-ca-cert-hash sha256:1354ccd2d221b0790829d0507f4f64f5e39a7acb31c38835824412a570cae610 
```

Follow the instruction to add `$HOME/.kube/config`. Then we can use `kubectl` to view our cluster. Some system pods should have been started.

```shell
$ kubectl get pods -A
NAMESPACE     NAME                                                                READY   STATUS    RESTARTS   AGE
kube-system   coredns-66bc5c9577-flqtw                                            0/1     Pending   0          9m37s
kube-system   coredns-66bc5c9577-hpj9l                                            0/1     Pending   0          9m37s
kube-system   etcd-ip-192-168-1-249.cn-shenzhen.ecs.internal                      1/1     Running   0          9m43s
kube-system   kube-apiserver-ip-192-168-1-249.cn-shenzhen.ecs.internal            1/1     Running   0          9m43s
kube-system   kube-controller-manager-ip-192-168-1-249.cn-shenzhen.ecs.internal   1/1     Running   0          9m43s
kube-system   kube-proxy-27m6l                                                    1/1     Running   0          9m38s
kube-system   kube-scheduler-ip-192-168-1-249.cn-shenzhen.ecs.internal            1/1     Running   0          9m43s
```

We can see the coredns pods are still pending. To run them, we now have to add the CNT plugin. There are multiple possible choice. Example scripts for **Calico** and **Flannel** are shown in the directory.

Here we use Calico.

```shell
# Need to pull these images, the first two image must be on all nodes in the cluster
ctr --namespace k8s.io images pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/calico/cni:v3.25.0 && \
ctr --namespace k8s.io images tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/calico/cni:v3.25.0 docker.io/calico/cni:v3.25.0
ctr --namespace k8s.io images pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/calico/node:v3.25.0 && \
ctr --namespace k8s.io images tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/calico/node:v3.25.0 docker.io/calico/node:v3.25.0
ctr --namespace k8s.io images pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/calico/kube-controllers:v3.25.0 && \
ctr --namespace k8s.io images tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/calico/kube-controllers:v3.25.0  docker.io/calico/kube-controllers:v3.25.0
# Start CNI
kubectl apply -f calico.yaml
```

Then you can see all pods start properly.

```shell
$ kubectl get pods -A 
NAMESPACE     NAME                                                                READY   STATUS    RESTARTS   AGE
kube-system   calico-kube-controllers-b45f49df6-84hx9                             1/1     Running   0          14m
kube-system   calico-node-fz9k9                                                   1/1     Running   0          14m
kube-system   coredns-66bc5c9577-flqtw                                            1/1     Running   0          38m
kube-system   coredns-66bc5c9577-hpj9l                                            1/1     Running   0          38m
kube-system   etcd-ip-192-168-1-249.cn-shenzhen.ecs.internal                      1/1     Running   0          38m
kube-system   kube-apiserver-ip-192-168-1-249.cn-shenzhen.ecs.internal            1/1     Running   0          38m
kube-system   kube-controller-manager-ip-192-168-1-249.cn-shenzhen.ecs.internal   1/1     Running   0          38m
kube-system   kube-proxy-27m6l                                                    1/1     Running   0          38m
kube-system   kube-scheduler-ip-192-168-1-249.cn-shenzhen.ecs.internal            1/1     Running   0          38m
```

For flannel is like this:

```shell
# Need to pull these images
ctr images pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/ghcr.io/flannel-io/flannel-cni-plugin:v1.9.0-flannel1
ctr --namespace k8s.io images tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/ghcr.io/flannel-io/flannel-cni-plugin:v1.9.0-flannel1  ghcr.io/flannel-io/flannel-cni-plugin:v1.9.0-flannel1

ctr images pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/ghcr.io/flannel-io/flannel:v0.28.1
ctr --namespace k8s.io images tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/ghcr.io/flannel-io/flannel:v0.28.1  ghcr.io/flannel-io/flannel:v0.28.1
# Start CNI
kubectl apply -f flannel.yaml
```
ctr --namespace k8s.io images pull ubuntu:22.04
### 5. Add worker to the cluster

On another worker server, use the worker join command shown when finish initializing the cluster to join it into the cluster.

```shell
kubeadm join 192.168.1.249:6443 --token abcdef.0123456789abcdef \
        --discovery-token-ca-cert-hash sha256:1354ccd2d221b0790829d0507f4f64f5e39a7acb31c38835824412a570cae610 
```

Result will be something like this.

```shell
This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.
```

Then use `kubectl get nodes` on the master node to check the status of the worker. 

```shell
NAME                                        STATUS     ROLES           AGE     VERSION
ip-192-168-1-249.cn-shenzhen.ecs.internal   Ready      control-plane   46m     v1.34.4
ip-192-168-1-250.cn-shenzhen.ecs.internal   Ready      <none>          2m31s   v1.34.4
```

