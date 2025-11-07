# Twinzo Multi-Plant Production Setup

This guide provides complete instructions for deploying the dual-bridge architecture to stream AMR data to both Twinzo plants.

## Architecture Overview

```
ATI MQTTS Server (tvs-dev.ifactory.ai:8883)
    |
    v
bridge_old_plant.py --> Twinzo Old Plant (Sector 2)
                        - tugger-05-old
                        - tugger-06-old

HiveMQ Cloud (*.s1.eu.hivemq.cloud:8883)
    |
    v
bridge_hitech.py --> Twinzo HiTech Plant (Sector 1)
                     - tugger-03
                     - tugger-04
```

## Prerequisites

### 1. Environment Setup

Create a `.env` file in the project root:

```bash
# Twinzo API Credentials (required for both bridges)
TWINZO_CLIENT=TVSMotor
TWINZO_PASSWORD=Tvs@Hosur$2025
TWINZO_API_KEY=sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S

# ATI MQTTS Credentials (for Old Plant bridge)
ATI_MQTT_HOST=tvs-dev.ifactory.ai
ATI_MQTT_PORT=8883
ATI_MQTT_USERNAME=<pending from ATI>
ATI_MQTT_PASSWORD=<pending from ATI>
ATI_MQTT_TOPIC=ati/amr/#

# Optional: Coordinate transformation for Old Plant
AFFINE_A=1.0
AFFINE_B=0.0
AFFINE_C=0.0
AFFINE_D=1.0
AFFINE_TX=0.0
AFFINE_TY=0.0

# Optional: Logging frequency
LOG_EVERY_N=50
```

### 2. HiveMQ Configuration

Ensure `config/hivemq_config.json` exists with:

```json
{
  "host": "0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud",
  "port": 8883,
  "username": "hitech-test",
  "password": "HitechAMR@2025"
}
```

### 3. Python Dependencies

```bash
pip install paho-mqtt requests python-dotenv
```

## Quick Start

### Start Both Bridges

```bash
python -X utf8 start_bridges.py
```

### Start Individual Bridges

```bash
# Old Plant bridge only
python -X utf8 start_bridges.py old

# HiTech bridge only
python -X utf8 start_bridges.py hitech
```

### Manual Bridge Startup

```bash
# Old Plant bridge
python -X utf8 src/bridge/bridge_old_plant.py

# HiTech bridge
python -X utf8 src/bridge/bridge_hitech.py
```

## Bridge Configuration

### Old Plant Bridge (bridge_old_plant.py)

**Purpose:** Stream ATI MQTTS data to Twinzo Old Plant

**Configuration:**
- **Target:** Sector 2, Branch `40557468-2d57-4a3d-9a5e-3eede177daf5`
- **Devices:** tugger-05-old, tugger-06-old
- **Source:** ATI MQTTS broker (TLS required)
- **Device Mapping:** Configured in `DEVICE_MAP` dictionary

**Device Mapping:**
```python
DEVICE_MAP = {
    "ati_amr_001": "tugger-05-old",
    "ati_amr_002": "tugger-06-old",
    # Add more mappings as ATI provides more AMRs
}
```

**Status:** Waiting for ATI MQTTS credentials

### HiTech Bridge (bridge_hitech.py)

**Purpose:** Stream HiveMQ Cloud data to Twinzo HiTech Plant

**Configuration:**
- **Target:** Sector 1, Branch `dcac4881-05ab-4f29-b0df-79c40df9c9c2`
- **Devices:** tugger-03, tugger-04
- **Source:** HiveMQ Cloud (TLS required)
- **Device Mapping:** Configured in `DEVICE_MAP` dictionary

**Device Mapping:**
```python
DEVICE_MAP = {
    "hitech_amr_001": "tugger-03",
    "hitech_amr_002": "tugger-04",
    # Add more mappings as HiTech provides more AMRs
}
```

**Status:** Ready, waiting for HiTech to configure AMRs to publish data

## Data Flow

### 1. MQTT Message Reception
- Bridge subscribes to MQTT topic (`ati/amr/#` or `hitech/amr/#`)
- Receives JSON payloads with AMR position and status data

### 2. Device Mapping
- Extracts device ID from MQTT payload
- Maps to Twinzo tugger login using `DEVICE_MAP`
- Ignores unknown devices (logs warning every N messages)

### 3. Twinzo Authentication
- OAuth authentication per device
- Token caching with expiration tracking
- Automatic re-authentication when tokens expire

### 4. Data Transformation
- Extracts position (x, y, z)
- Applies coordinate transformation if configured
- Calculates movement status (threshold: 10mm)
- Formats as Twinzo localization payload

### 5. API Posting
- Posts to `https://api.platform.twinzo.com/v3/localization`
- Headers include OAuth token and API key
- Targets appropriate SectorId (1 or 2)
- 5-second timeout with error handling

## Monitoring

### Log Output Format

**Success:**
```
OK tugger-05-old (ATI:ati_amr_001) -> Old Plant: (1234, 5678)
```

**Errors:**
```
FAIL OAuth failed for tugger-05-old: 401
FAIL POST failed for tugger-03: 500
WARN Unknown ATI device: ati_amr_999 (add to DEVICE_MAP)
```

### Key Metrics to Monitor

1. **Connection Status:** Initial connection messages
2. **Device Mapping:** Unknown device warnings
3. **Authentication:** OAuth success/failure
4. **API Posts:** Success rate and errors
5. **Movement Detection:** IsMoving status

