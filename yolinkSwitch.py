import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)


class YoLinkSwitch(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        
        self.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        self.eventList = ['StatusChange', 'Report', 'getState']
        self.stateList = ['open', 'closed', 'on', 'off']
        self.ManipulatorName = 'ManipulatorEvent'
        self.eventTime = 'Time'
        self.type = 'Switch'
        time.sleep(2)
        
        self.refreshState()
        #input()
        self.refreshSchedules()
        #self.refreshFWversion()


    '''
    def updateStatusData(self, data): 
        if 'online' in data[self.dData]:
            self.dataAPI[self.dOnline] = data[self.dData][self.dOnline]
        else:
            self.dataAPI[self.dOnline] = True
        if 'method' in data:
            for key in data[self.dData]:
                if key == 'delay':
                        self.dataAPI[self.dData][self.dDelays] = data[self.dData][key]
                else:
                        self.dataAPI[self.dData][self.dState][key] = data[self.dData][key]
        else: #event
            for key in data[self.dData]:
                self.dataAPI[self.dData][self.dState][key] = data[self.dData][key]
        self.updateLoraInfo(data)
        self.updateMessageInfo(data)

    
    def updateStatus(self, data):
        logging.debug(self.type+' - updateStatus')
        if 'method' in  data:
            if data['code'] == '000000':
                if  (data['method'] == self.type +'.getState' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)       
                elif  (data['method'] == self.type +'.setState' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)                          
                elif  (data['method'] == self.type +'.setDelay' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)       
                elif  (data['method'] == self.type +'.getSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateScheduleStatus(data)
                elif  (data['method'] == self.type +'.setSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateScheduleStatus(data)
                elif  (data['method'] == self.type +'.getVersion' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateFWStatus(data)
                else:
                    logging.debug('Unsupported Method passed' + json.dumps(data))     
            else:
                self.deviceError(data)
        elif 'event' in data:
            if data['event'] == self.type +'.StatusChange' :
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)              
            elif data['event'] == self.type +'.Report':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)   
            elif data['event'] == self.type +'.getState':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)                                         
            elif data['event'] == self.type +'.getSchedules':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateScheduleStatus(data)              
            else:
                logging.debug('Unsupported Event passed - trying anyway' + str(json(data)))
                try:
                    if int(data['time']) > int(self.getLastUpdate()):
                        if data['event'].find('chedule') >= 0 :
                            self.updateScheduleStatus(data)    
                        elif data['event'].find('ersion') >= 0 :
                            self.updateFWStatus(data)
                        else:
                            self.updateStatusData(data)   
                except logging.exception as E:
                    logging.debug('Unsupported event detected: ' + str(E))
            self.eventPending
        else:
            logging.debug('updateStatus: Unsupported packet type: ' +  json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
    '''

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
        while self.dataAPI[self.dData][self.dState]  == {} and attempts < 5:
            time.sleep(1)
            attempts = attempts + 1
        if attempts <= 5:
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