import json
import time


from yolink_mqtt_classV3 import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    #logging = getlogger('yolink Dimmer')
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)



import time

class YoLinkDim(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        yolink.eventList = ['StatusChange', 'Report', 'getState']
        yolink.stateList = ['open', 'closed', 'on', 'off']
        yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']

        yolink.brightness = 50  #default
        yolink.ramp_up_time = 1 #sec
        yolink.ramp_down_time = 1 #sec
        yolink.min_level = 0
        yolink.max_level = 99

        #time.sleep(2)
        #print('yolink.refreshState')
        #yolink.refreshState()
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()
        #print(' YoLinkSW - finished initailizing')

    ''' Assume no event support needed if using MQTT'''
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)
        yolink.brightness = yolink.dataAPI[yolink.dData][yolink.dState]['brightness'] 
    '''
    def initNode(yolink):
        yolink.refreshState()
        time.sleep(2)
        if not yolink.online:
            logging.error('Switch not online')
        #    yolink.refreshSchedules()
        #else:
            
        #yolink.refreshFWversion()
        #print(' YoLinkSW - finished intializing')
    
    
    def getDelays(yolink):
        return super().getDelays()
    '''



    def setBrightness (yolink, brightness, force_on=False):
        logging.debug('setBrightness : {}'.format(brightness))
        yolink.brightness = int(brightness)
        yolink.dataAPI[yolink.dData][yolink.dState]['brightness'] = yolink.brightness

        logging.debug( 'SetBrightness getState(): {}'.format(yolink.getState()))
        if 'on' == yolink.getState() or force_on:
            yolink.setState('on')
        else:
            yolink.setState('off')
        logging.debug('setBrightness : {}'.format(yolink.brightness))    


    def setState(yolink, state):
        logging.debug(yolink.type+' - setState')
        logging.debug('Dimmer Brightness: {}'.format(yolink.brightness))

        #if 'setState'  in yolink.methodList:          
        if state.lower() not in yolink.stateList:
            logging.error('Unknows state passed')
            return(False)
        if state.lower() == 'on':
            state = 'open'
        if state.lower() == 'off':
            state = 'closed'
        data = {}
        data['params'] = {}
        data['params']['state'] = state.lower()
        data['params']['brightness'] = int(yolink.brightness)
        logging.debug('Dimmer setState Data {}'.format(data))
        return(yolink.setDevice( data))

    

    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        attempts = 0
        logging.debug('getState - {}'.format(yolink.dataAPI[yolink.dData] ))

        if 'state' in yolink.dataAPI[yolink.dData][yolink.dState]:
            if 'brightness' in  yolink.dataAPI[yolink.dData][yolink.dState]:
                yolink.brightness = yolink.dataAPI[yolink.dData][yolink.dState]['brightness']
            if 'deviceAttributes' in  yolink.dataAPI[yolink.dData][yolink.dState]:
                if 'gradient' in yolink.dataAPI[yolink.dData][yolink.dState]['deviceAttributes']:
                    if 'on' in yolink.dataAPI[yolink.dData][yolink.dState]['deviceAttributes']['gradient']:
                        yolink.ramp_up_time =  yolink.dataAPI[yolink.dData][yolink.dState]['deviceAttributes']['gradient']['on']
                    if 'off' in yolink.dataAPI[yolink.dData][yolink.dState]['deviceAttributes']['gradient']:
                        yolink.ramp_down_time =  yolink.dataAPI[yolink.dData][yolink.dState]['deviceAttributes']['gradient']['off']
                if 'calibration' in yolink.dataAPI[yolink.dData][yolink.dState]['deviceAttributes']:
                    yolink.min_level = yolink.dataAPI[yolink.dData][yolink.dState]['deviceAttributes']['calibration']
                if 'calibrationHigh' in yolink.dataAPI[yolink.dData][yolink.dState]['deviceAttributes']:
                    yolink.max_level = yolink.dataAPI[yolink.dData][yolink.dState]['deviceAttributes']['calibrationHigh']
                    if  yolink.max_level <= yolink.min_level :
                         yolink.max_level = yolink.min_level + 1             
            
            if  yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'open':
                return('on')
            elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'closed':
                return('off')
            else:
                return('Unkown')
            
            
        else:
            return('Unkown')

    '''
    def getEnergy(yolink):
        logging.debug(yolink.type+' - getEnergy')
        return({'power':yolink.dataAPI[yolink.dData][yolink.dState]['power'], 'watt':yolink.dataAPI[yolink.dData][yolink.dState]['power']})
    '''

class YoLinkDimmer(YoLinkDim):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)

