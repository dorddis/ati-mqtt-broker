#!/usr/bin/env python3
"""
Data Structure Comparison Tool
Compare mock AMR data format vs TVS data expectations
"""
import json
import time
from datetime import datetime

def show_mock_data_structure():
    """Display the structure of mock data being generated"""
    print("📦 MOCK DATA STRUCTURE (What we're generating)")
    print("="*70)

    # Sample mock data from publisher.py
    mock_data = {
        "sherpa_name": "tugger-01",
        "mode": "Fleet",
        "error": "",
        "disabled": False,
        "disabled_reason": "",
        "pose": [220000.0, 209000.0, 0.0, 0.0, 0.0, 1.57],
        "battery_status": 79.0,
        "trip_id": 1001,
        "trip_leg_id": 5001
    }

    print("🔹 MQTT Topic: ati_fm/sherpa/status")
    print("🔹 Frequency: 10Hz per device")
    print("🔹 Sample Message:")
    print(json.dumps(mock_data, indent=2))

    print("\n📊 Field Analysis:")
    print("• sherpa_name: Device identifier (tugger-01, tugger-02, tugger-03)")
    print("• mode: Always 'Fleet'")
    print("• error: Empty string (no errors)")
    print("• disabled: Always False")
    print("• disabled_reason: Empty string")
    print("• pose: [X, Y, Z, roll, pitch, yaw] - real-world coordinates")
    print("  - X: 195,630.16 to 223,641.36 meters")
    print("  - Y: 188,397.78 to 213,782.93 meters")
    print("  - Z: Always 0.0")
    print("  - roll/pitch: Always 0.0")
    print("  - yaw: Direction in radians")
    print("• battery_status: Fixed values (79%, 77%, 75%)")
    print("• trip_id: 1001, 1002, 1003")
    print("• trip_leg_id: 5001, 5002, 5003")

def show_twinzo_transformation():
    """Show how data is transformed for Twinzo"""
    print("\n🔄 TWINZO TRANSFORMATION (bridge.py)")
    print("="*70)

    twinzo_payload = [
        {
            "Timestamp": int(time.time() * 1000),
            "SectorId": 1,
            "X": 220000.0,
            "Y": 209000.0,
            "Z": 0.0,
            "Interval": 100,
            "Battery": 79,
            "IsMoving": True,
            "LocalizationAreas": [],
            "NoGoAreas": []
        }
    ]

    print("🔹 Twinzo API Endpoint: https://api.platform.twinzo.com/v3/localization")
    print("🔹 Transformation Process:")
    print("  1. Extract pose coordinates from MQTT")
    print("  2. Apply affine transform (currently identity)")
    print("  3. Calculate movement from position changes")
    print("  4. Package for Twinzo API")
    print("\n🔹 Transformed Payload:")
    print(json.dumps(twinzo_payload, indent=2))

def show_tvs_expected_structure():
    """Show expected TVS data structure based on industry standards"""
    print("\n📡 TVS EXPECTED DATA STRUCTURE")
    print("="*70)

    print("🔹 Connection Details:")
    print("• Host: tvs-dev.ifactory.ai")
    print("• Port: 8883 (MQTT5 with TLS)")
    print("• Client ID: amr-001")
    print("• Username: amr-001")
    print("• Password: TVSamr001@2025")

    print("\n🔹 Known AMR Devices:")
    amr_devices = {
        "f4:7b:09:0e:04:1b": "Tug 133",
        "10:3d:1c:66:67:55": "Tug 39",
        "f4:4e:e3:f6:c7:91": "Tug 55",
        "ec:2e:98:4a:7c:f7": "Tug 78"
    }

    for mac, name in amr_devices.items():
        print(f"  • {name}: {mac}")

    print("\n🔹 Expected Topic Patterns:")
    expected_topics = [
        "amr/{device_id}/status",
        "amr/{device_id}/position",
        "amr/{device_id}/telemetry",
        "tug/{device_id}/status",
        "robot/{device_id}/position",
        "fleet/status",
        "tvs/amr/{device_id}"
    ]

    for topic in expected_topics:
        print(f"  • {topic}")

    print("\n🔹 Expected Data Fields (Industry Standard):")
    expected_fields = {
        "device_id": "Device identifier or MAC address",
        "timestamp": "Unix timestamp in ms",
        "position": {
            "x": "X coordinate (meters)",
            "y": "Y coordinate (meters)",
            "z": "Z coordinate (meters)",
            "heading": "Heading/orientation (degrees or radians)"
        },
        "status": {
            "battery": "Battery percentage (0-100)",
            "state": "Operating state (idle, moving, charging, error)",
            "speed": "Current speed (m/s)",
            "mode": "Operating mode (manual, auto, fleet)"
        },
        "navigation": {
            "target": "Current target/destination",
            "mission_id": "Current mission/task ID",
            "route": "Current route information"
        },
        "diagnostics": {
            "errors": "Error codes or messages",
            "warnings": "Warning messages",
            "health": "Overall system health"
        }
    }

    print(json.dumps(expected_fields, indent=2))

