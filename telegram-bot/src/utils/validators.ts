/**
 * Validates TON wallet address format
 * TON addresses are typically 48 characters in base64url format
 */
export function isValidTonAddress(address: string): boolean {
  // Basic validation for TON address format
  // Real validation would require TON SDK
  const tonAddressRegex = /^[A-Za-z0-9_-]{48}$/;
  return tonAddressRegex.test(address);
}

/**
 * Formats a number for display
 */
export function formatNumber(num: number, decimals: number = 2): string {
  return num.toFixed(decimals);
}

/**
 * Formats a date for display
 */
export function formatDate(date: Date): string {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Truncates a hash for display
 */
export function truncateHash(hash: string, length: number = 16): string {
  if (hash.length <= length) return hash;
  return `${hash.slice(0, length / 2)}...${hash.slice(-length / 2)}`;
}
