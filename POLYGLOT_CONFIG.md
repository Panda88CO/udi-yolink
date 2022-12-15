# udi-yolink
    Suppport for YoLink devices 
    
## Yolink Node server
    Current list of devices supported is as follows:

    'Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
    'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
    'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock', 'Dimmer', 'InfraredRemoter', 
    
    Code uses MQTT communications
    ###SHORT POLL sends a heart beat to the ISY - defauls is 60 sec
    ###LONG POLL check the online state of the devices (If a device goes off-line it will not be detected until this is called - for battery operated devices it may take even longer as data appear to be cached in the cloud - battery devices are not querried as part of the LONG POLL) 
    A device will redetected once it is back on-line. 
    Default is 3600 (1 hour).  

    Note if set too often it will affect battery consumption (especially the Manipulator) - if more than 2 hours - token will expire (but a new one should be obtained)


## Code
    Code uses V2 of the yolink API - PAC/UAC authendication - currrently this API only supports a single home (even if APP supports more)

    Coded in Python 3 - MIT license 

## Installation
    Credentials needs to be added to configuration.   In YoLink app goto Settings->Account->Advanced Settings -> User Access Credentials and copy UAID and SecretKey (alternaltive path in app is Profile->Advanced Settings -> User Access Credentials )
    Enter both UAID and SecretKey under configuration - then restart - some times it seems to require 2 restarts to fully get all devices synchronized (I have looked but cannot find pattern).  Note If devices are off-line when restarting they will get removed (They will stay if off-line during normal operation)

## Notes 
    
    Remaining delay time shown in ISY is estimated - count down is running on node server - not device
    Schedules are not supported yet (you can use ISY for the same and the YoLink APP can beused to set schdules)  
    