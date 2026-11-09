# udi-yolink (Local / Hybrid) (v1.8.73)
Support for YoLink devices in Universal Devices Polyglot (PG3 / PG3x) and IoX / eisy / Polisy with Local Hub (YS1606) and Cloud support.

Suggested installation is on PG3x from version 1.1.x going forward. PG3x is updated to Python 3.11+. It still runs under PG3, but PG3x is strongly recommended.

## Supported YoLink Devices

Enables YoLink ([shop.yosmart.com](https://shop.yosmart.com/)) devices to be monitored and controlled using the ISY / IoX.
The following device types are supported:

- **Switches & Outlets**: `Switch`, `Dimmer`, `Outlet`, `MultiOutlet`
- **Sensors**: `THSensor` (Temperature & Humidity), `DoorSensor`, `MotionSensor`, `LeakSensor`, `VibrationSensor`, `SoilThcSensor`, `COSmokeSensor`, `PowerFailureAlarm`, `WaterDepthSensor`
- **Water Management & Valves**: `WaterMeterController`, `WaterMeterMultiController`, `WaterMeterOnly`, `Sprinkler`, `SprinklerV2`, `Manipulator` (Valve Controller)
- **Security & Access**: `Lock`, `LockV2`, `GarageDoor`, `Finger`, `Siren`, `SmartRemoter`, `InfraredRemoter`
- **Climate**: `Thermostat`
- **Hubs**: `Hub`, `BatteryHub`, `SpeakerHub`
- **Schedules**: Built-in schedule support for on/off devices, multi-outlets, IR remotes, sprinklers, and water meters.

## Operating Modes

The node server supports three operating modes configured via the `MODE` custom parameter:

- **`hybrid` (Default)**: Operates in both local and cloud modes. Local communication is used for supported devices via the YoLink Local Hub (YS1606), with automatic cloud fallback and support for cloud-only devices (such as SpeakerHub).
- **`local`**: Operates in local-only mode. All communication is routed directly through the YoLink Local Hub on your local network (works without internet access once installed). *Note*: Devices requiring cloud services (e.g. SpeakerHub TTS) will not function in local-only mode.
- **`cloud`**: Operates purely via the YoLink Cloud OpenAPI and MQTT broker (similar to the standard YoLink node server).

## Communication & Polling

- **Short Poll (default: 60 seconds)**: Sends a heartbeat to the ISY and verifies whether pending command replies have updated device state. The server uses asynchronous background workers for non-blocking command dispatching.
- **Long Poll (default: 3600 seconds / 1 hour)**: Verifies the online/offline status of all devices. Battery-operated devices report status via heartbeats; if set too frequently, it will increase device battery consumption. If set to more than 2 hours, the access token will expire (though automatic token refresh is handled).

## Code & Architecture

- Uses V2 of the YoLink OpenAPI with PAC/UAC (User Access Credentials) authentication and direct local MQTT/HTTP communication with the YS1606 Local Hub.
- Implements modern **Phase 1 Dynamic JSON Profiles** (`updateJsonProfile`) for IoX 6.0.6+ and PG3x 3.4.5+, with automatic fallback to static profile uploads.
- Includes automatic active-node payload pruning to ensure MQTT profile payloads stay within network and broker limits (<60 KB).
- Coded in Python 3 with standard MIT license.

## Installation & Configuration

### 1. How to Obtain Cloud Credentials (for `cloud` or `hybrid` mode)

To connect the node server to your YoLink cloud account, you need your **UAID** and **SECRET_KEY**:
1. **Open the YoLink Mobile App** (iOS or Android).
2. **Verify Active Home**: Ensure your target Home is selected at the top. YoLink credentials are scoped per home.
3. **Navigate to User Access Credentials**: Tap **Menu (☰)** or **Settings** -> **Account** -> **Advanced Settings** -> **User Access Credentials**.
4. **Create / Retrieve Credentials**: Tap **`+`** to create credentials (e.g. name it `eisy` or `PG3`), or tap an existing credential.
5. **Copy Values**: Copy **UAID** and **SecretKey** (without trailing spaces).

### 2. How to Obtain Local Hub Credentials (for `local` or `hybrid` mode)

From the YoLink Mobile App with your YoLink Local Hub (YS1606):
1. **Local Client ID & Local Client Secret**: Select your Local Hub -> tap **Local Network** -> select **Integrations**. Copy `client_id` to `LOCAL_CLIENT_ID` and `client_secret` to `LOCAL_CLIENT_SECRET`.
2. **Subnet ID**: Select your Local Hub -> tap **Local Network** -> select **General**. Copy **Net ID** to `SUBNET_ID`.
3. **Local IP**: Select your Local Hub -> tap the **`|`** details menu (top-right corner). Copy the IP address to `LOCAL_IP`.

### 3. Configuring the Node Server in Polyglot (PG3 / PG3x)

In your browser, open the Polyglot (PG3/PG3x) dashboard:
1. Open the **YolinkLocal** node server details and navigate to the **Configuration** tab (scroll down to *Custom Configuration Parameters*).
2. Configure the parameters:

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| **`MODE`** | Optional | `hybrid` | Operating mode: `hybrid`, `local`, or `cloud`. |
| **`UAID`** | For cloud/hybrid | — | User Access ID obtained from YoLink app. |
| **`SECRET_KEY`** | For cloud/hybrid | — | Secret Key obtained from YoLink app. |
| **`LOCAL_CLIENT_ID`** | For local/hybrid | — | Local Client ID from Local Hub Integrations. |
| **`LOCAL_CLIENT_SECRET`** | For local/hybrid | — | Local Client Secret from Local Hub Integrations. |
| **`SUBNET_ID`** | For local/hybrid | — | Subnet / Net ID from Local Hub General settings. |
| **`LOCAL_IP`** | For local/hybrid | — | Local IP address of the YoLink Local Hub. |
| **`TEMP_UNIT`** | Optional | `C` | Temperature display unit: `F` for Fahrenheit (UOM 17) or `C` for Celsius (UOM 4). |
| **`WATER_UNIT`** | Optional | `G` | Water volume unit: `G` or `0` for Gallons (UOM 69), `C` or `1` for CCF (UOM 6), `M` or `2` for M³ (UOM 8), `L` or `3` for Liters (UOM 35). |
| **`CALLS_PER_MIN`** | Optional | `60` | Overall YoLink API rate limit (calls per minute across all devices). |
| **`DEV_CALLS_PER_MIN`** | Optional | `5` | Per-device YoLink API rate limit (calls per minute per device). |
| **`NBR_TTS`** | Optional | `0` | Number of SpeakerHub Text-to-Speech message slots to allocate (1–10). Saving this automatically generates the matching `TTS0`–`TTS<n-1>` input parameter fields. |
| **`GARAGE_TRAVEL_TIME`** | Optional | `15` | Garage door travel time in seconds for open/close motion tracking. Can also be set per-door via `GARAGE_TRAVEL_TIME_<address>`. |
| **`GARAGE_SENSOR`** | Optional | Auto | Paired DoorSensor address, deviceId, or name. Automatically discovered via YoLink kit pairing (`parentDeviceId`), name matching, or single sensor fallback. |

3. Click **Save Changes** and **Restart** the node server.

## Dynamic Profiles

The node server uses modern **Dynamic JSON Profiles** to push editor and node definitions directly to IoX at runtime:
- **Unit Customization**: Driver names and UOMs dynamically adjust to your `TEMP_UNIT` and `WATER_UNIT` preferences automatically.
- **Payload Safety**: Large installations automatically prune the profile payload to active device types, keeping messages compact.
- **Fallback**: If dynamic profile updates are unavailable on older PG3/IoX versions, the node server automatically falls back to static profile installation (`updateProfile`).

## Notes & Tips

- **Single Home per Instance**: Each node server instance connects to one YoLink home. If you have multiple homes, create credentials for each home and run separate node server slot instances.
- **SpeakerHub Messages**: When using a SpeakerHub, set `NBR_TTS` to the desired number of messages (1–10) and save changes. The node server automatically generates the corresponding `TTS0`, `TTS1`, ... input lines in Custom Configuration Parameters for you to enter your message texts. Once saved, restart the IoX / Admin Console (or re-login) to refresh the dropdown command labels.
- **Garage Door Controller & Finger**: Full smart state tracking is supported with paired YoLink door sensors (`Closed`, `Open`, `Opening`, `Closing`, `Half-Open`, `Half-Closed`, `Unknown`).
  - **Open (`DON`)**: Opens the door; ignored if already open or opening; executes a 3-pulse sequence if half-open.
  - **Close (`DOF`)**: Closes the door; ignored if already closed or closing; executes a 3-pulse sequence if half-closed.
  - **Toggle (`TOGGLE`)**: Always sends 1 toggle pulse unconditionally (supports stopping the door midway).
  - External door openings/closings (e.g. wall switch or car remote) are detected in real time by the paired sensor, automatically updating door state and travel timers.
- **Countdown Delays**: Remaining delay countdowns shown in the ISY are calculated in real time by the node server.
- **Schedules**: YoLink on-device schedules are fully supported for switches, outlets, dimmers, manipulators, sprinklers, and water meters.
- **Device Status & Reports**: The node server reports the latest report time and battery/connection health for each device.
