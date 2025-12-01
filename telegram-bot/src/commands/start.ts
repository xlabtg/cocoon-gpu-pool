import { Context } from 'telegraf';
import { UserService } from '../services/UserService';
import { getLocale } from '../locales';
import { isValidTonAddress } from '../utils/validators';
import { logger } from '../utils/logger';

export function registerStartCommand(
  bot: any,
  userService: UserService,
  userStates: Map<number, string>,
) {
  bot.command('start', async (ctx: Context) => {
    try {
      const from = ctx.from;
      if (!from) return;

      const user = await userService.findOrCreateUser(
        from.id,
        from.username,
        from.first_name,
        from.last_name,
        from.language_code || 'en',
      );

      const locale = getLocale(user.languageCode);

      if (user.tonWalletAddress) {
        await ctx.reply(locale.start.walletLinked);
      } else {
        await ctx.reply(locale.start.welcome);
        await ctx.reply(locale.start.enterWallet);
        userStates.set(from.id, 'awaiting_wallet');
      }
    } catch (error) {
      logger.error('Error in start command:', error);
      await ctx.reply('An error occurred. Please try again later.');
    }
  });

  // Handle wallet address input
  bot.on('text', async (ctx: Context, next: any) => {
    try {
      const from = ctx.from;
      if (!from || !('text' in ctx.message!)) return next();

      const state = userStates.get(from.id);
      if (state !== 'awaiting_wallet') return next();

      const text = ctx.message.text;
      const user = await userService.getUserByTelegramId(from.id);
      if (!user) return next();

      const locale = getLocale(user.languageCode);

      if (isValidTonAddress(text)) {
        await userService.updateTonWallet(user.id, text);
        await ctx.reply(locale.start.walletLinked);
        userStates.delete(from.id);
      } else {
        await ctx.reply(locale.start.invalidWallet);
      }
    } catch (error) {
      logger.error('Error handling wallet input:', error);
      await ctx.reply('An error occurred. Please try again later.');
    }
  });
}
