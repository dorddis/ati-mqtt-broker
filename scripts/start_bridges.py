#!/usr/bin/env python3
"""
Master Startup Script for Twinzo Multi-Plant Bridges

Launches both production bridges:
1. ATI MQTTS -> Old Plant (Sector 2)
2. HiveMQ Cloud -> HiTech Plant (Sector 1)

Usage:
  python -X utf8 start_bridges.py           # Start both bridges
  python -X utf8 start_bridges.py old       # Start only Old Plant bridge
  python -X utf8 start_bridges.py hitech    # Start only HiTech bridge
"""
import os
import sys
import subprocess
import time

def check_env_vars():
    """Check if required environment variables are set"""
    print("="*70)
    print("Checking Environment Configuration")
    print("="*70)

    warnings = []

    # Twinzo credentials (required for both)
    if not os.getenv("TWINZO_PASSWORD"):
        warnings.append("TWINZO_PASSWORD not set (using default)")
    if not os.getenv("TWINZO_API_KEY"):
        warnings.append("TWINZO_API_KEY not set (using default)")

    # ATI MQTTS credentials (for Old Plant bridge)
    if not os.getenv("ATI_MQTT_USERNAME"):
        warnings.append("ATI_MQTT_USERNAME not set (Old Plant bridge will wait for credentials)")
    if not os.getenv("ATI_MQTT_PASSWORD"):
        warnings.append("ATI_MQTT_PASSWORD not set (Old Plant bridge will wait for credentials)")

    # HiveMQ credentials (checked from config file, not env vars)
    if not os.path.exists("config/hivemq_config.json"):
        warnings.append("config/hivemq_config.json not found (HiTech bridge may fail)")

    if warnings:
        print("\nWARN Configuration warnings:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("OK All required environment variables are set")

    print("="*70 + "\n")
    return len(warnings) == 0

def start_bridge(bridge_name, script_path):
    """Start a bridge in a subprocess"""
    print(f"Starting {bridge_name}...")
    print(f"  Script: {script_path}")

    try:
        # Use python -X utf8 for Windows compatibility
        process = subprocess.Popen(
            [sys.executable, "-X", "utf8", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        print(f"OK {bridge_name} started (PID: {process.pid})\n")
        return process
    except Exception as e:
        print(f"FAIL Failed to start {bridge_name}: {e}\n")
        return None

def main():
    """Main startup orchestration"""
    print("\n")
    print("="*70)
    print("Twinzo Multi-Plant Bridge System")
    print("="*70)
    print("This will start bridges for:")
    print("  1. ATI MQTTS -> Old Plant (Sector 2) - tugger-05-old, tugger-06-old")
    print("  2. HiveMQ Cloud -> HiTech Plant (Sector 1) - tugger-03, tugger-04")
    print("="*70 + "\n")

    # Check environment
    check_env_vars()

    # Determine which bridges to start
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "both"

    processes = []

    if mode in ["both", "old"]:
        old_plant_bridge = start_bridge(
            "Old Plant Bridge",
            "src/bridge/bridge_old_plant.py"
        )
        if old_plant_bridge:
            processes.append(("Old Plant", old_plant_bridge))
        time.sleep(2)  # Stagger startup

    if mode in ["both", "hitech"]:
        hitech_bridge = start_bridge(
            "HiTech Plant Bridge",
            "src/bridge/bridge_hitech.py"
        )
        if hitech_bridge:
            processes.append(("HiTech", hitech_bridge))

    if not processes:
        print("FAIL No bridges started. Exiting.")
        return 1

    print("="*70)
    print(f"OK {len(processes)} bridge(s) running")
    print("="*70)
    print("Press Ctrl+C to stop all bridges\n")

    try:
        # Monitor processes
        while True:
            for name, proc in processes:
                line = proc.stdout.readline()
                if line:
                    print(f"[{name}] {line.rstrip()}")

            # Check if any process has died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\nWARN {name} bridge has stopped (exit code: {proc.returncode})")
                    processes.remove((name, proc))

            if not processes:
                print("FAIL All bridges have stopped. Exiting.")
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nShutting down bridges...")
        for name, proc in processes:
            print(f"  Stopping {name} bridge...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
                print(f"    OK {name} bridge stopped")
            except subprocess.TimeoutExpired:
                print(f"    WARN {name} bridge did not stop gracefully, killing...")
                proc.kill()
                proc.wait()
        print("OK All bridges stopped\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
