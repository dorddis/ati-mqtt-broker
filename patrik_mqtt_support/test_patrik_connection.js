/**
 * Minimal ATI MQTT Connection Test
 *
 * This script tests the exact connection settings needed for the ATI broker.
 * Share this with Patrik to help troubleshoot subscription issues.
 */

import mqtt from 'mqtt';

// ATI Audit Feed credentials
const connectionOptions = {
    protocol: 'mqtts',
    host: 'tvs-dev.ifactory.ai',
    port: 8883,
    clientId: 'tvs-audit-user',  // CRITICAL: Must match username!
    username: 'tvs-audit-user',
    password: 'TVSAudit@2025',
    protocolVersion: 5,           // MQTT v5 required
    clean: true,                  // Clean session
    reconnectPeriod: 5000,
    connectTimeout: 30000,
    rejectUnauthorized: false,    // Skip TLS cert verification
    properties: {
        sessionExpiryInterval: 0  // No persistent session
    }
};

console.log('='.repeat(70));
console.log('ATI MQTT Connection Test');
console.log('='.repeat(70));
console.log(`Host: ${connectionOptions.host}:${connectionOptions.port}`);
console.log(`Username: ${connectionOptions.username}`);
console.log(`Client ID: ${connectionOptions.clientId}`);
console.log(`Protocol: MQTT v${connectionOptions.protocolVersion}`);
console.log('='.repeat(70));

const client = mqtt.connect(connectionOptions);

client.on('connect', (connack) => {
    console.log('\n✅ CONNECTED successfully!');
    console.log('Connection details:', JSON.stringify(connack, null, 2));

    // Subscribe to topics with QoS 1
    const topics = {
        'ati_fm/#': { qos: 1 },
        'fleet/trips/info': { qos: 1 }
    };

    console.log('\nAttempting to subscribe to topics...');
    client.subscribe(topics, (err, granted) => {
        if (err) {
            console.error('❌ SUBSCRIPTION ERROR:', err);
            process.exit(1);
        }

        console.log('\n✅ SUBSCRIBED successfully!');
        console.log('Granted subscriptions:');
        for (const sub of granted) {
            console.log(`  - Topic: ${sub.topic}, QoS: ${sub.qos}`);
        }

        console.log('\nListening for messages (press Ctrl+C to stop)...\n');
    });
});

client.on('message', (topic, payload) => {
    console.log(`\n${'='.repeat(70)}`);
    console.log(`📨 MESSAGE RECEIVED`);
    console.log(`Topic: ${topic}`);
    console.log(`Time: ${new Date().toISOString()}`);

    try {
        const data = JSON.parse(payload.toString());
        console.log('Payload:', JSON.stringify(data, null, 2));
    } catch (e) {
        console.log('Raw payload:', payload.toString());
    }
    console.log('='.repeat(70));
});

client.on('error', (error) => {
    console.error('❌ MQTT ERROR:', error.message);
});

client.on('disconnect', (packet) => {
    console.log('⚠️  DISCONNECTED:', packet);
});

client.on('reconnect', () => {
    console.log('🔄 Reconnecting...');
});

client.on('offline', () => {
    console.log('⚠️  Client offline');
});

client.on('close', () => {
    console.log('⚠️  Connection closed');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\nShutting down...');
    client.end(false, () => {
        console.log('✅ Disconnected cleanly');
        process.exit(0);
    });
});
