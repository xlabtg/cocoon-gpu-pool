import { Context, Markup } from 'telegraf';
import { UserService } from '../services/UserService';
import { getLocale } from '../locales';
import { logger } from '../utils/logger';

export function registerSettingsCommand(bot: any, userService: UserService) {
  bot.command('settings', async (ctx: Context) => {
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
      const settings = await userService.getNotificationSettings(user.id);

      const keyboard = Markup.inlineKeyboard([
        [
          Markup.button.callback(
            `${locale.settings.paymentNotifications}: ${settings.paymentNotifications ? locale.common.enabled : locale.common.disabled}`,
            'toggle_payment',
          ),
        ],
        [
          Markup.button.callback(
            `${locale.settings.equipmentWarnings}: ${settings.equipmentWarnings ? locale.common.enabled : locale.common.disabled}`,
            'toggle_equipment',
          ),
        ],
        [
          Markup.button.callback(
            `${locale.settings.dailyReports}: ${settings.dailyReports ? locale.common.enabled : locale.common.disabled}`,
            'toggle_daily',
          ),
        ],
        [
          Markup.button.callback(
            `${locale.settings.weeklyReports}: ${settings.weeklyReports ? locale.common.enabled : locale.common.disabled}`,
            'toggle_weekly',
          ),
        ],
      ]);

      await ctx.reply(locale.settings.title, keyboard);
    } catch (error) {
      logger.error('Error in settings command:', error);
      const locale = getLocale(ctx.from?.language_code || 'en');
      await ctx.reply(locale.errors.general);
    }
  });

  // Handle settings toggles
  bot.action('toggle_payment', async (ctx: any) => {
    await handleSettingsToggle(ctx, userService, 'paymentNotifications');
  });

  bot.action('toggle_equipment', async (ctx: any) => {
    await handleSettingsToggle(ctx, userService, 'equipmentWarnings');
  });

  bot.action('toggle_daily', async (ctx: any) => {
    await handleSettingsToggle(ctx, userService, 'dailyReports');
  });

  bot.action('toggle_weekly', async (ctx: any) => {
    await handleSettingsToggle(ctx, userService, 'weeklyReports');
  });
}

async function handleSettingsToggle(
  ctx: any,
  userService: UserService,
  setting: 'paymentNotifications' | 'equipmentWarnings' | 'dailyReports' | 'weeklyReports',
) {
  try {
    const from = ctx.from;
    if (!from) return;

    const user = await userService.getUserByTelegramId(from.id);
    if (!user) return;

    const locale = getLocale(user.languageCode);
    const currentSettings = await userService.getNotificationSettings(user.id);

    await userService.updateNotificationSettings(user.id, {
      [setting]: !currentSettings[setting],
    });

    const updatedSettings = await userService.getNotificationSettings(user.id);

    const keyboard = Markup.inlineKeyboard([
      [
        Markup.button.callback(
          `${locale.settings.paymentNotifications}: ${updatedSettings.paymentNotifications ? locale.common.enabled : locale.common.disabled}`,
          'toggle_payment',
        ),
      ],
      [
        Markup.button.callback(
          `${locale.settings.equipmentWarnings}: ${updatedSettings.equipmentWarnings ? locale.common.enabled : locale.common.disabled}`,
          'toggle_equipment',
        ),
      ],
      [
        Markup.button.callback(
          `${locale.settings.dailyReports}: ${updatedSettings.dailyReports ? locale.common.enabled : locale.common.disabled}`,
          'toggle_daily',
        ),
      ],
      [
        Markup.button.callback(
          `${locale.settings.weeklyReports}: ${updatedSettings.weeklyReports ? locale.common.enabled : locale.common.disabled}`,
          'toggle_weekly',
        ),
      ],
    ]);

    await ctx.editMessageReplyMarkup(keyboard.reply_markup);
    await ctx.answerCbQuery(locale.settings.updated);
  } catch (error) {
    logger.error('Error handling settings toggle:', error);
    await ctx.answerCbQuery('Error updating settings');
  }
}
