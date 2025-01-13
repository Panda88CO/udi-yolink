

import time
from yolink_mqtt_classV3 import YoLinkMQTTDevice

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)




class YoLinkCOSmokeSen(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Report','Alert']
        yolink.waterName = 'WaterEvent'
        yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
        #time.sleep(1)
        #yolink.refreshSensor()

    def refreshSensor(yolink):
        logging.debug('refreshWaterSensor')
        #time.sleep(2)
        if yolink.online:   
            return(yolink.refreshDevice())

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)
    '''
    def initNode(yolink):
        yolink.refreshDevice()
        #time.sleep(2)
        #yolink.online = yolink.getOnlineStatus()
        if not yolink.online:
            logging.error('COSmoke Sensor not online')
    '''
    
        
    def alert_state(yolink, type):
        state = yolink.getDataStateValue('state')
        logging.debug('alert_state {}'.format(state ))
        if  type == 'smoke':
            if 'smokeAlarm' in state:
                return(state['smokeAlarm'])
            else:
                return (None)        
        elif type  == 'CO' :
            if 'gasAlarm' in state:
                return(state['gasAlarm'])
            else:
                return (None)     
        elif type == 'high_temp':
            if 'highTempAlarm' in state:
                return(state['highTempAlarm'])
            else:
                return (None)                 
        elif type == 'battery':
            if 'sLowBattery' in state:
                return(state['sLowBattery'])
            else:
                return (None)             

    def get_self_ckheck_state (yolink):
         state = yolink.getDataStateValue('metadata')
         if 'inspect' in state:
             return( state['inspect'])
         else:
             return(None)





class YoLinkCOSmokeSensor(YoLinkCOSmokeSen):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(   yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)
    

