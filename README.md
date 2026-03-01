## Kubernetes Learning

This is a guide for learning k8s, involving multiple different topics required for using k8s in real production environments.

1. Install （TODO）
2. Create a simple stateless service (Busybox & Flask)
3. Useful pod configurations
4. Gateway & Interceptor (TODO Nginx & Traefik)
5. Authentication & Authorization (TODO)
6. Job （TODO the job creator part）
7. Use images from private repo
8. Helm (TODO: get an two deployment example)
9. Logging & Monitor (Loki & Prometheus & Grafana) （TODO format Loki and Prometheus concepts）
10. HPA
11. Persist Data to Volume
12. Call external services (TODO)
13. CRD & Operator  （TODO）
14. FaaS Framework KNative  （TODO）
15. Pod with multiple containers
16. Istio  （TODO）

When a pod should contain multiple containers?
1. Sidecar used for logging/monitoring
2. Adapter used for data format transformation
3. Ambassador used for service discovery and proxy
4. Init container used for minimizing the main container, this always used when initalization requires extra memory/tools/permissions

### Docker image proxy

If you fail to pull official images because of the GFW, please try to find the image [here](https://docker.aityp.com/). 
