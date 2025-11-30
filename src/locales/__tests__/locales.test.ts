import { getLocale, formatString } from '../index';

describe('Locales', () => {
  describe('getLocale', () => {
    it('should return English locale for en language code', () => {
      const locale = getLocale('en');
      expect(locale.start.welcome).toContain('Welcome');
    });

    it('should return Russian locale for ru language code', () => {
      const locale = getLocale('ru');
      expect(locale.start.welcome).toContain('Добро пожаловать');
    });

    it('should default to English for unknown language codes', () => {
      const locale = getLocale('fr');
      expect(locale.start.welcome).toContain('Welcome');
    });
  });

  describe('formatString', () => {
    it('should replace placeholders with values', () => {
      const template = 'Hello {name}, you have {count} messages';
      const result = formatString(template, { name: 'Alice', count: 5 });
      expect(result).toBe('Hello Alice, you have 5 messages');
    });

    it('should handle multiple occurrences of same placeholder', () => {
      const template = '{name} {name} {name}';
      const result = formatString(template, { name: 'Test' });
      expect(result).toBe('Test Test Test');
    });
  });
});
