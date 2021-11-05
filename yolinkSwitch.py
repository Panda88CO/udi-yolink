import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)


class YoLinkSwitch(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        
        self.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        self.eventList = ['StatusChange', 'Report']
        self.stateList = ['open', 'closed', 'on', 'off']
        self.ManipulatorName = 'ManipulatorEvent'
        self.eventTime = 'Time'
        self.type = 'Switch'
        time.sleep(1)
        
        self.refreshState()
        self.refreshSchedules()
        #self.refreshFWversion()



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
        if data['code'] == '000000':
            if 'method' in  data:
                if  (data['method'] == 'Manipulator.getState' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)       
                elif  (data['method'] == 'Manipulator.setState' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)                          
                elif  (data['method'] == 'Manipulator.setDelay' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)       
                elif  (data['method'] == 'Manipulator.getSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateScheduleStatus(data)
                elif  (data['method'] == 'Manipulator.setSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateScheduleStatus(data)
                elif  (data['method'] == 'Manipulator.getVersion' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateFWStatus(data)
                else:
                    logging.debug('Unsupported Method passed' + json.dumps(data))                      
            elif 'event' in data:
                if data['event'] == 'Manipulator.StatusChange':
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)              
                elif data['event'] == 'Manipulator.Report':
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)                      
                else :
                    logging.debug('Unsupported Event passed' + str(json(data)))
        else:
            self.deviceError(data)

    def setState(self, state):
        logging.debug(self.type+' - setState')
        if 'setState'  in self.methodList:          
            if state.lower() not in self.stateList:
                logging.error('Unknows state passed')
                return(False)
            if state.lower == 'on':
                state = 'open'
            if state.lower == 'off':
                state = 'closed'
            data = {}
            data['params'] = {}
            data['params']['state'] = state.lower()
            return(self.setDevice( data))
        else:
            return(False)
    

    def getState(self):
        logging.debug(self.type+' - setState')
        if  self.dataAPI[self.dState] == 'open':
            return('ON')
        else:
            return('OFF')
 