import { AppDataSource, User, NotificationSettings } from '../database';
import { logger } from '../utils/logger';
import { CacheService } from './CacheService';

export class UserService {
  private cache: CacheService;

  constructor(cache: CacheService) {
    this.cache = cache;
  }

  async findOrCreateUser(
    telegramId: number,
    username?: string,
    firstName?: string,
    lastName?: string,
    languageCode: string = 'en',
  ): Promise<User> {
    const userRepository = AppDataSource.getRepository(User);

    let user = await userRepository.findOne({ where: { telegramId } });

    if (!user) {
      user = userRepository.create({
        telegramId,
        username,
        firstName,
        lastName,
        languageCode,
        isActive: true,
      });
      await userRepository.save(user);

      // Create default notification settings
      await this.createDefaultNotificationSettings(user.id);

      logger.info(`New user created: ${telegramId}`);
    } else {
      // Update user info if changed
      let updated = false;
      if (username && user.username !== username) {
        user.username = username;
        updated = true;
      }
      if (firstName && user.firstName !== firstName) {
        user.firstName = firstName;
        updated = true;
      }
      if (lastName && user.lastName !== lastName) {
        user.lastName = lastName;
        updated = true;
      }
      if (updated) {
        await userRepository.save(user);
      }
    }

    // Cache user data
    await this.cache.set(`user:${telegramId}`, user, 3600);

    return user;
  }

  async getUserByTelegramId(telegramId: number): Promise<User | null> {
    // Try cache first
    const cached = await this.cache.get<User>(`user:${telegramId}`);
    if (cached) return cached;

    const userRepository = AppDataSource.getRepository(User);
    const user = await userRepository.findOne({ where: { telegramId } });

    if (user) {
      await this.cache.set(`user:${telegramId}`, user, 3600);
    }

    return user;
  }

  async updateTonWallet(userId: number, tonWalletAddress: string): Promise<void> {
    const userRepository = AppDataSource.getRepository(User);
    await userRepository.update(userId, { tonWalletAddress });

    // Invalidate cache
    const user = await userRepository.findOne({ where: { id: userId } });
    if (user) {
      await this.cache.delete(`user:${user.telegramId}`);
    }

    logger.info(`TON wallet updated for user ${userId}`);
  }

  async getNotificationSettings(userId: number): Promise<NotificationSettings> {
    // Try cache first
    const cached = await this.cache.get<NotificationSettings>(`notifications:${userId}`);
    if (cached) return cached;

    const settingsRepository = AppDataSource.getRepository(NotificationSettings);
    let settings = await settingsRepository.findOne({ where: { userId } });

    if (!settings) {
      settings = await this.createDefaultNotificationSettings(userId);
    }

    await this.cache.set(`notifications:${userId}`, settings, 3600);
    return settings;
  }

  async updateNotificationSettings(
    userId: number,
    updates: Partial<NotificationSettings>,
  ): Promise<void> {
    const settingsRepository = AppDataSource.getRepository(NotificationSettings);
    await settingsRepository.update({ userId }, updates);

    // Invalidate cache
    await this.cache.delete(`notifications:${userId}`);

    logger.info(`Notification settings updated for user ${userId}`);
  }

  private async createDefaultNotificationSettings(userId: number): Promise<NotificationSettings> {
    const settingsRepository = AppDataSource.getRepository(NotificationSettings);
    const settings = settingsRepository.create({
      userId,
      paymentNotifications: true,
      equipmentWarnings: true,
      dailyReports: true,
      weeklyReports: true,
    });
    await settingsRepository.save(settings);
    return settings;
  }
}
