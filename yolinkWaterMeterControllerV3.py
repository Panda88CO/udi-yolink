import json
import time

from typing import Any, Union, List, Dict
from yolink_mqtt_classV4 import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)





class YoLinkWaterMeter(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__( yoAccess,  deviceInfo, callback)
  
        yolink.maxSchedules = 6
        #yolink.methodList = ['setAttributes', 'getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        #yolink.eventList = ['StatusChange', 'Report', 'HourlyReport']
        yolink.stateList = ['open', 'closed', 'on', 'off']
        #yolink.ManipulatorName = 'WaterMeterControllerEvent'
        #yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
        yolink.MQTT_type = 'c'
        yolink.uom = None
        #time.sleep(1)


    
    def initDevice (yolink):
        logging.debug('init node')
        yolink.WMcount = None
        yolink.meter_unit = None
        yolink.water_meter_count = 1 
        yolink.refreshDevice()
        #time.sleep(2)
        #logging.debug(f'Water Meter Controller - GV23 maxSchedules: {yolink.maxSchedules}')

        #if not yolink.check_system_online():
        #    logging.error('Water Meter Controller device not online')
        #    yolink.refreshSchedules()
        #else:
        #    
        #yolink.refreshFW
    

    
    def updateStatus(yolink, data, WM_index = None):
        yolink.updateCallbackStatus(data, False)


    def getMeterCount(yolink):
        yolink.water_meter_count = 1
        if yolink.check_system_online():
            if yolink.get_data('state', 'valve') is not None:
                yolink.water_meter_count = 1

            else:
                valve_list = yolink.get_data('state','meters')
                logging.debug(f'valve_list: {valve_list}')  
                if valve_list is not None and isinstance(valve_list, dict):
                    yolink.water_meter_count = len(valve_list)
        logging.debug(f'Water Meter Controller - meter count set to {yolink.water_meter_count}')
        return(yolink.water_meter_count)

    def getMeterUnit(yolink):   
        yolink.meter_unit = None
        if yolink.check_system_online():
            meter_unit = yolink.get_data('attributes', 'meterUnit')
            yolink.meter_unit = meter_unit
            logging.info(f'Water Meter Controller - meter unit set to {yolink.meter_unit}')
        return(yolink.meter_unit)

    def setValveState(yolink, state, WM_index=None):

        try:
            data = {}
            state = state.lower()
            data['params'] = {}
            if isinstance(state, str):
                if state in ['on', 'open']:
                    state = 'open'
                if state in ['off', 'closed', 'close']:
                    state = 'close'              
                if isinstance(WM_index, int) :
                    data['params']['valves']={str(WM_index):state}
                else:
                    data['params']['valve'] = state
            elif isinstance(state, dict) and len(state) > 0:
                data['params']['valves'] = state

            return(yolink.setDevice(data))
        except Exception as e:
            logging.error(f'Exception for {state}, {WM_index} as {e} ')
    #def setAttrib(yolink, attributes):
    #    logging.debug(yolink.type+' - setAttributes')
    #    return(yolink.setAttributes(attributes))


    
    def getBattery(yolink):
        logging.debug(yolink.type+' - getBattery')
        bat_lvl = None
        pwr_mode = None
        logging.debug('online {}'.format(yolink.check_system_online()))
        if yolink.check_system_online():   
            bat_lvl = yolink.get_data('battery')
            if bat_lvl is None:
                bat_lvl = yolink.get_data('battery', 'state')

            pwr_mode = yolink.get_data('powerSupply')
            if pwr_mode is None:
                pwr_mode = yolink.get_data('powerSupply', 'state')
        return(pwr_mode, bat_lvl)
    

    def getWaterTemperature(yolink):
        logging.debug(yolink.type+' - getWaterTemperature')
        water_temp = None

        if yolink.check_system_online():   
            water_temp = yolink.get_data('temperature', 'state')
            if water_temp is None:
                water_temp = yolink.get_data('waterTemperature', 'state')
        return(water_temp)
       

    def getValveState(yolink, WM_index = None):
        logging.debug(yolink.type+' - getValveState')

        valves = None
        if yolink.check_system_online():   
            valves = yolink.get_data('valve', 'state')
            if valves is None:
                valves = yolink.get_data('valves', 'state')

            if isinstance(valves, dict) and isinstance(WM_index, int):
                return valves.get(str(WM_index))

        return(valves)
   

    def getMeterReading(yolink, WM_index = None):
        try:
            meter_correction_factor = 1
            logging.debug(yolink.type+' - getMeterReading')
            temp = {'total':None, 'water_runing':None, 'recent_amount':None, 'recent_duration':None, 'daily_usage':None}

            logging.debug(f'temp1 {temp}')
            if yolink.check_system_online():   
                step_factor = yolink.get_data('meterStepFactor', 'attributes', WM_index)
                if step_factor is None:
                    step_factor = yolink.get_data('meterStepFactor', 'attributes')
                if isinstance(step_factor, (int, float)) and step_factor != 0:
                    meter_correction_factor = float(step_factor)
                else:
                    meter_correction_factor = 1.0

                meter = yolink.get_data('meter', 'state')
                if meter is None:
                    meter = yolink.get_data('meters', 'state')
                waterFlowing = yolink.get_data('waterFlowing', 'state')
                logging.debug(f'meter {meter} waterFlowing {waterFlowing} ')
                
                logging.debug(f'type of meter {type(meter)} type of waterFlowing {type(waterFlowing)} ')
                if meter is not None and not isinstance(meter, dict):
                    temp['total'] = round(meter/meter_correction_factor,1)
                    temp['water_runing'] = waterFlowing
                elif isinstance(meter, dict):
                    adjusted_meter = {}
                    for index in meter:
                        adjusted_meter[index] = round(meter[index]/meter_correction_factor,1)
                    temp['total'] = adjusted_meter
                    temp['water_runing'] = waterFlowing

                recent_amount  = yolink.get_data('amount', 'recentUsage', WM_index)
                if recent_amount is None:
                    recent_amount = yolink.get_data('amount', 'recentUsage')
                recent_duration = yolink.get_data('duration', 'recentUsage', WM_index)
                if recent_duration is None:
                    recent_duration = yolink.get_data('duration', 'recentUsage')
                daily_usage = yolink.get_data('amount', 'dailyUsage', WM_index)
                if daily_usage is None:
                    daily_usage = yolink.get_data('amount', 'dailyUsage')
                daily_duration = yolink.get_data('duration', 'dailyUsage', WM_index)
                if daily_duration is None:
                    daily_duration = yolink.get_data('duration', 'dailyUsage')
                if recent_amount is not None:
                    temp['recent_amount'] = round(recent_amount/meter_correction_factor,1)
                if recent_duration is not None:
                    temp['recent_duration'] = recent_duration
                if daily_usage is not None:
                    temp['daily_usage'] = round(daily_usage/meter_correction_factor,1)  
                if daily_duration is not None:
                    temp['daily_duration'] = daily_duration
                
            logging.debug(f' temp {temp}')   
            return(temp)

        except KeyError as e:
            logging.error(f'EXCEPTION - getMeterReading Key error {e}') 
            return(None)
        except ValueError as e:
            logging.error(f'EXCEPTION - getMeterReading Value error {e}') 
            return(None)
    

   
    
    def getAlarms(yolink, WM_index = None):
        try:
            logging.debug(yolink.type+' - getAlarms')
            alarms = {}
            if yolink.check_system_online():   
                alarm_data = yolink.get_data('alarm')
                if isinstance(alarm_data, dict):
                    alarms = dict(alarm_data)
                    if isinstance(WM_index, int):
                        wm_key = str(WM_index)
                        for item in list(alarms.keys()):
                            if isinstance(alarms[item], dict) and wm_key in alarms[item]:
                                alarms[item] = alarms[item][wm_key]
            return(alarms)

        except KeyError as e:
            logging.error(f'Exception : {e}')
            return(None)
        

    def getAttributes(yolink,  WM_index = None):
        try:
            logging.debug(yolink.type+' - getAttributes')
            attributes = {}
            if yolink.check_system_online():   
                attr_data = yolink.get_data('attributes')
                if isinstance(attr_data, dict):
                    attributes = dict(attr_data)
                    if 'meterUnit' in attributes and yolink.uom is None:
                        yolink.uom = attributes['meterUnit']
                    if isinstance(WM_index, int):
                        wm_key = str(WM_index)
                        for item in list(attributes.keys()):
                            if isinstance(attributes[item], dict) and wm_key in attributes[item]:
                                attributes[item] = attributes[item][wm_key]
                                    
            return(attributes)

        except KeyError as e:
            logging.error(f'Exception : {e}')
            return(None)
        
