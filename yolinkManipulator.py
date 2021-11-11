import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)


class YoLinkManipulator(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)
        yolink.maxSchedules = 6
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        yolink.eventList = ['StatusChange', 'Report']
        yolink.ManipulatorName = 'ManipulatorEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'Manipulator'
        time.sleep(1)
        
        yolink.refreshState()
        yolink.refreshSchedules()
        #yolink.refreshFWversion()

    '''
    def refreshDelays(yolink):
        logging.debug('refreshManipulator')
        yolink.refreshDevice()
        return(yolink.getDelays())


    def refreshSchedules(yolink):
        logging.debug('Manipulator - refreshSchedules')
        return(yolink.refreshDevice('Manipulator.getSchedules', yolink.updateStatus))

    def refreshFWversion(yolink):
        logging.debug('Manipulator - refreshFWversion - Not supported yet')
        #return(yolink.refreshDevice('Manipulator.getVersion', yolink.updateStatus))
    '''
    '''
    def updateStatusData(yolink, data): 
        if 'online' in data[yolink.dData]:
            yolink.dataAPI[yolink.dOnline] = data[yolink.dData][yolink.dOnline]
        else:
            yolink.dataAPI[yolink.dOnline] = True
        if 'method' in data:
            for key in data[yolink.dData]:
                if key == 'delay':
                        yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][key]
                else:
                        yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key]
        else: #event
            for key in data[yolink.dData]:
                yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key]
        yolink.updateLoraInfo(data)
        yolink.updateMessageInfo(data)
    '''

    '''
    def updateStatus(yolink, data):
        logging.debug(yolink.type + ' - updateStatus')
        if data['code'] == '000000':
            if 'method' in  data:
                if  (data['method'] == 'Manipulator.getState' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)       
                elif  (data['method'] == 'Manipulator.setState' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)                          
                elif  (data['method'] == 'Manipulator.setDelay' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)       
                elif  (data['method'] == 'Manipulator.getSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateScheduleStatus(data)
                elif  (data['method'] == 'Manipulator.setSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateScheduleStatus(data)
                elif  (data['method'] == 'Manipulator.getVersion' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateFWStatus(data)
                else:
                    logging.debug('Unsupported Method passed' + json.dumps(data))                      
            elif 'event' in data:
                if data['event'] == 'Manipulator.StatusChange':
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)              
                elif data['event'] == 'Manipulator.Report':
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)                      
                else :
    
                    logging.debug('Unsupported Event passed - trying anyway' + str(json(data)))
                try:
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        if data['event'].find('chedule') >= 0 :
                            yolink.updateScheduleStatus(data)    
                        elif data['event'].find('ersion') >= 0 :
                            yolink.updateFWStatus(data)
                        else:
                            yolink.updateStatusData(data)   
                except logging.exception as E:
                    logging.debug('Unsupported event detected: ' + str(E))
        else:
            logging.debug('updateStatus: Unsupported packet type: ' +  json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            yolink.deviceError(data)
    '''

    def setState(yolink, state):
        logging.debug(yolink.type+' - setState')  
        if state.lower() != 'open' and  state.lower() != 'closed':
            logging.error('Unknows state passed')
            return(False)
        data = {}
        data['params'] = {}
        data['params']['state'] = state.lower()
        return(yolink.setDevice( data))


    def getState(yolink):
        logging.debug(yolink.type+' - getState')
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
        return(yolink.getData())


