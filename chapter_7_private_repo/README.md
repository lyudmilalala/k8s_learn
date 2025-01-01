## 7. Use images from private repo

Create a `Secret` named `dockerSecret` with docker private hub credential in it as below:

```shell
$ kubectl create secret docker-registry <secret_name> \
  --docker-server=<acr_server> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email> # can be empty
```

For example, for my private repository on alibaba cloud, I should write

```shell
$ kubectl create secret docker-registry mySecret --docker-server=registry.cn-shenzhen.aliyuncs.com --docker-username=my_username --docker-password=my_psw
```

NOTICE: `docker-username` would be the lower-case version of your alibaba cloud username.

NOTICE: The secret will be created in namespace `default`. As `Secret` can only be referenced by pods in that same namespace, if you want to use it to pull images in another namespace, you have to change the namespace of the secret.

You can export the value of this `Secret` to a config file

```shell
$ kubectl get secret mySecret --output=yaml > mysecret.yaml
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

In which `.dockerconfigjson` is the encoded docker login information. You can check it by decoding.

```shell
$ echo "eyJhdXRocyI6eyJyZWd...ifX19" | base64 --decode
{"auths":{"registry.cn-shenzhen.aliyuncs.com":{"username":"my_username","password":"my_psw","auth":"c3BpbnF1Y...DgyNw=="}}}
$ echo "c3BpbnF1Y...DgyNw==" | base64 --decode
my_username:my_psw
```

Clean up the `Secret` config file, change its namespace, and apply it. Below is an example config file.

A `Secret` can only used by resources in the same namespace with it. Each `Secret` can only be used by one namespace. 

```yaml
apiVersion: v1
data:
  .dockerconfigjson: eyJhdXR...SJ9fX0=
kind: Secret
metadata:
  name: mySecret
  namespace: task-result-ns
type: kubernetes.io/dockerconfigjson
```

Then you can use this `Secret` for pulling private images.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-reg
  namespace: task-result-ns
spec:
  containers:
  - name: private-reg-container
    image: <your-private-image>
  imagePullSecrets:
  - name: mySecret
  ```