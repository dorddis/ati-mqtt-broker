# Twinzo Mock - MQTT Bridge for AMR Integration

This project provides a complete MQTT-based system for mocking and bridging AMR (Autonomous Mobile Robot) data between various sources and the Twinzo platform.

## Project Structure

### Core Components
- **`src/`** - Core application code
  - `publisher/` - Mock AMR data generator with realistic movement patterns
  - `bridge/` - MQTT-to-Twinzo REST API bridge with OAuth authentication and automatic database logging
  - `common/` - Shared utilities (database, transformations)
- **`config/`** - Configuration files
  - `mosquitto/` - MQTT broker configuration
  - `mappings/` - Device, field, and topic mappings
  - `environments/` - Environment-specific configs

### Integrations
- **`integrations/`** - External system integrations
  - `tvs/` - TVS MQTT broker integration
  - `ati/` - ATI platform integration
  - `twinzo/` - Twinzo API utilities

### Testing & Scripts
- **`tests/`** - All test files (unit, integration, mqtt, tvs, ati, render)
- **`scripts/`** - Utility scripts (setup, monitoring, deployment, verification, utils)

### Documentation & Deployment
- **`docs/`** - All documentation (guides, integrations, deployment, project, reference)
- **`deployments/`** - Deployment configs (docker, railway, render, ngrok)
- **`archive/`** - Deprecated files preserved for reference
  - `archive/audit_feed_exploration/shared_ati_code.js` - **Original ATI reference code** shared by ATI team for audit feed connection

## Important Safety Notes

### Process Management
**⚠️ CRITICAL WARNING**: NEVER use commands like `taskkill /F /IM node.exe` or `pkill -9 node` to kill all Node.js processes indiscriminately. These commands can terminate the Claude Code session itself, as it runs on Node.js. Instead:
- Use the `KillShell` tool to kill specific background shell processes by their ID
- If you need to kill a specific Node process, find its PID first and kill only that PID
- Use `ps aux | grep node` to identify specific processes before killing them
- Always prefer targeted process management over blanket kill commands

## Key Commands

### Development Workflow
```bash
# Start the complete system
docker-compose up -d

# View logs
docker-compose logs -f

# Stop system
docker-compose down

# Rebuild after changes
docker-compose build --no-cache
```

### Testing and Monitoring
```bash
# Monitor Twinzo integration
python -X utf8 scripts/monitoring/monitor_twinzo.py

# Visualize logged ATI data from database
python -X utf8 scripts/monitoring/visualize_ati_data.py stats         # Show statistics
python -X utf8 scripts/monitoring/visualize_ati_data.py recent        # Recent messages
python -X utf8 scripts/monitoring/visualize_ati_data.py plot tug-55-tvsmotor-hosur-09  # Plot movement
python -X utf8 scripts/monitoring/visualize_ati_data.py export tug-55-tvsmotor-hosur-09  # Export CSV

# Test connection to TVS broker (when AMRs are online)
python -X utf8 integrations/tvs/tvs_real_data_subscriber.py

# Run data structure comparison
python -X utf8 tests/tvs/data_structure_comparison.py

# Expose broker to external clients
python -X utf8 scripts/utils/expose_mqtt.py

# Test local MQTT connection
python -X utf8 integrations/twinzo/twinzo_test_client.py
```

### Development Tools
```bash
# Verify system setup
python -X utf8 scripts/verification/verify_system.py

# Test MQTT credentials
python -X utf8 scripts/verification/verify_credentials.py

# Simple MQTT test
python -X utf8 tests/mqtt/simple_mqtt_test.py

# Test multi-plant streaming (HiTech + Old Plant)
python -X utf8 tests/integration/test_multi_plant_streaming.py

# Check HiveMQ for incoming data
python -X utf8 check_hivemq_data.py
```

### Device Management

Manage Twinzo devices programmatically via API:

```bash
# List all devices in both plants
python -X utf8 scripts/utils/manage_twinzo_devices.py list

# List devices in specific plant
python -X utf8 scripts/utils/manage_twinzo_devices.py list hitech
python -X utf8 scripts/utils/manage_twinzo_devices.py list old

# Create new device in HiTech plant
python -X utf8 scripts/utils/manage_twinzo_devices.py create tugger-10 hitech --title "Tugger 10"

# Create new device in Old Plant
python -X utf8 scripts/utils/manage_twinzo_devices.py create tugger-07-old old --title "Tugger 07 Old"

# Delete device (use ID from list command)
python -X utf8 scripts/utils/manage_twinzo_devices.py delete 13 hitech
```

