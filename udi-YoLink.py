#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""

import sys
import time
#from apscheduler.schedulers.background import BackgroundScheduler


from yoLink_init_V4 import YoLinkInitPAC
from threading import Thread

try:
    import udi_interface
    loggingn = udi_interface.LOGGER
    loggingn.setLevel(30)
    logging = udi_interface.node.NLOGGER
    
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from udiCommonLib import version


def _summarize_devices_for_log(device_list):
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
        })
    return {'count': len(devices), 'devices': devices}


class YoLinkSetup (udi_interface.Node):
    from udiYolinkLib import my_setDriver, node_queue, wait_for_node_done, updateEpochTime, convert_temp_unit, convert_water_unit, apply_profile_driver_names
    from udiCommonLib import systemPoll, addNodes, heartbeat, checkNodes, handleLevelChange, saveNodeNames

    def  __init__(self, polyglot, primary, address, name):
        super().__init__( polyglot, primary, address, name)  
        logging.info(f'Version {version}')
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
        self._schedule_refresh_retry_stop = False
        self._schedule_refresh_retry_interval_sec = 30

        
        #logging.setLevel(10)

        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
        self.poly.subscribe(self.poly.DISCOVER, self.discover)

        self.Parameters = Custom(self.poly, 'customparams')
        self.Notices = Custom(self.poly, 'notices')

        self.n_queue = []
        self.yoLocal = None
        self.yoAccess = None 
        logging.info(f'Version {version}')

        logging.debug('YoLinkSetup init')
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))   
        self.poly.ready()
       
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(self.address)
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV1', 0)
        self.assigned_addresses = []
        self.assigned_addresses.append(self.address)   
        logging.debug('YoLinkSetup init DONE')        
        self.nodeDefineDone = True

 
    def configDoneHandler(self):
        self.poly.Notices.clear()
        logging.info('configDoneHandler called')
        self.nodes_in_db = self.poly.getNodesFromDb()
        logging.debug('Nodes in Nodeserver - before cleanup: {} - {}'.format(len(self.nodes_in_db),self.nodes_in_db))
        self.configDone = True

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
        logging.info ('Access using PAC/UAC')
        #logging.setLevel(30)
        while not self.nodeDefineDone or not self.configDone or not self.handleParamsDone:
            logging.debug ('waiting for inital node to get created')
            time.sleep(1)
    
        
        #self.supportedYoTypes = ['WaterMeterController',  'InfraredRemoter']
        #self.supportedYoTypes = [ 'WaterDepthSensor', 'VibrationSensor']    
        self.updateEpochTime()
        if self.uaid == None or self.uaid == '' or self.secretKey==None or self.secretKey=='':
            logging.error('UAID and secretKey must be provided to start node server')
            exit() 


        self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
        if self.yoAccess:
            self.my_setDriver('ST', 1)
        if 'TEMP_UNIT' in self.Parameters:
            self.temp_unit = self.convert_temp_unit(self.Parameters['TEMP_UNIT'])
        else:
            self.temp_unit = 0  
            self.Parameters['TEMP_UNIT'] = 'C'
        logging.debug('TEMP_UNIT: {}'.format(self.temp_unit ))
        self.yoAccess.set_temp_unit(self.temp_unit )
        if 'WATER_UNIT' in self.Parameters:
            self.water_unit = self.convert_water_unit(self.Parameters['WATER_UNIT'])
            logging.debug('WATER_UNIT: {}'.format(self.water_unit ))

        else:
            self.water_unit = 0  
            self.Parameters['WATER_UNIT'] = 'L'
            logging.debug('WATER_UNIT: {}'.format(self.water_unit ))
        if self.yoAccess:
            self.yoAccess.set_water_unit(self.water_unit )

        if 'DEBUG_EN' in self.Parameters:
            self.debug = self.Parameters['DEBUG_EN']
            self.yoAccess.set_debug(self.debug)
        else:
            self.debug = False
            self.yoAccess.set_debug(self.debug)
        
        if 'CALLS_PER_MIN' in self.Parameters:
            self.nbr_API_calls = self.Parameters['CALLS_PER_MIN']
            self.nbr_dev_API_calls = self.Parameters['DEV_CALLS_PER_MIN']
            self.yoAccess.set_api_limits(self.nbr_API_calls, self.nbr_dev_API_calls)
        self.deviceList = self.yoAccess.getDeviceList()


        logging.debug('Devices detected: %s', _summarize_devices_for_log(self.deviceList))
        if self.yoAccess:
            self.my_setDriver('ST', 1)
            self.my_setDriver('GV1', 1)
            self.deviceList = self.addNodes(self.deviceList)
            self.remove_legacy_node_name_params()
            # Defer non-critical schedule refreshes to avoid startup API bursts
            # Run in background so node server can continue initializing
            try:
                self._schedule_refresh_retry_stop = False
                t = Thread(target=self.deferred_refresh_schedules, daemon=True)
                t.start()
            except Exception:
                logging.debug('Failed to start deferred_refresh_schedules thread')
        else:
            self.my_setDriver('ST', 0)
        #self.poly.updateProfile()
        
        #self.scheduler = BackgroundScheduler()
        #self.scheduler.add_job(self.display_update, 'interval', seconds=self.display_update_sec)
        #self.scheduler.start()
        #self.updateEpochTime()


    
    def stop(self):
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

            if self.yoAccess and hasattr(self.yoAccess, 'shut_down'):
                self.yoAccess.shut_down()
            self.poly.stop()
            exit()
        except Exception as e:
            logging.error(f'Stop Exception : {e}')
            self._schedule_refresh_retry_stop = True
            try:
                self.saveNodeNames()
            except Exception as save_err:
                logging.debug(f'Stop saveNodeNames failed: {save_err}')
            if self.yoAccess and hasattr(self.yoAccess, 'shut_down'):
                self.yoAccess.shut_down()
            self.poly.stop()

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

                # space calls using yoAccess time tracking
                try:
                    delay = self.yoAccess.time_tracking(dev_id) if self.yoAccess is not None else 0
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

                try:
                    delay = self.yoAccess.time_tracking(dev_id) if self.yoAccess is not None else 0
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

    def handleParams (self, userParam ):
        logging.debug('handleParams')
        supportParams = ['YOLINKV2_URL', 'TOKEN_URL','MQTT_URL', 'MQTT_PORT', 'UAID', 'SECRET_KEY', 'NBR_TTS', 'TEMP_UNIT', 'NODE_READY_POLL_SEC' ]
        self.Parameters.load(userParam)

       
        self.poly.Notices.clear()

        try:
            #logging.setLevel(level=logging.INFO)
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

            self.remove_legacy_node_name_params()

            #    if param not in supportParams:
            #        del self.Parameters[param]
            #        logging.debug ('erasing key: ' + str(param))

            self.handleParamsDone = True


        except Exception as e:
            logging.debug('Error: {} {}'.format(e, userParam))


    def updateEpochTime(self, command=None ):
        logging.info('updateEpochTime ')
        #unit = int(command.get('value'))
        self.my_setDriver('TIME', int(time.time()))

    def discover(self, *args, **kwargs):
        logging.info("Discover requested - refreshing profile")
        self._update_dynamic_profile()

    def _update_dynamic_profile(self):
        from udiDynamicProfile import update_dynamic_profile
        update_dynamic_profile(self)

    id = 'setup'
    commands = {
                #'EPOCHTIME': updateEpochTime,
                }

    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Node Server'},
            {'driver': 'GV1', 'value': 0, 'uom': 25, 'name': 'Status'},
            {'driver': 'TIME', 'value': int(time.time()), 'uom': 151, 'name': 'LastPoll Time'},
           ]


if __name__ == "__main__":
    try:
        logging.info
        polyglot = udi_interface.Interface([])

        logging.info('Starting YoLink NodeServer - version {}'.format(version) )

        polyglot.start(version)
        logging.info('YoLink NodeServer Started - calling setup')
        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')
        logging.info('YoLinkSetup node created - entering runForever')
        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)