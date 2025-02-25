## 4. Routing by Gateway

### 4.1 Prepare two different services

Build two images similar to the one in chapter 2. Corresponding source codes are in directory `appA` and `appB`.
 
```shell
$ docker build -t crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/app-a:1.0.0 appA
$ docker build -t crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/app-b:1.0.0 appB
```

Still you can run a test the servers at local for debugging.

```shell
$ docker run -itd --name appA -p 18080:8080 crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/app-a:1.0.0
$ curl -X POST 'http://localhost:18080/sum' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 2}'
{"msg": "sum = 9", "status": 200}
$ docker rm -f appA
$ docker run -itd --name appB -p 18081:8080 crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/app-b:1.0.0
$ curl -X POST 'http://localhost:18081/subtract' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 2}'
{"msg": "diff = 5", "status": 200}
$ docker rm -f appB
```

And push these images.

```shell
$ docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/app-a:1.0.0
$ docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/app-b:1.0.0
```

And build the deployments and services, then test them.

```shell
$ kubectl apply -f appA/appA-deployment.yaml
$ kubectl apply -f appB/appB-deployment.yaml
$ kubectl get svc -n appa-ns
NAME       TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
appa-svc   NodePort   10.98.31.119   <none>        8080:30061/TCP   20s
$ kubectl get svc -n appb-ns
NAME       TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
appb-svc   NodePort   10.98.196.33   <none>        8080:30062/TCP   20s
$ kubectl get pods -n appA-ns
$ kubectl get pods -n appB-ns
$ curl -X POST 'http://47.119.148.12:30061/sum' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "sum = 22", "status": 200}
$ curl -X POST 'http://47.119.34.78:30062/subtract' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "sum = 22", "status": 200}
```

### 4.2 Routing by Ingress Nginx

Deploy the ingress controller by `kubectl apply -f` script `nginx-ingress-deploy.yaml` in the ingress directory. It is from the [official instruction](https://kubernetes.github.io/ingress-nginx/deploy/), the origin source code is

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0/deploy/static/provider/cloud/deploy.yaml
```

To avoid being blocked, I replace the image in script by images from [here](https://docker.aityp.com/).

After deploying, you should see the nginx controller service running, and now we can visit a nginx proxy by `http://<master_node_ip>:32240`.

```shell
$ kubectl get svc -n ingress-nginx
NAME                                 TYPE           CLUSTER-IP       EXTERNAL-IP                          PORT(S)                      AGE
ingress-nginx-controller             LoadBalancer   10.101.71.75     <pending>                            80:32240/TCP,443:31259/TCP   24h
ingress-nginx-controller-admission   ClusterIP      10.103.218.170   <none>                               443/TCP                      24h
```

Because our two services are from different namespaces, we need to create `ExternalName` services for them in the `ingress-nginx` namespace. 

```shell
kubectl apply -f externalSvc.yaml
```

Then we apply the ingress rules.

```shell
kubectl apply -f ingress.yaml
```

`port.number` in each rules should be equal to the `port` of service, not the `nodePort`.

Annotation `nginx.ingress.kubernetes.io/rewrite-target` is used to rewrite url by patterns. In our case, nginx will map `jerry.learning.com:32240/appa/sum` to `10.98.31.119:8080/sum`.

Set a relationship between the master node and the hostname in `/etc/hosts`.

```
127.0.0.1 jerry.learning.com
```

Then test by `curl` on the master node.

```shell
$ curl -X POST 'http://jerry.learning.com:32240/appa/sum' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "sum = 22", "status": 200}
$ curl -X POST 'http://jerry.learning.com:32240/appb/subtract' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "diff = -8", "status": 200}
```

### 4.2 Routing by Traefik