import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_mqtt_classV3 import YoLinkMQTTDevice


class YoLinkPowerFailSen(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Alert' , 'getState', 'StatusChange']
        yolink.eventName = 'PowerFailurerationEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'PowerFailureAlarm'
        #time.sleep(2)
       
    
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def getPowerSupplyConnected(yolink):
        tmp = yolink.getStateValue('PowerSupply')
        logging.debug('getPowerSupplyState: {}'.format(tmp))
        return(tmp)


    def getAlertType(yolink):
        tmp = yolink.getStateValue('alertType')
        logging.debug('{} getAlertType: {}'.format(yolink.type, tmp))
        if None == tmp:
            return(0)
        else:
            return(1)
              

    def muted(yolink):
        tmp = yolink.getStateValue('alertType')
        logging.debug('getAlertType: {}'.format(tmp))
        return(tmp)        

    def getState(yolink):
        tmp = yolink.getState()
        logging.debug('{} - getState: {}'.format(yolink.type, tmp))
        if "normal"  == tmp:
            return(0)
        elif "alert" == tmp:
            return(1)
        elif "off" == tmp:
            return(2)
        else:
            return(99)
        



    '''    
    def getVibrationState(yolink):
        return(yolink.getState())
    
    def refreshSensor(yolink):
        logging.debug(yolink.type+ ' - refreshSensor')
        return(yolink.refreshDevice( ))
    '''

class YoLinkPowerFailSensor(YoLinkPowerFailSen):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__( yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)