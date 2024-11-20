### 对服务器进行微调，并使用k8s pod启动

修改服务器，添加了`glog`，另一个接口，以及一些环境变量

编译golang应用，启动应用，并测试

```
$ go build -o run .
$ ./run 
I0903 21:05:19.435917   39473 main.go:29] APP_PORT = :5090
I0903 21:05:19.436168   39473 main.go:30] APP_LOG_LEVEL = WARNING
I0903 21:05:19.436189   39473 main.go:31] Starting http server...
$ curl -i http://localhost:5090/healthz
HTTP/1.1 200 OK
Version: 1.0.0
Date: Sun, 03 Sep 2023 13:06:30 GMT
Content-Length: 4
Content-Type: text/plain; charset=utf-8

pass: duration = 17.033926s
```

同样修改Dockerfile，添加一些环境变量，打包成镜像的命令不变

```
docker build . -t lyudmilalala/go_http_server:1.2.0
```

就可以使用如下命令在启动容器时配置项目的参数

```
$ docker run -itd --name go-test -e APP_PORT=5090 -e APP_LOG_LEVEL=WARNING -e VERSION=1.2.0 -p 5090:5090 lyudmilalala/go_http_server:1.1.0
b6877fa028c665cc99536eee1c42fe4c1ae6741834867a2c1c7ee3cba40f8fd1
$ curl -i http://localhost:5090/greeting?user=Tom
HTTP/1.1 200 OK
Accept: */*
App: mila-app
User-Agent: curl/7.54.0
Version: 1.2.0
Date: Sun, 03 Sep 2023 05:09:15 GMT
Content-Length: 12
Content-Type: text/plain; charset=utf-8

hello [Tom]
```

创建测试专用的namespace

```
kubectl create namespace go-func
```

调用`go-func-svc.yaml`启动服务集群，请求并获得环境变量`VERSION`

```
$ kubectl apply -f go-func-svc.yaml
deployment.apps/go-func-deploy created
service/go-func-svc created
$ kubectl get svc -n go-func
NAME          TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)          AGE
go-func-svc   NodePort   10.99.13.28   <none>        5080:30090/TCP   5s
$ curl -i http://localhost:30090/greeting?user=Tom
HTTP/1.1 200 OK
Accept: */*
App: mila-app
User-Agent: curl/7.54.0
Version: 1.2.0
Date: Sun, 03 Sep 2023 09:59:45 GMT
Content-Length: 12
Content-Type: text/plain; charset=utf-8

hello [Tom]
```

通过CoreDNS域名访问

### 通过CoreDNS域名访问

创建toolbox容器

```
$ kubectl apply -f toolbox.yml 
deployment.apps/toolbox-deploy created
```

进入toolbox容器

```
$ kubectl exec -it toolbox-deploy-cdd9c9655-n5rr9 bash -n go-func
```

查看`resolv.conf`

```
$ cat /etc/resolv.conf 
nameserver 10.96.0.10
search go-func.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

在容器中可以使用域名请求

```
$ curl -i http://go-func-svc.go-func.svc.cluster.local:5080/greeting?user=Tom
HTTP/1.1 200 OK
Accept: */*
App: mila-app
User-Agent: curl/7.81.0
Version: 1.2.0
Date: Tue, 05 Sep 2023 15:18:42 GMT
Content-Length: 12
Content-Type: text/plain; charset=utf-8

hello [Tom]
```

短名也可正常工作

```
curl -i http://go-func-svc.go-func:5080/greeting?user=Tom
HTTP/1.1 200 OK
Accept: */*
App: mila-app
User-Agent: curl/7.81.0
Version: 1.2.0
Date: Tue, 05 Sep 2023 17:28:53 GMT
Content-Length: 12
Content-Type: text/plain; charset=utf-8

