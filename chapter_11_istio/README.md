## Istio

Istio提供了k8s未提供的流量管理，服务发现和安全管理功能

通过为每一个pod配置一个sidecar容器，将业务app与服务管理完全分离

### 主要插件的职责

- Injector: 为每个pod注入envoy sidecar
- pilot: 服务发现和流量管理
- citadel：使用mtls双向加密实现安全管理
- gallery：设置和收集pod配置

VirtualService定义流量处理规则
DestinationRule将自定义流量规则匹配到具体的pod分组

Istio不擅长拿到比Pod粒度更细（比如App层面）的可观测性数据（链路跟踪，日志收集，指标监控），因此，目前最佳实践是将Prometheus，ELK等组件部署在Istio网格中，然后让应用主动向这些组件上报数据


分布式架构的可观测性要包含哪三个要素
- 链路跟踪（Zipkin, Skywalking, Jeager）
- 日志收集
- 指标监控（运行时定量数据）

OpenTelemetry (一站式采集指标监控，日志收集，链路跟踪所需要的数据，然将它们分发给各自的组件Zipkin，Promethus，ELK进行下一步处理，很新)

Loki相比起ELK存储体量小，检索速度高，无法全文检索

如何做到开发与生产对等
- /etc/hosts
- ConfigMap
- pvc挂载