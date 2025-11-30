export interface User {
  id: number;
  telegramId: number;
  username?: string;
  firstName?: string;
  lastName?: string;
  languageCode: string;
  tonWalletAddress?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface NotificationSettings {
  id: number;
  userId: number;
  paymentNotifications: boolean;
  equipmentWarnings: boolean;
  dailyReports: boolean;
  weeklyReports: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Payment {
  id: number;
  userId: number;
  amount: number;
  currency: string;
  transactionHash: string;
  status: 'pending' | 'completed' | 'failed';
  createdAt: Date;
  processedAt?: Date;
}

export interface PoolStats {
  totalHashrate: number;
  activeMiners: number;
  totalEarnings: number;
  dailyEarnings: number;
  weeklyEarnings: number;
  lastUpdate: Date;
}

export interface UserStats {
  userId: number;
  hashrate: number;
  totalEarnings: number;
  dailyEarnings: number;
  weeklyEarnings: number;
  activeDevices: number;
  lastActive: Date;
}

export interface EquipmentStatus {
  deviceId: string;
  userId: number;
  status: 'online' | 'offline' | 'error';
  hashrate: number;
  temperature?: number;
  errorMessage?: string;
  lastSeen: Date;
}

export interface BotContext {
  userId: number;
  languageCode: string;
}

export type Language = 'en' | 'ru';

export interface LocaleStrings {
  start: {
    welcome: string;
    enterWallet: string;
    walletLinked: string;
    invalidWallet: string;
  };
  status: {
    title: string;
    hashrate: string;
    earnings: string;
    dailyEarnings: string;
    weeklyEarnings: string;
    activeDevices: string;
    lastActive: string;
    noData: string;
  };
  withdrawals: {
    title: string;
    noWithdrawals: string;
    amount: string;
    status: string;
    date: string;
    transactionHash: string;
  };
  settings: {
    title: string;
    paymentNotifications: string;
    equipmentWarnings: string;
    dailyReports: string;
    weeklyReports: string;
    language: string;
    updated: string;
  };
  help: {
    title: string;
    description: string;
    commands: {
      start: string;
      status: string;
      withdrawals: string;
      settings: string;
      help: string;
    };
    support: string;
  };
  notifications: {
    payment: string;
    equipmentOffline: string;
    equipmentError: string;
    dailyReport: string;
    weeklyReport: string;
  };
  errors: {
    general: string;
    notRegistered: string;
    walletRequired: string;
    serviceUnavailable: string;
  };
  common: {
    yes: string;
    no: string;
    back: string;
    cancel: string;
    loading: string;
    enabled: string;
    disabled: string;
  };
}
