# Cocoon GPU Pool - Monitoring and Management System Architecture

## Overview
This document describes the architecture for the comprehensive monitoring and management system for Cocoon GPU Pool participants.

## System Components

### 1. Backend Service (`backend/`)
**Technology Stack:**
- Python 3.11+ with FastAPI
- PostgreSQL for data persistence
- Redis for caching and real-time data
- Prometheus client library for metrics
- SQLAlchemy ORM

**Core Modules:**
- **Metrics Collector**: Scrapes worker endpoints (`/stats`, `/jsonstats`, `/perf`) on ports 12000+
- **Performance Monitor**: Tracks GPU utilization, inference requests, profitability
- **Alert Manager**: Sends notifications for critical conditions (GPU failures, low performance, payment issues)
- **Payout Tracker**: Records TON blockchain payment history
- **REST API**: Exposes data to frontend and telegram bot

**Key Endpoints:**
```
GET  /api/v1/workers              - List all workers
GET  /api/v1/workers/{id}/metrics - Real-time worker metrics
GET  /api/v1/workers/{id}/stats   - Historical statistics
GET  /api/v1/payouts              - Payout history
GET  /api/v1/participants/{id}    - Participant profile
POST /api/v1/alerts/configure     - Configure alert rules
GET  /api/v1/export/tax-report    - Export tax data
```

### 2. Frontend Dashboard (`frontend/`)
**Technology Stack:**
- React 18 with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- Recharts for visualizations
- TanStack Query for data fetching
- TON Connect for wallet authentication

**Key Features:**
- Pool operator dashboard with aggregated metrics
- Participant personal accounts
- Real-time performance charts
- Payout history tables
- Tax report export
- Mobile-responsive design

**Pages:**
- `/dashboard` - Pool operator overview
- `/workers` - Worker management and monitoring
- `/participants` - Participant management
- `/payouts` - Payment history
- `/account` - Personal participant account
- `/settings` - Configuration and alerts

### 3. Telegram Bot (`telegram-bot/`)
**Technology Stack:**
- Python 3.11+ with python-telegram-bot
- Async/await for performance
- Shared database with backend

**Bot Commands:**
```
/start       - Register participant account
/stats       - View personal statistics
/payouts     - View payout history
/workers     - Manage GPU workers
/alerts      - Configure notifications
/help        - Get support
```

**Notifications:**
- Payment received alerts
- GPU/worker failure warnings
- Performance threshold alerts
- Scheduled statistics reports

### 4. Prometheus Integration (`monitoring/`)
**Components:**
- Prometheus server configuration
- Custom exporters for Cocoon workers
- Grafana dashboards
- Alert rules

**Metrics Exposed:**
```
cocoon_worker_status{worker_id, instance}
cocoon_gpu_utilization{worker_id, gpu_id}
cocoon_inference_requests_total{worker_id}
cocoon_inference_latency_seconds{worker_id, quantile}
cocoon_revenue_ton{worker_id, participant_id}
cocoon_worker_errors_total{worker_id, error_type}
```

## Database Schema

### Tables:
1. **participants** - User accounts with TON wallet addresses
2. **workers** - GPU worker instances
3. **worker_metrics** - Time-series performance data
4. **payouts** - Payment transaction history
5. **alerts** - Alert configurations and history
6. **alert_rules** - User-defined alert thresholds

## Security
- TON Wallet authentication for frontend
- API key authentication for backend services
- Telegram user verification
- Rate limiting on all APIs
- Encrypted storage of sensitive data

## Deployment
- Docker Compose for local development
- Kubernetes manifests for production
- Environment-based configuration
- Health check endpoints

## Monitoring Flow
```
Workers (ports 12000+)
  → Metrics Collector (scrapes every 15s)
    → PostgreSQL (stores historical data)
      → REST API (exposes data)
        → Frontend Dashboard / Telegram Bot
  → Prometheus (pulls metrics)
    → Grafana (visualizes)
    → Alert Manager (triggers notifications)
```

## Integration Points
- Worker HTTP endpoints: `/stats`, `/jsonstats`, `/perf`
- TON blockchain for payment verification
- Telegram API for bot functionality
- Prometheus for metrics aggregation
- Grafana for advanced visualization
