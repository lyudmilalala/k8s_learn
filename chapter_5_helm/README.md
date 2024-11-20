## 5. Helm

Install Helm

```shell
$ curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
$ sudo apt-get install apt-transport-https--yes
$ echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg]
https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
$ sudo apt-get update
$ sudo apt-get install helm
```

Pull a project from Helm

Push a project to Helm

helm install loki-stack loki/loki-stack-2.9.11/loki-stack -n loki-logging --create-namespace --values loki/loki-local-values.yaml

Then visit `http://<host_ip>:30456` to see the Grafana dashboard.