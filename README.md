# udi-yolink
    Suppport for YoLink devices 
    Suggest to install on PG3x from version 1.1.x going forward.  PG3x updated to Python 3.11.  Still works under PG3 but cannot guarantee for how long it will be possible 
    
## Yolink Node server
    Enables yoLink (https://shop.yosmart.com/) devices to be controlled using the ISY
    Current list of devices supported is as follows:
    
    'Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
    'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
    'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock', 'Dimmer', 'InfraredRemoter', 
    'PowerFailureAlarm', 'SmartRemoter', 'COSmokeSensor', 'Siren'
    'WaterMeterController','WaterDepthSensor', 'LockV2'

    
    Code uses MQTT communications
    ###SHORT POLL sends a heart beat to the ISY - defauls is 60 sec - It will also chech if data was updated since last update - this can happen when a command has a very slow reply from the cloud - the server uses separate threads from sending commands and receiving results 
    
    ###LONG POLL check the online state of the devices (If a device goes off-line it will not be detected until this is called - for battery operated devices it may take even longer as data appear to be cached in the cloud - battery devices are not querried as part of the LONG POLL) 
    A device will redetected once it is back on-line. 
    Default is 3600 (1 hour).  

    Note if set too often it will affect battery consumption (especially the Manipulator) - if more than 2 hours - token will expire (but a new one should be obtained)


## Code
    Code uses V2 of the yolink API - PAC/UAC authendication - currrently this API only supports a single home (even if APP supports more)

    Coded in Python 3 - MIT license 

## Installation
    Credentials needs to be added to configuration in YoLink node server under PG3.  In YoLink app goto Settings->Account->Advanced Settings -> User Access Credentials and copy UAID and SecretKey (alternaltive path in app is Profile->Advanced Settings -> User Access Credentials )
    It is possible to get credentials for each home that is defined but the nodes server can only handle one of them currently 

    Enter both UAID and SecretKey under configuration in the node in PG#'s browser page (scroll down if you do not see the fields to enter) - then restart - some times it seems to require 2 restarts to fully get all devices synchronized (I have looked but cannot find pattern)
    Sometimes a reboot of the ISY is required to make the node server show up correctly.  
     

## Notes 
    One node server can only handle 1 home - you can get credential for each home in the APP by selecting the home and get credentials - multiple credentials can exist at the same time, but the node server can only handle one

    Remaining delay time shown in ISY is estimated - count down is running on node server - not device

    <SpeakerHub> supports up to 10 Test to Speech messages.  You specify the number of messages desired, and then add the text of the message in TTS<n>.  Restart the node server.  After this a restart of the ISY/PoI is needed to transfer the messages to the UI.  The ISY/PoI only reads the file containg the messages during startup 

    In configuraiton TEMP_UNIT can be used to set temperature until to C, F or K

    YoLink Schedules are now supported 
    
    Remaining delay time shown in ISY is estimated - count down is running on node server - not device
    Schedules are not supported (you can use ISY for the same and the YoLink APP can beused to set schdules)
    
    The latest version of the node report latest report time for each device - the AC home automation will get a time.now() option so seconds between the two can be used in conditions 
    
