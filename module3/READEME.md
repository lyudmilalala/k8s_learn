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
```