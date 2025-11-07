# Twinzo Mock - MQTT Bridge for AMR Integration

This project provides a complete MQTT-based system for mocking and bridging AMR (Autonomous Mobile Robot) data between various sources and the Twinzo platform.

## Project Structure

### Core Components
- **`src/`** - Core application code
  - `publisher/` - Mock AMR data generator with realistic movement patterns
  - `bridge/` - MQTT-to-Twinzo REST API bridge with OAuth authentication
  - `common/` - Shared utilities
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

## Production Deployment

### Multi-Plant Architecture

This system now supports streaming to TWO Twinzo plants simultaneously:

1. **Old Plant Bridge** (Sector 2): ATI MQTTS → tugger-05-old, tugger-06-old
2. **HiTech Bridge** (Sector 1): HiveMQ Cloud → tugger-03, tugger-04

### Quick Start Production

```bash
# Start both bridges
python -X utf8 start_bridges.py

# Start only Old Plant bridge
python -X utf8 start_bridges.py old

# Start only HiTech bridge
python -X utf8 start_bridges.py hitech
```

### Manual Bridge Control

```bash
# Old Plant: ATI MQTTS → Twinzo Old Plant (Sector 2)
python -X utf8 src/bridge/bridge_old_plant.py

# HiTech: HiveMQ Cloud → Twinzo HiTech (Sector 1)
python -X utf8 src/bridge/bridge_hitech.py
```

### Production Environment Variables

Required for production bridges (add to `.env` file):

```bash
# Twinzo API (required for both bridges)
TWINZO_CLIENT=TVSMotor
TWINZO_PASSWORD=Tvs@Hosur$2025
TWINZO_API_KEY=sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S

# ATI MQTTS (for Old Plant bridge) - PENDING FROM ATI
ATI_MQTT_HOST=tvs-dev.ifactory.ai
ATI_MQTT_PORT=8883
ATI_MQTT_USERNAME=<pending>
ATI_MQTT_PASSWORD=<pending>
ATI_MQTT_TOPIC=ati/amr/#

# HiveMQ credentials are in config/hivemq_config.json
# HiTech AMRs need to be configured to publish to HiveMQ topics
```

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

### Coordinate System
- `REGION_MIN_X`, `REGION_MIN_Y` - Top-left coordinate bounds
- `REGION_MAX_X`, `REGION_MAX_Y` - Bottom-right coordinate bounds
- `AFFINE_A`, `AFFINE_B`, `AFFINE_C`, `AFFINE_D`, `AFFINE_TX`, `AFFINE_TY` - Coordinate transformation parameters

## Platform-Specific Notes

### Windows Compatibility
- **ALWAYS use `python -X utf8`** for running Python scripts to avoid Unicode issues
- Use `mosquitto_windows.conf` for local Windows mosquitto installation
- Docker Desktop required for containerized deployment

### Integration Points

#### ATI MQTTS (Production - Old Plant)
- Host: `tvs-dev.ifactory.ai:8883` (MQTT5 with TLS)
- Credentials: Pending from ATI team
- Bridge: `src/bridge/bridge_old_plant.py`
- Target: Twinzo Old Plant (Sector 2)
- Devices: tugger-05-old, tugger-06-old

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
- Per-device OAuth authentication with credential caching
- Two plants:
  - HiTech Plant: Branch `dcac4881-05ab-4f29-b0df-79c40df9c9c2`, Sector 1
  - Old Plant: Branch `40557468-2d57-4a3d-9a5e-3eede177daf5`, Sector 2

## Data Flow

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

Each major directory has its own README.md explaining its contents and usage.