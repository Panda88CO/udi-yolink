# udi-yolink
    Support for YoLink devices.
    
## Yolink Node server
    Current list of devices supported is as follows:

    'Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
    'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
    'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock' , 'LockV2', 'Dimmer', 'InfraredRemoter',
    'PowerFailureAlarm', 'SmartRemoter', 'COSmokeSensor', 'Siren', 'WaterMeterController',
    'WaterDepthSensor', 'WaterMeterMultiController', 'SprinklerV2', 'Thermostat',
    'SoilThcSensor'


    Code uses MQTT communications.
    ###SHORT POLL sends a heartbeat to the ISY - default is 60 seconds.
    ###LONG POLL checks the online state of the devices (if a device goes offline, it will not be detected until this is called - for battery-operated devices it may take even longer, as data appears to be cached in the cloud - battery devices are not queried as part of the LONG POLL).
    A device will be redetected once it is back online.
    Default is 3600 (1 hour).  

    Note: if set too often, it will affect battery consumption (especially the Manipulator). If set to more than 2 hours, the token will expire (but a new one should be obtained).


## Code
    Code uses V2 of the YoLink API - PAC/UAC authentication - the node only supports 1 home at a time. More homes can have separate PAC/UAC generated in the YoLink app.

    Coded in Python 3 - MIT license.

## Installation

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
   - **`UAID`**: Paste the copied UAID.
   - **`SECRET_KEY`**: Paste the copied SecretKey.
   - **`TEMP_UNIT`** *(optional)*: Temperature display unit:
     - `F` for Fahrenheit (UOM 17)
     - `C` for Celsius (UOM 4) — *default*
   - **`WATER_UNIT`** *(optional)*: Water volume display unit:
     - `G` or `0` for Gallons (UOM 69) — *default*
     - `C` or `1` for CCF / Hundred Cubic Feet (UOM 6)
     - `M` or `2` for M³ / Cubic Meters (UOM 8)
     - `L` or `3` for Liters (UOM 35)
   - **`NBR_TTS`** *(optional)*: Number of SpeakerHub Text-to-Speech message slots to allocate (1–10).
3. Click **Save Changes** and **Restart** the node server.
   - *Note*: On initial setup, it may occasionally take 1–2 restarts for all devices to synchronize completely. Sometimes a reboot of the ISY / Admin Console is needed for all node definitions to refresh.

## Notes 
    
    Remaining delay time shown in ISY is estimated - countdown is running on the node server, not the device.
    Schedules are not supported (you can use ISY for the same purpose, and the YoLink app can be used to set schedules).
    The latest version of the node reports the latest report time for each device - the AC home automation will get a time.now() option so seconds between the two can be used in conditions.
    