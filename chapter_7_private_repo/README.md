## 6. Use images from private repo

Create a `Secret` named `dockerSecret` with docker private hub credential in it as below:

```shell
$ kubectl create secret docker-registry <secret_name> \
  --docker-server=<acr_server> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email> # can be empty
```

For example, for my private repository on alibaba cloud, I should write

NOTICE: `docker-username` would be the lower-case version of your alibaba cloud username.

```shell
$ kubectl create secret docker-registry mySecret --docker-server=registry.cn-shenzhen.aliyuncs.com/mila --docker-username=my_username --docker-password=my_psw
```

因为比原来的多出了auth项所以拉取失败，原来用的应该是login后从文件获取的，但并不记得怎么找到`path/to/.docker/config.json>`的

 kubectl create secret docker-registry spinq-secret --docker-server=registry.cn-shenzhen.aliyuncs.com --docker-username=spinquantum --docker-password=SpinQ20180827

echo "eyJhdXRocyI6eyJyZWdpc3RyeS5jbi1zaGVuemhlbi5hbGl5dW5jcy5jb20iOnsidXNlcm5hbWUiOiJzcGlucXVhbnR1bSIsInBhc3N3b3JkIjoiU3BpblEyMDE4MDgyNyIsImF1dGgiOiJjM0JwYm5GMVlXNTBkVzA2VTNCcGJsRXlNREU0TURneU53PT0ifX19" | base64 --decode

You can check the value of this `Secret` in readable format by 

```shell
$ kubectl get secret mySecret --output=yaml
```

Then you will get something similar to this

```yaml
apiVersion: v1
data:
  .dockerconfigjson: eyJhdXR...SJ9fX0=
kind: Secret
metadata:
  creationTimestamp: "2024-11-20T15:36:24Z"
  name: mySecret
  namespace: default
  resourceVersion: "54915"
  uid: 21ba742e-1f6e-4733-9345-09c76bcd2b09
type: kubernetes.io/dockerconfigjson
```

Because `.dockerconfigjson` value is fixed. You can choose to keep this file. When you apply it on a different k8s cluster later, that cluster will also get accessability to the private repository.

Then you can use this `Secret` for pulling private images.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-reg
spec:
  containers:
  - name: private-reg-container
    image: <your-private-image>
  imagePullSecrets:
  - name: mySecret
  ```