
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

    '''    
    def initNode(yolink):
        yolink.refreshSensor()
        time.sleep(2)
        #yolink.online = yolink.getOnlineStatus()
        if not yolink.online:
            logging.error('WaterDept not online')
    '''
    
    def updateStatus(self, data):
        logging.debug('updataStatus WaterDept  : {}'.format(data))
        self.updateCallbackStatus(data, False)

    def refreshSensor(yolink):
        logging.debug(yolink.type+ ' - refreshSensor')
        return(yolink.refreshDevice( ))

    def setAttributes(yolink, data):
        logging.debug(yolink.type+ ' - setAttributes')
    #def onlineStatus(yolink):
    #    logging.debug(yolink.type+ ' - getOnlineStatus')
    #    return(yolink.getOnlineStatus( ))

    def getAlarms(yolink, data):
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
            logging.error(f'Exception - waterdepth not found {data}' )
        
    def getAlarmsLevels(yolink, data):
        logging.debug(yolink.type+ ' - getAlarmsLevels')
        try:
            alarmLevels = {}
            if yolink.online:
                if yolink.dState in yolink.dataAPI[yolink.dData]:
                    alarmLevels['low'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['lowAlarm']
                    alarmLevels['high'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['highAlarm']

                elif 'waterDepth' in yolink.dataAPI[yolink.dData]:
                    alarmLevels['low'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['lowAlarm']
                    alarmLevels['high'] = yolink.dataAPI[yolink.dData][yolink.dState]['alarmSettings']['highAlarm']

            return(alarmLevels)
        
        except Exception as e:
            logging.error(f'Exception - waterdepth not found {data}' )
        


    def getWaterDepth(yolink, data):
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
            logging.error(f'Exception - waterdepth not found {data}' )
        
    '''
    def getAlarms(yolink):
        return(yolink.getStateValue('alarm'))

    def getBattery(yolink):
        return(yolink.getStateValue('battery'))
    '''    

    #def probeState(yolink):
    #     return(yolink.getState() )

    #def probeData(yolink):
    #    return(yolink.getData() )

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