import { DataSource } from 'typeorm';
import { config } from '../config';
import { User } from './entities/User';
import { NotificationSettings } from './entities/NotificationSettings';
import { Payment } from './entities/Payment';

export const AppDataSource = new DataSource({
  type: 'sqlite',
  database: config.database.path,
  synchronize: true,
  logging: config.env === 'development',
  entities: [User, NotificationSettings, Payment],
});

export async function initializeDatabase(): Promise<void> {
  try {
    await AppDataSource.initialize();
    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Error during database initialization:', error);
    throw error;
  }
}

export { User, NotificationSettings, Payment };
