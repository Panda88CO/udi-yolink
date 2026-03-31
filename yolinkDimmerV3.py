import json
import time


from yolink_mqtt_classV4 import YoLinkMQTTDevice
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
        
        #yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        #yolink.eventList = ['StatusChange', 'Report', 'getState']
        #yolink.stateList = ['open', 'closed', 'on', 'off']
        #yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
        yolink.maxSchedules = 6
        logging.debug(f'Dimmer - GV23 maxSchedules: {yolink.maxSchedules}')

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
        brightness = yolink.get_data('brightness')
        if isinstance(brightness, (int, float)):
            yolink.brightness = int(brightness)
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

    def get_attributes(yolink):
        logging.debug('get_attributes')
        yolink.setDeviceAttributes(None)
        return()




    def setBrightness (yolink, brightness, force_on=False):
        logging.debug('setBrightness : {}'.format(brightness))
        yolink.brightness = int(brightness)

        logging.debug( 'SetBrightness getState(): {}'.format(yolink.getState()))
        if 'on' == yolink.getState() or force_on:
            yolink.setState('on')
        else:
            yolink.setState('off')
        logging.debug('setBrightness : {}'.format(yolink.brightness))    


    def setState(yolink, state, brightness=None):
        logging.debug(yolink.type+' - setState')
        logging.debug('Dimmer Brightness: {}'.format(yolink.brightness))

        #if 'setState'  in yolink.methodList:          
        if state.lower() in['on', 'open']:
            state = 'open'
        if state.lower() in ['off', 'closed']:
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
        while yolink.no_data() and attempts < 3:
            time.sleep(1)
            attempts = attempts + 1

        state_data = yolink.get_data('state')
        logging.debug('getState - {}'.format(state_data))

        if isinstance(yolink.get_data('brightness'), (int, float)):
            yolink.brightness = int(yolink.get_data('brightness'))

        ramp_up = yolink.get_data('on', 'gradient')
        ramp_down = yolink.get_data('off', 'gradient')
        min_level = yolink.get_data('calibration', 'deviceAttributes')
        max_level = yolink.get_data('calibrationHigh', 'deviceAttributes')

        if isinstance(ramp_up, (int, float)):
            yolink.ramp_up_time = ramp_up
        if isinstance(ramp_down, (int, float)):
            yolink.ramp_down_time = ramp_down
        if isinstance(min_level, (int, float)):
            yolink.min_level = min_level
        if isinstance(max_level, (int, float)):
            yolink.max_level = max_level
            if yolink.max_level <= yolink.min_level:
                yolink.max_level = yolink.min_level + 1

        state_val = state_data.get('state') if isinstance(state_data, dict) else state_data

        if state_val == 'open':
            return('on')
        elif state_val == 'closed':
            return('off')
        else:
            return('Unkown')

class YoLinkDimmer(YoLinkDim):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)