### Logging Frequency

Default: Every 50th message (configured via `LOG_EVERY_N`)

## Troubleshooting

### Bridge Won't Start

**Check:**
1. Python dependencies installed
2. Environment variables set (`.env` file loaded)
3. HiveMQ config file exists
4. Network connectivity to MQTT brokers

### No Data Appearing in Twinzo

**Check:**
1. MQTT connection successful (see connection logs)
2. MQTT messages being received (enable debug logging)
3. Device mapping correct (check `DEVICE_MAP`)
4. OAuth authentication successful
5. Coordinates within plant boundaries
6. IsMoving detection working (check movement threshold)

### Authentication Failures

**Check:**
1. Twinzo credentials correct
2. Device logins match exactly (tugger-05-old, not tugger-05)
3. Devices created in correct branch
4. Network access to Twinzo API

### Connection Errors

**ATI MQTTS:**
- Verify credentials from ATI team
- Check TLS certificate validation
- Ensure port 8883 not blocked

**HiveMQ Cloud:**
- Verify credentials in `config/hivemq_config.json`
- Test with `check_hivemq_data.py`
- Ensure port 8883 not blocked

## Adding New Devices

### 1. Create Device in Twinzo Dashboard

- Navigate to appropriate plant (Old Plant or HiTech)
- Create new tugger device
- Use consistent naming (tugger-XX-old for Old Plant)
- Use same password as existing devices

### 2. Update Bridge Configuration

**Old Plant:**
Edit `src/bridge/bridge_old_plant.py`:
```python
DEVICE_MAP = {
    "ati_amr_001": "tugger-05-old",
    "ati_amr_002": "tugger-06-old",
    "ati_amr_003": "tugger-07-old",  # New device
}
```

**HiTech:**
Edit `src/bridge/bridge_hitech.py`:
```python
DEVICE_MAP = {
    "hitech_amr_001": "tugger-03",
    "hitech_amr_002": "tugger-04",
    "hitech_amr_003": "tugger-05",  # New device
}
```

### 3. Restart Bridge

```bash
# Stop existing bridge (Ctrl+C)
# Restart with new configuration
python -X utf8 start_bridges.py
```

## Coordinate Transformation

If AMR coordinate systems don't match Twinzo plants, apply affine transformation:

```bash
# Set in .env file
AFFINE_A=1.0      # Scale X
AFFINE_B=0.0      # Skew X by Y
AFFINE_C=0.0      # Skew Y by X
AFFINE_D=1.0      # Scale Y
AFFINE_TX=0.0     # Translate X
AFFINE_TY=0.0     # Translate Y
```

**Transformation formula:**
```
X_twinzo = AFFINE_A * x + AFFINE_B * y + AFFINE_TX
Y_twinzo = AFFINE_C * x + AFFINE_D * y + AFFINE_TY
```

## Security Considerations

### Credentials Management

- **Never commit** `.env` file to repository
- Store credentials securely (environment variables or secrets manager)
- Use different credentials for production vs testing
- Rotate passwords regularly

### Network Security

- All MQTT connections use TLS (port 8883)
- All Twinzo API calls use HTTPS
- Verify TLS certificates (CERT_REQUIRED)
- Use strong passwords for MQTT authentication

### OAuth Token Handling

- Tokens cached in memory only (not persisted)
- Automatic expiration and renewal
- 10-minute cleanup cycle for expired tokens
- No token sharing between devices

## Performance Tuning

### Update Frequency

Default: Process every MQTT message, post to Twinzo when movement detected

**Adjust via movement threshold:**
```python
# In bridge code
is_moving = distance > 10  # mm, increase to reduce API calls
```

### API Rate Limiting

- Default timeout: 5 seconds
- Increase for slow networks
- Consider batching if hitting rate limits

### Logging Volume

```bash
# Reduce log noise
export LOG_EVERY_N=100  # Log every 100th message
```

## Production Deployment Options

### Option 1: Local Server

- Run bridges on local server with network access to MQTT brokers
- Use systemd or supervisord for process management
- Monitor with standard logging tools

### Option 2: Cloud Deployment

- Deploy to cloud VPS (DigitalOcean, Linode, etc.)
- Use Docker for containerization
- Configure environment variables via cloud platform

### Option 3: Render/Railway

- Use existing deployment configs in `deployments/` directory
- Configure environment variables in platform dashboard
- Monitor via platform logs

## Next Steps

1. **Obtain ATI credentials:** Contact ATI team for MQTTS access
2. **Configure HiTech AMRs:** HiTech team to publish data to HiveMQ
3. **Test data flow:** Verify both bridges receiving and posting data
4. **Monitor and optimize:** Adjust thresholds and mappings as needed
5. **Add more devices:** Scale up device mappings as more AMRs deployed

## Related Documentation

- [Multi-Plant Streaming Guide](MULTI_PLANT_STREAMING_GUIDE.md) - Technical deep-dive
- [Twinzo Multi-Plant Analysis](TWINZO_MULTI_PLANT_ANALYSIS.md) - Problem analysis
- [HiTech Integration](integrations/hitech/) - HiTech-specific documentation
- [ATI Integration](integrations/ati/) - ATI-specific documentation
- [Project Status](project/PROJECT_STATUS.md) - Current implementation status

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review related documentation
3. Check git commit history for recent changes
4. Contact development team
