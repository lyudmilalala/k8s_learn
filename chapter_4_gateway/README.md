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
$ docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-appA:1.0.0
$ docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/flask-appB:1.0.0
```

And build the deployments and services, then test them.

```shell
$ kubectl apply -f appA/appA-deployment.yaml
$ kubectl apply -f appB/appB-deployment.yaml
$ kubectl get pods -n appA-ns
$ kubectl get pods -n appB-ns
$ curl -X POST 'http://47.119.148.12:30061/sum' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "sum = 22", "status": 200}
$ curl -X POST 'http://47.119.148.12:30062/substract' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "sum = 22", "status": 200}
```

### 4.2 Routing by Nginx Ingress

### 4.3 Routing by Traefik