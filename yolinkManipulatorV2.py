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

class YoLinkManipul(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__( yoAccess,  deviceInfo, callback)
        yolink.maxSchedules = 6
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        yolink.eventList = ['StatusChange', 'Report']
        yolink.ManipulatorName = 'ManipulatorEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'Manipulator'
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

    
    def updateStatus(self, data):
        self.updateCallbackStatus(data, False)

    def setState(yolink, state):
        logging.debug(yolink.type+' - setState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            if state.lower() != 'open' and  state.lower() != 'closed':
                logging.error('Unknows state passed')
                return(False)
            data = {}
            data['params'] = {}
            data['params']['state'] = state.lower()
            return(yolink.setDevice( data))


    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            attempts = 0
            while yolink.dataAPI[yolink.dData][yolink.dState]  == {} and attempts < 3:
                time.sleep(1)
                attempts = attempts + 1
            if attempts <= 5:
                if  yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'open':
                    return('open')
                elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'closed':
                    return('closed')
                else:
                    return('Unkown')
            else:
                return('Unkown')
    
    def getData(yolink):
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            return(yolink.getData())


class YoLinkManipulator(YoLinkManipul):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)