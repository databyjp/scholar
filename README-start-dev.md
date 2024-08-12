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

### Investigate memory usage

Add the service to expose pprof usage with `kubectl apply -f pprof-service.yaml`

To see the memory profile:

- Text: `go tool pprof -top http://localhost:6060/debug/pprof/heap`
- Graphical: `go tool pprof -http=:8080 http://localhost:6060/debug/pprof/heap`

Note: Can delete the service with `kubectl delete service pprof-service -n weaviate`

### Cleanup

You can stop or delete a particular profile:

```shell
minikube stop
minikube delete
```

