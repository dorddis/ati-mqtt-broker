#!/usr/bin/env python3
"""
Quick monitoring script for Twinzo Docker containers
"""
import subprocess
import sys
import time

def run_command(cmd):
    """Run a command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"Error: {e}", 1

def show_status():
    """Show container status"""
    print("🐳 DOCKER CONTAINER STATUS")
    print("=" * 50)
    output, _ = run_command("docker-compose ps")
    print(output)
    print()

def show_recent_logs():
    """Show recent bridge logs"""
    print("📋 RECENT BRIDGE LOGS (last 10 lines)")
    print("=" * 50)
    output, _ = run_command("docker-compose logs --tail=10 bridge")
    print(output)
    print()

def show_live_logs():
    """Show live bridge logs"""
    print("📡 LIVE BRIDGE LOGS (Ctrl+C to stop)")
    print("=" * 50)
    subprocess.run("docker-compose logs -f bridge", shell=True)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            show_status()
        elif sys.argv[1] == "logs":
            show_recent_logs()
        elif sys.argv[1] == "live":
            show_live_logs()
        elif sys.argv[1] == "stop":
            print("🛑 Stopping containers...")
            run_command("docker-compose down")
            print("✅ Containers stopped")
        elif sys.argv[1] == "start":
            print("🚀 Starting containers...")
            run_command("docker-compose up -d")
            print("✅ Containers started")
        elif sys.argv[1] == "restart":
            print("🔄 Restarting containers...")
            run_command("docker-compose restart")
            print("✅ Containers restarted")
        else:
            print("❌ Unknown command. Use: status, logs, live, stop, start, restart")
    else:
        # Default: show status and recent logs
        show_status()
        show_recent_logs()
        
        print("💡 USAGE:")
        print("  python monitor_twinzo.py status    - Show container status")
        print("  python monitor_twinzo.py logs      - Show recent logs")
        print("  python monitor_twinzo.py live      - Show live logs")
        print("  python monitor_twinzo.py stop      - Stop containers")
        print("  python monitor_twinzo.py start     - Start containers")
        print("  python monitor_twinzo.py restart   - Restart containers")

if __name__ == "__main__":
    main()