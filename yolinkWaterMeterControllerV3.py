import json
import time

from typing import Any, Union, List, Dict
from yolink_mqtt_classV3 import YoLinkMQTTDevice
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
        #import getMeterCount, getData
        yolink.maxSchedules = 6
        yolink.methodList = ['setAttributes', 'getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        yolink.eventList = ['StatusChange', 'Report', 'HourlyReport']
        yolink.stateList = ['open', 'closed', 'on', 'off']
        yolink.ManipulatorName = 'WaterMeterControllerEvent'
        yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
        yolink.MQTT_type = 'c'
        yolink.uom = None
        #time.sleep(1)


    
    def initNode(yolink):
        logging.debug('init node')
        yolink.WMcount = None
        yolink.meter_unit = None
        yolink.water_meter_count = 1 
        yolink.refreshDevice()
        time.sleep(2)

        if not yolink.online:
            logging.error('Water Meter Controller device not online')
        #    yolink.refreshSchedules()
        #else:
        #    
        #yolink.refreshFW
    

    
    def updateStatus(yolink, data, WM_index = None):
        yolink.updateCallbackStatus(data, False)


    def getMeterCount(yolink):
        if yolink.online:
            if 'state' in yolink.dataAPI[yolink.dData] and 'state' in yolink.dataAPI[yolink.dData]['state']:
            
                if 'meters' in yolink.dataAPI[yolink.dData]['state']['state'] and isinstance(yolink.dataAPI[yolink.dData]['state']['state']['meters'], dict):
                    yolink.water_meter_count = len(yolink.dataAPI[yolink.dData]['state']['state']['meters'])
                elif 'valves' in yolink.dataAPI[yolink.dData]['state']['state'] and isinstance(yolink.dataAPI[yolink.dData]['state']['state']['valves'], dict):
                    yolink.water_meter_count = len(yolink.dataAPI[yolink.dData]['state']['state']['valves'])
                else:
                    yolink.water_meter_count = 1 
                logging.info(f'Water Meter Controller - {yolink.water_meter_count} meters found')

    def getMeterUnit(yolink):   
        yolink.meter_unit = None
        if yolink.online:
            meter_unit = yolink.getData('attributes', 'meterUnit')
            yolink.meter_unit = meter_unit
            logging.info(f'Water Meter Controller - meter unit set to {yolink.meter_unit}')


    def setValveState(yolink, state, WM_index=None):
        #yolink.online = yolink.getOnlineStatus()
        try:
            if yolink.online:   
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
        logging.debug('online {} , data {}'.format(yolink.online, yolink.dataAPI[yolink.dData] ))
        if yolink.online:   
            if 'battery' in yolink.dataAPI[yolink.dData]:
                bat_lvl = yolink.dataAPI[yolink.dData]['battery']
            elif yolink.dState in yolink.dataAPI[yolink.dData] and 'battery' in yolink.dataAPI[yolink.dData][yolink.dState]: 
                bat_lvl = yolink.dataAPI[yolink.dData][yolink.dState]['battery']    
            if 'powerSupply' in yolink.dataAPI[yolink.dData]:                
                pwr_mode = yolink.dataAPI[yolink.dData]['powerSupply']
            elif yolink.dState in yolink.dataAPI[yolink.dData] and 'powerSupply' in yolink.dataAPI[yolink.dData][yolink.dState]:
                pwr_mode = yolink.dataAPI[yolink.dData][yolink.dState]['powerSupply']                   
        return(pwr_mode, bat_lvl)
    

    def getWaterTemperature(yolink):
        logging.debug(yolink.type+' - getWaterTemperature')
        water_temp = None
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            if yolink.dState in yolink.dataAPI[yolink.dData]:
                if 'temperature' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    water_temp = yolink.dataAPI[yolink.dData][yolink.dState]['temperature']
        return(water_temp)
       

    def getValveState(yolink, WM_index = None):
        logging.debug(yolink.type+' - getValveState')
        #yolink.online = yolink.getOnlineStatus()
        valves = None
        if yolink.online:   
            if yolink.dState in yolink.dataAPI[yolink.dData]:
                if 'valve' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    valves = yolink.dataAPI[yolink.dData][yolink.dState]['valve']
                if 'state' in yolink.dataAPI[yolink.dData][yolink.dState] and 'valves' in yolink.dataAPI[yolink.dData][yolink.dState]['state'] :                    
                    valves = yolink.dataAPI[yolink.dData][yolink.dState]['state']['valves']
                    if isinstance(yolink.dataAPI[yolink.dData][yolink.dState]['state']['valves'], dict):
                        valves = yolink.dataAPI[yolink.dData][yolink.dState]['state']['valves']
                        if isinstance( WM_index, int):
                            if str(WM_index) in valves:
                                valves[str(WM_index)] == yolink.dataAPI[yolink.dData][yolink.dState]['state']['valves'][str(WM_index)]

        return(valves)
    
    def step_in (self, dict_data, category, key):
        ret_val = None
        for temp_cat in dict_data:
            if isinstance(temp_cat, dict):
                logging.debug(f'dict identified {temp_cat} in data')
                if category in dict_data[temp_cat]:
                    logging.debug(f'category {category} found in data under {temp_cat}')    
                    if key in dict_data[temp_cat][category]:
                        ret_val = dict_data[temp_cat][category][key]
                    elif isinstance(dict_data[temp_cat][category], dict):
                        logging.debug(f'going deeper into dict for key {key}')  
                        for temp_key in dict_data[temp_cat][category]:
                            if key in temp_key:
                                ret_val = dict_data[temp_cat][category][temp_key][key]
                                break
        return ret_val

    def check_for_cat_key(cat, key, WM_index, data_dict):
        ret_val = None
        if cat in data_dict:
            logging.debug(f'category {cat} found in data {data_dict[cat]}')
            if key in data_dict[cat]:
                if not isinstance(data_dict[cat][key], dict):
                    logging.debug(f'key {key} found in [ {cat} ]  {data_dict[cat][key]}')
                    ret_val = data_dict[cat][key]
            elif isinstance(data_dict[cat], dict):
                logging.debug(f'going deeper into dict for key {key}')  
                for temp_key in data_dict[cat]:
                    if key in temp_key:
                        ret_val = data_dict[cat][temp_key][key]
                        break
        return ret_val



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

        #def safe_get(d: Any, k: str) -> Any:
        #    """Safely get a key from a dict, return None if not found."""
        #    return d.get(k) if isinstance(d, dict) else None

        def traverse(obj: Any):
            """Recursively traverse dicts/lists to find matching keys."""
            if isinstance(obj, dict):
                if key1 in obj and isinstance(obj[key1], dict):
                    if key2 in obj[key1]:
                        results.append(obj[key1][key2])
                for v in obj.values():
                    traverse(v)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)
        traverse(yolink.dataAPI[yolink.dData]['state'])
        return results[0] if results else None

    def getData(yolink, category, key, WM_index = None):    
        try:
            logging.debug(yolink.type+f' - getData category {category} key {key} {WM_index} {yolink.dataAPI[yolink.dData]}')
            ret_val = None  
            if yolink.online and yolink.dData in yolink.dataAPI : 
                if yolink.dataAPI[yolink.dData] is {}:
                    logging.info(f'No data exists (no data returned)')
                    return("no data")
                if category is None:
                    if key in yolink.dataAPI[yolink.dData]:
                        logging.debug(f'ret_val0 {ret_val} {key}  {category}')
                        return(yolink.dataAPI[yolink.dData][key])
                    
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



    def getData1(yolink, category, key, WM_index = None):    
        try:
            logging.debug(yolink.type+f' - getData category {category} key {key} {WM_index} {yolink.dataAPI[yolink.dData]}')
            ret_val = None  
            if yolink.online and yolink.dData in yolink.dataAPI : 
                if yolink.dataAPI[yolink.dData] is {}:
                    logging.info(f'No data exists (no data returned)')
                    return("no data")
                if category is None:
                    if key in yolink.dataAPI[yolink.dData]:
                        logging.debug(f'ret_val0 {ret_val} {key}  {category}')
                        return(yolink.dataAPI[yolink.dData][key])
                # parse category/key
                       
                if category in yolink.dataAPI[yolink.dData] and not isinstance(yolink.dataAPI[yolink.dData][category], dict):
                    logging.debug(f'{category} found as single value')
                    if key in yolink.dataAPI[yolink.dData][category]:
                        ret_val = yolink.dataAPI[yolink.dData][category][key]
                        logging.debug(f'ret_val1 {ret_val}  {key}  {category}')

                        return(ret_val)

                if isinstance(yolink.dataAPI[yolink.dData], dict): # dict detected
                    logging.debug(f'[dict] selected')
                    if category in yolink.dataAPI[yolink.dData]:
                        logging.debug(f'category {category} found in data {yolink.dataAPI[yolink.dData][category]}')

                        if not isinstance(yolink.dataAPI[yolink.dData][category], dict):
                            if key in yolink.dataAPI[yolink.dData][category]:
                                ret_val = yolink.dataAPI[yolink.dData][category][key]
                        else: 
                            logging.debug(f'category {category} is a dict - {yolink.dataAPI[yolink.dData][category]}')
                            if key in yolink.dataAPI[yolink.dData][category]:
                                if not isinstance(yolink.dataAPI[yolink.dData][category][key], dict):
                                    logging.debug(f'key {key} found in [ {category} ]  {yolink.dataAPI[yolink.dData][category][key]}')
                                    ret_val = yolink.dataAPI[yolink.dData][category][key]
                                else:
                                    logging.debug(f"key {key} is a dict {yolink.dataAPI[yolink.dData][category][key]}")
                                    items = yolink.dataAPI[yolink.dData][category][key]
                                    logging.debug(f'items for {key} found {items}')
                                    if isinstance( WM_index, int):
                                        if str(WM_index) in items:
                                            ret_val = items[str(WM_index)]
                                    else:
                                        ret_val = items
                        logging.debug(f'ret_val2 {ret_val}  {key}  {category}')               
                        return(ret_val)
                    else:
                        for temp_cat, temp_val in yolink.dataAPI[yolink.dData].items():
                            logging.debug(f'temp_cat {temp_cat} ')
                            if isinstance(temp_val, dict):
                                if category in yolink.dataAPI[yolink.dData][temp_cat]:
                                    logging.debug(f'category {category} found in data under {temp_cat}')
                                    if key in yolink.dataAPI[yolink.dData][temp_cat][category] and not isinstance(yolink.dataAPI[yolink.dData][temp_cat][category][key], dict):
                                        ret_val = yolink.dataAPI[yolink.dData][temp_cat][category][key]
                                    elif key in yolink.dataAPI[yolink.dData][temp_cat][category] and isinstance(yolink.dataAPI[yolink.dData][temp_cat][category][key], dict):
                                        items = yolink.dataAPI[yolink.dData][temp_cat][category][key]                      
                                        logging.debug(f'items for {key} found {items}')
                                        if isinstance( WM_index, int):
                                            if str(WM_index) in items:
                                                ret_val = items[str(WM_index)]
                                        else:
                                            ret_val = items
                                    else: # 
                                        for temp_cat2, temp_val2 in yolink.dataAPI[yolink.dData][temp_cat][category].items():

                                            if key in temp_val2:
                                                logging.debug(f'key {key} found in [ {temp_cat} ][ {category} ][ {temp_cat2} ]  [ {temp_val2}]')  
                                                ret_val = yolink.dataAPI[yolink.dData][temp_cat][category][temp_cat2][key]
                                                break
                                else: # going deeper
                                    for temp_cat2 in temp_cat:
                                        logging.debug(f'temp_cat {temp_cat} ')
                                        if isinstance(temp_cat2, dict):
                                            if category in yolink.dataAPI[yolink.dData][temp_cat][temp_cat2]:
                                                logging.debug(f'category {category} found in data under {temp_cat2}')
                                                if key in yolink.dataAPI[yolink.dData][temp_cat][temp_cat2] and not isinstance(yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][key], dict):
                                                    ret_val = yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][key]
                                                elif key in yolink.dataAPI[yolink.dData][temp_cat][temp_cat2] and isinstance(yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][key], dict):
                                                    items = yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][key]                      
                                                    logging.debug(f'items for {key} found {items}')
                                                    if isinstance( WM_index, int):
                                                        if str(WM_index) in items:
                                                            ret_val = items[str(WM_index)]
                                                    else:
                                                        ret_val = items
                                                else: # go further in
                                                    for temp_key in yolink.dataAPI[yolink.dData][temp_cat][temp_cat2]:
                                                        if key in temp_key:
                                                            logging.debug(f'key {key} found in [ {temp_cat} ][ {category} ][ {temp_key} ] ')  
                                                            ret_val = yolink.dataAPI[yolink.dData][temp_cat][category][temp_key][key]
                                                            break
                                            else: # going deeper
                                                for temp_cat3 in temp_cat2:
                                                    logging.debug(f'temp_cat {temp_cat} ')
                                                    if isinstance(temp_cat3, dict):
                                                        if category in yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][temp_cat3]:
                                                            logging.debug(f'category {category} found in data under {temp_cat3}')
                                                            if key in yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][temp_cat3] and not isinstance(yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][temp_cat3][key], dict):
                                                                ret_val = yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][temp_cat3][key]
                                                            elif key in yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][temp_cat3] and isinstance(yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][temp_cat3][key], dict):
                                                                items = yolink.dataAPI[yolink.dData][temp_cat][temp_cat2][temp_cat3][key]                      
                                                                logging.debug(f'items for {key} found {items}')
                                                                if isinstance( WM_index, int):
                                                                    if str(WM_index) in items:
                                                                        ret_val = items[str(WM_index)]
                                                                else:
                                                                    ret_val = items
                                                            else: # go further in
                                                                for temp_key in yolink.dataAPI[yolink.dData][temp_cat][temp_cat2]:
                                                                    if key in temp_key:
                                                                        logging.debug(f'key {key} found in [ {temp_cat} ][ {category} ][ {temp_key} ] ')  
                                                                        ret_val = yolink.dataAPI[yolink.dData][temp_cat][category][temp_key][key]
                                                                        break


            logging.debug(f'ret_val {ret_val} {key}  {category}')
            return(ret_val)
        
        except KeyError as e:
            logging.error(f'EXCEPTION - getData {e}') 

    def getDataOLD(yolink, category, key, WM_index = None):    
        try:
            logging.debug(yolink.type+f' - getData category {category} key {key} {WM_index} {yolink.dataAPI[yolink.dData]}')
            ret_val = None  
            if yolink.online: 
                if yolink.dataAPI[yolink.dData] is {}:
                    logging.info(f'No data exists (no data returned)')
                    return("no data")
                if category is None:
                    if key in yolink.dataAPI[yolink.dData]:
                        ret_val = yolink.dataAPI[yolink.dData][key]
                    
                if category in yolink.dataAPI[yolink.dData] and not isinstance(yolink.dataAPI[yolink.dData][category], dict):
                    logging.debug(f'{category} found as single value')
                    if key in yolink.dataAPI[yolink.dData][category]:
                        ret_val = yolink.dataAPI[yolink.dData][category][key]
                if yolink.dState in yolink.dataAPI[yolink.dData] : # dict detected
                    logging.debug(f'[dict] selected')
                    
                    if category in yolink.dataAPI[yolink.dData][yolink.dState]:
                        logging.debug(f'category {category} found in state')
                        if key in yolink.dataAPI[yolink.dData][yolink.dState][category] and not isinstance(yolink.dataAPI[yolink.dData][yolink.dState][category][key], dict):
                            ret_val = yolink.dataAPI[yolink.dData][yolink.dState][category][key]
                if category in yolink.dataAPI[yolink.dData][yolink.dState]:
                    logging.debug(f" {category} found in [state] selected - {yolink.dataAPI[yolink.dData][yolink.dState][category]}")

                    if key in yolink.dataAPI[yolink.dData][yolink.dState][category]:
                        logging.debug(f'key {key} found in [state][{category}]')
                        if isinstance(yolink.dataAPI[yolink.dData][yolink.dState][category][key], dict):
                            logging.debug(f"key {key} is a dict {yolink.dataAPI[yolink.dData][yolink.dState][category][key]}")
                            items = yolink.dataAPI[yolink.dData][yolink.dState][category][key]                      
                            logging.debug(f'items for {key} found {items}')
                            if isinstance( WM_index, int):
                                if str(WM_index) in items:
                                    ret_val = items[str(WM_index)]
                            else:
                                ret_val = items
                        else:
                            ret_val = yolink.dataAPI[yolink.dData][yolink.dState][category][key]                              
                    
            logging.debug(f'ret_val {ret_val} {key}  {category}')
            return(ret_val)
        
        except KeyError as e:
            logging.error(f'EXCEPTION - getData {e}') 
            return(None)
 
    def getMeterReading(yolink, WM_index = None):
        try:
            meter_correction_factor = 1
            logging.debug(yolink.type+f' - getMeterReading {json.dumps(yolink.dataAPI[yolink.dData], indent=4)}')
            temp = {'total':None, 'water_runing':None, 'recent_amount':None, 'recent_duration':None, 'daily_usage':None}
            #yolink.online = yolink.getOnlineStatus()
            logging.debug(f'temp1 {temp}')
            if yolink.online:   
                #logging.debug(f'yolink.dataAPI[yolink.dData][yolink.dState]: {yolink.dataAPI[yolink.dData][yolink.dState]} ')
                #if 'attributes' in yolink.dataAPI[yolink.dData] and 'meterStepFactor' in yolink.dataAPI[yolink.dData]['attributes']:
                #    meter_correction_factor = yolink.dataAPI[yolink.dData]['attributes']['meterStepFactor']
                meter_correction_factor = float(yolink.getData('attributes', 'meterStepFactor', WM_index))
                if meter_correction_factor is None:     
                    meter_correction_factor = 1.0   
                #logging.debug(f'logic {yolink.dState in yolink.dataAPI[yolink.dData]}')
                if 'meter' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    meter = yolink.getData(yolink.dState, 'meter')
                    waterFlowing = yolink.getData(yolink.dState, 'waterFlowing')
                elif 'state' in yolink.dataAPI[yolink.dData][yolink.dState] and 'meters' in yolink.dataAPI[yolink.dData][yolink.dState]['state']:                    
                    meter = yolink.getData(yolink.dState, 'meters')
                    waterFlowing = yolink.getData(yolink.dState, 'waterFlowing')
                logging.debug(f'meter {meter} waterFlowing {waterFlowing} ')
                
                #if yolink.dState in yolink.dataAPI[yolink.dData]:
                logging.debug(f'type of meter {type(meter)} type of waterFlowing {type(waterFlowing)} ')
                if not isinstance(meter, dict):
                    temp['total'] = round(meter/meter_correction_factor,1)
                    temp['water_runing'] = waterFlowing
                else:
                    for index in meter:
                        meter[WM_index] = round(meter[index]/meter_correction_factor,1)
                    temp['total'] = meter
                    temp['water_runing'] = waterFlowing

                recent_amount  = yolink.getData('recentUsage', 'amount', WM_index)
                recent_duration = yolink.getData('recentUsage', 'duration', WM_index)
                daily_usage = yolink.getData('dailyUsage', 'amount', WM_index)
                daily_duration = yolink.getData('dailyUsage', 'duration', WM_index) 
                if recent_amount is not None:
                    temp['recent_amount'] = round(recent_amount/meter_correction_factor,1)
                if recent_duration is not None:
                    temp['recent_duration'] = recent_duration
                if daily_usage is not None:
                    temp['daily_usage'] = round(daily_usage/meter_correction_factor,1)  
                else:
                    daily_usage = yolink.getData(None, 'dailyUsage', WM_index)
                if daily_duration is not None:
                    temp['daily_duration'] = daily_duration

                
                if 'recentUsage' in yolink.dataAPI[yolink.dData]:
                    if 'amount' in yolink.dataAPI[yolink.dData]['recentUsage']:
                        temp['recent_amount'] = round(yolink.dataAPI[yolink.dData]['recentUsage']['amount']/meter_correction_factor,1)
                    if 'duration' in yolink.dataAPI[yolink.dData]['recentUsage']:
                        temp['recent_duration'] = yolink.dataAPI[yolink.dData]['recentUsage']['duration']
                if 'dailyUsage' in yolink.dataAPI[yolink.dData]:
                    if isinstance(yolink.dataAPI[yolink.dData]['dailyUsage'], dict):
                        if 'amount' in yolink.dataAPI[yolink.dData]['dailyUsage']:
                            temp['daily_usage'] = round(yolink.dataAPI[yolink.dData]['dailyUsage']['amount']/meter_correction_factor,1)
                        if 'duration' in yolink.dataAPI[yolink.dData]['dailyUsage']:
                            temp['daily_duration'] = yolink.dataAPI[yolink.dData]['dailyUsage']['duration']           
                        else:
                            temp['daily_duration'] = None     
                    elif isinstance(yolink.dataAPI[yolink.dData]['dailyUsage'], int) or isinstance(yolink.dataAPI[yolink.dData]['dailyUsage'], float):
                        temp['daily_usage'] = round(yolink.dataAPI[yolink.dData]['dailyUsage']/meter_correction_factor,1)
                
            logging.debug(f' temp {temp}')   
            return(temp)

        except KeyError as e:
            logging.error(f'EXCEPTION - getMeterReading Key error {e}') 
            return(None)
        except ValueError as e:
            logging.error(f'EXCEPTION - getMeterReading Value error {e}') 
            return(None)
    

    '''
    def getMeterReading(yolink):
        try:
            meter_correction_factor = 1
            logging.debug(yolink.type+f' - getMeterReading {json.dumps(yolink.dataAPI[yolink.dData], indent=4)}')
            temp = {'total':None, 'water_runing':None, 'recent_amount':None, 'recent_duration':None, 'daily_usage':None}
            #yolink.online = yolink.getOnlineStatus()
            logging.debug(f'temp1 Non-multi {temp}')
            if yolink.online:   
                logging.debug(f'yolink.dataAPI[yolink.dData][yolink.dState]: {yolink.dataAPI[yolink.dData][yolink.dState]} ')
                if 'attributes' in yolink.dataAPI[yolink.dData] and 'meterStepFactor' in yolink.dataAPI[yolink.dData]['attributes']:
                    meter_correction_factor = yolink.dataAPI[yolink.dData]['attributes']['meterStepFactor']
                elif yolink.dState in yolink.dataAPI[yolink.dData] and 'attributes' in yolink.dataAPI[yolink.dData][yolink.dState] and 'meterStepFactor' in yolink.dataAPI[yolink.dData][yolink.dState]['attributes']:
                    meter_correction_factor = yolink.dataAPI[yolink.dData]['state']['attributes']['meterStepFactor']                    
                else:
                    meter_correction_factor = 1.0   
                #logging.debug(f'logic {yolink.dState in yolink.dataAPI[yolink.dData]}')
                if yolink.dState in yolink.dataAPI[yolink.dData]:
                    #logging.debug('next {}'.format(yolink.dataAPI[yolink.dData][yolink.dState]['meter']))
                    if 'meter' in yolink.dataAPI[yolink.dData][yolink.dState]:
                        temp['total'] = round(yolink.dataAPI[yolink.dData][yolink.dState]['meter']/meter_correction_factor,1)
                    if 'waterFlowing' in yolink.dataAPI[yolink.dData][yolink.dState]:
                        temp['water_runing'] = yolink.dataAPI[yolink.dData][yolink.dState]['waterFlowing']
                    #logging.debug('next 2 {}'.format(temp ))

                if 'recentUsage' in yolink.dataAPI[yolink.dData]:
                    if 'amount' in yolink.dataAPI[yolink.dData]['recentUsage']:
                        temp['recent_amount'] = round(yolink.dataAPI[yolink.dData]['recentUsage']['amount']/meter_correction_factor,1)
                    if 'duration' in yolink.dataAPI[yolink.dData]['recentUsage']:
                        temp['recent_duration'] = yolink.dataAPI[yolink.dData]['recentUsage']['duration']
                if 'dailyUsage' in yolink.dataAPI[yolink.dData]:
                    if isinstance(yolink.dataAPI[yolink.dData]['dailyUsage'], dict):
                        if 'amount' in yolink.dataAPI[yolink.dData]['dailyUsage']:
                            temp['daily_usage'] = round(yolink.dataAPI[yolink.dData]['dailyUsage']['amount']/meter_correction_factor,1)
                        if 'duration' in yolink.dataAPI[yolink.dData]['dailyUsage']:
                            temp['daily_duration'] = yolink.dataAPI[yolink.dData]['dailyUsage']['duration']           
                        else:
                            temp['daily_duration'] = None     
                    elif isinstance(yolink.dataAPI[yolink.dData]['dailyUsage'], int) or isinstance(yolink.dataAPI[yolink.dData]['dailyUsage'], float):
                        temp['daily_usage'] = round(yolink.dataAPI[yolink.dData]['dailyUsage']/meter_correction_factor,1)
            #logging.debug(f' temp {temp}')             
            return(temp)

        except KeyError as e:
            logging.error(f'EXCEPTION - getMeterReading {e}') 
            return(None)
    '''
    
    def getAlarms(yolink, WM_index = None):
        try:
            logging.debug(yolink.type+' - getAlarms')
            alarms = {}
            if yolink.online:   

                if 'alarm' in yolink.dataAPI[yolink.dData]:
                    alarms = yolink.dataAPI[yolink.dData]['alarm']
                    if isinstance( WM_index, int):
                        for item in yolink.dataAPI[yolink.dData]['alarm']:
                            if isinstance(yolink.dataAPI[yolink.dData]['alarm'][item], dict):
                                if str(WM_index) in item:
                                    alarms[item] = yolink.dataAPI[yolink.dData]['alarm'][item][str(WM_index)]
            return(alarms)

        except KeyError as e:
            logging.error(f'Exception : {e}')
            return(None)
        

    def getAttributes(yolink,  WM_index = None):
        try:
            logging.debug(yolink.type+' - getAttributes')
            attributes = {}
            if yolink.online: 
                data = yolink.getData('attributes', 'meterUnit')  
                if 'attributes' in yolink.dataAPI[yolink.dData]:
                    attributes = yolink.dataAPI[yolink.dData]['attributes' ]
                    if 'meterUnit' in attributes and yolink.uom is None:
                        yolink.uom = attributes['meterUnit']
                    if isinstance( WM_index, int):
                        for item in yolink.dataAPI[yolink.dData]['attributes']:
                            if isinstance(yolink.dataAPI[yolink.dData]['attributes'][item], dict):
                                if str(WM_index) in item:
                                    attributes[item] = yolink.dataAPI[yolink.dData]['attributes'][item][str(WM_index)]                        
                                    
            return(attributes)

        except KeyError as e:
            logging.error(f'Exception : {e}')
            return(None)
        


        

    #def getData(yolink):
        #yolink.online = yolink.getOnlineStatus()
    #    if yolink.online:   
    #        return(yolink.getData())
