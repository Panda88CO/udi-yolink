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
        logging.debug(yolink.type+' - setState = {}'.format(state))
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            if state == 'on':
                state = 'on'
            if state == 'off':
                state = 'off'
            else:
                logging.error('Unknows state passed')
                return(False)
            data = {}
            data['params'] = {}
            data['params']['state'] = state
            return(yolink.setDevice(data))


    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            attempts = 0
            while yolink.dataAPI[yolink.dData] == {} and attempts < 3:
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
        logging.debug(yolink.type+' - getSupplyType = {}'.format(yolink.dataAPI[yolink.dData]))
        try:
            if 'powerSupply' in yolink.dataAPI[yolink.dData][yolink.dState]:
                if yolink.dataAPI[yolink.dData][yolink.dState]['powerSupply'] == 'battery':
                    return('battery')
                else:
                    return('ext_supply')
        except Exception as e:
            logging.error('No supply type provided')
            return(None)   

    def getSirenDuration(yolink):
        logging.debug(yolink.type+' - getSirenDuration:{}'.format(yolink.dataAPI[yolink.dData]))
        try:
            if 'alarmDuation' in yolink.dataAPI[yolink.dData][yolink.dState]:
                return (yolink.dataAPI[yolink.dData][yolink.dState]['alarmDuation'])
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