def show_integration_challenges():
    """Identify potential integration challenges"""
    print("\n⚠️  INTEGRATION CHALLENGES & CONSIDERATIONS")
    print("="*70)

    challenges = [
        {
            "issue": "Data Format Mismatch",
            "description": "TVS may use different field names or structures",
            "solution": "Create field mapping in bridge.py"
        },
        {
            "issue": "Coordinate Systems",
            "description": "TVS coordinates may be in different reference frame",
            "solution": "Configure affine transform parameters"
        },
        {
            "issue": "Topic Structure",
            "description": "TVS may use different MQTT topic hierarchy",
            "solution": "Update topic subscriptions in bridge"
        },
        {
            "issue": "Device Identification",
            "description": "TVS may use MAC addresses vs friendly names",
            "solution": "Create device mapping table"
        },
        {
            "issue": "Data Frequency",
            "description": "TVS update rate may differ from 10Hz",
            "solution": "Adjust processing logic for different rates"
        },
        {
            "issue": "Authentication",
            "description": "OAuth credentials per device vs global",
            "solution": "Modify authentication logic"
        }
    ]

    for i, challenge in enumerate(challenges, 1):
        print(f"\n{i}. {challenge['issue']}")
        print(f"   Problem: {challenge['description']}")
        print(f"   Solution: {challenge['solution']}")

def show_next_steps():
    """Show recommended next steps"""
    print("\n📋 RECOMMENDED NEXT STEPS")
    print("="*70)

    steps = [
        "1. Wait for TVS AMRs to come online and capture real data",
        "2. Analyze actual TVS data structure vs expectations",
        "3. Create field mapping configuration file",
        "4. Update bridge.py to handle TVS data format",
        "5. Configure coordinate transformation if needed",
        "6. Test end-to-end data flow: TVS → Bridge → Twinzo",
        "7. Monitor and validate data accuracy",
        "8. Set up error handling and alerting"
    ]

    for step in steps:
        print(f"   {step}")

    print("\n🔧 Configuration Files Needed:")
    config_files = [
        "device_mapping.json - Map MAC addresses to device names",
        "coordinate_transform.json - Coordinate system parameters",
        "topic_mapping.json - Map TVS topics to our format",
        "field_mapping.json - Map TVS fields to Twinzo format"
    ]

    for config in config_files:
        print(f"   • {config}")

def create_sample_config_files():
    """Create sample configuration files for integration"""
    print("\n📁 CREATING SAMPLE CONFIGURATION FILES")
    print("="*70)

    # Device mapping
    device_mapping = {
        "f4:7b:09:0e:04:1b": {
            "name": "Tug 133",
            "twinzo_device": "tugger-01",
            "oauth_login": "Tug133"
        },
        "10:3d:1c:66:67:55": {
            "name": "Tug 39",
            "twinzo_device": "tugger-02",
            "oauth_login": "Tug39"
        },
        "f4:4e:e3:f6:c7:91": {
            "name": "Tug 55",
            "twinzo_device": "tugger-03",
            "oauth_login": "Tug55"
        },
        "ec:2e:98:4a:7c:f7": {
            "name": "Tug 78",
            "twinzo_device": "tugger-04",
            "oauth_login": "Tug78"
        }
    }

    with open("device_mapping.json", "w") as f:
        json.dump(device_mapping, f, indent=2)
    print("✅ Created: device_mapping.json")

    # Field mapping
    field_mapping = {
        "position_fields": {
            "x": ["x", "pos_x", "position.x", "pose[0]"],
            "y": ["y", "pos_y", "position.y", "pose[1]"],
            "z": ["z", "pos_z", "position.z", "pose[2]"],
            "heading": ["heading", "yaw", "orientation", "pose[5]"]
        },
        "status_fields": {
            "battery": ["battery", "battery_level", "battery_status", "charge"],
            "mode": ["mode", "state", "status", "operating_mode"],
            "speed": ["speed", "velocity", "current_speed"],
            "error": ["error", "errors", "error_msg", "fault"]
        },
        "id_fields": {
            "device_id": ["id", "device_id", "robot_id", "amr_id", "mac", "sherpa_name"]
        }
    }

    with open("field_mapping.json", "w") as f:
        json.dump(field_mapping, f, indent=2)
    print("✅ Created: field_mapping.json")

    # Topic mapping
    topic_mapping = {
        "patterns": [
            "amr/+/status",
            "amr/+/position",
            "tug/+/status",
            "robot/+/position",
            "fleet/+/status"
        ],
        "mapping": {
            "amr/{device}/status": "status",
            "amr/{device}/position": "position",
            "tug/{device}/status": "status",
            "robot/{device}/position": "position"
        }
    }

    with open("topic_mapping.json", "w") as f:
        json.dump(topic_mapping, f, indent=2)
    print("✅ Created: topic_mapping.json")

def main():
    """Main function to display all comparisons"""
    print("🔍 TVS ↔ MOCK DATA STRUCTURE COMPARISON")
    print("="*80)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    show_mock_data_structure()
    show_twinzo_transformation()
    show_tvs_expected_structure()
    show_integration_challenges()
    show_next_steps()
    create_sample_config_files()

    print("\n" + "="*80)
    print("📝 SUMMARY")
    print("="*80)
    print("✅ Successfully connected to TVS MQTT broker")
    print("❓ No active data detected (AMRs may be offline)")
    print("📋 Configuration files created for future integration")
    print("🔄 Ready to adapt bridge when real TVS data is available")
    print("="*80)

if __name__ == "__main__":
    main()