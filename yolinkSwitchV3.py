import json
import time


from yolink_mqtt_classV4 import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)




class YoLinkSwitch(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        
        #yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        #yolink.eventList = ['StatusChange', 'Report', 'getState']
        #yolink.stateList = ['open', 'closed', 'on', 'off']
        #yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
        yolink.maxSchedules = 6
        logging.debug(f'Switch - GV23 maxSchedules: {yolink.maxSchedules}')
        #time.sleep(2)
        #print('yolink.refreshState')
        #yolink.refreshState()
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()
        #print(' YoLinkSW - finished initailizing')

    ''' Assume no event support needed if using MQTT'''
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def get_attributes(yolink):
        logging.debug(f'{yolink.type} ({yolink.name}) - get_attributes: attributes already populated via getState; skipping redundant API call')
        return ()

    def set_attributes(yolink, params):
        logging.debug(yolink.type+' - set_attributes {}'.format(params))
        if not params:
            return ()
        data = {'params': {}}
        if isinstance(params, dict):
            data['params'].update(params)
        return(yolink.setDeviceAttributes(data))
    def refreshDevice(yolink):
        logging.debug(f'{yolink.type} ({yolink.name}) - refreshDevice')
        methodStr = yolink.type + '.getState'
        data = {
            'method': methodStr,
            'targetDevice': yolink.deviceInfo['deviceId'],
            'token': yolink.deviceInfo['token'],
            'params': {}
        }
        yolink.yoAccess.publish_data(data)

    def initNode(yolink):
        yolink.refreshDevice()


    def setState(yolink, state):
        logging.debug(yolink.type+' - setState + {}'.format(state))
      
        if state.lower() in ['on', 'open']:
            state = 'open'
        if state.lower() in ['off', 'closed']:
            state = 'closed'
        data = {}
        data['params'] = {}
        data['params']['state'] = state.lower()
        return(yolink.setDevice( data))

    
    def getEventData(yolink):
        temp = yolink.get_event_from_state()
        logging.debug('getEventData: {}'.format(temp))
        return(temp)
    
    #def isControlEvent(yolink):
    #    return(yolink.isControlEvent())

    def clearEventData(yolink):
        if yolink.clear_event_from_state():
            logging.debug('clearEventData - SUCCESS:')

            
    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        attempts = 0

        while yolink.no_data() and attempts < 5:
            time.sleep(1)
            attempts = attempts + 1

        state_data = yolink.get_data('state')
        state_val = state_data.get('state') if isinstance(state_data, dict) else state_data

        if attempts < 5 and state_val == 'open':
            return('on')
        elif attempts < 5 and state_val == 'closed':
            return('off')
        else:
            return('Unkown')
    def getEnergy(yolink):
        logging.debug(yolink.type+' - getEnergy : {}'.format(yolink.data))

        #yolink.online = yolink.getOnlineStatus()
        if yolink.check_system_online():   
            try:
                power = yolink.get_data('power')
                watt = yolink.get_data('watt')
                if power is None and watt is None:
                    return(None)
                return({'power': power, 'watt': watt})
            except:
                return(None)
    

