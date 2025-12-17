# Ada on HashiCorp Nomad

**Deploy Ada using Nomad for orchestration**

Nomad is a simpler alternative to Kubernetes, great for smaller deployments or edge computing.

## Quick Start

```bash
# Deploy to Nomad cluster
nomad job run ada.nomad.hcl

# Check status
nomad status ada

# Access logs
nomad logs -f ada brain
```

## Architecture

```
                 Nomad Cluster
┌─────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐            │
│  │  Brain   │  │ ChromaDB │            │
│  │  (group) │  │  (group) │            │
│  └────┬─────┘  └─────┬────┘            │
│       │              │                  │
│  ┌────▼──────────────▼────┐            │
│  │      Ollama (group)     │            │
│  │      (with GPU)         │            │
│  └─────────────────────────┘            │
└─────────────────────────────────────────┘
```

## Features

✅ **Simpler than K8s** - Less complexity, easier to operate  
✅ **GPU support** - NVIDIA/AMD GPU constraints  
✅ **Consul integration** - Service discovery built-in  
✅ **Vault integration** - Secrets management  
✅ **Multi-region** - Deploy across data centers  
✅ **Host volumes** - Persistent storage for models

## Job Files

- `ada.nomad.hcl` - Full deployment (all services)
- `ada-brain-only.nomad.hcl` - Brain + external Ollama
- `ada-gpu.nomad.hcl` - GPU-optimized configuration
- `ada-edge.nomad.hcl` - Edge deployment (ARM64)

## Prerequisites

- Nomad 1.6+
- Consul (optional, for service discovery)
- Vault (optional, for secrets)
- Docker driver enabled
- GPU nodes (optional)

## Configuration

### Environment Variables

```hcl
env {
  OLLAMA_MODEL = "deepseek-r1:14b"
  RAG_ENABLED = "true"
  AI_NAME = "Ada"
  LOG_LEVEL = "info"
}
```

### Consul Service Discovery

```hcl
service {
  name = "ada-brain"
  port = "api"
  
  check {
    type     = "http"
    path     = "/v1/healthz"
    interval = "10s"
    timeout  = "2s"
  }
}
```

### Vault Secrets

```hcl
vault {
  policies = ["ada-secrets"]
}

template {
  data = <<EOH
{{ with secret "secret/ada/matrix" }}
MATRIX_ACCESS_TOKEN="{{ .Data.data.token }}"
{{ end }}
EOH
  destination = "secrets/matrix.env"
  env         = true
}
```

## GPU Support

### NVIDIA

```hcl
resources {
  cpu    = 4000
  memory = 8192
  
  device "nvidia/gpu" {
    count = 1
    
    constraint {
      attribute = "${device.attr.compute_capability}"
      operator  = ">="
      value     = "7.0"
    }
  }
}
```

### Constraints

```hcl
constraint {
  attribute = "${attr.unique.hostname}"
  operator  = "regexp"
  value     = "gpu-node.*"
}
```

## Storage

### Host Volumes

```hcl
# In client config (nomad agent)
client {
  host_volume "ollama-models" {
    path      = "/opt/ollama/models"
    read_only = false
  }
}

# In job spec
volume "models" {
  type      = "host"
  source    = "ollama-models"
  read_only = false
}
```

### CSI Volumes

```hcl
volume "chroma-data" {
  type            = "csi"
  source          = "chroma-vol"
  access_mode     = "single-node-writer"
  attachment_mode = "file-system"
}
```

## Networking

### Bridge Mode

```hcl
network {
  mode = "bridge"
  
  port "api" {
    static = 7000
    to     = 7000
  }
}
```

### Host Mode (GPU access)

```hcl
network {
  mode = "host"
  
  port "api" {
    static = 7000
  }
}
```

## Scaling

### Update Strategy

```hcl
update {
  max_parallel     = 1
  min_healthy_time = "30s"
  healthy_deadline = "5m"
  auto_revert      = true
  canary           = 1
}
```

### Count

```hcl
group "brain" {
  count = 3  # Run 3 instances
  
  # Spread across nodes
  spread {
    attribute = "${node.unique.id}"
    weight    = 100
  }
}
```

## Monitoring

### Prometheus Integration

```hcl
service {
  name = "ada-brain"
  port = "api"
  
  tags = [
    "prometheus",
    "metrics"
  ]
  
  meta {
    metrics_path = "/metrics"
  }
}
```

### Logs

```bash
# Stream logs
nomad alloc logs -f <alloc-id> brain

# Export to Loki
nomad alloc logs -json <alloc-id> | promtail-client
```

## Deployment Examples

### Local Development

```bash
# Single-node Nomad
nomad agent -dev &

# Deploy
nomad job run ada-dev.nomad.hcl
```

### Production (HA)

```bash
# 3-server cluster, 5 clients
nomad job run -var="replicas=3" ada-ha.nomad.hcl
```

### Edge (ARM64 + GPU)

```bash
# Jetson Nano, Raspberry Pi 5
nomad job run ada-edge.nomad.hcl
```

## Migration from Docker Compose

```bash
# Use nomad-pack (experimental)
nomad-pack run ada --var="image=ada:latest"

# Or convert manually
docker-compose-to-nomad compose.yaml > ada.nomad.hcl
```

## Troubleshooting

### Check Allocation

```bash
nomad alloc status <alloc-id>
nomad alloc logs <alloc-id> brain
```

### GPU Not Available

```bash
# Check node attributes
nomad node status -verbose <node-id> | grep gpu

# Check device plugin
nomad node status -json <node-id> | jq '.Attributes["device.nvidia"]'
```

### Service Not Registered

```bash
# Check Consul
consul catalog services
consul catalog service ada-brain
```

## Best Practices

1. **Host volumes for models** - Avoid re-downloading on restart
2. **Spread constraints** - Distribute across nodes
3. **Health checks** - Use HTTP checks for all services
4. **Auto-revert** - Enable automatic rollback
5. **Resource limits** - Set CPU/memory reservations
6. **Consul DNS** - Use service discovery
7. **Vault secrets** - Never hardcode credentials
8. **Monitoring** - Export metrics to Prometheus
9. **Logging** - Centralize with Loki/Elasticsearch
10. **Backups** - Regular CSI volume snapshots

## Cost Optimization

### Spot Instances (AWS)

```hcl
constraint {
  attribute = "${meta.spot}"
  value     = "true"
}

reschedule {
  attempts  = 3
  interval  = "15m"
  unlimited = false
}
```

### Preemption

```hcl
migrate {
  max_parallel     = 1
  health_check     = "checks"
  min_healthy_time = "10s"
}
```

## Files

- `ada.nomad.hcl` - Main job specification
- `ada-gpu.nomad.hcl` - GPU-enabled deployment
- `ada-edge.nomad.hcl` - ARM64/edge deployment
- `variables.hcl` - Job variables
- `examples/` - Example configurations

## Support

- **Nomad Docs**: https://developer.hashicorp.com/nomad
- **Ada Issues**: https://github.com/luna-system/ada/issues

---

**Nomad: Simpler orchestration for AI workloads** 🚀
