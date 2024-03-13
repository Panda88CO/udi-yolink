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
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        yolink.eventList = ['StatusChange', 'Report']
        yolink.stateList = ['open', 'closed', 'on', 'off']
        yolink.ManipulatorName = 'WaterMeterControllerEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'WaterMeterController'
        yolink.MQTT_type = 'c'
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

    def getBattery(yolink):
        logging.debug(yolink.type+' - getBattery')
        bat_lvl = 99
        pwr_mode = 'Unknown'
        logging.debug('online {} , data {}'.format(yolink.online, yolink.dataAPI[yolink.dData] ))
        if yolink.online:   
            attempts = 0
            while yolink.dataAPI[yolink.dData]  == {} and attempts < 3:
                time.sleep(1)
                attempts = attempts + 1
            if attempts <= 3:
                if 'battery' in yolink.dataAPI[yolink.dData]:
                    bat_lvl = yolink.dataAPI[yolink.dData]['battery']
                if 'powerSupply' in yolink.dataAPI[yolink.dData]:
                    pwr_mode = yolink.dataAPI[yolink.dData]['powerSupply']
        return(pwr_mode, bat_lvl)
    

    def getValveState(yolink):
        logging.debug(yolink.type+' - getValveState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            attempts = 0
            if yolink.dState in yolink.dataAPI[yolink.dData]:
                while yolink.dataAPI[yolink.dData][yolink.dState]  == {} and attempts < 3:
                    time.sleep(1)
                    attempts = attempts + 1
                if attempts <= 3 and 'valve' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    if  yolink.dataAPI[yolink.dData][yolink.dState]['valve'] == 'open':
                        return('open')
                    elif yolink.dataAPI[yolink.dData][yolink.dState]['valve'] == 'closed':
                        return('closed')
                    else:
                        return('Unkown')
            else:
                return(None)
    
    def getMeterReading(yolink):
        logging.debug(yolink.type+' - getMeterReading')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            attempts = 0
            while yolink.dataAPI[yolink.dData][yolink.dState]  == {} and attempts < 3:
                time.sleep(1)
                attempts = attempts + 1
            if attempts <= 5:
                if  'meter' in yolink.dataAPI[yolink.dData][yolink.dState]:
                    return(round(yolink.dataAPI[yolink.dData][yolink.dState]['meter']/10,1))
                else:
                    return(None)
            else:
                return('Unknown')        

    def getAlarms(yolink):
        logging.debug(yolink.type+' - getAlarms')
        if yolink.online:   
            attempts = 0
            if yolink.dAlarm in yolink.dataAPI[yolink.dData]:
                while yolink.dataAPI[yolink.dData][yolink.dAlarm]  == {} and attempts < 3:
                    time.sleep(1)
                    attempts = attempts + 1
                if attempts <= 5 and yolink.dAlarm in yolink.dataAPI[yolink.dData]:
                    alarms = yolink.dataAPI[yolink.dData][yolink.dAlarm]
                    return(alarms)
                else:
                    return(None)
     
    def getData(yolink):
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            return(yolink.getData())


class YoLinkWaterMeterCtrl(YoLinkWaterMeter):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)