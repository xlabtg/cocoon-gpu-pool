# Infrastructure Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the GPU Resource Pool infrastructure, from initial setup to production deployment and ongoing operations.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Smart Contract Deployment](#smart-contract-deployment)
3. [Backend Services Deployment](#backend-services-deployment)
4. [Worker Deployment](#worker-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [Security Hardening](#security-hardening)
7. [Operational Procedures](#operational-procedures)

## Prerequisites

### Hardware Requirements

**Control Plane (Pool Operator Infrastructure):**
- 1x Application Server
  - CPU: 8 cores minimum (16 cores recommended)
  - RAM: 32 GB minimum (64 GB recommended)
  - Storage: 500 GB SSD
  - Network: 1 Gbps connection
  - OS: Ubuntu 22.04 LTS or later

- 1x Database Server
  - CPU: 8 cores
  - RAM: 64 GB (for PostgreSQL + Redis)
  - Storage: 1 TB SSD (NVMe recommended)
  - Network: 1 Gbps connection

**Worker Nodes (Participant Infrastructure):**
- CPU: Intel TDX-capable processor (6th gen Xeon Scalable or later)
- RAM: 256+ GB
- GPU: NVIDIA H100 or newer with compute capability 9.0+
- Storage: 2 TB NVMe SSD
- Network: 1 Gbps dedicated connection
- OS: Linux 6.16+ (for full TDX support)

### Software Requirements

**Development Tools:**
```bash
# Node.js and package managers
node >= 18.0.0
npm >= 9.0.0
pnpm >= 8.0.0 (recommended)

# TON development tools
@ton/blueprint
@ton/ton
@ton/core

# Smart contract tools
func >= 0.4.0
fift >= 0.4.0

# Backend development
go >= 1.21 (for Go services)
python >= 3.11 (for ML components)
docker >= 24.0
docker-compose >= 2.20
```

**Infrastructure Tools:**
```bash
terraform >= 1.5.0
kubectl >= 1.28
helm >= 3.12
ansible >= 2.15
```

### Network Access

- TON mainnet RPC endpoint (or run your own node)
- Cocoon network access (ci.cocoon.org)
- Docker Hub or private container registry
- DNS management for pool gateway

## Smart Contract Deployment

### 1. Environment Setup

Create deployment configuration:

```bash
# .env.production
TON_NETWORK=mainnet
TON_ENDPOINT=https://toncenter.com/api/v2/jsonRPC
DEPLOYER_WALLET_MNEMONIC="your wallet mnemonic"
POOL_OPERATOR_WALLET="EQD..."
COCOON_ROOT_ADDRESS="EQC..."  # From Cocoon network

# Pool configuration
POOL_NAME="YourPoolName"
POOL_FEE_BPS=500  # 5%
MIN_PARTICIPANT_STAKE=100000000000  # 100 TON
MAX_PARTICIPANTS=100
EPOCH_DURATION_SEC=604800  # 7 days
```

### 2. Compile Contracts

```bash
# Clone repository
git clone https://github.com/your-org/gpu-pool-contracts
cd gpu-pool-contracts

# Install dependencies
npm install

# Compile contracts
npx blueprint build

# Verify compilation
ls -la build/
# Should see:
# - PoolOperator.compiled.json
# - RewardDistribution.compiled.json
# - ParticipantRegistry.compiled.json
```

### 3. Deploy PoolOperator Contract

```typescript
// scripts/deploy-pool-operator.ts
import { toNano } from '@ton/core';
import { PoolOperator } from '../wrappers/PoolOperator';
import { compile, NetworkProvider } from '@ton/blueprint';

export async function run(provider: NetworkProvider) {
    const poolOperator = provider.open(PoolOperator.createFromConfig({
        pool_id: 1,
        owner_address: provider.sender().address,
        cocoon_root_address: Address.parse(process.env.COCOON_ROOT_ADDRESS!),
        pool_fee_bps: parseInt(process.env.POOL_FEE_BPS!),
        min_participant_stake: BigInt(process.env.MIN_PARTICIPANT_STAKE!),
        max_participants: parseInt(process.env.MAX_PARTICIPANTS!),
    }, await compile('PoolOperator')));

    await poolOperator.sendDeploy(provider.sender(), toNano('0.5'));

    await provider.waitForDeploy(poolOperator.address);

    console.log('PoolOperator deployed at:', poolOperator.address.toString());

    // Store address for next deployments
    process.env.POOL_OPERATOR_ADDRESS = poolOperator.address.toString();
}
```

Deploy:
```bash
npx blueprint run deployPoolOperator --mainnet
```

### 4. Deploy ParticipantRegistry Contract

```typescript
// scripts/deploy-participant-registry.ts
export async function run(provider: NetworkProvider) {
    const registry = provider.open(ParticipantRegistry.createFromConfig({
        pool_operator_address: Address.parse(process.env.POOL_OPERATOR_ADDRESS!),
        min_stake_amount: BigInt(process.env.MIN_PARTICIPANT_STAKE!),
        withdrawal_delay_sec: 604800, // 7 days
        slash_percentage_bps: 1000, // 10%
    }, await compile('ParticipantRegistry')));

    await registry.sendDeploy(provider.sender(), toNano('0.5'));
    await provider.waitForDeploy(registry.address);

    console.log('ParticipantRegistry deployed at:', registry.address.toString());
    process.env.PARTICIPANT_REGISTRY_ADDRESS = registry.address.toString();
}
```

Deploy:
```bash
npx blueprint run deployParticipantRegistry --mainnet
```

### 5. Deploy RewardDistribution Contract

```typescript
// scripts/deploy-reward-distribution.ts
export async function run(provider: NetworkProvider) {
    const rewardDist = provider.open(RewardDistribution.createFromConfig({
        pool_operator_address: Address.parse(process.env.POOL_OPERATOR_ADDRESS!),
        participant_registry_address: Address.parse(process.env.PARTICIPANT_REGISTRY_ADDRESS!),
        epoch_duration_sec: parseInt(process.env.EPOCH_DURATION_SEC!),
        pool_fee_bps: parseInt(process.env.POOL_FEE_BPS!),
    }, await compile('RewardDistribution')));

    await rewardDist.sendDeploy(provider.sender(), toNano('0.5'));
    await provider.waitForDeploy(rewardDist.address);

    console.log('RewardDistribution deployed at:', rewardDist.address.toString());
    process.env.REWARD_DISTRIBUTION_ADDRESS = rewardDist.address.toString();
}
```

Deploy:
```bash
npx blueprint run deployRewardDistribution --mainnet
```

### 6. Initialize Pool

Link contracts and initialize:

```typescript
// scripts/initialize-pool.ts
export async function run(provider: NetworkProvider) {
    const poolOperator = provider.open(PoolOperator.createFromAddress(
        Address.parse(process.env.POOL_OPERATOR_ADDRESS!)
    ));

    // Initialize pool with contract references
    await poolOperator.sendInitialize(provider.sender(), {
        cocoon_root: Address.parse(process.env.COCOON_ROOT_ADDRESS!),
        participant_registry: Address.parse(process.env.PARTICIPANT_REGISTRY_ADDRESS!),
        reward_distribution: Address.parse(process.env.REWARD_DISTRIBUTION_ADDRESS!),
        pool_fee: parseInt(process.env.POOL_FEE_BPS!),
        min_stake: BigInt(process.env.MIN_PARTICIPANT_STAKE!),
        metadata: createPoolMetadata({
            name: process.env.POOL_NAME!,
            description: "GPU Resource Pool for Cocoon Network",
            website: "https://your-pool.com",
            contact: "operator@your-pool.com"
        })
    });

    console.log('Pool initialized successfully');
}
```

Execute:
```bash
npx blueprint run initializePool --mainnet
```

### 7. Verify Deployment

```typescript
// scripts/verify-deployment.ts
export async function run(provider: NetworkProvider) {
    const poolOperator = provider.open(PoolOperator.createFromAddress(
        Address.parse(process.env.POOL_OPERATOR_ADDRESS!)
    ));

    const info = await poolOperator.getPoolInfo();

    console.log('Pool Verification:');
    console.log('- Pool ID:', info.pool_id);
    console.log('- Owner:', info.owner_address.toString());
    console.log('- Pool State:', info.pool_state);
    console.log('- Fee (bps):', info.pool_fee_bps);
    console.log('- Participant Registry:', info.participant_registry_address.toString());
    console.log('- Reward Distribution:', info.reward_distribution_address.toString());

    console.log('\n✓ Smart contracts deployed and verified');
}
```

Run verification:
```bash
npx blueprint run verifyDeployment --mainnet
```

## Backend Services Deployment

### 1. Infrastructure Provisioning

Use Terraform to provision cloud infrastructure:

```hcl
# terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and networking
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# EKS cluster for backend services
module "eks" {
  source = "./modules/eks"

  cluster_name = "gpu-pool-backend"
  cluster_version = "1.28"
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids

  node_groups = {
    general = {
      instance_types = ["t3.xlarge"]
      min_size = 2
      max_size = 10
      desired_size = 3
    }
  }
}

# RDS PostgreSQL
module "database" {
  source = "./modules/rds"

  identifier = "gpu-pool-db"
  engine_version = "15.4"
  instance_class = "db.r6g.xlarge"
  allocated_storage = 1000

  database_name = "gpupool"
  master_username = var.db_username
  master_password = var.db_password

  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnet_ids
}

# ElastiCache Redis
module "redis" {
  source = "./modules/elasticache"

  cluster_id = "gpu-pool-cache"
  engine_version = "7.0"
  node_type = "cache.r6g.large"
  num_cache_nodes = 2

  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.cache_subnet_ids
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"

  name = "gpu-pool-gateway"
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnet_ids

  certificate_arn = var.ssl_certificate_arn
}
```

Apply infrastructure:
```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### 2. Kubernetes Deployment

Create Kubernetes configurations:

```yaml
# k8s/pool-gateway-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pool-gateway
  namespace: gpu-pool
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pool-gateway
  template:
    metadata:
      labels:
        app: pool-gateway
    spec:
      containers:
      - name: gateway
        image: your-registry/pool-gateway:v1.0.0
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        - name: TON_ENDPOINT
          value: "https://toncenter.com/api/v2/jsonRPC"
        - name: POOL_OPERATOR_ADDRESS
          valueFrom:
            configMapKeyRef:
              name: pool-config
              key: pool_operator_address
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: pool-gateway
  namespace: gpu-pool
spec:
  selector:
    app: pool-gateway
  ports:
  - port: 80
    targetPort: 8080
    name: http
  - port: 9090
    targetPort: 9090
    name: metrics
  type: LoadBalancer
```

```yaml
# k8s/worker-manager-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker-manager
  namespace: gpu-pool
spec:
  replicas: 2
  selector:
    matchLabels:
      app: worker-manager
  template:
    metadata:
      labels:
        app: worker-manager
    spec:
      serviceAccountName: worker-manager
      containers:
      - name: manager
        image: your-registry/worker-manager:v1.0.0
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: WORKER_IMAGE_URL
          value: "https://ci.cocoon.org/cocoon-worker-release-latest.tar.xz"
        - name: POOL_GATEWAY_URL
          value: "http://pool-gateway"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

```yaml
# k8s/contribution-tracker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: contribution-tracker
  namespace: gpu-pool
spec:
  replicas: 2
  selector:
    matchLabels:
      app: contribution-tracker
  template:
    metadata:
      labels:
        app: contribution-tracker
    spec:
      containers:
      - name: tracker
        image: your-registry/contribution-tracker:v1.0.0
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        - name: PARTICIPANT_REGISTRY_ADDRESS
          valueFrom:
            configMapKeyRef:
              name: pool-config
              key: participant_registry_address
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

Deploy to Kubernetes:
```bash
# Create namespace
kubectl create namespace gpu-pool

# Create secrets
kubectl create secret generic db-credentials \
  --from-literal=url="postgresql://user:pass@host:5432/gpupool" \
  -n gpu-pool

kubectl create secret generic redis-credentials \
  --from-literal=url="redis://host:6379" \
  -n gpu-pool

# Create config map
kubectl create configmap pool-config \
  --from-literal=pool_operator_address="$POOL_OPERATOR_ADDRESS" \
  --from-literal=participant_registry_address="$PARTICIPANT_REGISTRY_ADDRESS" \
  --from-literal=reward_distribution_address="$REWARD_DISTRIBUTION_ADDRESS" \
  -n gpu-pool

# Deploy services
kubectl apply -f k8s/pool-gateway-deployment.yaml
kubectl apply -f k8s/worker-manager-deployment.yaml
kubectl apply -f k8s/contribution-tracker-deployment.yaml
kubectl apply -f k8s/blockchain-interface-deployment.yaml

# Verify deployments
kubectl get pods -n gpu-pool
kubectl get services -n gpu-pool
```

### 3. Database Initialization

Run database migrations:

```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# Run migrations
\i migrations/001_initial_schema.sql
\i migrations/002_create_indexes.sql
\i migrations/003_create_functions.sql
```

Example migration:
```sql
-- migrations/001_initial_schema.sql
CREATE TABLE participants (
    address TEXT PRIMARY KEY,
    worker_id TEXT,
    gpu_model TEXT,
    gpu_count INTEGER,
    stake_amount BIGINT,
    status INTEGER,
    join_timestamp BIGINT,
    reputation_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contributions (
    id SERIAL PRIMARY KEY,
    participant_address TEXT REFERENCES participants(address),
    epoch_id BIGINT,
    task_id TEXT,
    tokens_processed INTEGER,
    timestamp BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE epochs (
    epoch_id BIGINT PRIMARY KEY,
    start_timestamp BIGINT,
    end_timestamp BIGINT,
    total_rewards BIGINT,
    status INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contributions_epoch ON contributions(epoch_id);
CREATE INDEX idx_contributions_participant ON contributions(participant_address);
CREATE INDEX idx_contributions_timestamp ON contributions(timestamp);
```

## Worker Deployment

### 1. Worker Node Preparation

On each worker node:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    build-essential \
    linux-headers-$(uname -r) \
    qemu-kvm \
    libvirt-daemon-system \
    libvirt-clients \
    bridge-utils

# Install NVIDIA drivers
sudo apt install -y nvidia-driver-535

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Cocoon dependencies
sudo apt install -y \
    intel-tdx \
    seal-server
```

Enable Intel TDX:
```bash
# Enable TDX in BIOS (hardware-specific)
# Then verify:
dmesg | grep -i tdx

# Expected output:
# [    X.XXXXXX] tdx: TDX module initialized
```

### 2. Deploy Worker Container

Create worker configuration:

```yaml
# worker-config.yaml
worker:
  pool_id: 1
  participant_address: "EQD..."  # Participant's wallet address
  payment_address: "EQR..."      # RewardDistribution contract
  proxy_address: "EQP..."        # Cocoon proxy (or pool gateway)

  worker_coefficient: 1000       # 1.0x pricing

  gpu_devices: [0, 1, 2, 3]     # GPU indices to use

resources:
  memory_limit: 48GB
  cpu_limit: 16

models:
  - name: "llama-3-70b"
    max_batch_size: 32
    max_context_length: 8192
  - name: "mixtral-8x7b"
    max_batch_size: 24
    max_context_length: 8192

tee:
  enabled: true
  type: "intel-tdx"
  sealed_keys_path: "/var/lib/cocoon/keys"

monitoring:
  metrics_port: 9090
  health_check_interval: 10s
  heartbeat_interval: 30s
  heartbeat_url: "http://pool-gateway/api/v1/contributions/heartbeat"
```

Deploy worker:
```bash
# Download worker image
wget https://ci.cocoon.org/cocoon-worker-release-latest.tar.xz

# Verify checksum (get from Cocoon root contract)
echo "$EXPECTED_CHECKSUM cocoon-worker-release-latest.tar.xz" | sha256sum -c

# Extract
tar -xf cocoon-worker-release-latest.tar.xz
cd cocoon-worker

# Configure
cp worker-config.yaml config/

# Deploy (launches TDX VM with worker)
./scripts/deploy-worker.sh \
  --config config/worker-config.yaml \
  --gpus 0,1,2,3 \
  --memory 48G

# Verify worker is running
docker ps | grep cocoon-worker

# Check logs
docker logs -f cocoon-worker

# Expected output:
# Worker initialized
# TDX attestation verified
# Connected to pool gateway
# Worker registered: worker-abc123
# Waiting for requests...
```

### 3. Register Worker with Pool

Register the participant with the pool:

```bash
# From participant wallet, send registration transaction
npx ton-cli call \
  --contract $POOL_OPERATOR_ADDRESS \
  --method pool_register_participant \
  --params '{
    "gpu_specification": {
      "model": "NVIDIA H100",
      "count": 4,
      "vram_gb": 320
    },
    "stake_amount": "100000000000"
  }' \
  --value 100.1  # 100 TON stake + 0.1 TON gas
```

Verify registration:
```bash
# Check participant status
curl https://pool-gateway.example.com/api/v1/workers

# Should see your worker listed
```

## Monitoring Setup

### 1. Prometheus Configuration

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Pool Gateway metrics
  - job_name: 'pool-gateway'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - gpu-pool
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: pool-gateway
        action: keep
      - source_labels: [__meta_kubernetes_pod_container_port_name]
        regex: metrics
        action: keep

  # Worker Manager metrics
  - job_name: 'worker-manager'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - gpu-pool
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: worker-manager
        action: keep

  # Worker metrics (remote workers)
  - job_name: 'workers'
    static_configs:
      - targets:
        - worker-1.example.com:9090
        - worker-2.example.com:9090
        # ... add all worker nodes

# Alerting rules
rule_files:
  - 'alerts.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

Alert rules:
```yaml
# prometheus/alerts.yml
groups:
  - name: pool_alerts
    interval: 30s
    rules:
      - alert: WorkerDown
        expr: up{job="workers"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Worker {{ $labels.instance }} is down"

      - alert: HighErrorRate
        expr: rate(inference_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate: {{ $value }}%"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency above 1s: {{ $value }}s"
```

Deploy Prometheus:
```bash
kubectl apply -f prometheus/prometheus-deployment.yaml
kubectl apply -f prometheus/prometheus-service.yaml
```

### 2. Grafana Dashboards

Deploy Grafana:
```bash
kubectl apply -f grafana/grafana-deployment.yaml
```

Import dashboards:
```json
// grafana/dashboards/pool-overview.json
{
  "dashboard": {
    "title": "GPU Pool Overview",
    "panels": [
      {
        "title": "Requests per Second",
        "targets": [
          {
            "expr": "rate(inference_requests_total[1m])"
          }
        ]
      },
      {
        "title": "Worker Status",
        "targets": [
          {
            "expr": "count by (status) (worker_status)"
          }
        ]
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

## Security Hardening

### 1. Network Security

```bash
# Configure firewall (UFW)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 9090/tcp  # Metrics (internal only)
sudo ufw enable

# Restrict SSH to key-only authentication
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 2. TLS/SSL Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pool-gateway-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - pool-gateway.example.com
      secretName: pool-gateway-tls
  rules:
    - host: pool-gateway.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: pool-gateway
                port:
                  number: 80
```

### 3. Secret Management

Use external secrets manager:
```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets \
  external-secrets/external-secrets \
  -n external-secrets-system \
  --create-namespace

# Configure AWS Secrets Manager backend
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets
  namespace: gpu-pool
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
EOF
```

## Operational Procedures

### Daily Operations

**Morning Checklist:**
1. Check dashboard for overnight alerts
2. Verify all workers are online
3. Review error logs
4. Check blockchain sync status

**Automated Tasks:**
- Contribution updates (hourly)
- Health checks (every 30s)
- Backup database (daily at 02:00 UTC)
- Log rotation (daily)

### Weekly Operations

**Epoch Management:**
```bash
# Sunday 23:55 UTC - Finalize current epoch
curl -X POST https://pool-gateway.example.com/api/v1/epochs/finalize \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Monday 00:05 UTC - Calculate distribution
./scripts/calculate-distribution.sh --epoch 156

# Monday 00:30 UTC - Execute distribution
./scripts/distribute-rewards.sh --epoch 156 --batch-size 10
```

**Performance Review:**
1. Review weekly metrics report
2. Analyze top/bottom performing workers
3. Adjust optimization model parameters
4. Update forecasts

### Monthly Operations

**Infrastructure Maintenance:**
1. Apply security patches
2. Review and optimize costs
3. Database maintenance (VACUUM, ANALYZE)
4. Update documentation

**Financial Operations:**
1. Withdraw operator fees
2. Reconcile accounting
3. Generate financial reports
4. Tax preparation (if applicable)

### Emergency Procedures

**Pool Pause:**
```bash
# Pause pool operations
curl -X POST https://pool-gateway.example.com/api/v1/pool/pause \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Verify paused
curl https://pool-gateway.example.com/api/v1/pool/stats
```

**Worker Emergency Shutdown:**
```bash
# Graceful shutdown
curl -X POST https://pool-gateway.example.com/api/v1/workers/$WORKER_ID/shutdown \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"graceful": true, "drain_timeout_sec": 60}'

# Force shutdown
docker stop cocoon-worker
```

**Contract Upgrade:**
See [Migration Plan](../MIGRATION_PLAN.md) for detailed upgrade procedures.

## Health Checks

**System Health Indicators:**

| Component | Healthy | Warning | Critical |
|-----------|---------|---------|----------|
| Pool Gateway | Uptime >99% | Uptime 95-99% | Uptime <95% |
| Worker Nodes | All active | 1-2 inactive | >2 inactive |
| Database | Latency <50ms | Latency 50-100ms | Latency >100ms |
| Blockchain Sync | <5 blocks behind | 5-20 blocks | >20 blocks |
| Error Rate | <0.1% | 0.1-1% | >1% |

**Monitoring Commands:**
```bash
# Check all services
kubectl get pods -n gpu-pool

# Check worker status
curl https://pool-gateway.example.com/api/v1/workers

# Check database
psql $DATABASE_URL -c "SELECT pg_database_size('gpupool');"

# Check blockchain sync
curl https://blockchain-api.example.com/api/v1/health
```

## Backup and Recovery

**Automated Backups:**
```bash
# Database backup (daily)
0 2 * * * pg_dump $DATABASE_URL | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz

# Contract state export (weekly)
0 0 * * 0 ./scripts/export-contract-state.sh
```

**Recovery Procedures:**
```bash
# Restore database
gunzip < /backups/db-20251130.sql.gz | psql $DATABASE_URL

# Redeploy services
kubectl apply -f k8s/

# Verify integrity
./scripts/verify-deployment.sh
```

## Conclusion

Following this deployment guide ensures a robust, secure, and scalable GPU resource pool infrastructure. Regular maintenance and monitoring are essential for optimal performance.

For troubleshooting, see [Troubleshooting Guide](TROUBLESHOOTING.md).
For upgrades, see [Migration Plan](../MIGRATION_PLAN.md).
