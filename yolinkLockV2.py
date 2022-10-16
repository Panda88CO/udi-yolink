import json
import time

from yolink_mqtt_classV2 import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)


class YoLink_lock(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        
        yolink.methodList = ['getState', 'fetchState', 'setState' ]
        yolink.eventList = ['StatusChange', 'Report', 'getState']
        yolink.stateList = ['open', 'closed', 'lock', 'unlock']
        yolink.eventTime = 'Time'
        yolink.type = 'Lock'
        yolink.doorBellRing = False
        #time.sleep(2)
        
        #yolink.refreshState()
        #input()
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()

    '''
    def initNode(yolink):
        attemps = 0
        maxAttemts = 3
        yolink.refreshState()
        time.sleep(1)
        #yolink.online = yolink.getOnlineStatus()
        while not yolink.online and attemps <= maxAttemts:
            yolink.refreshState()
            time.sleep(1)
        if yolink.online:    
            logging.error('Outlet not online')
        #else:
        #   yolink.refreshSchedules()
        #self.refreshFWversion()
        #print(' YoLinkSW - finished intializing')
    '''
    
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)
        if 'event' in data:
            if '.Alert' in data['event']:
                if 'alertType' in data['data']:
                    yolink.doorBellRing = data['data']['alertType']
        else:
            yolink.doorBellRing = None

    def getDoorBellRing(yolink):
        return(yolink.doorBellRing)

    def setState(yolink, state):
        logging.debug(yolink.type + ' - setState')
        outlet = str(state)
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            if 'setState'  in yolink.methodList:          
                if outlet.lower() not in yolink.stateList:
                    logging.error('Unknows state passed')
                    return(False, yolink.dataAPI[yolink.dOnline])
                if outlet.lower() == 'lock':
                    state = 'lock'
                if state.lower() == 'unlock':
                    state = 'unlock'
                data = {}
                data['params'] = {}
                data['params']['state'] = state.lower()
                return(yolink.setDevice( data))
        else:
            return(False)
    

    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:       
            attempts = 0
            while yolink.dataAPI[yolink.dData][yolink.dState]  == {} and attempts < 3:
                time.sleep(1)
                attempts = attempts + 1
            if attempts <= 5 and yolink.dataAPI[yolink.dData][yolink.dState]:
                if  yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'locked':
                    return('LOCK')
                elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'unlocked':
                    return('UNLOCK')
                else:
                    return('Unkown')
            else:
                return('Unkown')
        else:
            return('Unkown')

    def fetchState(yolink):
        logging.debug(yolink.type+' - fetchState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:       
            attempts = 0
            while yolink.dataAPI[yolink.dData][yolink.dState]  == {} and attempts < 3:
                time.sleep(1)
                attempts = attempts + 1
            if attempts <= 5 and yolink.dataAPI[yolink.dData][yolink.dState]:
                if  yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'locked':
                    return('LOCK')
                elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'unlocked':
                    return('UNLOCK')
                else:
                    return('Unkown')
            else:
                return('Unkown')
        else:
            return('Unkown')


    
    
class YoLinkLock(YoLink_lock):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()
        #yolink.fetchDevice()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)