import json
import time


from yolink_mqtt_classV3 import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

class YoLinkSir(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__( yoAccess,  deviceInfo, callback)
        yolink.maxSchedules = 6
        yolink.methodList = ['getState', 'setState']
        yolink.stateList = ['normal', 'alert', 'off' ]
        yolink.SirenName = 'SirenEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'Siren'
        #time.sleep(1)

    '''
    def initNode(yolink):
        yolink.refreshState()
        time.sleep(2)
        if not yolink.online:
            logging.error('Manipulator device not online')
        #    yolink.refreshSchedules()
        #else:
        #    
        #yolink.refreshFW
    ''' 

    
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def setState(yolink, state):
        logging.debug(yolink.type+' - setState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            if state.lower() not in yolink.stateList:
                logging.error('Unknows state passed')
                return(False)
            if state.lower() == 'on':
                state = True
            if state.lower() == 'off':
                state = False
            data = {}
            data['params'] = {}
            data['params']['state'] = state.lower()
            return(yolink.setDevice(data))


    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            attempts = 0
            while yolink.dataAPI[yolink.dData][yolink.dState]  == {} and attempts < 3:
                time.sleep(1)
                attempts = attempts + 1
            if attempts <= 5:
                if  yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'normal':
                    return('normal')
                elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'alert':
                    return('alert')
                elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'off':
                    return('off')                
                else:
                    return('Unkown')
            else:
                return('Unkown')
    
    def getSupplyType(yolink):
        logging.debug(yolink.type+' - getSupplyType')
        try:
            if 'powerSupply' in yolink.dataAPI[yolink.dData]:
                if yolink.dataAPI[yolink.dData]['powerSupply'] == 'battery':
                    return('battery')
                else:
                    return('ext_supply')            
        except Exception as e:
            logging.error('No supply type provided')
            return(None)   

    def getSirenDuration(yolink):
        logging.debug(yolink.type+' - getSirenDuration')
        try:
            if 'alarmDuration' in yolink.dataAPI[yolink.dData]:
                return (yolink.dataAPI[yolink.dData]['alarmDuration'])
            else:
                return (0)          
        except Exception as e:
            logging.error('No alarmDuration provided')
            return(None)   


    def getData(yolink):
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            return(yolink.getData())


class YoLinkSiren(YoLinkSir):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)