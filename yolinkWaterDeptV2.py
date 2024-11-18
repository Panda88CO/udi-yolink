
import time


from yolink_mqtt_classV3 import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

class YoLinkWaterDept(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__( yoAccess,  deviceInfo, callback)    
        yolink.methodList = ['getState', 'setAttributes' ]
        yolink.eventList = ['Report']
        yolink.tempName = 'WaterDept'
        #yolink.temperature = 'Temperature'
        #yolink.humidity = 'Humidity'
        yolink.eventTime = 'Time'
        yolink.type = 'WaterDepthSensor'
        #time.sleep(2)
        yolink.alarmSettings = {'standby':None, 'interval':None, 'high':None, 'low':None}

    '''    
    def initNode(yolink):
        yolink.refreshSensor()
        time.sleep(2)
        #yolink.online = yolink.getOnlineStatus()
        if not yolink.online:
            logging.error('WaterDept not online')
    '''
    
    def updateStatus(yolink, data):
        logging.debug('updataStatus WaterDept  : {}'.format(data))
        yolink.updateCallbackStatus(data, False)
        yolink.alarmSettings = yolink.getAlarmSettings()

    def refreshSensor(yolink):
        logging.debug(yolink.type+ ' - refreshSensor')
        return(yolink.refreshDevice( ))

    def setAttributes(yolink, attribs):
        logging.debug(yolink.type+ ' - setAttributes')
        data = {}
        try:
            if 'setAttributes' in yolink.methodList:
                if 'alarmSettings' not in yolink.dataAPI[yolink.dData][yolink.dState]:
                    yolink.refreshDevice()

                if 'low' in attribs:
                    yolink.alarmSettings['low'] = attribs['low']
                else:
                    yolink.alarmSettings['low'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['low']
                if 'high' in attribs:
                    yolink.alarmSettings['high'] = attribs['high']
                else:
                    yolink.alarmSettings['high'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['high']

                if 'standby' in attribs:
                    yolink.alarmSettings['standby'] = attribs['standby']
                else:
                    yolink.alarmSettings['standby'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['standby']
                if 'interval' in attribs:
                    yolink.alarmSettings['interval'] = attribs['interval']    
                else:
                    yolink.alarmSettings['interval'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['interval']

                data['params'] = yolink.alarmSettings
                return(yolink.setDevice( data))

        except Exception as e:
            logging.error(f'Exception - setAttributes {e}' )
            return(False)
        
    
    def getAlarms(yolink):
        logging.debug(yolink.type+ ' - getAlarms')
        try:
            alarms = {}
            if yolink.online:
                if yolink.dState in yolink.dataAPI[yolink.dData]:
                    alarms['low'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarms']['lowAlarm']
                    alarms['high'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarms']['highAlarm']
                    alarms['error'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarms']['detectorError']  
                elif 'waterDepth' in yolink.dataAPI[yolink.dData]:
                    alarms['low'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarms']['lowAlarm']
                    alarms['high'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarms']['highAlarm']
                    alarms['error'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarms']['detectorError']  
            return(alarms)
        
        except Exception as e:
            logging.error(f'Exception - getAlarms data not found {yolink.dataAPI[yolink.dData]}' )
            return({})
        
    def getAlarmSettings(yolink):
        logging.debug(yolink.type+ ' - getAlarmsLevels')
        try:
            if yolink.online:
                if yolink.dState in yolink.dataAPI[yolink.dData]:
                    yolink.alarmSettings['low'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['low']
                    yolink.alarmSettings['high'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['high']
                    yolink.alarmSettings['standby'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['standby']
                    yolink.alarmSettings['interval'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['interval']


                elif 'waterDepth' in yolink.dataAPI[yolink.dData]:
                    yolink.alarmSettings['low'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['low']
                    yolink.alarmSettings['high'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['high']
                    yolink.alarmSettings['standby'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['standby']
                    yolink.alarmSettings['interval'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['interval']
            return(yolink.alarmSettings)
        
        except Exception as e:
            logging.error(f'Exception - getAlarmSettings not found {yolink.dataAPI[yolink.dData]}' )
            return({})
    

    def getWaterDepth(yolink):
        logging.debug(yolink.type+ ' - getWaterDepth')
        try:
            waterDepth = None
            if yolink.online:
                if yolink.dState in yolink.dataAPI[yolink.dData]:
                    waterDepth = yolink.dataAPI[yolink.dData][yolink.dState]['waterDepth']
                elif 'waterDepth' in yolink.dataAPI[yolink.dData]:
                     waterDepth = yolink.dataAPI[yolink.dData][yolink.dState]['waterDepth']
            return(waterDepth)
        
        except Exception as e:
            logging.error(f'Exception - getWaterDepth not found' )
        
'''
Stand-Alone Operation of WaterDept (no call back to live update data - pooling data in upper APP)
''' 

class YoLinkWaterDeptSens(YoLinkWaterDept):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__( yoAccess,  deviceInfo, yolink.updateStatus)    
        yolink.initNode()

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)