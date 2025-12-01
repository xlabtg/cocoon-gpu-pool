# Cocoon GPU Pool - Setup Guide

This guide will help you set up the Cocoon GPU Pool monitoring and management system.

## Prerequisites

- Docker and Docker Compose (recommended)
- OR: Python 3.11+, Node.js 20+, PostgreSQL 16+, Redis 7+
- TON Wallet for authentication
- (Optional) Telegram Bot Token for bot functionality

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/xlabtg/cocoon-gpu-pool.git
cd cocoon-gpu-pool
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Backend Configuration
SECRET_KEY=your-secret-key-here
DEBUG=false
DATABASE_URL=postgresql://cocoon:cocoon@postgres:5432/cocoon_pool
REDIS_URL=redis://redis:6379/0

# TON Blockchain
TON_API_KEY=your-ton-api-key

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Grafana
GRAFANA_PASSWORD=admin
```

### 3. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Backend API (port 8000)
- Frontend dashboard (port 3000)
- Telegram bot
- Prometheus (port 9090)
- Grafana (port 3001)

### 4. Access the Dashboard

Open your browser and navigate to:
- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## Manual Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Telegram Bot Setup

```bash
cd telegram-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export TELEGRAM_BOT_TOKEN=your-token-here

# Start bot
python -m bot.main
```

## Database Migrations

To create a new migration:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Configuration

### Worker Monitoring

The system automatically scrapes metrics from GPU workers running on ports 12000, 12010, 12020, etc.

Workers should expose the following endpoints:
- `/stats` - Human-readable statistics
- `/jsonstats` - JSON-formatted metrics
- `/perf` - Performance data

### Adding a Worker

1. Navigate to the Dashboard
2. Connect your TON Wallet
3. Go to "Workers" page
4. Click "Add Worker"
5. Configure worker details:
   - Worker name
   - Instance number (0, 1, 2, ...)
   - Host and port
   - Price coefficient

### Alert Configuration

1. Go to "Account" → "Alerts"
2. Configure notification preferences:
   - Worker down alerts
   - High temperature warnings
   - Performance thresholds
   - Payment notifications

## Monitoring

### Prometheus Metrics

Access Prometheus at http://localhost:9090 to query metrics:

```promql
# GPU utilization
cocoon_gpu_utilization{worker_id="1"}

# Revenue
cocoon_revenue_ton{participant_id="1"}

# Worker status
cocoon_worker_status{worker_name="Worker-0"}
```

### Grafana Dashboards

1. Access Grafana at http://localhost:3001
2. Login with admin/admin
3. Import pre-configured dashboards from `monitoring/grafana/dashboards/`

## Telegram Bot

### Setting Up the Bot

1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Copy the bot token
3. Set `TELEGRAM_BOT_TOKEN` in `.env`
4. Start the bot service

### Available Commands

- `/start` - Register your account
- `/stats` - View statistics
- `/payouts` - View payout history
- `/workers` - Manage workers
- `/alerts` - Configure notifications
- `/help` - Get help

## Troubleshooting

### Database Connection Issues

```bash
# Check database is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Worker Not Appearing

1. Check worker is running and accessible
2. Verify worker endpoints respond:
   ```bash
   curl http://localhost:12000/stats
   curl http://localhost:12000/jsonstats
   ```
3. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

### Frontend Not Loading

```bash
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Check logs
docker-compose logs frontend
```

## Production Deployment

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS with reverse proxy (nginx/caddy)
- [ ] Configure firewall rules
- [ ] Set DEBUG=false
- [ ] Use environment-specific .env files
- [ ] Enable database backups
- [ ] Configure log rotation

### Recommended Architecture

```
Internet
  ↓
Nginx/Caddy (HTTPS, port 443)
  ↓
Frontend (port 3000) + Backend (port 8000)
  ↓
PostgreSQL + Redis
```

### Example Nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name pool.cocoon.org;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

## Support

- **Documentation**: https://cocoon.org/gpu-owners
- **Telegram Community**: https://t.me/xlab_tg
- **GitHub Issues**: https://github.com/xlabtg/cocoon-gpu-pool/issues
