# udi-yolink (v1.8.73)
Support for YoLink devices in Universal Devices Polyglot (PG3 / PG3x).

## Supported YoLink Devices

The node server supports monitoring and controlling the following YoLink device types:

- **Switches & Outlets**: `Switch`, `Dimmer`, `Outlet`, `MultiOutlet`
- **Sensors**: `THSensor` (Temperature & Humidity), `DoorSensor`, `MotionSensor`, `LeakSensor`, `VibrationSensor`, `SoilThcSensor`, `COSmokeSensor`, `PowerFailureAlarm`, `WaterDepthSensor`
- **Water Management & Valves**: `WaterMeterController`, `WaterMeterMultiController`, `WaterMeterOnly`, `Sprinkler`, `SprinklerV2`, `Manipulator` (Valve Controller)
- **Security & Access**: `Lock`, `LockV2`, `GarageDoor`, `Finger`, `Siren`, `SmartRemoter`, `InfraredRemoter`
- **Hubs**: `Hub`, `BatteryHub`, `SpeakerHub`
- **Schedules**: Built-in schedule support for on/off devices, multi-outlets, IR remotes, sprinklers, and water meters.

## Communication & Polling

- **Short Poll (default: 60s)**: Sends a heartbeat to the ISY and verifies whether pending command replies have updated device state.
- **Long Poll (default: 3600s / 1 hour)**: Queries device online/offline states. Battery-operated devices rely on heartbeats. Setting long poll higher than 2 hours is not recommended to ensure tokens stay refreshed.

## Code & Architecture

- Uses V2 of the YoLink OpenAPI with PAC/UAC (User Access Credentials) authentication. Each node server instance supports 1 home.
- Uses dynamic JSON profile generation (`updateJsonProfile`) with automatic active-node payload pruning (<60 KB) and fallback to static profile updates.
- Coded in Python 3 with standard MIT license.

## Installation & Configuration

### How to Obtain Credentials from the YoLink App

To connect the node server to your YoLink account, you need your **UAID** and **SECRET_KEY** (User Access Credentials):

1. **Open the YoLink Mobile App** (iOS or Android).
2. **Verify Active Home**:
   - Check the active Home name displayed at the top of the app.
   - If you have multiple homes, tap the home name to switch to the home you want to control.
   - *Note*: YoLink credentials are scoped per home. If you want to control devices in multiple homes, generate credentials for each and run a separate node server instance for each home.
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
   - Use the **Copy** icon next to each field to copy them without extra spaces.

### Configuring the Node Server in Polyglot (PG3 / PG3x)

In your browser, open the Polyglot (PG3/PG3x) dashboard:
1. Open the **YoLink** node server details and navigate to the **Configuration** tab (scroll down to the *Custom Configuration Parameters* section).
2. Configure the following parameters:

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| **`UAID`** | **Yes** | — | User Access ID obtained from the YoLink app. |
| **`SECRET_KEY`** | **Yes** | — | Secret Key obtained from the YoLink app. |
| **`TEMP_UNIT`** | Optional | `C` | Temperature display unit: `F` for Fahrenheit (UOM 17) or `C` for Celsius (UOM 4). |
| **`WATER_UNIT`** | Optional | `G` | Water volume unit: `G` or `0` for Gallons (UOM 69), `C` or `1` for CCF (UOM 6), `M` or `2` for M³ (UOM 8), `L` or `3` for Liters (UOM 35). |
| **`CALLS_PER_MIN`** | Optional | `60` | Overall YoLink API rate limit (calls per minute across all devices). |
| **`DEV_CALLS_PER_MIN`** | Optional | `5` | Per-device YoLink API rate limit (calls per minute per device). |
| **`NBR_TTS`** | Optional | `0` | Number of SpeakerHub Text-to-Speech message slots to allocate (1–10). Saving this automatically generates the matching `TTS0`–`TTS<n-1>` input parameter fields. |
| **`GARAGE_TRAVEL_TIME`** | Optional | `15` | Garage door travel time in seconds for open/close motion tracking. Can also be set per-door via `GARAGE_TRAVEL_TIME_<address>`. |
| **`GARAGE_SENSOR`** | Optional | Auto | Paired DoorSensor address, deviceId, or name. Automatically discovered via YoLink kit pairing (`parentDeviceId`), name matching, or single sensor fallback. |

3. Click **Save Changes** and **Restart** the node server.
   - *Note*: On initial setup, allow 1–2 minutes for all devices to synchronize completely.

## Notes

- **Single Home per Instance**: Each node server instance connects to one YoLink home. If you have multiple homes, create credentials for each home and run separate node server instances.
- **Schedules**: YoLink schedules are supported for on/off devices, multi-outlets, IR remotes, sprinklers, and water meters.
- **Countdown Delays**: Remaining delay countdowns shown in ISY are estimated and tracked on the node server.
- **SpeakerHub Messages**: When using a SpeakerHub, set `NBR_TTS` to the desired number of messages (1–10) and click **Save Changes**. The node server automatically creates the corresponding `TTS0`, `TTS1`, ... input lines in Custom Configuration Parameters for you to enter your message texts. Once saved, restart the IoX / Admin Console (or re-login) to refresh the dropdown command labels.
- **Garage Door Controller & Finger**: Full smart state tracking is supported with paired YoLink door sensors (`Closed`, `Open`, `Opening`, `Closing`, `Half-Open`, `Half-Closed`, `Unknown`).
  - **Open (`DON`)**: Opens the door; ignored if already open or opening; executes a 3-pulse sequence if half-open.
  - **Close (`DOF`)**: Closes the door; ignored if already closed or closing; executes a 3-pulse sequence if half-closed.
  - **Toggle (`TOGGLE`)**: Always sends 1 toggle pulse unconditionally (supports stopping the door midway).
  - External door openings/closings (e.g. wall switch or car remote) are detected in real time by the paired sensor, automatically updating door state and travel timers.
- **Dynamic Profile Updates**: Device profiles and custom unit labels are automatically registered upon startup.