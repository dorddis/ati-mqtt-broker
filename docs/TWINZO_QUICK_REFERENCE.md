# Twinzo Integration - Quick Reference

**From**: Factories of Future
**Date**: 2025-01-13

---

## MQTT Connection

```javascript
{
  host: 'tvs-dev.ifactory.ai',
  port: 8883,
  username: 'tvs-audit-user',
  password: 'TVSAudit@2025',
  clientId: 'tvs-audit-user',
  protocol: 'mqtts',
  protocolVersion: 5
}
```

Subscribe: `ati_fm/#` (QoS 1)
Filter: `ati_fm/sherpa/status` only

---

## Affine Transform (ATI meters → Twinzo mm)

```javascript
const A = 999.738230, B = 22.879501, C = 22.879501;
const D = -999.738230, TX = 95598.77, TY = 167357.60;

X_twinzo = A * X_ati + B * Y_ati + TX;
Y_twinzo = C * X_ati + D * Y_ati + TY;
```

---

## Device Map

```javascript
{
  'tug-55-tvsmotor-hosur-09': 'tug-55-hosur-09',
  'tug-39-tvsmotor-hosur-07': 'tug-39-hosur-07',
  'tug-133': 'tug-133'
}
```

Sector: 2 (Old Plant)
Branch: `40557468-2d57-4a3d-9a5e-3eede177daf5`

---

## Twinzo API

**Auth**: `https://api.platform.twinzo.com/v3/authorization/authenticate`
```json
{
  "client": "TVSMotor",
  "login": "tug-55-hosur-09",
  "password": "Tvs@Hosur$2025"
}
```

**Localization**: `https://api.platform.twinzo.com/v3/localization`
```javascript
Headers: {
  'Client': token.Client,
  'Branch': token.Branch,
  'Token': token.Token,
  'Api-Key': 'sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S'
}

Body: [{  // Array!
  Timestamp: Date.now(),
  SectorId: 2,
  X: x_twinzo,
  Y: y_twinzo,
  Z: 0,
  Interval: 100,
  Battery: battery,
  IsMoving: true,
  LocalizationAreas: [],
  NoGoAreas: []
}]
```

---

## Complete Code

```javascript
const mqtt = require('mqtt');
const fetch = require('node-fetch');

const client = mqtt.connect({
  protocol: 'mqtts',
  host: 'tvs-dev.ifactory.ai',
  port: 8883,
  username: 'tvs-audit-user',
  password: 'TVSAudit@2025',
  clientId: 'tvs-audit-user',
  protocolVersion: 5,
  rejectUnauthorized: false
});

const AFFINE = { A: 999.738230, B: 22.879501, C: 22.879501, D: -999.738230, TX: 95598.77, TY: 167357.60 };
const DEVICES = { 'tug-55-tvsmotor-hosur-09': 'tug-55-hosur-09', 'tug-39-tvsmotor-hosur-07': 'tug-39-hosur-07', 'tug-133': 'tug-133' };
const tokens = {};

function transform(x, y) {
  return [AFFINE.A * x + AFFINE.B * y + AFFINE.TX, AFFINE.C * x + AFFINE.D * y + AFFINE.TY];
}

async function getToken(device) {
  if (tokens[device]?.expires > Date.now() + 60000) return tokens[device];

  const res = await fetch('https://api.platform.twinzo.com/v3/authorization/authenticate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client: 'TVSMotor', login: device, password: 'Tvs@Hosur$2025' })
  });

  const data = await res.json();
  tokens[device] = { token: data.Token, client: data.Client, branch: data.Branch, expires: data.Expiration };
  return tokens[device];
}

async function send(device, x, y, heading, battery) {
  const t = await getToken(device);
  await fetch('https://api.platform.twinzo.com/v3/localization', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Client': t.client, 'Branch': t.branch, 'Token': t.token, 'Api-Key': 'sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S' },
    body: JSON.stringify([{ Timestamp: Date.now(), SectorId: 2, X: x, Y: y, Z: 0, Interval: 100, Battery: battery, IsMoving: true, LocalizationAreas: [], NoGoAreas: [] }])
  });
}

client.on('connect', () => client.subscribe({ 'ati_fm/#': { qos: 1 } }));

client.on('message', async (topic, msg) => {
  if (topic !== 'ati_fm/sherpa/status') return;
  const d = JSON.parse(msg.toString());
  if (d.mode !== 'fleet' || !d.pose || d.pose.length < 3) return;
  const device = DEVICES[d.sherpa_name];
  if (!device) return;
  const [x, y] = transform(d.pose[0], d.pose[1]);
  await send(device, x, y, d.pose[2], d.battery_status || 0);
});
```

---

## Critical

- Client ID = Username
- Process only `mode === 'fleet'`
- Payload is array `[{...}]`
- Headers: `Client`, `Branch`, `Token`, `Api-Key`
- D coefficient is negative (Y-flip)

---

**Factories of Future**
