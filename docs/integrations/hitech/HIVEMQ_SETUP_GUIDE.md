# HiveMQ Cloud Serverless Setup Guide

## 🎯 Goal
Set up HiveMQ Cloud MQTT broker and test it from external network (phone) to simulate Hi-tech AMR integration.

---

## 📋 Step 1: Create HiveMQ Cloud Account (YOU DO THIS)

### Actions:
1. **Go to**: https://console.hivemq.cloud/
2. **Sign up** using:
   - GitHub, Google, LinkedIn, OR
   - Email address
3. **Verify email** (check inbox/spam)
4. **Complete profile** (name, company info)

✅ **Done when**: You're logged into HiveMQ Cloud console

---

## 📋 Step 2: Create Serverless Cluster (YOU DO THIS)

### Actions:
1. On dashboard, find **"HiveMQ Cloud Serverless"** card
2. Click **"Create Serverless Cluster"**
3. Wait ~10 seconds for cluster to launch
4. Click **"Manage Cluster"** when it appears

✅ **Done when**: You see the cluster Overview tab with connection details

---

## 📋 Step 3: Get Connection Details (YOU DO THIS)

### Actions:
1. In **Overview** tab, copy these details:
   - **Host/URL**: (e.g., `abc123def456.s1.eu.hivemq.cloud`)
   - **Port**: (typically `8883` for MQTT with TLS)
   - **WebSocket Port**: (typically `8884`)
   - **Cluster ID**: (for reference)

📝 **Paste these details here when done**

---

## 📋 Step 4: Create MQTT Credentials (YOU DO THIS)

### Actions:
1. Go to **"Access Management"** tab
2. Under **Credentials** section, click **"Edit"**
3. Click **"Add Credentials"**
4. Fill in:
   - **Username**: `hitech-test` (or whatever you like)
   - **Password**: `HitechAMR@2025` (or whatever you like)
   - **Permission**: Select "All topics" or "Publish & Subscribe"
5. Click **"Save"**

📝 **Paste username and password here when done**

---

## 📋 Step 5: Test Connection from Local Machine (I'LL HELP)

### Once you provide the details above, I will:
1. ✅ Create Python MQTT test script
2. ✅ Test connection from your PC
3. ✅ Subscribe to test topic
4. ✅ Publish test messages
5. ✅ Verify data flow

---

## 📋 Step 6: Test from Phone/External Network (YOU DO THIS)

### Actions:
1. **Install MQTT app** on phone:
   - Android: **"MQTT Dash"** or **"IoT MQTT Panel"**
   - iOS: **"MQTTool"** or **"MQTT Explorer"**
2. **Turn OFF WiFi** on phone (use cellular data only)
3. **Configure connection** in app:
   - Host: (the URL from Step 3)
   - Port: 8883
   - Username: (from Step 4)
   - Password: (from Step 4)
   - Enable SSL/TLS: YES
4. **Connect** and test publish/subscribe

✅ **Done when**: You can send messages from phone and see them on PC

---

## 📋 Step 7: Simulate Hi-tech AMR Data (I'LL HELP)

### I will create:
1. ✅ Python script to publish AMR position data in Hi-tech format
2. ✅ Bridge script to consume from HiveMQ and forward to Twinzo
3. ✅ End-to-end test from phone → HiveMQ → Twinzo → Platform

---

## 🚀 Ready to Start?

### What YOU need to do RIGHT NOW:
1. Open https://console.hivemq.cloud/ in your browser
2. Create account (Step 1)
3. Create cluster (Step 2)
4. Copy connection details (Step 3)
5. Create credentials (Step 4)
6. **PASTE THE DETAILS HERE** so I can write the test scripts!

---

## 📝 Connection Details Template

When done with Steps 1-4, copy and paste this filled out:

```
HiveMQ Cluster Details:
- Host: [paste here]
- Port: [paste here, usually 8883]
- WebSocket Port: [paste here, usually 8884]
- Username: [paste here]
- Password: [paste here]
- Cluster ID: [paste here]
```

---

**LET'S GO! 🚀**
