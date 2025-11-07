# Instructions: Move Devices to Old Plant

## Current Device Setup

From the diagnostic, all 7 devices are in **Branch 1 (HiTech)**:

| Device | Current Branch | Current Sector | Suggested Action |
|--------|----------------|----------------|------------------|
| tugger-01 | Branch 1 | Sector 2 | **Move to Branch 2** |
| tugger-02 | Branch 1 | Sector 2 | **Move to Branch 2** |
| tugger-03 | Branch 1 | Sector 2 | Keep in Branch 1 |
| tugger-04 | Branch 1 | Sector 1 | Keep in Branch 1 |
| dzdB2rvp3k | Branch 1 | Sector 1 | Keep in Branch 1 |
| kjuSXGs4Y9 | Branch 1 | - | Keep in Branch 1 |
| hitech-amr-01 | Branch 1 | - | Keep in Branch 1 |

## Steps to Move Devices

### In Twinzo Dashboard:

1. **Navigate to Devices/Assets**
   - Go to the devices management page

2. **Edit tugger-01:**
   - Click on tugger-01
   - Change **Branch** from "Plant 4 - HiTech" → **"Plant 1 - Oldest Original"**
   - Change **Sector** to **"Main"** (Sector 2)
   - Save

3. **Edit tugger-02:**
   - Click on tugger-02
   - Change **Branch** from "Plant 4 - HiTech" → **"Plant 1 - Oldest Original"**
   - Change **Sector** to **"Main"** (Sector 2)
   - Save

4. **Keep tugger-03 in Branch 1 / Sector 1:**
   - Click on tugger-03
   - Change **Branch**: Keep as "Plant 4 - HiTech"
   - Change **Sector** to **"Sector 1"** (not Sector 2)
   - Save

## Result

After these changes:
- **Old Plant (Branch 2)**: tugger-01, tugger-02
- **HiTech (Branch 1)**: tugger-03, tugger-04, and others

Then run: `python -X utf8 test_both_plants.py`

This will stream:
- tugger-01, tugger-02 → Old Plant (Sector 2 in Branch 2)
- tugger-03, tugger-04 → HiTech (Sector 1 in Branch 1)
