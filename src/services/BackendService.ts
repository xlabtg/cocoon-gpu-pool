import axios, { AxiosInstance } from 'axios';
import { config } from '../config';
import { logger } from '../utils/logger';
import { UserStats, EquipmentStatus, Payment } from '../types';
import { CacheService } from './CacheService';

export class BackendService {
  private client: AxiosInstance;
  private cache: CacheService;

  constructor(cache: CacheService) {
    this.cache = cache;
    this.client = axios.create({
      baseURL: config.backend.apiUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${config.backend.apiKey}`,
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        logger.error('Backend API error:', {
          url: error.config?.url,
          status: error.response?.status,
          message: error.message,
        });
        throw error;
      },
    );
  }

  async getUserStats(userId: number): Promise<UserStats | null> {
    try {
      // Try cache first
      const cacheKey = `stats:${userId}`;
      const cached = await this.cache.get<UserStats>(cacheKey);
      if (cached) return cached;

      const response = await this.client.get(`/users/${userId}/stats`);
      const stats = response.data;

      // Cache for 5 minutes
      await this.cache.set(cacheKey, stats, 300);

      return stats;
    } catch (error) {
      logger.error(`Failed to fetch user stats for ${userId}:`, error);
      return null;
    }
  }

  async getUserPayments(userId: number, limit: number = 10): Promise<Payment[]> {
    try {
      const response = await this.client.get(`/users/${userId}/payments`, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      logger.error(`Failed to fetch user payments for ${userId}:`, error);
      return [];
    }
  }

  async getEquipmentStatus(userId: number): Promise<EquipmentStatus[]> {
    try {
      const response = await this.client.get(`/users/${userId}/equipment`);
      return response.data;
    } catch (error) {
      logger.error(`Failed to fetch equipment status for ${userId}:`, error);
      return [];
    }
  }

  async registerWebhook(url: string): Promise<boolean> {
    try {
      await this.client.post('/webhooks/register', { url });
      logger.info('Webhook registered successfully');
      return true;
    } catch (error) {
      logger.error('Failed to register webhook:', error);
      return false;
    }
  }
}
