import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity('notification_settings')
export class NotificationSettings {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column({ unique: true })
  userId!: number;

  @Column({ default: true })
  paymentNotifications!: boolean;

  @Column({ default: true })
  equipmentWarnings!: boolean;

  @Column({ default: true })
  dailyReports!: boolean;

  @Column({ default: true })
  weeklyReports!: boolean;

  @CreateDateColumn()
  createdAt!: Date;

  @UpdateDateColumn()
  updatedAt!: Date;
}
