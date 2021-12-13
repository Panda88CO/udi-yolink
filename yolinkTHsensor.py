
import time


from yolink_mqtt_class import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

class YoLinkTHSen(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey,  deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)    
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Report']
        yolink.tempName = 'THEvent'
        yolink.temperature = 'Temperature'
        yolink.humidity = 'Humidity'
        yolink.eventTime = 'Time'
        yolink.type = 'THSensor'
        time.sleep(2)

        
    def initNode(yolink):
        yolink.refreshSensor()
    
    def updataStatus(self, data):
        self.updateCallbackStatus(data, False)

    def refreshSensor(yolink):
        logging.debug(yolink.type+ ' - refreshSensor')
        return(yolink.refreshDevice( ))

    def getOnlineStatus(yolink):
        logging.debug(yolink.type+ ' - refreshSensor')
        return(yolink.getOnlineStatus( ))

    def getTempValueF(yolink):
        return(yolink.getStateValue('temperature')*9/5+32)
    
    def getTempValueC(yolink):
        return(yolink.getStateValue('temperature'))

    def getHumidityValue(yolink):
        return(yolink.getStateValue('humidity'))
    '''
    def getAlarms(yolink):
        return(yolink.getStateValue('alarm'))

    def getBattery(yolink):
        return(yolink.getStateValue('battery'))
    '''    

    def probeState(yolink):
         return(yolink.getState() )

    def probeData(yolink):
        return(yolink.getData() )

'''
Stand-Alone Operation of THsensor (no call back to live update data - pooling data in upper APP)
''' 

class YoLinkTHSensor(YoLinkTHSen):
    def __init__(yolink, csName, csid, csseckey,  deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, deviceInfo, yolink.updateStatus, yolink_URL, mqtt_URL, mqtt_port)    
        yolink.initNode()

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)