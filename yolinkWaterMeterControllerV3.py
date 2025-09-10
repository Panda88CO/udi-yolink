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
            logging.error('Manipulator device not online')
        #    yolink.refreshSchedules()
        #else:
        #    
        #yolink.refreshFW
    ''' 

    
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
        bat_lvl = 99
        pwr_mode = 'Unknown'
        logging.debug('online {} , data {}'.format(yolink.online, yolink.dataAPI[yolink.dData] ))
        if yolink.online:   
            if 'battery' in yolink.dataAPI[yolink.dData]:
                bat_lvl = yolink.dataAPI[yolink.dData]['battery']
            if 'powerSupply' in yolink.dataAPI[yolink.dData]:
                pwr_mode = yolink.dataAPI[yolink.dData]['powerSupply']
        return(pwr_mode, bat_lvl)
    

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


class YoLinkWaterMeterCtrl(YoLinkWaterMeter):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)