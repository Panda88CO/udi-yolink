
import time
import datetime
import json
import re
#import threading

from  datetime import datetime
from dateutil.tz import *

try:
    import udi_interface
    logging = udi_interface.LOGGER
    #logging = getlogger('yolink_mqtt_classV2')
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)



from queue import Queue
from yolink_delay_timerV2 import CountdownTimer
"""
Object representation for YoLink MQTT Client
"""
class YoLinkMQTTDevice(object):
    def __init__(yolink, yoAccess, deviceInfo, callback ):
        #super().__init__( yolink_URL, csid, csseckey, deviceInfo)
        #yolink.callback = callback
        #yolink.build_device_api_request_data()
        #yolink.enable_device_api()
        #{"deviceId": "d88b4c1603007966", "deviceUDID": "75addd8e21394d769b85bc292c553275", "name": "YoLink Hub", "token": "118347ae-d7dc-49da-976b-16fae28d8444", "type": "Hub"}
        
        yolinkDelaySupport = ['']
        yolink.yoAccess = yoAccess
        yolink.deviceInfo = deviceInfo
        #yolink.deviceId = yolink.deviceInfo['deviceId']
        yolink.type = yolink.deviceInfo['type']
        yolink.delaySupport = ['Outlet', 'MultiOutlet', 'Manipulator', 'Switch', 'Dimmer']
        yolink.scheduleSupport = []#['Outlet', 'MultiOutlet', 'Manipulator', 'Switch','InfraredRemoter','Sprinkler', 'Thermostat', 'Dimmer' ]
        yolink.online  = False 
        yolink.nbrPorts = 1
        yolink.nbrOutlets = 1
        yolink.nbrUsb = 0 
        logging.debug('subscribe_mqtt: {}'.format(yolink.deviceInfo['deviceId']))
        yolink.yoAccess.subscribe_mqtt(deviceInfo['deviceId'], callback)
        yolink.lastDataPacket = ''
        yolink.lastControlPacket = '' 
        yolink.TZcomp = (yolink.timezoneOffsetSec() /60 /60)
        yolink.lastUpdateTime = 0
        #yolink.yolink_URL = yoAccess.apiv2URL
        #yolink.mqttURL = yoAccess.mqttURL
        yolink.noconnect = 0 # number on consecutive no connect to device
        yolink.daysOfWeek = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        yolink.maxSchedules = 6
        yolink.deviceSupportList = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 'SpeakerHub', 'VibrationSensor',  'Dimmer', 'InfraredRemoter' ]
        yolink.lastUpd = 'lastUpdTime'
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
        yolink.disconnect = False
        if yolink.type in yolink.delaySupport and yolink.type not in yolink.scheduleSupport :
            yolink.dataAPI = {
                              yolink.lastUpd:0
                            , yolink.lastMessage:{}
                            ,'lastStateTime':{}
                            , yolink.dOnline:False
                            , yolink.dData :{yolink.dState:{}
                                             }
                            }
            yolink.extDelayTimer = CountdownTimer()
        elif yolink.type in yolink.scheduleSupport:
            yolink.dataAPI = {
                              yolink.lastUpd:0
                            , yolink.lastMessage:{}
                            ,'lastStateTime':{}
                            , yolink.dOnline:False
                            , yolink.dData :{   yolink.dState:{}
                                                ,yolink.dSchedule : [] 
                                                }
                            }
            yolink.extDelayTimer = CountdownTimer()
        else:
            yolink.dataAPI = {
                              yolink.lastUpd:0
                            , yolink.lastMessage:{}
                            ,'lastStateTime':{}
                            , yolink.dOnline :False
                            , yolink.dData :{ yolink.dState:{} }
                            }  
            yolink.extDelayTimer = None
        yolink.eventQueue = Queue()
        #yolink.mutex = threading.Lock()
        yolink.timezoneOffsetSec = yolink.timezoneOffsetSec()
        #yolink.yoAccess.connect_to_broker()
        #yolink.loopTimeSec = updateTimeSec
    
        #yolink.updateInterval = 3
        yolink.messagePending = False
    
    def delayTimerCallback(yolink, callback, updateTime=5):

        yolink.extDelayTimer.timerReportInterval(updateTime)
        yolink.extDelayTimer.timerCallback(callback, updateTime)
        #logging.debug('delayTimerCallback: '.format(updateTime))

    def measure_time(func):                                                                                                   
                                                                                                                          
        def wrapper(*arg):                                                                                                      
            t = time.time()                                                                                                     
            res = func(*arg)                                                                                                    
            logging.debug ("Function took " + str(time.time()-t) + " seconds to run")                                                    
            return res                                                                                                          
        return wrapper                                                                                                                


    #@measure_time
    def initDevice(yolink):
        yolink.refreshDevice()
        #time.sleep(2) 
        #yolink.online = yolink.getOnlineStatus()

    '''
    def publish_data(yolink, data):
        logging.debug( 'Publish Data to Queue: {}'.format(data))
        while not yolink.yoAccess.connectedToBroker:
            logging.debug('Connection to Broker not established - waiting')
            time.sleep(1)
        
        yolink.yoAccess.publishQueue.put(data, timeout = 2)
        if yolink.yoAccess.publishQueue.full():
            return(False)
        else:
            return(True)
    '''
    #@measure_time
    def shut_down(yolink):
        yolink.disconnect = True
        yolink.online = False
        #yolink.yoAccess.shut_down()

    #@measure_time
    def deviceError(yolink, data):
        logging.debug(yolink.type+' - deviceError')
        yolink.dataAPI[yolink.dOnline] = False
        # may need to add more error handling 

    #@measure_time
    def initNode(yolink):
        count = 0
        maxCount = 2
        yolink.refreshDevice()
        #time.sleep(3)
        #yolink.online = yolink.getOnlineStatus()
        #while not yolink.online and count < maxCount and not yolink.disconnect:
        #    time.sleep(10)
        #    yolink.refreshDevice()
        #    count = count + 1
        #    print ('retry count : {}'.format(count))

        if not yolink.online:    
            logging.error('{} not online'.format(yolink.type))

    #@measure_time
    def refreshDevice(yolink):
        logging.debug('{} - refreshDevice - supports {}'.format(yolink.type, yolink.methodList))
        attempt = 1
        maxAttempts = 3
        if 'getState' in yolink.methodList:
            methodStr = yolink.type+'.getState'
            #logging.debug(methodStr)  
            data = {}
            data['time'] = str(int(time.time_ns()/1e6))
            data['method'] = methodStr
            data["targetDevice"] =  yolink.deviceInfo['deviceId']
            data["token"]= yolink.deviceInfo['token']
            #logging.debug  ('refreshDevice')
            while  not yolink.yoAccess.publish_data(data) and attempt <= maxAttempts:
                time.sleep(1)
                attempt = attempt + 1
            yolink.lastControlPacket = data
            time.sleep(2)
            yolink.check_system_online()
              
    #@measure_time
    def lastUpdate(yolink):
        logging.debug('{} - Checking last update'.format(yolink.type))
        if yolink.dataAPI['lastStateTime']:
            return(yolink.dataAPI['lastStateTime'])
        else:
            return(0)
    #@measure_time
    def check_system_online(yolink):
        if yolink.yoAccess.online:
            yolink.online = yolink.dataAPI[yolink.dOnline]
        else:
            yolink.online = False
        return(yolink.online)

    #@measure_time
    def data_updated(yolink):
        tmp = yolink.lastUpdate()
        if ( tmp > yolink.lastUpdateTime):
            yolink.lastUpdateTime = tmp 
            logging.debug('{} - Data Updated'.format(yolink.type))
            return(True)
        else:
            return(False)

    #@measure_time
    def setDevice(yolink,  data):
        attempt = 1
        maxAttempts = 3
        logging.debug(yolink.type+' - setDevice')
        worked = False
        if 'setState' in yolink.methodList:
            methodStr = yolink.type+'.setState'
            worked = True
        elif 'toggle' in yolink.methodList:
            methodStr = yolink.type+'.toggle'
            worked = True
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = methodStr
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        logging.debug(yolink.type+' - setDevice -data {}'.format(data))
        if worked:
            while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
                time.sleep(1)
                attempt = attempt + 1
            #yolink.yoAccess.publish_data(data)
            return(True)
        else:
            return(False)

    def getDataValue(yolink,key): 
        logging.debug('{} -     def getDataValue {}: '.format(yolink.type, key))
        try:
            count = 1
            while key not in yolink.dataAPI[yolink.dData] and count <3:
                time.sleep(1)
                count = count + 1
            #logging.debug('DEBUGME getDataValue {}-{} : {}'.format(yolink.type, key, yolink.dataAPI[yolink.dData] ))
            if key in yolink.dataAPI[yolink.dData]:
                yolink.online = yolink.check_system_online()
                return(yolink.dataAPI[yolink.dData][key])
            else:
                yolink.online = False 
                return('NA')
        except Exception as E:
            logging.error('getDataValue Exception: {}'.format(E))
    #@measure_time

    def getDataStateValue(yolink, key):
        logging.debug('{} - getDataStateValue, key:{}'.format(yolink.type, key))
        try:
            count = 1
            yolink.online = yolink.check_system_online()
            #logging.debug("getStateValue Online: {}".format(yolink.online))
            if yolink.online :
                while key not in yolink.dataAPI[yolink.dData][yolink.dState] and count <3:
                    time.sleep(1)
                    count = count + 1
                #logging.debug('DEBUGME getDataStateValue {}-{} : {}'.format(yolink.type, key, yolink.dataAPI[yolink.dData][yolink.dState] ))
                if key in yolink.dataAPI[yolink.dData][yolink.dState]:
                    return(yolink.dataAPI[yolink.dData][yolink.dState][key])
                else:
                    return(-1)
            else:
                return( )
        except Exception as E:
            logging.debug('getData exceptiom: {}'.format(E) )
            return( )

    #@measure_time
    def getValue(yolink,key): 
        logging.debug('{} -     def getValue {}: '.format(yolink.type, key))
        try:
            count = 1
            while key not in yolink.dataAPI[yolink.dData] and count <3:
                time.sleep(1)
                count = count + 1
            #logging.debug('DEBUG getValue {}-{} : {}'.format(yolink.type, key, yolink.dataAPI[yolink.dData] ))
            if key in yolink.dataAPI[yolink.dData]:
                yolink.online = yolink.check_system_online()
                return(yolink.dataAPI[yolink.dData][key])
            else:
                yolink.online = False 
                return('NA')
        except Exception as E:
            logging.debug('getData exceptiom: {}'.format(E) )
            return( )    

    #@measure_time
    def getStateValue(yolink, key):
    
        logging.debug('{} - getStateValue, key:{}'.format(yolink.type, key))
        try:
            count = 1
            yolink.online = yolink.check_system_online()
            #logging.debug("getStateValue Online: {}".format(yolink.online))
            if yolink.online :
                while key not in yolink.dataAPI[yolink.dData][yolink.dState] and count <3:
                    time.sleep(1)
                    count = count + 1
                #logging.debug('DEBUG getStateValue {}-{} : {}'.format(yolink.type, key, yolink.dataAPI[yolink.dData]))
                if key in yolink.dataAPI[yolink.dData][yolink.dState]:
                    return(yolink.dataAPI[yolink.dData][yolink.dState][key])
                else:
                    return(-1)
            else:
                return( )
        except Exception as e:
            logging.debug('getData exceptiom: {}'.format(e) )
            return( )
    
    #@measure_time
    def getInfoAPI (yolink):
        return(yolink.dataAPI)

    #def sensorOnline(yolink):
    #    return(yolink.check_system_online() )       

    #@measure_time
    def getAlarms(yolink):
        return(yolink.getStateValue('alarm'))

    #@measure_time
    def getBattery(yolink):
        return(yolink.getStateValue('battery'))

    #@measure_time
    def getLastUpdate (yolink):
        try:
            if yolink.lastUpd in yolink.dataAPI:
                if yolink.dataAPI[yolink.lastUpd] and  yolink.dataAPI[yolink.lastUpd] !='' :
                    return(int(yolink.dataAPI[yolink.lastUpd]))
                else:
                    yolink.dataAPI[yolink.lastUpd] = 0
                    return(0)
            else:
                yolink.dataAPI[yolink.lastUpd] = 0
                return(0)
        except:
            logging.debug('Exception yolink.dataAPI[yolink.lastUpd] does not exist')
            return(time.time())

    '''
    def refreshState(yolink):
        logging.debug(str(yolink.type)+ ' - refreshState')
        yolink.refreshDevice()
    '''
    #@measure_time
    def getDataAll(yolink):
        try:
            logging.debug(yolink.type +' - getDataAll')
            return(yolink.dataAPI[yolink.dData])
        except Exception as e:
            logging.debug('getData exceptiom: {}'.format(e) )
            return(None)

    #@measure_time
    def getLastDataPacket(yolink):
        return(yolink.dataAPI['lastMessage']) 

    #@measure_time
    def getState(yolink):
        try:                
            return(yolink.dataAPI[yolink.dData][yolink.dState][yolink.dState] )
        except Exception as e:
            logging.debug('getState exception: {}'.format(e) )
            return(None)
        
    #@measure_time
    def getData(yolink):
        try:
            logging.debug(yolink.type +' - getData')
            return(yolink.dataAPI[yolink.dData][yolink.dState])
        except Exception as e:
            logging.debug('getData exceptiom: {}'.format(e) )
            return(None)

    '''
    def getOnlineStatus(yolink):
        maxCount = 3
        attempt = 1
        logging.debug(yolink.type+' - getOnlineStatus')
        if 'online' in yolink.dataAPI:
            return(yolink.check_system_online())
        else:
            while count 
            return(False)

    def onlineStatus(yolink):
        return(yolink.getOnlineStatus())
    '''
    #@measure_time
    def checkOnlineStatus(yolink, dataPacket):

        if 'code' in dataPacket:
            if dataPacket['code'] == '000000':
                if 'data' in dataPacket:
                    if 'online' in dataPacket['data']:
                        yolink.online = dataPacket['data']['online']
                    else:
                        yolink.online = True
            else:
                yolink.online = False
        elif 'event' in dataPacket:
            if 'data' in dataPacket:
                    if 'online' in dataPacket['data']:
                        yolink.online = dataPacket['data']['online']
                    else:
                        yolink.online = True
            else:
                yolink.online = True 
        else:
            
            yolink.online = False    
        if not yolink.online:
            logging.debug('checkOnlineStatus {} - Off line detected: {}'.format(yolink.deviceInfo['name'], dataPacket))
        return(yolink.online)

    #@measure_time
    def updateCallbackStatus(yolink, data, eventSupport = False):
        try:
            logging.debug('{} - updateCallbackStatus : {}'.format(yolink.type, data))
            
            if 'method' in  data and 'event' not in data:
                logging.debug('Method detected')
                if data['code'] == '000000':

                    yolink.online = yolink.checkOnlineStatus(data)
                    yolink.noconnect = 0
                    if  '.getState' in data['method'] :
                        #if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data) 
                        
                    elif  '.setState' in data['method'] :
                        #if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)                          
                    elif  '.setDelay'  in data['method']:
                        #if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateDelayData(data)       
                    #elif  '.getSchedules'  in data['method'] :
                    #    #if int(data['time']) > int(yolink.getLastUpdate()):
                    #    yolink.updateScheduleStatus(data)
                    #elif  '.setSchedules' in data['method'] :
                    #    #if int(data['time']) > int(yolink.getLastUpdate()):
                    #    yolink.updateScheduleStatus(data)
                    #elif  '.getVersion' in data['method']:
                    #    #if int(data['time']) > int(yolink.getLastUpdate()):
                    #    yolink.updateFWStatus(data)
                    elif  '.toggle' in data['method']:
                        #if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)          
                    elif  '.setWiFi' in data['method'] :
                        #if int(data['time']) > int(yolink.getLastUpdate()):
                        #yolink.updateStatusData(data)       
                        logging.debug('Do Nothing for now')
                    elif  '.playAudio' in data['method'] :
                        #if int(data['time']) > int(yolink.getLastUpdate()):
                        logging.debug('Do Nothing for now')
                        #yolink.updateStatusData(data)      
                    elif  '.setOption' in data['method'] :
                        #if int(data['time']) > int(yolink.getLastUpdate()):
                        logging.debug('Do Nothing for now')
                        #yolink.updateStatusData(data)   
                    elif  '.StatusChange' in data['method']:
                        #if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)     


                    else:
                        logging.debug('Unsupported Method passed' + str(json.dumps(data))) 
                #elif data['code'] == '000201': #Cannot connect to device - retry
                #    if yolink.noconnect < yolink.max_noconnect:
                #        time.sleep(1)
                #        logging.debug('Device not connected - trying agian ')
                else:
                    yolink.deviceError(data)
                    yolink.online = yolink.checkOnlineStatus(data)
                    logging.error(yolink.type+ ': ' + data['desc'])
            elif 'event' in data:
                #logging.debug('Event deteced')
                yolink.online = True #
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
                #elif '.getSchedules' in data['event']:
                #    if int(data['time']) > int(yolink.getLastUpdate()):
                #        yolink.updateScheduleStatus(data)   
                #elif '.setSchedules' in data['event']:
                #    if int(data['time']) > int(yolink.getLastUpdate()):
                #        yolink.updateScheduleStatus(data)   
                elif '.Alert' in data['event']:         
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)  
                elif '.StatusChange' in data['event']:         
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)                          
                elif '.setDelay' in data['event']:         
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)     
                elif '.openReminder' in data['event']:         
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)
                elif '.DataRecord' in  data['event']:
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        yolink.updateStatusData(data)
                else:
                    logging.debug('Unsupported Event passed - trying anyway; {}'.format(data) )
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
                            logging.error('Unsupported event detected: ' + str(E))
                if eventSupport:
                    yolink.eventQueue.put(data['event']) 
                yolink.lastDataPacket = data
            else:
                yolink.online = yolink.checkOnlineStatus(data) and yolink.check_system_online()
                logging.debug('updateStatus: Unsupported packet type: ' +  json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
            yolink.dataAPI[yolink.dOnline] = yolink.online 
        except Exception as e:
            logging.debug('Exception: updateCallbackStatus: {}'.format(e))
            logging.debug('Exception data: {}'.format(data))
    ####################################


    #@measure_time
    def setDelays(yolink,  onDelay, offDelay):
        attempt = 1
        maxAttempts = 3
        logging.debug(yolink.type+' - setDelay')
        data = {}
        delays = {}
        temp = []
        data['params'] = {}
        data['params']['delayOn'] = onDelay
        data['params']['delayOff'] = offDelay
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
       
        while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
            time.sleep(1)
            attempt = attempt + 1
        
        delays['ch'] = 1
        delays['on'] = data['params']['delayOn']
        delays['off'] = data['params']['delayOff']
        temp.append(delays)
        yolink.extDelayTimer.addDelays(temp)
        yolink.online = yolink.check_system_online()
        return(True)

    def setOnDelay(yolink,  onDelay):
        attempt = 1
        maxAttempts = 3
        logging.debug(yolink.type+' - setOnDelay')
        data = {}
        delays = {}
        temp = []
        data['params'] = {}
        data['params']['delayOn'] = onDelay
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        #yolink.yoAccess.publish_data( data)
        while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
            time.sleep(1)
            attempt = attempt + 1
            
        delays['ch'] = 1
        delays['on'] = data['params']['delayOn']
        temp.append(delays)
        yolink.extDelayTimer.addDelays(temp)
        yolink.online = yolink.check_system_online()
        return(True)

    #@measure_time
    def setOffDelay(yolink,  offDelay):
        attempt = 1
        maxAttempts = 3
        logging.debug(yolink.type+' - setOffDelay')
        data = {}
        delays = {}
        temp = []
        data['params'] = {}
        data['params']['delayOff'] = offDelay
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
            time.sleep(1)
            attempt = attempt + 1

        delays['ch'] = 1
        delays['off'] = data['params']['delayOff']
        temp.append(delays)
        yolink.extDelayTimer.addDelays(temp)
        yolink.online = yolink.check_system_online()
        return(True)

    #@measure_time
    def setDelayList(yolink, delayList):
        attempt = 1
        maxAttempts = 3
        logging.debug(yolink.type+' - setDelay')
        delays = {}
        temp = []
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
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
            time.sleep(1)
            attempt = attempt + 1
        delays['ch'] = 1
        delays['on'] = data['params']['delayOn']
        delays['off'] = data['params']['delayOff']
        temp.append(delays)
        #yolink.writeDelayData(data)
        yolink.extDelayTimer.addDelays(temp)
        yolink.online = yolink.check_system_online()
        return(True)

    #@measure_time
    def updateDelayData(yolink, data):
        if 'event' in data:
            if  yolink.check_system_online():

                tmp =  {}
                for key in data[yolink.dData]:
                    if key == 'delayOn':
                        tmp['on'] = data[yolink.dData][key]
                    elif key == 'delayOff':
                        tmp['off'] = data[yolink.dData][key] 
                    else:
                        tmp[key] =  data[yolink.dData][key] 
                yolink.extDelayTimer.addDelays(tmp)
            yolink.updateLoraInfo(data)
            yolink.updateMessageInfo(data)
    

    #@measure_time
    def refreshDelays(yolink):
        logging.debug(yolink.type+' - refreshDelays')
        #yolink.refreshDevice()
        #yolink.online = yolink.check_system_online()
        return(yolink.extDelayTimer.timeRemaining())


    ##############################################


    '''
    def refreshSchedules(yolink):
        logging.debug(yolink.type + '- refreshSchedules')
        attempt = 1
        maxAttempts = 3
        if 'getSchedules' in yolink.methodList:
            methodStr = yolink.type+'.getSchedules'
            #logging.debug(methodStr)  
            data = {}
            data['time'] = str(int(time.time_ns()//1e6))
            data['method'] = methodStr
            data["targetDevice"] =  yolink.deviceInfo['deviceId']
            data["token"]= yolink.deviceInfo['token']
            while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
                time.sleep(1)
                attempt = attempt + 1
            

    def getSchedules(yolink):
        logging.debug('{}- getSchedules: {}'.format(yolink.type, yolink.deviceInfo['name'] ))
        yolink.refreshSchedules()
        test = 0 
        while yolink.dSchedule not in yolink.dataAPI[yolink.dData] and test < 3:
            time.sleep(1)
            test = test +1
            
        nbrSchedules  = len(yolink.dataAPI[yolink.dData][yolink.dSchedule])
        temp = {}
        yolink.scheduleList = []
        for scheduleNbr in yolink.dataAPI[yolink.dData][yolink.dSchedule]:
            temp[scheduleNbr] = {}
            for key in yolink.dataAPI[yolink.dData][yolink.dSchedule][scheduleNbr]:
                if key == 'week':
                    days = yolink.maskToDays(yolink.dataAPI[yolink.dData][yolink.dSchedule][scheduleNbr][key])
                    temp[scheduleNbr][key]= days
                elif yolink.dataAPI[yolink.dData][yolink.dSchedule][scheduleNbr][key] == '25:0':
                    #temp[schedule].pop(key)
                    pass
                else:
                    temp[scheduleNbr][key] = yolink.dataAPI[yolink.dData][yolink.dSchedule][scheduleNbr][key]
            temp[scheduleNbr]['index'] = scheduleNbr   
            yolink.scheduleList.append(temp[scheduleNbr])
        return(temp)


    
    def setSchedules(yolink):
        logging.debug(yolink.type + '- setSchedule')
        data = yolink.prepareScheduleData()        
        
        data['time'] = strint((time.time_ns()//1e6))
        data['method'] = yolink.type+'.setSchedules'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        yolink.yoAccess.publish_data(data)
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

    
    def bool2Nbr(yolink, bool):
        if bool:
            return(1)
        else:
            return(0)


    
    def setOnline(yolink, data):
        logging.debug('SetOnline:')
        if yolink.dOnline in data[yolink.dData]:
            yolink.dataAPI[yolink.dOnline] = data[yolink.dData][yolink.dOnline]
        elif data[yolink.dData] == {}:
            yolink.dataAPI[yolink.dOnline] = False
        else:
            yolink.dataAPI[yolink.dOnline] = True
        yolink.online = yolink.dataAPI[yolink.dOnline]
        logging.debug('online: {}'.format( yolink.online))
 

    def updateLoraInfo(yolink, data):
        if yolink.dState in data[yolink.dData]:
            if 'loraInfo' in data[yolink.dData][yolink.dState]:
                yolink.dataAPI[yolink.dData][yolink.dState]['loraInfo']= data[yolink.dData]['loraInfo']

    def updateMessageInfo(yolink, data):
        yolink.dataAPI[yolink.lastUpd] = data[yolink.messageTime]
        yolink.dataAPI[yolink.lastMessage] = data
   
    #@measure_time
    def updateStatusData  (yolink, data):
        try:
            logging.debug('{} - updateStatusData : {}'.format(yolink.type , data))
            #yolink.setOnline(data)
            if 'reportAt' in data[yolink.dData] :
                reportAt = datetime.strptime(data[yolink.dData]['reportAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                yolink.dataAPI['lastStateTime'] = (reportAt.timestamp() -  yolink.timezoneOffsetSec)*1000
            elif 'stateChangedAt' in data[yolink.dData]:
                yolink.dataAPI['lastStateTime'] = data[yolink.dData]['stateChangedAt' ]
            else:
                yolink.dataAPI['lastStateTime'] = data[yolink.messageTime]
            if 'delays' in data['data']:
                    yolink.nbrOutlets = len(data['data']['delays'])
                    yolink.nbrUsb = data['data']['delays'][0]['ch']
                    yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
            if 'method' in data:
                if yolink.dState in data[yolink.dData]:
                    #if 'reportAt' in data[yolink.dData] or 'stateChangedAt' in data[yolink.dData]:
                    #    reportAt = datetime.strptime(data[yolink.dData]['reportAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    #    yolink.dataAPI['lastStateTime'] = (reportAt.timestamp() -  yolink.timezoneOffsetSec)*1000
                    #else:
                    #    yolink.dataAPI['lastStateTime'] = data[yolink.messageTime]
                    if type(data[yolink.dData][yolink.dState]) is dict:
                        #logging.debug('State is Dict: {} '.format(data[yolink.dData][yolink.dState]))
                        for key in data[yolink.dData][yolink.dState]:
                            if key == yolink.dDelay and yolink.type in yolink.delaySupport:
                                temp = []
                                temp.append(data[yolink.dData][yolink.dState][yolink.dDelay])
                                yolink.extDelayTimer.addDelays(temp)
                                # yolink.dataAPI[yolink.dData][yolink.dDelay].append(data[yolink.dData][yolink.dState][yolink.dDelay])
                            else:
                                yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][yolink.dState][key]      
                    elif  type(data[yolink.dData][yolink.dState]) is list:
                        #logging.debug('State is List (multi): {} '.format(data[yolink.dData][yolink.dState]))
                        if yolink.dDelays in data[yolink.dData]:
                            #logging.debug('delays exist in data - LIST')
                            yolink.extDelayTimer.addDelays(data[yolink.dData][yolink.dDelays])
                            yolink.nbrOutlets = len(data[yolink.dData][yolink.dDelays])
                            yolink.nbrUsb = data[yolink.dData][yolink.dDelays][0]['ch']
                            yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
                            #temp = []
                            #for delatIndx in range(0,len(data[yolink.dData][yolink.dDelays])):
                            # yolink.dataAPI[yolink.dData][yolink.dDelays] = data[yolink.dData][yolink.dDelays]
                            #yolink.extDelayTimer.add(data[yolink.dData][yolink.dDelays])
                            #yolink.nbrPorts = len( yolink.dataAPI[yolink.dData][yolink.dDelays])
                            #yolink.fistOutlet = yolink.dataAPI[yolink.dData][yolink.dDelays][0]['ch']
                            #need to update USB handling
                        yolink.dataAPI[yolink.dData][yolink.dState] = data[yolink.dData][yolink.dState][0:yolink.nbrPorts+yolink.nbrUsb]
                        
                    else:
                        for key in data[yolink.dData]:
                            if key == yolink.dDelay:
                                temp = []
                                if 'ch' not in data[yolink.dData][key]:
                                    data[yolink.dData][key]['ch'] = 1
                                temp.append(data[yolink.dData][key])
                                yolink.extDelayTimer.addDelays(temp) 
                                yolink.nbrOutlets = 1
                                yolink.nbrUsb = 0
                                yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
                            else:
                                yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key]
                    logging.debug('updateStatusData - Method data : {}'.format(yolink.dataAPI))
                elif 'data' in data:
                    yolink.dataAPI[yolink.dData] = data['data']
                else: # setDelay only returns data
                    yolink.dataAPI['lastStateTime'] = data[yolink.messageTime]
                    if ".setDelay" in data['method']:
                        logging.debug("setDelay detected")
                        if data[yolink.dData] != {}: #multiOutlet currently returns {}
                            if type(data[yolink.dData]) is dict:
                                temp = []
                                temp.append(data[yolink.dData])
                                yolink.extDelayTimer.addDelays(temp)
                                yolink.nbrOutlets = len(temp)
                                yolink.nbrUsb = 0
                                yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
            else: #event

                if ".setDelay" in data['event']:
                    #logging.debug("setDelay detected")
                    if data[yolink.dData] != {}: #multiOutlet currently returns {}
                        if type(data[yolink.dData]) is dict:
                            temp = []
                            temp.append(data[yolink.dData])
                            yolink.extDelayTimer.addDelays(temp)
                            yolink.nbrOutlets = 1
                            yolink.nbrUsb = 0
                            yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
                    else: # multi outlet - need to getState 
                        yolink.refreshDevice()
                elif '.DataRecord'in data['event']:
                    logging.debug('.DataRecord : {}'.format(data))
                    for key in data[yolink.dData]:
                        if type(key) is list: # list of structs
                            meas_time = -1 
                            for index in key: # each struct 
                                for element in index: 
                                    if 'time' in element:
                                        tmp_time = datetime.strptime(element['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
                                        if tmp_time >= meas_time: # more recent data
                                            meas_time = tmp_time
                                            if 'temperature' in element:
                                                tmp_temp = element['temperature']
                                            if 'humidity' in element:
                                                tmp_hum = element['humidity']
                            if tmp_temp:
                                yolink.dataAPI[yolink.dData][yolink.dState]['temperature'] =  tmp_temp        
                            if tmp_hum:
                                yolink.dataAPI[yolink.dData][yolink.dState]['humidity'] =  tmp_hum                             
                            if meas_time != -1:
                                yolink.dataAPI[yolink.dData][yolink.dState]['time'] =  meas_time                                         
                        else:
                            yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key] 

                elif yolink.dState in data[yolink.dData]:
                    if type(data[yolink.dData][yolink.dState]) is dict:
                        for key in data[yolink.dData][yolink.dState]:
                            if key == yolink.dDelay:
                                temp = []
                                temp.append(data[yolink.dData][key])
                                yolink.extDelayTimer.addDelays(temp)   
                            else:
                                yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][yolink.dState][key]
                    elif  type(data[yolink.dData][yolink.dState]) is list:           
                        if yolink.dDelays in data[yolink.dData]:
                            logging.debug('delays exist in data (LIST')
                            yolink.extDelayTimer.addDelays(data[yolink.dData][yolink.dDelays])
                            yolink.nbrOutlets = len(data[yolink.dData][yolink.dDelays])
                            yolink.nbrUsb = data[yolink.dData][yolink.dDelays][0]['ch']
                            yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
                            yolink.dataAPI[yolink.dData][yolink.dState] = data[yolink.dData][yolink.dState][0:yolink.nbrPorts+yolink.nbrUsb]
                        else:
                            #yolink.dataAPI[yolink.dData][yolink.dDelays] = []
                            yolink.dataAPI[yolink.dData][yolink.dState] = data[yolink.dData][yolink.dState][0:yolink.nbrPorts+yolink.nbrUsb]
                    else: #must be single key - add all keys but contains key = 'state
                        for key in data[yolink.dData]:
                            yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key]
                else:
                    for key in data[yolink.dData]:
                        yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key] # sAdding all keys to state  
                        #yolink.dataAPI[yolink.dData][yolink.dState][key] = data[yolink.dData][key]
                logging.debug('updateStatusData - Event data : {}'.format(yolink.dataAPI))

            #yolink.dataAPI['nbrPorts'] = yolink.nbrPorts
            #yolink.online = yolink.check_system_online()
            yolink.updateLoraInfo(data)
            yolink.updateMessageInfo(data)
        except Exception as e:
            logging.debug('Exception updateStatusData - {}'.format(e))
            logging.debug('Exception Data - {}'.format(data))

    def get_event_from_state(yolink):
        logging.debug('get_event_from_state')
        try:
            return(yolink.dataAPI[yolink.dData][yolink.dState]['event'])
        except Exception as E:
            logging.error('Exception in get_event_in_state {} {}'.format(E,yolink.dataAPI[yolink.dData][yolink.dState] ))

    '''
    def updateScheduleStatus(yolink, data):
        logging.debug(yolink.type + 'updateScheduleStatus')

        yolink.setOnline(data)
        #yolink.setNbrPorts(data)
        yolink.updateLoraInfo(data)
        yolink.dataAPI[yolink.dData][yolink.dSchedule] = data[yolink.dData]
        yolink.dataAPI[yolink.lastMessage] = data

    


    def updateFWStatus(yolink, data):
        logging.debug(yolink.type + 'updateFWStatus - not working ??')
        # Need to have it workign forst - not sure what return struture will look lik
        #yolink.dataAPI['data']['state']['state'].append( data['data'])
        yolink.dataAPI['state']['lastTime'] = data['time']
        yolink.dataAPI['lastMessage'] = data      
    '''
    def eventPending(yolink):
        return( not yolink.eventQueue.empty())
    
    def getEvent(yolink):
        if not yolink.eventQueue.empty():
            return(yolink.eventQueue.get())
        else:
            return(None)
           
    def extractStrNbr (yolink, port):
        portStr = str(port)
        portStr = re.findall('[0-9]+', portStr)
        return(int(portStr.pop()))

    #@measure_time
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

    '''
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
        yolink.online = yolink.check_system_online()
        return(yolink.setDevice( 'Manipulator.setSchedules'))   
    '''