import json
import time


from yolink_mqtt_class import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

class YoLinkManipul(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)
        yolink.maxSchedules = 6
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        yolink.eventList = ['StatusChange', 'Report']
        yolink.ManipulatorName = 'ManipulatorEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'Manipulator'
        time.sleep(1)


    def initNode(yolink):
        yolink.refreshState()
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            yolink.refreshSchedules()
        else:
            logging.error('Manipulator device not online')

        #yolink.refreshFW
        

    
    def updateStatus(self, data):
        self.updateCallbackStatus(data, False)

    def setState(yolink, state):
        logging.debug(yolink.type+' - setState')
        yolink.online = yolink.getOnlineStatus()
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
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            attempts = 0
            while yolink.dataAPI[yolink.dData][yolink.dState]  == {} and attempts < 5:
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
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            return(yolink.getData())


class YoLinkManipulator(YoLinkManipul):
    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey,  deviceInfo, self.updateStatus, yolink_URL, mqtt_URL, mqtt_port)
        self.initNode()


    def updateStatus(self, data):
        self.updateCallbackStatus(data, True)