### Database Logging

The bridge automatically logs all ATI data to a SQLite database for analysis and debugging.

**Database Location**: `logs/ati_data.db`

**What's Logged**: ATI raw coordinates, transformed Twinzo coordinates, battery status, API responses, errors, timestamps

```bash
# Show statistics (success rate, error rate, active devices)
python -X utf8 scripts/monitoring/visualize_ati_data.py stats

# View recent messages
python -X utf8 scripts/monitoring/visualize_ati_data.py recent
python -X utf8 scripts/monitoring/visualize_ati_data.py recent tug-55-tvsmotor-hosur-09 50

# Plot movement path (requires matplotlib)
python -X utf8 scripts/monitoring/visualize_ati_data.py plot tug-55-tvsmotor-hosur-09

# Export to CSV for analysis
python -X utf8 scripts/monitoring/visualize_ati_data.py export tug-55-tvsmotor-hosur-09

# Quick query from Node.js
node scripts/monitoring/query_database.js

# Clean up old data (keep last 30 days)
python -X utf8 scripts/monitoring/visualize_ati_data.py cleanup 30
```

**Safety**: Database uses `CREATE TABLE IF NOT EXISTS` - data is NEVER overwritten on bridge restart. All historical data is preserved.

**Documentation**: See `docs/DATABASE_LOGGING.md` for complete guide.

## Production Deployment

### Current Status (Updated: 2025-11-25)

**🔄 TWINZO INTEGRATION IN PROGRESS:**
- License extended till **30th November 2025**
- Patrik from Twinzo is connecting directly to ATI broker
- **BLOCKED**: ATI broker has IP whitelisting - Twinzo's IP needs to be whitelisted
- Awaiting Twinzo's IP address to forward to ATI for whitelisting

**Twinzo Direct Connection Support:**
- Support files in `patrik_mqtt_support/` folder
- Test scripts (Node.js + Python) verified working
- Troubleshooting guide and email templates provided
- **Issue**: Error 135 (Not Authorized) on subscribe = IP not whitelisted

**Important Notes:**
- Our bridge works fine from our network (IP whitelisted)
- Twinzo needs their IP whitelisted by ATI to subscribe to topics
- All AMR data logging and coordinate transformations remain functional

### Multi-Plant Architecture

**Old Plant (Sector 2) - Temporarily Paused:**
- **Configuration**: ATI Audit Feed MQTTS → 3 AMRs (tug-55, tug-39, tug-133)
- **Status**: Streaming paused pending Twinzo final integration

**Disabled (not in Old Plant):**
- tug-140, tug-78, tug-24, tug-11 (data from these AMRs is ignored)

**Note**: The bridge `bridge_audit_feed.js` only processes AMRs listed in `DEVICE_MAP`. Other AMRs visible in the ATI feed are ignored.

### Quick Start Production

```bash
# Start ATI audit feed bridge (Old Plant)
node src/bridge/bridge_audit_feed.js > logs/audit_feed_bridge.log 2>&1 &

# Monitor the bridge
tail -f logs/audit_feed_bridge.log

# Or use the unified starter (both plants)
python -X utf8 start_bridges.py

# Start only Old Plant bridge
python -X utf8 start_bridges.py old

# Start only HiTech bridge
python -X utf8 start_bridges.py hitech
```

### Manual Bridge Control

```bash
# Old Plant: ATI Audit Feed → Twinzo Old Plant (Sector 2) - NODE.JS
node src/bridge/bridge_audit_feed.js

# Alternative Python bridge (if needed)
python -X utf8 src/bridge/bridge_old_plant.py

# HiTech: HiveMQ Cloud → Twinzo HiTech (Sector 1)
python -X utf8 src/bridge/bridge_hitech.py
```

### Deploying to a New Device (24/7 Production)

This section provides complete instructions for setting up the bridge on a fresh device for 24/7 operation.

#### Prerequisites

1. **Operating System**: Windows, Linux, or macOS
2. **Node.js**: Version 18.0.0 or higher
   - Check: `node --version`
   - Install from: https://nodejs.org/
3. **Git**: For cloning the repository
   - Check: `git --version`
