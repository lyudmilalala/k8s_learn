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
