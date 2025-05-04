In this chapter, we would like to learn logging and monitoring the resource usage in our k8s cluster. We will use the following tools:

Grafana - we use it to create and view the dashbaords of our logs and statistic data.
Loki - we use to it store and tag logs.
Promtail - we use it to collect logs from each k8s node to Loki.
Prometheus - we use it to collect time-series system performance metrics and summarize data through customized queries.

Prometheus + Grafana works for monitoring. Promtail + Loki + Grafana works for logging, known as the PLG stack.

Following the steps below to build up the full logging and monitoring system:
1. Go through the `README.md` in the `grafana` directory, and you will get an online platform for visualization all collected data. We will then add Prometheus and Loki as the data sources of this platform.
2. Go through the `README.md` in the `loki` directory to setup Loki and Promtail for logging. 
3. Go through the `README.md` in the `prometheus` directory to setup Prometheus for collecting pod resource metrics. 

`test_app` directory includes a simple stateless http web application, and will be included as an test sample in instructions.

All components are installed by `helm`, so you must first have `helm` installed on your k8s master server. [Follow this link to install helm.](https://helm.sh/docs/intro/install/)