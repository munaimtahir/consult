/**
 * Simple logging service for the mobile app.
 * In production, this could be extended to send logs to a remote service.
 */

declare const __DEV__: boolean;

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  data?: unknown;
}

/**
 * Format a log entry for console output.
 */
function formatLogEntry(entry: LogEntry): string {
  const prefix = `[${entry.timestamp}] [${entry.level.toUpperCase()}]`;
  return `${prefix} ${entry.message}`;
}

/**
 * Create a log entry.
 */
function createLogEntry(level: LogLevel, message: string, data?: unknown): LogEntry {
  return {
    level,
    message,
    timestamp: new Date().toISOString(),
    data,
  };
}

/**
 * Logger service.
 */
export const logger = {
  /**
   * Log a debug message (only in development).
   */
  debug(message: string, data?: unknown): void {
    if (__DEV__) {
      const entry = createLogEntry('debug', message, data);
      console.debug(formatLogEntry(entry), data ?? '');
    }
  },

  /**
   * Log an info message.
   */
  info(message: string, data?: unknown): void {
    const entry = createLogEntry('info', message, data);
    if (__DEV__) {
      console.info(formatLogEntry(entry), data ?? '');
    }
    // TODO: In production, send to remote logging service
  },

  /**
   * Log a warning message.
   */
  warn(message: string, data?: unknown): void {
    const entry = createLogEntry('warn', message, data);
    if (__DEV__) {
      console.warn(formatLogEntry(entry), data ?? '');
    }
    // TODO: In production, send to remote logging service
  },

  /**
   * Log an error message.
   */
  error(message: string, error?: unknown): void {
    const entry = createLogEntry('error', message, error);
    if (__DEV__) {
      console.error(formatLogEntry(entry), error ?? '');
    }
    // TODO: In production, send to remote error tracking service (e.g., Sentry)
  },

  /**
   * Log an API request.
   */
  apiRequest(method: string, url: string, data?: unknown): void {
    if (__DEV__) {
      const message = `API ${method.toUpperCase()} ${url}`;
      const entry = createLogEntry('debug', message, data);
      console.debug(formatLogEntry(entry), data ?? '');
    }
  },

  /**
   * Log an API response.
   */
  apiResponse(method: string, url: string, status: number, data?: unknown): void {
    if (__DEV__) {
      const message = `API ${method.toUpperCase()} ${url} -> ${status}`;
      const entry = createLogEntry('debug', message, data);
      console.debug(formatLogEntry(entry), data ?? '');
    }
  },

  /**
   * Log an API error.
   */
  apiError(method: string, url: string, error: unknown): void {
    const message = `API ${method.toUpperCase()} ${url} -> ERROR`;
    const entry = createLogEntry('error', message, error);
    if (__DEV__) {
      console.error(formatLogEntry(entry), error);
    }
    // TODO: In production, send to remote error tracking service
  },
};
