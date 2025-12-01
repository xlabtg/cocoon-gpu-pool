import { Context } from 'telegraf';
import { UserService } from '../services/UserService';
import { BackendService } from '../services/BackendService';
import { getLocale, formatString } from '../locales';
import { formatNumber, formatDate, truncateHash } from '../utils/validators';
import { logger } from '../utils/logger';

export function registerWithdrawalsCommand(
  bot: any,
  userService: UserService,
  backendService: BackendService,
) {
  bot.command('withdrawals', async (ctx: Context) => {
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

      const payments = await backendService.getUserPayments(user.id, 10);

      if (payments.length === 0) {
        await ctx.reply(locale.withdrawals.noWithdrawals);
        return;
      }

      const messages = [locale.withdrawals.title, ''];

      for (const payment of payments) {
        const paymentInfo = [
          '───────────',
          formatString(locale.withdrawals.amount, {
            amount: formatNumber(payment.amount, 4),
            currency: payment.currency,
          }),
          formatString(locale.withdrawals.status, { status: payment.status }),
          formatString(locale.withdrawals.date, { date: formatDate(payment.createdAt) }),
          formatString(locale.withdrawals.transactionHash, {
            hash: truncateHash(payment.transactionHash),
          }),
        ];
        messages.push(...paymentInfo);
      }

      await ctx.reply(messages.join('\n'));
    } catch (error) {
      logger.error('Error in withdrawals command:', error);
      const locale = getLocale(ctx.from?.language_code || 'en');
      await ctx.reply(locale.errors.general);
    }
  });
}
