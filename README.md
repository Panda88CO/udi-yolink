# udi-yolink
    Suppport for YoLink devices 
    
## Yolink Node server
    Enables yoLink (https://shop.yosmart.com/) devices to be controlled using the ISY
    Current list of devices supported is as follows:
    
    'Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor'
    
    Code uses MQTT communications
    ###SHORT POLL sends a heart beat to the ISY - defauls in 60 sec
    ###LONG POLL check the online state of the devices (If a device goes off-line it will not be detected until this is called - for battery operated devices it may take even longer as data appear to be cached in the cloud) - the device will reinstall itself once it is back on-line - default is 3600 (1 hour).  Note if set too often it will affect battery consumption (especially the Manipulator) - if more than 2 hours - token will expire (but a new one should be obtained)

    Code uses V2 of the yolink API - PAC/UAC authendication - currrently this API only supports a single home (even if APP supports more)
    Credentials needs to be added to configuration.  Goto Settings->Account->Advanced Settings -> User Access Credentials 
    Enter both UAID and Secret Key under configuration - then restart 

## Code
    Coded in Python 3 - MIT license 

## Installation
    See above

## Notes 