"""
class YoLinkWaterMultiMeter(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__( yoAccess,  deviceInfo, callback)
        yolink.maxSchedules = 6
        yolink.methodList = ['setAttributes', 'getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        yolink.eventList = ['StatusChange', 'Report', 'HourlyReport']
        yolink.stateList = ['open', 'closed', 'on', 'off']
        yolink.ManipulatorName = 'WaterMeterControllerEvent'
        yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
        yolink.MQTT_type = 'c'
        yolink.uom = None
        #time.sleep(1)
    '''
    def initNode(yolink):
        yolink.refreshState()
        time.sleep(2)
        if not yolink.online:
            logging.error('YoLinkWaterMultiMeter device not online')
        #    yolink.refreshSchedules()
        #else:
        #    
        #yolink.refreshFW
    ''' 
    def initNode(yolink):
        
        yolink.WMcount = None
        yolink.refreshDevice()
        yolink.getMeterCount()
        time.sleep(2)   
        if not yolink.online:
            logging.error('Water Meter Controller device not online')

    
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

   

    def getMeterCount(yolink):
        if yolink.online:
            if 'state' in yolink.dataAPI[yolink.dData] and 'state' in yolink.dataAPI[yolink.dData]['state']:
            
                if 'meters' in yolink.dataAPI[yolink.dData]['state']['state'] and isinstance(yolink.dataAPI[yolink.dData]['state']['state']['meters'], dict):
                    yolink.water_meter_count = len(yolink.dataAPI[yolink.dData]['state']['state']['meters'])
                elif 'valves' in yolink.dataAPI[yolink.dData]['state']['state'] and isinstance(yolink.dataAPI[yolink.dData]['state']['state']['valves'], dict):
                    yolink.water_meter_count = len(yolink.dataAPI[yolink.dData]['state']['state']['valves'])
                else:
                    yolink.water_meter_count = 1 
                logging.info(f'Water Meter Controller - {yolink.water_meter_count} meters found')



    def setState(yolink, state):
        logging.debug(yolink.type+' - setState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            if state.lower() not in yolink.stateList:
                logging.error('Unknows state passed')
                return(False)
            if state.lower() == 'on':
                state = 'open'
            if state.lower() == 'off':
                state = 'closed'
            data = {}
            data['params'] = {}
            data['params']['valve'] = state.lower()
            return(yolink.setDevice(data))
        
    #def setAttrib(yolink, attributes):
    #    logging.debug(yolink.type+' - setAttributes')
    #    return(yolink.setAttributes(attributes))

    def getBattery(yolink):
        logging.debug(yolink.type+' - getBattery')
        bat_lvl = None
        pwr_mode = None
        logging.debug('online {} , data {}'.format(yolink.online, yolink.dataAPI[yolink.dData] ))
        if yolink.online:   
            if 'battery' in yolink.dataAPI[yolink.dData]:
                bat_lvl = yolink.dataAPI[yolink.dData]['battery']
            elif yolink.dState in yolink.dataAPI[yolink.dData] and 'battery' in yolink.dataAPI[yolink.dData][yolink.dState]: 
                bat_lvl = yolink.dataAPI[yolink.dData][yolink.dState]['battery']    
            if 'powerSupply' in yolink.dataAPI[yolink.dData]:                
                pwr_mode = yolink.dataAPI[yolink.dData]['powerSupply']
            elif yolink.dState in yolink.dataAPI[yolink.dData] and 'powerSupply' in yolink.dataAPI[yolink.dData][yolink.dState]:
                pwr_mode = yolink.dataAPI[yolink.dData][yolink.dState]['powerSupply']                   
        return(pwr_mode, bat_lvl)
    

    def getWaterTemperature(yolink):
        logging.debug(yolink.type+' - getWaterTemperature')
        water_temp = None
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            if yolink.dState in yolink.dataAPI[yolink.dData]:
                if 'temperature' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    water_temp = yolink.dataAPI[yolink.dData][yolink.dState]['temperature']
        return(water_temp)
    

    def getValveState(yolink, WM_index = None):
        logging.debug(yolink.type+' - getValveState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            if yolink.dState in yolink.dataAPI[yolink.dData]:
                if 'valve' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    if  yolink.dataAPI[yolink.dData][yolink.dState]['valve'] == 'open':
                        return('open')
                    elif yolink.dataAPI[yolink.dData][yolink.dState]['valve'] == 'close':
                        return('closed')
                    else:
                        return('Unkown')
                elif yolink.dState in yolink.dataAPI[yolink.dData][yolink.dState] and 'valves' in yolink.dataAPI[yolink.dData][yolink.dState][yolink.dState] :
                    if isinstance(yolink.dataAPI[yolink.dData][yolink.dState][yolink.dState]['valves'], dict):
                        valves = yolink.dataAPI[yolink.dData][yolink.dState][yolink.dState]['valves']
                        if isinstance( WM_index, int):
                            if str(WM_index) in valves:
                                if valves[str(WM_index)] == 'open':
                                    return('open')
                                elif valves[str(WM_index)] == 'close':
                                    return('closed')
                                else:
                                    return('Unkown')
            else:
                return(None)
    
    
    def getData(yolink, category, key, WM_index = None):    
        try:
            logging.debug(yolink.type+f' - getData category {category} key {key} {WM_index} {yolink.dataAPI[yolink.dData]}')
            ret_val = None  
            if yolink.online: 
                if category is None:
                    if key in yolink.dataAPI[yolink.dData]:
                        ret_val = yolink.dataAPI[yolink.dData][key]
                    
                if category in yolink.dataAPI[yolink.dData] and not isinstance(yolink.dataAPI[yolink.dData][category], dict):
                    logging.debug(f'{category} found as single value')
                    if key in yolink.dataAPI[yolink.dData][category]:
                        ret_val = yolink.dataAPI[yolink.dData][category][key]
                if yolink.dState in yolink.dataAPI[yolink.dData] :
                    logging.debug(f'[state] selected')
                    if category in yolink.dataAPI[yolink.dData][yolink.dState] :
                        logging.debug(f'category {category} found in state')
                        if key in yolink.dataAPI[yolink.dData][yolink.dState][category] and not isinstance(yolink.dataAPI[yolink.dData][yolink.dState][category][key], dict):
                            ret_val = yolink.dataAPI[yolink.dData][yolink.dState][category][key]
                if category in yolink.dataAPI[yolink.dData][yolink.dState]:
                    logging.debug(f" {category} found in [state] selected - {yolink.dataAPI[yolink.dData][yolink.dState][category]}")

                    if key in yolink.dataAPI[yolink.dData][yolink.dState][category]:
                        logging.debug(f'key {key} found in [state][{category}]')
                        if isinstance(yolink.dataAPI[yolink.dData][yolink.dState][category][key], dict):
                            logging.debug(f"key {key} is a dict {yolink.dataAPI[yolink.dData][yolink.dState][category][key]}")
                            items = yolink.dataAPI[yolink.dData][yolink.dState][category][key]                      
                            logging.debug(f'items for {key} found {items}')
                            if isinstance( WM_index, int):
                                if str(WM_index) in items:
                                    ret_val = items[str(WM_index)]
                            else:
                                ret_val = items
                        else:
                            ret_val = yolink.dataAPI[yolink.dData][yolink.dState][category][key]                              
            logging.debug(f'ret_val {ret_val} {key}  {category}')
            return(ret_val)
        
        except KeyError as e:
            logging.error(f'EXCEPTION - getData {e}') 
            return(None)

    def getMeterReading(yolink, WM_index = None):
        try:
            meter_correction_factor = 1
            logging.debug(yolink.type+f' - getMeterReading {json.dumps(yolink.dataAPI[yolink.dData], indent=4)}')
            temp = {'total':None, 'water_runing':None, 'recent_amount':None, 'recent_duration':None, 'daily_usage':None}
            #yolink.online = yolink.getOnlineStatus()
            logging.debug(f'temp1 {temp}')
            if yolink.online:   
                #logging.debug(f'yolink.dataAPI[yolink.dData][yolink.dState]: {yolink.dataAPI[yolink.dData][yolink.dState]} ')
                #if 'attributes' in yolink.dataAPI[yolink.dData] and 'meterStepFactor' in yolink.dataAPI[yolink.dData]['attributes']:
                #    meter_correction_factor = yolink.dataAPI[yolink.dData]['attributes']['meterStepFactor']
                meter_correction_factor = float(yolink.getData('attributes', 'meterStepFactor', WM_index))
                if meter_correction_factor is None:     
                    meter_correction_factor = 1.0   
                #logging.debug(f'logic {yolink.dState in yolink.dataAPI[yolink.dData]}')
                if 'meter' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    meter = yolink.getData(yolink.dState, 'meter', WM_index)
                    waterFlowing = yolink.getData(yolink.dState, 'waterFlowing', WM_index)
                elif 'state' in yolink.dataAPI[yolink.dData][yolink.dState] and 'meters' in yolink.dataAPI[yolink.dData][yolink.dState]['state']:                    
                    meter = yolink.getData(yolink.dState, 'meters', WM_index)
                    waterFlowing = yolink.getData(yolink.dState, 'waterFlowing', WM_index)
                logging.debug(f'meter {meter} waterFlowing {waterFlowing} ')
                
                #if yolink.dState in yolink.dataAPI[yolink.dData]:
                logging.debug(f'type of meter {type(meter)} type of waterFlowing {type(waterFlowing)} ')
                if not isinstance(meter, dict):
                    temp['total'] = round(meter/meter_correction_factor,1)
                    temp['water_runing'] = waterFlowing
                else:
                    for index in meter:
                        meter[WM_index] = round(meter[index]/meter_correction_factor,1)
                    temp['total'] = meter
                    temp['water_runing'] = waterFlowing

                recent_amount  = yolink.getData('recentUsage', 'amount', WM_index)
                recent_duration = yolink.getData('recentUsage', 'duration', WM_index)
                daily_usage = yolink.getData('dailyUsage', 'amount', WM_index)
                daily_duration = yolink.getData('dailyUsage', 'duration', WM_index) 
                if recent_amount is not None:
                    temp['recent_amount'] = round(recent_amount/meter_correction_factor,1)
                if recent_duration is not None:
                    temp['recent_duration'] = recent_duration
                if daily_usage is not None:
                    temp['daily_usage'] = round(daily_usage/meter_correction_factor,1)  
                else:
                    daily_usage = yolink.getData(None, 'dailyUsage', WM_index)
                if daily_duration is not None:
                    temp['daily_duration'] = daily_duration

                '''
                if 'recentUsage' in yolink.dataAPI[yolink.dData]:
                    if 'amount' in yolink.dataAPI[yolink.dData]['recentUsage']:
                        temp['recent_amount'] = round(yolink.dataAPI[yolink.dData]['recentUsage']['amount']/meter_correction_factor,1)
                    if 'duration' in yolink.dataAPI[yolink.dData]['recentUsage']:
                        temp['recent_duration'] = yolink.dataAPI[yolink.dData]['recentUsage']['duration']
                if 'dailyUsage' in yolink.dataAPI[yolink.dData]:
                    if isinstance(yolink.dataAPI[yolink.dData]['dailyUsage'], dict):
                        if 'amount' in yolink.dataAPI[yolink.dData]['dailyUsage']:
                            temp['daily_usage'] = round(yolink.dataAPI[yolink.dData]['dailyUsage']['amount']/meter_correction_factor,1)
                        if 'duration' in yolink.dataAPI[yolink.dData]['dailyUsage']:
                            temp['daily_duration'] = yolink.dataAPI[yolink.dData]['dailyUsage']['duration']           
                        else:
                            temp['daily_duration'] = None     
                    elif isinstance(yolink.dataAPI[yolink.dData]['dailyUsage'], int) or isinstance(yolink.dataAPI[yolink.dData]['dailyUsage'], float):
                        temp['daily_usage'] = round(yolink.dataAPI[yolink.dData]['dailyUsage']/meter_correction_factor,1)
                '''
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
            if yolink.online:   

                if 'alarm' in yolink.dataAPI[yolink.dData]:
                    alarms = yolink.dataAPI[yolink.dData]['alarm']
                    return(alarms)
                else:
                    return(None)
        except KeyError as e:
            logging.error(f'Exception : {e}')
            return(None)
        

    def getAttributes(yolink, WM_index = None):
        try:
            logging.debug(yolink.type+' - getAttributes')
            if yolink.online:   
                if 'attributes' in yolink.dataAPI[yolink.dData]:
                    attributes = yolink.dataAPI[yolink.dData]['attributes' ]
                    if 'meterUnit' in attributes and yolink.uom is None:
                        yolink.uom = attributes['meterUnit']
                    return(attributes)
                
                else:
                    return(None)
        except KeyError as e:
            logging.error(f'Exception : {e}')
            return(None)
        
"""


class YoLinkWaterMeterCtrl(YoLinkWaterMeter):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)