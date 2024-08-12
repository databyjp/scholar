## Demo - Multiple minikube clusters

### Start multiple minikube profiles

This will start 3x minikube clusters with different resources.

```shell
minikube start --nodes=1 --memory=2024 --cpus=2 -p mk-small
minikube start --nodes=6 --memory=4048 --cpus=6 -p mk-large
minikube start --nodes=12 --memory=4048 --cpus=6 -p mk-vlarge
```

To see the status of the profiles:

```shell
minikube profile list
```

### Deploy Weaviate onto the clusters

Add the Weaviate Helm repository

```shell
helm repo add weaviate https://weaviate.github.io/weaviate-helm
```

Set up the single-node cluster

```shell
kubectl config use-context mk-small
kubectl create namespace weaviate
helm upgrade --install \
  "weaviate" \
  weaviate/weaviate \
  --namespace "weaviate" \
  --values ./values-01-single.yaml
kubectl get pods -n weaviate
minikube tunnel -p mk-small
```

Set up the multi-node cluster

```shell
kubectl config use-context mk-large
kubectl create namespace weaviate
helm upgrade --install \
  "weaviate" \
  weaviate/weaviate \
  --namespace "weaviate" \
  --values ./values-06-large.yaml
kubectl get pods -n weaviate
minikube tunnel -p mk-large
```

Set up an even larger cluster

```shell
kubectl config use-context mk-vlarge
kubectl create namespace weaviate
helm upgrade --install \
  "weaviate" \
  weaviate/weaviate \
  --namespace "weaviate" \
  --values ./values-12-vlarge.yaml
kubectl get pods -n weaviate
minikube tunnel -p mk-vlarge
```

### Try it out

Run `multinode-demo.ipynb`

Example commands to see what's going on:

```shell
minikube logs --profile=mk-small
minikube logs --profile=mk-large --node=mk-large
kubectl logs -n weaviate weaviate-0
```

### Take nodes down and see what happens!

Try this on different profiles. (Switch between profiles with `kubectl config use-context <profile>`.)

```shell
kubectl get nodes
minikube node stop minikube-m02
```

### Cleanup

You can stop or delete a particular profile:

```shell
minikube stop -p mk-small
minikube delete -p mk-small
```

Or delete all profiles:

```shell
minikube delete --all
```
