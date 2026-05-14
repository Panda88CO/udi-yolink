
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

# Ensure custom log levels are available regardless of import path
from yolink_logging import BUSY, OFFLINE
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
    def __init__(yolink, yoAccess, deviceInfo, callback, subscribe_mqtt=True, route_filter='default' ):
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
        yolink.name = yolink.deviceInfo['name']
        yolink.methodList = []
        yolink.MQTT_type = 'default'
        #yolink.delaySupport = ['Outlet', 'MultiOutlet', 'Manipulator', 'Switch', 'Dimmer', 'WaterMeterController']
        yolink.delaySupport = ['Outlet', 'MultiOutlet', 'Manipulator', 'Switch', 'Dimmer']
        yolink.scheduleSupport = []#['Outlet', 'MultiOutlet', 'Manipulator', 'Switch','InfraredRemoter','Sprinkler', 'Thermostat', 'Dimmer' ]
        yolink.scheduleRefreshTypes = {
            'Dimmer',
            'InfraredRemoter',
            'Manipulator',
            'MultiOutlet',
            'Outlet',
            'Sprinkler',
            'SprinklerV2',
            'Switch',
            'WaterMeterController',
            'WaterMeterMultiController',
        }
        yolink.online = False # assume it is offline  until otherwise
        yolink.suspended = True # assume it is suspended until otherwise
        yolink.nbrPorts = 1
        yolink.nbrOutlets = 1
        yolink.nbrUsb = 0 
        if subscribe_mqtt:
            logging.debug(f"{yoAccess.access_mode} subscribe_mqtt: {yolink.deviceInfo['deviceId']}")
            yolink.yoAccess.subscribe_mqtt(deviceInfo['deviceId'], callback, route_filter=route_filter)
        yolink.lastDataPacket = ''
        yolink.lastControlPacket = {}
        #yolink.TZcomp = (yolink.timezoneOffsetSec() /60 /60)
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
        logging.debug(f'{yolink.type} ({yolink.name}) - Initialized with timezone offset (sec): {yolink.timezoneOffset_Sec}')
        #yolink.yoAccess.connect_to_broker()
        #yolink.loopTimeSec = updateTimeSec
    
        #yolink.updateInterval = 3
        yolink.messagePending = False
        yolink._schedule_refresh_last_sent = {}
        yolink.scheduleRefreshCooldownSec = 4 if yolink.type == 'InfraredRemoter' else 2
        yolink.offlineLogThrottleSec = 300
        yolink._lastOfflineLogTime = 0
        yolink._lastOfflineLogSig = None

    def log_offline_detected(yolink, dataPacket):
        code = dataPacket.get('code') if isinstance(dataPacket, dict) else None
        method = dataPacket.get('method') if isinstance(dataPacket, dict) else None
        event = dataPacket.get('event') if isinstance(dataPacket, dict) else None
        desc = dataPacket.get('desc') if isinstance(dataPacket, dict) else None
        signature = (code, method, event, desc)
        now = time.time()

        if (
            yolink._lastOfflineLogSig == signature
            and now - yolink._lastOfflineLogTime < yolink.offlineLogThrottleSec
        ):
            return

        yolink._lastOfflineLogSig = signature
        yolink._lastOfflineLogTime = now
        logging.log(OFFLINE, 'Status {} - Off line detected: {}'.format(yolink.deviceInfo['name'], dataPacket))

    def supports_schedule_refresh(yolink):
        return yolink.type in yolink.scheduleRefreshTypes

    def wait_until_online(yolink, timeout_sec=30, poll_interval_sec=2):
        deadline = time.time() + max(0, timeout_sec)
        while not yolink.disconnect:
            if yolink.check_system_online():
                return True

            remaining = deadline - time.time()
            if remaining <= 0:
                break

            time.sleep(min(poll_interval_sec, remaining))

        return yolink.check_system_online()
    
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
        logging.debug(f'{yolink.type} ({yolink.name}) - deviceError : {data}')
        yolink.online = False
        # Determine appropriate log level for known transient/busy codes
        code = None
        if isinstance(data, dict):
            code = data.get('code') or (data.get('data') and data.get('data').get('code'))
        msg = f'{yolink.type} ({yolink.name}) - deviceError : {data}'
        if code == '000201':
            logging.log(OFFLINE, msg)
        elif code == '020401':
            logging.log(BUSY, msg)
        else:
            logging.error(msg)
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
        logging.debug(f'{yolink.type} ({yolink.name}) - refreshDevice')
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
        #yolink.lastControlPacket = data
        time.sleep(1)
        yolink.check_system_online()

    #@measure_time
    def latestUpdate(yolink):
        logging.debug(f'{yolink.type} ({yolink.name}) - Checking last update')
        logging.debug(f'{yolink.type} ({yolink.name}) - Data: {yolink.data}')
        if 'stateChangedAt' in yolink.data[yolink.dData]:
            logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate stateChangedAt {yolink.data.get(yolink.dData, {})["stateChangedAt"]}')
            return(yolink.unix_time_seconds(yolink.data[yolink.dData]['stateChangedAt']))
        elif 'lastStateTime' in yolink.data:
            logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate lastStateTime {yolink.data.get("lastStateTime")}')       
            if isinstance(yolink.data['lastStateTime'], (int, float)):
                return(yolink.unix_time_seconds(yolink.data['lastStateTime']))
            else:
                return(0)        
        elif yolink.lastUpd in yolink.data:
            logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate lastUpdTime {yolink.data.get(yolink.lastUpd)}')
            if isinstance(yolink.data[yolink.lastUpd ], (int, float)):
                return(yolink.unix_time_seconds(yolink.data[yolink.lastUpd ]))
            else:
                return(0)            
        elif 'reportAt' in yolink.data:
            timestamp = yolink.data.get('reportAt')
            if isinstance(timestamp, str):                
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")            
                logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate reportAt {int(dt.timestamp())}')
                return(yolink.unix_time_seconds(dt.timestamp()))
        elif 'time' in yolink.data:
            logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate time {yolink.data.get("time")}')
            return(yolink.unix_time_seconds(yolink.data.get('time')))
        else:
            return(0)


    #@measure_time
    def lastUpdate(yolink):
        logging.debug(f'{yolink.type} ({yolink.name}) - Checking last update')
        logging.debug(f'{yolink.type} ({yolink.name}) - Data: {yolink.data}')
        if 'stateChangedAt' in yolink.data.get(yolink.dData, {}):
            logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate stateChangedAt {yolink.data.get(yolink.dData, {})["stateChangedAt"]}')
            return(yolink.unix_time_seconds(yolink.data.get(yolink.dData, {})['stateChangedAt']))
        elif 'lastStateTime' in yolink.data:
            logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate lastStateTime {yolink.data.get("lastStateTime")}')
            if isinstance(yolink.data.get('lastStateTime', 0), (int, float)):
                return(yolink.unix_time_seconds(yolink.data.get('lastStateTime', 0)))
            else:
                return(0)        
        elif yolink.lastUpd in yolink.data:
            logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate lastUpdTime {yolink.data.get(yolink.lastUpd)}')
            if isinstance(yolink.data.get(yolink.lastUpd), (int, float)):
                return(yolink.unix_time_seconds(yolink.data.get(yolink.lastUpd)))
            else:
                return(0)            
        elif 'reportAt' in yolink.data:
            timestamp = yolink.data.get('reportAt')
            if isinstance(timestamp, str):
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")                
                logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate reportAt {int(dt.timestamp())}')
                return(yolink.unix_time_seconds(dt.timestamp()))
        elif 'time' in yolink.data:
            logging.debug(f'{yolink.type} ({yolink.name}) - lastUpdate time {yolink.data.get("time")}') 

            return(yolink.unix_time_seconds(yolink.data.get('time')))
        else:
            return(0)

    def unix_time_seconds(yolink, unix_time):
        if not isinstance(unix_time, (int, float)):
            return None

        normalized_time = int(unix_time)
        if normalized_time <= 0:
            return None

        min_reasonable_seconds = 946684800  # 2000-01-01 UTC
        max_reasonable_seconds = time.time() + (10 * 365 * 24 * 60 * 60)
        while normalized_time > max_reasonable_seconds:
            normalized_time = normalized_time / 1000.0

        if normalized_time < min_reasonable_seconds or normalized_time > max_reasonable_seconds:
            logging.debug('unix_time_seconds rejected implausible timestamp: {}'.format(unix_time))
            return None

        return int(normalized_time)
    
    def throttled(yolink) -> bool:
        logging.debug(f"Checking if throttled for {yolink.deviceInfo['name']} ({yolink.deviceInfo['deviceId']})")
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

        if yolink.online:
            # Online freshness is based on device update/report timestamps only.
            # lastStateTime/stateChangedAt are preserved for state history but must
            # not participate in online evaluation.
            # Prefer reportAt when present because it reflects device data update time.
            freshness_time_sec = None

            data_section = yolink.data.get(yolink.dData, {}) if isinstance(yolink.data, dict) else {}
            report_at_str = None
            if isinstance(data_section, dict):
                report_at_str = data_section.get('reportAt')
            if report_at_str is None and isinstance(yolink.data.get('reportAt'), str):
                report_at_str = yolink.data.get('reportAt')

            if isinstance(report_at_str, str):
                try:
                    report_at_dt = datetime.strptime(report_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    freshness_time_sec = yolink.unix_time_seconds(report_at_dt.timestamp())
                except Exception as e:
                    logging.debug(f'check_system_online reportAt parse failed: {e} value={report_at_str}')

            if freshness_time_sec is None:
                freshness_time_sec = yolink.unix_time_seconds(yolink.data.get(yolink.messageTime))
            if freshness_time_sec is None:
                freshness_time_sec = yolink.unix_time_seconds(yolink.data.get(yolink.lastUpd))
            if freshness_time_sec is None:
                freshness_time_sec = yolink.unix_time_seconds(yolink.data.get('report_time'))

            if freshness_time_sec is not None and freshness_time_sec + 60*60*4 <= time.time():
                yolink.online = False

        
        if not yolink.online:
            yolink.log_offline_detected(yolink.data)
        
        logging.debug(f'check_system_online result for {yolink.deviceInfo["name"]}: {yolink.online}')   
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
            data['params'] = {}
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
                return(None)
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
            epoch_time = yolink.unix_time_seconds(utc_time)
            if epoch_time is not None:
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
        last_update_time = yolink.unix_time_seconds(yolink.lastUpdate())
        if last_update_time is None:
            return 0
        return last_update_time
    
    
    def getTimeSinceUpdate(yolink):
        logging.debug('getTimeSinceUpdate')
        try:

            utc_time = yolink.unix_time_seconds(yolink.lastUpdate())
            if utc_time is None:
                return None

            
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
            yolink.log_offline_detected(dataPacket)
        return(yolink.online)

    #@measure_time
    def updateCallbackStatus(yolink, data, eventSupport = False):
        try:
            logging.debug('{} - updateCallbackStatus '.format(yolink.type))
            if isinstance(data, dict):
                event_name = data.get('event')
                if isinstance(event_name, str) and event_name.split('.')[-1] == 'DataRecord':
                    # DataRecord payloads are historical rollups and can omit live state keys.
                    # Ignore them globally so they do not overwrite current runtime state.
                    logging.debug('{} ({}) - skipping DataRecord packet'.format(yolink.type, yolink.name))
                    return
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
                    # map specific codes to levels: 000201 -> OFFLINE, 020401 -> BUSY, else error
                    code = data.get('code') if isinstance(data, dict) else None
                    desc = data.get('desc', str(data)) if isinstance(data, dict) else str(data)
                    if code == '000201':
                        logging.log(OFFLINE, yolink.type + ': ' + desc)
                    elif code == '020401':
                        logging.log(BUSY, yolink.type + ': ' + desc)
                    else:
                        logging.error(yolink.type + ': ' + desc)
            elif 'event' in data:
                #logging.debug('Event deteced')
                yolink.online = True # Event generated so it must be online 
                yolink.noconnect = 0
     
                last_update = yolink.getLastUpdate()
                message_time = yolink.unix_time_seconds(data.get('time'))
                if isinstance(message_time, int) and isinstance(last_update, int):             
                    if '.getSchedules' in data['event'] or '.getValveSchedules' in data['event'] or '.getLeakSchedules' in data['event']:
                        if message_time >= last_update:
                            yolink.updateScheduleStatus(data)   
                    elif '.setSchedules' in data['event'] or '.setValveSchedules' in data['event'] or '.setLeakSchedules' in data['event']:
                        if message_time >= last_update:
                            yolink.updateScheduleStatus(data)   

                    elif '.HourlyUsageReport' in  data['event']:
                        if message_time >= last_update:
                            yolink.updateHourlyData(data)
                    else:
                        if message_time >= last_update:
                            yolink.updateMessageInfo(data)


                elif '.setInitState' in  data['event']:
                        #yolink.updateStatusData(data)
                        #yolink.initData(data)
                        # there is no memery, so jet get the latest data from teh device 
                        yolink.refreshDevice()
                        yolink.refreshSchedules()
                        #yolink.updateScheduleStatus(data)   
                else:
                    yolink.updateMessageInfo(data)
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

        if not yolink.check_system_online():
            logging.debug(
                '{}- refreshSchedules skipped because device is offline'.format(
                    yolink.type
                )
            )
            return False

        unsupported_models = {'YS5029', 'YS5009'}
        model_name = str(yolink.deviceInfo.get('modelName', ''))[:6]

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
            if model_name in unsupported_models:
                logging.debug(
                    '{}- refreshSchedules skipped for unsupported water meter model {}'.format(
                        yolink.type, model_name
                    )
                )
                return False

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

            return True
            
    
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
            yolink.data[yolink.lastUpd] = yolink.unix_time_seconds(data[yolink.lastUpd])
        elif yolink.messageTime in data:
            yolink.data[yolink.lastUpd] = yolink.unix_time_seconds(data[yolink.messageTime])
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
                yolink.data['lastStateTime'] = yolink.unix_time_seconds(data[yolink.messageTime])
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

                if dt is not None:
                    # Adjust for timezone if tz is not valid
                    if tz is None:
                        epoch_time = yolink.unix_time_seconds(dt.timestamp()) - yolink.timezoneOffset_Sec
                    else:
                        epoch_time = yolink.unix_time_seconds(dt.timestamp())
                else:
                    epoch_time = None
                return epoch_time
            except Exception as e:
                logging.debug(f'get_report_time: failed to parse time_str: {e}')
                pass
        # If not found or not valid, fall back to lastUpdate logic
        try:
            last_update = yolink.lastUpdate()
            if last_update:
                return yolink.unix_time_seconds(last_update)
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
                logging.debug(yolink.type+f' - get Data key {key} category {category} index {WM_index} {yolink.data[yolink.dData]}')

                if yolink.data[yolink.dData] is {}:
                    logging.info(f'No data exists (no data returned)')
                    return("no data")

                data_root = yolink.data[yolink.dData]

                # Direct category lookup first: get_data('temperature', 'state')
                # and get_data('properties', 'state') when nested under state.
                if isinstance(category, str) and category in data_root and isinstance(data_root[category], dict):
                    if key in data_root[category]:
                        ret_val = data_root[category][key]

                # Direct top-level lookup: returns both scalars and dicts/lists,
                # e.g. get_data('properties') when properties is at data root.
                if ret_val is None and key in data_root:
                    logging.debug(f'ret_val0  {key} {data_root[key]}')
                    ret_val = data_root[key]

                if ret_val is None:
                    ret_val = yolink.extract_two_level(category, key)
                    logging.debug(f'extract_two_level result: {ret_val}')

                if isinstance(ret_val, dict) and WM_index is not None:
                    wm_key = str(WM_index)
                    if wm_key in ret_val:
                        return ret_val[wm_key]
                    if WM_index in ret_val:
                        return ret_val[WM_index]

                if isinstance(ret_val, list) and WM_index is not None:
                    try:
                        wm_idx = int(WM_index)
                        if 0 <= wm_idx < len(ret_val):
                            return ret_val[wm_idx]
                    except (TypeError, ValueError):
                        pass
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
                yolink.data['report_time'] = yolink.unix_time_seconds(data['time'])
            else:
                yolink.data['report_time'] = None
            data_section = data.get(yolink.dData, {}) if isinstance(data, dict) else {}
            if isinstance(data_section, dict) and 'delays' in data_section:
                delays = data_section.get('delays')
                if isinstance(delays, list) and len(delays) > 0:
                    yolink.nbrOutlets = len(delays)
                    first_delay = delays[0] if isinstance(delays[0], dict) else {}
                    if isinstance(first_delay.get('ch'), int):
                        yolink.nbrUsb = first_delay['ch']
                    yolink.nbrPorts = yolink.nbrOutlets + yolink.nbrUsb
                elif isinstance(data_section.get('state'), list):
                    # Some MultiOutlet status events report full state with delays=[].
                    inferred_ports = len(data_section.get('state', []))
                    if not isinstance(yolink.nbrUsb, int) or yolink.nbrUsb < 0 or yolink.nbrUsb > inferred_ports:
                        yolink.nbrUsb = 0
                    yolink.nbrOutlets = max(0, inferred_ports - yolink.nbrUsb)
                    yolink.nbrPorts = inferred_ports
                    logging.debug(
                        '{} - inferred port layout from state because delays was empty: ports={}, outlets={}, usb={}'.format(
                            yolink.type, yolink.nbrPorts, yolink.nbrOutlets, yolink.nbrUsb
                        )
                    )
            if 'reportAt' in data['data'] :
                reportAt = datetime.strptime(data['data']['reportAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                yolink.data['lastStateTime'] = int(yolink.unix_time_seconds(reportAt.timestamp()) -  yolink.timezoneOffset_Sec)
            elif 'stateChangedAt' in data['data']:
                yolink.data['lastStateTime'] = int(yolink.unix_time_seconds(data['data']['stateChangedAt']))
            else:
                yolink.data['lastStateTime'] = int(yolink.unix_time_seconds(data[yolink.messageTime]))
            if 'data' in yolink.data and yolink.data['data'] == {}: 
                logging.debug('Empty data received - do not update data to blank data')
                yolink.data['emptyData'] = True
            else:
                yolink.data['emptyData'] = False    
                

            logging.debug('After parsing NEW {}'.format(json.dumps(yolink.data, indent=4)))

        except Exception as e:
            logging.error('Exception updatePacketData - {}'.format(e))
            logging.error('Exception Data - {}'.format(json.dumps(data, indent=4)))

   

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