import { isValidTonAddress, formatNumber, truncateHash } from '../validators';

describe('Validators', () => {
  describe('isValidTonAddress', () => {
    it('should validate correct TON address format', () => {
      const validAddress = 'EQDtFpEwcFAEcRe5mLVh2N6C0x-_hJEM7W61_JLnSF74p4q2';
      expect(isValidTonAddress(validAddress)).toBe(true);
    });

    it('should reject invalid TON address format', () => {
      expect(isValidTonAddress('invalid')).toBe(false);
      expect(isValidTonAddress('123')).toBe(false);
      expect(isValidTonAddress('')).toBe(false);
    });
  });

  describe('formatNumber', () => {
    it('should format numbers with specified decimals', () => {
      expect(formatNumber(1.23456, 2)).toBe('1.23');
      expect(formatNumber(1.23456, 4)).toBe('1.2346');
      expect(formatNumber(100, 2)).toBe('100.00');
    });
  });

  describe('truncateHash', () => {
    it('should truncate long hashes', () => {
      const hash = '0x1234567890abcdef1234567890abcdef12345678';
      const truncated = truncateHash(hash, 16);
      expect(truncated).toBe('0x123456...345678');
      expect(truncated.length).toBeLessThan(hash.length);
    });

    it('should not truncate short hashes', () => {
      const hash = '0x12345678';
      expect(truncateHash(hash, 16)).toBe(hash);
    });
  });
});
