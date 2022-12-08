import json
import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_mqtt_classV3 import YoLinkMQTTDevice


class YoLinkDoorSens(YoLinkMQTTDevice):
    def __init__ (yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Report']
        yolink.eventTime = 'Time'
        yolink.type = 'DoorSensor'
        #time.sleep(2)
       
  
    #def refreshDoorSensor(yolink):
    #    logging.debug(yolink.type+ ' - refreshDoorSensor') 
    #    return(yolink.refreshDevice( ))

    #def doorState(yolink):
    #    return(yolink.getState())

    #def doorData(yolink):
    #    return(yolink.getData())

    
    def refreshSensor(yolink):
        yolink.refreshDevice()

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    
class YoLinkDoorSensor(YoLinkDoorSens):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)