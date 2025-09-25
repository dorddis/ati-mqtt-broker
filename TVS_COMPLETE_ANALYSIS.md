# TVS MQTT Integration - Complete Analysis & Action Plan

**Date**: 2025-09-24
**Status**: ❌ **BLOCKED - Authorization Issues**

## Executive Summary

After exhaustive testing, we've confirmed that the `amr-001` account provided by TVS **cannot subscribe to any topics** on their MQTT broker. Every subscription attempt returns "Not authorized" and causes immediate disconnection.

## What We've Verified ✅

### 1. Network & Connection
- **DNS Resolution**: ✅ Works (`tvs-dev.ifactory.ai` → `146.190.9.161`)
- **TCP Port 8883**: ✅ Reachable
- **TLS Handshake**: ✅ Successful (TLSv1.3)
- **MQTT Authentication**: ✅ Accepts username/password

### 2. MQTT Protocol Support
- **MQTTv5**: ✅ Connects successfully
- **MQTTv3.1.1**: ✅ Connects successfully
- **MQTTv3.1**: ✅ Connects successfully

### 3. Client Configuration
- **Client ID**: ✅ `amr-001` accepted
- **Username/Password**: ✅ `amr-001` / `TVSamr001@2025` authenticated
- **Keep-alive**: ✅ Connection maintained

## What's Failing ❌

### Authorization Failures on ALL Topics

We systematically tested 46+ topic variations, including:

#### Primary Targets
- ❌ `ati_fm/sherpa/status` - **"Not authorized"**
- ❌ `ati/sherpa/status` - **"Not authorized"**
- ❌ `robotspace/sherpa/status` - **"Not authorized"**

#### Wildcard Attempts
- ❌ `#` - **"Not authorized"**
- ❌ `+` - **"Not authorized"**
- ❌ `ati_fm/#` - **"Not authorized"**
- ❌ `robotspace/#` - **"Not authorized"**

#### Device-Specific Topics
- ❌ `amr/f4:7b:09:0e:04:1b/status` (Tug 133 MAC)
- ❌ `amr/10:3d:1c:66:67:55/status` (Tug 39 MAC)
- ❌ `tug/133/status`
- ❌ `amr/tug133/status`

#### Client-Based Topics
- ❌ `amr-001/status`
- ❌ `amr-001/#`
- ❌ `clients/amr-001/#`

**EVERY SINGLE SUBSCRIPTION RETURNS: "Not authorized"**

## Root Cause Analysis 🔍

### The Problem
The MQTT broker is configured with **Access Control Lists (ACLs)** that restrict what topics each user can subscribe to. The `amr-001` account has:
- ✅ **Connection permission** (can authenticate)
- ❌ **No subscription permissions** (cannot read any topics)
- ❓ **Unknown publish permissions** (haven't tested)

### Why This Happens
1. **Broker-side ACL Configuration**: The broker has strict ACL rules
2. **Account Limitations**: The `amr-001` account is not granted read permissions
3. **Immediate Disconnection**: The broker disconnects clients upon authorization failure

## Data Flow Understanding 📊

Based on your information:
```
ATI System → Publishes to → MQTT Broker (topic: ati_fm/sherpa/status)
                                ↓
                          RobotSpace System
                                ↓
                    Subscribes & Processes Data
                                ↓
                      Publishes to Different Topic
                                ↓
                          MQTT Broker (topic: unknown)
```

## What We Need From TVS 🎯

### Option 1: Fix Current Credentials (Preferred)
Ask TVS to:
1. **Grant subscription permissions** to `amr-001` for topic `ati_fm/sherpa/status`
2. Or grant permission to subscribe to `#` (all topics) for testing
3. Confirm the exact topic where data is being published

Example ACL configuration they need to add:
```
user amr-001
topic read ati_fm/sherpa/status
topic read ati_fm/sherpa/#
```

### Option 2: Get Different Credentials
Request:
1. **ATI System Credentials** - Direct access to source data
2. **RobotSpace Credentials** - Access to processed data
3. **Admin/Test Account** - Unrestricted access for development

### Option 3: Get Specific Information
Ask TVS to provide:
1. **Exact topic names** where AMR data is published
2. **ACL configuration** for the amr-001 account
3. **Alternative ports/brokers** if data is published elsewhere
4. **Sample data format** of what's being published

## Communication Template for TVS 📧

```
Subject: MQTT Authorization Issue - Need ACL Update

Hi TVS Team,

We've successfully connected to your MQTT broker (tvs-dev.ifactory.ai:8883) using the provided credentials (amr-001), but we're experiencing authorization issues.

Current Status:
✅ Connection successful
✅ Authentication working
❌ Cannot subscribe to any topics - all return "Not authorized"

Specifically, we cannot subscribe to:
- ati_fm/sherpa/status (mentioned as the primary topic)
- Any wildcard patterns
- Any device-specific topics

This appears to be an ACL (Access Control List) configuration issue on the broker.

We need ONE of the following:
1. Update ACL for amr-001 to allow reading from ati_fm/sherpa/status
2. Provide credentials with proper read permissions
3. Share the exact topic names and required permissions

Additionally, please confirm:
- Is data currently being published? (AMRs operational?)
- What is the exact topic structure?
- Are there multiple brokers/ports we should try?

This is blocking our integration. Please advise on the quickest resolution.

Best regards,
[Your Name]
```

## Technical Details for Reference 🔧

### What We Know Works
```python
# Connection works
client.connect("tvs-dev.ifactory.ai", 8883)  # ✅
client.username_pw_set("amr-001", "TVSamr001@2025")  # ✅

# But subscription fails
client.subscribe("ati_fm/sherpa/status")  # ❌ Not authorized
client.subscribe("#")  # ❌ Not authorized
```

### MQTT ACL Basics
ACLs control three permissions:
1. **Connect** - Can the user connect? (✅ We have this)
2. **Subscribe/Read** - Can the user read topics? (❌ We don't have this)
3. **Publish/Write** - Can the user publish to topics? (? Unknown)

### Common Broker ACL Patterns
```
# Mosquitto ACL example
user amr-001
topic read ati_fm/sherpa/status
topic read ati_fm/sherpa/#
topic write amr-001/status

# Or pattern-based
pattern read ati_fm/%u/status  # %u = username
```

## Next Steps 🚀

1. **Immediate**: Send the communication to TVS with our findings
2. **Request**: Specific ACL configuration or new credentials
3. **Alternative**: Ask if there's a different broker/port/protocol
4. **Backup**: Consider requesting direct database/API access instead of MQTT

## Conclusion

**We have done everything possible on our end.** The issue is 100% on the broker configuration side. We need TVS to either:
- Fix the ACL permissions for `amr-001`
- Provide different credentials with proper permissions
- Give us the exact topic names if they're different than expected

Without this, we cannot proceed with the MQTT integration.