## 10. Job

A job is a one-time task running on a pod in the k8s cluster. If a job failed, k8s can retry it automatically, until success or achieving the maximum retry times.

We first create a simple job image. Functions are written in `job.py`. We define the script in the way that it has 20% chance to fail.

Then we build and upload the image.

```shell
docker build . -t crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/job-test:1.0.0
docker push crpi-foj3lu39cfzgj05z.cn-shenzhen.personal.cr.aliyuncs.com/jerry-learn/job-test:1.0.0
```

Then we run the job on the k8s cluster. 

```shell
kubectl apply -f job-deploy.yaml
```

Here are the definitions of some configuration parameters.

- `spec.completions`: Specifies the number of successfully finished Pods required to define the job as successful. Default value is 1.
- `spec.parallelism`: Specifies the maximum number of Pods that can run at the same time for the job. Default value is 1.
- `spec.ttlSecondsAfterFinished`: Specifies the max period length a job will be kept existing after its completion or failure.
- `spec.activeDeadlineSeconds`: Specifies the duration in seconds that the job keeps running before the system will actively try to terminate it.
- `spec.backoffLimit`: 3 Specifies the number of retries after failure. Default is 6.
- `spec.template.spec.restartPolicy`: Specifies whether to restart a Pod. Can be `OnFailure`, `Never`, and `Always`.

### Authorization

To call the k8s apiserver, we need to first create a token, otherwise we would get a `401` error.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: java-admin

---
  
apiVersion: v1
kind: Secret
metadata:
  name: java-access-secret
  annotations:
    kubernetes.io/service-account.name: java-admin
type: kubernetes.io/service-account-token

---

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-updater
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list", "patch", "update", "delete", "create"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get", "list"]

---

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: simu-auth-binding
subjects:
- kind: ServiceAccount
  name: java-admin
  namespace: default
roleRef:
  kind: ClusterRole
  name: pod-updater
  apiGroup: rbac.authorization.k8s.io
```

After apply the above configures to the K8s cluster, you can grab the secret `java-access-secret`.

```shell
$ kubectl apply -f authorization.yaml
serviceaccount/java-admin created
secret/java-access-secret created
clusterrole.rbac.authorization.k8s.io/pod-updater unchanged
clusterrolebinding.rbac.authorization.k8s.io/simu-auth-binding configured
$ kubectl describe secret java-access-secret -n default
Name:         java-access-secret
Namespace:    default
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: java-admin
              kubernetes.io/service-account.uid: 5a1fe00d-1fce-4b0c-95e6-72997c591685

Type:  kubernetes.io/service-account-token

Data
====
token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IncxNVYweUtCbGlZWnRFUmdrbzJaNWEwWWNHVUU4OFhVNkY3aFdpTWpweFUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImphdmEtYWNjZXNzLXNlY3JldCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJqYXZhLWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNWExZmUwMGQtMWZjZS00YjBjLTk1ZTYtNzI5OTdjNTkxNjg1Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6amF2YS1hZG1pbiJ9.YvgqEmVKXhU0XHCR0RMGLn3sjbXONY9oj1TvXDuRSkGG3RJwJBJ3GxxfoxQBgFDydw-jlYHuosIzKPDxFeLbBulHnShKprk9w0821ehMvFAAhDoovSjEO1JaCKE6CJe_EO3egQR_xbyLCTxLgfdrkQQLRVbbw3M4RGq-3ONUhkwhq4nk_K8hqT3ZeInDmB9iM8tzhRNHFREmf5qrpKquVd162vOMv2KBhAYGMOAyoGOUX_Y1CoealTpo_zqd9BlzyG1-C3fx1YaP6OsPnl1Q3vRKbdipw1lxABKP8UGRJM9ZRH_bsuY32Kb8VNCdLAgEK-zD-NMr8jQhbMCUEqgR0w
ca.crt:     1099 bytes
```

Then you can call apiserver with this token.

```shell
curl -k -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IncxNVYweUtCbGlZWnRFUmdrbzJaNWEwWWNHVUU4OFhVNkY3aFdpTWpweFUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImphdmEtYWNjZXNzLXNlY3JldCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJqYXZhLWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNWExZmUwMGQtMWZjZS00YjBjLTk1ZTYtNzI5OTdjNTkxNjg1Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6amF2YS1hZG1pbiJ9.YvgqEmVKXhU0XHCR0RMGLn3sjbXONY9oj1TvXDuRSkGG3RJwJBJ3GxxfoxQBgFDydw-jlYHuosIzKPDxFeLbBulHnShKprk9w0821ehMvFAAhDoovSjEO1JaCKE6CJe_EO3egQR_xbyLCTxLgfdrkQQLRVbbw3M4RGq-3ONUhkwhq4nk_K8hqT3ZeInDmB9iM8tzhRNHFREmf5qrpKquVd162vOMv2KBhAYGMOAyoGOUX_Y1CoealTpo_zqd9BlzyG1-C3fx1YaP6OsPnl1Q3vRKbdipw1lxABKP8UGRJM9ZRH_bsuY32Kb8VNCdLAgEK-zD-NMr8jQhbMCUEqgR0w" https://47.119.56.113:6443/api/v1/namespaces/flask-ns/pods/
```

### Call apiserver by Java

If use call K8s api by a java client, you may get an error similar to this

```shell
Exception in thread "main" io.fabric8.kubernetes.client.KubernetesClientException: Operation: [list]  for kind: [Pod]  with name: [null]  in namespace: [kube-system]  failed.
	at io.fabric8.kubernetes.client.KubernetesClientException.launderThrowable(KubernetesClientException.java:159)
	at io.fabric8.kubernetes.client.dsl.internal.BaseOperation.list(BaseOperation.java:422)
	at io.fabric8.kubernetes.client.dsl.internal.BaseOperation.list(BaseOperation.java:388)
	at io.fabric8.kubernetes.client.dsl.internal.BaseOperation.list(BaseOperation.java:92)
	at Demo.main(Demo.java:29)
Caused by: java.io.IOException: sun.security.validator.ValidatorException: PKIX path validation failed: java.security.cert.CertPathValidatorException: Path does not chain with any of the trust anchors
	at io.fabric8.kubernetes.client.dsl.internal.OperationSupport.waitForResult(OperationSupport.java:504)
	at io.fabric8.kubernetes.client.dsl.internal.BaseOperation.list(BaseOperation.java:420)
	... 3 more
```

To solve this problem, we need to create a trust sotre of the k8s certificaation.

Visit your `$JAVA_HOME/bin`, then use the `keytool` tool there.

openssl x509 -outform der -in D:\projects\k8s_learn\chapter_10_job\k8s-fullchain.crt -out D:\projects\k8s_learn\chapter_10_job\k8s-fullchain.der

keytool -keystore "D:\tools\java8\jre8\lib\security\cacerts" -storepass changeit -importcert -alias k8s-crt -file D:\projects\k8s_learn\chapter_10_job\k8s-fullchain.der

$ keytool -list -keystore "D:\tools\java8\jre8\lib\security\cacerts" -storepass changeit | findstr k8s-crt
k8s-crt, 2025-3-20, trustedCertEntry, 

keytool -import -alias k8s-crt -file D:\projects\k8s_learn\chapter_10_job\k8s-fullchain.crt -keystore D:\projects\k8s_learn\chapter_10_job\fullchain-cacerts.jks -storepass myPassword

Run the java client will get result like this

```
Number of pods = 3
pod name = flask-deploy-7f5c58d55f-9dxgx
pod name = flask-deploy-7f5c58d55f-qppd7
pod name = flask-deploy-7f5c58d55f-vfb2p
```