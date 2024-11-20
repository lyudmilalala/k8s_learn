我希望为我的pod在创建和删除时添加一行log，以便收集之后知道它什么时候被销毁了

然而，我执行了如下脚本，创建pod后执行`kubectl logs <pod_name> -n default`，并没有"Hello, I am created!"，只有"hello in loop"。为什么?

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lifecycle-deploy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: lifecycle-app
  template:
    metadata:
      labels:
        app: lifecycle-app
    spec:
      containers:
      - name: lifecycle-app-pod
        image: busybox:1.36
        imagePullPolicy: IfNotPresent
        command: ["/bin/sh", "-c", "while true; do echo 'hello in loop'; sleep
10;done"]
        lifecycle:
          postStart:
            exec:
              command: ["/bin/sh", "-c", "echo 'Hello, I am created! My pod name
is' $HOSTNAME"]
          preStop:
            exec:
              command: ["/bin/sh", "-c", "echo 'Goodbye, I am being terminated! My
pod name was' $HOSTNAME"]
```
