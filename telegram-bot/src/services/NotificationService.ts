import { Telegraf } from 'telegraf';
import { UserService } from './UserService';
import { BackendService } from './BackendService';
import { getLocale, formatString } from '../locales';
import { logger } from '../utils/logger';
import { formatNumber, formatDate, truncateHash } from '../utils/validators';

export class NotificationService {
  constructor(
    private bot: Telegraf,
    private userService: UserService,
    private backendService: BackendService,
  ) {}

  async sendPaymentNotification(userId: number, amount: number, hash: string): Promise<void> {
    try {
      const user = await this.userService.getUserByTelegramId(userId);
      if (!user) return;

      const settings = await this.userService.getNotificationSettings(user.id);
      if (!settings.paymentNotifications) return;

      const locale = getLocale(user.languageCode);
      const message = formatString(locale.notifications.payment, {
        amount: formatNumber(amount, 4),
        hash: truncateHash(hash),
      });

      await this.bot.telegram.sendMessage(user.telegramId, message);
      logger.info(`Payment notification sent to user ${userId}`);
    } catch (error) {
      logger.error(`Failed to send payment notification to user ${userId}:`, error);
    }
  }

  async sendEquipmentOfflineNotification(
    userId: number,
    deviceId: string,
    lastSeen: Date,
  ): Promise<void> {
    try {
      const user = await this.userService.getUserByTelegramId(userId);
      if (!user) return;

      const settings = await this.userService.getNotificationSettings(user.id);
      if (!settings.equipmentWarnings) return;

      const locale = getLocale(user.languageCode);
      const message = formatString(locale.notifications.equipmentOffline, {
        deviceId,
        lastSeen: formatDate(lastSeen),
      });

      await this.bot.telegram.sendMessage(user.telegramId, message);
      logger.info(`Equipment offline notification sent to user ${userId}`);
    } catch (error) {
      logger.error(`Failed to send equipment offline notification to user ${userId}:`, error);
    }
  }

  async sendEquipmentErrorNotification(
    userId: number,
    deviceId: string,
    error: string,
  ): Promise<void> {
    try {
      const user = await this.userService.getUserByTelegramId(userId);
      if (!user) return;

      const settings = await this.userService.getNotificationSettings(user.id);
      if (!settings.equipmentWarnings) return;

      const locale = getLocale(user.languageCode);
      const message = formatString(locale.notifications.equipmentError, {
        deviceId,
        error,
      });

      await this.bot.telegram.sendMessage(user.telegramId, message);
      logger.info(`Equipment error notification sent to user ${userId}`);
    } catch (error) {
      logger.error(`Failed to send equipment error notification to user ${userId}:`, error);
    }
  }

  async sendDailyReport(userId: number): Promise<void> {
    try {
      const user = await this.userService.getUserByTelegramId(userId);
      if (!user) return;

      const settings = await this.userService.getNotificationSettings(user.id);
      if (!settings.dailyReports) return;

      const stats = await this.backendService.getUserStats(user.id);
      if (!stats) return;

      const locale = getLocale(user.languageCode);
      const message = formatString(locale.notifications.dailyReport, {
        date: formatDate(new Date()),
        hashrate: formatNumber(stats.hashrate, 2),
        earnings: formatNumber(stats.dailyEarnings, 4),
        devices: stats.activeDevices.toString(),
      });

      await this.bot.telegram.sendMessage(user.telegramId, message);
      logger.info(`Daily report sent to user ${userId}`);
    } catch (error) {
      logger.error(`Failed to send daily report to user ${userId}:`, error);
    }
  }

  async sendWeeklyReport(userId: number, weekNumber: number, uptime: number): Promise<void> {
    try {
      const user = await this.userService.getUserByTelegramId(userId);
      if (!user) return;

      const settings = await this.userService.getNotificationSettings(user.id);
      if (!settings.weeklyReports) return;

      const stats = await this.backendService.getUserStats(user.id);
      if (!stats) return;

      const locale = getLocale(user.languageCode);
      const message = formatString(locale.notifications.weeklyReport, {
        week: weekNumber.toString(),
        hashrate: formatNumber(stats.hashrate, 2),
        earnings: formatNumber(stats.weeklyEarnings, 4),
        devices: stats.activeDevices.toString(),
        uptime: formatNumber(uptime, 1),
      });

      await this.bot.telegram.sendMessage(user.telegramId, message);
      logger.info(`Weekly report sent to user ${userId}`);
    } catch (error) {
      logger.error(`Failed to send weekly report to user ${userId}:`, error);
    }
  }
}
