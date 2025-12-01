import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn } from 'typeorm';

@Entity('payments')
export class Payment {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column()
  userId!: number;

  @Column('decimal', { precision: 18, scale: 8 })
  amount!: number;

  @Column({ default: 'TON' })
  currency!: string;

  @Column()
  transactionHash!: string;

  @Column({ default: 'pending' })
  status!: 'pending' | 'completed' | 'failed';

  @CreateDateColumn()
  createdAt!: Date;

  @Column({ nullable: true })
  processedAt?: Date;
}
