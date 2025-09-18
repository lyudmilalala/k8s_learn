To obtain enough privilege to get information about k8s resources by HTTP API, you need to:
1. Create a service account for the HTTP client.
2. Create a secret token for the service account.
3. Create a k8s cluster role with enough privilege.
4. Bind the service account with the cluster role.

The full required configuration is shown in `auth.yaml`.

**NOTICE:** `ServiceAccounts` and `Secrets` are namespace-scoped resources in Kubernetes. Remeber to create one for each namespace.

**NOTICE:** you need to use different `apiGroups` for different types of k8s resources:
- `""` (empty string) represents the core API group, which includes basic resources like `pods`, `services`, `configmaps`, etc.
- `"apps"` represents the apps API group, which includes resources like `deployments`, `statefulsets`, `daemonsets`, etc.
- `"batch"` represents the batch API group, which includes resources like `jobs`, `cronjobs`, etc.

After applying the `auth.yaml`, you can grab the value of the token `java-access-secret`.

For K8s version < 1.27, `service-account-token` does not have an expiration time. It can be used for long-running jobs.

```shell
$ kubectl apply -f auth.yaml
namespace/busybox-ns created
serviceaccount/busybox-admin created
secret/busybox-access-secret created
clusterrole.rbac.authorization.k8s.io/busybox-updater created
clusterrolebinding.rbac.authorization.k8s.io/busybox-auth-binding created
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

Then you can call apiserver with this token.

```shell
curl -k -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IncxNVYweUtCbGlZWnRFUmdrbzJaNWEwWWNHVUU4OFhVNkY3aFdpTWpweFUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJidXN5Ym94LW5zIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImJ1c3lib3gtYWNjZXNzLXNlY3JldCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJidXN5Ym94LWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNDgxMjU5NGYtZTkyMC00ODEyLWE0ZjUtMzM2OWQ5YTlkYmNmIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmJ1c3lib3gtbnM6YnVzeWJveC1hZG1pbiJ9.KPDhTaPQFxoyuWtRUvULJuVF162kreQRIz72drgRP0zc8K-eji65Av2upzE66ApuDG1oOEHD3UHUWNICfoFaAaUXIGjwpyu-Buz7Sm5GNMlo672ufIttAkjjljZJNwFS1weknmts2W0xHlCN-uvV-PgGcr4eU-FNvQFK3ARs8nc0qYXHrm8ZweytuOJdxd0NmxmLlj-kds_JKdIAyoBCeiJMb0FDWoIoAzBl6mARA2eOb1oqBsVvNUPlraTlKDZKU7h_iGcCf0h98unVg9SuceC3ETuHLT1kRS9DsVa1XGIZ20EMUFo8CAokO0CrRXeletkbFyfRPM9hrAz91TSfJw" https://47.115.170.172:6443/api/v1/namespaces/busybox-ns/pods/
```

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