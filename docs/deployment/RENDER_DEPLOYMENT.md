# Render Deployment Instructions

## Quick Setup (5 minutes)

### 1. Create Render Account
- Go to https://render.com
- Sign up with GitHub (free)
- No credit card required

### 2. Deploy from GitHub
- Connect your GitHub repo
- Select "Web Service"
- Choose this repository
- Render auto-detects render.yaml

### 3. Get Your URL
After deployment completes:
- Your app will be at: https://your-app-name.onrender.com
- WebSocket URL: wss://your-app-name.onrender.com

### 4. Test Connection
```bash
# Monitor your broker
python monitor_render_mqtt.py --url https://your-app-name.onrender.com
```

### 5. Share with ATI
Give ATI these details:
```
MQTT WebSocket URL: wss://your-app-name.onrender.com
Username: ati_user
Password: ati_password_123
Topics: ati/amr/status, amr/position, etc.
```

## Important Notes

**Sleep Behavior:**
- Service sleeps after 15 minutes of no HTTP requests
- WebSocket connections don't prevent sleep
- Monitor script includes keep-alive HTTP pings
- ATI can add keep-alive pings too

**Free Tier Limits:**
- 750 hours/month (31+ days)
- No bandwidth limits
- 1GB disk storage
- Automatic SSL/HTTPS

**Keep Awake Options:**
1. Monitor script (recommended)
2. ATI adds keep-alive HTTP requests
3. External uptime monitor (UptimeRobot, etc.)

## Troubleshooting

**Service won't start:**
- Check build logs in Render dashboard
- Ensure Dockerfile.render is correct

**Connection refused:**
- Service may be sleeping
- Try HTTP request to https://your-app.onrender.com/health
- Wait 30 seconds for wake-up

**Can't connect via WebSocket:**
- URL should start with wss:// not ws://
- Port should be 443 (default for wss)
- Render handles SSL termination
