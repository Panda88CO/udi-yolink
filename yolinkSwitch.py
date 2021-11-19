import json
import time
import logging

from yolink_mqtt_class import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)




class YoLinkSW(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)
        
        self.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        self.eventList = ['StatusChange', 'Report', 'getState']
        self.stateList = ['open', 'closed', 'on', 'off']
        self.eventTime = 'Time'
        self.type = 'Switch'
        time.sleep(3)
        #print('self.refreshState')
        #self.refreshState()
        #self.refreshSchedules()
        #self.refreshFWversion()
        #print(' YoLinkSW - finished initailizing')

    ''' Assume no event support needed if using MQTT'''
    def updataStatus(self, data):
        self.updateCallbackStatus(data, False)

    def initNode(self):
        self.refreshState()
        self.refreshSchedules()
        #self.refreshFWversion()
        #print(' YoLinkSW - finished intializing')
 
    def setState(self, state):
        logging.debug(self.type+' - setState')

        if 'setState'  in self.methodList:          
            if state.lower() not in self.stateList:
                logging.error('Unknows state passed')
                return(False)
            if state.lower() == 'on':
                state = 'open'
            if state.lower() == 'off':
                state = 'closed'
            data = {}
            data['params'] = {}
            data['params']['state'] = state.lower()
            return(self.setDevice( data))
        else:
            return(False)
    

    def getState(self):
        logging.debug(self.type+' - getState')
        attempts = 0

        while self.dState not in self.dataAPI[self.dData] and attempts < 5:
            time.sleep(1)
            attempts = attempts + 1
        if attempts < 5 and 'state' in self.dataAPI[self.dData][self.dState]:
            if  self.dataAPI[self.dData][self.dState]['state'] == 'open':
                return('ON')
            elif self.dataAPI[self.dData][self.dState]['state'] == 'closed':
                return('OFF')
            else:
                return('Unkown')
        else:
            return('Unkown')
 
    def getEnergy(self):
        logging.debug(self.type+' - getEnergy')
        return({'power':self.dataAPI[self.dData][self.dState]['power'], 'watt':self.dataAPI[self.dData][self.dState]['power']})


class YoLinkSwitch(YoLinkSW):
    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey,  deviceInfo, self.updateStatus, yolink_URL, mqtt_URL, mqtt_port)
        self.initNode()


    def updateStatus(self, data):
        self.updateCallbackStatus(data, True)

