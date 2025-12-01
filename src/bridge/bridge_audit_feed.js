/**
 * ATI Audit Feed Bridge - Old Plant AMRs to Twinzo
 *
 * This bridge uses the ATI audit feed credentials to monitor active AMRs
 * and stream their positions to Twinzo Old Plant (Sector 2).
 *
 * Features:
 * - Monitors ati_fm/sherpa/status for all AMRs
 * - Maps ATI sherpa_name to Twinzo device logins
 * - Streams to Old Plant (Sector 2) only
 * - Currently handling 3 AMRs: tug-55, tug-39, tug-133
 * - Uses affine transformation for coordinate mapping
 * - Logs all data to SQLite database (logs/ati_data.db)
 *
 * IMPORTANT - ATI Timestamp Format:
 * - ATI includes a "timestamp" field in ISO 8601 format with 'Z' suffix
 * - Example: "timestamp": "2025-12-01T13:21:52Z"
 * - WARNING: Despite the 'Z' (UTC indicator), timestamps are actually in IST (UTC+5:30)
 * - This is a data formatting issue on ATI's side
 * - Bridge uses Date.now() for Twinzo API (real-time when received)
 *
 * Usage:
 *     node src/bridge/bridge_audit_feed.js
 */

import mqtt from 'mqtt';
import 'dotenv/config';
import fetch from 'node-fetch';
import { logATIMessage } from '../common/database.js';

// ATI Audit Feed Configuration
const ATI_HOST = process.env.AUDIT_MQTT_HOST || 'tvs-dev.ifactory.ai';
const ATI_PORT = parseInt(process.env.AUDIT_MQTT_PORT || '8883', 10);
const ATI_USERNAME = process.env.AUDIT_USERNAME || 'tvs-audit-user';
const ATI_PASSWORD = process.env.AUDIT_PASSWORD || 'TVSAudit@2025';
// Try exact match first - audit credentials require client ID = username
const ATI_CLIENT_ID = ATI_USERNAME;
// Subscribe to ATI topics (same format as Pavan's working code)
const SUBSCRIPTION_TOPICS = {
    'ati_fm/#': {qos: 1},
    'fleet/trips/info': {qos: 1}
};

// Twinzo API Configuration
const TWINZO_CLIENT = process.env.TWINZO_CLIENT || 'TVSMotor';
const TWINZO_PASSWORD = process.env.TWINZO_PASSWORD;
const TWINZO_API_KEY = process.env.TWINZO_API_KEY;
const TWINZO_AUTH_URL = 'https://api.platform.twinzo.com/v3/authorization/authenticate';
const TWINZO_LOC_URL = 'https://api.platform.twinzo.com/v3/localization';

// Plant Configuration
const OLD_PLANT_SECTOR = 2;
const OLD_PLANT_BRANCH = '40557468-2d57-4a3d-9a5e-3eede177daf5';
const HITECH_PLANT_SECTOR = 1;
const HITECH_PLANT_BRANCH = 'dcac4881-05ab-4f29-b0df-79c40df9c9c2';

// Device Mapping: ATI sherpa_name -> Twinzo login (ONLY OLD PLANT)
const DEVICE_MAP = {
    'tug-55-tvsmotor-hosur-09': 'tug-55-hosur-09',
    'tug-39-tvsmotor-hosur-07': 'tug-39-hosur-07',
    'tug-133': 'tug-133'
    // Disabled: tug-140, tug-78, tug-24, tug-11 (not in Old Plant)
};

// Device-to-Sector Mapping: Which sector each device belongs to
const DEVICE_SECTOR_MAP = {
    'tug-55-hosur-09': OLD_PLANT_SECTOR,
    'tug-39-hosur-07': OLD_PLANT_SECTOR,
    'tug-133': OLD_PLANT_SECTOR
};

// Coordinate transformation: Scale ATI meters (0-120 range) to Twinzo units (100k range)
// ATI coordinates are in meters, Twinzo uses ~100k scale
// Transform: Scale by 1000, then offset to place in Old Plant map area
const AFFINE_A = parseFloat(process.env.AFFINE_A || '1000.0');  // X scale
const AFFINE_B = parseFloat(process.env.AFFINE_B || '0.0');     // X rotation
const AFFINE_C = parseFloat(process.env.AFFINE_C || '0.0');     // Y rotation
const AFFINE_D = parseFloat(process.env.AFFINE_D || '1000.0');  // Y scale
const AFFINE_TX = parseFloat(process.env.AFFINE_TX || '100000.0');  // X offset (center at 100k)
const AFFINE_TY = parseFloat(process.env.AFFINE_TY || '100000.0');  // Y offset (center at 100k)

// OAuth token cache
const oauthCache = {};

// Statistics
const stats = {
    messagesReceived: 0,
    messagesTotal: 0,  // All messages including non-sherpa
    messagesSent: 0,
    errors: 0,
    lastUpdate: {}
};

function transformXY(x, y) {
    return [
        AFFINE_A * x + AFFINE_B * y + AFFINE_TX,
        AFFINE_C * x + AFFINE_D * y + AFFINE_TY
    ];
}

