import json
import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_mqtt_classV2 import YoLinkMQTTDevice


class YoLinkGarageDoorSen(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Report']
        yolink.GarageName = 'GarageEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'DoorSensor'

        time.sleep(2)
        yolink.refreshGarageDoorSensor()
  
    def refreshGarageDoorSensor(yolink):
        logging.debug('refreshGarageDoorSensor') 
        return(yolink.refreshDevice( ))

    def initNode(yolink):
        yolink.refreshDevice()
        yolink.online = yolink.getOnlineStatus()
        if not yolink.online:
            logging.error('Door Sensor not online')

    def updataStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def doorState(yolink):
        return(yolink.getState())

    def doorData(yolink):
        return(yolink.getData())
    


class YoLinkGarageDoorSensor(YoLinkGarageDoorSen):        
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__( yoAccess,  deviceInfo,  yolink.updateStatus)    
        yolink.initNode()

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)