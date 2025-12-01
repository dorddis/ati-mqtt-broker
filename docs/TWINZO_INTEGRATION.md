Twinzo Direct MQTT Integration
Prepared by: Factories of Future 
Date: 2025-11-13 
Purpose: Direct ATI MQTT subscription implementation


1. MQTT Connection - Important
```javascript
const mqtt = require('mqtt');


const client = mqtt.connect({
  protocol: 'mqtts',
  host: 'tvs-dev.ifactory.ai',
  port: 8883,
  username: 'tvs-audit-user',
  password: 'TVSAudit@2025',
  clientId: 'tvs-audit-user',  // MUST match username
  protocolVersion: 5,
  clean: true,
  reconnectPeriod: 5000,
  rejectUnauthorized: false
});


client.on('connect', () => {
  client.subscribe({ 'ati_fm/#': { qos: 1 } });
});
```

2. Message Processing - Important
```javascript
client.on('message', async (topic, message) => {
  // Filter
  if (topic !== 'ati_fm/sherpa/status') return;


  const data = JSON.parse(message.toString());


  // Validate
  if (data.mode !== 'fleet') return;
  if (!data.pose || data.pose.length < 3) return;


  const deviceMap = {
    'tug-55-tvsmotor-hosur-09': 'tug-55-hosur-09',
    'tug-39-tvsmotor-hosur-07': 'tug-39-hosur-07',
    'tug-133': 'tug-133'
  };


  const twinzoDevice = deviceMap[data.sherpa_name];
  if (!twinzoDevice) return;


  // Transform coordinates
  const [x_ati, y_ati, heading] = data.pose;
  const [x_twinzo, y_twinzo] = transformCoordinates(x_ati, y_ati);


  // Send to Twinzo
  await sendToTwinzo(twinzoDevice, x_twinzo, y_twinzo, heading, data.battery_status);
});
```

3. ATI Message Format - What You Receive
```javascript
// Topic: ati_fm/sherpa/status
// Message payload:
{
  "sherpa_name": "tug-55-tvsmotor-hosur-09",  // Device identifier
  "pose": [82.45, 12.33, 1.57],               // [x_meters, y_meters, heading_radians]
  "battery_status": 78,                       // Battery percentage (0-100)
  "mode": "fleet",                            // "fleet" = moving, "disconnected" = idle
  "timestamp": 1705172345000                  // Unix timestamp (optional)
}

// Coordinate ranges (ATI in meters):
// X: -1.3 to 117.0 meters
// Y: -11.0 to 76.4 meters
// Heading: 0 to 2π radians
```

4. Coordinate Transformation - Important
```javascript
const AFFINE = {
  A:  999.738230,
  B:  22.879501,
  C:  22.879501,
  D: -999.738230,
  TX: 95598.77,
  TY: 167357.60
};


function transformCoordinates(x_ati, y_ati) {
  const x_twinzo = AFFINE.A * x_ati + AFFINE.B * y_ati + AFFINE.TX;
  const y_twinzo = AFFINE.C * x_ati + AFFINE.D * y_ati + AFFINE.TY;
  return [x_twinzo, y_twinzo];
}
```

5. Twinzo API Integration - what FoF used
```javascript
const TWINZO_CONFIG = {
  client: 'TVSMotor',
  password: 'Tvs@Hosur$2025',
  apiKey: 'sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S',
  authUrl: 'https://api.platform.twinzo.com/v3/authorization/authenticate',
  locUrl: 'https://api.platform.twinzo.com/v3/localization',
  sector: 2,  // Old Plant
  branch: '40557468-2d57-4a3d-9a5e-3eede177daf5'
};


const tokenCache = {};


async function authenticateDevice(deviceLogin) {
  const response = await fetch(TWINZO_CONFIG.authUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client: TWINZO_CONFIG.client,
      login: deviceLogin,
      password: TWINZO_CONFIG.password
    })
  });


  const data = await response.json();
  tokenCache[deviceLogin] = {
    token: data.Token,
    client: data.Client,
    branch: data.Branch,
    expires: data.Expiration
  };


  return tokenCache[deviceLogin];
}


async function getToken(deviceLogin) {
  const cached = tokenCache[deviceLogin];
  const now = Date.now();


  if (cached && cached.expires > now + 60000) {
    return cached;
  }


  return await authenticateDevice(deviceLogin);
}


async function sendToTwinzo(deviceLogin, x, y, heading, battery) {
  const creds = await getToken(deviceLogin);


  const payload = [{  // MUST be array
    Timestamp: Date.now(),
    SectorId: TWINZO_CONFIG.sector,
    X: x,
    Y: y,
    Z: 0,
    Interval: 100,
    Battery: battery,
    IsMoving: true,
    LocalizationAreas: [],
    NoGoAreas: []
  }];


  const response = await fetch(TWINZO_CONFIG.locUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Client': creds.client,
      'Branch': creds.branch,
      'Token': creds.token,
      'Api-Key': TWINZO_CONFIG.apiKey
    },
    body: JSON.stringify(payload)
  });


  return response.ok || response.status === 204;
}
```

6. Dependencies - Important
```bash
npm install mqtt node-fetch
```

7. Environment Variables - Important
```bash
# ATI MQTT
AUDIT_MQTT_HOST=tvs-dev.ifactory.ai
AUDIT_MQTT_PORT=8883
AUDIT_USERNAME=tvs-audit-user
AUDIT_PASSWORD=TVSAudit@2025


# Twinzo API
TWINZO_CLIENT=TVSMotor
TWINZO_PASSWORD=Tvs@Hosur$2025
TWINZO_API_KEY=sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S


# Affine Transform
AFFINE_A=999.738230
AFFINE_B=22.879501
AFFINE_C=22.879501
AFFINE_D=-999.738230
AFFINE_TX=95598.77
AFFINE_TY=167357.60
```

8. Test Data - Validation
```javascript
// Test Input (ATI Message):
{
  "sherpa_name": "tug-55-tvsmotor-hosur-09",
  "pose": [82.45, 12.33, 1.57],
  "battery_status": 78,
  "mode": "fleet"
}

// Expected Output (After Transform):
X_twinzo ≈ 178,000 mm
Y_twinzo ≈ 155,000 mm
```

9. Critical Requirements
- Client ID must equal username: `tvs-audit-user`
- Only process messages where `mode === 'fleet'`
- API payload must be array: `[{...}]` not `{...}`
- Headers: `Client`, `Branch`, `Token`, `Api-Key` (not `Authorization`)
- Coordinate D coefficient is negative (Y-axis flip)
- Cache OAuth tokens (expire after ~1 hour)
- Ignore devices not in DEVICE_MAP
































Provided by Factories of Future - Advanced Manufacturing Integration Solutions
