import json
import time


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
        
        yolink.WMcount = None
        yolink.refreshDevice()
        yolink.water_meter_count = 1 
        time.sleep(2)   
        if not yolink.online:
            logging.error('Water Meter Controller device not online')

        #    yolink.refreshSchedules()
        #else:
        #    
        #yolink.refreshFW
    

    
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)


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
       

    def getValveState(yolink):
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
            else:
                return(None)
    
    def getMeterReading(yolink):
        try:
            meter_correction_factor = 1
            logging.debug(yolink.type+f' - getMeterReading {json.dumps(yolink.dataAPI[yolink.dData], indent=4)}')
            temp = {'total':None, 'water_runing':None, 'recent_amount':None, 'recent_duration':None, 'daily_usage':None}
            #yolink.online = yolink.getOnlineStatus()
            logging.debug(f'temp1 {temp}')
            if yolink.online:   
                #logging.debug(f'yolink.dataAPI[yolink.dData][yolink.dState]: {yolink.dataAPI[yolink.dData][yolink.dState]} ')
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

    def getAlarms(yolink):
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
        

    def getAttributes(yolink):
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
        


        

    #def getData(yolink):
        #yolink.online = yolink.getOnlineStatus()
    #    if yolink.online:   
    #        return(yolink.getData())

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
            logging.debug(yolink.type+f' - getData category {category} key {key} ')
            if yolink.online: 
                if category is None:
                    if key in yolink.dataAPI[yolink.dData]:
                        return(yolink.dataAPI[yolink.dData][key])
                if category in yolink.dataAPI[yolink.dData]:
                    logging.debug('category found')
                    if key in yolink.dataAPI[yolink.dData][category]:
                        return(yolink.dataAPI[yolink.dData][category][key])

                elif yolink.dState in yolink.dataAPI[yolink.dData]:
                    if category in yolink.dataAPI[yolink.dData][yolink.dState]:
                        logging.debug('category found in state')
                        if key in yolink.dataAPI[yolink.dData][yolink.dState][category]:
                            return(yolink.dataAPI[yolink.dData][yolink.dState][category][key])  
                elif 'state' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    if category in yolink.dataAPI[yolink.dData][yolink.dState]['state']:
                        logging.debug(f'category {category} found in [state][state]')
                        if isinstance(yolink.dataAPI[yolink.dData][yolink.dState]['state'][category], dict):
                            if key in yolink.dataAPI[yolink.dData][yolink.dState]['state'][category]:                            
                                items = yolink.dataAPI[yolink.dData][yolink.dState]['state'][category][key]
                                logging.debug(f'items for {key} found {items}')
                            if isinstance( WM_index, int):
                                if str(WM_index) in items:
                                    return(items[str(WM_index)])
                            else:
                                logging.error('WM_index not provided')
                                return(None)
                else:
                    return(None)       
            return(None)
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
                elif 'state' in yolink.dataAPI[yolink.dData][yolink.dState] and 'meters' in yolink.dataAPI[yolink.dData][yolink.dState]['state'] and isinstance(yolink.dataAPI[yolink.dData][yolink.dState]['state']['meters'], dict):
                    meter = yolink.getData(yolink.dState, 'meters', WM_index)
                    waterFlowing = yolink.getData(yolink.dState, 'waterFlowing', WM_index)
                logging.debug(f'meter {meter} waterFlowing {waterFlowing} ')
                
                if yolink.dState in yolink.dataAPI[yolink.dData]:
                    temp['total'] = round(meter/meter_correction_factor,1)
                    temp['water_runing'] = waterFlowing
                    #logging.debug('next {}'.format(yolink.dataAPI[yolink.dData][yolink.dState]['meter']))
                    #if 'meter' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    #    temp['total'] = round(yolink.dataAPI[yolink.dData][yolink.dState]['meter']/meter_correction_factor,1)
                    #if 'waterFlowing' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    #    temp['water_runing'] = yolink.dataAPI[yolink.dData][yolink.dState]['waterFlowing']
                    #logging.debug('next 2 {}'.format(temp ))

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
            logging.error(f'EXCEPTION - getMeterReading {e}') 
            return(None)

    def getAlarms(yolink):
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
        

    def getAttributes(yolink):
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
        


        

    #def getData(yolink):
        #yolink.online = yolink.getOnlineStatus()
    #    if yolink.online:   
    #        return(yolink.getData())


class YoLinkWaterMeterCtrl(YoLinkWaterMeter):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)