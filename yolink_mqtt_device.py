import hashlib
import json
import os
import sys
import time
import threading
import paho.mqtt.client as mqtt
import logging
import datetime
import pytz

from queue import Queue
from yolink_mqtt_class1 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

#from yolink_mqtt_client import YoLinkMQTTClient
"""
Object representation for YoLink MQTT device
"""
class YoLinkMultiOutlet(YoLinkMQTTDevice):

    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec = 3):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        startTime = str(int(time.time()*1000))
        self.dataAPI = {
                        'lastTime':startTime
                        ,'lastMessage':{}
                        ,'nbrPorts': -1
                        ,'data':{   'state':{}
                                    ,'schedules': {}
                                }

                        }


       
        self.delayList = []
        self.scheduleList = []

        self.connect_to_broker()
        self.loopTimeSec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimeSec  )
        time.sleep(2)

        self.refreshMultiOutput() # needed to get number of ports on device
        self.refreshSchedules()
        self.refreshFWversion()


    def getStateValue (self):
        temp = self.dataAPI['data']['state']['state']
        temp = temp[0:self.dataAPI['nbrPorts']]
        for port in range(len(temp)):
            if temp[port] == 'closed':
                temp[port] = 'OFF'
            elif temp[port] == 'open':
                temp[port] = 'ON'
            else:
                temp[port] = '??'
                
        return(temp)

    def getSchedules (self):
        return(self.dataAPI['data']['schedules'])  

    def getDelays (self):
        return(self.dataAPI['data']['state']['delays'])  


    '''
    def getInfoAPI(self):  
        return(self.dataAPI)
    '''
    def updateStatus(self, data):
        if 'method' in  data:
            if  (data['method'] == 'MultiOutlet.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):

                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['nbrPorts'] = len(data['data']['delays'])

                    self.dataAPI['data']['state'] = data['data']
            elif  (data['method'] == 'MultiOutlet.setState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['data']['state']['state'] = data['data']['state']
                    self.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
                   
            elif  (data['method'] == 'MultiOutlet.setDelay' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    self.dataAPI['data']['state']['delays']=data['data']['delays']
                    self.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']

            elif  (data['method'] == 'MultiOutlet.getSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):  
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['data']['schedules'] = data['data']
            elif  (data['method'] == 'MultiOutlet.setSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):  
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['data']['schedules'] = data['data']

            elif  (data['method'] == 'MultiOutlet.getVersion' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    # Need to have it workign forst - not sure what return struture will look lik
                    #self.dataAPI['data']['state']['state'].append( data['data'])
                    self.dataAPI['state']['lastTime'] = data['time']
                    self.dataAPI['lastMessage'] = data
            else:
                logging.debug('Unsupported Method passed' + str(json(data)))
        elif 'event' in data:
            if data['event'] == 'MultiOutlet.StatusChange':
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['data']['state']['state'] = data['data']['state']
                    self.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
            elif data['event'] == 'MultiOutlet.Report':
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    self.dataAPI['data']['state'] = data['data']
                    
            else :
                logging.debug('Unsupported Event passed' + str(json(data)))
                                        

    def refreshMultiOutput(self):
        return(self.refreshDevice('MultiOutlet.getState', self.updateStatus))


    def setState(self, portList, value):
        logging.debug('setMultiOutletState')
        # portlist a a listof ports being changed port range 0-7
        # vaue is state that need to change 2 (ON/OFF)
        port = 0
        for i in portList:
            port = port + pow(2, i)
        if value.upper() == 'ON':
            state = 'open'
        elif value.upper() == 'OFF':
            state = 'closed'
        else:
            logging.error('Unknows state passed')
        data={}
        data["params"] = {}
        data["params"]["chs"] =  port
        data["params"]['state'] = state

        return(self.setDevice( 'MultiOutlet.setState', data, self.updateStatus))


    def refreshSchedules(self):
        return(self.refreshDevice('MultiOutlet.getSchedules', self.updateStatus))
 
    
    def resetScheduleList(self):
        self.scheduleList = []

    def setSchedule(self, scheduleList):
        logging.debug('setMultiOutletSchedule - not currently supported')
       
        data = {}
        data["params"] = {}
        data["params"]["chs"] =  scheduleList
        #data["params"]['state'] = state
        return(self.setDevice('MultiOutlet.setSchedules', data, self.updateStatus))


    def resetDelayList (self):
        self.delayList = []

    def appedDelay(self, delay):
        nbrDelays = len(self.delayList)
        self

    def setDelay(self, delayList):
        logging.debug('setMultiOutletDelay - not currently supported')
        data={}
        nbrDelays = len(delayList)
        data["params"]["delays"] = {}
        if nbrDelays > 0:
            for delayNbr in delayList:
                data["params"]["delays"][delayNbr]={}
                data["params"]["delays"][delayNbr]['ch'] = delayList[delayNbr]['port']
                data["params"]['delays'][delayNbr]['on'] = delayList[delayNbr]['OnDelay']
                data["params"]['delays'][delayNbr]['off'] = delayList[delayNbr]['OffDelay']
        
        return(self.setDevice('MultiOutlet.setDelay', data, self.updateStatus))


    def refreshFWversion(self):
        logging.debug('refreshFWversion - not currently supported')
        #return(self.refreshDevice('MultiOutlet.getVersion',  self.updateStatus))

    def startUpgrade(self):
        logging.debug('startUpgrade - not currently supported')
    '''
    def checkStatusChanges(self):
        logging.debug('checkStatusChanges')
    '''



class YoLinkMotionSensor(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec = 3):
        self.YolinkSensor = YoLinkMQTTDevice(csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, self.updateStatus)
        self.methodList = ['MotionSensor.getState' ]
        self.eventList = ['MotionSensor.Alert' , 'MotionSensor.getState', 'MotionSensor.StatusChange']
        self.loopTimeSec = updateTimeSec

        self.eventName = 'MotionEvent'
        self.eventTime = 'Time'

        
        #self.YolinkSensor.monitorLoop(self.updateStatus, self.loopTimeSec  )
        time.sleep(2)
        self.refreshSensor()

    def refreshSensor(self):
        return(self.YolinkSensor.refreshDevice('MotionSensor.getState',  self.updateStatus, ))

    def updateStatus(self, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in self.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(self.YolinkSensor.getLastUpdate()):
                     self.YolinkSensor.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.YolinkSensor.getLastUpdate()):
                    self.YolinkSensor.updateStatusData(data)
                    eventData = {}
                    eventData[self.eventName] = self.YolinkSensor.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.YolinkSensor.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    def motionState(self):
        return(self.YolinkSensor.getState())


    def getMotionData(self):
        return(self.YolinkSensor.getState())         

'''
class YoLinkMotionSensor(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec = 3):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)

        self.methodList = ['MotionSensor.getState' ]
        self.eventList = ['MotionSensor.Alert' , 'MotionSensor.getState', 'MotionSensor.StatusChange']
        self.loopTimeSec = updateTimeSec

        self.eventName = 'MotionEvent'
        self.eventTime = 'Time'

        self.connect_to_broker()
        self.loopTimeSec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimeSec  )
        time.sleep(2)
        self.refreshSensor()

    def refreshSensor(self):
        return(self.refreshDevice('MotionSensor.getState',  self.updateStatus, ))

    def updateStatus(self, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in self.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                     self.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)
                    eventData = {}
                    eventData[self.eventName] = self.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    def motionState(self):
        return(self.getState())


    def getMotionData(self):
        return(self.dataAPI[self.deviceData])         
'''


class YoLinkTHSensor(YoLinkMQTTDevice):

    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num,updateStatus,  updateTimeSec = 3):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateStatus)
      
        self.methodList = ['THSensor.getState' ]
        self.eventList = ['THSensor.Report']
        self.tempName = 'THEvent'
        self.temperature = 'Temperature'
        self.humidity = 'Humidity'
        self.eventTime = 'Time'

        self.connect_to_broker()
        self.loopTimeSec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimeSec  )
        time.sleep(2)
        self.refreshSensor()
        
   

    def refreshSensor(self):
        logging.debug('refreshTHsensor')
        return(self.refreshDevice('THSensor.getState',  self.updateStatus, ))

    def updateStatus(self, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in self.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                     self.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)
                    eventData = {}
                    eventData[self.tempName] = self.getState()
                    eventData[self.temperature] = self.getTempValueC()
                    eventData[self.humidity] = self.getHumidityValue()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))



class YoLinkWaterSensor(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        
        self.methodList = ['LeakSensor.getState' ]
        self.eventList = ['LeakSensor.Report']
        self.waterName = 'WaterEvent'
        self.eventTime = 'Time'

        self.loopTimesec = updateTimeSec
        self.connect_to_broker()
        self.monitorLoop(self.updateStatus, self.loopTimesec  )
        time.sleep(2)
        self.refreshSensor()

    def refreshSensor(self):
        logging.debug('refreshWaterSensor')
        return(self.refreshDevice('LeakSensor.getState', self.updateStatus))


    def updateStatus(self, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in self.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                     self.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)
                    eventData = {}
                    eventData[self.waterName] = self.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    
    def probeState(self):
         return(self.getState() )

    


class YoLinkManipulator(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        startTime = str(int(time.time()*1000))
        self.dataAPI = {
                        'lastTime':startTime
                        ,'lastMessage':{}
                        ,'nbrPorts': -1
                        ,'data':{   'state':{}
                                    ,'schedules': {}
                                }

                        }
        self.maxSchedules = 6
        self.connect_to_broker()
        self.loopTimesec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimesec  )
        time.sleep(2)
        
        self.refreshState()
        self.refreshSchedules()
        self.refreshFWversion()


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





class YoLinkGarageDoorCtrl(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec):
        logging.debug('toggleGarageDoorCtrl Init') 
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        self.methodList = ['GarageDoor.toggle' ]
        self.eventList = ['GarageDoor.Report']
        self.ToggleName = 'GarageEvent'
        self.eventTime = 'Time'


        self.connect_to_broker()
        self.loopTimesec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimesec  )
        time.sleep(2)
        

    def toggleGarageDoorCtrl(self):
        logging.debug('toggleGarageDoorCtrl') 
        data={}
        return(self.setDevice( 'GarageDoor.toggle', data, self.updateStatus))

    def updateStatus(self, data):
        logging.debug(' YoLinkGarageDoorCtrl updateStatus')  
        #special case 
        if 'method' in  data:
            if  (data['method'] in self.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateGarageCtrlStatus(data)

        elif 'event' in data: # not sure events exits
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)
                    eventData = {}
                    eventData[self.ToggleName] = self.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.ToggleEventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))




