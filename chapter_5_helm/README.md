## 5. Helm

Helm is a Kubernetes package manager. It facilitates the deployment and management of the applications in different K8s environments. It's important terminologies includes:

- `Charts`: a bundle of predefined Kubernetes resources, typically consists of `templates`, `values.yaml`, and `chart.yaml`. 
    - `templates`: consists of all the metadata related to the deployment.
    - `values.yaml`: consists of default configurations needed for the application to function, can be changed along with the change of use case.
    - `chart.yaml`: uses Golang templating format to convert the configurations from `values.yaml` or Helm CLI lines to a Kubernetes manifest.
- `Tiller`: a server deployment listens and acts on the commands administered through the Helm CLI tool and convert those to Kubernetes manifests.
- `Release`: an instance of running charts. A single chart can be mapped to multiple releases due to varied configurations. 
- `Repository`: a collection of charts that can be shared and stored.


Install Helm

```shell
$ curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
$ sudo apt-get install apt-transport-https--yes
$ echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg]
https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
$ sudo apt-get update
$ sudo apt-get install helm
```

List all helm release in the current Kubernetes cluster

```shell
helm list
```

Install a helm release

`-n`: name the namespace where the release is deployed to 

`--values`: customize configuration file

```shell
helm install <release-name> <chart-name>
```

helm install loki-stack loki/loki-stack-2.9.11/loki-stack -n loki-logging --create-namespace --values loki/loki-local-values.yaml

Upgrade a helm release

```shell
helm upgrade <release-name> <chart-name>
```

Uninstall a helm release

```shell
helm uninstall <release-name>
```

Push a project to Helm



Then visit `http://<host_ip>:30456` to see the Grafana dashboard.