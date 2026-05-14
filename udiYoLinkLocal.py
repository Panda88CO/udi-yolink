#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""

import sys
import time
#from apscheduler.schedulers.background import BackgroundScheduler
from yoLink_init_V4 import YoLinkInitPAC

try:
    import udi_interface
    logging = udi_interface.LOGGER
    logging.setLevel(30)
    logging = udi_interface.node.NLOGGER

    loggingc = udi_interface.custom.CLOGGER
    loggingc.setLevel(30)
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

#version = '0.0.0
from udiCommonLib import version


SENSITIVE_LOG_KEYS = {
    'access_token',
    'refresh_token',
    'token',
    'authorization',
    'client_secret',
    'local_client_secret',
    'secret_key',
    'password',
    'secid',
    'uaid',
    'local_client_id',
}


def _mask_secret(value, keep=4):
    text = str(value)
    if len(text) <= keep:
        return '*' * len(text)
    return f"***{text[-keep:]}"


def _redact_log_value(value):
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_LOG_KEYS:
                redacted[key] = _mask_secret(item)
            else:
                redacted[key] = _redact_log_value(item)
        return redacted

    if isinstance(value, list):
        return [_redact_log_value(item) for item in value]

    return value


def _summarize_device_list(device_list):
    devices = []
    for device in device_list:
        if not isinstance(device, dict):
            continue
        devices.append({
            'deviceId': device.get('deviceId'),
            'name': device.get('name'),
            'type': device.get('type'),
            'modelName': device.get('modelName'),
            'parentDeviceId': device.get('parentDeviceId'),
            'access': device.get('access'),
        })
    return {'count': len(devices), 'devices': devices}

