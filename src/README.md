# Source Code

Core application code for the Twinzo Mock AMR system.

## Structure

### publisher/
Mock AMR data generator that simulates realistic robot movement patterns.
- Generates location data for multiple robots
- Configurable movement patterns (loop, line, rectangle)
- MQTT-based data publishing
- See publisher/README.md for details

### bridge/
MQTT-to-Twinzo REST API bridge with OAuth authentication.
- Subscribes to MQTT topics
- Transforms data to Twinzo format
- Handles OAuth authentication and token caching
- Posts location data to Twinzo API
- See bridge/README.md for details

### common/
Shared utilities and common code used across components.
- Configuration helpers
- MQTT utilities
- Data transformation functions

## Development

Each component is designed to run independently:
- As Docker containers (see docker-compose.yml)
- As standalone Python scripts for testing
- With configurable environment variables

See the root README.md for usage instructions.