4. **Network Access**: Device must have internet connectivity and be on a whitelisted IP (if required by ATI)

#### Step-by-Step Setup

**1. Clone the Repository**

```bash
# Navigate to your preferred directory
cd /path/to/your/projects

# Clone the repository
git clone https://github.com/dorddis/ati-mqtt-broker.git twinzo-mock
cd twinzo-mock
```

**2. Install Dependencies**

```bash
# Install Node.js dependencies
npm install

# Verify installation
npm list
```

**3. Configure Environment Variables**

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your credentials
# On Windows: notepad .env
# On Linux/Mac: nano .env
```

**Required variables** (get these from the project owner or secure credential storage):
- `TWINZO_PASSWORD` - Twinzo API password
- `TWINZO_API_KEY` - Twinzo API key
- `AUDIT_USERNAME` - ATI audit feed username
- `AUDIT_PASSWORD` - ATI audit feed password

**4. Test the Bridge**

```bash
# Test run (Ctrl+C to stop after verifying connection)
node src/bridge/bridge_audit_feed.js
```

You should see:
- `OK Connected to ATI audit feed`
- `OK Subscribed to: ati_fm/#, fleet/trips/info`
- `OK Bridge ready - streaming 3 AMRs to Old Plant (Sector 2)`

**5. Set Up 24/7 Operation**

**Option A: Using PM2 (Recommended for Node.js)**

```bash
# Install PM2 globally
npm install -g pm2

# Start the bridge with PM2
pm2 start src/bridge/bridge_audit_feed.js --name twinzo-bridge

# Configure PM2 to start on system boot
pm2 startup
# Follow the instructions shown by PM2

# Save the PM2 process list
pm2 save

# View logs
pm2 logs twinzo-bridge

# Monitor status
pm2 status

# Other useful PM2 commands:
pm2 restart twinzo-bridge  # Restart the bridge
pm2 stop twinzo-bridge     # Stop the bridge
pm2 delete twinzo-bridge   # Remove from PM2
```

**Option B: Using systemd (Linux)**

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/twinzo-bridge.service
```

Add the following content (adjust paths as needed):

```ini
[Unit]
Description=Twinzo ATI Bridge
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/twinzo-mock
ExecStart=/usr/bin/node src/bridge/bridge_audit_feed.js
Restart=always
RestartSec=10
StandardOutput=append:/path/to/twinzo-mock/logs/audit_feed_bridge.log
StandardError=append:/path/to/twinzo-mock/logs/audit_feed_bridge.log

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable twinzo-bridge
sudo systemctl start twinzo-bridge

# Check status
sudo systemctl status twinzo-bridge

# View logs
sudo journalctl -u twinzo-bridge -f
```

**Option C: Using Windows Task Scheduler**

1. Open Task Scheduler
2. Create New Task:
   - **General Tab**: Name it "Twinzo Bridge", run whether user is logged on or not
   - **Triggers Tab**: At startup
   - **Actions Tab**:
     - Action: Start a program
     - Program: `C:\Program Files\nodejs\node.exe`
     - Arguments: `src\bridge\bridge_audit_feed.js`
     - Start in: `C:\path\to\twinzo-mock`
   - **Settings Tab**:
     - Allow task to run on demand
     - If task fails, restart every 1 minute
     - Stop task if runs longer than 3 days (unchecked)

**6. Monitor the Bridge**

```bash
# View live logs (if using PM2)
pm2 logs twinzo-bridge

# View database statistics
python -X utf8 scripts/monitoring/visualize_ati_data.py stats

# Check recent messages
python -X utf8 scripts/monitoring/visualize_ati_data.py recent

# Monitor active devices
python -X utf8 scripts/monitoring/visualize_ati_data.py recent tug-55-tvsmotor-hosur-09
```

**7. Verify Operation**

After 5-10 minutes of operation:

```bash
# Check that messages are being logged
python -X utf8 scripts/monitoring/visualize_ati_data.py stats

# Verify API posts are successful
# Look for "posted_count" in stats output

