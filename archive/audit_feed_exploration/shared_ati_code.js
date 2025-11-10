import mqtt from 'mqtt';
import 'dotenv/config';
// Configuration
const MQTT_HOST = process.env.MQTT_HOST || 'tvs-dev.ifactory.ai';
const MQTT_PORT = parseInt(process.env.MQTT_PORT || '8883', 10);
const USERNAME = process.env.AUDIT_USERNAME || 'tvs-audit-user';
const PASSWORD = process.env.AUDIT_PASSWORD || 'TVSAudit@2025';
const CLIENT_ID = process.env.AUDIT_USERNAME || 'tvs-audit-user';
const SUBSCRIPTION_TOPICS = {
'ati_fm/#': {qos: 1},
'fleet/trips/info': {qos: 1}
}
// Connection options
const connectionOptions = {
protocol: 'mqtts',
host: MQTT_HOST,
port: MQTT_PORT,
clientId: CLIENT_ID,
username: USERNAME,
password: PASSWORD,
protocolVersion: 5,
clean: false,
reconnectPeriod: 5000,
connectTimeout: 30000,
rejectUnauthorized: false,
properties: {
sessionExpiryInterval: 86400, // 24 hours
}
};
console.log('Connecting to audit feed...');
console.log('Host:', MQTT_HOST);
console.log('Port:', MQTT_PORT);
console.log('Username:', USERNAME);
console.log('Client ID:', CLIENT_ID);
console.log('Topic:', SUBSCRIPTION_TOPICS);
console.log('=====================================\n');
const client = mqtt.connect(connectionOptions);

client.on('connect', () => {
console.log('Connected to audit feed');
client.subscribe(SUBSCRIPTION_TOPICS, (err, granted) => {
if (err) {
console.error('Subscription error:', err);
return;
}
console.log('Subscribed to: ');
for (const subscribed of granted) {
console.log(` Topic: ${subscribed.topic}`);
}
console.log('\nWaiting for audit messages...\n');
});
});
client.on('message', (topic, messageBuffer) => {
try {
const payload = JSON.parse(messageBuffer.toString());
console.log('=====================================');
console.log('Raw Message Received');
console.log('=====================================');
console.log(`Received on topic: ${topic}`);
console.log('\n--- Original Message ---');
console.log(JSON.stringify(payload, null, 2));
console.log('=====================================\n');
// TVS can process the message here
// processMessage(payload.message);
} catch (error) {
console.error('Error processing message:', error.message);
console.error('Raw message:', messageBuffer.toString());
}
});
client.on('error', (error) => {
console.error('MQTT Error:', error.message);
});

client.on('reconnect', () => {
console.log('Reconnecting to audit feed...');
});
client.on('offline', () => {
console.log('Client offline');
});
client.on('close', () => {
console.log('Connection closed');
});
// Graceful shutdown
process.on('SIGINT', () => {
console.log('\n\nShutting down...');
client.end(false, () => {
console.log('Disconnected from audit feed');
process.exit(0);
});
});
process.on('SIGTERM', () => {
console.log('\n\nShutting down...');
client.end(false, () => {
console.log('Disconnected from audit feed');
process.exit(0);
});
});