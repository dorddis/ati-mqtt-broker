#!/usr/bin/env python3
"""
HTTP-only integration test for ATI
Tests the working HTTP REST API method
"""
import requests
import json
import time

def test_multiple_amr_publishing():
    """Test publishing data for multiple AMRs like ATI would"""
    print("🧪 Testing Multiple AMR Data Publishing (ATI Simulation)")

    amr_data = [
        {
            "sherpa_name": "tugger-01",
            "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
            "battery_status": 79.5,
            "mode": "Fleet",
        },
        {
            "sherpa_name": "tugger-02",
            "pose": [195635.22, 188402.33, 0.0, 0.0, 0.0, 2.14],
            "battery_status": 82.1,
            "mode": "Fleet",
        },
        {
            "sherpa_name": "sherpa-01",
            "pose": [195628.91, 188395.44, 0.0, 0.0, 0.0, 0.78],
            "battery_status": 74.8,
            "mode": "Manual",
        }
    ]

    results = []

    for i, amr in enumerate(amr_data):
        print(f"\n📡 Publishing data for {amr['sherpa_name']}...")

        # Add timestamp and trip info
        amr.update({
            "timestamp": int(time.time() * 1000),
            "error": "",
            "disabled": False,
            "trip_id": 1000 + i,
            "trip_leg_id": 5000 + i
        })

        payload = {
            "topic": f"ati/amr/{amr['sherpa_name']}/status",
            "message": amr
        }

        try:
            response = requests.post(
                "https://ati-mqtt-broker.onrender.com/publish",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result}")
                results.append({"amr": amr['sherpa_name'], "status": "success", "result": result})
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                results.append({"amr": amr['sherpa_name'], "status": "failed", "error": response.text})

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"amr": amr['sherpa_name'], "status": "error", "error": str(e)})

        # Small delay between publishes
        time.sleep(0.5)

    return results

def test_high_frequency_publishing():
    """Test high frequency publishing like real AMR updates"""
    print("\n🧪 Testing High-Frequency Publishing (10 Hz simulation)")

    amr_name = "test-high-freq-amr"
    base_x, base_y = 195630.0, 188400.0

    success_count = 0
    total_count = 10  # 10 messages over 1 second = 10 Hz

    for i in range(total_count):
        # Simulate movement
        x = base_x + (i * 0.1)  # Move 0.1 units each update
        y = base_y + (i * 0.05)  # Move 0.05 units each update
        yaw = (i * 0.1) % (2 * 3.14159)  # Rotate slightly

        data = {
            "topic": f"ati/amr/{amr_name}/position",
            "message": {
                "sherpa_name": amr_name,
                "pose": [x, y, 0.0, 0.0, 0.0, yaw],
                "battery_status": 85.0 - (i * 0.1),  # Battery slowly decreases
                "timestamp": int(time.time() * 1000)
            }
        }

        try:
            response = requests.post(
                "https://ati-mqtt-broker.onrender.com/publish",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=5
            )

            if response.status_code == 200:
                success_count += 1
                print(f"✅ Message {i+1}/{total_count} published")
            else:
                print(f"❌ Message {i+1}/{total_count} failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Message {i+1}/{total_count} error: {e}")

        # 100ms delay for 10Hz
        time.sleep(0.1)

    success_rate = (success_count / total_count) * 100
    print(f"\n📊 High-Frequency Test Results: {success_count}/{total_count} success ({success_rate:.1f}%)")

    return success_rate >= 90  # Consider 90%+ success rate as passing

def main():
    print("🚀 ATI MQTT Broker - HTTP API Integration Test")
    print("=" * 55)

    # Test 1: Service Health
    print("🧪 Testing Service Health...")
    try:
        response = requests.get("https://ati-mqtt-broker.onrender.com/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Service Status: {status}")
            if not status.get('mqtt_connected'):
                print("⚠️  MQTT broker not connected - HTTP API may not work")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

    print("\n" + "="*55)

    # Test 2: Multiple AMR Publishing
    multi_amr_results = test_multiple_amr_publishing()

    print("\n" + "="*55)

    # Test 3: High-Frequency Publishing
    high_freq_success = test_high_frequency_publishing()

    print("\n" + "="*55)

    # Summary
    print("📊 Final Test Summary")
    print("="*25)

    successful_amrs = sum(1 for r in multi_amr_results if r['status'] == 'success')
    total_amrs = len(multi_amr_results)

    print(f"Multi-AMR Publishing: {successful_amrs}/{total_amrs} AMRs successful")
    print(f"High-Frequency Publishing: {'✅ PASS' if high_freq_success else '❌ FAIL'}")

    # Overall assessment
    all_tests_passed = (successful_amrs == total_amrs) and high_freq_success

    print(f"\n🎯 Overall Assessment: {'✅ PRODUCTION READY' if all_tests_passed else '⚠️  NEEDS REVIEW'}")

    if all_tests_passed:
        print("\n🎉 ATI MQTT Broker HTTP API is fully functional!")
        print("ATI can proceed with integration using:")
        print("  • URL: https://ati-mqtt-broker.onrender.com/publish")
        print("  • Method: HTTP POST")
        print("  • Content-Type: application/json")
        print("  • Data format: See ATI_MQTT_INTEGRATION_GUIDE.md")
    else:
        print("\n⚠️  Some issues detected. Review logs above.")

    return all_tests_passed

if __name__ == "__main__":
    main()