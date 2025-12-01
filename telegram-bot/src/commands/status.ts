import { Context } from 'telegraf';
import { UserService } from '../services/UserService';
import { BackendService } from '../services/BackendService';
import { getLocale, formatString } from '../locales';
import { formatNumber, formatDate } from '../utils/validators';
import { logger } from '../utils/logger';

export function registerStatusCommand(
  bot: any,
  userService: UserService,
  backendService: BackendService,
) {
  bot.command('status', async (ctx: Context) => {
    try {
      const from = ctx.from;
      if (!from) return;

      const user = await userService.getUserByTelegramId(from.id);
      if (!user) {
        const locale = getLocale(from.language_code || 'en');
        await ctx.reply(locale.errors.notRegistered);
        return;
      }

      const locale = getLocale(user.languageCode);

      if (!user.tonWalletAddress) {
        await ctx.reply(locale.errors.walletRequired);
        return;
      }

      const stats = await backendService.getUserStats(user.id);

      if (!stats) {
        await ctx.reply(locale.status.noData);
        return;
      }

      const message = [
        locale.status.title,
        '',
        formatString(locale.status.hashrate, { hashrate: formatNumber(stats.hashrate, 2) }),
        formatString(locale.status.earnings, { amount: formatNumber(stats.totalEarnings, 4) }),
        formatString(locale.status.dailyEarnings, {
          amount: formatNumber(stats.dailyEarnings, 4),
        }),
        formatString(locale.status.weeklyEarnings, {
          amount: formatNumber(stats.weeklyEarnings, 4),
        }),
        formatString(locale.status.activeDevices, { count: stats.activeDevices.toString() }),
        formatString(locale.status.lastActive, { time: formatDate(stats.lastActive) }),
      ].join('\n');

      await ctx.reply(message);
    } catch (error) {
      logger.error('Error in status command:', error);
      const locale = getLocale(ctx.from?.language_code || 'en');
      await ctx.reply(locale.errors.general);
    }
  });
}