class YoLinkGarageDoorSensor(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num,  updateTimeSec):
        logging.debug('YoLinkGarageDoorSensor init') 
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)

        self.methodList = ['DoorSensor.getState' ]
        self.eventList = ['DoorSensor.Report']
        self.GarageName = 'GarageEvent'
        self.eventTime = 'Time'

        self.connect_to_broker()
        self.loopTimesec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimesec  )
        time.sleep(2)
        self.refreshGarageDoorSensor()
  
    def refreshGarageDoorSensor(self):
        logging.debug('refreshGarageDoorSensor') 
        return(self.refreshDevice( 'DoorSensor.getState', self.updateStatus))


    def updateStatus(self, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in self.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                     self.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)
                    eventData = {}
                    eventData[self.GarageName] = self.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    
    def DoorState(self):
         return(self.getState())
    



class YoLinkGarageDoor(YoLinkGarageDoorSensor, YoLinkGarageDoorCtrl):

        def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_numToggle,serial_numSensor,   updateTimeSec):
            logging.debug('YoLinkGarageDoor Init') 
            YoLinkGarageDoorSensor.__init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_numSensor,   updateTimeSec)
            YoLinkGarageDoorCtrl.__init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_numToggle,   updateTimeSec)
            startTime = str(int(time.time()*1000))

        def refreshGarageDoorSensor(self):
            return YoLinkGarageDoorSensor().refreshGarageDoorSensor()   

        def toggleGarageDoorCtrl(self): 
            YoLinkGarageDoorCtrl.toggleGarageDoorCtrl()

        def getGarageDoorStatus(self):
            return(YoLinkGarageDoorSensor.getGarageDoorStaus())

        def garagDoorSensorOnline(self):
             return(YoLinkGarageDoorSensor.GaragDoorSensorOnline())

        def getGarageDoorInfoAll(self):
            return(YoLinkGarageDoorSensor.getGarageSensorAll())