/**
 * Quick Database Query Tool
 *
 * Simple Node.js script to query the ATI data database
 *
 * Usage:
 *     node scripts/monitoring/query_database.js
 */

import {
    getActiveDevices,
    getDeviceStats,
    getRecentMessages
} from '../../src/common/database.js';

console.log('========================================');
console.log('ATI DATA QUERY TOOL');
console.log('========================================\n');

// Show active devices
console.log('Active Devices (Last 24 hours):');
console.log('----------------------------------------');
const devices = getActiveDevices(24);

if (devices.length === 0) {
    console.log('No devices found. Make sure the bridge is running.');
} else {
    console.log(`Found ${devices.length} active device(s):\n`);

    for (const device of devices) {
        console.log(`Device: ${device.device_name}`);
        console.log(`  Messages: ${device.message_count}`);
        console.log(`  Last Seen: ${device.last_seen}`);
        console.log(`  Avg Battery: ${device.avg_battery ? device.avg_battery.toFixed(1) + '%' : 'N/A'}`);
        console.log('');

        // Show detailed stats for each device
        const stats = getDeviceStats(device.device_name, 24);
        console.log(`  Stats:`);
        console.log(`    Total Messages: ${stats.total_messages}`);
        console.log(`    Posted to API: ${stats.posted_count} (${(stats.posted_count/stats.total_messages*100).toFixed(1)}%)`);
        console.log(`    Errors: ${stats.error_count} (${(stats.error_count/stats.total_messages*100).toFixed(1)}%)`);
        console.log('');

        // Show last 5 messages
        console.log(`  Last 5 Messages:`);
        const recent = getRecentMessages(device.device_name, 5);
        for (const msg of recent) {
            const posted = msg.posted_to_api ? '✓' : '✗';
            const error = msg.error ? `[ERROR: ${msg.error.substring(0, 30)}]` : '';
            console.log(`    ${msg.timestamp} | ATI: (${msg.ati_x.toFixed(2)}, ${msg.ati_y.toFixed(2)})m | Twinzo: (${msg.twinzo_x.toFixed(0)}, ${msg.twinzo_y.toFixed(0)}) | Battery: ${msg.battery_status}% | ${posted} ${error}`);
        }
        console.log('\n' + '='.repeat(80) + '\n');
    }
}

console.log('Query complete.\n');
console.log('For more options, use: python -X utf8 scripts/monitoring/visualize_ati_data.py\n');