# Check Twinzo dashboard
# Log in to Twinzo and verify AMR positions are updating
```

#### Troubleshooting

**Bridge won't connect to ATI:**
- Check internet connectivity
- Verify `.env` file has correct credentials
- Ensure device IP is whitelisted (contact ATI admin)

**Connected but no messages:**
- AMRs may be offline or not moving
- Data comes in bursts (8-11 min gaps are normal)
- Check `stats.messagesTotal` is incrementing in logs

**API posts failing:**
- Check Twinzo credentials in `.env`
- Verify Twinzo license is active
- Check logs for specific error messages

**Bridge stops unexpectedly:**
- Enable auto-restart (PM2 or systemd recommended)
- Check system resources (RAM, CPU)
- Review logs for error patterns

#### Updating the Bridge

```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies (if package.json changed)
npm install

# Restart the bridge
pm2 restart twinzo-bridge
# OR (systemd)
sudo systemctl restart twinzo-bridge
```

#### Security Considerations

1. **Never commit `.env` file** - it contains sensitive credentials
2. **Restrict file permissions**:
   ```bash
   chmod 600 .env  # On Linux/Mac
   ```
3. **Use a dedicated user account** for running the service
4. **Regularly rotate credentials** (coordinate with project owner)
5. **Monitor logs for unauthorized access attempts**
6. **Keep Node.js and dependencies updated**:
   ```bash
   npm outdated
   npm update
   ```

### Production Environment Variables

Required for production bridges (add to `.env` file):

```bash
# Twinzo API (required for both bridges)
TWINZO_CLIENT=TVSMotor
TWINZO_PASSWORD=Tvs@Hosur$2025
TWINZO_API_KEY=sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S

# ATI Audit Feed - PRODUCTION (streaming 3 AMRs to Old Plant only)
AUDIT_MQTT_HOST=tvs-dev.ifactory.ai
AUDIT_MQTT_PORT=8883
AUDIT_USERNAME=tvs-audit-user
AUDIT_PASSWORD=TVSAudit@2025

# ATI Production Feed - ALTERNATIVE (individual AMRs)
ATI_MQTT_HOST=tvs-dev.ifactory.ai
ATI_MQTT_PORT=8883
ATI_MQTT_USERNAME=amr-001
ATI_MQTT_PASSWORD=TVSamr001@2025
ATI_CLIENT_ID=amr-001
ATI_MQTT_TOPIC=ati_fm/sherpa/status

# Coordinate Transform - ATI to Twinzo units (1000:1 scale with rotation and Y-axis flip)
# Based on 8 HIGH-QUALITY reference coordinate pairs (battery stations excluded)
# Constrained similarity transformation: exact 1000:1 scale, 3 parameters (theta, TX, TY)
# Mean error: 3,076 units (~3.1m / 2.0%), Max error: 9,615 units (~9.6m / 6.2%)
# 60.4% improvement over previous calibration
AFFINE_A=999.738230
AFFINE_B=22.879501
AFFINE_C=22.879501
AFFINE_D=-999.738230
AFFINE_TX=95598.77
AFFINE_TY=167357.60

