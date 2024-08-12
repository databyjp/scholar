## Demo - Multiple minikube clusters

### Start multiple minikube profiles

This will start 3x minikube clusters with different resources.

```shell
minikube start
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
kubectl create namespace weaviate
helm upgrade --install \
  "weaviate" \
  weaviate/weaviate \
  --namespace "weaviate" \
  --values ./values-dev.yaml
kubectl get pods -n weaviate
minikube tunnel
```

### Cleanup

You can stop or delete a particular profile:

```shell
minikube stop
minikube delete
```

