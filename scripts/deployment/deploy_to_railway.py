#!/usr/bin/env python3
"""
Deploy ATI MQTT Broker to Railway
Automated deployment script
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run command with error handling"""
    print(f"🚀 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def main():
    print("="*60)
    print("🚀 DEPLOYING ATI MQTT BROKER TO RAILWAY")
    print("="*60)

    # Check if Railway CLI is installed
    try:
        subprocess.run(["railway", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Railway CLI not found!")
        print("Install with: npm install -g @railway/cli")
        print("Or: brew install railway")
        sys.exit(1)

    # Check if logged in
    try:
        subprocess.run(["railway", "whoami"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️ Not logged in to Railway")
        run_command("railway login", "Logging in to Railway")

    # Initialize project if needed
    if not os.path.exists(".railway"):
        run_command("railway init", "Initializing Railway project")

    # Deploy
    run_command("railway up", "Deploying to Railway")

    # Get the URL
    try:
        url = subprocess.run(["railway", "domain"], capture_output=True, text=True, check=True)
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("="*60)
        print(f"🌐 Your ATI MQTT Broker URL: {url.stdout.strip()}")
        print()
        print("📋 For ATI Team:")
        print(f"   MQTT WebSocket: wss://{url.stdout.strip()}")
        print("   Username: ati_user")
        print("   Password: ati_password_123")
        print()
        print("📋 For Twinzo Integration:")
        print(f"   Subscribe to: wss://{url.stdout.strip()}")
        print("   Topics: ati/+/status, amr/+/position")
        print("="*60)
    except subprocess.CalledProcessError:
        print("⚠️ Could not get Railway URL automatically")
        print("Run 'railway domain' to get your deployment URL")

if __name__ == "__main__":
    main()
