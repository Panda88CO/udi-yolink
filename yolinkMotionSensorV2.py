import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_mqtt_classV2 import YoLinkMQTTDevice


class YoLinkMotionSen(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Alert' , 'getState', 'StatusChange']
        yolink.eventName = 'MotionEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'MotionSensor'
        #time.sleep(2)
       
    '''
    def initNode(yolink):
        yolink.refreshDevice()
        time.sleep(2)
        #yolink.online = yolink.getOnlineStatus()
        if not yolink.online:
            logging.error('Motion Sensor not online')
    '''
    
    def refreshSensor(yolink):
        yolink.refreshDevice()

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def getMotionState(yolink):
        return(yolink.getState())
    
    def motionData(yolink):
        return(yolink.getData())         

class YoLinkMotionSensor(YoLinkMotionSen):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__( yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)