hello [Tom]
```

### 通过Ingress Gateway访问

以下步骤在`ingress`目录下进行

创建Install ingress controller
```
kubectl create -f nginx-ingress-deployment.yaml
```

创建tls证书并配置成secret

```
$ openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=cncamp.com/O=cncamp" -addext "subjectAltName = DNS:cncamp.com"
Generating a RSA private key
..............+++++
................................+++++
writing new private key to 'tls.key'
-----
$ ls
ingress.yaml			tls.crt
nginx-ingress-deployment.yaml	tls.key
$ kubectl create secret tls cncamp-tls --cert=./tls.crt --key=./tls.key -n go-func
secret/cncamp-tls created
$ kubectl get secret -n go-func
NAME                  TYPE                                  DATA   AGE
cncamp-tls            kubernetes.io/tls                     2      11s
default-token-xk92l   kubernetes.io/service-account-token   3      2d8h
```

应用ingress gateway，发生报错

```
$ kubectl apply -f ingress.yaml 
Error from server (InternalError): error when creating "ingress.yaml": Internal error occurred: failed calling webhook "validate.nginx.ingress.kubernetes.io": Post "https://ingress-nginx-controller-admission.ingress-nginx.svc:443/networking/v1/ingresses?timeout=10s": dial tcp 10.104.62.177:443: connect: connection refused
```

根据网上的教程删除admission后，成功创建

```
$ kubectl get ValidatingWebhookConfiguration
NAME                           WEBHOOKS   AGE
ingress-nginx-admission        1          46h
$ kubectl delete -A ValidatingWebhookConfiguration ingress-nginx-admission
validatingwebhookconfiguration.admissionregistration.k8s.io "ingress-nginx-admission" deleted
$ kubectl apply -f ingress.yaml 
ingress.networking.k8s.io/gateway created
$ kubectl get ingress -n go-func
NAME      CLASS    HOSTS        ADDRESS   PORTS     AGE
gateway   <none>   cncamp.com             80, 443   25s
```

访问域名

```
$ curl -H "Host: cncamp.com" https://10.107.196.184/healthz -ivk
*   Trying 10.107.196.184...
* TCP_NODELAY set
```

```
$ curl -H "Host: cncamp.com" https://10.107.196.184/greeting?user=Tom -ivk
```

### 添加不同环境的配置参数

在`config`目录里创建生成configmap所使用的脚本，并使用它们创建configmap

```
kubectl apply -f config/dev-config.yaml
```

也可以直接创建

```
kubectl create configmap prod-config -n go-func --from-literal=APP_PORT=5090 --from-literal=APP_LOG_LEVEL=WARNING --from-literal=VERSION=1.2.0
```

调用`go-func-svc-with-config.yaml`启动服务集群，请求并获得环境变量`VERSION`

```
$ kubectl apply -f go-func-svc-with-config.yaml 
deployment.apps/go-func-deploy created
service/go-func-svc created
$ kubectl get svc -n go-func
NAME          TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
go-func-svc   NodePort   10.108.113.83   <none>        5090:30090/TCP   5s
$ curl -i http://localhost:30090/greeting?user=Tom
HTTP/1.1 200 OK
Accept: */*
App: mila-app
User-Agent: curl/7.54.0
Version: 1.2.0
Date: Sun, 03 Sep 2023 10:05:56 GMT
Content-Length: 12
Content-Type: text/plain; charset=utf-8

hello [Tom]
```

如果替换`envFrom`部分为`name: dev-config`，重新请求，结果会有所不同

### 添加探活

在`golang`服务器中，若环境变量`APP_LIVENESS_TEST`为`Y`则启动探活测试

探活测试时，接口`/healthz`前60s返回状态码200，60s后返回状态码500并报错

将config文件中的`APP_LIVENESS_TEST`切换为`Y`，启动集群

```
$ kubectl apply -f go-func-svc-with-liveness-check.yaml 
deployment.apps/go-func-deploy created
service/go-func-svc createdxx
```

此时列出pod会发现所有的pod并没有`READY`，这是因为我们在``中设置``为30s，所以在没有做检测的前30s，就算应用已经就绪，夜检测不到

```
$ kubectl get pods -n go-func
NAME                              READY   STATUS    RESTARTS   AGE
go-func-deploy-79f4cb65cc-5flsp   0/1     Running   0          34s
go-func-deploy-79f4cb65cc-89jqm   0/1     Running   0          34s
go-func-deploy-79f4cb65cc-xb9p2   0/1     Running   0          34s
```

30s以后，60s以前，pod为`READY`

```
$ kubectl get pods -n go-func
NAME                              READY   STATUS    RESTARTS   AGE
go-func-deploy-79f4cb65cc-5flsp   1/1     Running   0          39s
go-func-deploy-79f4cb65cc-89jqm   1/1     Running   0          39s
go-func-deploy-79f4cb65cc-xb9p2   1/1     Running   0          39s
```

请求结果如下

```
$ curl -i http://localhost:5090/healthz
HTTP/1.1 200 OK
Version: 1.0.0
Date: Sun, 03 Sep 2023 13:07:11 GMT
Content-Length: 4
Content-Type: text/plain; charset=utf-8

pass: duration = 37.993326s
```

60s以后，请求结果如下

```
$ curl -i http://localhost:5090/healthz
HTTP/1.1 500 Internal Server Error
Version: 1.0.0
Date: Sun, 03 Sep 2023 13:07:53 GMT
Content-Length: 28
Content-Type: text/plain; charset=utf-8

error: duration = 79.279601s
```

每个pod请求失败3次以后，开始重启

```
$ kubectl get pods -n go-func
NAME                              READY   STATUS    RESTARTS     AGE
go-func-deploy-5c69f49c7c-dxvr9   0/1     Running   1 (3s ago)   78s
go-func-deploy-5c69f49c7c-pvk2r   0/1     Running   1 (3s ago)   78s
go-func-deploy-5c69f49c7c-tfq59   0/1     Running   1 (2s ago)   78s
```

### 添加优雅启动和关闭

