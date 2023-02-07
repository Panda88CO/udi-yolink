# udi-yolink
    Suppport for YoLink devices 
    
## Yolink Node server
    Current list of devices supported is as follows:

    'Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
    'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
    'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock', 'Dimmer', 'InfraredRemoter', 
    'PowerFailureAlarm', 'SmartRemoter'

    Code uses MQTT communications
    ###SHORT POLL sends a heart beat to the ISY - defauls is 60 sec
    ###LONG POLL check the online state of the devices (If a device goes off-line it will not be detected until this is called - for battery operated devices it may take even longer as data appear to be cached in the cloud - battery devices are not querried as part of the LONG POLL) 
    A device will redetected once it is back on-line. 
    Default is 3600 (1 hour).  

    Note if set too often it will affect battery consumption (especially the Manipulator) - if more than 2 hours - token will expire (but a new one should be obtained)


## Code
    Code uses V2 of the yolink API - PAC/UAC authendication - node only support 1 home at a time - more homes can have separate PAC/UAE generated in the YoLink App 

    Coded in Python 3 - MIT license 

## Installation
    Credentials needs to be added to configuration.   In YoLink app goto Settings->Account->Advanced Settings -> User Access Credentials and copy UAID and SecretKey (alternaltive path in app is Profile->Advanced Settings -> User Access Credentials ).  It is also possible to set the temp unit (C/F/K)

    Note, It is possible to create more than 1 home in the app - each home will have it own credentials.  if more than one home is to be supported, a separate node server must be used for each home.  

    Enter both UAID and SecretKey under Yolink node (PG3) configuration in browser (scroll down for see fields) - then restart - some times it seems to require 2 restarts to fully get all devices synchronized (I have looked but cannot find pattern).  Note If devices are off-line when restarting they will get removed (They will stay if off-line during normal operation)

    Speakerhub requires the desired sentences to be input in config (up to 10 are supported).  You will need to reboot the isy after runnign the node server for this to take effect (no way to update these while ISY is running)

## Notes 
    
    Remaining delay time shown in ISY is estimated - count down is running on node server - not device
    Schedules are not supported (you can use ISY for the same and the YoLink APP can beused to set schdules)  
    