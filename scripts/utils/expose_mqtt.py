import ngrok
import asyncio
import subprocess

async def create_tunnel():
    # Set your ngrok auth token
    ngrok.set_auth_token("30ilj8Rj8hAmLUtOU8OmOqsotYs_4XPhwPJ64iaN4Z1pAbLS6")
    
    print("🚀 Exposing MQTT broker to Twinzo...")
    print("=" * 50)
    
    # Check if broker is running
    result = subprocess.run(["docker", "ps", "--filter", "name=mock-mqtt-broker"], 
                          capture_output=True, text=True)
    
    if "mock-mqtt-broker" not in result.stdout:
        print("❌ MQTT broker is not running!")
        print("   Start with: docker-compose up -d")
        return
    
    # Create an HTTP tunnel to port 9001 (WebSockets)
    listener = await ngrok.connect(9001, "http")
    
    # Convert HTTPS URL to WSS for WebSocket connection
    wss_url = listener.url().replace('https://', 'wss://')
    host_only = listener.url().replace('https://', '')
    
    print(f"✅ MQTT WebSocket broker exposed!")
    print("=" * 70)
    print("📋 COPY THESE CONNECTION DETAILS:")
    print("=" * 70)
    
    print(f"\n🌐 WebSocket URL: {wss_url}")
    print(f"🔐 Username: mock_tvs")
    print(f"🔐 Password: Twinzo2025!@#")
    print(f"📡 Topic: ati_fm/sherpa/status")
    
    print("\n" + "=" * 70)
    print("📋 COPY-PASTE READY CONNECTION CODE:")
    print("=" * 70)
    
    print("\n🐍 Python Connection Code:")
    print("-" * 40)
    print(f'''import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe("ati_fm/sherpa/status")
    else:
        print(f"❌ Connection failed: {{rc}}")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    device = data.get("sherpa_name", "unknown")
    battery = data.get("battery_status", 0)
    pose = data.get("pose", [])
    if len(pose) >= 2:
        print(f"📦 {{device}}: X={{pose[0]:.1f}}, Y={{pose[1]:.1f}}, Battery={{battery}}%")

client = mqtt.Client()
client.username_pw_set("mock_tvs", "Twinzo2025!@#")
client.on_connect = on_connect
client.on_message = on_message

# Connect using WebSocket
client.connect("{host_only}", 443, 60)
client.loop_forever()''')
    
    print("\n🟨 JavaScript/Node.js Connection Code:")
    print("-" * 40)
    print(f'''const mqtt = require('mqtt');

const client = mqtt.connect('{wss_url}', {{
  username: 'mock_tvs',
  password: 'Twinzo2025!@#',
  keepalive: 60
}});

client.on('connect', () => {{
  console.log('✅ Connected to MQTT broker');
  client.subscribe('ati_fm/sherpa/status');
}});

client.on('message', (topic, message) => {{
  const data = JSON.parse(message.toString());
  const device = data.sherpa_name || 'unknown';
  const battery = data.battery_status || 0;
  const pose = data.pose || [];
  if (pose.length >= 2) {{
    console.log(`📦 ${{device}}: X=${{pose[0].toFixed(1)}}, Y=${{pose[1].toFixed(1)}}, Battery=${{battery}}%`);
  }}
}});''')
    
    print("\n🔍 Sample Message Format:")
    print("-" * 40)
    print('''{
  "sherpa_name": "tugger-01",
  "mode": "Fleet",
  "error": "",
  "disabled": false,
  "disabled_reason": "",
  "pose": [220000.0, 209000.0, 0.0, 0.0, 0.0, 1.57],
  "battery_status": 79.0,
  "trip_id": 1001,
  "trip_leg_id": 5001
}''')
    
    print("\n" + "=" * 70)
    print("📊 SYSTEM STATUS:")
    print("=" * 70)
    print("• 3 devices streaming: tugger-01, tugger-02, tugger-03")
    print("• Update frequency: 10Hz per device (~30 messages/second)")
    print("• Real-time coordinates in meters")
    print("• Battery levels: 79%, 77%, 75%")
    print("=" * 70)
    
    # Keep the tunnel open
    print("\n⏳ Tunnel is active. Press Ctrl+C to close...")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Closing tunnel...")
    finally:
        await listener.close()
        print("✅ Tunnel closed")

if __name__ == "__main__":
    asyncio.run(create_tunnel())