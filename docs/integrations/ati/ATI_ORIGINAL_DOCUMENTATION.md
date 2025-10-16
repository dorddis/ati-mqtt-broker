# ATI Original MQTT Integration Documentation

**Source**: ATI Motors Inc.
**Date**: 13-Jun-25
**Document**: MQTT-Based Integration to get data from ATI Fleet Manager

---

## Overview

This document outlines the MQTT-based integration model for interfacing with ATI Fleet Manager. It specifies the topic structure, payload schema, and expected message formats for monitoring and interacting with Trips, Trip Legs, Sherpa (AMR) statuses, and System Alerts.

## 1. MQTT Topics

### 1.1 Trip Information
**Topic**: `fleet/trips/info`

**Payload Schema (JSON)**:
```json
{
  "id": 1234,
  "sherpa_name": "val-sherpa-01",
  "fleet_name": "XXXXX-Inbound",
  "booking_time": "2025-06-01T10:05:00Z",
  "start_time": "2025-06-01T10:07:00Z",
  "end_time": "2025-06-01T10:15:00Z",
  "route": ["StationA", "StationB", "StationC"],
  "status": "Succeeded",
  "route_lengths": 453.6,
  "scheduled": true,
  "trip_metadata": {"priority": "High", "cargo_type": "Parts"},
  "booked_by": "user_admin"
}
```

### 1.2 Trip Legs Information
**Topic**: `ati_fm/trips/legs`

**Payload Schema (JSON)**:
```json
{
  "trip_id": 1234,
  "legs": [
    {
      "leg_id": 5678,
      "from_station": "StationB",
      "to_station": "StationC",
      "cte": 0.38,
      "route_length": 303.4,
      "time_elapsed_obstacle_stoppages": 6.8,
      "time_elapsed_visa_stoppages": 0.0,
      "time_elapsed_other_stoppages": 2.1
    }
  ]
}
```

### 1.3 Sherpa Status Update
**Topic**: `ati_fm/sherpa/status`

**Payload Schema (JSON)**:
```json
{
  "sherpa_name": "val-sherpa-01",
  "mode": "Fleet",
  "error": "",
  "disabled": false,
  "disabled_reason": "",
  "pose": [10.5, 22.4, 0.0, 0.0, 0.0, 0.0],
  "battery_status": 82.5,
  "trip_id": 1234,
  "trip_leg_id": 5678
}
```

### 1.4 System Alerts
**Topic**: `ati_fm/alerts`

**Payload Schema**: [Document appears cut off]

## Client Role Summary

| Use Case | Topic | Client Role |
|----------|-------|-------------|
| Real-time Sherpa Monitoring | `ati_fm/sherpa/status` | Dashboard / Monitor |
| Trip Summary View | `ati_fm/trips/info` | Analytics / Dashboard |
| Trip Analysis | `ati_fm/trips/legs` | Reporting / Audit Tool |
| Real-Time Alert Handling | `ati_fm/alerts` | Operations / Support |

---

**Copyright © ATI Motors Inc. (Intended recipients only)**