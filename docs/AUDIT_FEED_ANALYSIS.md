# ATI Audit Feed Analysis

## Active AMRs Discovered (2025-11-10)

### Active & Moving AMRs

| Sherpa Name | Fleet Name | Battery | Status | Trip ID |
|-------------|------------|---------|--------|---------|
| tug-55-tvsmotor-hosur-09 | xltest | 95% | fleet | 178573 |
| tug-39-tvsmotor-hosur-07 | xltest | 93% | fleet | 178574 |
| tug-133 | xltest | 59% | fleet | 178580 |
| tug-140 | TVS-plant-2 | 17% | fleet | 178591 |
| tug-78 | TVS-plant-2 | 82% | fleet | 178376 |
| tug-24-tvsmotor-hosur-05 | TVS-Hosur-3wheeler-Line | 71% | fleet | 178565 |
| tug-11 | Tvs-plant3 | 44% | fleet | 178579 |

### Disconnected AMRs

| Sherpa Name | Fleet Name | Last Status | Error |
|-------------|------------|-------------|-------|
| tug-134 | (unknown) | disconnected | Mule app down |
| tug-20-tvsmotor-hosur-02 | Tvs_store | disconnected | control_module died |
| lite-26 | (unknown) | disconnected | Mule app down |
| tug-23-tvsmotor-hosur-03 | bmw_line | disconnected | stale_heartbeat |
| tug-87-tvsmotor-hosur-04 | (unknown) | disconnected | Mule app down |

## Fleet Mapping Strategy

### Proposed Twinzo Plant Assignment

**HiTech Plant (Sector 1)** - Modern lines, higher production
- Fleet: `xltest`
  - tug-55-tvsmotor-hosur-09
  - tug-39-tvsmotor-hosur-07
  - tug-133
- Fleet: `TVS-plant-2`
  - tug-140
  - tug-78

**Old Plant (Sector 2)** - Traditional lines, established processes
- Fleet: `TVS-Hosur-3wheeler-Line`
  - tug-24-tvsmotor-hosur-05
- Fleet: `Tvs-plant3`
  - tug-11
- Fleet: `Tvs_store`
  - tug-20-tvsmotor-hosur-02
- Fleet: `bmw_line`
  - tug-23-tvsmotor-hosur-03

**Unknown/Unassigned** (Skip for now)
- tug-134, lite-26, tug-87-tvsmotor-hosur-04 (disconnected with no fleet info)

## Data Structure

### Position Data (pose array)
```
[x, y, heading]
```
- x, y: Coordinates in meters
- heading: Rotation in radians

### Topics Available
1. `ati_fm/sherpa/status` - Real-time AMR positions (2-3 sec updates)
2. `fleet/trips/info` - Trip details and routes
3. `ati_fm/trips/legs` - Individual leg progress

## Implementation Plan

1. Create device naming convention: `{sherpa_name}` (use exact ATI names)
2. Map fleets to Twinzo sectors based on production line type
3. Use audit feed credentials for all data collection
4. Single bridge with intelligent routing based on fleet_name
