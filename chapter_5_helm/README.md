## 5. Helm

[Official docs](https://helm.sh/docs/)

[Official chart hub](https://artifacthub.io/)

Helm is a Kubernetes package manager. It facilitates the deployment and management of the applications in different K8s environments. It's important terminologies includes:

- `Charts`: a bundle of predefined Kubernetes resources, typically consists of `templates`, `values.yaml`, and `chart.yaml`. 
    - `templates`: consists of all the metadata related to the deployment.
    - `values.yaml`: consists of default configurations needed for the application to function, can be changed along with the change of use case.
    - `chart.yaml`: uses Golang templating format to convert the configurations from `values.yaml` or Helm CLI lines to a Kubernetes manifest.
- `Tiller`: a server deployment listens and acts on the commands administered through the Helm CLI tool and convert those to Kubernetes manifests.
- `Release`: an instance of running charts. A single chart can be mapped to multiple releases due to varied configurations. 
- `Repository`: a collection of charts that can be shared and stored.

### 5.1 Install Helm

```shell
$ curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
$ sudo apt-get install apt-transport-https--yes
$ echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg]
https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
$ sudo apt-get update
$ sudo apt-get install helm
```

### 5.2 Install a helm release

Before installing, we first need to ensure that our helm knows the repository where our desired resource is. To add a repository for helm to search for resources, use

```shell
helm repo add <repo_name> <repo_url> 
```

You can use `helm repo list` to see all repositories you have already added.

Then you can search for charts in a repository by

```shell
helm search repo <repo_name>
```

For installing an existing chart release into our k8s cluster, we use

```shell
helm install <release-name> <chart-name>
```

Some of the frequently used parameters are:

`-n`: name the namespace where the release is deployed to 

`--create-namespace`: generate the namespace if the namespace mentioned in `-n` does not exist

`--generate-name`: generate a name for the new release automatically
`--values`: customize configuration file

For example, when we want to install Loki-Grafana for logging in our k8s cluster, we may use the following command:

```shell
$ helm repo add grafana https://grafana.github.io/helm-charts
$ helm repo update
$ helm install loki-stack grafana/loki-stack -n loki-logging --create-namespace --values loki-local-values.yaml
```

Here we first add the repository of Grafana. Then we update the repository to see all latest charts. Finally, we deploy the `grafana/loki-stack` chart to a local release named `loki-stack`, with customized parameters in local file `loki-local-values.yaml`.

### 5.3 Custommize the configuration of a helm release

Use the below command to save the default values of the helm chart in a YAML file.

```
helm show values grafana/loki-stack > loki-local-values.yaml
```

You can then modify this configuration file to fit your requirements, and use it when installing a new release with the `--values` parameter.

### 5.4 Switch to another helm repository

Because of the GFW, sometimes it would be hard to pull resouces from the github or google repositories. Here are some alternative choices. You can add them to your repository list.

```shell
$ helm repo list
$ helm repo remove stable
$ helm repo add stable https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts
$ helm repo add kaiyuanshe http://mirror.kaiyuanshe.cn/kubernetes/charts
$ helm repo add azure http://mirror.azure.cn/kubernetes/charts
$ helm repo add dandydev https://dandydeveloper.github.io/charts
$ helm repo add bitnami https://charts.bitnami.com/bitnami
```

Then when you search for a chart, the resources from these repositories will be available. Then you can pull and use them as usual.

```shell
$ helm pull bitnami/redis-cluster --version 8.1.2
$ helm install redis-cluster bitnami/redis-cluster --set global.storageClass=nfs,global.redis.password=xiagao --version 8.1.2
$ helm uninstall redis-cluster
```

But be careful, charts from these repositories may have serious dependency problems.

### 5.5 List all helm release in the current Kubernetes cluster

`helm list -n <release-ns>` or `helm ls -n <release-ns>` list the deployed releases in this k8s cluster for us. 

Remember you should never forget to take the namespace in your command. Otherwise you can find nothing in the `default` namespace.

Thing look as below

```shell
$ helm list -n loki-logging
NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART               APP VERSION
loki-stack      loki-logging    1               2024-12-21 17:47:33.469280818 +0800 CST deployed        loki-stack-2.9.11   v2.6.1 
```

### 5.6 Upgrade and rollback a helm release

After detecting the updates of a chart, you can updating your existing release.

Remember you should never forget to take the namespace in your command.

If you want to update the value config file of the release, use

```shell
helm upgrade <release-name> <chart-name> --values new_values.yml -n <release-ns>
```

If you want to upgrade to a higher version of the chart, use

```shell
helm upgrade <release-name> <chart-name> --version a.b.c -n <release-ns>
```

And if something breaks with the new chart, you can rollback your release by

```shell
helm rollback <release-name> <revision> -n <release-ns>
```

### 5.7 Uninstall a helm release

```shell
helm uninstall <release-name> -n <release-ns>
```

### 5.8 Create a helm chart by yourself

We can first create a framework of a chart by

```shell
helm create my-first-chart
```

Then you will get a folder with the following structure. It should be same as the `my-first-chart` folder in the current directory.

```shell
$ tree my-first-chart/
my-first-chart/
├── charts
├── Chart.yaml
├── templates
│   ├── deployment.yaml
│   ├── _helpers.tpl
│   ├── hpa.yaml
│   ├── ingress.yaml
│   ├── NOTES.txt
│   ├── serviceaccount.yaml
│   ├── service.yaml
│   └── tests
│       └── test-connection.yaml
└── values.yaml
```

Modify `Chart.yaml`, `templates/deployment.yaml`, `templates/service.yaml`, `values.yaml` as shown in the `my-first-chart` folder in the current directory. Make the chart similar to our `flask-app` service in chapter 3.2. 

There are many predefined functions look similar to `my-first-chart.fullname` in files in `templates`. These functions are defined in `templates/_helpers.tpl`. You can look into their definitions details or defined more functions for your convenience in this file.

You can examine the chart after modification by `lint`. You should be at the same location with your `my-first-chart` folder. It looks as below.

```shell
$ helm lint --strict my-first-chart
==> Linting my-first-chart
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

For more verification before real deployment, you can also output the k8s configuration yaml that will be generated from the helm chart by the following command. An example `template_sample.yaml` is also shown in the chapter folder.

```shell
helm template chart-demo my-first-chart -n chart-ns --create-namespace > template_sample.yaml
```

After ensuring the correctness of the chart, move it to the k8s master node, and then deploy it to the k8s cluster by the following command.

```shell
$ helm install chart-demo my-first-chart -n chart-ns --create-namespace 
NAME: chart-demo
LAST DEPLOYED: Wed Jan  1 23:31:22 2025
NAMESPACE: chart-ns
STATUS: deployed
REVISION: 1
$ helm list -n chart-ns
NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                       APP VERSION
chart-demo      chart-ns        1               2025-01-02 00:08:36.344770019 +0800 CST deployed        my-first-chart-0.0.1        1.16.0 
```

If the chart size is large, you can first pack it to a `.tgz` file, and then install it as previous operation.

```shell
$ helm package my-first-chart
$ helm install chart-demo my-first-chart-0.0.1.tgz -n chart-ns --create-namespace 
```

Test to request the servers.

```shell
curl -X POST 'http://112.74.104.158:30050/sum' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "[Jerry-learning-chart-demo-my-first-chart-6c84fd5b5-kwhzj] sum = 22", "status": 200}
```

We create a new config file `new_values.yaml`, in which only changed `appName` from "Jerry-learning" to "Jerry-learning2". Then upgrade the current release.

```shell
$ helm upgrade chart-demo my-first-chart --values my-first-chart/new_values.yaml -n chart-ns
Release "chart-demo" has been upgraded. Happy Helming!
NAME: chart-demo
LAST DEPLOYED: Thu Jan  2 00:08:36 2025
NAMESPACE: chart-ns
STATUS: deployed
REVISION: 2
```

You can see the pods are changing

```shell
$ kubectl get pods -n chart-ns
NAME                                         READY   STATUS        RESTARTS   AGE
chart-demo-my-first-chart-6c84fd5b5-8f9gh    1/1     Terminating   0          38m
chart-demo-my-first-chart-7944c59f8c-5ntvj   1/1     Running       0          32s
chart-demo-my-first-chart-7944c59f8c-b7jv2   1/1     Running       0          47s
chart-demo-my-first-chart-7944c59f8c-dtnkf   1/1     Running       0          16s
```

Check the request, you can see the `appName` has changed.

```shell
curl -X POST 'http://112.74.104.158:30050/sum' --header 'Content-Type: application/json' --data-raw '{"a": 7,"b": 15}'
{"msg": "[Jerry-learning2-chart-demo-my-first-chart-7944c59f8c-5ntvj] sum = 22", "status": 200}
```

### 5.9 Push your helm chart to Artifacthub

To publish your helm chart on Artifacthub, you need to first publish it as a git repository. You can use either GitHub or GitLab to approach this target. After then, sharing your repository url with Artifacthub will make things work. You can find further detail in [this post](https://www.devopsschool.com/blog/helm-tutorial-how-to-publish-chart-at-artifacthub/).

