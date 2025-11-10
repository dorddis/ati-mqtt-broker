/**
 * Analyze ATI coordinate ranges to determine proper scaling
 */
import mqtt from 'mqtt';
import 'dotenv/config';

const ATI_HOST = 'tvs-dev.ifactory.ai';
const ATI_PORT = 8883;
const ATI_USERNAME = 'tvs-audit-user';
const ATI_PASSWORD = 'TVSAudit@2025';
const ATI_CLIENT_ID = `${ATI_USERNAME}-analyzer`;

const coords = {
    minX: Infinity,
    maxX: -Infinity,
    minY: Infinity,
    maxY: -Infinity,
    samples: []
};

const connectionOptions = {
    protocol: 'mqtts',
    host: ATI_HOST,
    port: ATI_PORT,
    clientId: ATI_CLIENT_ID,
    username: ATI_USERNAME,
    password: ATI_PASSWORD,
    protocolVersion: 5,
    clean: false,
    reconnectPeriod: 5000,
    connectTimeout: 30000,
    rejectUnauthorized: false,
    properties: {
        sessionExpiryInterval: 86400
    }
};

console.log('Connecting to ATI to analyze coordinate ranges...\n');

const client = mqtt.connect(connectionOptions);

client.on('connect', () => {
    console.log('Connected! Subscribing to sherpa status...');
    client.subscribe('ati_fm/sherpa/status', {qos: 1});
});

client.on('message', (topic, messageBuffer) => {
    try {
        const payload = JSON.parse(messageBuffer.toString());

        if (payload.mode === 'fleet' && payload.pose && payload.pose.length >= 2) {
            const [x, y] = payload.pose;
            const name = payload.sherpa_name;

            coords.minX = Math.min(coords.minX, x);
            coords.maxX = Math.max(coords.maxX, x);
            coords.minY = Math.min(coords.minY, y);
            coords.maxY = Math.max(coords.maxY, y);

            coords.samples.push({name, x, y});

            if (coords.samples.length % 10 === 0) {
                console.log(`\n=== Coordinate Analysis (${coords.samples.length} samples) ===`);
                console.log(`X Range: ${coords.minX.toFixed(2)} to ${coords.maxX.toFixed(2)} (span: ${(coords.maxX - coords.minX).toFixed(2)}m)`);
                console.log(`Y Range: ${coords.minY.toFixed(2)} to ${coords.maxY.toFixed(2)} (span: ${(coords.maxY - coords.minY).toFixed(2)}m)`);
                console.log(`\nRecent samples:`);
                coords.samples.slice(-5).forEach(s => {
                    console.log(`  ${s.name}: (${s.x.toFixed(2)}, ${s.y.toFixed(2)})`);
                });
            }

            if (coords.samples.length >= 50) {
                console.log('\n\n=== FINAL ANALYSIS ===');
                console.log(`X Range: ${coords.minX.toFixed(2)} to ${coords.maxX.toFixed(2)}`);
                console.log(`Y Range: ${coords.minY.toFixed(2)} to ${coords.maxY.toFixed(2)}`);
                console.log(`\nCenter point: (${((coords.minX + coords.maxX) / 2).toFixed(2)}, ${((coords.minY + coords.maxY) / 2).toFixed(2)})`);
                console.log(`\nRecommended scaling factor: 1000 (to map to ~100k coordinate system)`);
                console.log(`\nExample transforms:`);
                console.log(`  If Old Plant map center is at (100000, 100000):`);
                console.log(`    X_twinzo = X_ati * 1000 + ${(100000 - (coords.minX + coords.maxX) / 2 * 1000).toFixed(0)}`);
                console.log(`    Y_twinzo = Y_ati * 1000 + ${(100000 - (coords.minY + coords.maxY) / 2 * 1000).toFixed(0)}`);

                client.end();
                process.exit(0);
            }
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
});

setTimeout(() => {
    console.log('\n\nTimeout - stopping analysis');
    client.end();
    process.exit(0);
}, 60000);
