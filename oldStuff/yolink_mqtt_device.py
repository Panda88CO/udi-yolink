import json
import time


try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)


from yolink_mqtt_class import YoLinkMQTTDevice


#from yolink_mqtt_client import YoLinkMQTTClient
"""
Object representation for YoLink MQTT device
"""
class YoLinkMultiOutlet(YoLinkMQTTDevice):

    def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec = 3):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        startTime = str(int(time.time()*1000))
        yolink.dataAPI = {
                        'lastTime':startTime
                        ,'lastMessage':{}
                        ,'nbrPorts': -1
                        ,'data':{   'state':{}
                                    ,'schedules': {}
                                }

                        }


       
        yolink.delayList = []
        yolink.scheduleList = []

        yolink.connect_to_broker()
        yolink.loopTimeSec = updateTimeSec
        yolink.monitorLoop(yolink.updateStatus, yolink.loopTimeSec  )
        time.sleep(2)

        yolink.refreshMultiOutput() # needed to get number of ports on device
        yolink.refreshSchedules()
        yolink.refreshFWversion()


    def getStateValue (yolink):
        temp = yolink.dataAPI['data']['state']['state']
        temp = temp[0:yolink.dataAPI['nbrPorts']]
        for port in range(len(temp)):
            if temp[port] == 'closed':
                temp[port] = 'OFF'
            elif temp[port] == 'open':
                temp[port] = 'ON'
            else:
                temp[port] = '??'
                
        return(temp)

    def getSchedules (yolink):
        return(yolink.dataAPI['data']['schedules'])  

    def getDelays (yolink):
        return(yolink.dataAPI['data']['state']['delays'])  


    '''
    def getInfoAPI(yolink):  
        return(yolink.dataAPI)
    '''
    def updateStatus(yolink, data):
        if 'method' in  data:
            if  (data['method'] == 'MultiOutlet.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):

                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['nbrPorts'] = len(data['data']['delays'])

                    yolink.dataAPI['data']['state'] = data['data']
            elif  (data['method'] == 'MultiOutlet.setState' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['data']['state']['state'] = data['data']['state']
                    yolink.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
                   
            elif  (data['method'] == 'MultiOutlet.setDelay' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    yolink.dataAPI['data']['state']['delays']=data['data']['delays']
                    yolink.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']

            elif  (data['method'] == 'MultiOutlet.getSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):  
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['data']['schedules'] = data['data']
            elif  (data['method'] == 'MultiOutlet.setSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):  
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['data']['schedules'] = data['data']

            elif  (data['method'] == 'MultiOutlet.getVersion' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    # Need to have it workign forst - not sure what return struture will look lik
                    #yolink.dataAPI['data']['state']['state'].append( data['data'])
                    yolink.dataAPI['state']['lastTime'] = data['time']
                    yolink.dataAPI['lastMessage'] = data
            else:
                logging.debug('Unsupported Method passed' + str(json(data)))
        elif 'event' in data:
            if data['event'] == 'MultiOutlet.StatusChange':
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['data']['state']['state'] = data['data']['state']
                    yolink.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
            elif data['event'] == 'MultiOutlet.Report':
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    yolink.dataAPI['data']['state'] = data['data']
                    
            else :
                logging.debug('Unsupported Event passed' + str(json(data)))
                                        

    def refreshMultiOutput(yolink):
        return(yolink.refreshDevice('MultiOutlet.getState', yolink.updateStatus))


    def setState(yolink, portList, value):
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

        return(yolink.setDevice( 'MultiOutlet.setState', data, yolink.updateStatus))


    def refreshSchedules(yolink):
        return(yolink.refreshDevice('MultiOutlet.getSchedules', yolink.updateStatus))
 
    
    def resetScheduleList(yolink):
        yolink.scheduleList = []

    def setSchedule(yolink, scheduleList):
        logging.debug('setMultiOutletSchedule - not currently supported')
       
        data = {}
        data["params"] = {}
        data["params"]["chs"] =  scheduleList
        #data["params"]['state'] = state
        return(yolink.setDevice('MultiOutlet.setSchedules', data, yolink.updateStatus))


    def resetDelayList (yolink):
        yolink.delayList = []

    def appedDelay(yolink, delay):
        nbrDelays = len(yolink.delayList)
        yolink

    def setDelay(yolink, delayList):
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
        
        return(yolink.setDevice('MultiOutlet.setDelay', data, yolink.updateStatus))


    def refreshFWversion(yolink):
        logging.debug('refreshFWversion - not currently supported')
        #return(yolink.refreshDevice('MultiOutlet.getVersion',  yolink.updateStatus))

    def startUpgrade(yolink):
        logging.debug('startUpgrade - not currently supported')
    '''
    def checkStatusChanges(yolink):
        logging.debug('checkStatusChanges')
    '''



class YoLinkMotionSensor(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec = 3):
        yolink.YolinkSensor = YoLinkMQTTDevice(csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, yolink.updateStatus)
        yolink.methodList = ['MotionSensor.getState' ]
        yolink.eventList = ['MotionSensor.Alert' , 'MotionSensor.getState', 'MotionSensor.StatusChange']
        yolink.loopTimeSec = updateTimeSec

        yolink.eventName = 'MotionEvent'
        yolink.eventTime = 'Time'

        
        #yolink.YolinkSensor.monitorLoop(yolink.updateStatus, yolink.loopTimeSec  )
        time.sleep(2)
        yolink.refreshSensor()

    def refreshSensor(yolink):
        return(yolink.YolinkSensor.refreshDevice('MotionSensor.getState',  yolink.updateStatus, ))

    def updateStatus(yolink, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in yolink.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.YolinkSensor.getLastUpdate()):
                     yolink.YolinkSensor.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in yolink.eventList:
                if int(data['time']) > int(yolink.YolinkSensor.getLastUpdate()):
                    yolink.YolinkSensor.updateStatusData(data)
                    eventData = {}
                    eventData[yolink.eventName] = yolink.YolinkSensor.getState()
                    eventData[yolink.eventTime] = yolink.data[yolink.messageTime]
                    yolink.YolinkSensor.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    def motionState(yolink):
        return(yolink.YolinkSensor.getState())


    def getMotionData(yolink):
        return(yolink.YolinkSensor.getState())         

'''
class YoLinkMotionSensor(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec = 3):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)

        yolink.methodList = ['MotionSensor.getState' ]
        yolink.eventList = ['MotionSensor.Alert' , 'MotionSensor.getState', 'MotionSensor.StatusChange']
        yolink.loopTimeSec = updateTimeSec

        yolink.eventName = 'MotionEvent'
        yolink.eventTime = 'Time'

        yolink.connect_to_broker()
        yolink.loopTimeSec = updateTimeSec
        yolink.monitorLoop(yolink.updateStatus, yolink.loopTimeSec  )
        time.sleep(2)
        yolink.refreshSensor()

    def refreshSensor(yolink):
        return(yolink.refreshDevice('MotionSensor.getState',  yolink.updateStatus, ))

    def updateStatus(yolink, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in yolink.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                     yolink.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in yolink.eventList:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)
                    eventData = {}
                    eventData[yolink.eventName] = yolink.getState()
                    eventData[yolink.eventTime] = yolink.data[yolink.messageTime]
                    yolink.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    def motionState(yolink):
        return(yolink.getState())


    def getMotionData(yolink):
        return(yolink.dataAPI[yolink.deviceData])         
'''


class YoLinkTHSensor(YoLinkMQTTDevice):

    def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num,updateStatus,  updateTimeSec = 3):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateStatus)
      
        yolink.methodList = ['THSensor.getState' ]
        yolink.eventList = ['THSensor.Report']
        yolink.tempName = 'THEvent'
        yolink.temperature = 'Temperature'
        yolink.humidity = 'Humidity'
        yolink.eventTime = 'Time'

        yolink.connect_to_broker()
        yolink.loopTimeSec = updateTimeSec
        yolink.monitorLoop(yolink.updateStatus, yolink.loopTimeSec  )
        time.sleep(2)
        yolink.refreshSensor()
        
   

    def refreshSensor(yolink):
        logging.debug('refreshTHsensor')
        return(yolink.refreshDevice('THSensor.getState',  yolink.updateStatus, ))

    def updateStatus(yolink, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in yolink.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                     yolink.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in yolink.eventList:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)
                    eventData = {}
                    eventData[yolink.tempName] = yolink.getState()
                    eventData[yolink.temperature] = yolink.getTempValueC()
                    eventData[yolink.humidity] = yolink.getHumidityValue()
                    eventData[yolink.eventTime] = yolink.data[yolink.messageTime]
                    yolink.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))



class YoLinkWaterSensor(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        
        yolink.methodList = ['LeakSensor.getState' ]
        yolink.eventList = ['LeakSensor.Report']
        yolink.waterName = 'WaterEvent'
        yolink.eventTime = 'Time'

        yolink.loopTimesec = updateTimeSec
        yolink.connect_to_broker()
        yolink.monitorLoop(yolink.updateStatus, yolink.loopTimesec  )
        time.sleep(2)
        yolink.refreshSensor()

    def refreshSensor(yolink):
        logging.debug('refreshWaterSensor')
        return(yolink.refreshDevice('LeakSensor.getState', yolink.updateStatus))


    def updateStatus(yolink, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in yolink.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                     yolink.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in yolink.eventList:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)
                    eventData = {}
                    eventData[yolink.waterName] = yolink.getState()
                    eventData[yolink.eventTime] = yolink.data[yolink.messageTime]
                    yolink.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    
    def probeState(yolink):
         return(yolink.getState() )

    


class YoLinkManipulator(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        startTime = str(int(time.time()*1000))
        yolink.dataAPI = {
                        'lastTime':startTime
                        ,'lastMessage':{}
                        ,'nbrPorts': -1
                        ,'data':{   'state':{}
                                    ,'schedules': {}
                                }

                        }
        yolink.maxSchedules = 6
        yolink.connect_to_broker()
        yolink.loopTimesec = updateTimeSec
        yolink.monitorLoop(yolink.updateStatus, yolink.loopTimesec  )
        time.sleep(2)
        
        yolink.refreshState()
        yolink.refreshSchedules()
        yolink.refreshFWversion()


    def getState(yolink):
        logging.debug('getState')
        return(yolink.Manipulator['state']['state'])


    def refreshState(yolink):
        logging.debug('refreshManipulator')
        return(yolink.refreshDevice('Manipulator.getState', yolink.updateStatus))


    def refreshSchedules(yolink):
        logging.debug('refreshManiulatorSchedules')
        return(yolink.refreshDevice('Manipulator.getSchedules', yolink.updateStatus))

    def refreshFWversion(yolink):
        logging.debug('refreshManipulatorFWversion - Not supported yet')
        #return(yolink.refreshDevice('Manipulator.getVersion', yolink.updateStatus))


    def updateStatus(yolink, data):
        if 'method' in  data:
            if  (data['method'] == 'Manipulator.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['nbrPorts'] = len(data['data']['delay'])
                    yolink.dataAPI['data']['state'] = data['data']
            elif  (data['method'] == 'Manipulator.setState' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['data']['state']['state'] = data['data']['state']
                    yolink.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
                   
            elif  (data['method'] == 'Manipulator.setDelay' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    yolink.dataAPI['data']['state']['delay']=data['data']['delay']
                    yolink.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']

            elif  (data['method'] == 'Manipulator.getSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):  
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['data']['schedules'] = data['data']
            elif  (data['method'] == 'Manipulator.setSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):  
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['data']['schedules'] = data['data']

            elif  (data['method'] == 'Manipulator.getVersion' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    # Need to have it workign forst - not sure what return struture will look lik
                    #yolink.dataAPI['data']['state']['state'].append( data['data'])
                    yolink.dataAPI['state']['lastTime'] = data['time']
                    yolink.dataAPI['lastMessage'] = data
            else:
                logging.debug('Unsupported Method passed' + str(json(data)))
        elif 'event' in data:
            if data['event'] == 'Manipulator.StatusChange':
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['data']['state']['state'] = data['data']['state']
                    yolink.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
            elif data['event'] == 'Manipulator.Report':
                if int(data['time']) > int(yolink.dataAPI['lastTime']):
                    yolink.dataAPI['lastMessage'] = data
                    yolink.dataAPI['lastTime'] = data['time']
                    yolink.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    yolink.dataAPI['data']['state'] = data['data']
                    
            else :
                logging.debug('Unsupported Event passed' + str(json(data)))



    '''
    def updateStatus(yolink, data):
        logging.debug('updateStatus') 
        if 'method' in  data:
            if  (data['method'] == 'Manipulator.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.Manipulator['state']['lastTime']):
                    yolink.Manipulator['state']['state'] = data['data']['state']
                    yolink.Manipulator['state']['lastTime'] = str(data['time'])
                    yolink.Manipulator['status']['battery'] = data['data']['battery']               
                    yolink.Manipulator['status']['FWvers'] = data['data']['version']
                    yolink.Manipulator['status']['signaldB'] =  data['data']['loraInfo']['signal']    
                    yolink.Manipulator['status']['timeZone']= data['data']['tz']
                    yolink.Manipulator['status']['lastTime'] = str(data['time'])
                    if 'delay' in data['data']:
                        channel = data['data']['delay']['ch']
                        yolink.Manipulator['delays'][channel]= {}
                        if 'on' in data['data']['delay']:
                            yolink.Manipulator['delays'][channel]= {'onTimeLeft':data['data']['delay']['on']}
                        if 'off' in data['data']['delay']:
                            yolink.Manipulator['delays'][channel]= {'offTimeLeft':data['data']['delay']['off']}

                    else:
                        yolink.Manipulator['delays']= {'lastTime':data['time']}

            elif (data['method'] == 'Manipulator.getSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.Manipulator['schedules']['lastTime']):
                    yolink.Manipulator['schedules']['lastTime'] = str(data['time'])
                    yolink.scheduleList = {}
                    for index in data['data']:
                        yolink.Manipulator['schedules'][index] = {}
                        yolink.Manipulator['schedules'][index]['isValid'] = data['data'][index]['isValid']
                        yolink.Manipulator['schedules'][index]['index'] = data['data'][index]['index']
                        yolink.Manipulator['schedules'][index]['onTime'] = data['data'][index]['on']
                        yolink.Manipulator['schedules'][index]['offTime'] = data['data'][index]['off']
                        week =  data['data'][index]['week']
                        yolink.Manipulator['schedules'][index]['days'] = yolink.maskToDays(week)
                                               
                        yolink.scheduleList[ yolink.Manipulator['schedules'][index]['index'] ]= {}
                        for key in yolink.Manipulator['schedules'][index]:
                            yolink.scheduleList[ yolink.Manipulator['schedules'][index]['index']] = yolink.Manipulator['schedules'][index][key]

                        

            elif (data['method'] == 'Manipulator.getVersion' and  data['code'] == '000000'):  
                 if int(data['time']) > int(yolink.Manipulator['status']['lastTime']):
                    yolink.Manipulator['status']['lastTime'] = str(data['time'])
        elif 'event' in data:
            if int(data['time']) > int(yolink.Manipulator['state']['lastTime']):
                yolink.Manipulator['state']['state'] = data['data']['state']
                yolink.Manipulator['state']['lastTime'] = str(data['time'])
                yolink.Manipulator['status']['battery'] = data['data']['battery']             
                yolink.Manipulator['status']['signaldB'] =  data['data']['loraInfo']['signal']       
                yolink.Manipulator['status']['lastTime'] = str(data['time'])
        else:
            logging.error('unsupported data')
    '''

    def setState(yolink, state):
        logging.debug('setManipulatorState')
        if state != 'open' and  state != 'closed':
            logging.error('Unknows state passed')
            return(False)
        data = {}
        data['params'] = {}
        data['params']['state'] = state
        return(yolink.setDevice( 'Manipulator.setState', data, yolink.updateStatus))

    def setDelay(yolink,delayList):
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
        return(yolink.setDevice( 'Manipulator.setDelay', data, yolink.updateStatus))


    def resetSchedules(yolink):
        logging.debug('resetSchedules')
        yolink.scheduleList = {}

    def activateSchedules(yolink, index, Activated):
        logging.debug('activateSchedules')
        if index in yolink. scheduleList:
            if Activated:
                yolink.scheduleList[index]['isValid'] = 'Enabled'
            else:
                yolink.scheduleList[index]['isValid'] = 'Disabled'
            return(True)
        else:
            return(False)


    def addSchedule(yolink, schedule):
        logging.debug('addSchedule')
        if 'days' and ('onTime' or 'offTime') and 'isValid' in schedule:    
            index = 0
            while  index in yolink.scheduleList:
                index=index+1
            if index < yolink.maxSchedules:
                yolink.scheduleList[index] = schedule
                return(index)
        return(-1)
            
    def deleteSchedule(yolink, index):
        logging.debug('addSchedule')       
        if index in yolink.scheduleList:
            yolink.scheduleList.pop(1)
            return(True)
        else:
            return(False)

    def transferSchedules(yolink):
        logging.debug('transferSchedules - does not seem to work yet')
        data = {}

        for index in yolink.scheduleList:
            data[index] = {}
            data[index]['index'] = index
            if yolink.scheduleList[index]['isValid'] == 'Enabled':
                data[index]['isValid'] = True
            else:
                data[index]['isValid'] = False
            if 'onTime' in yolink.scheduleList[index]:
                data[index]['on'] = yolink.scheduleList[index]['onTime']
            else:
                data[index]['on'] = '25:0'
            if 'offTime' in yolink.scheduleList[index]:
                data[index]['off'] = yolink.scheduleList[index]['offTime'] 
            else:
                data[index]['off'] = '25:0'
            data[index]['week'] = yolink.daysToMask(yolink.scheduleList[index]['days'])

        return(yolink.setDevice( 'Manipulator.setSchedules', data, yolink.updateStatus))





class YoLinkGarageDoorCtrl(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec):
        logging.debug('toggleGarageDoorCtrl Init') 
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        yolink.methodList = ['GarageDoor.toggle' ]
        yolink.eventList = ['GarageDoor.Report']
        yolink.ToggleName = 'GarageEvent'
        yolink.eventTime = 'Time'


        yolink.connect_to_broker()
        yolink.loopTimesec = updateTimeSec
        yolink.monitorLoop(yolink.updateStatus, yolink.loopTimesec  )
        time.sleep(2)
        

    def toggleGarageDoorCtrl(yolink):
        logging.debug('toggleGarageDoorCtrl') 
        data={}
        return(yolink.setDevice( 'GarageDoor.toggle', data, yolink.updateStatus))

    def updateStatus(yolink, data):
        logging.debug(' YoLinkGarageDoorCtrl updateStatus')  
        #special case 
        if 'method' in  data:
            if  (data['method'] in yolink.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateGarageCtrlStatus(data)

        elif 'event' in data: # not sure events exits
            if data['event'] in yolink.eventList:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)
                    eventData = {}
                    eventData[yolink.ToggleName] = yolink.getState()
                    eventData[yolink.eventTime] = yolink.data[yolink.messageTime]
                    yolink.ToggleEventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))




class YoLinkGarageDoorSensor(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num,  updateTimeSec):
        logging.debug('YoLinkGarageDoorSensor init') 
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)

        yolink.methodList = ['DoorSensor.getState' ]
        yolink.eventList = ['DoorSensor.Report']
        yolink.GarageName = 'GarageEvent'
        yolink.eventTime = 'Time'

        yolink.connect_to_broker()
        yolink.loopTimesec = updateTimeSec
        yolink.monitorLoop(yolink.updateStatus, yolink.loopTimesec  )
        time.sleep(2)
        yolink.refreshGarageDoorSensor()
  
    def refreshGarageDoorSensor(yolink):
        logging.debug('refreshGarageDoorSensor') 
        return(yolink.refreshDevice( 'DoorSensor.getState', yolink.updateStatus))


    def updateStatus(yolink, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in yolink.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                     yolink.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in yolink.eventList:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)
                    eventData = {}
                    eventData[yolink.GarageName] = yolink.getState()
                    eventData[yolink.eventTime] = yolink.data[yolink.messageTime]
                    yolink.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    
    def DoorState(yolink):
         return(yolink.getState())
    



class YoLinkGarageDoor(YoLinkGarageDoorSensor, YoLinkGarageDoorCtrl):

        def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_numToggle,serial_numSensor,   updateTimeSec):
            logging.debug('YoLinkGarageDoor Init') 
            YoLinkGarageDoorSensor.__init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_numSensor,   updateTimeSec)
            YoLinkGarageDoorCtrl.__init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_numToggle,   updateTimeSec)
            startTime = str(int(time.time()*1000))

        def refreshGarageDoorSensor(yolink):
            return YoLinkGarageDoorSensor().refreshGarageDoorSensor()   

        def toggleGarageDoorCtrl(yolink): 
            YoLinkGarageDoorCtrl.toggleGarageDoorCtrl()

        def getGarageDoorStatus(yolink):
            return(YoLinkGarageDoorSensor.getGarageDoorStaus())

        def garagDoorSensorOnline(yolink):
             return(YoLinkGarageDoorSensor.GaragDoorSensorOnline())

        def getGarageDoorInfoAll(yolink):
            return(YoLinkGarageDoorSensor.getGarageSensorAll())