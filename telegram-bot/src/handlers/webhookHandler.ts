import { Request, Response } from 'express';
import { NotificationService } from '../services/NotificationService';
import { logger } from '../utils/logger';

interface WebhookPayment {
  userId: number;
  amount: number;
  transactionHash: string;
}

interface WebhookEquipmentOffline {
  userId: number;
  deviceId: string;
  lastSeen: string;
}

interface WebhookEquipmentError {
  userId: number;
  deviceId: string;
  error: string;
}

interface WebhookPayload {
  type: 'payment' | 'equipment_offline' | 'equipment_error';
  data: WebhookPayment | WebhookEquipmentOffline | WebhookEquipmentError;
}

export class WebhookHandler {
  constructor(private notificationService: NotificationService) {}

  async handleWebhook(req: Request, res: Response): Promise<void> {
    try {
      const payload: WebhookPayload = req.body;

      switch (payload.type) {
        case 'payment':
          await this.handlePaymentWebhook(payload.data as WebhookPayment);
          break;
        case 'equipment_offline':
          await this.handleEquipmentOfflineWebhook(payload.data as WebhookEquipmentOffline);
          break;
        case 'equipment_error':
          await this.handleEquipmentErrorWebhook(payload.data as WebhookEquipmentError);
          break;
        default:
          logger.warn(`Unknown webhook type: ${payload.type}`);
      }

      res.status(200).json({ success: true });
    } catch (error) {
      logger.error('Error handling webhook:', error);
      res.status(500).json({ success: false, error: 'Internal server error' });
    }
  }

  private async handlePaymentWebhook(data: WebhookPayment): Promise<void> {
    logger.info(`Processing payment webhook for user ${data.userId}`);
    await this.notificationService.sendPaymentNotification(
      data.userId,
      data.amount,
      data.transactionHash,
    );
  }

  private async handleEquipmentOfflineWebhook(data: WebhookEquipmentOffline): Promise<void> {
    logger.info(`Processing equipment offline webhook for user ${data.userId}`);
    await this.notificationService.sendEquipmentOfflineNotification(
      data.userId,
      data.deviceId,
      new Date(data.lastSeen),
    );
  }

  private async handleEquipmentErrorWebhook(data: WebhookEquipmentError): Promise<void> {
    logger.info(`Processing equipment error webhook for user ${data.userId}`);
    await this.notificationService.sendEquipmentErrorNotification(
      data.userId,
      data.deviceId,
      data.error,
    );
  }
}
