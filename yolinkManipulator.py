import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)


class YoLinkManipulator(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        self.maxSchedules = 6
        self.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        self.eventList = ['StatusChange', 'Report']
        self.ManipulatorName = 'ManipulatorEvent'
        self.eventTime = 'Time'
        self.type = 'Manipulator'
        time.sleep(1)
        
        self.refreshState()
        self.refreshSchedules()
        #self.refreshFWversion()

    '''
    def refreshDelays(self):
        logging.debug('refreshManipulator')
        self.refreshDevice()
        return(self.getDelays())


    def refreshSchedules(self):
        logging.debug('Manipulator - refreshSchedules')
        return(self.refreshDevice('Manipulator.getSchedules', self.updateStatus))

    def refreshFWversion(self):
        logging.debug('Manipulator - refreshFWversion - Not supported yet')
        #return(self.refreshDevice('Manipulator.getVersion', self.updateStatus))
    '''
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
    '''

    '''
    def updateStatus(self, data):
        logging.debug(self.type + ' - updateStatus')
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
        else:
            logging.debug('updateStatus: Unsupported packet type: ' +  json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            self.deviceError(data)
    '''

    def setState(self, state):
        logging.debug(self.type+' - setState')  
        if state.lower() != 'open' and  state.lower() != 'closed':
            logging.error('Unknows state passed')
            return(False)
        data = {}
        data['params'] = {}
        data['params']['state'] = state.lower()
        return(self.setDevice( data))


    def getState(self):
        logging.debug(self.type+' - getState')
        attempts = 0
        while self.dataAPI[self.dData][self.dState]  == {} and attempts < 5:
            time.sleep(1)
            attempts = attempts + 1
        if attempts <= 5:
            if  self.dataAPI[self.dData][self.dState]['state'] == 'open':
                return('open')
            elif self.dataAPI[self.dData][self.dState]['state'] == 'closed':
                return('closed')
            else:
                return('Unkown')
        else:
            return('Unkown')
    
    def getData(self):
        return(self.getData())


