import { Context } from 'telegraf';
import { UserService } from '../services/UserService';
import { getLocale } from '../locales';
import { logger } from '../utils/logger';

export function registerHelpCommand(bot: any, userService: UserService) {
  bot.command('help', async (ctx: Context) => {
    try {
      const from = ctx.from;
      if (!from) return;

      const user = await userService.getUserByTelegramId(from.id);
      const languageCode = user?.languageCode || from.language_code || 'en';
      const locale = getLocale(languageCode);

      const message = [
        locale.help.title,
        '',
        locale.help.description,
        locale.help.commands.start,
        locale.help.commands.status,
        locale.help.commands.withdrawals,
        locale.help.commands.settings,
        locale.help.commands.help,
        locale.help.support,
      ].join('\n');

      await ctx.reply(message);
    } catch (error) {
      logger.error('Error in help command:', error);
      const locale = getLocale(ctx.from?.language_code || 'en');
      await ctx.reply(locale.errors.general);
    }
  });
}
