# ATI MQTT Broker - Direct Access for Twinzo

This document provides credentials and configuration for Twinzo to directly subscribe to the ATI MQTT broker for real-time AMR position data.

## MQTT Broker Connection

```
Host: tvs-dev.ifactory.ai
Port: 8883 (MQTTS with TLS)
Protocol: MQTT v5
Username: tvs-audit-user
Password: TVSAudit@2025
Client ID: tvs-audit-user
```

**Important**: Client ID must match the username for this credential.

## Topics

```
ati_fm/sherpa/status    # Main AMR position data
ati_fm/#                # All topics (includes sherpa/status)
```

## Active AMRs - Old Plant (Sector 2)

| ATI Name | Twinzo Device Login | Status |
|----------|-------------------|--------|
| tug-55-tvsmotor-hosur-09 | tug-55-hosur-09 | Active |
| tug-39-tvsmotor-hosur-07 | tug-39-hosur-07 | Active |
| tug-133 | tug-133 | Active |

**Note**: Other AMRs (tug-140, tug-78, tug-24, tug-11) are not in Old Plant and should be ignored.

## Message Format

Messages on `ati_fm/sherpa/status` contain:

```json
{
  "sherpa_name": "tug-55-tvsmotor-hosur-09",
  "pose": [110.943, 62.396, 2.456],
  "battery_status": 78,
  "mode": "fleet",
  "timestamp": 1234567890
}
```

**Fields:**
- `sherpa_name`: AMR identifier (map to Twinzo device using table above)
- `pose`: Array of `[X_meters, Y_meters, heading_radians]`
- `battery_status`: Battery percentage (0-100)
- `mode`: "fleet" (moving/active) or "disconnected" (offline)
- Skip messages where `mode != "fleet"` or `pose` is missing

## Coordinate Transformation

ATI provides coordinates in **meters**. Transform to Twinzo units using simplified transformation (no rotation):

```
X_twinzo = 1479.084727 * X_ati + 63341.22
Y_twinzo = -1479.084727 * Y_ati + 197825.86
```

**Example:**
- ATI: `(44.62, 62.295)` meters → Twinzo: `(129,337, 105,686)` units
- ATI: `(116.97, 62.295)` meters → Twinzo: `(236,349, 105,686)` units

**Key features:**
- Y-axis flip (negative coefficient for Y)
- No rotation (horizontal tugger paths)
- Uniform scaling: 1479 units/meter (both axes)
- Accuracy: Perfect X alignment, Y error ~0.24%

**Updated**: 2025-11-11 (based on precise tug-55 movement path coordinates)

## Data Characteristics

- **Update Frequency**: 2-6 seconds per AMR (burst pattern)
- **Gaps**: 8-11 minute gaps between bursts
- **Coordinate Range**:
  - ATI: X = [-15m, 120m], Y = [0m, 80m]
  - Twinzo: X = [77k, 228k], Y = [86k, 168k]

## Authentication & Device Mapping

Each Twinzo device requires:
- **Login**: Device login from table above
- **Password**: `Tvs@Hosur$2025`
- **Sector**: 2 (Old Plant)
- **Branch**: `40557468-2d57-4a3d-9a5e-3eede177daf5`

## Testing Connection

Use any MQTT client (e.g., MQTTX, mosquitto_sub) to verify:

```bash
mosquitto_sub -h tvs-dev.ifactory.ai -p 8883 \
  -u tvs-audit-user -P "TVSAudit@2025" \
  -t "ati_fm/sherpa/status" \
  --capath /etc/ssl/certs \
  -i "test-client-001" \
  -V mqttv5
```

You should see JSON messages for active AMRs every few seconds.

---

**Contact**: Siddharth (dorddis@gmail.com)
**Date**: 2025-01-11
