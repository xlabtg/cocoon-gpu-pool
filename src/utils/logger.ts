import winston from 'winston';
import { config } from '../config';
import { mkdirSync, existsSync } from 'fs';
import { dirname } from 'path';

// Ensure log directory exists
const logDir = dirname(config.logging.file);
if (!existsSync(logDir)) {
  mkdirSync(logDir, { recursive: true });
}

const logger = winston.createLogger({
  level: config.logging.level,
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json(),
  ),
  defaultMeta: { service: 'cocoon-bot' },
  transports: [
    new winston.transports.File({ filename: config.logging.file }),
    new winston.transports.File({
      filename: config.logging.file.replace('.log', '-error.log'),
      level: 'error',
    }),
  ],
});

if (config.env !== 'production') {
  logger.add(
    new winston.transports.Console({
      format: winston.format.combine(winston.format.colorize(), winston.format.simple()),
    }),
  );
}

export { logger };