# HiveMQ credentials are in config/hivemq_config.json
```

### Active AMRs (ATI Audit Feed → Twinzo)

**Old Plant (Sector 2)** - Streaming Paused (Awaiting Final Integration):

| Twinzo Device | ATI Name | Battery | Status |
|---------------|----------|---------|--------|
| tug-55-hosur-09 | tug-55-tvsmotor-hosur-09 | 75-85% | ⏸️ Paused - Ready to resume |
| tug-39-hosur-07 | tug-39-tvsmotor-hosur-07 | 68-81% | ⏸️ Paused - Ready to resume |
| tug-133 | tug-133 | 44-52% | ⏸️ Paused - Ready to resume |

**Disabled AMRs** (data ignored):

| ATI Name | Reason |
|----------|--------|
| tug-140 | Not in Old Plant |
| tug-78 | Not in Old Plant |
| tug-24-tvsmotor-hosur-05 | Not in Old Plant |
| tug-11 | Not in Old Plant |

### Complete Production Guide

For complete production deployment instructions, device mapping, troubleshooting, and monitoring:

**→ See [docs/PRODUCTION_SETUP.md](docs/PRODUCTION_SETUP.md)**

## Environment Variables

### MQTT Configuration
- `MQTT_HOST` - MQTT broker hostname (default: localhost)
- `MQTT_PORT` - MQTT broker port (default: 1883)
- `MQTT_USERNAME` - MQTT username (optional)
- `MQTT_PASSWORD` - MQTT password (optional)
- `MQTT_TOPIC` - MQTT topic for AMR data (default: ati_fm/sherpa/status)

### Twinzo API Configuration
- `TWINZO_CLIENT` - OAuth client name (default: TVSMotor)
- `TWINZO_PASSWORD` - OAuth password
- `TWINZO_API_KEY` - Twinzo API key
- `DRY_RUN` - Set to "true" to disable actual API calls (default: false)
- `SECTOR_IDS` - Comma-separated list of sector IDs to stream to (default: "1,2" for both HiTech and Old Plant)
  - "1" = HiTech Plant only
  - "2" = Old Plant only
  - "1,2" = Both plants (default)

### Mock Data Configuration
- `NUM_ROBOTS` - Number of mock robots (default: 3)
- `ROBOT_PREFIX` - Robot name prefix (default: tugger)
- `HZ` - Update frequency in Hz (default: 10)
- `PATH_SHAPE` - Movement pattern: loop, line, rectangle (default: loop)

### Coordinate System (OLD PLANT - ATI to Twinzo)

ATI provides coordinates in **meters** (range: -1.3 to 117m). These are transformed to Twinzo units (millimeters) using constrained similarity transformation with exact 1000:1 scale:

```
X_twinzo = AFFINE_A * X_ati + AFFINE_B * Y_ati + AFFINE_TX
Y_twinzo = AFFINE_C * X_ati + AFFINE_D * Y_ati + AFFINE_TY
```

**Current Transform (Updated 2025-01-12 - Option B, 1000:1 Constrained):**
- `AFFINE_A=999.738230` - X scale component (cos θ × 1000)
- `AFFINE_B=22.879501` - Rotation component (sin θ × 1000)
- `AFFINE_C=22.879501` - Rotation component (sin θ × 1000)
- `AFFINE_D=-999.738230` - Y scale component (NEGATIVE = Y-axis flip)
- `AFFINE_TX=95598.77` - X offset
- `AFFINE_TY=167357.60` - Y offset

**Key Features:**
- **Unit conversion**: Exactly **1000:1** (meters to millimeters)
- **Rotation**: 1.31° clockwise
- **Y-axis flip**: ATI's Y-axis points opposite to Twinzo's (negative D coefficient)
- **Uniform scale**: Same scale in both X and Y directions (1000.0)
- **Accuracy**: Mean error ~3.1m (2.0%), Max error ~9.6m (6.2%)
- **Improvement**: **60.4% better** than previous calibration
- **Simplicity**: Only 3 free parameters (rotation angle, TX, TY) - easier to maintain

**Calculation Basis:**
- Based on **8 HIGH-QUALITY reference coordinate pairs**
- Battery stations excluded (poor reference quality with 10-14m errors)
- Quality over quantity: fewer but better reference points
- Reference stations: Origin, XL Engine areas, Dispatch, Engine Assembly, Jupiter B areas
- Constrained similarity transform maintains exact 1000:1 meter-to-millimeter conversion

**Coordinate Range:**
- ATI: X=[-1.3, 116.4], Y=[-11.0, 76.4] meters
- Twinzo: X=[94,350, 217,216], Y=[84,928, 180,531] millimeters
- Factory floor: ~120m × 90m

**Note on Battery Stations:**
Battery area reference measurements have 10-14m errors (poor quality). These stations are excluded from calibration. If you need better accuracy in battery areas, remeasure those reference points with surveyed coordinates.

### Mock Data Configuration (For Testing Only)
- `NUM_ROBOTS` - Number of mock robots (default: 3)
- `ROBOT_PREFIX` - Robot name prefix (default: tugger)
- `HZ` - Update frequency in Hz (default: 10)
- `PATH_SHAPE` - Movement pattern: loop, line, rectangle (default: loop)
- `REGION_MIN_X`, `REGION_MIN_Y` - Top-left coordinate bounds (for mock data)
- `REGION_MAX_X`, `REGION_MAX_Y` - Bottom-right coordinate bounds (for mock data)

## Platform-Specific Notes

### Windows Compatibility
- **ALWAYS use `python -X utf8`** for running Python scripts to avoid Unicode issues
- Use `mosquitto_windows.conf` for local Windows mosquitto installation
- Docker Desktop required for containerized deployment

### Integration Points

#### ATI Audit Feed (Production - Old Plant) ⏸️ PAUSED
- Host: `tvs-dev.ifactory.ai:8883` (MQTT5 with TLS)
- Credentials: `tvs-audit-user` / `TVSAudit@2025`
- Client ID: Must match username (`tvs-audit-user`)
- Topics: `ati_fm/#` (wildcard), `fleet/trips/info`
- QoS Level: 1
- **Original ATI Reference Code**: `archive/audit_feed_exploration/shared_ati_code.js` (provided by ATI team)
- Data Format:
  - `sherpa_name`: Device identifier (e.g., "tug-55-tvsmotor-hosur-09")
  - `pose`: [x, y, heading] array in **meters**
  - `battery_status`: Battery percentage (0-100), -1 = unknown
  - `mode`: "fleet" (active/moving) or "disconnected"
  - `disabled`: boolean - true if AMR is offline
  - `disabled_reason`: "stale_heartbeat" or empty string
  - `trip_id`, `trip_leg_id`: Current trip information
  - `message_id`: UUID for each message
  - **`timestamp`**: ISO 8601 format (e.g., "2025-12-01T13:21:52Z") - **⚠️ IMPORTANT: Despite the 'Z' suffix, timestamps are actually in IST (Indian Standard Time, UTC+5:30), NOT UTC**
  - Update frequency: Real-time bursts when AMRs are active
