# Database Logging Feature

## Overview

Added: 2025-01-12

The bridge (`bridge_audit_feed.js`) now automatically logs all ATI data to SQLite database for analysis and debugging.

## Database Details

- **Location**: `logs/ati_data.db`
- **Type**: SQLite (file-based, no server needed)
- **Format**: WAL mode for concurrent access
- **Performance**: ~0.5ms per insert (minimal impact)

## What Gets Logged

Every ATI message includes:
- Timestamp
- Device name (ATI sherpa_name)
- ATI raw coordinates (X, Y, heading) - units unknown, assumed meters
- Twinzo transformed coordinates (X, Y, heading)
- Battery status (%)
- Device mode (fleet/disconnected)
- API posting status (success/failure)
- API response
- Error messages (if any)

## Visualization Tools

### Python Script: `scripts/monitoring/visualize_ati_data.py`

```bash
# Show statistics
python -X utf8 scripts/monitoring/visualize_ati_data.py stats

# Recent messages
python -X utf8 scripts/monitoring/visualize_ati_data.py recent tug-55-tvsmotor-hosur-09

# Plot movement path (requires matplotlib)
python -X utf8 scripts/monitoring/visualize_ati_data.py plot tug-55-tvsmotor-hosur-09

# Export to CSV
python -X utf8 scripts/monitoring/visualize_ati_data.py export tug-55-tvsmotor-hosur-09

# Cleanup old data
python -X utf8 scripts/monitoring/visualize_ati_data.py cleanup 30
```

### Node.js Script: `scripts/monitoring/query_database.js`

```bash
node scripts/monitoring/query_database.js
```

Quick summary of active devices and stats.

## Use Cases

1. **Debug coordinate transformation**: Compare ATI raw vs Twinzo transformed
2. **Monitor bridge health**: Check API success/error rates
3. **Analyze movement patterns**: Export data for Excel/Python analysis
4. **Track battery levels**: Plot battery degradation over time
5. **Verify affine parameters**: Validate transformation accuracy

## Database Schema

```sql
CREATE TABLE ati_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    device_name TEXT NOT NULL,
    ati_x REAL NOT NULL,
    ati_y REAL NOT NULL,
    ati_heading REAL,
    twinzo_x REAL NOT NULL,
    twinzo_y REAL NOT NULL,
    twinzo_heading REAL,
    battery_status INTEGER,
    mode TEXT,
    posted_to_api BOOLEAN DEFAULT 0,
    api_response TEXT,
    error TEXT
);
```

## Implementation

- **Module**: `src/common/database.js` (ES6 modules)
- **Package**: `better-sqlite3` (native SQLite bindings)
- **Integration**: Automatically logs in `bridge_audit_feed.js` message handler
- **Error handling**: Database errors logged as warnings, don't crash bridge

## Documentation

See: `docs/DATABASE_LOGGING.md` for complete guide