async function authenticateDevice(deviceLogin) {
    try {
        const response = await fetch(TWINZO_AUTH_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                client: TWINZO_CLIENT,
                login: deviceLogin,
                password: TWINZO_PASSWORD
            }),
            timeout: 10000
        });

        if (response.ok) {
            const data = await response.json();
            oauthCache[deviceLogin] = {
                token: data.Token,
                client: data.Client,
                branch: data.Branch,
                expires: data.Expiration
            };
            console.log(`OK OAuth successful for ${deviceLogin}`);
            return oauthCache[deviceLogin];
        } else {
            console.log(`FAIL OAuth failed for ${deviceLogin}: ${response.status}`);
            return null;
        }
    } catch (error) {
        console.log(`FAIL OAuth error for ${deviceLogin}: ${error.message}`);
        return null;
    }
}

async function getDeviceCredentials(deviceLogin) {
    const now = Date.now();

    // Check if we have valid token
    if (oauthCache[deviceLogin]) {
        const creds = oauthCache[deviceLogin];
        if (creds.expires > now + 60000) {
            return creds;
        }
    }

    // Get fresh token
    return await authenticateDevice(deviceLogin);
}

async function sendToTwinzo(deviceLogin, x, y, heading, battery = 0) {
    try {
        const creds = await getDeviceCredentials(deviceLogin);
        if (!creds) {
            return { success: false, error: 'Authentication failed' };
        }

        // Validate coordinates
        if (!isFinite(x) || !isFinite(y)) {
            console.log(`FAIL Invalid coordinates for ${deviceLogin}: X=${x}, Y=${y}`);
            return { success: false, error: `Invalid coordinates: X=${x}, Y=${y}` };
        }

        // Get device-specific sector (default to Old Plant if not configured)
        const sectorId = DEVICE_SECTOR_MAP[deviceLogin] || OLD_PLANT_SECTOR;

        // Prepare localization data (MUST be an array, match Python bridge format)
        const data = [{
            Timestamp: Date.now(),
            SectorId: sectorId,
            X: x,
            Y: y,
            Z: 0,
            Interval: 100,
            Battery: battery,
            IsMoving: true,
            LocalizationAreas: [],
            NoGoAreas: []
        }];

        // Send to Twinzo (use exact header format from Python bridge)
        const response = await fetch(TWINZO_LOC_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Client': creds.client,
                'Branch': creds.branch,
                'Token': creds.token,
                'Api-Key': TWINZO_API_KEY
            },
            body: JSON.stringify(data),
            timeout: 5000
        });

        if (response.ok || response.status === 204) {
            stats.messagesSent++;
            return { success: true, response: `HTTP ${response.status}` };
        } else {
            const errorText = await response.text();
            console.log(`FAIL Twinzo API error for ${deviceLogin}: ${response.status}`);
            console.log(`  Sector: ${sectorId}, X: ${x.toFixed(2)}, Y: ${y.toFixed(2)}, Battery: ${battery}`);
            console.log(`  Response: ${errorText.substring(0, 200)}`);
            stats.errors++;
            return { success: false, error: `HTTP ${response.status}: ${errorText.substring(0, 200)}` };
        }
    } catch (error) {
        console.log(`FAIL Error sending to Twinzo for ${deviceLogin}: ${error.message}`);
        stats.errors++;
        return { success: false, error: error.message };
    }
}

// Connection options
const connectionOptions = {
    protocol: 'mqtts',
    host: ATI_HOST,
    port: ATI_PORT,
    clientId: ATI_CLIENT_ID,
    username: ATI_USERNAME,
    password: ATI_PASSWORD,
    protocolVersion: 5,
    clean: true,  // Use clean session to avoid conflicts
    reconnectPeriod: 5000,
    connectTimeout: 30000,
    rejectUnauthorized: false,
    properties: {
        sessionExpiryInterval: 0  // No persistent session
    }
};

console.log('======================================================================');
console.log('ATI Audit Feed Bridge - Old Plant (Sector 2)');
console.log('======================================================================');
console.log(`ATI Broker: ${ATI_HOST}:${ATI_PORT}`);
console.log(`ATI Username: ${ATI_USERNAME}`);
console.log(`Client ID: ${ATI_CLIENT_ID}`);
console.log(`Topics: ${Object.keys(SUBSCRIPTION_TOPICS).join(', ')}`);
console.log(`Old Plant - Sector: ${OLD_PLANT_SECTOR}, Branch: ${OLD_PLANT_BRANCH}`);
console.log(`HiTech Plant - Sector: ${HITECH_PLANT_SECTOR}, Branch: ${HITECH_PLANT_BRANCH}`);
console.log(`Coordinate Transform: A=${AFFINE_A}, B=${AFFINE_B}, C=${AFFINE_C}, D=${AFFINE_D}, TX=${AFFINE_TX}, TY=${AFFINE_TY}`);
console.log(`Active AMRs: ${Object.keys(DEVICE_MAP).length}`);
for (const [atiName, twinzoLogin] of Object.entries(DEVICE_MAP)) {
    const sector = DEVICE_SECTOR_MAP[twinzoLogin] || OLD_PLANT_SECTOR;
    const plantName = sector === HITECH_PLANT_SECTOR ? 'HiTech' : 'Old Plant';
    console.log(`  ${atiName} -> ${twinzoLogin} (${plantName}, Sector ${sector})`);
}
console.log('======================================================================\\n');