class YoLinkSetup (udi_interface.Node):
    from udiYolinkLib import my_setDriver, node_queue, wait_for_node_done, updateEpochTime, convert_temp_unit, convert_water_unit
    from udiCommonLib import systemPoll, addNodes, heartbeat, configDoneHandler, checkNodes, handleLevelChange, saveNodeNames
    def  __init__(self, polyglot, primary, address, name):
        super().__init__( polyglot, primary, address, name)  
        
        self.poly=polyglot
        self.hb = 0
        self.nodeDefineDone = False
        self.handleParamsDone = False
        self.configDone = False
        self.pollStart = False
        self.debug = False
        self.address = address
        self.name = name
        self.yoAccess = None
        self.yoLocal = None
        self.TTSstr = 'TTS'
        self.nbr_API_calls = 19
        self.nbr_dev_API_calls = 5
        self.supportParams = ['YOLINKV2_URL', 'TOKEN_URL','MQTT_URL', 'MQTT_PORT', 'UAID', 'SECRET_KEY', 'NBR_TTS', 'TEMP_UNIT', 'NODE_READY_POLL_SEC' ]
        self.node_ready_poll_seconds = 0.2
        self.yolinkURL = 'https://api.yosmart.com/openApi'
        self.yolinkV2URL = 'https://api.yosmart.com/open/yolink/v2/api' 
        self.temp_unit = 0
        self.tokenURL = 'https://api.yosmart.com/open/yolink/token'
        self.mqttURL = 'api.yosmart.com'
        self.mqttPort = 8003
        self.display_update_sec=60
        self.uaid = ''
        self.secretKey = ''
        self.nbrTTS = None
        self.local_client_id = None
        self.local_client_secret = None
        self.local_ip = ''
        self.local_port = ':1080'
        self.local_URL = ''
        self.local_MQTT_port = 18080
        self._schedule_refresh_retry_stop = False
        self._schedule_refresh_retry_interval_sec = 30
        
        #logging.setLevel(10)
        logging.info(f'Version {version}')
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
        self.n_queue = []
        self.yoLocal = None
        self.yoAccess = None
        
        self.Parameters = Custom(self.poly, 'customparams')
        self.Notices = Custom(self.poly, 'notices')
        logging.debug('YoLinkSetup init')
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))   
        self.poly.updateProfile()
        self.poly.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(self.address)
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV1', 0)
        self.assigned_addresses = []
        self.assigned_addresses.append(self.address)   
        logging.debug('YoLinkSetup init DONE')
        self.nodeDefineDone = True



    def parse_device_lists (self, cloud_list = [], local_list =[]) -> list:
        logging.debug(
            'parse_device_lists cloud=%s local=%s',
            _summarize_device_list(cloud_list),
            _summarize_device_list(local_list),
        )
        device_list = []        
        cloud_devs = {}
        for dev in cloud_list:
            cloud_devs[dev['deviceId']] = dev       
        local_devs = {}
        for dev in local_list:
            local_devs[dev['deviceId']] = dev
    
        for dev in local_list:
                dev['access'] = 0
                if dev['deviceId'] in cloud_devs:
                    dev['modelName'] = cloud_devs[dev['deviceId']]['modelName'] 
                device_list.append(dev)        
        for dev in cloud_list:
            if dev['deviceId'] not in local_devs:
                dev['access'] = 1
                device_list.append(dev)

        logging.debug('Resulting Device List %s', _summarize_device_list(device_list))
        return(device_list)

    def remove_legacy_node_name_params(self):
        removed = []
        try:
            nodes = self.poly.getNodes()
        except Exception as e:
            logging.debug(f'Could not load nodes while cleaning legacy custom params: {e}')
            return

        for addr in list(nodes.keys()):
            if addr == self.address or addr not in self.Parameters:
                continue
            try:
                if hasattr(self.Parameters, 'delete'):
                    self.Parameters.delete(addr)
                else:
                    del self.Parameters[addr]
                removed.append(addr)
            except Exception as e:
                logging.debug(f'Failed removing legacy custom param for {addr}: {e}')

        if removed:
            logging.info('Removed legacy node-name custom params for %s', removed)

    def start (self):
        logging.info('Executing start - udi-YoLink')
        
        #logging.setLevel(30)
        while not self.nodeDefineDone or not self.handleParamsDone or not self.configDone:
            time.sleep(1)
            logging.debug ('waiting for inital node to get created')

        #self.supportedYoTypes = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
        #                        'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
        #                        'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock' , 'LockV2', 'Dimmer', 'InfraredRemoter',
        #                        'PowerFailureAlarm', 'SmartRemoter', 'COSmokeSensor', 'Siren', 'WaterMeterController',
        #                        'WaterDepthSensor', 'WaterMeterMultiController']
        logging.info (f'Access mode : {self.access_mode}')
        self.updateEpochTime()
        logging.debug(
            'credentials mode=%s cloud_configured=%s local_configured=%s',
            self.access_mode,
            bool(self.uaid and self.secretKey),
            bool(self.local_client_id and self.local_client_secret),
        )
        if 'cloud' in self.access_mode:
            if self.uaid == None or self.uaid == '' or self.secretKey==None or self.secretKey=='':
                logging.error('UAID and secretKey must be provided to start node server')
                self.poly.Notices['cloud'] = 'UAID and secretKey must be provided to start node server in cloud or hybrid mode'
                exit() 
            else:
                logging.debug('initializing Cloud mode with configured credentials')
                self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey )
        if 'local' in self.access_mode:
            if self.local_client_id == None or self.local_client_id == '' or self.local_client_secret==None or self.local_client_secret=='':
                logging.error('Client ID  and Client Secret must be provided to start node server')
                self.poly.Notices['local'] = 'Client ID  and Client Secret must be provided to start node server in local or hybrid mode'
                exit() 
            else:
                tokenURL = self.local_URL+'/open/yolink/token'
                apiURL = self.local_URL+'/open/yolink/v2/api'
                logging.debug(
                    'initializing Local mode token_url=%s api_url=%s host=%s mqtt_port=%s subnet_id=%s',
                    tokenURL,
                    apiURL,
                    self.local_ip,
                    self.local_MQTT_port,
                    self.subnet_id,
                )
                self.yoLocal = YoLinkInitPAC (self.local_client_id, self.local_client_secret, tokenURL, apiURL, self.local_ip, self.local_MQTT_port, self.subnet_id  )
   

        if self.yoAccess or self.yoLocal:
            self.my_setDriver('ST', 0)
        if 'TEMP_UNIT' in self.Parameters:
            self.temp_unit = self.convert_temp_unit(self.Parameters['TEMP_UNIT'])
        else:
            self.temp_unit = 0  
            self.Parameters['TEMP_UNIT'] = 'C'
            logging.debug('TEMP_UNIT: {}'.format(self.temp_unit ))
        if self.yoAccess:
            self.yoAccess.set_temp_unit(self.temp_unit )
        if self.yoLocal:
            self.yoLocal.set_temp_unit(self.temp_unit )      

        if 'WATER_UNIT' in self.Parameters:
            self.water_unit = self.convert_water_unit(self.Parameters['WATER_UNIT'])
            logging.debug('WATER_UNIT: {}'.format(self.water_unit ))

        else:
            self.water_unit = 0  
            self.Parameters['WATER_UNIT'] = 'L'
            logging.debug('WATER_UNIT: {}'.format(self.water_unit ))
        if self.yoAccess:
            self.yoAccess.set_water_unit(self.water_unit )
        if self.yoLocal:
            self.yoLocal.set_water_unit(self.water_unit )   

        if 'DEBUG_EN' in self.Parameters:
            self.debug = self.Parameters['DEBUG_EN']
        else:
            self.debug = False
        if self.yoAccess:
            self.yoAccess.set_debug(self.debug)
        if self.yoLocal:
            self.yoLocal.set_debug(self.debug)                 
        
        if 'CALLS_PER_MIN' in self.Parameters:
            self.nbr_API_calls = self.Parameters['CALLS_PER_MIN']
            self.nbr_dev_API_calls = self.Parameters['DEV_CALLS_PER_MIN']
        if self.yoAccess:
            self.yoAccess.set_api_limits(self.nbr_API_calls, self.nbr_dev_API_calls)          
        
        # NEED TO DETERMINE IF LOCAL HUB EXISTS AND THEN GET LIST FROM THAT AS WELL 
        
        
        deviceListCloud=[]
        deviceListLocal=[]
        if self.yoAccess:  # get cloud and local devices
            self.yoAccess.retrieve_device_list()
            deviceListCloud = self.yoAccess.getDeviceList()
        
            #self.deviceList = self.yoAccess.get_device_list()

        if self.yoLocal: #get only local devices 
            self.yoLocal.retrieve_device_list()
            deviceListLocal = self.yoLocal.getDeviceList()

        self.deviceList = self.parse_device_lists(deviceListCloud, deviceListLocal )

        logging.debug('Devices detected: %s', _summarize_device_list(self.deviceList))
        if self.yoAccess or self.yoLocal:
            self.my_setDriver('ST', 1)
            self.my_setDriver('GV1', 1)
            self.deviceList = self.addNodes(self.deviceList)
            self.remove_legacy_node_name_params()
            # Defer non-critical schedule refreshes to avoid startup API bursts
            # Run in background so node server can continue initializing
            try:
                from threading import Thread
                self._schedule_refresh_retry_stop = False
                t = Thread(target=self.deferred_refresh_schedules, daemon=True)
                t.start()
            except Exception:
                logging.debug('Failed to start deferred_refresh_schedules thread')
        else:
            self.my_setDriver('ST', 0)

    def deferred_refresh_schedules(self):
        """Background pass to refresh schedules for schedule-capable devices.

        Iterates created nodes and invokes `refreshSchedules()` on the
        first attribute that exposes it for each node. Offline devices are
        queued for later retries so late-online devices still receive the
        startup refresh. Calls are spaced using `yoAccess.time_tracking(dev_id)`
        to avoid bursting API calls.
        """
        logging.info('Starting deferred schedule refresh pass')
        try:
            nodes = self.poly.getNodes()
        except Exception as e:
            logging.debug(f'Could not enumerate nodes for deferred refresh: {e}')
            return

        try:
            node_items = list(nodes.items())
        except Exception as e:
            logging.debug(f'Could not snapshot nodes for deferred refresh: {e}')
            return

        pending = []
        processed_dev_ids = set()

        for addr, node in node_items:
            if addr == self.address:
                continue
            try:
                node_class_name = getattr(getattr(node, '__class__', None), '__name__', '')
                if node_class_name.endswith('ScheduleNode'):
                    logging.debug(f'Skipping schedule child node {addr} during deferred refresh')
                    continue

                # prefer device-level devInfo if present
                dev_id = None
                try:
                    if hasattr(node, 'devInfo') and isinstance(node.devInfo, dict):
                        dev_id = node.devInfo.get('deviceId')
                except Exception:
                    dev_id = None

                # find first schedule-capable device wrapper
                source = None
                for attr in dir(node):
                    try:
                        val = getattr(node, attr)
                        if not hasattr(val, 'refreshSchedules'):
                            continue
                        supports_schedule_refresh = getattr(val, 'supports_schedule_refresh', None)
                        if callable(supports_schedule_refresh) and supports_schedule_refresh():
                            source = val
                            break
                    except Exception:
                        continue

                if source is None:
                    continue

                # try to obtain deviceId from the source wrapper if missing
                if dev_id is None:
                    try:
                        if hasattr(source, 'devInfo') and isinstance(source.devInfo, dict):
                            dev_id = source.devInfo.get('deviceId')
                    except Exception:
                        dev_id = None

                if dev_id is None:
                    logging.debug(f'No deviceId for node {addr}, skipping schedule refresh')
                    continue

                if dev_id in processed_dev_ids:
                    logging.debug(f'Skipping duplicate startup schedule refresh for {addr}; device {dev_id} already handled')
                    continue

                check_system_online = getattr(source, 'check_system_online', None)
                is_online = False
                try:
                    if callable(check_system_online):
                        is_online = check_system_online()
                except Exception as e:
                    logging.debug(f'Online check failed for {addr}: {e}')
                    is_online = False

                if not is_online:
                    logging.info(f'Queueing startup schedule refresh retry for {addr}; device is offline')
                    pending.append({'addr': addr, 'dev_id': dev_id, 'source': source})
                    continue

                # space calls using yoAccess/yoLocal time tracking
                delay = 0
                try:
                    if self.yoAccess:
                        delay = self.yoAccess.time_tracking(dev_id)
                    elif self.yoLocal:
                        delay = self.yoLocal.time_tracking(dev_id)
                except Exception:
                    delay = 0
                if delay and delay > 0:
                    time.sleep(delay)

                try:
                    refreshed = source.refreshSchedules()
                    processed_dev_ids.add(dev_id)
                    if refreshed:
                        logging.info(f'Startup schedule refresh sent for {addr}')
                    else:
                        logging.debug(f'Startup schedule refresh skipped for {addr}')
                except Exception as e:
                    logging.debug(f'Failed refreshSchedules for {addr}: {e}')
                    pending.append({'addr': addr, 'dev_id': dev_id, 'source': source})

            except Exception as e:
                logging.debug(f'deferred refresh error for {addr}: {e}')

        while pending and not self._schedule_refresh_retry_stop:
            logging.info(
                f'Retrying startup schedule refresh for {len(pending)} offline device(s) in '
                f'{self._schedule_refresh_retry_interval_sec} seconds'
            )
            time.sleep(self._schedule_refresh_retry_interval_sec)

            remaining = []
            for item in pending:
                if self._schedule_refresh_retry_stop:
                    break

                addr = item['addr']
                dev_id = item['dev_id']
                source = item['source']
                check_system_online = getattr(source, 'check_system_online', None)

                is_online = False
                try:
                    if callable(check_system_online):
                        is_online = check_system_online()
                except Exception as e:
                    logging.debug(f'Retry online check failed for {addr}: {e}')

                if not is_online:
                    remaining.append(item)
                    continue

                delay = 0
                try:
                    if self.yoAccess:
                        delay = self.yoAccess.time_tracking(dev_id)
                    elif self.yoLocal:
                        delay = self.yoLocal.time_tracking(dev_id)
                except Exception:
                    delay = 0
                if delay and delay > 0:
                    time.sleep(delay)

                try:
                    refreshed = source.refreshSchedules()
                    if refreshed:
                        logging.info(f'Startup schedule refresh retry sent for {addr}')
                    else:
                        logging.debug(f'Startup schedule refresh retry skipped for {addr}')
                except Exception as e:
                    logging.debug(f'Failed refreshSchedules retry for {addr}: {e}')
                    remaining.append(item)

            pending = remaining

        if pending and self._schedule_refresh_retry_stop:
            logging.info('Stopping deferred schedule refresh retry queue')

            
        #self.poly.updateProfile()        
        #self.scheduler = BackgroundScheduler()
        #self.scheduler.add_job(self.display_update, 'interval', seconds=self.display_update_sec)
        #self.scheduler.start()
        #self.updateEpochTime()
        
    def stop(self):
        yo_access = getattr(self, 'yoAccess', None)
        yo_local = getattr(self, 'yoLocal', None)
        driver_ready = getattr(self, 'nodeDefineDone', False) and getattr(self, 'node', None) is not None
        try:
            logging.info('Stop Called:')
            #self.yoAccess.writeTtsFile() #save current TTS messages
            self._schedule_refresh_retry_stop = True

            if driver_ready:
                self.my_setDriver('ST', 0)
            else:
                logging.debug('Stop: skipping ST driver update before node is ready')
            self.saveNodeNames()

            if yo_access is not None and hasattr(yo_access, 'shut_down'):
                yo_access.shut_down()
            if yo_local is not None and hasattr(yo_local, 'shut_down'):
                yo_local.shut_down()
            self.poly.stop()
            exit()
        except Exception as e:
            logging.error(f'Stop Exception : {e}')
            self._schedule_refresh_retry_stop = True
            try:
                self.saveNodeNames()
            except Exception as save_err:
                logging.debug(f'Stop saveNodeNames failed: {save_err}')
            if yo_access is not None and hasattr(yo_access, 'shut_down'):
                yo_access.shut_down()
            if yo_local is not None and hasattr(yo_local, 'shut_down'):
                yo_local.shut_down()
            self.poly.stop()


    

    def handleParams (self, userParam ):
        logging.debug('handleParams')
        supportParams = ['YOLINKV2_URL', 'TOKEN_URL','MQTT_URL', 'MQTT_PORT', 'UAID', 'SECRET_KEY', 'NBR_TTS', 'TEMP_UNIT', 'NODE_READY_POLL_SEC' ]
        self.Parameters.load(userParam)

       
        self.poly.Notices.clear()

        try:
            if 'YOLINKV2_URL' in userParam:
                self.yolinkV2URL = userParam['YOLINKV2_URL']
            #else:
            #    self.poly.Notices['yl2url'] = 'Missing YOLINKV2_URL parameter'
            #    self.yolinkV2URL = ''

            if 'TOKEN_URL' in userParam:
                self.tokenURL = userParam['TOKEN_URL']
            #else:
            #    self.poly.Notices['turl'] = 'Missing TOKEN_URL parameter'
            #    self.tokenURL = ''

            if 'MQTT_URL' in userParam:
                self.mqttURL = userParam['MQTT_URL']
            #else:
            #    self.poly.Notices['murl'] = 'Missing MQTT_URL parameter'
            #    self.mqttURL = ''

            if 'MQTT_PORT' in userParam:
                self.mqttPort = userParam['MQTT_PORT']
            #else:
            #    self.poly.Notices['mport'] = 'Missing MQTT_PORT parameter'
            #    self.mqttPort = 0

            if 'TEMP_UNIT' in userParam:
                self.temp_unit = self.convert_temp_unit(userParam['TEMP_UNIT'])
            else:
                self.temp_unit = 0
            if 'WATER_UNIT' in userParam:
                self.water_unit = self.convert_water_unit(userParam['WATER_UNIT'])
            else:
                self.water_unit = 3
            if 'UAID' in userParam:
                self.uaid = str(userParam['UAID'])
                self.uaid = self.uaid.strip()
            else:
                self.poly.Notices['uaid'] = 'Missing UAID parameter'
                self.uaid = ''

            if 'SECRET_KEY' in userParam:
                self.secretKey = str(userParam['SECRET_KEY'])
                self.secretKey = self.secretKey.strip()
            else:
                self.poly.Notices['sk'] = 'Missing SECRET_KEY parameter'
                self.secretKey = ''

            if 'NBR_TTS' in userParam:
                self.nbrTTS = int(userParam['NBR_TTS'])

            if 'NODE_READY_POLL_SEC' in userParam:
                try:
                    self.node_ready_poll_seconds = float(userParam['NODE_READY_POLL_SEC'])
                except (TypeError, ValueError):
                    logging.warning('Invalid NODE_READY_POLL_SEC value: %s', userParam['NODE_READY_POLL_SEC'])
                    self.node_ready_poll_seconds = 0.2
              
                #self.yoAccess.writeTtsFile()    
                
            if 'DEBUG_EN' in userParam:
                self.debug = True

            if 'CALLS_PER_MIN' in userParam:
                self.nbr_API_calls = int(userParam['CALLS_PER_MIN'])
         
            if 'DEV_CALLS_PER_MIN' in userParam:
                self.nbr_dev_API_calls = int(userParam['DEV_CALLS_PER_MIN'])

            # LOCAL ACCESS
            if 'MODE'in userParam:
                mode = userParam['MODE'].lower()
                if mode in ['local']:
                    self.access_mode = ['local']
                elif mode in ['cloud']:
                    self.access_mode = ['cloud']
                elif mode in ['hybrid']:
                    self.access_mode = ['local', 'cloud']
                else:
                    self.poly.Notices['mode'] = 'Missing MODE parameter'

            logging.debug('Access mode set to: {}'.format(self.access_mode))
            if 'LOCAL_CLIENT_ID' in userParam:
                self.local_client_id = userParam['LOCAL_CLIENT_ID']
            else:
                self.local_client_id = None
        
            if 'LOCAL_CLIENT_SECRET' in userParam:
                self.local_client_secret = userParam['LOCAL_CLIENT_SECRET']
            else:
                self.local_client_secret = None

            if 'SUBNET_ID' in userParam:
                self.subnet_id = userParam['SUBNET_ID']
            else:
                self.subnet_id = None
            if 'LOCAL_IP' in  userParam:
                self.local_ip = str(userParam['LOCAL_IP'])
                self.local_ip = self.local_ip.strip()
                self.local_URL = 'http://'+self.local_ip+self.local_port
 
            else:
                self.poly.Notices['ck'] = 'Missing LOCAL_IP parameter'
                self.secretKey = 'x.x.x.x'

            self.remove_legacy_node_name_params()

            #    if param not in supportParams:
            #        del self.Parameters[param]
            #        logging.debug ('erasing key: ' + str(param))

            self.handleParamsDone = True


        except Exception as e:
            logging.debug('Error: %s %s', e, _redact_log_value(userParam))





    id = 'setup'
    commands = {
          #'EPOCHTIME': updateEpochTime,
          }

    drivers = [
         {'driver': 'ST', 'value':0, 'uom':25},
         {'driver': 'GV1', 'value':0, 'uom':25},
         {'driver': 'TIME', 'value':int(time.time()), 'uom':151},
        ]


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        logging.info(f'Version {version}')

        polyglot.start(version)

        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)