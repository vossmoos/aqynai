# Aqyn Helm Chart

This Helm chart deploys the Aqyn application stack on Kubernetes, including:

- PostgreSQL database
- MinIO object storage
- Dagster webserver and daemon
- Hasura GraphQL engine  
- Aqyn API service

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (for persistent storage)

## Installing the Chart

1. **Clone or download the chart:**
   ```bash
   git clone <repository-url>
   cd aqyn-chart
   ```

2. **Create a custom values file:**
   ```bash
   cp values.yaml my-values.yaml
   ```

3. **Set required secrets in your values file:**
   ```yaml
   secrets:
     qdrantApiKey: "your-qdrant-api-key"
     openaiApiKey: "your-openai-api-key"
   ```

4. **Install the chart:**
   ```bash
   helm install aqyn . -f values.yaml
   ```

   Or install with inline values:
   ```bash
   helm install aqyn . \
     --set secrets.qdrantApiKey="your-qdrant-key" \
     --set secrets.openaiApiKey="your-openai-key"
   ```

## Upgrading the Chart

```bash
helm upgrade aqyn . -f my-values.yaml
```

## Uninstalling the Chart

```bash
helm uninstall aqyn
```

This removes all the Kubernetes components associated with the chart and deletes the release.

## Configuration

### Global Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Kubernetes namespace for all resources | `aqyn` |

### Application Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config.dagster.webserverPort` | Dagster webserver port | `"3000"` |
| `config.qdrant.host` | Qdrant service host | `"rag.aqyn.tech"` |
| `config.qdrant.port` | Qdrant service port | `"6333"` |
| `config.postgres.user` | PostgreSQL username | `"postgres"` |
| `config.postgres.password` | PostgreSQL password | `"postgres"` |
| `config.postgres.database` | PostgreSQL database name | `"dagster"` |

### Secrets

| Parameter | Description | Default |
|-----------|-------------|---------|
| `secrets.qdrantApiKey` | Qdrant API key (required) | `""` |
| `secrets.openaiApiKey` | OpenAI API key (required) | `""` |

### PostgreSQL

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgres.enabled` | Enable PostgreSQL deployment | `true` |
| `postgres.image.repository` | PostgreSQL image repository | `postgres` |
| `postgres.image.tag` | PostgreSQL image tag | `"13"` |
| `postgres.persistence.enabled` | Enable persistent storage | `true` |
| `postgres.persistence.size` | Storage size | `1Gi` |
| `postgres.resources.requests.cpu` | CPU request | `100m` |
| `postgres.resources.requests.memory` | Memory request | `256Mi` |

### MinIO

| Parameter | Description | Default |
|-----------|-------------|---------|
| `minio.enabled` | Enable MinIO deployment | `true` |
| `minio.image.repository` | MinIO image repository | `minio/minio` |
| `minio.image.tag` | MinIO image tag | `latest` |
| `minio.persistence.enabled` | Enable persistent storage | `true` |
| `minio.persistence.size` | Storage size | `1Gi` |

### Dagster

| Parameter | Description | Default |
|-----------|-------------|---------|
| `dagster.webserver.enabled` | Enable Dagster webserver | `true` |
| `dagster.webserver.replicaCount` | Number of webserver replicas | `1` |
| `dagster.webserver.image.repository` | Dagster image repository | `jyothiram266/dagster-app` |
| `dagster.webserver.image.tag` | Dagster image tag | `v1.0.0` |
| `dagster.daemon.enabled` | Enable Dagster daemon | `true` |

### Hasura

| Parameter | Description | Default |
|-----------|-------------|---------|
| `hasura.enabled` | Enable Hasura deployment | `true` |
| `hasura.replicaCount` | Number of Hasura replicas | `1` |
| `hasura.image.repository` | Hasura image repository | `hasura/graphql-engine` |
| `hasura.image.tag` | Hasura image tag | `v2.34.0` |

### API

| Parameter | Description | Default |
|-----------|-------------|---------|
| `api.enabled` | Enable API deployment | `true` |
| `api.replicaCount` | Number of API replicas | `1` |
| `api.image.repository` | API image repository | `jyothiram266/aqyn-api` |
| `api.image.tag` | API image tag | `v1.0.0` |

### Ingress

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.hosts[0].host` | Hostname | `aqyn.local` |

## Examples

### Development Environment

```yaml
# dev-values.yaml
config:
  postgres:
    password: "dev-password"
  hasura:
    devMode: "true"

postgres:
  persistence:
    size: 2Gi

minio:
  persistence:
    size: 5Gi

ingress:
  enabled: true
  hosts:
    - host: aqyn-dev.local
      paths:
        - path: /
          pathType: Prefix
          service: api-service
          port: 8000
```

### Production Environment

```yaml
# prod-values.yaml
config:
  postgres:
    password: "secure-production-password"
  hasura:
    devMode: "false"
    adminSecret: "super-secure-secret"

postgres:
  persistence:
    storageClass: "fast-ssd"
    size: 50Gi
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 4Gi

minio:
  persistence:
    storageClass: "fast-ssd" 
    size: 100Gi
  resources:
    requests:
      cpu: 500m
      memory: 1Gi

dagster:
  webserver:
    replicaCount: 2
    resources:
      requests:
        cpu: 500m
        memory: 1Gi

api:
  replicaCount: 3
  resources:
    requests:
      cpu: 500m
      memory: 1Gi

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: aqyn.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
          service: api-service
          port: 8000
  tls:
    - secretName: aqyn-tls
      hosts:
        - aqyn.yourdomain.com
```

## Accessing Services

After installation, you can access the services:

### Port Forwarding (for development)

```bash
# Dagster Web UI
kubectl port-forward service/aqyn-dagster-webserver-service 3000:3000 -n aqyn

# Hasura Console  
kubectl port-forward service/aqyn-hasura-service 8080:8080 -n aqyn

# API
kubectl port-forward service/aqyn-api-service 8000:8000 -n aqyn

# MinIO Console
kubectl port-forward service/aqyn-minio-service 9001:9001 -n aqyn
```

### Ingress (for production)

Configure ingress settings in your values file and access via your configured domain.

## Troubleshooting

### Check pod status:
```bash
kubectl get pods -n aqyn
```

### View logs:
```bash
kubectl logs -f deployment/aqyn-postgres -n aqyn
kubectl logs -f deployment/aqyn-dagster-webserver -n aqyn
```

### Check persistent volumes:
```bash
kubectl get pv,pvc -n aqyn
```

### Verify configuration:
```bash
kubectl get configmap aqyn-config -n aqyn -o yaml
```

## Security Considerations

1. **Change default passwords** in production environments
2. **Set strong admin secrets** for Hasura
3. **Use TLS/SSL** for production ingress
4. **Regularly update** container images
5. **Configure network policies** as needed
6. **Use secrets management** for sensitive data

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Kubernetes events: `kubectl get events -n aqyn`
3. Check application logs for specific services
4. Consult individual service documentation (Dagster, Hasura, etc.)