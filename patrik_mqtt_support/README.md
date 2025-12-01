# Patrik MQTT Support Files

This folder contains all files created to help Patrik (Twinzo team) troubleshoot MQTT subscription issues with the ATI broker.

## Issue Summary

Patrik can connect to `tvs-dev.ifactory.ai:8883` but cannot subscribe to topics (`ati_fm/#`, `ati_fm/sherpa/status`). Getting **Error Code 135: Not Authorized (ACL)**.

## Files in This Folder

### Test Scripts (Both Working & Verified)
- **`test_patrik_connection.js`** - Node.js MQTT connection test
- **`test_patrik_connection.py`** - Python MQTT connection test

Both scripts successfully connect and receive live AMR data from the ATI broker.

### Documentation
- **`PATRIK_MQTT_TROUBLESHOOTING.md`** - Complete troubleshooting guide with:
  - Correct connection settings for Node.js, Python, and CLI tools
  - Common mistakes and solutions
  - Expected data format
  - Verification checklist

### Email Correspondence
- **`email_patrik_mqtt_fix.txt`** - Initial email with solution (Client ID must match username)
- **`email_followup_patrik.txt`** - Follow-up email addressing ACL Error 135 issue

## Quick Reference

### Correct Connection Settings
- Host: `tvs-dev.ifactory.ai:8883`
- Username: `tvs-audit-user`
- Password: `TVSAudit@2025`
- Client ID: `tvs-audit-user` (MUST match username!)
- Protocol: MQTT v5
- Certificate: CA or Self signed certificates (NOT "CA signed server certificate")
- SSL Secure: Disabled

### Topics to Subscribe
- `ati_fm/#` - All ATI Fleet Manager topics
- `fleet/trips/info` - Trip information

## Current Status

**Issue:** MQTTX client shows "Error Code 135: Not Authorized" when subscribing, despite correct credentials.

**Suspected Cause:** Certificate validation mismatch in MQTTX settings.

**Next Steps:**
1. Change MQTTX certificate setting from "CA signed server certificate" to "CA or Self signed certificates"
2. Have Patrik run test scripts to verify they work on his machine
3. If issue persists, schedule call to debug together

## Test Results

Both test scripts confirmed working on 2025-11-20:
- ✅ Successfully connected to ATI broker
- ✅ Successfully subscribed to both topics
- ✅ Receiving live data from all AMRs (tug-55, tug-133, tug-39, tug-140, tug-78, tug-24, tug-11, etc.)
- ✅ Data includes position, battery, trip info, timestamps

---

**Created:** 2025-11-20
**Last Updated:** 2025-11-22
**Contact:** Patrik (Twinzo Integration Team)
