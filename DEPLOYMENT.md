# Ada Orchestration & Deployment Guide

**Deploy Ada anywhere - from local dev to production clusters**

## Deployment Options

| Platform | Best For | Complexity | GPU Support |
|----------|----------|------------|-------------|
| **Local (ada CLI)** | Development, personal use | ⭐ Easy | ✅ Native |
| **Docker Compose** | Single server, homelab | ⭐⭐ Simple | ✅ Passthrough |
| **Kubernetes** | Production, multi-tenant | ⭐⭐⭐⭐ Complex | ✅ Device plugins |
| **Nomad** | Edge, simpler clusters | ⭐⭐⭐ Medium | ✅ Device plugins |
| **systemd** | Bare metal, VPS | ⭐⭐ Simple | ✅ Native |

## Quick Links

- **[Local Mode](../docs/local_mode.rst)** - No Docker, just Python + Ollama
- **[Docker Compose](../compose.yaml)** - Single-server deployment
- **[Kubernetes](k8s/)** - Helm charts + manifests
- **[Nomad](k8s/nomad/)** - HashiCorp Nomad jobs
- **[systemd](#systemd-deployment)** - Linux service units

## Architecture Patterns

### Pattern 1: All-in-One (Development)

```
┌─────────────────────┐
│   Single Machine    │
│  ┌────┐ ┌────┐     │
│  │Ada │ │LLM │     │
│  └────┘ └────┘     │
└─────────────────────┘
```

**Best for:** Local development, testing  
**Deploy with:** ada CLI, Docker Compose  
**Resources:** 8GB RAM, 4 CPU

### Pattern 2: Separate LLM (Production)

```
┌──────────┐      ┌──────────┐
│   Ada    │─────▶│  Ollama  │
│  Cluster │      │ (shared) │
└──────────┘      └──────────┘
```

**Best for:** Multiple Ada instances, cost optimization  
**Deploy with:** Kubernetes, Nomad  
**Resources:** Brain: 2GB RAM per instance, Ollama: 16GB+ RAM

### Pattern 3: Multi-Tenant (SaaS)

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Ada-A   │  │ Ada-B   │  │ Ada-C   │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┴────────────┘
                  │
          ┌───────▼────────┐
          │  Shared Ollama │
          │  + Load Balancer│
          └────────────────┘
```

**Best for:** Multi-team, namespace isolation  
**Deploy with:** Kubernetes + Ingress  
**Resources:** Variable per tenant

### Pattern 4: Edge (IoT/ARM)

```
┌──────────────┐
│ Jetson/RPi5  │
│ ┌──┐  ┌────┐ │
│ │Ada│ │LLM│  │
│ └──┘  └────┘ │
└──────────────┘
```

**Best for:** Edge AI, offline operation  
**Deploy with:** ada CLI, systemd  
**Resources:** 4GB+ RAM, ARM64 CPU

## Kubernetes Deployment

### Quick Start

```bash
# Install Helm chart
helm install ada oci://ghcr.io/luna-system/charts/ada \
  --set ollama.model=deepseek-r1:14b \
  --set ingress.enabled=true \
  --set ingress.hostname=ada.example.com
```

### With GPU

```bash
helm install ada oci://ghcr.io/luna-system/charts/ada \
  --set ollama.gpu.enabled=true \
  --set ollama.gpu.type=nvidia \
  --set ollama.nodeSelector."nvidia\.com/gpu"=true
```

### Production (HA)

```bash
helm install ada oci://ghcr.io/luna-system/charts/ada \
  -f values-production.yaml \
  --set brain.replicaCount=3 \
  --set monitoring.enabled=true
```

**See [k8s/README.md](k8s/README.md) for complete guide**

## Nomad Deployment

### Quick Start

```bash
# Deploy to Nomad
nomad job run k8s/nomad/ada.nomad.hcl

# Check status
nomad status ada
```

### With GPU

```bash
nomad job run k8s/nomad/ada-gpu.nomad.hcl
```

**See [k8s/nomad/README.md](k8s/nomad/README.md) for complete guide**

## systemd Deployment

### Installation

```bash
# 1. Install Ada
git clone https://github.com/luna-system/ada.git /opt/ada
cd /opt/ada
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 2. Install service units
sudo cp k8s/systemd/ada-*.service /etc/systemd/system/
sudo systemctl daemon-reload

# 3. Start services
sudo systemctl enable --now ada-ollama
sudo systemctl enable --now ada-chroma
sudo systemctl enable --now ada-brain
```

### Status

```bash
sudo systemctl status ada-brain
sudo journalctl -u ada-brain -f
```

## Cloud Provider Examples

### AWS (EKS + GPU)

```bash
# Create EKS cluster with GPU nodes
eksctl create cluster -f k8s/examples/aws-eks-gpu.yaml

# Install Ada
helm install ada oci://ghcr.io/luna-system/charts/ada \
  --set ollama.gpu.enabled=true \
  --set ollama.persistence.storageClass=gp3
```

### GCP (GKE + TPU)

```bash
# Create GKE cluster
gcloud container clusters create ada-cluster \
  --accelerator type=nvidia-tesla-t4,count=1 \
  --machine-type n1-standard-4 \
  --num-nodes 3

# Install Ada
helm install ada oci://ghcr.io/luna-system/charts/ada \
  --set ollama.gpu.type=nvidia
```

### Azure (AKS + GPU)

```bash
# Create AKS cluster with GPU
az aks create -g ada-rg -n ada-cluster \
  --node-vm-size Standard_NC6s_v3 \
  --node-count 2

# Install Ada
helm install ada oci://ghcr.io/luna-system/charts/ada \
  --set ollama.gpu.enabled=true
```

## Configuration Management

### Helm Values

```yaml
# values-production.yaml
brain:
  replicaCount: 3
  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi"
      cpu: "2"

ollama:
  model: "deepseek-r1:14b"
  gpu:
    enabled: true
    type: nvidia
  persistence:
    size: "100Gi"
    storageClass: "fast-ssd"

chroma:
  persistence:
    size: "50Gi"

ingress:
  enabled: true
  hostname: "ada.example.com"
  tls:
    enabled: true
    secretName: "ada-tls"

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

### Kustomize Overlay

```yaml
# k8s/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

patchesStrategicMerge:
  - brain-deployment.yaml
  - resources.yaml

configMapGenerator:
  - name: ada-config
    literals:
      - OLLAMA_MODEL=deepseek-r1:14b
      - RAG_ENABLED=true
```

### Nomad Variables

```hcl
# variables.hcl
variable "model" {
  default = "deepseek-r1:14b"
}

variable "replicas" {
  default = 2
}

variable "enable_gpu" {
  default = false
}
```

## Monitoring & Observability

### Prometheus Metrics

All deployments expose Prometheus metrics:

```yaml
# ServiceMonitor (K8s)
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ada-brain
spec:
  selector:
    matchLabels:
      app: ada-brain
  endpoints:
    - port: metrics
      interval: 30s
```

### Grafana Dashboard

Import dashboard: `k8s/examples/grafana-dashboard.json`

Metrics:
- Request rate
- Response latency
- Memory usage
- GPU utilization
- RAG retrieval time
- Token generation rate

### Logging

```yaml
# FluentBit/Promtail config
[INPUT]
    Name tail
    Path /var/log/containers/ada-brain-*.log
    Tag ada.brain

[OUTPUT]
    Name loki
    Match ada.*
    Host loki:3100
```

## Security

### Network Policies

```yaml
# Restrict brain access
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ada-brain
spec:
  podSelector:
    matchLabels:
      app: ada-brain
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: ada-web
      ports:
        - protocol: TCP
          port: 7000
```

### Pod Security Standards

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ada-brain
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: brain
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop:
            - ALL
```

### Secrets Management

**Kubernetes:**
```bash
# Sealed Secrets
kubeseal < secret.yaml > sealed-secret.yaml
kubectl apply -f sealed-secret.yaml

# External Secrets Operator
kubectl apply -f k8s/examples/external-secret.yaml
```

**Nomad:**
```hcl
vault {
  policies = ["ada"]
}

template {
  data = <<EOH
{{ with secret "secret/ada" }}
API_KEY={{ .Data.data.key }}
{{ end }}
EOH
  destination = "secrets/api.env"
  env         = true
}
```

## Backup & Disaster Recovery

### Velero (Kubernetes)

```bash
# Install Velero
velero install --provider aws --bucket ada-backups

# Backup Ada namespace
velero backup create ada-backup --include-namespaces ada

# Restore
velero restore create --from-backup ada-backup
```

### Volume Snapshots

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: ollama-snapshot
spec:
  source:
    persistentVolumeClaimName: ada-ollama-data
```

### Restic (Nomad)

```bash
# Backup Nomad host volumes
restic -r s3:s3.amazonaws.com/ada-backups backup /opt/ollama/models
```

## Performance Tuning

### GPU Optimization

```yaml
# MIG (Multi-Instance GPU)
ollama:
  resources:
    limits:
      nvidia.com/mig-1g.10gb: 1
```

### CPU Optimization

```yaml
# NUMA awareness
ollama:
  nodeSelector:
    kubernetes.io/arch: amd64
  resources:
    requests:
      cpu: "8"  # Full NUMA node
```

### Storage Optimization

```yaml
# NVMe for models
ollama:
  persistence:
    storageClass: "nvme-ssd"
    
# Network storage for ChromaDB (backup-friendly)
chroma:
  persistence:
    storageClass: "nfs-client"
```

## Troubleshooting

### Common Issues

**Pod CrashLoopBackOff**
```bash
kubectl describe pod ada-brain-xxx
kubectl logs ada-brain-xxx --previous
```

**GPU Not Available**
```bash
kubectl get nodes -o json | jq '.items[].status.allocatable | ."nvidia.com/gpu"'
```

**Storage Full**
```bash
kubectl get pvc
kubectl describe pvc ada-ollama-data
df -h /mnt/ollama
```

**Network Issues**
```bash
kubectl exec ada-brain-xxx -- curl ollama:11434/api/tags
kubectl exec ada-brain-xxx -- curl chroma:8000/api/v1/heartbeat
```

## Migration Guides

### Docker Compose → Kubernetes

```bash
# 1. Export data
docker run --rm -v ada-v1_chroma-data:/data -v $(pwd)/backup:/backup \
  alpine tar czf /backup/data.tar.gz -C /data .

# 2. Create PVC in K8s
kubectl apply -f k8s/manifests/pvcs.yaml

# 3. Restore data
kubectl run -it restore --image=alpine --rm -- sh
tar xzf /backup/data.tar.gz -C /data

# 4. Deploy Ada
helm install ada oci://ghcr.io/luna-system/charts/ada
```

### Kubernetes → Nomad

```bash
# 1. Backup volumes
velero backup create ada-migration

# 2. Export to S3
velero backup download ada-migration

# 3. Deploy to Nomad
nomad job run ada.nomad.hcl

# 4. Restore from S3
nomad exec ada ollama restore s3://backup
```

## Production Checklist

- [ ] Resource requests/limits set
- [ ] Persistent storage configured
- [ ] Health checks enabled
- [ ] Monitoring/alerting configured
- [ ] Logging centralized
- [ ] Backup strategy tested
- [ ] Network policies applied
- [ ] Secrets externalized
- [ ] TLS certificates configured
- [ ] Autoscaling configured (if applicable)
- [ ] Disaster recovery plan documented
- [ ] Cost monitoring enabled
- [ ] Security scanning automated

## Support & Resources

- **Documentation**: https://ada-docs.readthedocs.io/
- **Issues**: https://github.com/luna-system/ada/issues
- **Discussions**: https://github.com/luna-system/ada/discussions
- **Helm Charts**: https://github.com/luna-system/charts
- **Matrix**: `#ada-kubernetes:matrix.org`

---

**Deploy Ada your way - from laptop to data center** 🚀
