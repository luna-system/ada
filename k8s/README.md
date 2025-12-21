# Ada Kubernetes Deployment Examples

**Run Ada on Kubernetes with ease!**

This directory contains production-ready Kubernetes manifests and Helm charts for deploying Ada.

## Quick Start Options

### Option 1: Helm Chart (Recommended)

```bash
# Add Ada Helm repo (once available)
helm repo add ada https://charts.ada.ai
helm repo update

# Install with defaults
helm install my-ada ada/ada

# Or customize
helm install my-ada ada/ada -f my-values.yaml
```

### Option 2: kubectl + kustomize

```bash
# Apply base manifests
kubectl apply -k k8s/base/

# Or with overlay (production)
kubectl apply -k k8s/overlays/production/
```

### Option 3: Raw manifests

```bash
kubectl apply -f k8s/manifests/
```

## Architecture

```
┌─────────────────────────────────────────┐
│          Ingress (optional)             │
│  ada.example.com → ada-web service      │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┴──────────────┐
    │                            │
┌───▼────┐  ┌──────┐  ┌─────────▼──┐
│ Web UI │  │ Brain│  │  Matrix    │
│ (nginx)│  │ API  │  │  Bridge    │
└────────┘  └──┬───┘  └────────────┘
               │
       ┌───────┴────────┐
       │                │
   ┌───▼───┐      ┌─────▼────┐
   │Ollama │      │ ChromaDB │
   │  LLM  │      │ VectorDB │
   └───────┘      └──────────┘
```

## Features

✅ **Production-ready** - Health checks, resource limits, liveness/readiness probes  
✅ **GPU support** - NVIDIA and AMD GPU node selectors  
✅ **Persistent storage** - PVC templates for models and data  
✅ **Scalable** - HPA templates for brain API replicas  
✅ **Secure** - NetworkPolicies, RBAC, secrets management  
✅ **Observable** - Prometheus metrics, logging integration  
✅ **Flexible** - Helm values for easy customization

## Directory Structure

```
k8s/
├── README.md              # This file
├── helm/                  # Helm chart
│   └── ada/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       └── README.md
├── manifests/             # Raw Kubernetes YAML
│   ├── namespace.yaml
│   ├── brain-deployment.yaml
│   ├── ollama-statefulset.yaml
│   ├── chroma-statefulset.yaml
│   ├── services.yaml
│   ├── ingress.yaml
│   └── configmaps.yaml
├── kustomize/             # Kustomize overlays
│   ├── base/
│   └── overlays/
│       ├── development/
│       ├── staging/
│       └── production/
└── examples/              # Example configurations
    ├── gpu-node-pool.yaml
    ├── storage-class.yaml
    └── monitoring.yaml
```

## Prerequisites

- Kubernetes 1.24+
- kubectl configured
- Helm 3+ (if using Helm)
- GPU nodes (optional, for GPU acceleration)
- StorageClass for persistent volumes
- Minimum: 3 nodes, 4 CPU, 16GB RAM each
- Recommended: GPU nodes with 8GB+ VRAM

## Configuration

### Helm Values

```yaml
# values.yaml - Common customizations
brain:
  replicaCount: 2
  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi"
      cpu: "2"

ollama:
  model: "qwen2.5-coder:7b"
  gpu:
    enabled: true
    type: "nvidia"  # or "amd"
  persistence:
    size: "50Gi"

chroma:
  persistence:
    size: "20Gi"

ingress:
  enabled: true
  hostname: "ada.example.com"
  tls:
    enabled: true
    secretName: "ada-tls"
```

### Environment Variables

Configure via ConfigMap or Helm values:

```yaml
env:
  OLLAMA_MODEL: "qwen2.5-coder:7b"
  RAG_ENABLED: "true"
  AI_NAME: "Ada"
  LOG_LEVEL: "info"
```

## Deployment Modes

### Development (CPU-only, minimal resources)

```bash
helm install ada ada/ada \
  --set ollama.gpu.enabled=false \
  --set brain.replicaCount=1 \
  --set resources.requests.memory=1Gi
```

### Production (GPU, HA, monitoring)

```bash
helm install ada ada/ada \
  -f values-production.yaml \
  --set monitoring.enabled=true \
  --set brain.replicaCount=3 \
  --set ollama.gpu.enabled=true
```

### Hybrid (External Ollama)

```bash
# Use existing Ollama cluster
helm install ada ada/ada \
  --set ollama.enabled=false \
  --set ollama.externalUrl=http://ollama-cluster:11434
```

## GPU Support

### NVIDIA GPUs

```yaml
ollama:
  gpu:
    enabled: true
    type: nvidia
  nodeSelector:
    nvidia.com/gpu: "true"
  resources:
    limits:
      nvidia.com/gpu: 1
```

### AMD GPUs (ROCm)

```yaml
ollama:
  gpu:
    enabled: true
    type: amd
  nodeSelector:
    amd.com/gpu: "true"
  resources:
    limits:
      amd.com/gpu: 1
```

## Storage

### Ollama Models (Large, read-heavy)

