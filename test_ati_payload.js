/**
 * Quick test to see the full raw ATI payload
 */

import mqtt from 'mqtt';
import 'dotenv/config';

const ATI_HOST = process.env.AUDIT_MQTT_HOST || 'tvs-dev.ifactory.ai';
const ATI_PORT = parseInt(process.env.AUDIT_MQTT_PORT || '8883', 10);
const ATI_USERNAME = process.env.AUDIT_USERNAME || 'tvs-audit-user';
const ATI_PASSWORD = process.env.AUDIT_PASSWORD || 'TVSAudit@2025';
const ATI_CLIENT_ID = 'test-payload-inspector';

const connectionOptions = {
    protocol: 'mqtts',
    host: ATI_HOST,
    port: ATI_PORT,
    clientId: ATI_CLIENT_ID,
    username: ATI_USERNAME,
    password: ATI_PASSWORD,
    protocolVersion: 5,
    clean: true,
    reconnectPeriod: 5000,
    connectTimeout: 30000,
    rejectUnauthorized: false
};

console.log('Connecting to ATI audit feed...');
const client = mqtt.connect(connectionOptions);

let messageCount = 0;

client.on('connect', () => {
    console.log('Connected! Subscribing to ati_fm/sherpa/status...\n');
    client.subscribe('ati_fm/sherpa/status', { qos: 1 }, (err) => {
        if (err) {
            console.error('Subscribe error:', err);
        } else {
            console.log('Subscribed. Waiting for first message...\n');
        }
    });
});

client.on('message', (topic, messageBuffer) => {
    messageCount++;

    if (messageCount === 1) {
        console.log('='.repeat(80));
        console.log('FIRST MESSAGE - FULL RAW PAYLOAD');
        console.log('='.repeat(80));
        console.log('Topic:', topic);
        console.log('\nRaw JSON:');
        console.log(messageBuffer.toString());

        console.log('\nParsed object:');
        const payload = JSON.parse(messageBuffer.toString());
        console.log(JSON.stringify(payload, null, 2));

        console.log('\nAll keys in payload:');
        console.log(Object.keys(payload));

        console.log('\n' + '='.repeat(80));
        console.log('Disconnecting...');
        client.end();
        process.exit(0);
    }
});

client.on('error', (error) => {
    console.error('MQTT Error:', error);
    process.exit(1);
});

// Timeout after 30 seconds
setTimeout(() => {
    console.log('Timeout - no messages received in 30 seconds');
    client.end();
    process.exit(1);
}, 30000);
