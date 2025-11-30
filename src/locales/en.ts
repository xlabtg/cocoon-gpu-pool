import { LocaleStrings } from '../types';

export const en: LocaleStrings = {
  start: {
    welcome:
      '👋 Welcome to Cocoon GPU Pool Bot!\n\n' +
      'This bot helps you manage your GPU mining participation, track earnings, and receive notifications.\n\n' +
      'To get started, please link your TON wallet address.',
    enterWallet: '📝 Please enter your TON wallet address:',
    walletLinked: '✅ Your TON wallet has been successfully linked!\n\nUse /status to view your statistics.',
    invalidWallet: '❌ Invalid wallet address. Please try again.',
  },
  status: {
    title: '📊 Your Mining Statistics',
    hashrate: '⚡ Hashrate: {hashrate} H/s',
    earnings: '💰 Total Earnings: {amount} TON',
    dailyEarnings: '📅 Daily Earnings: {amount} TON',
    weeklyEarnings: '📈 Weekly Earnings: {amount} TON',
    activeDevices: '🖥️ Active Devices: {count}',
    lastActive: '🕐 Last Active: {time}',
    noData: 'No mining data available yet. Make sure your equipment is connected.',
  },
  withdrawals: {
    title: '💳 Payment History',
    noWithdrawals: 'No payments recorded yet.',
    amount: 'Amount: {amount} {currency}',
    status: 'Status: {status}',
    date: 'Date: {date}',
    transactionHash: 'Transaction: {hash}',
  },
  settings: {
    title: '⚙️ Notification Settings',
    paymentNotifications: '💰 Payment Notifications',
    equipmentWarnings: '⚠️ Equipment Warnings',
    dailyReports: '📅 Daily Reports',
    weeklyReports: '📈 Weekly Reports',
    language: '🌐 Language',
    updated: '✅ Settings updated successfully!',
  },
  help: {
    title: '❓ Help & Documentation',
    description:
      'Cocoon GPU Pool Bot allows you to manage your GPU mining participation and earn passive income in TON.\n\n',
    commands: {
      start: '/start - Register and link TON wallet',
      status: '/status - View current mining statistics',
      withdrawals: '/withdrawals - View payment history',
      settings: '/settings - Configure notification preferences',
      help: '/help - Show this help message',
    },
    support: '\n📞 Support: @xlab_tg\n🌐 Website: https://cocoon.org',
  },
  notifications: {
    payment: '💰 Payment Received!\n\nAmount: {amount} TON\nTransaction: {hash}\n\nCheck /withdrawals for details.',
    equipmentOffline:
      '⚠️ Equipment Alert\n\nDevice {deviceId} is offline.\nLast seen: {lastSeen}\n\nPlease check your equipment.',
    equipmentError:
      '❌ Equipment Error\n\nDevice {deviceId} encountered an error:\n{error}\n\nPlease investigate immediately.',
    dailyReport:
      '📅 Daily Report - {date}\n\n' +
      '⚡ Hashrate: {hashrate} H/s\n' +
      '💰 Earnings: {earnings} TON\n' +
      '🖥️ Active Devices: {devices}\n\n' +
      'Keep up the good work!',
    weeklyReport:
      '📈 Weekly Report - Week {week}\n\n' +
      '⚡ Avg Hashrate: {hashrate} H/s\n' +
      '💰 Total Earnings: {earnings} TON\n' +
      '🖥️ Active Devices: {devices}\n' +
      '📊 Uptime: {uptime}%\n\n' +
      'Great performance this week!',
  },
  errors: {
    general: '❌ An error occurred. Please try again later.',
    notRegistered: '⚠️ You are not registered. Please use /start to register first.',
    walletRequired: '⚠️ Please link your TON wallet first using /start.',
    serviceUnavailable: '🔧 Service temporarily unavailable. Please try again later.',
  },
  common: {
    yes: 'Yes',
    no: 'No',
    back: 'Back',
    cancel: 'Cancel',
    loading: 'Loading...',
    enabled: 'Enabled',
    disabled: 'Disabled',
  },
};
