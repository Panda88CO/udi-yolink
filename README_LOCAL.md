# udi-yolink
    Support for YoLink devices.
    Suggested installation is on PG3x from version 1.1.x going forward. PG3x is updated to Python 3.11. It still works under PG3, but we cannot guarantee how long that will remain possible.
    
## Yolink Node server
    Enables YoLink (https://shop.yosmart.com/) devices to be controlled using the ISY.
    Current list of devices supported is as follows:
    
    'Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
    'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
    'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock' , 'LockV2', 'Dimmer', 'InfraredRemoter',
    'PowerFailureAlarm', 'SmartRemoter', 'COSmokeSensor', 'Siren', 'WaterMeterController',
    'WaterDepthSensor', 'WaterMeterMultiController', 'SprinklerV2', 'Thermostat',
    'SoilThcSensor'

    
    Code uses MQTT communications.
    ###SHORT POLL sends a heartbeat to the ISY - default is 60 seconds - It also checks whether data has been updated since the last update. This can happen when a command has a very slow reply from the cloud. The server uses separate threads for sending commands and receiving results.
    
    ###LONG POLL checks the online state of the devices (if a device goes offline, it will not be detected until this is called - for battery-operated devices it may take even longer, as data appears to be cached in the cloud - battery devices are not queried as part of the LONG POLL).
    A device will be redetected once it is back online.
    Default is 3600 (1 hour).  

    Note: if set too often, it will affect battery consumption (especially the Manipulator). If set to more than 2 hours, the token will expire (but a new one should be obtained).


## Code
    Code uses V2 of the YoLink API - PAC/UAC authentication - currently this API only supports a single home (even if the app supports more).

    Coded in Python 3 - MIT license.

## Installation
MODE
    Mode sets the operation of the node server.
    local - uses local-only operation - This allows all local devices to be controlled (even without internet access once installed). Note: some devices do not work in local-only mode (e.g., SpeakerHub).
    hybrid - operates in both local and cloud modes - This is the default if you have the YoLink local hub (YS1606).
    cloud - operates like the YoLink node (separate node) - only uses cloud access/control for devices.

UAID / SECRET_KEY (needed for cloud or hybrid mode)
    Credentials need to be added to configuration in the YoLink node server under PG3:
    1. In the YoLink app, ensure your target Home is selected at the top.
    2. Tap the Menu icon (☰) or Settings -> Account -> Advanced Settings -> User Access Credentials.
    3. Tap '+' to create credentials if none exist, or tap the existing entry.
    4. Copy UAID and SecretKey.
    5. In PG3/PG3x configuration, set UAID and SECRET_KEY (no extra spaces).
    Note: YoLink credentials are scoped per home; each home requires its own credentials and separate node server instance.

LOCAL_CLIENT_ID, LOCAL_CLIENT_SECRET (needed for local or hybrid mode)
    These can only be obtained from the YoLink local hub.
    In the YoLink app - select the local hub - select Local Network, then select Integrations.
    Copy `client_id` to LOCAL_CLIENT_ID and copy `client_secret` to LOCAL_CLIENT_SECRET.

SUBNET_ID (needed for local or hybrid mode)
    This can only be obtained from the YoLink local hub.
    In the YoLink app - select the local hub - select Local Network, then select General.
    Copy Net ID to SUBNET_ID.

LOCAL_IP (needed for local or hybrid mode)
    IP address of the local hub.
    This can only be obtained from the YoLink local hub - select `|` (upper right corner).
    Copy the IP address to LOCAL_IP.

TEMP_UNIT
    Select F or C (default is F)

WATER_UNIT
    Select Gallon, CCF, M³, or Liter (or G, C, M, L / 0, 1, 2, 3). Default is Gallon.

NBR_TTS
    Number of SpeakerHub Text-to-Speech messages to support (see below).

## Notes 
    One node server can only handle 1 home - you can get separate credentials for each home in the app by selecting the home and getting credentials - multiple credentials can exist at the same time, but the node server can only handle one.

    Remaining delay time shown in ISY is estimated - countdown is running on the node server, not the device.

    <SpeakerHub> supports up to 10 Text-to-Speech messages. You specify the number of messages desired, and then add the text of the message in TTS<n>. Restart the node server. After this, a restart of the ISY/PoI is needed to transfer the messages to the UI. The ISY/PoI only reads the file containing the messages during startup.

    In configuration, TEMP_UNIT can be used to set the temperature unit to C or F (default is F).

    YoLink schedules are supported for On/Off devices, keys/buttons, multi-outlet devices, sprinkler controllers, and water meters.
    
    The latest version of the node reports the latest report time for each device - the AC home automation will get a time.now() option so seconds between the two can be used in conditions.

    YoLink and YoLink local use the same device code.
    
    
