import { Telegraf } from 'telegraf';
import express from 'express';
import { config, validateConfig } from './config';
import { initializeDatabase } from './database';
import { CacheService } from './services/CacheService';
import { UserService } from './services/UserService';
import { BackendService } from './services/BackendService';
import { NotificationService } from './services/NotificationService';
import { SchedulerService } from './services/SchedulerService';
import { WebhookHandler } from './handlers/webhookHandler';
import { registerStartCommand } from './commands/start';
import { registerStatusCommand } from './commands/status';
import { registerWithdrawalsCommand } from './commands/withdrawals';
import { registerSettingsCommand } from './commands/settings';
import { registerHelpCommand } from './commands/help';
import { logger } from './utils/logger';

// User states for managing conversation flow
const userStates = new Map<number, string>();

async function main() {
  try {
    // Validate configuration
    validateConfig();
    logger.info('Configuration validated');

    // Initialize database
    await initializeDatabase();

    // Initialize services
    const cacheService = new CacheService();
    const userService = new UserService(cacheService);
    const backendService = new BackendService(cacheService);

    // Initialize bot
    const bot = new Telegraf(config.bot.token);
    const notificationService = new NotificationService(bot, userService, backendService);
    const schedulerService = new SchedulerService(notificationService);

    // Register commands
    registerStartCommand(bot, userService, userStates);
    registerStatusCommand(bot, userService, backendService);
    registerWithdrawalsCommand(bot, userService, backendService);
    registerSettingsCommand(bot, userService);
    registerHelpCommand(bot, userService);

    // Error handling
    bot.catch((err, ctx) => {
      logger.error('Bot error:', err);
      ctx.reply('An unexpected error occurred. Please try again later.').catch(() => {
        logger.error('Failed to send error message to user');
      });
    });

    // Start scheduler
    schedulerService.start();

    // Setup webhook or polling
    if (config.bot.webhookDomain) {
      // Webhook mode
      const app = express();
      app.use(express.json());

      // Webhook endpoint for backend notifications
      const webhookHandler = new WebhookHandler(notificationService);
      app.post('/webhook/notifications', (req, res) => webhookHandler.handleWebhook(req, res));

      // Telegram webhook
      const webhookPath = `/webhook/telegram/${config.bot.token}`;
      app.use(bot.webhookCallback(webhookPath));

      app.listen(config.bot.webhookPort, async () => {
        logger.info(`Webhook server listening on port ${config.bot.webhookPort}`);
        await bot.telegram.setWebhook(`${config.bot.webhookDomain}${webhookPath}`);
        logger.info('Telegram webhook set successfully');

        // Register backend webhook
        await backendService.registerWebhook(
          `${config.bot.webhookDomain}/webhook/notifications`,
        );
      });
    } else {
      // Long polling mode
      logger.info('Starting bot in polling mode');
      await bot.launch();
      logger.info('Bot started successfully');
    }

    // Graceful shutdown
    process.once('SIGINT', () => shutdown(bot, cacheService, schedulerService));
    process.once('SIGTERM', () => shutdown(bot, cacheService, schedulerService));

    logger.info('Cocoon GPU Pool Bot is running');
  } catch (error) {
    logger.error('Failed to start bot:', error);
    process.exit(1);
  }
}

async function shutdown(bot: Telegraf, cache: CacheService, scheduler: SchedulerService) {
  logger.info('Shutting down bot...');
  scheduler.stop();
  bot.stop('SIGTERM');
  await cache.disconnect();
  logger.info('Bot shut down successfully');
  process.exit(0);
}

main();
