# Twinzo Mock - MQTT Bridge for AMR Integration

This project provides a complete MQTT-based system for mocking and bridging AMR (Autonomous Mobile Robot) data between various sources and the Twinzo platform.

## Project Structure

### Core Components
- **`publisher/`** - Mock AMR data generator with realistic movement patterns
- **`bridge/`** - MQTT-to-Twinzo REST API bridge with OAuth authentication
- **`mosquitto/`** - MQTT broker configuration and data persistence

### TVS Integration Tools
- **`tvs_real_data_subscriber.py`** - Connect to real TVS MQTT broker and capture AMR data
- **`data_structure_comparison.py`** - Analyze differences between mock and real data
- **Configuration files** - Field mapping, device mapping, topic mapping for integration

### Utilities
- **`expose_mqtt.py`** - Expose local MQTT broker via ngrok tunnel
- **Test clients** - Various test clients for different scenarios

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
# Test connection to TVS broker (when AMRs are online)
python -X utf8 tvs_real_data_subscriber.py

# Run data structure comparison
python -X utf8 data_structure_comparison.py

# Expose broker to external clients
python -X utf8 expose_mqtt.py

# Test local MQTT connection
python -X utf8 twinzo_test_client.py
```

### Development Tools
```bash
# Verify system setup
python -X utf8 verify_system.py

# Test MQTT credentials
python -X utf8 verify_credentials.py

# Simple MQTT test
python -X utf8 simple_mqtt_test.py
```

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

#### TVS Integration
- Host: `tvs-dev.ifactory.ai:8883` (MQTT5 with TLS)
- Client ID: `amr-001`
- Credentials: `amr-001` / `TVSamr001@2025`
- Known AMR MAC addresses in `device_mapping.json`

#### Twinzo Integration
- OAuth endpoint: `https://api.platform.twinzo.com/v3/authorization/authenticate`
- Localization endpoint: `https://api.platform.twinzo.com/v3/localization`
- Per-device OAuth authentication with credential caching

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