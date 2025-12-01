# Cocoon GPU Pool Telegram Bot

Cocoon GPU Pool allows GPU owners to pool computing resources to participate in the Cocoon network, receiving passive income in TON for processing confidential calculations using TEE/SGX technologies.

This repository contains the official Telegram Bot for managing participant accounts, receiving payment notifications, and viewing statistics.

## Features

### Commands

- `/start` - Register and link TON wallet
- `/status` - View current mining statistics
- `/withdrawals` - View payment history
- `/settings` - Configure notification preferences
- `/help` - Show help and documentation

### Notifications

- **Payment Notifications** - Instant alerts when you receive payments
- **Equipment Warnings** - Alerts when your mining equipment goes offline or encounters errors
- **Daily Reports** - Daily summary of your mining performance
- **Weekly Reports** - Comprehensive weekly statistics and earnings

### Multilingual Support

The bot supports both Russian and English languages, automatically detecting your Telegram language preference.

## Architecture

### Scalability Features

- **Caching Layer**: Redis-based caching to reduce database load and API calls
- **Database**: SQLite for development, easily upgradable to PostgreSQL for production
- **Error Handling**: Comprehensive error handling with automatic recovery
- **Logging**: Structured logging with Winston for monitoring and debugging
- **Webhooks**: Support for both webhook and long polling modes

### Technology Stack

- **TypeScript** - Type-safe development
- **Telegraf** - Modern Telegram Bot framework
- **TypeORM** - Database ORM with entity management
- **Redis** - High-performance caching
- **Express** - Webhook server
- **Node-cron** - Scheduled reports
- **Winston** - Professional logging

## Installation

### Prerequisites

- Node.js 18 or higher
- npm or yarn
- Redis (optional, for caching)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/xlabtg/cocoon-gpu-pool.git
cd cocoon-gpu-pool
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file from example:
```bash
cp .env.example .env
```

4. Configure your `.env` file:
```env
BOT_TOKEN=your_bot_token_from_botfather
BACKEND_API_URL=http://localhost:8080/api
BACKEND_API_KEY=your_api_key
```

5. Run in development mode:
```bash
npm run dev
```

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f bot
```

3. Stop the bot:
```bash
docker-compose down
```

### Production Deployment

For production deployment with webhook mode:

1. Set up your environment variables:
```env
BOT_TOKEN=your_production_bot_token
WEBHOOK_DOMAIN=https://your-domain.com
WEBHOOK_PORT=3000
BACKEND_API_URL=https://api.cocoon.org
NODE_ENV=production
```

2. Deploy with Docker:
```bash
docker-compose up -d
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram Bot token from BotFather | Required |
| `WEBHOOK_DOMAIN` | Domain for webhook mode (optional) | - |
| `WEBHOOK_PORT` | Port for webhook server | 3000 |
| `DB_TYPE` | Database type (sqlite/postgres) | sqlite |
| `DB_PATH` | SQLite database file path | ./data/bot.db |
| `REDIS_HOST` | Redis host for caching | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `BACKEND_API_URL` | Backend API endpoint | Required |
| `BACKEND_API_KEY` | Backend API authentication key | Required |
| `ENABLE_DAILY_REPORTS` | Enable daily reports | true |
| `ENABLE_WEEKLY_REPORTS` | Enable weekly reports | true |
| `LOG_LEVEL` | Logging level (info/debug/error) | info |
| `NODE_ENV` | Environment (development/production) | development |

## Testing

Run the test suite:
```bash
npm test
```

Run tests with coverage:
```bash
npm run test:coverage
```

Run tests in watch mode:
```bash
npm run test:watch
```

## Development

### Project Structure

```
src/
├── commands/          # Bot command handlers
│   ├── start.ts
│   ├── status.ts
│   ├── withdrawals.ts
│   ├── settings.ts
│   └── help.ts
├── config/           # Configuration management
├── database/         # Database entities and setup
│   └── entities/
├── handlers/         # Webhook and event handlers
├── locales/          # Internationalization
│   ├── en.ts
│   └── ru.ts
├── services/         # Business logic services
│   ├── BackendService.ts
│   ├── CacheService.ts
│   ├── NotificationService.ts
│   ├── SchedulerService.ts
│   └── UserService.ts
├── types/            # TypeScript type definitions
├── utils/            # Utility functions
└── index.ts          # Application entry point
```

### Code Quality

Lint your code:
```bash
npm run lint
```

Auto-fix linting issues:
```bash
npm run lint:fix
```

Format code:
```bash
npm run format
```

### Building

Build the project:
```bash
npm run build
```

## API Integration

### Backend Webhooks

The bot expects webhooks from the backend API for real-time notifications:

**Payment Notification:**
```json
POST /webhook/notifications
{
  "type": "payment",
  "data": {
    "userId": 123,
    "amount": 1.5,
    "transactionHash": "0x..."
  }
}
```

**Equipment Offline:**
```json
POST /webhook/notifications
{
  "type": "equipment_offline",
  "data": {
    "userId": 123,
    "deviceId": "gpu-001",
    "lastSeen": "2025-11-30T10:00:00Z"
  }
}
```

**Equipment Error:**
```json
POST /webhook/notifications
{
  "type": "equipment_error",
  "data": {
    "userId": 123,
    "deviceId": "gpu-001",
    "error": "Temperature too high"
  }
}
```

### Backend API Endpoints

The bot expects these endpoints from the backend API:

- `GET /users/{userId}/stats` - Get user mining statistics
- `GET /users/{userId}/payments` - Get user payment history
- `GET /users/{userId}/equipment` - Get user equipment status
- `POST /webhooks/register` - Register webhook URL

## Security Considerations

- Bot token and API keys are stored in environment variables
- User data is securely stored in the database
- All API communications use HTTPS in production
- Webhook endpoints validate request authenticity
- User inputs are validated and sanitized

## Support

- Telegram: [@xlab_tg](https://t.me/xlab_tg)
- Website: [https://cocoon.org](https://cocoon.org)
- Issues: [GitHub Issues](https://github.com/xlabtg/cocoon-gpu-pool/issues)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
