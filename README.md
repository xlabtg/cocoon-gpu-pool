# Cocoon GPU Pool - Monitoring & Management System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.2+-blue.svg)](https://reactjs.org/)

Cocoon GPU Pool allows GPU owners to pool computing resources to participate in the Cocoon network, receiving passive income in TON for processing confidential calculations using TEE/SGX technologies.

This repository contains a comprehensive monitoring and management system for pool participants, featuring:

- 📊 **Real-time Performance Monitoring** - Track GPU utilization, inference requests, and profitability
- 💰 **Payment History & Tax Reports** - Complete payout tracking with export functionality
- 🔔 **Intelligent Alerting** - Get notified about worker issues, payments, and performance
- 🎯 **Pool Operator Dashboard** - Manage all participants and workers from a central interface
- 👤 **Participant Accounts** - Personal dashboards with detailed statistics
- 🤖 **Telegram Bot** - Manage workers and receive alerts via Telegram
- 📈 **Grafana Integration** - Advanced visualization with Prometheus metrics
- 🔐 **TON Wallet Authentication** - Secure access using TON blockchain wallets

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/xlabtg/cocoon-gpu-pool.git
cd cocoon-gpu-pool

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Access the dashboard
open http://localhost:3000
```

### Manual Setup

See [docs/SETUP.md](docs/SETUP.md) for detailed installation instructions.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  Dashboard | Workers | Payouts | Account | TON Connect      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  Workers | Participants | Payouts | Metrics | Alerts        │
└───┬────────────────┬─────────────────┬──────────────────────┘
    │                │                 │
┌───┴────┐     ┌─────┴──────┐    ┌────┴──────┐
│PostgreSQL│     │Prometheus  │    │  Redis    │
└──────────┘     │  Grafana   │    └───────────┘
                 └────────────┘
┌────────────────────────────────────────────────────────────┐
│           Telegram Bot (TypeScript/Node.js)                 │
│  /start | /status | /withdrawals | /settings | /help       │
└────────────────────────────────────────────────────────────┘
```

## Features

### Backend API
- **Worker Monitoring**: Automatic scraping of worker endpoints (`/stats`, `/jsonstats`, `/perf`)
- **Metrics Collection**: Time-series data storage with PostgreSQL
- **Alert System**: Configurable alerts for critical conditions
- **Payout Tracking**: Integration with TON blockchain for payment verification
- **REST API**: Comprehensive API with OpenAPI documentation
- **Prometheus Exporter**: Native metrics export for Prometheus

### Frontend Dashboard
- **Pool Overview**: Real-time statistics and performance charts
- **Worker Management**: Add, configure, and monitor GPU workers
- **Payout History**: Complete transaction history with tax export
- **Personal Account**: User profile and notification settings
- **TON Wallet Auth**: Secure authentication via TON Connect
- **Mobile Responsive**: Optimized for all device sizes

### Telegram Bot (TypeScript)
- **Account Management**: Register and link TON wallet addresses
- **Statistics**: View real-time worker performance and earnings
- **Payment History**: Track all payouts with detailed transaction info
- **Notifications**: Configurable alerts for payments, equipment issues, and reports
- **Multilingual**: Full support for Russian and English languages
- **Scheduled Reports**: Daily and weekly performance summaries

### Monitoring & Alerting
- **Prometheus Metrics**: Complete observability stack
- **Grafana Dashboards**: Pre-configured visualization dashboards
- **Alert Rules**: Worker down, high temperature, performance degradation
- **Multi-channel Notifications**: Email and Telegram alerts

## API Endpoints

See [docs/API.md](docs/API.md) for complete API documentation.

Key endpoints:
- `GET /api/v1/workers` - List all workers
- `GET /api/v1/workers/{id}/metrics` - Get worker metrics
- `GET /api/v1/payouts` - List payouts
- `GET /api/v1/payouts/export/tax-report` - Export tax report
- `GET /metrics` - Prometheus metrics

## Configuration

### Environment Variables

```env
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/cocoon_pool
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key

# TON Blockchain
TON_API_KEY=your-ton-api-key

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token

# Monitoring
WORKER_SCRAPE_INTERVAL=15  # seconds
ALERT_CHECK_INTERVAL=60     # seconds
```

### Worker Setup

Workers should expose these endpoints:
- `http://localhost:12000/stats` - Human-readable stats
- `http://localhost:12000/jsonstats` - JSON metrics
- `http://localhost:12000/perf` - Performance data

Multiple workers use incremental ports: 12000, 12010, 12020, etc.

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Documentation

- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [API Documentation](docs/API.md) - REST API reference
- [Architecture](ARCHITECTURE.md) - System architecture overview

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## Support

- **Telegram Community**: [t.me/xlab_tg](https://t.me/xlab_tg)
- **Documentation**: [cocoon.org/gpu-owners](https://cocoon.org/gpu-owners)
- **Issues**: [GitHub Issues](https://github.com/xlabtg/cocoon-gpu-pool/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the [Cocoon Network](https://cocoon.org)
- Powered by TON Blockchain
- Monitoring with Prometheus & Grafana