const client = mqtt.connect(connectionOptions);

client.on('connect', () => {
    console.log('OK Connected to ATI audit feed');
    client.subscribe(SUBSCRIPTION_TOPICS, (err, granted) => {
        if (err) {
            console.error('FAIL Subscription error:', err);
            return;
        }
        console.log('OK Subscribed to:');
        for (const sub of granted) {
            console.log(`  ${sub.topic}`);
        }
        console.log('OK Bridge ready - streaming 3 AMRs to Old Plant (Sector 2)\\n');
    });
});

client.on('message', async (topic, messageBuffer) => {
    try {
        stats.messagesTotal++;

        // Log every 20 messages to show activity
        if (stats.messagesTotal % 20 === 0) {
            console.log(`DEBUG: Total=${stats.messagesTotal}, Processed=${stats.messagesReceived}, Sent=${stats.messagesSent}, topic=${topic}`);
        }

        // Only process sherpa status messages
        if (topic !== 'ati_fm/sherpa/status') {
            return;
        }

        stats.messagesReceived++;

        const payload = JSON.parse(messageBuffer.toString());
        const sherpaName = payload.sherpa_name;
        const mode = payload.mode;
        const pose = payload.pose;
        const battery = payload.battery_status || 0;

        // Skip if not in our device map
        if (!DEVICE_MAP[sherpaName]) {
            return;
        }

        // Skip if disconnected or no position data
        if (mode !== 'fleet' || !pose || pose.length < 3) {
            return;
        }

        // Get Twinzo device login
        const deviceLogin = DEVICE_MAP[sherpaName];

        // Extract position
        const [xRaw, yRaw, heading] = pose;

        // Apply coordinate transformation
        const [x, y] = transformXY(xRaw, yRaw);

        // Log detailed data for every message
        console.log(`\n${'='.repeat(70)}`);
        console.log(`AMR: ${sherpaName} -> ${deviceLogin}`);
        console.log(`Time: ${new Date().toISOString()}`);
        console.log(`ATI Raw Coordinates: X=${xRaw.toFixed(2)}m, Y=${yRaw.toFixed(2)}m, Heading=${heading.toFixed(3)}rad`);
        console.log(`Twinzo Transformed: X=${x.toFixed(0)}, Y=${y.toFixed(0)}`);
        console.log(`Battery: ${battery}%, Mode: ${mode}`);
        console.log(`${'='.repeat(70)}`);

        // Send to Twinzo
        const result = await sendToTwinzo(deviceLogin, x, y, heading, battery);

        // Log to database
        try {
            logATIMessage({
                device_name: sherpaName,
                ati_x: xRaw,
                ati_y: yRaw,
                ati_heading: heading,
                twinzo_x: x,
                twinzo_y: y,
                twinzo_heading: heading,
                battery_status: battery,
                mode: mode,
                posted_to_api: result.success,
                api_response: result.response || null,
                error: result.error || null
            });
        } catch (dbError) {
            console.log(`WARN Database logging failed: ${dbError.message}`);
        }

        // Update stats
        stats.lastUpdate[sherpaName] = Date.now();

        // Log periodically
        if (stats.messagesReceived % 50 === 0) {
            const now = Date.now();
            const activeCount = Object.values(stats.lastUpdate).filter(t => now - t < 30000).length;
            console.log(`\\nStats: Received=${stats.messagesReceived}, ` +
                       `Sent=${stats.messagesSent}, Active=${activeCount}, ` +
                       `Errors=${stats.errors}`);
            console.log(`Recent updates: ${Object.keys(stats.lastUpdate).join(', ')}\\n`);
        }

    } catch (error) {
        console.error('FAIL Error processing message:', error.message);
        stats.errors++;
    }
});

client.on('error', (error) => {
    console.error('FAIL MQTT Error:', error.message);
});

client.on('reconnect', () => {
    console.log('Reconnecting to ATI audit feed...');
});

client.on('offline', () => {
    console.log('Client offline');
});

client.on('close', () => {
    console.log('Connection closed');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\\n\\nShutting down bridge...');
    console.log(`Final stats: Received=${stats.messagesReceived}, ` +
               `Sent=${stats.messagesSent}, Errors=${stats.errors}`);
    client.end(false, () => {
        console.log('OK Bridge stopped');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    console.log('\\n\\nShutting down bridge...');
    console.log(`Final stats: Received=${stats.messagesReceived}, ` +
               `Sent=${stats.messagesSent}, Errors=${stats.errors}`);
    client.end(false, () => {
        console.log('OK Bridge stopped');
        process.exit(0);
    });
});
