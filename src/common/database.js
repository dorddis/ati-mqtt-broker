/**
 * Database setup for ATI data logging
 * Uses SQLite for simple, file-based storage
 */

import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ensure logs directory exists
const logsDir = path.join(__dirname, '..', '..', 'logs');
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
}

const dbPath = path.join(logsDir, 'ati_data.db');
const db = new Database(dbPath);

// Enable WAL mode for better concurrent access
db.pragma('journal_mode = WAL');

// Check if table already exists (to log appropriate message)
const tableExists = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='ati_messages'").get();
if (tableExists) {
    const count = db.prepare("SELECT COUNT(*) as count FROM ati_messages").get();
    console.log(`Database: Using existing database with ${count.count} messages`);
} else {
    console.log('Database: Creating new database tables');
}

// Create tables (safe: IF NOT EXISTS means no data loss)
db.exec(`
    CREATE TABLE IF NOT EXISTS ati_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        device_name TEXT NOT NULL,

        -- ATI raw data
        ati_x REAL NOT NULL,
        ati_y REAL NOT NULL,
        ati_heading REAL,

        -- Transformed Twinzo data
        twinzo_x REAL NOT NULL,
        twinzo_y REAL NOT NULL,
        twinzo_heading REAL,

        -- Status data
        battery_status INTEGER,
        mode TEXT,

        -- Metadata
        posted_to_api BOOLEAN DEFAULT 0,
        api_response TEXT,
        error TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_device_timestamp ON ati_messages(device_name, timestamp);
    CREATE INDEX IF NOT EXISTS idx_timestamp ON ati_messages(timestamp);
    CREATE INDEX IF NOT EXISTS idx_posted ON ati_messages(posted_to_api);
`);

/**
 * Log an ATI message to the database
 */
function logATIMessage(data) {
    const stmt = db.prepare(`
        INSERT INTO ati_messages (
            device_name, ati_x, ati_y, ati_heading,
            twinzo_x, twinzo_y, twinzo_heading,
            battery_status, mode, posted_to_api, api_response, error
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    return stmt.run(
        data.device_name,
        data.ati_x,
        data.ati_y,
        data.ati_heading || null,
        data.twinzo_x,
        data.twinzo_y,
        data.twinzo_heading || null,
        data.battery_status || null,
        data.mode || null,
        data.posted_to_api ? 1 : 0,
        data.api_response || null,
        data.error || null
    );
}

/**
 * Get recent messages for a device
 */
function getRecentMessages(deviceName, limit = 100) {
    const stmt = db.prepare(`
        SELECT * FROM ati_messages
        WHERE device_name = ?
        ORDER BY timestamp DESC
        LIMIT ?
    `);
    return stmt.all(deviceName, limit);
}

/**
 * Get statistics for a device
 */
function getDeviceStats(deviceName, hours = 24) {
    const stmt = db.prepare(`
        SELECT
            COUNT(*) as total_messages,
            COUNT(CASE WHEN posted_to_api = 1 THEN 1 END) as posted_count,
            COUNT(CASE WHEN error IS NOT NULL THEN 1 END) as error_count,
            AVG(battery_status) as avg_battery,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen
        FROM ati_messages
        WHERE device_name = ?
        AND timestamp > datetime('now', '-' || ? || ' hours')
    `);
    return stmt.get(deviceName, hours);
}

/**
 * Get all devices seen in the last N hours
 */
function getActiveDevices(hours = 24) {
    const stmt = db.prepare(`
        SELECT
            device_name,
            COUNT(*) as message_count,
            MAX(timestamp) as last_seen,
            AVG(battery_status) as avg_battery
        FROM ati_messages
        WHERE timestamp > datetime('now', '-' || ? || ' hours')
        GROUP BY device_name
        ORDER BY last_seen DESC
    `);
    return stmt.all(hours);
}

/**
 * Clean up old data (keep last N days)
 */
function cleanupOldData(daysToKeep = 30) {
    const stmt = db.prepare(`
        DELETE FROM ati_messages
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    `);
    const result = stmt.run(daysToKeep);
    return result.changes;
}

export {
    db,
    logATIMessage,
    getRecentMessages,
    getDeviceStats,
    getActiveDevices,
    cleanupOldData
};
