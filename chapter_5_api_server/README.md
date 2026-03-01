## 5. Call API gateway

In K8s, we get to know how many services are running, and modifying the configuration of pods, all by calling the K8s API gateway. The reason that we can call commands `kubectl get pods -A` to get information on our master node is that a default user with full access permission has been created during the cluster initialization. If we call the specific K8s API with no token, we will get the following response:

```shell
$ curl -k https://47.115.170.172:6443/api/v1/namespaces/busybox-ns/pods/
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "pods is forbidden: User \"system:anonymous\" cannot list resource \"pods\" in API group \"\" in the namespace \"busybox-ns\"",
  "reason": "Forbidden",
  "details": {
    "kind": "pods"
  },
  "code": 403
```

To solve tis problem, we need to follow 2 steps:
1. Authentication - Assign an identity to the request. This identity is always represented by a username or JWT token.
2. Authorization - Give the identity enough chance for performing the operation.

### 5.1 Authentication

Authentication is the process of verifying the identity of a caller. There are many approaches to gain an identity. Here we introduce 2 ways, use X509 certificate and Service Account.

#### Create a user with X509 certificate

#### Create a Service Account with a secret token

We create a service account and a secret token for it by `kubectl apply -f service_account.yaml`.

**NOTICE:** `ServiceAccounts` and `Secrets` are namespace-scoped resources in Kubernetes. Remeber to create one for each namespace.

**NOTICE:** For K8s version < 1.27, `service-account-token` does not have an expiration time. It can be used for long-running jobs.

Then you can grab the value of the secret token.

```shell
$ kubectl describe secret busybox-access-secret -n busybox-ns
Name:         busybox-access-secret
Namespace:    busybox-ns
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: busybox-admin
              kubernetes.io/service-account.uid: 4812594f-e920-4812-a4f5-3369d9a9dbcf

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1099 bytes
namespace:  10 bytes
token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IncxNVYweUtCbGlZWnRFUmdrbzJaNWEwWWNHVUU4OFhVNkY3aFdpTWpweFUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJidXN5Ym94LW5zIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImJ1c3lib3gtYWNjZXNzLXNlY3JldCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJidXN5Ym94LWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNDgxMjU5NGYtZTkyMC00ODEyLWE0ZjUtMzM2OWQ5YTlkYmNmIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmJ1c3lib3gtbnM6YnVzeWJveC1hZG1pbiJ9.KPDhTaPQFxoyuWtRUvULJuVF162kreQRIz72drgRP0zc8K-eji65Av2upzE66ApuDG1oOEHD3UHUWNICfoFaAaUXIGjwpyu-Buz7Sm5GNMlo672ufIttAkjjljZJNwFS1weknmts2W0xHlCN-uvV-PgGcr4eU-FNvQFK3ARs8nc0qYXHrm8ZweytuOJdxd0NmxmLlj-kds_JKdIAyoBCeiJMb0FDWoIoAzBl6mARA2eOb1oqBsVvNUPlraTlKDZKU7h_iGcCf0h98unVg9SuceC3ETuHLT1kRS9DsVa1XGIZ20EMUFo8CAokO0CrRXeletkbFyfRPM9hrAz91TSfJw
```

Then we can use this token in our request.

```shell
$ curl -k -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IncxNVYweUtCbGlZWnRFUmdrbzJaNWEwWWNHVUU4OFhVNkY3aFdpTWpweFUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJidXN5Ym94LW5zIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImJ1c3lib3gtYWNjZXNzLXNlY3JldCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJidXN5Ym94LWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNDgxMjU5NGYtZTkyMC00ODEyLWE0ZjUtMzM2OWQ5YTlkYmNmIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmJ1c3lib3gtbnM6YnVzeWJveC1hZG1pbiJ9.KPDhTaPQFxoyuWtRUvULJuVF162kreQRIz72drgRP0zc8K-eji65Av2upzE66ApuDG1oOEHD3UHUWNICfoFaAaUXIGjwpyu-Buz7Sm5GNMlo672ufIttAkjjljZJNwFS1weknmts2W0xHlCN-uvV-PgGcr4eU-FNvQFK3ARs8nc0qYXHrm8ZweytuOJdxd0NmxmLlj-kds_JKdIAyoBCeiJMb0FDWoIoAzBl6mARA2eOb1oqBsVvNUPlraTlKDZKU7h_iGcCf0h98unVg9SuceC3ETuHLT1kRS9DsVa1XGIZ20EMUFo8CAokO0CrRXeletkbFyfRPM9hrAz91TSfJw" https://47.115.170.172:6443/api/v1/namespaces/busybox-ns/pods/
```

#### Some more useful commands

Use HTTP api to modify pod annotations.

```shell
curl -k -X PATCH \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/strategic-merge-patch+json" \
  https://<your-k8s-api-server>:6443/api/v1/namespaces/<namespace>/pods/<pod-name> \
  -d '{
    "metadata": {
      "annotations": {
        "controller.kubernetes.io/pod-deletion-cost": "100"
      }
    }
  }'
```

Use HTTP api to modify deployment replicas.

```shell
curl -k -X PATCH \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/strategic-merge-patch+json" \
  https://<your-k8s-api-server>:6443/apis/apps/v1/namespaces/<namespace>/deployments/<deployment-name>/scale \
  -d '{
    "spec": {
      "replicas": 5
    }
  }'
```

### 5.2 Authorization

Authorization is the process of verifying whether an authenticated entity has the permission to do something.

If we just do authentication but not authorization, we will still get a 403 error when calling the K8s API. This is because our user/service account still does not have permission to call the API.

In `role_binding.yaml`, we create a role with enough access permission, and then bind it to our serice account `busybox-admin`. Now when we call the K8s API, we will get a 200 response.

```json
{
  "kind": "PodList",
  "apiVersion": "v1",
  "metadata": {
    "resourceVersion": "2209468"
  },
  "items": []
}
```

**NOTICE:** you need to use different `apiGroups` for different types of k8s resources:

- `""` (empty string) represents the core API group, which includes basic resources like `pods`, `services`, `configmaps`, etc.
- `"apps"` represents the apps API group, which includes resources like `deployments`, `statefulsets`, `daemonsets`, etc.
- `"batch"` represents the batch API group, which includes resources like `jobs`, `cronjobs`, etc.