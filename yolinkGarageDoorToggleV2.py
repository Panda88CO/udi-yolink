
import time


from yolink_mqtt_classV3 import YoLinkMQTTDevice

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)


class YoLinkGarageDoorCtrl(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess, deviceInfo, callback)
        yolink.methodList = ['toggle' ]
        yolink.eventList = ['Report']
        yolink.ToggleName = 'GarageEvent'
        yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
        yolink.online = True # No way to check 
        
    def toggleDevice(yolink):
        logging.debug(yolink.type+' - toggle')
        data={}
        return(yolink.setDevice(data))

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    
class YoLinkGarageDoorToggle(YoLinkGarageDoorCtrl):
    def __init__(yolink, yoAccess,  deviceInfo ):
        super().__init__( yoAccess,  deviceInfo, yolink.updateStatus)
        #yolink.initNode()
        yolink.online = True # No way to check 
        

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)