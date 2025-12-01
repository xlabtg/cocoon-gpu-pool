import dotenv from 'dotenv';

dotenv.config();

export const config = {
  bot: {
    token: process.env.BOT_TOKEN || '',
    webhookDomain: process.env.WEBHOOK_DOMAIN || '',
    webhookPort: parseInt(process.env.WEBHOOK_PORT || '3000', 10),
  },
  database: {
    type: process.env.DB_TYPE || 'sqlite',
    path: process.env.DB_PATH || './data/bot.db',
  },
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD || undefined,
    db: parseInt(process.env.REDIS_DB || '0', 10),
  },
  backend: {
    apiUrl: process.env.BACKEND_API_URL || 'http://localhost:8080/api',
    apiKey: process.env.BACKEND_API_KEY || '',
  },
  notifications: {
    enableDailyReports: process.env.ENABLE_DAILY_REPORTS === 'true',
    enableWeeklyReports: process.env.ENABLE_WEEKLY_REPORTS === 'true',
    dailyReportTime: process.env.DAILY_REPORT_TIME || '09:00',
    weeklyReportDay: parseInt(process.env.WEEKLY_REPORT_DAY || '1', 10),
    weeklyReportTime: process.env.WEEKLY_REPORT_TIME || '09:00',
  },
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || './logs/bot.log',
  },
  env: process.env.NODE_ENV || 'development',
};

export function validateConfig(): void {
  if (!config.bot.token) {
    throw new Error('BOT_TOKEN is required');
  }
}
