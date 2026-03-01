## Appendix-1: Pod with multiple containers

Sometimes we would see a pod with multiple containers. Take `grafana` as an example, when you start a grafana pod and run `kubectl describe pod grafana`, you would see something as below.

Boradly speaking, the reasons for a pod to have multiple containers are:

1. Distinguish the responsibility of each submodule, excluding the initializaer, identifier, logger, monitor from the main business logic.
2. Make the core container slim, without tools for downloading sources, monitoring, etc.
3. Increse the flexibility of configuration.
4. Make some modules resuable.

And the reasons that these contaienrs are in the same pod is that we want them to share volumes and data. Also, we want them to share the same lifecycle, being created and deleted all together.

Some common design modes for a pod with multiple containers are as bleow.

|  Name  | Use case  |
|:--:|:--:|
|  Sidecar  | Use for logging, monitoring, etc.  |
|  Adaptor  | Use for data format transfer, e.g. transfer data format to save them in different storages. |
|  Ambassador  | Use as a load balancer, unifying the access path management. |
|  Initializer  | Use to initialize the applcation. |

Some common use cases for a pod with multiple containers are as below.

### 1. Use a different container for initialization

A common use case is that you need to insert some basic data into an application immediately after it starts, for example creating a default account. We probably want to use an extra container to do the data initialization.

Another use case is for applications with machine learning models. We may want to take advantage of latest models with multiple different encoding methods. At the same time migrating a model may need much larger memory than running a model, Thus we probably want to use a specific intialization container to download the latest model and transform it to the file format required by your applicstion.

### 2. Use a sidecar for logging or monitoring

### 3 Separate different functions into different containers


