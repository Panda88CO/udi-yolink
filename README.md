# udi-yolink (v1.8.65)
Support for YoLink devices in Universal Devices Polyglot (PG3 / PG3x) and IoX / eisy / Polisy.

Suggested installation is on PG3x from version 1.1.x going forward. PG3x is updated to Python 3.11+. It still runs under PG3, but PG3x is strongly recommended.

## Supported YoLink Devices

Enables YoLink ([shop.yosmart.com](https://shop.yosmart.com/)) devices to be monitored and controlled using the ISY / IoX.
The following device types are supported:

- **Switches & Outlets**: `Switch`, `Dimmer`, `Outlet`, `MultiOutlet`
- **Sensors**: `THSensor` (Temperature & Humidity), `DoorSensor`, `MotionSensor`, `LeakSensor`, `VibrationSensor`, `SoilThcSensor`, `COSmokeSensor`, `PowerFailureAlarm`, `WaterDepthSensor`
- **Water Management & Valves**: `WaterMeterController`, `WaterMeterMultiController`, `WaterMeterOnly`, `Sprinkler`, `SprinklerV2`, `Manipulator` (Valve Controller)
- **Security & Access**: `Lock`, `LockV2`, `GarageDoor`, `Finger`, `Siren`, `SmartRemoter`, `InfraredRemoter`
- **Hubs**: `Hub`, `BatteryHub`, `SpeakerHub`
- **Schedules**: Built-in schedule support for on/off devices, multi-outlets, IR remotes, sprinklers, and water meters.

## Communication & Polling

The node server connects directly to the YoLink Cloud via MQTT for real-time status and alerts.

- **Short Poll (default: 60 seconds)**: Sends a heartbeat to the ISY and verifies whether pending command replies have updated device state. The server uses asynchronous background workers to ensure fast, non-blocking command dispatching.
- **Long Poll (default: 3600 seconds / 1 hour)**: Verifies the online/offline status of all devices. Battery-operated devices report status via heartbeats; if set too frequently, it will increase device battery consumption. If set to more than 2 hours, the access token will expire (though automatic token refresh is handled).

## Code & Architecture

- Uses V2 of the YoLink OpenAPI with PAC/UAC (User Access Credentials) authentication.
- Implements modern **Phase 1 Dynamic JSON Profiles** (`updateJsonProfile`) for IoX 6.0.6+ and PG3x 3.4.5+, with automatic fallback to static profile uploads.
- Includes automatic active-node payload pruning to ensure MQTT profile payloads stay within network and broker limits (<60 KB).
- Coded in Python 3 with standard MIT license.

## Installation & Configuration

### How to Obtain Credentials from the YoLink App

To connect the node server to your YoLink account, you need your **UAID** and **SECRET_KEY** (User Access Credentials):

1. **Open the YoLink Mobile App** (iOS or Android).
2. **Verify Active Home**:
   - Check the active Home name displayed at the top of the app.
   - If you have multiple homes, tap the home name to switch to the home you want to control.
   - *Note*: YoLink credentials are scoped per home. If you have devices in multiple homes, create separate credentials for each home and install a dedicated node server instance for each home.
3. **Navigate to User Access Credentials**:
   - Tap the **Menu icon** (`☰` in the top-left corner) or tap the **Profile / Settings** icon.
   - Tap **Settings** -> **Account** (or tap your account avatar/email address).
   - Tap **Advanced Settings**.
   - Tap **User Access Credentials**.
   *(Alternative path in some app versions: Profile tab -> Advanced Settings -> User Access Credentials)*.
4. **Create / Retrieve Credentials**:
   - If no credentials exist yet, tap the **`+` (Plus)** button in the top-right corner to create one.
   - Enter a description name (such as `eisy`, `PG3`, or `ISY`).
   - Tap the created credential entry to view details.
5. **Copy the Values**:
   - **UAID** (User Access ID / Client ID)
   - **SecretKey** (Client Secret)
   - Use the **Copy** icon next to each field to copy them to your clipboard without trailing spaces.

### Configuring the Node Server in Polyglot (PG3 / PG3x)

In your browser, open the Polyglot (PG3/PG3x) dashboard:
1. Open the **YoLink** node server details and navigate to the **Configuration** tab (scroll down to *Custom Configuration Parameters*).
2. Configure the following parameters:

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| **`UAID`** | **Yes** | — | User Access ID obtained from the YoLink app. |
| **`SECRET_KEY`** | **Yes** | — | Secret Key obtained from the YoLink app. |
| **`TEMP_UNIT`** | Optional | `C` | Temperature display unit: `F` for Fahrenheit (UOM 17) or `C` for Celsius (UOM 4). |
| **`WATER_UNIT`** | Optional | `G` | Water volume unit: `G` or `0` for Gallons (UOM 69), `C` or `1` for CCF (UOM 6), `M` or `2` for M³ (UOM 8), `L` or `3` for Liters (UOM 35). |
| **`CALLS_PER_MIN`** | Optional | `60` | Overall YoLink API rate limit (calls per minute across all devices). |
| **`DEV_CALLS_PER_MIN`** | Optional | `5` | Per-device YoLink API rate limit (calls per minute per device). |
| **`NBR_TTS`** | Optional | `0` | Number of SpeakerHub Text-to-Speech message slots to allocate (1–10). |

3. Click **Save Changes** and **Restart** the node server.
   - *Note*: On initial setup, allow 1–2 minutes for all devices to discover and synchronize completely.

## Dynamic Profiles & Debugging

The node server uses modern **Dynamic JSON Profiles** to push editor and node definitions directly to IoX at runtime:
- **Unit Customization**: Driver names and UOMs dynamically adjust to your `TEMP_UNIT` and `WATER_UNIT` preferences automatically.
- **Payload Safety**: Large installations with dozens of devices automatically prune the profile payload to active device types, keeping MQTT messages under 60 KB.
- **Debug Dumps**: The node server automatically writes payload debug files for inspection:
  - `profile_payload_debug.json`: Full dynamic profile structure.
  - `profile_payload_pruned_debug.json`: Active-node pruned structure.
- **Fallback**: If dynamic profile updates are unavailable on older PG3/IoX versions, the node server automatically falls back to static profile installation (`updateProfile`).

## Testing & Verification

The codebase includes an automated test harness and setup file validator:

- **Run all unit tests (73 tests)**:
  ```bash
  python3 run_tests.py
  ```
- **Validate setup files (NodeDefs, Editors, NLS translations)**:
  ```bash
  python3 CheckSetupFiles.py
  ```

## Notes & Tips

- **Single Home per Instance**: Each node server instance connects to one YoLink home. If you have multiple homes, create credentials for each home and run separate node server slot instances.
- **SpeakerHub Messages**: If using a SpeakerHub, set `NBR_TTS` to the desired number of messages (up to 10), then configure the message text in `TTS<n>` parameters. Restart the node server; an IoX / Admin Console restart is required to refresh message labels.
- **Countdown Delays**: Remaining delay countdowns shown in the ISY are calculated in real time by the node server.
- **Schedules**: YoLink on-device schedules are fully supported for switches, outlets, dimmers, manipulators, sprinklers, and water meters.
- **Heartbeat & Event Deduplication**: State changes include ghost-trigger protection and alert event deduplication to ensure reliable automation trigger execution.