- Bridge: `src/bridge/bridge_audit_feed.js` (Node.js)
- Target: Twinzo Old Plant (Sector 2)
- Devices: **7 AMRs** - tug-55-hosur-09, tug-39-hosur-07, tug-133, tug-140, tug-78, tug-24-hosur-05, tug-11
- Status: ⏸️ **PAUSED** - Awaiting Twinzo final integration (license valid till 30 Nov 2025)
- Coordinate Range: -160m to 125m (ATI) → varies (Twinzo after transformation)
- **Timezone Note**: ⚠️ ATI timestamps have a 'Z' suffix (which normally means UTC) but are actually in **IST (Indian Standard Time, UTC+5:30)**. This is a data formatting issue on ATI's side - treat all timestamps as IST.

#### HiveMQ Cloud (Production - HiTech)
- Host: `0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud:8883`
- Credentials: In `config/hivemq_config.json`
- Bridge: `src/bridge/bridge_hitech.py`
- Target: Twinzo HiTech Plant (Sector 1)
- Devices: tugger-03, tugger-04

#### TVS Integration (Testing/Development)
- Host: `tvs-dev.ifactory.ai:8883` (MQTT5 with TLS)
- Client ID: `amr-001`
- Credentials: `amr-001` / `TVSamr001@2025`
- Known AMR MAC addresses in `device_mapping.json`

#### Twinzo API
- OAuth endpoint: `https://api.platform.twinzo.com/v3/authorization/authenticate`
- Localization endpoint: `https://api.platform.twinzo.com/v3/localization`
- Device management endpoint: `https://api.platform.twinzo.com/v3/devices`
- Per-device OAuth authentication with credential caching
- Authentication: Individual device login with password `Tvs@Hosur$2025`
- Headers: `Client`, `Branch`, `Token`, `Api-Key` (NOT `Authorization: Bearer`)
- Payload: Array format `[{...}]` (NOT single object)
- Two plants:
  - **HiTech Plant**: Branch `dcac4881-05ab-4f29-b0df-79c40df9c9c2`, Sector 1, Branch ID 1
    - ATI AMRs: tug-140, tug-78, tug-24-hosur-05, tug-11
    - Other devices: tugger-01, tugger-02, tugger-03, tugger-04
  - **Old Plant**: Branch `40557468-2d57-4a3d-9a5e-3eede177daf5`, Sector 2, Branch ID 2
    - ATI AMRs: tug-55-hosur-09, tug-39-hosur-07, tug-133
    - Other devices: tugger-05-old, tugger-06-old, tugger-07-old

## Data Flow

### Production Flow (Old Plant - ATI Audit Feed)

1. **ATI AMRs**: Real tuggers operating in factory, publishing position to ATI MQTT broker
2. **ATI MQTT Broker**: `tvs-dev.ifactory.ai:8883` publishes to `ati_fm/#` topics
3. **Bridge (Node.js)**: `bridge_audit_feed.js` subscribes, processes, transforms coordinates
4. **OAuth Authentication**: Per-device login to Twinzo API with token caching
5. **Coordinate Transform**: ATI meters → Twinzo units (affine: scale ~1114x/1022y, Y-flip, -0.35° rotation)
6. **API Posting**: Transformed data sent to Twinzo localization API (Sector 2)
7. **Twinzo Map**: Tuggers visible and tracking in real-time on Old Plant map

