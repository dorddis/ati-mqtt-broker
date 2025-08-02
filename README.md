# Twinzo Mock System

A Docker-based system that simulates tugger devices and streams real-time location data to the Twinzo platform using OAuth authentication.

## 🎯 **Overview**

This system creates a complete mock environment for testing Twinzo API integration:
- **3 Tugger devices** (tugger-01, tugger-02, tugger-03) with realistic movement patterns
- **OAuth authentication** with automatic token management
- **Real-time location streaming** to Twinzo platform
- **MQTT-based architecture** for scalable device simulation

## 🏗️ **Architecture**

```
┌─────────────────┐    MQTT     ┌─────────────────┐    OAuth+API    ┌─────────────────┐
│   Publisher     │ ──────────► │     Bridge      │ ──────────────► │  Twinzo API     │
│ (Mock Devices)  │             │ (Auth + Proxy)  │                 │   Platform      │
└─────────────────┘             └─────────────────┘                 └─────────────────┘
         │                               │
         ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│  MQTT Broker    │             │ Token Cache +   │
│  (Mosquitto)    │             │ Movement Logic  │
└─────────────────┘             └─────────────────┘
```

## 🚀 **Quick Start**

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for monitoring tools)

### Running the System
```bash
# Start all containers
docker-compose up -d

# Monitor status and logs
python monitor_twinzo.py

# View live data stream
python monitor_twinzo.py live

# Stop the system
python monitor_twinzo.py stop
```

## 📊 **Device Configuration**

| Device    | Battery | Movement Pattern | Speed    |
|-----------|---------|------------------|----------|
| tugger-01 | 79%     | Loop pattern     | 800 u/s  |
| tugger-02 | 77%     | Loop pattern     | 1000 u/s |
| tugger-03 | 75%     | Loop pattern     | 1200 u/s |

**Coordinate Bounds:**
- Top Left: X: 195630.16, Y: 188397.78
- Bottom Right: X: 223641.36, Y: 213782.93

## 🔧 **Configuration**

### Environment Variables (docker-compose.yml)
```yaml
# Twinzo OAuth
TWINZO_CLIENT: "TVSMotor"
TWINZO_PASSWORD: "Tvs@Hosur$2025"
TWINZO_API_KEY: "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"

# Movement Settings
HZ: "10"                    # 10Hz update rate
REGION_MIN_X: "195630.16"   # Real-world coordinates
REGION_MIN_Y: "188397.78"
REGION_MAX_X: "223641.36"
REGION_MAX_Y: "213782.93"
```

## 📡 **API Integration**

### Working Configuration
- **Authentication URL**: `https://api.platform.twinzo.com/v3/authorization/authenticate`
- **Localization URL**: `https://api.platform.twinzo.com/v3/localization`
- **Headers**: `Token`, `Client`, `Branch`, `Api-Key`
- **Payload Format**: Direct array (not wrapped in object)

### Sample Payload
```json
[
  {
    "Timestamp": 1754132294838,
    "SectorId": 1,
    "X": 200000.0,
    "Y": 200000.0,
    "Z": 0.0,
    "Interval": 100,
    "Battery": 79,
    "IsMoving": true,
    "LocalizationAreas": [],
    "NoGoAreas": []
  }
]
```

## 🛠️ **Monitoring Tools**

### monitor_twinzo.py
```bash
python monitor_twinzo.py status    # Container status
python monitor_twinzo.py logs      # Recent logs
python monitor_twinzo.py live      # Live log stream
python monitor_twinzo.py restart   # Restart containers
```

## 📁 **Project Structure**

```
twinzo-mock/
├── docker-compose.yml          # Main orchestration
├── bridge/
│   └── bridge.py               # OAuth + API bridge
├── publisher/
│   ├── publisher.py            # Device simulator
│   └── requirements.txt
├── mosquitto/
│   └── mosquitto.conf          # MQTT broker config
├── monitor_twinzo.py           # Monitoring utility
└── README.md                   # This file
```

## 🔍 **Key Features**

- **Dynamic OAuth**: Automatic device authentication with token caching
- **Movement Detection**: Smart IsMoving calculation based on coordinate changes
- **Battery Simulation**: Device-specific battery levels
- **Error Handling**: Comprehensive logging and error recovery
- **Real-time Updates**: 10Hz location streaming
- **Scalable Architecture**: Easy to add more devices

## 🎯 **Success Metrics**

- ✅ All 3 tugger devices visible on Twinzo platform
- ✅ Real-time movement tracking
- ✅ Correct battery levels (79%, 77%, 75%)
- ✅ OAuth authentication working
- ✅ 200 OK API responses
- ✅ Movement detection active

## 🔧 **Troubleshooting**

### Common Issues
1. **401 Unauthorized**: Check OAuth credentials
2. **400 Bad Request**: Verify payload format
3. **Devices not moving**: Check coordinate bounds and movement speed
4. **Container startup issues**: Check Docker logs

### Debug Commands
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs bridge --tail=50

# Test API directly
python test_final_format.py
```

## 📚 **Development Notes**

This system was developed through iterative testing and debugging of the Twinzo API integration. Key learnings are documented in the project history.

---

**Status**: ✅ Production Ready  
**Last Updated**: August 2025  
**Twinzo API Version**: v3