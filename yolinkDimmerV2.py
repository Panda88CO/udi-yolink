import json
import time


from yolink_mqtt_classV2 import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
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
        yolink.type = 'Dimmer'
        yolink.brightness = 50  #default

        #time.sleep(2)
        #print('yolink.refreshState')
        #yolink.refreshState()
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()
        #print(' YoLinkSW - finished initailizing')

    ''' Assume no event support needed if using MQTT'''
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)
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
    def setBrightness (yolink, brightness):
        logging.debug('setBrightness : {}'.format(brightness))
        yolink.brightness = int(brightness)
        if 'on' == yolink.getState():
            yolink.setState('on')
        else:
            yolink.setState('off')


    def setState(yolink, state):
        logging.debug(yolink.type+' - setState')
        logging.debug('Dimmer setState Brightness: {}'.format(yolink.brightness))
        if 'setState'  in yolink.methodList:          
            if state.lower() not in yolink.stateList:
                logging.error('Unknows state passed')
                return(False)
            if state.lower() == 'on':
                state = 'open'
            if state.lower() == 'off':
                state = 'close'
            data = {}
            data['params'] = {}
            data['params']['state'] = state.lower()
            data['params']['brightness'] = int(yolink.brightness)
            logging.debug('Dimmer setState Data {}'.format(data))
            return(yolink.setDevice( data))
        else:
            return(False)
    

    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        attempts = 0

        while yolink.dState not in yolink.dataAPI[yolink.dData] and attempts < 3:
            time.sleep(1)
            attempts = attempts + 1
        if attempts <3 and 'state' in yolink.dataAPI[yolink.dData][yolink.dState]:
            if 'brightness' in  yolink.dataAPI[yolink.dData][yolink.dState]:
                yolink.brightness = yolink.dataAPI[yolink.dData][yolink.dState]['brightness']
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