### Mock/Testing Flow (Development)

1. **Mock Data Generation**: `publisher/` generates realistic AMR movement data
2. **MQTT Broker**: `mosquitto/` handles message routing and persistence
3. **Bridge Processing**: `bridge/` subscribes to MQTT, transforms data, authenticates with Twinzo
4. **API Posting**: Transformed data sent to Twinzo localization API

## Testing Strategy

### Unit Testing
- Test individual components: publisher, bridge, subscribers
- Validate data transformations and coordinate conversions
- Test OAuth authentication and error handling

### Integration Testing
- End-to-end data flow: Mock → MQTT → Bridge → Twinzo
- Real TVS data capture and analysis
- Network connectivity and TLS validation

### Load Testing
- Multiple robot simulation at various frequencies
- MQTT broker performance under load
- API rate limiting and error recovery

## Troubleshooting

### Common Issues
1. **Unicode Errors**: Always use `python -X utf8` on Windows
2. **Connection Failures**: Check firewall settings for ports 1883, 8883, 9001
3. **Authentication Errors**: Verify credentials and API keys
4. **Coordinate Issues**: Check affine transform parameters

### Debug Commands
```bash
# Check docker containers
docker ps -a

# View specific service logs
docker-compose logs bridge
docker-compose logs publisher

# Test MQTT connectivity
mosquitto_pub -h localhost -p 1883 -t test -m "hello"
mosquitto_sub -h localhost -p 1883 -t "#"
```

## Development Guidelines

### Code Style
- Follow existing patterns in the codebase
- Use clear, descriptive variable names
- Add error handling for network operations
- Log important events with appropriate levels

### Testing
- Test all network connections thoroughly
- Validate data transformations with known inputs
- Test error scenarios and recovery mechanisms
- Document any platform-specific behavior

### Documentation
- Update this file when adding new features
- Document environment variables and their defaults
- Include troubleshooting steps for new components
- Provide clear examples for common use cases

## Security Considerations

- Never commit API keys or passwords to the repository
- Use environment variables for all sensitive configuration
- Validate and sanitize all external data inputs
- Use TLS for all external communications
- Implement proper error handling to avoid information leakage

## File Organization

The codebase has been refactored into a clean, organized structure:

### Navigation Tips
- **Starting point**: See README.md in the root and docs/README.md for documentation index
- **Running tests**: All tests are in tests/ organized by type
- **Scripts**: All utility scripts are in scripts/ organized by purpose
- **Integration code**: External integrations are in integrations/
- **Documentation**: All docs are in docs/ organized by category
  - **Database logging**: See docs/DATABASE_LOGGING.md for visualization and analysis tools
- **Archive**: Old/deprecated files are in archive/ - check here before recreating old solutions

### Quick Reference
- Production code: `src/`
- Configuration: `config/`
- Tests: `tests/`
- Scripts: `scripts/`
- Docs: `docs/`
- Deployments: `deployments/`
- Integrations: `integrations/`
- Archive: `archive/`
- **Twinzo Support**: `patrik_mqtt_support/` - MQTT connection help for Patrik

Each major directory has its own README.md explaining its contents and usage.

## Twinzo Direct Integration Support

Support files for Patrik (Twinzo) to connect directly to ATI broker:

**Location**: `patrik_mqtt_support/`

**Contents**:
- `test_patrik_connection.js` - Working Node.js MQTT test script
- `test_patrik_connection.py` - Working Python MQTT test script
- `PATRIK_MQTT_TROUBLESHOOTING.md` - Complete troubleshooting guide
- `email_*.txt` - Email templates for communication
- `README.md` - Overview and current status

**ATI Broker Connection Requirements**:
```javascript
{
    protocol: 'mqtts',
    host: 'tvs-dev.ifactory.ai',
    port: 8883,
    clientId: 'tvs-audit-user',      // MUST match username!
    username: 'tvs-audit-user',
    password: 'TVSAudit@2025',
    protocolVersion: 5,               // MQTT v5 required
    clean: true,                      // Clean session
    rejectUnauthorized: false         // Skip cert verification
}
```

**Known Issue**: ATI broker has IP whitelisting. External IPs need to be whitelisted by ATI to subscribe to topics. Error 135 (Not Authorized) = IP not whitelisted.