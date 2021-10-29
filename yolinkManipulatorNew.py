import json
import time
import logging

from yolink_mqtt_class1 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)


class YoLinkManipulator(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        self.maxSchedules = 6
        self.methodList = []
        self.eventList = []
        self.ManipulatorName = 'ManipulatorEvent'
        self.eventTime = 'Time'
        time.sleep(1)
        
        self.refreshState()
        self.refreshSchedules()
        self.refreshFWversion()

    '''
    def getState(self):
        logging.debug('getState')
        return(self.Manipulator['state']['state'])


    def refreshState(self):
        logging.debug('refreshManipulator')
        return(self.refreshDevice('Manipulator.getState', self.updateStatus))


    def refreshSchedules(self):
        logging.debug('refreshManiulatorSchedules')
        return(self.refreshDevice('Manipulator.getSchedules', self.updateStatus))

    def refreshFWversion(self):
        logging.debug('refreshManipulatorFWversion - Not supported yet')
        #return(self.refreshDevice('Manipulator.getVersion', self.updateStatus))

    '''
    
    def updateStatus(self, data):
        if 'method' in  data:
            if  (data['method'] == 'Manipulator.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['nbrPorts'] = len(data['data']['delay'])
                    self.dataAPI['data']['state'] = data['data']
            elif  (data['method'] == 'Manipulator.setState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['data']['state']['state'] = data['data']['state']
                    self.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
                   
            elif  (data['method'] == 'Manipulator.setDelay' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    self.dataAPI['data']['state']['delay']=data['data']['delay']
                    self.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']

            elif  (data['method'] == 'Manipulator.getSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):  
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['data']['schedules'] = data['data']
            elif  (data['method'] == 'Manipulator.setSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):  
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['data']['schedules'] = data['data']

            elif  (data['method'] == 'Manipulator.getVersion' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    # Need to have it workign forst - not sure what return struture will look lik
                    #self.dataAPI['data']['state']['state'].append( data['data'])
                    self.dataAPI['state']['lastTime'] = data['time']
                    self.dataAPI['lastMessage'] = data
            else:
                logging.debug('Unsupported Method passed' + str(json(data)))
        elif 'event' in data:
            if data['event'] == 'Manipulator.StatusChange':
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['data']['state']['state'] = data['data']['state']
                    self.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
            elif data['event'] == 'Manipulator.Report':
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    self.dataAPI['data']['state'] = data['data']
                    
            else :
                logging.debug('Unsupported Event passed' + str(json(data)))



    '''
    def updateStatus(self, data):
        logging.debug('updateStatus') 
        if 'method' in  data:
            if  (data['method'] == 'Manipulator.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.Manipulator['state']['lastTime']):
                    self.Manipulator['state']['state'] = data['data']['state']
                    self.Manipulator['state']['lastTime'] = str(data['time'])
                    self.Manipulator['status']['battery'] = data['data']['battery']               
                    self.Manipulator['status']['FWvers'] = data['data']['version']
                    self.Manipulator['status']['signaldB'] =  data['data']['loraInfo']['signal']    
                    self.Manipulator['status']['timeZone']= data['data']['tz']
                    self.Manipulator['status']['lastTime'] = str(data['time'])
                    if 'delay' in data['data']:
                        channel = data['data']['delay']['ch']
                        self.Manipulator['delays'][channel]= {}
                        if 'on' in data['data']['delay']:
                            self.Manipulator['delays'][channel]= {'onTimeLeft':data['data']['delay']['on']}
                        if 'off' in data['data']['delay']:
                            self.Manipulator['delays'][channel]= {'offTimeLeft':data['data']['delay']['off']}

                    else:
                        self.Manipulator['delays']= {'lastTime':data['time']}

            elif (data['method'] == 'Manipulator.getSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(self.Manipulator['schedules']['lastTime']):
                    self.Manipulator['schedules']['lastTime'] = str(data['time'])
                    self.scheduleList = {}
                    for index in data['data']:
                        self.Manipulator['schedules'][index] = {}
                        self.Manipulator['schedules'][index]['isValid'] = data['data'][index]['isValid']
                        self.Manipulator['schedules'][index]['index'] = data['data'][index]['index']
                        self.Manipulator['schedules'][index]['onTime'] = data['data'][index]['on']
                        self.Manipulator['schedules'][index]['offTime'] = data['data'][index]['off']
                        week =  data['data'][index]['week']
                        self.Manipulator['schedules'][index]['days'] = self.maskToDays(week)
                                               
                        self.scheduleList[ self.Manipulator['schedules'][index]['index'] ]= {}
                        for key in self.Manipulator['schedules'][index]:
                            self.scheduleList[ self.Manipulator['schedules'][index]['index']] = self.Manipulator['schedules'][index][key]

                        

            elif (data['method'] == 'Manipulator.getVersion' and  data['code'] == '000000'):  
                 if int(data['time']) > int(self.Manipulator['status']['lastTime']):
                    self.Manipulator['status']['lastTime'] = str(data['time'])
        elif 'event' in data:
            if int(data['time']) > int(self.Manipulator['state']['lastTime']):
                self.Manipulator['state']['state'] = data['data']['state']
                self.Manipulator['state']['lastTime'] = str(data['time'])
                self.Manipulator['status']['battery'] = data['data']['battery']             
                self.Manipulator['status']['signaldB'] =  data['data']['loraInfo']['signal']       
                self.Manipulator['status']['lastTime'] = str(data['time'])
        else:
            logging.error('unsupported data')
    '''

    def setState(self, state):
        logging.debug('setManipulatorState')
        if state != 'open' and  state != 'closed':
            logging.error('Unknows state passed')
            return(False)
        data = {}
        data['params'] = {}
        data['params']['state'] = state
        return(self.setDevice( 'Manipulator.setState', data, self.updateStatus))

    def setDelay(self,delayList):
        logging.debug('setManipulatorDelay')
        data = {}
        data['params'] = {} 
        if 'delayOn' in delayList:
            data['params']['delayOn'] = delayList['delayOn']
        #else:
        #    data['params']['delayOn'] = '25:0'
        if 'delayOff' in delayList:
            data['params']['delayOff'] = delayList['delayOff']   
        #else:
        #    data['params']['delayOff'] = '25:0'
        return(self.setDevice( 'Manipulator.setDelay', data, self.updateStatus))


    def resetSchedules(self):
        logging.debug('resetSchedules')
        self.scheduleList = {}

    def activateSchedules(self, index, Activated):
        logging.debug('activateSchedules')
        if index in self. scheduleList:
            if Activated:
                self.scheduleList[index]['isValid'] = 'Enabled'
            else:
                self.scheduleList[index]['isValid'] = 'Disabled'
            return(True)
        else:
            return(False)


    def addSchedule(self, schedule):
        logging.debug('addSchedule')
        if 'days' and ('onTime' or 'offTime') and 'isValid' in schedule:    
            index = 0
            while  index in self.scheduleList:
                index=index+1
            if index < self.maxSchedules:
                self.scheduleList[index] = schedule
                return(index)
        return(-1)
            
    def deleteSchedule(self, index):
        logging.debug('addSchedule')       
        if index in self.scheduleList:
            self.scheduleList.pop(1)
            return(True)
        else:
            return(False)

    def transferSchedules(self):
        logging.debug('transferSchedules - does not seem to work yet')
        data = {}

        for index in self.scheduleList:
            data[index] = {}
            data[index]['index'] = index
            if self.scheduleList[index]['isValid'] == 'Enabled':
                data[index]['isValid'] = True
            else:
                data[index]['isValid'] = False
            if 'onTime' in self.scheduleList[index]:
                data[index]['on'] = self.scheduleList[index]['onTime']
            else:
                data[index]['on'] = '25:0'
            if 'offTime' in self.scheduleList[index]:
                data[index]['off'] = self.scheduleList[index]['offTime'] 
            else:
                data[index]['off'] = '25:0'
            data[index]['week'] = self.daysToMask(self.scheduleList[index]['days'])

        return(self.setDevice( 'Manipulator.setSchedules', data, self.updateStatus))



