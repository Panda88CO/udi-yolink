
import time
import json
import threading

from  datetime import datetime
from dateutil.tz import *

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)



import paho.mqtt.client as mqtt
from queue import Queue
from yolink_mqtt_client import YoLinkMQTTClient

"""
Object representation for YoLink MQTT Client
"""
class YoLinkMQTTDevice(object):
    def __init__(yolink, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback ):
        #super().__init__( yolink_URL, csid, csseckey, deviceInfo)
        #yolink.callback = callback
        #yolink.build_device_api_request_data()
        #yolink.enable_device_api()
        #{"deviceId": "d88b4c1603007966", "deviceUDID": "75addd8e21394d769b85bc292c553275", "name": "YoLink Hub", "token": "118347ae-d7dc-49da-976b-16fae28d8444", "type": "Hub"}
        yolink.deviceInfo = deviceInfo
        yolink.deviceId = yolink.deviceInfo['deviceId']
        yolink.delayList = []

        yolink.yolinkMQTTclient = YoLinkMQTTClient(csName, csid, csseckey, mqtt_URL, mqtt_port,  yolink.deviceId , callback )

        yolink.yolink_URL = yolink_URL
        yolink.mqtt_url = mqtt_URL

        yolink.daysOfWeek = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        yolink.type = ''
        
        
        yolink.maxSchedules = 6
        yolink.methodList = []
        yolink.eventList = []
        yolink.lastUpdate = 'lastTime'
        yolink.lastMessage = 'lastMessage'
        yolink.dOnline = 'online'
        yolink.dData = 'data'
        yolink.dState= 'state'
        yolink.dSchedule = 'schedules'
        yolink.dDelays = 'delays'
        yolink.dDelay = 'delay'
        yolink.messageTime = 'time'
        yolink.forceStop = False
        yolink.eventSupport = False # Support adding to EventQueue

        
        yolink.dataAPI = {
                        'lastTime':str(int(time.time()*1000))
                        ,'lastMessage':{}
                        ,'online':None
                        ,'data':{ 'state':{} }
                        }
   
        yolink.eventQueue = Queue()
        #yolink.mutex = threading.Lock()
        yolink.timezoneOffsetSec = yolink.timezoneOffsetSec()
        yolink.yolinkMQTTclient.connect_to_broker()
        #yolink.loopTimeSec = updateTimeSec
    
        #yolink.updateInterval = 3
        yolink.messagePending = False
    def shut_down(yolink):
        yolink.yolinkMQTTclient.shut_down()
   
    def deviceError(yolink, data):
        logging.debug(yolink.type+' - deviceError')
        yolink.dataAPI[yolink.dOnline] = False
        # may need to add more error handling 

    def refreshDevice(yolink):
        logging.debug(yolink.type+' - refreshDevice')
        if 'getState' in yolink.methodList:
            methodStr = yolink.type+'.getState'
            #logging.debug(methodStr)  
            data = {}
            data['time'] = str(int(time.time())*1000)
            data['method'] = methodStr
            data["targetDevice"] =  yolink.deviceInfo['deviceId']
            data["token"]= yolink.deviceInfo['token']
            logging.debug  ('refreshDevice')
            yolink.yolinkMQTTclient.publish_data(data)
            time.sleep(2)
              
    def setDevice(yolink,  data):
        logging.debug(yolink.type+' - setDevice')
        worked = False
        if 'setState' in yolink.methodList:
            methodStr = yolink.type+'.setState'
            worked = True
        elif 'toggle' in yolink.methodList:
            methodStr = yolink.type+'.toggle'
            worked = True
        data['time'] = str(int(time.time())*1000)
        data['method'] = methodStr
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        if worked:
            yolink.yolinkMQTTclient.publish_data(data)
            return(True)
        else:
            return(False)

    def getValue(yolink,key): 
        logging.debug(yolink.type+' -     def getValue(yolink,key): ')
        attempts = 1
        while key not in yolink.dataAPI[yolink.dData] and attempts <3:
            time.sleep(1)
            attempts = attempts + 1
        if key in yolink.dataAPI[yolink.dData]:
            return(yolink.dataAPI[yolink.dData][key])
        else:
            return('NA')

    def getStateValue(yolink, key):
        logging.debug(yolink.type+' - getStateValue')
        try:
            attempts = 1
            while key not in yolink.dataAPI[yolink.dData][yolink.dState] and attempts <3:
                time.sleep(1)
                attempts = attempts + 1
            if key in yolink.dataAPI[yolink.dData][yolink.dState]:
                return(yolink.dataAPI[yolink.dData][yolink.dState][key])
            else:
                return('NA')
        except Exception as e:
            logging.debug('getData exceptiom: {}'.format(e) )
            return(None)
  

    def getOnlineStatus(yolink):
        logging.debug(yolink.type+' - getOnlineStatus')
        if 'online' in yolink.dataAPI:
            return(yolink.dataAPI['online'])
        else:
            return(False)

    def onlinestatus(yolink):
        return(yolink.getOnlineStatus())

    def refreshDelays(yolink):
        logging.debug(yolink.type+' - refreshDelays')
        yolink.refreshDevice()
        return(yolink.getDelays())
    


    def updateDelayData(yolink, data):
        if not data[yolink.dData]: # No data returned
            yolink.dataAPI[yolink.dOnline] = False
        elif 'online' in data[yolink.dData]:
            yolink.dataAPI[yolink.dOnline] = data[yolink.dData][yolink.dOnline]
        else:
            yolink.dataAPI[yolink.dOnline] = True
        
        if 'event' in data:
            if  yolink.dataAPI[yolink.dOnline]:
                tmp =  {}
                for key in data[yolink.dData]:
                    if key == 'delayOn':
                        tmp['on'] = data[yolink.dData][key]
                    elif key == 'delayOff':
                        tmp['off'] = data[yolink.dData][key] 
                    else:
                        tmp[key] =  data[yolink.dData][key] 
                yolink.dataAPI[yolink.dData][yolink.dDelays]= tmp
            yolink.updateLoraInfo(data)
            yolink.updateMessageInfo(data)

    def updateCallbackStatus(yolink, data, eventSupport = False):
        logging.debug(yolink.type+' - updateCallbackStatus')
        logging.debug(data)

        if 'method' in  data:
            if data['code'] == '000000':
                if  ('.getState' in data['method'] and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)       
                elif  ('.setState' in data['method'] and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)                          
                elif  ('.setDelay'  in data['method'] and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateDelayData(data)       
                elif  ('.getSchedules'  in data['method'] and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateScheduleStatus(data)
                elif  ('.setSchedules' in data['method'] and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateScheduleStatus(data)
                elif  ('.getVersion' in data['method'] and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateFWStatus(data)
                else:
                    logging.debug('Unsupported Method passed' + str(json.dumps(data)))    
            else:
                yolink.deviceError(data)
                logging.error(yolink.type+ ': ' + data['desc'])
        elif 'event' in data:
            if '.StatusChange' in data['event']:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)              
            elif '.Report' in data['event']:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)  
            elif '.getState' in data['event']:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)  
            elif '.setState' in data['event']:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)                      
            elif '.getSchedules' in data['event']:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateScheduleStatus(data)   
            elif '.Alert' in data['event']:         
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateScheduleStatus(data)  
            elif '.setDelay' in data['event']:         
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateDelayData(data)                    
            else:
                logging.debug('Unsupported Event passed - trying anyway' )
                logging.debug(data)
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)  
                    try:
                        if int(data['time']) > int(yolink.getLastUpdate()) and data['data'] != {}:
                            if data['event'].find('chedule') >= 0 :
                                yolink.updateScheduleStatus(data)    
                            elif data['event'].find('ersion') >= 0 :
                                yolink.updateFWStatus(data)
                            else:
                                yolink.updateStatusData(data)   
                        else:
                            yolink.dataAPI[yolink.dOnline] = False
                            logging.error('Device appears offline: '+ data['desc'])
                    except logging.exception as E:
                        logging.debug('Unsupported event detected: ' + str(E))
            if eventSupport:
                yolink.eventQueue.put(data['event']) 
        else:
            logging.debug('updateStatus: Unsupported packet type: ' +  json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
    '''
    def updateCallbackStatus(yolink, data, eventSupport = False):
        logging.debug(yolink.type+' - updateCallbackStatus')
        logging.debug(data)
        if 'method' in  data:
            if data['code'] == '000000':
                if  (data['method'] == yolink.type +'.getState' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)       
                elif  (data['method'] == yolink.type +'.setState' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)                          
                elif  (data['method'] == yolink.type +'.setDelay' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateDelayData(data)       
                elif  (data['method'] == yolink.type +'.getSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateScheduleStatus(data)
                elif  (data['method'] == yolink.type +'.setSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateScheduleStatus(data)
                elif  (data['method'] == yolink.type +'.getVersion' and  data['code'] == '000000'):
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateFWStatus(data)
                else:
                    logging.debug('Unsupported Method passed' + str(json.dumps(data)))     
            else:
                yolink.deviceError(data)
        elif 'event' in data:
            if data['event'] == yolink.type +'.StatusChange' :
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)              
            elif data['event'] == yolink.type +'.Report':
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)  
            elif data['event'] == yolink.type +'.getState':
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)  
            elif data['event'] == yolink.type +'.setState':
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)                      
            elif data['event'] == yolink.type +'.getSchedules':
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateScheduleStatus(data)   
            elif data['event'] == yolink.type +'.Alert':         
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateScheduleStatus(data)  
            elif data['event'] == yolink.type +'.setDelay':         
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateDelayData(data)                    
            else:
                logging.debug('Unsupported Event passed - trying anyway' )
                logging.debug(data)
                logging.debug(data)
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
            if eventSupport:
                yolink.eventQueue.put(data['event']) 
        else:
            logging.debug('updateStatus: Unsupported packet type: ' +  json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
    '''    

    def setDelay(yolink, delayList):
        logging.debug(yolink.type+' - setDelay')
        data = {}
        data['params'] = {}
        if len(delayList) == 0:  
            data['params']['delayOn'] = 0
            data['params']['delayOff'] = 0
        elif len(delayList) == 1:
            for key in delayList[0]:
                if key.lower() == 'delayon' or key.lower() == 'on' :
                    data['params']['delayOn'] = delayList[0][key]
                elif key.lower() == 'delayoff'or key.lower() == 'off' :
                    data['params']['delayOff'] = delayList[0][key] 
                else:
                    logging.debug('Wrong parameter passed - must be overwritten to support multi devices  : ' + str(key))
        else:
            logging.debug('Must overwrite to support multi devices for now')
            return(False)
        data['time'] = str(int(time.time())*1000)
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.yolinkMQTTclient.publish_data( data)
        return(True)

    def resetScheduleList(yolink):
        yolink.scheduleList = []


    def prepareScheduleData(yolink):
        logging.debug(yolink.type + '- prepareScheduleData')
        nbrSchedules = len(yolink.scheduleList)
        if nbrSchedules <= yolink.maxSchedules:
            tmpData = {}
            for schedule in range (0, nbrSchedules):
                tmpData[schedule] = {}

                tmpData[schedule]['isValid'] = yolink.scheduleList[schedule]['isValid']
                tmpData[schedule]['index'] = yolink.scheduleList[schedule]['index']
                if 'on' in yolink.scheduleList[schedule]:
                    tmpData[schedule]['on'] = yolink.scheduleList[schedule]['on']
                else:
                    tmpData[schedule]['on'] = '25:0'
                if 'off' in yolink.scheduleList[schedule]:
                    tmpData[schedule]['off'] = yolink.scheduleList[schedule]['off']
                else:
                    tmpData[schedule]['off'] = '25:0'
                tmpData[schedule]['week'] = yolink.daysToMask(yolink.scheduleList[schedule]['week'])
            return(tmpData)
        else:
            logging.error('More than '+str(yolink.maxSchedules)+' defined')
            return(None)
        
    def refreshSchedules(yolink):
        logging.debug(yolink.type + '- refreshSchedules')

        if 'getSchedules' in yolink.methodList:
            methodStr = yolink.type+'.getSchedules'
            #logging.debug(methodStr)  
            data = {}
            data['time'] = str(int(time.time())*1000)
            data['method'] = methodStr
            data["targetDevice"] =  yolink.deviceInfo['deviceId']
            data["token"]= yolink.deviceInfo['token']
            yolink.yolinkMQTTclient.publish_data(data)
            

    def getSchedules(yolink):
        logging.debug(yolink.type + '- getSchedules')
        yolink.refreshSchedules()
        nbrSchedules  = len(yolink.dataAPI[yolink.dData][yolink.dSchedule])
        temp = {}
        yolink.scheduleList = []
        for schedule in range(0,nbrSchedules):
            temp[schedule] = {}
            for key in yolink.dataAPI[yolink.dData][yolink.dSchedule][str(schedule)]:
                if key == 'week':
                    days = yolink.maskToDays(yolink.dataAPI[yolink.dData][yolink.dSchedule][str(schedule)][key])
                    temp[schedule][key]= days
                elif yolink.dataAPI[yolink.dData][yolink.dSchedule][str(schedule)][key] == '25:0':
                    #temp[schedule].pop(key)
                    pass
                else:
                    temp[schedule][key] = yolink.dataAPI[yolink.dData][yolink.dSchedule][str(schedule)][key]
            temp[schedule]['index'] = schedule   
            yolink.scheduleList.append(temp[schedule])
        return(temp)



    def setSchedules(yolink):
        logging.debug(yolink.type + '- setSchedule')
        data = yolink.prepareScheduleData()        
        
        data['time'] = str(int(time.time())*1000)
        data['method'] = yolink.type+'.setSchedules'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        yolink.yolinkMQTTclient.publish_data(data)
        time.sleep(1)

    
    def activateSchedules(yolink, index, Activate):
        logging.debug(yolink.type + 'activateSchedules')
        for schedule  in yolink.scheduleList:
            if schedule['index'] == index:        
                yolink.scheduleList[index]['isValid'] = Activate
                return(True)
        else:
            return(False)

    def addSchedule(yolink, schedule):
        logging.debug(yolink.type + 'addSchedule')
        tmp = schedule
        if 'week' and ('on' or 'off') and 'isValid' in schedule:    
            indexList = []
            for sch in yolink.scheduleList:
                indexList.append(sch['index'])
            index = 0
            while index in indexList and index <yolink.maxSchedules:
                index = index+ 1
            if index < yolink.maxSchedules:
                tmp['index'] = index
                yolink.scheduleList.append(tmp)
            return(index)
        return(-1)
            
    def deleteSchedule(yolink, index):
        logging.debug(yolink.type + 'addSchedule')       
        sch = 0 
       
        while sch < len(yolink.scheduleList):
            if yolink.scheduleList[sch]['index'] == index:
                yolink.scheduleList.pop(sch)
                return(True)
            else:
                sch = sch + 1
        return(False)

    
    def resetSchedules(yolink):
        logging.debug(yolink.type + 'resetSchedules')
        yolink.scheduleList = {}

    def bool2Nbr(yolink, bool):
        if bool:
            return(1)
        else:
            return(0)

    '''
    def transferSchedules(yolink):
        logging.debug(yolink.type + 'transferSchedules - does not seem to work yet')
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
    '''

    '''
 
    def refreshFWversion(yolink):
        logging.debug(yolink.type+' - refreshFWversion - Not supported yet')
        #return(yolink.refreshDevice('Manipulator.getVersion', yolink.updateStatus))

   '''


    def daysToMask (yolink, dayList):
        daysValue = 0 
        i = 0
        for day in yolink.daysOfWeek:
            if day in dayList:
                daysValue = daysValue + pow(2,i)
            i = i+1
        return(daysValue)

    def maskToDays(yolink, daysValue):
        daysList = []
        for i in range(0,7):
            mask = pow(2,i)
            if (daysValue & mask) != 0 :
                daysList.append(yolink.daysOfWeek[i])
        return(daysList)

    def updateNbrPorts(yolink, data):
        if 'delays' in data['data']:
            yolink.dataAPI['nbrPorts'] = len(data['data']['delays'])  
        return(yolink.dataAPI['nbrPorts'])

    def getNbrPorts(yolink):
        if 'nbrPorts' in yolink.dataAPI:
            return(yolink.dataAPI['nbrPorts'] )
        else:
            return (0)

    def setOnline(yolink, data):
        if 'online' in data[yolink.dData]:
            yolink.dataAPI[yolink.dOnline] = data[yolink.dData][yolink.dOnline]
        else:
            yolink.dataAPI[yolink.dOnline] = True

    def setNbrPorts(yolink, data):
        if not 'nbrPorts' in yolink.dataAPI:
            if 'delays' in data['data']:
                yolink.nbrPorts  = len(data['data']['delays'])
                yolink.dataAPI['nbrPorts'] = yolink.nbrPorts 
            else:
                yolink.dataAPI['nbrPorts'] = -1 # to handle case where event happens before first poll - will be updated right after this

    def updateLoraInfo(yolink, data):
        if yolink.dState in data[yolink.dData]:
            if 'loraInfo' in data[yolink.dData][yolink.dState]:
                yolink.dataAPI[yolink.dData][yolink.dState]['loraInfo']= data[yolink.dData]['loraInfo']

    def updateMessageInfo(yolink, data):
        yolink.dataAPI[yolink.lastUpdate] = data[yolink.messageTime]
        yolink.dataAPI[yolink.lastMessage] = data
    '''
    def updateMultiStatusData (yolink, data):
        yolink.setOnline(data)
        yolink.setNbrPorts(data)
        yolink.updateLoraInfo(data)
        if 'method' in data:
            #for key in range(0, yolink.nbrPorts):
            yolink.dataAPI[yolink.dData][yolink.dState] = data[yolink.dData][yolink.dState][0:yolink.nbrPorts]
                
            if 'delays'in data[yolink.dData]:
                yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][yolink.dDelays]
                    #yolink.dataAPI[yolink.dData][yolink.dDelays]=[]
                    #test = data[yolink.dData][yolink.dDelays][key]
                    #yolink.dataAPI[yolink.dData][yolink.dDelays][key] = test
        else: #event
            yolink.dataAPI[yolink.dData][yolink.dState] = data[yolink.dData][yolink.dState][0:yolink.nbrPorts]
            if 'delays'in data[yolink.dData]:
                yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][yolink.dDelays]                 
        yolink.updateMessageInfo(data)
    '''
    '''    
    def updateStatusData(yolink, data): 
        if not data[yolink.dData]: # No data returned
            yolink.dataAPI[yolink.dOnline] = False
        elif 'online' in data[yolink.dData]:
            yolink.dataAPI[yolink.dOnline] = data[yolink.dData][yolink.dOnline]
        else:
            yolink.dataAPI[yolink.dOnline] = True
        if 'method' in data:
            if  yolink.dataAPI[yolink.dOnline]:
                for key in data[yolink.dData]:
                    if key == 'delay':
                            yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][key]
                    else:
                            yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key]
                yolink.updateLoraInfo(data)
                yolink.updateMessageInfo(data)
       
        else: #event
            if  yolink.dataAPI[yolink.dOnline]:
                for key in data[yolink.dData]:
                        yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key]
                yolink.updateLoraInfo(data)
                yolink.updateMessageInfo(data)
    '''
    def updateStatusData  (yolink, data):
        logging.debug(yolink.type + ' - updateStatusData')
        
        if 'online' in data[yolink.dData]:
            yolink.dataAPI[yolink.dOnline] = data[yolink.dData][yolink.dOnline]
        else:
            yolink.dataAPI[yolink.dOnline] = True
        if 'method' in data:
            if yolink.dState in data[yolink.dData]:
                if type(data[yolink.dData][yolink.dState]) is dict:
                    logging.debug('State is Dict: {} '.format(data[yolink.dData][yolink.dState]))
                    for key in data[yolink.dData][yolink.dState]:
                        
                        if key == 'delay':
                             yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][yolink.dState][yolink.dDelay]
                        else:
                            yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][yolink.dState][key]
                    yolink.nbrPorts = 1        
                elif  type(data[yolink.dData][yolink.dState]) is list:
                    logging.debug('State is List (multi): {} '.format(data[yolink.dData][yolink.dState]))
                    if 'delays'in data[yolink.dData]:
                        logging.debug('delays exist in data')
                        yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][yolink.dDelays]
                        yolink.nbrPorts = len( yolink.dataAPI[yolink.dData][yolink.dDelays])
                    else:
                        yolink.nbrPorts = 1
                    yolink.dataAPI['nbrPorts'] = yolink.nbrPorts     
                    yolink.dataAPI[yolink.dData][yolink.dState] = data[yolink.dData][yolink.dState][0:yolink.nbrPorts]
                else:
                    for key in data[yolink.dData]:
                        if key == 'delay':
                             yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][key]
                        else:
                             yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key]
            else:
                pass # no data and state         
        else: #event
            if type(data[yolink.dData][yolink.dState]) is dict:
                for key in data[yolink.dData][yolink.dState]:
                    if key == 'delay':
                            yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][yolink.dState][yolink.dDelay]
                    else:
                        yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][yolink.dState][key]
            elif  type(data[yolink.dData][yolink.dState]) is list:           
                if 'delays'in data[yolink.dData]:
                    yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][yolink.dDelays]
                else:
                    yolink.dataAPI[yolink.dData][yolink.dDelays] = None
                yolink.dataAPI[yolink.dData][yolink.dState] = data[yolink.dData][yolink.dState][0:yolink.nbrPorts]
            else:
                for key in data[yolink.dData]:
                    yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key]
        yolink.updateLoraInfo(data)
        yolink.updateMessageInfo(data)
    
    def updateScheduleStatus(yolink, data):
        logging.debug(yolink.type + 'updateScheduleStatus')
        yolink.setOnline(data)
        yolink.setNbrPorts(data)
        yolink.updateLoraInfo(data)
        yolink.dataAPI[yolink.dData][yolink.dSchedule] = data[yolink.dData]
        yolink.dataAPI[yolink.lastMessage] = data

    def updateDelayStatus(yolink, data):
        logging.debug(yolink.type + 'updateDelayStatus')
        yolink.setOnline(data)
        yolink.setNbrPorts(data)
        yolink.updateLoraInfo(data)
        if 'delays'in data[yolink.dData]:
            yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][yolink.dDelays]
 
        yolink.updateMessageInfo(data)


    def updateFWStatus(yolink, data):
        logging.debug(yolink.type + 'updateFWStatus - not working ??')
        # Need to have it workign forst - not sure what return struture will look lik
        #yolink.dataAPI['data']['state']['state'].append( data['data'])
        yolink.dataAPI['state']['lastTime'] = data['time']
        yolink.dataAPI['lastMessage'] = data      
    
    def eventPending(yolink):
        return( not yolink.eventQueue.empty())
    
    def getEvent(yolink):
        if not yolink.eventQueue.empty():
            return(yolink.eventQueue.get())
        else:
            return(None)
           
    def getInfoAPI (yolink):
        return(yolink.dataAPI)

    def sensorOnline(yolink):
        return(yolink.dataAPI['online'] )       

    def getAlarms(yolink):
        return(yolink.getStateValue('alarm'))

    def getBattery(yolink):
        return(yolink.getStateValue('battery'))

    def getLastUpdate (yolink):
        return(yolink.dataAPI[yolink.lastUpdate])

    def refreshState(yolink):
        logging.debug(str(yolink.type)+ ' - refreshState')
        #devStr = str(yolink.type)+'.getSate'
        yolink.refreshDevice()
        #time.sleep(2)
   
    def getState(yolink):
        try:
            logging.debug(yolink.type +' - getState')
            return(yolink.dataAPI[yolink.dData][yolink.dState])
        except Exception as e:
            logging.debug('getState exceptiom: {}'.format(e) )
            return(None)

    def getData(yolink):
        try:
            logging.debug(yolink.type +' - getData')
            return(yolink.dataAPI[yolink.dData][yolink.dState])
        except Exception as e:
            logging.debug('getData exceptiom: {}'.format(e) )
            return(None)



    def refreshDelays(yolink):
        logging.debug(str(yolink.type)+ ' - refreshDelays')
        yolink.refreshDevice()
        time.sleep(2)
        return(yolink.getDelays())

    def getDelays(yolink):
        logging.debug(str(yolink.type)+ ' - getDelays')
        if yolink.dDelays in yolink.dataAPI[yolink.dData]:
            return(yolink.dataAPI[yolink.dData][yolink.dDelays])
        else:
            return(None)
    
    def timezoneOffsetSec(yolink):
        local = tzlocal()
        tnow = datetime.now()
        tnow = tnow.replace(tzinfo = local)
        utctnow = tnow.astimezone(tzutc())
        tnowStr = str(tnow)
        
        pos = tnowStr.rfind('+')
        if pos > 0:
            tnowStr = tnowStr[0:pos]
        else:
            pos = tnowStr.rfind('-')
            tnowStr = tnowStr[0:pos]
        utctnowStr = str(utctnow)
        pos = utctnowStr.rfind('+')
        if pos > 0:
            utctnowStr = utctnowStr[0:pos]
        else:
            pos = utctnowStr.rfind('-')
            utctnowStr = utctnowStr[0:pos]

        tnow = datetime.strptime(tnowStr,  '%Y-%m-%d %H:%M:%S.%f')
        utctnow = datetime.strptime(utctnowStr,  '%Y-%m-%d %H:%M:%S.%f')
        diff = utctnow - tnow
        return (diff.total_seconds())


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