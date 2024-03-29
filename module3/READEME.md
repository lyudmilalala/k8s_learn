1. Build docker image
```
$ docker build . -t lyudmilalala/go_http_server:1.0.0
```

2. Pull image to Docker Hub
```
$ docker login -u <user_name> -p <user_password>
WARNING! Using --password via the CLI is insecure. Use --password-stdin.
Login Succeeded
$ docker push lyudmilalala/go_http_server:1.0.0
```

<img width="975" alt="image" src="https://github.com/lyudmilalala/k8s_learn/assets/32922504/825091a9-b758-4479-835b-20d958f6fbc4">

3. Run a docker container holding the golang http server
```
$ docker run -itd --name go-test -p 5080:5080 lyudmilalala/go_http_server:1.0.0
$ docker ps
CONTAINER ID   IMAGE                               COMMAND      CREATED          STATUS         PORTS                    NAMES
aceff21eeae7   lyudmilalala/go_http_server:1.0.0   "/opt/run"   14 minutes ago   Up 7 seconds   0.0.0.0:5080->5080/tcp   go-test
$ curl -i http://localhost:5080/healthz?user=Tom
HTTP/1.1 200 OK
Accept: */*
App: mila-app
User-Agent: curl/7.54.0
Date: Tue, 20 Jun 2023 15:11:54 GMT
Content-Length: 16
Content-Type: text/plain; charset=utf-8

200
hello [Tom]
```

4. Check container IP by `nsenter`
```
$ docker inspect <container_id> | grep -i pid
            "Pid": 9674,
            "PidMode": "",
            "PidsLimit": null,
$ nsenter -t 9674 -n ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
4: eth0@if5: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:ac:11:00:02 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 172.17.0.2/16 brd 172.17.255.255 scope global eth0
       valid_lft forever preferred_lft forever    
```
