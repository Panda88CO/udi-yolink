
from os import link
import time
import datetime
import json
import re
#import threading
from typing import Any, Union, List, Dict
from  datetime import datetime, timedelta, timezone
from dateutil.tz import *

try:
    import udi_interface
    logging = udi_interface.LOGGER
    #logging = getlogger('yolink_mqtt_classV2')
    Custom = udi_interface.Custom

except ImportError:
    import logging
    import sys
    logging.basicConfig(level=logging.DEBUG)
    
    #root = logging.getLogger()
    #root.setLevel(logging.DEBUG)
    #handler = logging.StreamHandler(sys.stdout)
    #handler.setLevel(logging.DEBUG)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #handler.setFormatter(formatter)
    #root.addHandler(handler)



from queue import Queue
from yolink_delay_timer import CountdownTimer
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
        yolink.methodList = []
        yolink.MQTT_type = 'default'
        #yolink.delaySupport = ['Outlet', 'MultiOutlet', 'Manipulator', 'Switch', 'Dimmer', 'WaterMeterController']
        yolink.delaySupport = ['Outlet', 'MultiOutlet', 'Manipulator', 'Switch', 'Dimmer']
        yolink.scheduleSupport = []#['Outlet', 'MultiOutlet', 'Manipulator', 'Switch','InfraredRemoter','Sprinkler', 'Thermostat', 'Dimmer' ]
        yolink.online = False # assume it is offline  until otherwise
        yolink.suspended = True # assume it is suspended until otherwise
        yolink.nbrPorts = 1
        yolink.nbrOutlets = 1
        yolink.nbrUsb = 0 
        logging.debug(f"{yoAccess.access_mode} subscribe_mqtt: {yolink.deviceInfo['deviceId']}")
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
        yolink.dState = 'state'
        yolink.dAlarm = 'alarm'
        yolink.dSchedule = 'schedules'
        yolink.dDelays = 'delays'
        yolink.dDelay = 'delay'
        yolink.messageTime = 'time'
        yolink.scheduleSec = False


        yolink.forceStop = False
        yolink.eventSupport = False # Support adding to EventQueue
        yolink.disconnect = False
        yolink.data = {}
        yolink.schedule = {}
        if yolink.type in yolink.delaySupport and yolink.type not in yolink.scheduleSupport :
            yolink.extDelayTimer = CountdownTimer()
        elif yolink.type in yolink.scheduleSupport:
            yolink.extDelayTimer = CountdownTimer()
        else:
            yolink.extDelayTimer = None
        yolink.eventQueue = Queue()
        #yolink.mutex = threading.Lock()
        yolink.timezoneOffset_Sec = yolink.timezoneOffsetSec()
        #yolink.yoAccess.connect_to_broker()
        #yolink.loopTimeSec = updateTimeSec
    
        #yolink.updateInterval = 3
        yolink.messagePending = False
        yolink._schedule_refresh_last_sent = {}
        yolink.scheduleRefreshCooldownSec = 4 if yolink.type == 'InfraredRemoter' else 2
    
    def reset_structure(yolink):
        if yolink.type in yolink.delaySupport and yolink.type not in yolink.scheduleSupport :
            pass
            #yolink.extDelayTimer = CountdownTimer()
        elif yolink.type in yolink.scheduleSupport:
            pass
            #yolink.extDelayTimer = CountdownTimer()
        else:
            pass
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


    #@measure_time
    def deviceError(yolink, data):
        logging.debug(yolink.type+' - deviceError : {}'.format(data))
        yolink.online = False
        # may need to add more error handling 

    #@measure_time
    def initNode(yolink):
        #maxCount = 3
        yolink.refreshDevice()
        #time.sleep(4)

        #yolink.online = yolink.check_system_online()
        #while yolink.suspended and yolink.online :
        #    logging.debug( 'Yolink servers may be overloaded so sleep ') 
         #   time.sleep(10)
         #   yolink.refreshDevice()
        #count = 0
        time.sleep(1)
        #while not yolink.online  and count < maxCount and not yolink.disconnect:
        #    time.sleep(4)
        #    yolink.refreshDevice()
        #    count = count + 1
        #    print ('retry count : {}'.format(count))
        #if not yolink.online:
        #    logging.error('{} not online'.format(yolink.type))

    #@measure_time
    def refreshDevice(yolink):
        logging.debug('{} - refreshDevice - supports'.format(yolink.type))
        #attempt = 1
        #maxAttempts = 3

        methodStr = yolink.type+'.getState'
        #logging.debug(methodStr)  
        data = {}
        #data['time'] = str(int(time.time_ns()/1e6)) # we assign time just before publish
        data['method'] = methodStr
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        data['params'] = {}
        #logging.debug  ('refreshDevice')
        yolink.yoAccess.publish_data(data) 
        #while not yolink.yoAccess.publish_data(data) and attempt <= maxAttempts:
        #    time.sleep(2)
        #    attempt = attempt + 1
        yolink.lastControlPacket = data
        time.sleep(1)
        yolink.check_system_online()

    #@measure_time
    def latestUpdate(yolink):
        logging.debug('{} - Checking last update'.format(yolink.type))
        logging.debug('Data: {}'.format(yolink.data))
        if 'stateChangedAt' in yolink.data[yolink.dData]:
            logging.debug('lastUpdate stateChangedAt {}'.format(yolink.data.get(yolink.dData, {})['stateChangedAt']))
            return(yolink.data[yolink.dData]['stateChangedAt'])
        elif 'lastStateTime' in yolink.data:
            logging.debug('lastUpdate lastStateTime {}'.format(yolink.data.get('lastStateTime')))
            if isinstance(yolink.data['lastStateTime'], (int, float)):
                return(yolink.data['lastStateTime'] )
            else:
                return(0)        
        elif yolink.lastUpd in yolink.data:
            logging.debug('lastUpdate lastUpdTime {}'.format(yolink.data.get(yolink.lastUpd)))
            if isinstance(yolink.data[yolink.lastUpd ], (int, float)):
                return(yolink.data[yolink.lastUpd ])
            else:
                return(0)            
        elif 'reportAt' in yolink.data:
            timestamp = yolink.data.get('reportAt')
            if isinstance(timestamp, str):                
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")            
                logging.debug('lastUpdate reportAt {}'.format(int(dt.timestamp())))
                return(dt.timestamp()*1000) # make in ms
        elif 'time' in yolink.data:
            logging.debug('lastUpdate time {}'.format(yolink.data.get('time')))

            return(yolink.data.get('time'))
        else:
            return(0)


    #@measure_time
    def lastUpdate(yolink):
        logging.debug('{} - Checking last update'.format(yolink.type))
        logging.debug('Data: {}'.format(yolink.data))
        if 'stateChangedAt' in yolink.data.get(yolink.dData, {}):
            logging.debug('lastUpdate stateChangedAt {}'.format(yolink.data.get(yolink.dData, {})['stateChangedAt']))
            return(yolink.data.get(yolink.dData, {})['stateChangedAt'])
        elif 'lastStateTime' in yolink.data:
            logging.debug('lastUpdate lastStateTime {}'.format(yolink.data.get('lastStateTime')))
            if isinstance(yolink.data.get('lastStateTime', 0), (int, float)):
                return(yolink.data.get('lastStateTime', 0) )
            else:
                return(0)        
        elif yolink.lastUpd in yolink.data:
            logging.debug('lastUpdate lastUpdTime {}'.format(yolink.data.get(yolink.lastUpd)))
            if isinstance(yolink.data.get(yolink.lastUpd), (int, float)):
                return(yolink.data.get(yolink.lastUpd))
            else:
                return(0)            
        elif 'reportAt' in yolink.data:
            timestamp = yolink.data.get('reportAt')
            if isinstance(timestamp, str):
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")                
                logging.debug('lastUpdate reportAt {}'.format(int(dt.timestamp())))
                return(dt.timestamp()*1000) # make in ms
        elif 'time' in yolink.data:
            logging.debug('lastUpdate time {}'.format(yolink.data.get('time')))

            return(yolink.data.get('time'))
        else:
            return(0)
    
    def throttled(yolink) -> bool:
        logging.debug(f"Checking if throttled for {json.dumps(yolink.deviceInfo, indent=2)}")
        targetId = yolink.deviceInfo['deviceId']
        delay_s = yolink.yoAccess.time_tracking(targetId)
        logging.debug(f"Throttled check for {targetId}, delay_s: {delay_s}")
        if delay_s is not None and delay_s >0:  # Assuming a 60-second throttle period
            return True
        return False

    #@measure_time
    def check_system_online(yolink):
        #return(yolink.yoAccess.online)
        
        if yolink.data is None or yolink.data == {}:    
            yolink.online = False
            return(yolink.online)
        logging.debug(f'check_system_online : {yolink.data}')
        yolink.online = True
        if 'lastStateTime' in yolink.data:
            #logging.debug('lastStateTime selected')
            if isinstance(yolink.data['lastStateTime'], (int, float)):
                if yolink.data['lastStateTime'] + 60*60*4 <= time.time(): # if no update for 4 hours then assume offline
                    yolink.online = False
                    logging.error('Status {} - Off line detected: {}'.format(yolink.deviceInfo['name'], yolink.data))
                else:
                    yolink.online = True
            return(yolink.online)
        
        if 'code' in yolink.data:
            #logging.debug('code selected')
            if yolink.data['code'] == '000000':
                    yolink.online = True
            elif yolink.data['code'].find('00020') == 0: # Offline
                yolink.online = False
        elif 'event' in yolink.data:
            #logging.debug('event selected')
            if 'data' in yolink.data:
                if 'online' in yolink.data['data']:
                    yolink.online = yolink.data['data']['online']

        else:
            yolink.online = False
            logging.error(f'OFFLINE STRANGE {yolink.data}')

        
        if not yolink.online:
            logging.error('Status {} - Off line detected: {}'.format(yolink.deviceInfo['name'], yolink.data))
        return(yolink.online)




    #@measure_time
    def local_connection(yolink):
        try:
            return( 'local' in  yolink.yoAccess.access_mode)

        except Exception as e:
            logging.error('connection_mode Exception: {}'.format(e))
            return(False)


    #@measure_time
    def data_updated(yolink):
        tmp = yolink.lastUpdate()
        logging.debug('data_updated {} vs {}'.format(tmp, yolink.lastUpdateTime))
        if tmp == {} or tmp is None:
            return(False)        
        if yolink.lastUpdateTime == 0:
            return(True) # must be first time 

        if ( tmp > yolink.lastUpdateTime):
            yolink.lastUpdateTime = tmp 
            logging.debug('{} - Data Updated'.format(yolink.type))
            return(True)
        else:
            return(False)
    '''    
    #@measure_time
    def send_data(yolink,  data):
        logging.debug('send_data {}'.format(data))
        yolink.yoAccess.publish_data( data)
        if yolink.MQTT_type == 'c':
            time.sleep(1) 
        return (True)
    '''
   #@measure_time
    def setAttributes(yolink,  data):
        logging.debug(yolink.type+f' - setAttributes {data}')
        if data is None:
            data = {}
        methodStr = yolink.type+'.setAttributes'
            
        #data['time'] = str(int(time.time_ns()//1e6))# we assign time just before publish
        data['method'] = methodStr
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        logging.debug(yolink.type+' - setDevice -data {}'.format(data))
        yolink.yoAccess.publish_data(data)
        return(True)
    
    
    def setDeviceAttributes(yolink,  data):
        logging.debug(yolink.type+f' - setDeviceAttributes {data}')
        if data is None:
            data = {}  
        methodStr = yolink.type+'.setDeviceAttributes'
        #data['time'] = str(int(time.time_ns()//1e6))# we assign time just before publish
        data['method'] = methodStr
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        logging.debug(yolink.type+' - setDevice -data {}'.format(data))
        yolink.yoAccess.publish_data(data)
        return(True)
 


    #@measure_time
    def setDevice(yolink,  data):
        logging.debug(yolink.type+' - setDevice')

        worked = False
        if 'toggle' in yolink.methodList:
            methodStr = yolink.type+'.toggle'
            worked = True
        else:
            methodStr = yolink.type+'.setState'
            worked = True

        if data is None:
            data = {}           
        #data['time'] = str(int(time.time_ns()//1e6))# we assign time just before publish
        data['method'] = methodStr
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        logging.debug(yolink.type+' - setDevice -data {}'.format(data))
        if worked:
            yolink.yoAccess.publish_data(data)
            #while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
            #    time.sleep(10.1) # we can only try 6 timer per minute per device 
            #    attempt = attempt + 1
            #yolink.yoAccess.publish_data(data)
            return(True)
        else:
            return(False)

    def getDataValue(yolink,key): 
        logging.debug('{} -     def getDataValue {}: '.format(yolink.type, key))
        try:
            yolink.online = yolink.check_system_online()
            result = yolink.get_data(key)
            if result is None:
                logging.debug('getDataValue NO Match  - {} '.format(key))
                return('NA')
            return(result)
        except Exception as E:
            logging.error('getDataValue Exception: {}'.format(E))
    #@measure_time


    def getState(yolink):
        return(yolink.getStateValue('state'))

    def getDataStateValue(yolink, key):
        logging.debug('{} - getDataStateValue, key:{}'.format(yolink.type, key))
        try:
            yolink.online = yolink.check_system_online()
            if yolink.online:
                result = yolink.get_data(key, category=yolink.dState)
                if result is None:
                    logging.debug('getDataStateValue NO MATCH - {} '.format(key))
                return(result)
            else:
                return(None)
        except Exception as E:
            logging.debug('getData exception: {}'.format(E) )
            return(None)

    #@measure_time
    def getValue(yolink,key): 
        logging.debug('{} -     def getValue {}: '.format(yolink.type, key))
        try:
            yolink.online = yolink.check_system_online()
            result = yolink.get_data(key)
            if result is None:
                logging.debug('getValue NO MATCH - {} '.format(key))
            return(result)
        except Exception as E:
            logging.debug('getData exception: {}'.format(E) )
            return(None)    

    #@measure_time
    def getStateValue(yolink, key):
        logging.debug('{} - getStateValue, key:{}'.format(yolink.type, key))
        try:
            yolink.online = yolink.check_system_online()
            if yolink.online:
                result = yolink.get_data(key, category=yolink.dState)
                if result is None:
                    logging.debug('getStateValue NO MATCH - {} '.format(key))
                return(result)
            else:
                return(99)
        except Exception as e:
            logging.debug('getData exception: {}'.format(e) )
            return(None)
    
    #@measure_time
    def getInfoAPI (yolink):
        return(yolink.data)

    #def sensorOnline(yolink):
    #    return(yolink.check_system_online() )       

    #@measure_time
    def getAlarms(yolink):
        return(yolink.get_data('alarm', category=yolink.dState))

    def getLimits(yolink):
        res = {}
        tmp = yolink.getStateValue('tempLimit')
        if tmp:
            res['tempLimit'] = tmp
        tmp = yolink.getStateValue('humidityLimit')
        if tmp:
            res['humidityLimit'] = tmp
        return(res)


    #@measure_time
    def getBattery(yolink):
        bat = yolink.getStateValue('battery')
        if bat == None: # No battery under state
            bat = yolink.getValue('battery')
        return(bat)
    

    #@measure_time
    def getAlertInfo(yolink):
        logging.debug('getAlertInfo {}'.format(yolink.data))
        try:
            if 'alertType' in yolink.data.get(yolink.dData, {})[yolink.dState]:
                return(yolink.data.get(yolink.dData, {})[yolink.dState]['alertType'])
            else:
                return(None)
        except Exception as e:
            logging.error('No AlertTypoe found {} - {}'.format(yolink.data, e))
            return(None)


    #@measure_time
    def getDeviceTemperature(yolink):
        temp = yolink.getStateValue('devTemperature')
        logging.debug('getDeviceTemperature: {}'.format(temp))
        return(temp)

    #@measure_time
    def getLastUpdate (yolink):
        try:
            return(yolink.lastUpdate())
        except:
            logging.debug('Exception yolink.data.get(yolink.lastUpd, 0) does not exist')
            return(time.time())
        
    def getDataTimestamp(yolink):
        logging.debug('getDataTimestamp')
        try:

            utc_time = yolink.lastUpdate()
            logging.debug('utc_time {}'.format(utc_time))

            #datetime.strptime(reportAtStr, "%Y-%m-%dT%H:%M:%S.%fZ")
            if utc_time is not None:
                epoch_time = int(utc_time)
                return(epoch_time)
            else:
                return(None)    
        
        except Exception as e:
            logging.error(f'getDataTimestamp : {e}')

    def getTimeSinceUpdateMin(yolink):
        time_since = yolink.getTimeSinceUpdate()
        logging.debug(f'getTimeSinceUpdateMin {time_since}')
        if time_since != None:
            return(int(time_since/60))
        else:
            return(None)

    def getLastUpdateTime(yolink):
        return(int(yolink.lastUpdate()/1000))
    
    
    def getTimeSinceUpdate(yolink):
        logging.debug('getTimeSinceUpdate')
        try:

            utc_time = int(yolink.lastUpdate()/1000) # reported in ms

            
            #datetime.strptime(reportAtStr, "%Y-%m-%dT%H:%M:%S.%fZ")
            epoch_time = int(time.time())
            logging.debug(f'utc_time {utc_time}  epoch : {epoch_time} - diff: {int(epoch_time-utc_time)}')
            return(epoch_time-utc_time)

        except Exception as e:
            logging.error(f'Exception getDataTimestamp : {e}')
            return(None)


    def refreshState(yolink):
        logging.debug(str(yolink.type)+ ' - refreshState')
        yolink.refreshDevice()
    
    #@measure_time
    def getDataAll(yolink):
        try:
            logging.debug(yolink.type +' - getDataAll')
            if yolink.dData in yolink.data:
                return(yolink.data[yolink.dData])
            return({})
        except Exception as e:
            logging.debug('getDataAll exception: {}'.format(e) )
            return({})

    #@measure_time
    def getLastDataPacket(yolink):
        if 'lastMessage' in yolink.data:
            return(yolink.data['lastMessage'])
        return({}) 

    #@measure_time
    #def getState(yolink):
    #    try:                
    #        return(yolink.data.get(yolink.dData, {})[yolink.dState][yolink.dState] )
    #    except Exception as e:
    #        logging.debug('getState exception: {}'.format(e) )
    #        return(None)
        
    #@measure_time
    #def getData(yolink):
    #    try:
    #        logging.debug(yolink.type +' - getData')
    #        return(yolink.data.get(yolink.dData, {})[yolink.dState])
    #    except Exception as e:
    #        logging.debug('getData exception: {}'.format(e) )
    #        return(None)

    '''
    def getOnlineStatus(yolink):
        maxCount = 3
        attempt = 1
        logging.debug(yolink.type+' - getOnlineStatus')
        if 'online' in yolink.data:
            return(yolink.check_system_online())
        else:
            return(False)

    def onlineStatus(yolink):
        return(yolink.getOnlineStatus())
    '''

    #@measure_time
    def checkSuspendedStatus(yolink):
        '''checkSuspendedStatus'''
        return(yolink.suspended)

    #@measure_time
    def Status(yolink, dataPacket):
        '''Status'''
        logging.debug(f'Status : {dataPacket}')
        yolink.suspended= False
        if 'code' in dataPacket:
            logging.debug('code selected')
            if dataPacket['code'] == '000000':
                    yolink.online = True
            elif dataPacket['code'].find('00020') == 0: # Offline
                yolink.online = False
            elif  dataPacket['code'] == '010301': # need to add a wait
                yolink.online = True 
                yolink.suspended= True
                time.sleep(1)

        elif 'event' in dataPacket:
            logging.debug('event selected')
            if yolink.dData in dataPacket:
                if 'online' in dataPacket[yolink.dData]:
                    yolink.online = dataPacket[yolink.dData]['online']
                else: #assume device is online as it is reporting   
                    yolink.online = True
            else:
                yolink.online = True
        else:
            yolink.online = False
            logging.debug(f'OFFLINE STRANGE {dataPacket}')
        if not yolink.online:
            logging.error('Status {} - Off line detected: {}'.format(yolink.deviceInfo['name'], dataPacket))
        return(yolink.online)

    #@measure_time
    def updateCallbackStatus(yolink, data, eventSupport = False):
        try:
            logging.debug('{} - updateCallbackStatus '.format(yolink.type))
            yolink.updatePacketData(data)
            if 'method' in  data and 'event' not in data:
                logging.debug('Method detected')
                yolink.online = yolink.Status(data)
                if data['code'] == '000000':
                    yolink.noconnect = 0
                       
                    if  '.setDelay'  in data['method']:

                        yolink.updateDelayData(data)       
                    elif  '.getSchedules'  in data['method'] or '.getValveSchedules' in data['method'] or '.getLeakSchedules' in data['method']:
                        logging.debug('callback getSchedules {}'.format(data ))

                        yolink.updateScheduleStatus(data)
                    elif  '.setSchedules' in data['method'] or '.setValveSchedules' in data['method'] or '.setLeakSchedules' in data['method']:
                        logging.debug('callback setSchedules t={} lu={} d={}'.format(data['time'],  yolink.getLastUpdate(),data ))

                        yolink.updateScheduleStatus(data)

                    elif  '.playAudio' in data['method'] :
                        logging.debug('playAudio No data returned - just update time')

                    elif  '.setOption' in data['method'] :

                        logging.debug('setOption No data returned - just update time')

                        yolink.updateMessageInfo(data)  

                else:
                    yolink.deviceError(data)

                    logging.error(yolink.type+ ': ' + data['desc'])
            elif 'event' in data:
                #logging.debug('Event deteced')
                yolink.online = True # Event generated so it must be online 
     
                last_update = yolink.getLastUpdate()
                if 'time' in data and isinstance(data['time'], int) and isinstance(last_update, int):             
                    if '.getSchedules' in data['event'] or '.getValveSchedules' in data['event'] or '.getLeakSchedules' in data['event']:
                        if data['time'] >= last_update:
                            yolink.updateScheduleStatus(data)   
                    elif '.setSchedules' in data['event'] or '.setValveSchedules' in data['event'] or '.setLeakSchedules' in data['event']:
                        if data['time'] >= last_update:
                            yolink.updateScheduleStatus(data)   

                    elif '.HourlyUsageReport' in  data['event']:
                        if data['time'] >= last_update:
                            yolink.updateHourlyData(data)


                elif '.setInitState' in  data['event']:
                        #yolink.updateStatusData(data)
                        #yolink.initData(data)
                        # there is no memery, so jet get the latest data from teh device 
                        yolink.refreshDevice()
                        yolink.refreshSchedules()
                        #yolink.updateScheduleStatus(data)   
                #else:
                #    logging.debug('Unsupported Event passed - trying anyway; {}'.format(data) )
                #    if int(data['time']) >= int(yolink.getLastUpdate()):
                #        yolink.updatePacketData(data)
                        '''
                        try:
                            if int(data['time']) >= int(yolink.getLastUpdate()) and data['data'] != {}:
                                if data['event'].find('chedule') >= 0 :
                                    yolink.updateScheduleStatus(data)    
                                elif data['event'].find('ersion') >= 0 :
                                    yolink.updateFWStatus(data)
                                else:
                                    yolink.updatePacketData(data)   
                            else:
                                yolink.online = False
                                logging.error('Device appears offline: '+ data['desc'])
                        except logging.exception as E:
                            logging.error('Unsupported event detected: ' + str(E))
                        '''    
                if eventSupport:
                    yolink.eventQueue.put(data['event']) 
                yolink.lastDataPacket = data
            else:
                #yolink.online = yolink.Status(data) and yolink.check_system_online()
                yolink.online = yolink.Status(data)

                logging.debug('updateStatus: Unsupported packet type: ' +  json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
            # Online status tracked in yolink.online 
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
        #data['time'] = str(int(time.time_ns()//1e6)) # we assign time just before publish
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.yoAccess.publish_data(data) 
        #while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
        #    time.sleep(1)
        #    attempt = attempt + 1
        
        delays['ch'] = 1
        delays['on'] = data['params']['delayOn']
        delays['off'] = data['params']['delayOff']
        temp.append(delays)
        yolink.extDelayTimer.addDelays(temp)
        #yolink.online = yolink.check_system_online()
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
        #data['time'] = str(int(time.time_ns()//1e6)) # we assign time just before publish
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.yoAccess.publish_data( data)
        #while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
        #    time.sleep(1)
        #    attempt = attempt + 1
            
        delays['ch'] = 1
        delays['on'] = data['params']['delayOn']
        temp.append(delays)
        yolink.extDelayTimer.addDelays(temp)
        #yolink.online = yolink.check_system_online()
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
        #data['time'] = str(int(time.time_ns()//1e6)) # we assign time just before publish
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.yoAccess.publish_data(data) 
        #while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
        #    time.sleep(1)
        #    attempt = attempt + 1

        delays['ch'] = 1
        delays['off'] = data['params']['delayOff']
        temp.append(delays)
        yolink.extDelayTimer.addDelays(temp)
        #yolink.online = yolink.check_system_online()
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
        # = str(int(time.time_ns()//1e6)) # we assign time just before publish
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.yoAccess.publish_data(data) 
        #while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
        #    time.sleep(1)
        #    attempt = attempt + 1
        delays['ch'] = 1
        delays['on'] = data['params']['delayOn']
        delays['off'] = data['params']['delayOff']
        temp.append(delays)
        #yolink.writeDelayData(data)
        yolink.extDelayTimer.addDelays(temp)
        #yolink.online = yolink.check_system_online()
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



    def refreshSchedules(yolink):
        logging.debug(yolink.type + '- refreshSchedules')

        def _can_send_schedule_request(method_name):
            now = time.time()
            last_sent = yolink._schedule_refresh_last_sent.get(method_name, 0)
            if now - last_sent < yolink.scheduleRefreshCooldownSec:
                logging.debug(
                    '{}- refreshSchedules skip duplicate {} ({}s cooldown)'.format(
                        yolink.type, method_name, yolink.scheduleRefreshCooldownSec
                    )
                )
                return False
            yolink._schedule_refresh_last_sent[method_name] = now
            return True

        data = {}

        # Water meter controllers (single + multi) support valve and leak schedules.
        if yolink.type in ['WaterMeterController', 'WaterMeterMultiController']:
            valve_method = yolink.type + '.getValveSchedules'
            if _can_send_schedule_request(valve_method):
                data['method'] = valve_method
                data["targetDevice"] = yolink.deviceInfo['deviceId']
                data["token"] = yolink.deviceInfo['token']
                data['params'] = {}
                yolink.yoAccess.publish_data(data)

            data = {}
            leak_method = yolink.type + '.getLeakSchedules'
            if _can_send_schedule_request(leak_method):
                data['method'] = leak_method
                data["targetDevice"] = yolink.deviceInfo['deviceId']
                data["token"] = yolink.deviceInfo['token']
                data['params'] = {} 
                yolink.yoAccess.publish_data(data)
        else:
            methodStr = yolink.type + '.getSchedules'
            if _can_send_schedule_request(methodStr):
                data['method'] = methodStr
                data["targetDevice"] = yolink.deviceInfo['deviceId']
                data["token"] = yolink.deviceInfo['token']
                data['params'] = {}
                yolink.yoAccess.publish_data(data)
            
    
    '''
    def getSchedules(yolink):
        logging.debug('{}- getSchedules: {}'.format(yolink.type, yolink.deviceInfo['name'] ))
        
        yolink.refreshSchedules()
        time.sleep(2)
        #while 'schedules' not in yolink.data.get(yolink.dData, {}):
        #    time.sleep(1)
        #    logging.debug('Waiting for schedules to be retrieved')
            
        #nbrSchedules  = len(yolink.data.get(yolink.dData, {}))
        #f 'supportSeconds' in yolink.data.get(yolink.dData, {})[yolink.dSchedule]:
        #   yolink.scheduleSec = yolink.data.get(yolink.dData, {})[yolink.dSchedule]['supportSeconds']
        #else:
        #    yolink.scheduleSec = False
        yolink.scheduleSec = yolink.get_data('supportSeconds')

        temp = {}
        yolink.scheduleList = []
        logging.debug('getSchedules - schedules  {}'.format(yolink.schedules))
        for scheduleNbr in yolink.schedules:
            temp[scheduleNbr] = {}
            for key in yolink.schedules[scheduleNbr]:
                if key == 'week':
                    days = yolink.maskToDays(yolink.schedules[scheduleNbr][key])
                    temp[scheduleNbr][key]= days
                elif yolink.schedules[scheduleNbr][key] == '25:0':
                    #temp[schedule].pop(key)
                    pass
                else:
                    temp[scheduleNbr][key] = yolink.schedules[scheduleNbr][key]
            #temp[scheduleNbr]['index'] = scheduleNbr   
            yolink.scheduleList.append(temp[scheduleNbr])
        logging.debug('getSchedules - schedules : {}'.format(temp))
        return(temp)
    '''
    def activateSchedule(yolink, index, active):
        logging.debug(yolink.type + '- activateSchedule {} {} '.format(index, active))
        #logging.debug('data cache {}'.format(yolink.data.get(yolink.dData, {})))
        logging.debug('data-schedules {}'.format( yolink.schedules))
        indexS = str(index)
        if indexS in yolink.schedules:
            schedule = yolink.schedules[indexS]
            schedule['isValid'] = active
            schedule[indexS] = index
            yolink.setSchedule( index, schedule)
   


    def setSchedule(yolink, index, params, schedule_method=None):
        logging.debug(yolink.type + '- setSchedule')
        indexS = str(index)
        data = {}

        # Water meter controllers (single + multi) use separate write methods per schedule type.
        if yolink.type in ['WaterMeterController', 'WaterMeterMultiController'] and schedule_method in ['valve', 'leak']:
            if schedule_method == 'valve':
                data['method'] = yolink.type + '.setValveSchedules'
            else:
                data['method'] = yolink.type + '.setLeakSchedules'
        else:
            data['method'] = yolink.type + '.setSchedules'

        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        data['params'] = {}
        if isinstance (yolink.schedules, dict) and len(yolink.schedules) != 0:
            data['params']['sches'] = yolink.schedules
        else:
            yolink.getSchedules()
            while yolink.dSchedule not in yolink.schedules:
                time.sleep(1)
                logging.info('Waiting for schedules to be updated')

        data['params']['sches'] = yolink.schedules
        logging.debug('setSchedule1 : {}'.format(data))
        data['params']['sches'][indexS] = params
        logging.debug('setSchedule1 : {}'.format(data))
        '''
        if 'ch' in params: # multiOutlet
            index = index + params['ch']
            data['params']['sches'][index] = {}
            data['params']['sches'][index]['ch'] = params['ch']
        else:
            data['params']['sches'][index] = {}
        data['params']['sches'][index]['index'] = index 
        data['params']['sches'][index]['isValid'] = active
        if 'on' in params:
             data['params']['sches'][index]['on'] = params['on']
        else:
            data['params']['sches'][index]['on'] = "25:0"
        if 'off' in params:
             data['params']['sches'][index]['off'] = params['off']
        else:
            data['params']['sches'][index]['off'] = "25:0"
        data['params']['sches'][index]['week'] = params['week']
        '''
        logging.debug('setSchedule data = {}'.format(data))
        yolink.yoAccess.publish_data(data)
        time.sleep(1)
    
    '''
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
        return(None)
            
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
            pass
            # Online status set in updatePacketData
        elif data[yolink.dData] == {}:
            yolink.online = False
        else:
            yolink.online = True
        yolink.online = yolink.Status(data)
        logging.debug('online: {}'.format( yolink.online))
 

    def updateLoraInfo(yolink, data):
        if yolink.dState in data[yolink.dData]:
            if 'loraInfo' in data[yolink.dData][yolink.dState]:
                yolink.data.get(yolink.dData, {})[yolink.dState]['loraInfo']= data[yolink.dData][yolink.dState]['loraInfo']

    def updateMessageInfo(yolink, data):
        logging.debug(f'updateMessageInfo {data}')
        if yolink.lastUpd in data:
            yolink.data[yolink.lastUpd] = data[yolink.lastUpd]
        elif yolink.messageTime in data:
            yolink.data[yolink.lastUpd] = data[yolink.messageTime]
        else:
            yolink.data[yolink.lastUpd] = 0
        logging.debug(f'updateMessageInfo 2 {yolink.data}')
        # should be last update time 
        yolink.data[yolink.lastMessage] = data
   
    #@measure_time
    def initData  (yolink, data):
        try:
            logging.debug('{} - initData : {}'.format(yolink.type , data))
            #yolink.setOnline(data)
            if 'time' in data[yolink.dData] :
                yolink.data['lastStateTime'] = data[yolink.messageTime]
            if 'event' in data:
                if ".initData" in data['event']:
                    logging.debug("initData detected")
                    state_cache = yolink.data.get(yolink.dData, {}).setdefault(yolink.dState, {})
                    for key in data[yolink.dData]:
                        #logging.debug('Adding data values {} {}'.format(key, data[yolink.dData][key]))
                        if key == yolink.dState:
                            logging.debug('Skipping nested state copy during initData to avoid self-reference')
                            continue
                        state_cache[key] = data[yolink.dData][key]
                        if key == 'initState':
                            state_cache['state'] = data[yolink.dData][key]
                else:
                    #logging.debug('adding event data {}'.format(data[yolink.dData]))
                    if yolink.dState not in  yolink.data.get(yolink.dData, {}):
                        yolink.data.get(yolink.dData, {})[yolink.dState] = {}
                    for key in data[yolink.dData]:
                        #logging.debug('adding event data {}  {}'.format(key, data[yolink.dData]))
                        yolink.data.get(yolink.dData, {})[yolink.dState][key] = data[yolink.dData][key] # sAdding all keys to state                    

                yolink.updateLoraInfo(data)
                yolink.updateMessageInfo(data)
        except Exception as e:
            logging.error('Exception initData - {}'.format(e))
            logging.error('Exception Data - {}'.format(data))

    #@measure_time
    def updateHourlyData(yolink, data):
        logging.debug('{} - updateHourlyData : {}'.format(yolink.type , json.dumps(data, indent=4)))

    def emptyData(yolink):
        logging.debug('{} - emptyData : {}'.format(yolink.type , yolink.data.get('emptyData', False)))
        return(yolink.data.get('emptyData', False) )


    def extract_two_level(yolink, key1: str, key2: str) -> List[Any]:
        """
        Extracts values from a nested data structure where the first level is key1
        and the second level is key2. Works with dicts and lists of dicts.

        Args:
            data: The nested data structure (dict or list of dicts).
            key1: The first-level key.
            key2: The second-level key.

        Returns:
            A list of extracted values (empty if not found).
        """
        results = []
        visited = set()

        #def safe_get(d: Any, k: str) -> Any:
        #    """Safely get a key from a dict, return None if not found."""
        #    return d.get(k) if isinstance(d, dict) else None

        def traverse(obj: Any):
            """Recursively traverse dicts/lists to find matching keys."""
            if isinstance(obj, (dict, list)):
                obj_id = id(obj)
                if obj_id in visited:
                    return
                visited.add(obj_id)
            if isinstance(obj, dict):
                if key1 in obj and isinstance(obj[key1], dict):
                    if key2 in obj[key1]:
                        results.append(obj[key1][key2])
                for v in obj.values():
                    traverse(v)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)
        traverse(yolink.data[yolink.dData])
        return results[0] if results else None
    
    def _get_report_time(yolink):
        if 'report_time' in yolink.data:
            return(yolink.data['report_time'])
        else:
            return(None)

    def get_report_time(yolink,  target_str=None):
        time_str = yolink.get_data(target_str)
        logging.debug('Getting report time for target_str: {}'.format(target_str))
        if isinstance(time_str, str):
            try:
                tz = yolink.get_data('tz')
                logging.debug('Time String: {} TZ: {}'.format(time_str, tz))
                dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                # Optionally adjust for timezone if tz is valid
                epoch_time = int(dt.timestamp())
                return epoch_time
            except Exception as e:
                logging.debug(f'get_report_time: failed to parse time_str: {e}')
                pass
        # If not found or not valid, fall back to lastUpdate logic
        try:
            last_update = yolink.lastUpdate()
            if last_update:
                # If lastUpdate returns ms, convert to seconds for consistency
                if last_update > 9999999999:  # ms threshold
                    return int(last_update // 1000)
                else:
                    return int(last_update)
        except Exception as e:
            logging.debug(f'get_report_time: lastUpdate fallback failed: {e}')
        # If all else fails, fallback to _get_report_time
        return yolink._get_report_time()


    #@measure_time
    def get_info(yolink, key = None):    
        try:
            ret_val = None  
            if yolink.online :
                logging.debug(yolink.type+f' - getinfo category key {key} {yolink.data}')
                if key in yolink.data:
                    ret_val = yolink.data[key]

            return(ret_val)
        except KeyError as e:
            logging.error(f'EXCEPTION - getData {e}')      


    def get_dict_data(yolink, key):    
        try:
            ret_val = None  
            if yolink.online and yolink.dData in yolink.data:
                #logging.debug(yolink.type+f' - getData key {key} category {json.dumps(yolink.data[yolink.dData], indent=4)}')

                if yolink.data[yolink.dData] is {}:
                    logging.info(f'No data exists (no data returned)')
                    return("no data")
                if key in yolink.data[yolink.dData] and isinstance(yolink.data[yolink.dData][key], dict): # MAy need to add list in future if it exists
                        logging.debug(f'ret_val0  {key} {yolink.data[yolink.dData][key]}')
                        return(yolink.data[yolink.dData][key])
                else:
                    return(None)
        except KeyError as e:
            logging.error(f'EXCEPTION - getData {e}')   


    def get_data(yolink, key :str, category=None, WM_index = None):    
        try:
            ret_val = None  
            if yolink.online and yolink.dData in yolink.data:
                logging.debug(yolink.type+f' - getData key {key} category {category} index {WM_index} {yolink.data[yolink.dData]}')

                if yolink.data[yolink.dData] is {}:
                    logging.info(f'No data exists (no data returned)')
                    return("no data")

                data_root = yolink.data[yolink.dData]

                # Direct category lookup first: get_data('temperature', 'state')
                # and get_data('properties', 'state') when nested under state.
                if isinstance(category, str) and category in data_root and isinstance(data_root[category], dict):
                    if key in data_root[category]:
                        return data_root[category][key]

                # Direct top-level lookup: returns both scalars and dicts/lists,
                # e.g. get_data('properties') when properties is at data root.
                if key in data_root:
                    logging.debug(f'ret_val0  {key} {data_root[key]}')
                    return data_root[key]
                        
                res = yolink.extract_two_level(category, key)
                logging.debug(f'extract_two_level result: {res}')
                if res and isinstance(res, dict):
                    if isinstance( WM_index, int):
                        if str(WM_index) in res:
                                ret_val = res[str(WM_index)]
                    else:
                        ret_val = res
                else:
                    ret_val = res
            return(ret_val)
        except KeyError as e:
            logging.error(f'EXCEPTION - getData {e}')    



    def scheduleDataUpdate(self) -> bool:
        msg_type, msg_action  = self.get_message_type()
        logging.debug('scheduleDataPresent - last message type: {}, action: {}'.format(msg_type, msg_action))
        if isinstance(msg_action, str):
            if msg_action in ['getSchedules', 'setSchedules']:
                return True
        return False
    


    def get_message_type(yolink):
        try:
            #logging.debug(f'get_message_type - data: {json.dumps(yolink.data, indent=4)}')
            msg_type = None
            msg_action = None
            if 'event' in yolink.data:
                msg_type = 'event'
                msg_action  = yolink.data['event'].split('.')[-1]
            if 'method' in yolink.data:
                msg_type = 'method'
                msg_action = yolink.data['method'].split('.')[-1]
            return(msg_type, msg_action)
        
        except KeyError as e:
            logging.error(f'EXCEPTION - get_message_type {e}')
            return(None, None)

    def no_data(yolink):
        try:
           return(yolink.data['emptyData'])
        except KeyError as e:
            logging.debug(f'EXCEPTION - no_data {e}')    
            return(False)
        

    #@measure_time
    def updatePacketData(yolink, data):
        try:
            logging.debug('{} - updatePacketData - start: '.format(yolink.type ))
            yolink.data = data
            yolink.online = yolink.Status(data)
            if 'data' in yolink.data and yolink.data['data'] == {}: 
                logging.debug('Empty data received - do not update data to blank data')
                yolink.data['emptyData'] = True
                
            if 'event' in data: 
                yolink.data['type'] = 'event'
                yolink.data['action'] = data['event'].split('.')[-1]
            if 'method' in data:
                yolink.data['type'] = 'method'
                yolink.data['action'] = data['method'].split('.')[-1]  
            if 'time' in data:
                yolink.data['report_time'] = int(data['time']/1000)
            else:
                yolink.data['report_time'] = None
            if 'delays' in data['data']:
                yolink.nbrOutlets = len(data['data']['delays'])
                yolink.nbrUsb = data['data']['delays'][0]['ch']
                yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb                
            if 'reportAt' in data['data'] :
                reportAt = datetime.strptime(data['data']['reportAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                yolink.data['lastStateTime'] = (reportAt.timestamp() -  yolink.timezoneOffset_Sec)*1000
            elif 'stateChangedAt' in data['data']:
                yolink.data['lastStateTime'] = data['data']['stateChangedAt' ]
            else:
                yolink.data['lastStateTime'] = data[yolink.messageTime]
            if 'data' in yolink.data and yolink.data['data'] == {}: 
                logging.debug('Empty data received - do not update data to blank data')
                yolink.data['emptyData'] = True
            else:
                yolink.data['emptyData'] = False    
                

            logging.debug('After parsing NEW {}'.format(json.dumps(yolink.data, indent=4)))

        except Exception as e:
            logging.error('Exception updateStatusData - {}'.format(e))
            logging.error('Exception Data - {}'.format(json.dumps(data, indent=4)))

    '''
    #@measure_time
    def updateStatusData  (yolink, data):
        try:
            logging.debug('{} - updateStatusData - start: {} - {}'.format(yolink.type, json.dumps(data, indent=4), json.dumps(yolink.data, indent=4)))
            
            yolink.data = data
            yolink.online = yolink.Status(data)

            if 'event' in data: 
                yolink.data['type'] = 'event'
                yolink.data['action'] = data['event'].split('.')[-1]
            if 'method' in data:
                yolink.data['type'] = 'method'
                yolink.data['action'] = data['method'].split('.')[-1]  
            if 'time' in data:
                yolink.data['report_time'] = int(data['time']/1000)
            else:
                yolink.data['report_time'] = None
            if 'data' in data:
                if data['data'] == {}: 
                    logging.debug('Empty data received - do not update data to blank data')
                    yolink.data['emptyData'] = True
                    return
            else:
                yolink.data['emptyData'] = False
                yolink.data['emptyData'] = False

            if yolink.data['action'] in ['getSchedules' , 'setSchedules'] and 'data' in data:
                yolink.schdeule = data['data']


            
            temp = yolink.data.get('lastMessage', {})
            yolink.reset_structure() #do not let old data persist
            yolink.data['lastMessage'] = temp    
            if 'delays' in data['data']:
                    yolink.nbrOutlets = len(data['data']['delays'])
                    yolink.nbrUsb = data['data']['delays'][0]['ch']
                    yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
            if 'reportAt' in data[yolink.dData] :
                reportAt = datetime.strptime(data[yolink.dData]['reportAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                yolink.data['lastStateTime'] = (reportAt.timestamp() -  yolink.timezoneOffset_Sec)*1000
            elif 'stateChangedAt' in data[yolink.dData]:
                yolink.data['lastStateTime'] = data[yolink.dData]['stateChangedAt' ]
            else:
                yolink.data['lastStateTime'] = data[yolink.messageTime]

            if 'method' in data:
                if data['method'] == 'getSchedules' or data['method'] == 'setSchedules':
                    yolink.updateScheduleStatus(data)
                else:
                    if yolink.dState in data[yolink.dData]:
                        #if 'reportAt' in data[yolink.dData] or 'stateChangedAt' in data[yolink.dData]:
                        #    reportAt = datetime.strptime(data[yolink.dData]['reportAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        #    yolink.data['lastStateTime'] = (reportAt.timestamp() -  yolink.timezoneOffset_Sec)*1000
                        #else:
                        #    yolink.data['lastStateTime'] = data[yolink.messageTime]
                        if type(data[yolink.dData][yolink.dState]) is dict:
                            logging.debug('State is Dict: {} '.format(json.dumps(data[yolink.dData][yolink.dState])))
                            yolink.data.get(yolink.dData, {})[yolink.dState] = data[yolink.dData][yolink.dState] # maintain data structure
                            temp_dict = data[yolink.dData][yolink.dState]
                            if 'loraInfo' in temp_dict:
                                lora_inf = temp_dict['loraInfo']
                                del temp_dict['loraInfo']
                            
                            for key in temp_dict:
                                #ogging.debug(f'key {key}')
                                #logging.debug(f'value {temp_dict[key]} ')
                                if key == yolink.dDelay and yolink.type in yolink.delaySupport:
                                    temp = []
                                    temp.append(temp_dict[yolink.dDelay])
                                    yolink.extDelayTimer.addDelays(temp)
                                    # yolink.data.get(yolink.dData, {})[yolink.dDelay].append(data[yolink.dData][yolink.dState][yolink.dDelay])
                                else:
                                    yolink.data.get(yolink.dData, {})[yolink.dState][key] = temp_dict[key]  
                            for info in data[yolink.dData]: 
                                if info != yolink.dState:
                                    #logging.debug(f'info loop {info}')
                                    yolink.data.get(yolink.dData, {})[info] = data[yolink.dData][info]

                            #logging.debug('After parsing {}'.format(json.dumps(yolink.data.get(yolink.dData, {}), indent=4)))
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
                                # yolink.data.get(yolink.dData, {})[yolink.dDelays] = data[yolink.dData][yolink.dDelays]
                                #yolink.extDelayTimer.add(data[yolink.dData][yolink.dDelays])
                                #yolink.nbrPorts = len( yolink.data.get(yolink.dData, {})[yolink.dDelays])
                                #yolink.fistOutlet = yolink.data.get(yolink.dData, {})[yolink.dDelays][0]['ch']
                                #need to update USB handling
                            yolink.data.get(yolink.dData, {})[yolink.dState] = data[yolink.dData][yolink.dState][0:yolink.nbrPorts+yolink.nbrUsb]
                            
                        else:
                            logging.debug('input data: {}'.format(data[yolink.dData]) )
                            #if  yolink.data.get(yolink.dData, {})[yolink.dState] is not dict:
                                #logging.debug('State is not dict - {}'.format(yolink.data.get(yolink.dData, {})))
                                #yolink.data.get(yolink.dData, {})[yolink.dState]= {}
                            for key in data[yolink.dData]:
                                #logging.debug('adding data : {} - {} {} '.format(key, data[yolink.dData][key], yolink.data))
                                if key == yolink.dDelay:
                                    temp = []
                                    dat = data[yolink.dData][key]
                                    logging.debug('delay detected 1 - {}'.format(dat))
                                    if 'ch' not in dat:
                                        dat['ch'] = 1

                                    #temp.append(dat)
                                    logging.debug('temp {}'.format(temp))
                                    yolink.extDelayTimer.addDelays(temp) 
                                    yolink.nbrOutlets = 1
                                    yolink.nbrUsb = 0
                                    yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
                                else:
                                    #logging.debug('adding 1 {} {}:'.format(key,data[yolink.dData] ))
                                    #logging.debug('adding 2 {} {}:'.format(key, yolink.data.get(yolink.dData, {})[yolink.dState]))  
                                    #logging.debug('adding 3 {} {}:'.format(key, data[yolink.dData][key]))
                                    if yolink.dState not in yolink.data.get(yolink.dData, {}):
                                        yolink.data.get(yolink.dData, {})[yolink.dState] = {}
                                        #logging.debug('dState added')
                                    yolink.data.get(yolink.dData, {})[yolink.dState][key] = data[yolink.dData][key]


                    else: # setDelay only returns data
                        if 'data' in data:  #new
                            yolink.data[yolink.dData] = data['data'] #new
                        yolink.data['lastStateTime'] = data[yolink.messageTime]
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

                    yolink.updateLoraInfo(data)
                    yolink.updateMessageInfo(data)                                                 
            else: #event
                if ".setDelay" in data['event']:
                    logging.debug("setDelay detected")
                    if data[yolink.dData] != {}: #multiOutlet currently returns {}
                        if type(data[yolink.dData]) is dict:
                            temp = []
                            temp.append(data[yolink.dData])
                            yolink.extDelayTimer.addDelays(temp)
                            yolink.nbrOutlets = 1
                            yolink.nbrUsb = 0
                            yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
                    else: # multi outlet - need to getState 
                        logging.debug('EXTRA refresh device - data = {}'.format(data))
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
                                yolink.data.get(yolink.dData, {})[yolink.dState]['temperature'] =  tmp_temp        
                            if tmp_hum:
                                yolink.data.get(yolink.dData, {})[yolink.dState]['humidity'] =  tmp_hum                             
                            if meas_time != -1:
                                yolink.data.get(yolink.dData, {})[yolink.dState]['time'] =  meas_time                                         
                        else:
                            yolink.data.get(yolink.dData, {})[yolink.dState][key] = data[yolink.dData][key] 
                #elif '.DevEvent'in data['event']:
                #    logging.debug('.DevEvent {}'.format(data))

                elif yolink.dState in data[yolink.dData]:
                    if type(data[yolink.dData][yolink.dState]) is dict:
                        for key in data[yolink.dData][yolink.dState]:
                            if key == yolink.dDelay:
                                temp = []
                                temp.append(data[yolink.dData][key])
                                yolink.extDelayTimer.addDelays(temp)   
                            else:
                                yolink.data.get(yolink.dData, {})[yolink.dState][key] = data[yolink.dData][yolink.dState][key]
                    elif  type(data[yolink.dData][yolink.dState]) is list:           
                        if yolink.dDelays in data[yolink.dData]:
                            if data[yolink.dData][yolink.dDelays] is not {}:
                                logging.debug('delays exist in data (LIST')
                                yolink.extDelayTimer.addDelays(data[yolink.dData][yolink.dDelays])
                                yolink.nbrOutlets = len(data[yolink.dData][yolink.dDelays])
                                yolink.nbrUsb = data[yolink.dData][yolink.dDelays][0]['ch']
                                yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
                        yolink.data.get(yolink.dData, {})[yolink.dState] = data[yolink.dData][yolink.dState][0:yolink.nbrPorts+yolink.nbrUsb]

                    else: #must be single key - add all keys but contains key = 'state
                        #logging.debug('data - {}'.format(data))
                        #logging.debug('data cache - {}'.format(yolink.data.get(yolink.dData, {})))
                        for key in data[yolink.dData]:
                            #logging.debug('Adding data values {} {}'.format(key, data[yolink.dData][key]))
                            yolink.data.get(yolink.dData, {})[yolink.dState][key] = data[yolink.dData][key]
                        #logging.debug('data cache AFTER - {}'.format(yolink.data.get(yolink.dData, {})))
                else:
                    #logging.debug('adding event data {}'.format(data[yolink.dData]))
                    if yolink.dState not in  yolink.data.get(yolink.dData, {}):
                        yolink.data.get(yolink.dData, {})[yolink.dState] = {}
                    for key in data[yolink.dData]:
                        #logging.debug('adding event data {}  {}'.format(key, data[yolink.dData]))
                        yolink.data.get(yolink.dData, {})[yolink.dState][key] = data[yolink.dData][key] # sAdding all keys to state
                    
                        #yolink.data.get(yolink.dData, {})[yolink.dState][key] = data[yolink.dData][key]
                yolink.updateLoraInfo(data)
                yolink.updateMessageInfo(data)
                logging.debug('Nbr Outlets {}'.format(yolink.nbrOutlets ))
                logging.debug('updateStatusData - Event data : {}'.format(yolink.data))
                #if  yolink.data.get(yolink.dData, {})[yolink.dState] is not dict:
                    #logging.debug('END State is not dict 1 - {}'.format(yolink.data.get(yolink.dData, {})[yolink.dState]))
                    #logging.debug('END State is not dict 2 - {}'.format(yolink.data.get(yolink.dData, {})))
            #yolink.data['nbrPorts'] = yolink.nbrPorts
            #yolink.online = yolink.Status(data)
            #logging.debug('After parsing {}'.format(json.dumps(yolink.data, indent=4)))

        except Exception as e:
            logging.error('Exception updateStatusData - {}'.format(e))
            logging.error('Exception Data - {}'.format(data))
    '''

    def get_event_from_state(yolink):
        logging.debug('get_event_from_state')
        try:
            logging.debug('get_event_from_state: {}'.format(yolink.data.get(yolink.dData, {})))
            if 'event' in yolink.data.get(yolink.dData, {})[yolink.dState]:
                return(yolink.data.get(yolink.dData, {})[yolink.dState]['event'])
            else:
                return(None)
        except Exception as E:
            logging.error('Exception in get_event_in_state {} {}'.format(E,yolink.data.get(yolink.dData, {})[yolink.dState] ))
            return(None)
        
    def clear_event_from_state(yolink):
        logging.debug('clear_event_from_state and last message')
        try:
            yolink.data.get(yolink.dData, {})[yolink.dState]['event'] =  None
            if 'event' in yolink.data.get(yolink.lastMessage, {}):
                yolink.data.get(yolink.lastMessage, {})['event'] = {}
            return(True)
        except Exception as E:
            return(False)

    def isControlEvent(yolink):
        logging.debug('isControlEvent')
        try:
            data = yolink.data.get(yolink.lastMessage, {}) 
            logging.debug('isControlEvent - data {}'.format(data))
            if 'method' in data:
                temp = data['method']
                if '.getState' in temp:
                    return(False)
            elif 'event' in data:
                temp = data['event']
                if 'StatusChange' in temp or '.Alert' in temp or'.DevEvent' in temp:
                    return(True)
                else:
                    return(False)
            else:
                return(False)
        except Exception as E:
            logging.error('isControlEvent Exception: {}'.format(E))
            return(False)


    def getNbrScheduleDefined(yolink):
        try:
            logging.debug('getNbrScheduleDefined : {} '.format(yolink.schedule))
            nbr_sch = len(yolink.schedule)
            if nbr_sch == 0:
                return (None)
            else:
                return(nbr_sch)

        except Exception as e:
            return(None) #No schedules exist
        
    def schedule_support_sec(yolink):
        logging.debug('schedule_support_sec') 

        return(yolink.get_data('supportSeconds'))


    def getScheduleInfo(yolink, index):
        logging.debug(f'{yolink.type} getScheduleInfo {index}')      
        indexS = str(index)
        try: 
            #logging.debug( 'getScheduleInfo 1 : {} '.format(yolink.data.get(yolink.dData, {})))
            #logging.debug( 'getScheduleInfo 2 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule]))
            #logging.debug( 'getScheduleInfo 3 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule][indexS]))
            yolink.scheduleSec= yolink.get_data('supportSeconds')
            if not isinstance(yolink.scheduleSec, bool):
                yolink.scheduleSec = False

            sch_data = yolink.get_dict_data(str(index))    

            logging.debug(' return {} support sec'.format(json.dumps(sch_data, indent=4), yolink.scheduleSec) )
            return(sch_data)
    
        except Exception as e:
            logging.debug('No schedules found {}'.format(e))
            return(None)


    def getScheduleInfo_org(yolink, index):
        logging.debug(f'{yolink.type} getScheduleInfo {index} -- {yolink.schedule}')      
        indexS = str(index)
        try: 
            #logging.debug( 'getScheduleInfo 1 : {} '.format(yolink.data.get(yolink.dData, {})))
            #logging.debug( 'getScheduleInfo 2 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule]))
            #logging.debug( 'getScheduleInfo 3 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule][indexS]))
            if  yolink.schedule_support_sec():
                yolink.scheduleSec = yolink.data.get(yolink.dData, {})[yolink.dSchedule]['supportSeconds']
            else:
                yolink.scheduleSec = False
            if  indexS in yolink.schedule:
                sch = yolink.schedule[indexS]
            else:
                sch = None
            logging.debug(' return {}'.format(sch) )
            return(sch)
    
        except Exception as e:
            logging.debug('No schedules found {}'.format(e))
            return(None)
        

    def getScheduleInfoOLD(yolink, index):
        logging.debug(f'{yolink.type} getScheduleInfo {index} -- {yolink.schedule}')     
        indexS = str(index)
        try: 
            #logging.debug( 'getScheduleInfo 1 : {} '.format(yolink.data.get(yolink.dData, {})))
            #logging.debug( 'getScheduleInfo 2 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule]))
            #logging.debug( 'getScheduleInfo 3 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule][indexS]))
            if 'supportSeconds' in yolink.schedule:
                yolink.scheduleSec = yolink.data.get(yolink.dData, {})[yolink.dSchedule]['supportSeconds']
            else:
                yolink.scheduleSec = False
            if  indexS in yolink.data.get(yolink.dData, {})[yolink.dSchedule]:
                sch = yolink.data.get(yolink.dData, {})[yolink.dSchedule][indexS]
            else:
                sch = None
            logging.debug(' return {}'.format(sch) )
            return(sch)
    
        except Exception as e:
            logging.debug('No schedules found {}'.format(e))
            return(None)

    def updateScheduleStatus(yolink, data):
        logging.debug(yolink.type + ' updateScheduleStatus ;{}'.format(yolink.schedule))
        try:
            if 'event' in data: 
                yolink.data['type'] = 'event'
                yolink.data['action'] = data['event'].split('.')[-1]
            if 'method' in data:
                yolink.data['type'] = 'method'
                yolink.data['action'] = data['method'].split('.')[-1]  

            yolink.schedules = data['data']
            #yolink.setOnline(data)
            #yolink.setNbrPorts(data)
            #yolink.updateLoraInfo(data)
            #if yolink.dSchedule not in yolink.data.get(yolink.dData, {}):
            #    yolink.data.get(yolink.dData, {})[yolink.dSchedule] = {}
            #logging.debug('updateScheduleStatus 1: {}'.format(yolink.data) )
            #yolink.data.get(yolink.dData, {})[yolink.dSchedule] = data[yolink.dData]
            #logging.debug('updateScheduleStatus 2: {}'.format(yolink.data) )
            #yolink.data[yolink.lastMessage] = data
            #logging.debug('updateScheduleStatus finish: {}'.format(yolink.data) )
        except Exception as e:
            logging.debug(' Error schedules not fully supported yet {}'.format(e))

    def updateScheduleStatusOLD(yolink, data):
        logging.debug(yolink.type + ' updateScheduleStatus ;{}'.format(data))
        try:
            yolink.data['schedules'] = data[yolink.dData]
            #yolink.setOnline(data)
            #yolink.setNbrPorts(data)
            #yolink.updateLoraInfo(data)
            if yolink.dSchedule not in yolink.data.get(yolink.dData, {}):
                yolink.data.get(yolink.dData, {})[yolink.dSchedule] = {}
            #logging.debug('updateScheduleStatus 1: {}'.format(yolink.data) )
            yolink.data.get(yolink.dData, {})[yolink.dSchedule] = data[yolink.dData]
            #logging.debug('updateScheduleStatus 2: {}'.format(yolink.data) )
            #yolink.data[yolink.lastMessage] = data
            #logging.debug('updateScheduleStatus finish: {}'.format(yolink.data) )
        except Exception as e:
            logging.debug(' Error schedules not fully supported yet {}'.format(e)) 

    def isScheduleActive(yolink, index):
        logging.debug(yolink.type + ' scheduleActive {} '.format( index))   
        active = None
        indexS = str(index)
        try: 
            #logging.debug( 'getScheduleInfo 1 : {} '.format(yolink.data.get(yolink.dData, {})))
            #logging.debug( 'getScheduleInfo 2 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule]))
            #logging.debug( 'getScheduleInfo 3 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule][indexS]))
            active
            
            if  indexS in yolink.schedule:
                active = yolink.schedule[indexS]['isValid']
            logging.debug( 'getScheduleInfo {}'.format(active))
            return(active)
        
        except Exception as e:
            logging.debug('Schedules not fully supported yet {}'.format(e))
            return(None)


    def isScheduleActiveOLD(yolink, index):        
        logging.debug(yolink.type + ' scheduleActive {} '.format( index))   
        active = None
        indexS = str(index)
        try: 
            #logging.debug( 'getScheduleInfo 1 : {} '.format(yolink.data.get(yolink.dData, {})))
            #logging.debug( 'getScheduleInfo 2 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule]))
            #logging.debug( 'getScheduleInfo 3 : {} '.format(yolink.data.get(yolink.dData, {})[yolink.dSchedule][indexS]))
            if  indexS in yolink.data.get(yolink.dData, {})[yolink.dSchedule]:
                active = yolink.data.get(yolink.dData, {})[yolink.dSchedule][indexS]['isValid']
            logging.debug( 'getScheduleInfo {}'.format(active))
            return(active)
        except Exception as e:
            logging.debug('Schedules not fully supported yet {}'.format(e))
            return(None)    


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