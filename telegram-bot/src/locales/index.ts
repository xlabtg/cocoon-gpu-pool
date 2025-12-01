import { Language, LocaleStrings } from '../types';
import { en } from './en';
import { ru } from './ru';

const locales: Record<Language, LocaleStrings> = {
  en,
  ru,
};

export function getLocale(languageCode: string): LocaleStrings {
  const lang = (languageCode.toLowerCase().startsWith('ru') ? 'ru' : 'en') as Language;
  return locales[lang];
}

export function formatString(template: string, params: Record<string, string | number>): string {
  let result = template;
  for (const [key, value] of Object.entries(params)) {
    result = result.replace(new RegExp(`{${key}}`, 'g'), String(value));
  }
  return result;
}
