# udi-yolink
    Suppport for YoLink devices 
    
## Yolink Node server
    Enables yoLink (https://shop.yosmart.com/) devices to be controlled using the ISY
    Current list of devices supported is as follows:
    
    'Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
    'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
    'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock', 'Dimmer', 
    
    Code uses MQTT communications
    ###SHORT POLL sends a heart beat to the ISY - defauls in 60 sec - It will also chech if data was updated since last update - this can happen when a command has a very slow reply from the cloud - the server uses separate threads from sending commands and receiving results 
    
    ###LONG POLL check the online state of the devices (If a device goes off-line it will not be detected until this is called - for battery operated devices it may take even longer as data appear to be cached in the cloud - battery devices are not querried as part of the LONG POLL) 
    A device will redetected once it is back on-line. 
    Default is 3600 (1 hour).  

    Note if set too often it will affect battery consumption (especially the Manipulator) - if more than 2 hours - token will expire (but a new one should be obtained)


## Code
    Code uses V2 of the yolink API - PAC/UAC authendication - currrently this API only supports a single home (even if APP supports more)

    Coded in Python 3 - MIT license 

## Installation
    Credentials needs to be added to configuration.  In YoLink app goto Settings->Account->Advanced Settings -> User Access Credentials and copy UAID and SecretKey (alternaltive path in app is Profile->Advanced Settings -> User Access Credentials )
    It is possible to get credentials for each home that is defined but the nodes server can only handle one of them currently 

    Enter both UAID and SecretKey under configuration - then restart - some times it seems to require 2 restarts to fully get all devices synchronized (I have looked but cannot find pattern)
    Sometimes a reboot of the ISY is required to make the node server show up correctly.  
     

## Notes 
    One node server can only handle 1 home - you can get credential for each home in the APP by selecting the home and get credentials - multiple credentials can exist at the same time, but ther node server can only handle one

    Remaining delay time shown in ISY is estimated - count down is running on node server - not device

    <SpeakerHub> supports up to 10 Test to Speech messages.  You specify the number of messages desired, and then add the text of the message in TTS<n>.  Restart the node server.  After this a restart of the ISY/PoI is needed to transfer the messages to the UI.  The ISY/PoI only reads the file containg the messages during startup 

    In configuraiton TEMP_UNIT can be used to set temperature until to C, F or K

    Schedules are not supported yet (you can use ISY for the same and the YoLink APP can beused to set schedules)  - I did not manage to get API working with schdules yet 
    