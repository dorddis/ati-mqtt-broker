# Database Logging for ATI Data

The bridge now automatically logs all ATI data to a SQLite database for analysis and visualization.

## Overview

- **Database Location**: `logs/ati_data.db`
- **Database Type**: SQLite (file-based, no server required)
- **Logged Data**: ATI raw coordinates, transformed Twinzo coordinates, battery status, API responses, errors
- **Automatic**: No configuration needed - just run the bridge

## What Gets Logged

Every message from ATI is logged with:
- **Timestamp**: When the message was received
- **Device Name**: ATI sherpa_name (e.g., "tug-55-tvsmotor-hosur-09")
- **ATI Position**: Raw coordinates in meters (x, y, heading)
- **Twinzo Position**: Transformed coordinates (x, y, heading)
- **Battery Status**: Battery percentage (0-100)
- **Mode**: Device mode ("fleet", "disconnected", etc.)
- **API Status**: Whether the data was successfully posted to Twinzo
- **API Response**: Response from Twinzo API
- **Errors**: Any errors that occurred

## Visualization Script

Use the `visualize_ati_data.py` script to analyze logged data:

### Show Statistics
```bash
# Last 24 hours (default)
python -X utf8 scripts/monitoring/visualize_ati_data.py stats

# Last 48 hours
python -X utf8 scripts/monitoring/visualize_ati_data.py stats 48
```

Output:
- Total messages received
- Success rate (posted to API)
- Error rate
- Per-device statistics
- Average battery levels
- Last seen times

### View Recent Messages
```bash
# Last 20 messages from all devices (default)
python -X utf8 scripts/monitoring/visualize_ati_data.py recent

# Last 50 messages from specific device
python -X utf8 scripts/monitoring/visualize_ati_data.py recent tug-55-tvsmotor-hosur-09 50
```

### Plot Movement Path
```bash
# Requires: pip install matplotlib

# Last 24 hours (default)
python -X utf8 scripts/monitoring/visualize_ati_data.py plot tug-55-tvsmotor-hosur-09

# Last 48 hours
python -X utf8 scripts/monitoring/visualize_ati_data.py plot tug-55-tvsmotor-hosur-09 48
```

Creates a visual plot showing:
1. **ATI coordinates**: Raw movement path in meters
2. **Twinzo coordinates**: Transformed path
3. **Battery level**: Over time

Plots are saved to `logs/` directory.

### Export to CSV
```bash
# Export specific device (last 24 hours)
python -X utf8 scripts/monitoring/visualize_ati_data.py export tug-55-tvsmotor-hosur-09

# Export all devices (last 48 hours)
python -X utf8 scripts/monitoring/visualize_ati_data.py export all 48
```

CSV files are saved to `logs/` directory.

### Cleanup Old Data
```bash
# Delete data older than 30 days (default)
python -X utf8 scripts/monitoring/visualize_ati_data.py cleanup

# Delete data older than 7 days
python -X utf8 scripts/monitoring/visualize_ati_data.py cleanup 7
```

## Direct Database Access

You can also query the database directly using any SQLite tool:

```bash
# Using sqlite3 CLI
sqlite3 logs/ati_data.db

# Example queries:
sqlite> SELECT COUNT(*) FROM ati_messages;
sqlite> SELECT device_name, COUNT(*) FROM ati_messages GROUP BY device_name;
sqlite> SELECT * FROM ati_messages ORDER BY timestamp DESC LIMIT 10;
```

## Database Schema

```sql
CREATE TABLE ati_messages (
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
```

## Use Cases

### Debug Coordinate Transformation
```bash
# View recent coordinates to verify transformation
python -X utf8 scripts/monitoring/visualize_ati_data.py recent tug-55-tvsmotor-hosur-09 100

# Plot movement to visualize transformation
python -X utf8 scripts/monitoring/visualize_ati_data.py plot tug-55-tvsmotor-hosur-09
```

### Monitor Bridge Health
```bash
# Check success rate and errors
python -X utf8 scripts/monitoring/visualize_ati_data.py stats
```

### Analyze Movement Patterns
```bash
# Export data for analysis in Excel/Python
python -X utf8 scripts/monitoring/visualize_ati_data.py export tug-55-tvsmotor-hosur-09 168
```

### Track Battery Levels
```bash
# Plot shows battery degradation over time
python -X utf8 scripts/monitoring/visualize_ati_data.py plot tug-55-tvsmotor-hosur-09 24
```

## Performance Notes

- Database uses WAL (Write-Ahead Logging) for better concurrent access
- Indexed on device_name and timestamp for fast queries
- Minimal performance impact on bridge (~0.5ms per insert)
- Automatic cleanup recommended every 30 days to keep database size manageable

## Troubleshooting

**Database not found**:
- Make sure the bridge has been run at least once
- Database is created automatically on first run
- Location: `logs/ati_data.db`

**Visualization script errors**:
- Install matplotlib: `pip install matplotlib`
- Use `python -X utf8` on Windows to avoid Unicode issues

**Database locked errors**:
- WAL mode reduces these significantly
- Close other connections to the database
- The bridge handles this automatically

## Advanced: Custom Queries

You can write custom queries using the database module:

```javascript
// In a Node.js script
import { db } from './src/common/database.js';

// Get average battery by device
const result = db.prepare(`
    SELECT device_name, AVG(battery_status) as avg_battery
    FROM ati_messages
    WHERE timestamp > datetime('now', '-7 days')
    GROUP BY device_name
`).all();

console.log(result);
```

```python
# In a Python script
import sqlite3
conn = sqlite3.connect('logs/ati_data.db')
cursor = conn.cursor()

# Get error rate by device
cursor.execute("""
    SELECT device_name,
           COUNT(*) as total,
           SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as errors
    FROM ati_messages
    WHERE timestamp > datetime('now', '-7 days')
    GROUP BY device_name
""")

for row in cursor.fetchall():
    device, total, errors = row
    error_rate = (errors / total * 100) if total > 0 else 0
    print(f"{device}: {error_rate:.1f}% error rate ({errors}/{total})")
```
