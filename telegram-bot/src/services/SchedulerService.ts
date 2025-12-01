import cron from 'node-cron';
import { AppDataSource, User } from '../database';
import { NotificationService } from './NotificationService';
import { config } from '../config';
import { logger } from '../utils/logger';

export class SchedulerService {
  private notificationService: NotificationService;
  private dailyTask?: cron.ScheduledTask;
  private weeklyTask?: cron.ScheduledTask;

  constructor(notificationService: NotificationService) {
    this.notificationService = notificationService;
  }

  start(): void {
    if (config.notifications.enableDailyReports) {
      this.scheduleDailyReports();
    }

    if (config.notifications.enableWeeklyReports) {
      this.scheduleWeeklyReports();
    }

    logger.info('Scheduler service started');
  }

  stop(): void {
    if (this.dailyTask) {
      this.dailyTask.stop();
    }
    if (this.weeklyTask) {
      this.weeklyTask.stop();
    }
    logger.info('Scheduler service stopped');
  }

  private scheduleDailyReports(): void {
    const [hour, minute] = config.notifications.dailyReportTime.split(':');
    const cronExpression = `${minute} ${hour} * * *`;

    this.dailyTask = cron.schedule(cronExpression, async () => {
      logger.info('Running daily reports task');
      await this.sendDailyReports();
    });

    logger.info(`Daily reports scheduled at ${config.notifications.dailyReportTime}`);
  }

  private scheduleWeeklyReports(): void {
    const [hour, minute] = config.notifications.weeklyReportTime.split(':');
    const day = config.notifications.weeklyReportDay;
    const cronExpression = `${minute} ${hour} * * ${day}`;

    this.weeklyTask = cron.schedule(cronExpression, async () => {
      logger.info('Running weekly reports task');
      await this.sendWeeklyReports();
    });

    logger.info(
      `Weekly reports scheduled on day ${day} at ${config.notifications.weeklyReportTime}`,
    );
  }

  private async sendDailyReports(): Promise<void> {
    try {
      const userRepository = AppDataSource.getRepository(User);
      const users = await userRepository.find({
        where: { isActive: true },
      });

      for (const user of users) {
        try {
          await this.notificationService.sendDailyReport(user.telegramId);
          // Add small delay to avoid rate limiting
          await new Promise((resolve) => setTimeout(resolve, 100));
        } catch (error) {
          logger.error(`Failed to send daily report to user ${user.telegramId}:`, error);
        }
      }

      logger.info(`Daily reports sent to ${users.length} users`);
    } catch (error) {
      logger.error('Error sending daily reports:', error);
    }
  }

  private async sendWeeklyReports(): Promise<void> {
    try {
      const userRepository = AppDataSource.getRepository(User);
      const users = await userRepository.find({
        where: { isActive: true },
      });

      const weekNumber = this.getWeekNumber(new Date());
      const uptime = 99.5; // This should come from backend API

      for (const user of users) {
        try {
          await this.notificationService.sendWeeklyReport(user.telegramId, weekNumber, uptime);
          // Add small delay to avoid rate limiting
          await new Promise((resolve) => setTimeout(resolve, 100));
        } catch (error) {
          logger.error(`Failed to send weekly report to user ${user.telegramId}:`, error);
        }
      }

      logger.info(`Weekly reports sent to ${users.length} users`);
    } catch (error) {
      logger.error('Error sending weekly reports:', error);
    }
  }

  private getWeekNumber(date: Date): number {
    const onejan = new Date(date.getFullYear(), 0, 1);
    const millisecsInDay = 86400000;
    return Math.ceil(((date.getTime() - onejan.getTime()) / millisecsInDay + onejan.getDay() + 1) / 7);
  }
}