```yaml
ollama:
  persistence:
    storageClass: "fast-ssd"  # or "nfs-client" for shared
    size: "100Gi"
    accessMode: ReadWriteOnce
```

### ChromaDB (Small, write-heavy)

```yaml
chroma:
  persistence:
    storageClass: "fast-ssd"
    size: "20Gi"
    accessMode: ReadWriteOnce
```

### Shared Models (Multi-node)

```yaml
ollama:
  persistence:
    storageClass: "nfs-client"  # Shared storage
    accessMode: ReadOnlyMany
```

## Networking

### Internal-only (no ingress)

```bash
# Port-forward for testing
kubectl port-forward svc/ada-brain 7000:7000
```

### Ingress (HTTPS)

```yaml
ingress:
  enabled: true
  className: "nginx"
  hostname: "ada.example.com"
  tls:
    enabled: true
    secretName: "ada-tls"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

### LoadBalancer

```yaml
brain:
  service:
    type: LoadBalancer
    annotations:
      cloud.provider.io/load-balancer-type: "nlb"
```

## Scaling

### Horizontal Pod Autoscaling

```yaml
brain:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
```

### Manual Scaling

```bash
kubectl scale deployment ada-brain --replicas=5
```

## Monitoring

### Prometheus Integration

```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
```

### Grafana Dashboard

```bash
# Import Ada dashboard
kubectl apply -f examples/grafana-dashboard.yaml
```

### Logs (Elasticsearch/Loki)

```yaml
logging:
  enabled: true
  backend: "loki"  # or "elasticsearch"
```

## Security

### Network Policies

```bash
# Apply network policies
kubectl apply -f manifests/networkpolicies.yaml
```

### Secrets Management

```yaml
# Using external secrets operator
secrets:
  provider: "aws-secretsmanager"  # or "vault", "gcp"
  region: "us-west-2"
```

### RBAC

```bash
# Minimal permissions
kubectl apply -f manifests/rbac.yaml
```

## Upgrading

### Helm

```bash
# Update chart
helm repo update

# Upgrade release
helm upgrade my-ada ada/ada -f values.yaml

# Rollback if needed
helm rollback my-ada
```

### kubectl

```bash
# Apply new manifests
kubectl apply -f k8s/manifests/

# Check rollout status
kubectl rollout status deployment/ada-brain
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n ada
kubectl describe pod ada-brain-xxx
kubectl logs ada-brain-xxx -f
```

### Health Checks

```bash
# Brain API
kubectl exec -it ada-brain-xxx -- curl localhost:7000/v1/healthz

# Ollama
kubectl exec -it ada-ollama-0 -- curl localhost:11434/api/tags
```

### GPU Not Detected

```bash
# Check GPU availability
kubectl get nodes -l nvidia.com/gpu=true

# Check device plugin
kubectl get pods -n kube-system | grep nvidia-device-plugin
```

### Storage Issues

```bash
# Check PVCs
kubectl get pvc -n ada

# Check PV binding
kubectl describe pvc ada-ollama-data
```

## Production Best Practices

1. **Resource Limits** - Always set requests/limits
2. **GPU Sharing** - Use MIG or time-slicing for multi-tenancy
3. **Persistent Storage** - Use fast SSDs for Ollama/ChromaDB
4. **Health Checks** - Configure liveness/readiness probes
5. **Monitoring** - Enable Prometheus metrics
6. **Backups** - Regular PVC snapshots
7. **Network Policies** - Restrict pod-to-pod traffic
8. **Secrets** - Use external secrets management
9. **Updates** - Rolling updates with readiness checks
10. **Disaster Recovery** - Test restore procedures

## Cost Optimization

### CPU-Only Deployment

```yaml
ollama:
  gpu:
    enabled: false
  nodeSelector:
    node.kubernetes.io/instance-type: "c6i.2xlarge"
```

### Spot Instances

```yaml
ollama:
  tolerations:
    - key: "spot"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
  nodeSelector:
    workload-type: "spot"
```

### Autoscaling with Scale-to-Zero

```yaml
brain:
  autoscaling:
    minReplicas: 0  # Scale to zero when idle
    scaleDownBehavior:
      stabilizationWindowSeconds: 300
```

## Multi-Tenancy

### Namespace Isolation

```bash
# Deploy per-tenant instances
helm install ada-team-a ada/ada -n team-a
helm install ada-team-b ada/ada -n team-b
```

### Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ada-quota
spec:
  hard:
    requests.cpu: "8"
    requests.memory: 32Gi
    nvidia.com/gpu: "2"
```

## Examples

See `examples/` directory for:
- `production-values.yaml` - Full production config
- `gpu-node-pool.yaml` - GKE/EKS GPU node pool
- `backup-cronjob.yaml` - Automated PVC backups
- `monitoring-stack.yaml` - Prometheus + Grafana
- `external-ollama.yaml` - Use shared Ollama cluster

## Support

- **Issues**: https://github.com/luna-system/ada/issues
- **Discussions**: https://github.com/luna-system/ada/discussions
- **Docs**: https://ada-docs.readthedocs.io/

## Contributing

Found a bug or have a better way to deploy? PRs welcome!

---

**Built with 💜 for platform engineers who want personal AI at scale**
