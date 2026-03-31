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

class YoLinkSiren(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__( yoAccess,  deviceInfo, callback)
        yolink.maxSchedules = 6
        #yolink.methodList = ['getState', 'setState']
        #yolink.stateList = ['normal', 'alert', 'off' ]
        #yolink.SirenName = 'SirenEvent'
        #yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
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
    def shut_down(yolink):
        logging.debug(yolink.type+' - shut_down')
        # Any thing specfic to do when polyglot stops
        return(True)
    
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def setState(yolink, state):
        state = str(state).lower()
        logging.debug(yolink.type+' - setState = {}'.format(state))
        #yolink.online = yolink.getOnlineStatus()
        if yolink.check_system_online():
            if state == 'on' or state == 'alert' or state == True:
                sirenState = True
            elif state == 'off' or state == 'normal' or state == False:
                sirenState = False
            else:
                logging.error('Unknows state passed - {}'.format(state))
                return(False)
            data = {}
            data['params'] = {}
            data['params']['state'] = {}
            data['params']['state']['alarm'] = sirenState
            return(yolink.setDevice(data))


    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        #yolink.online = yolink.getOnlineStatus()
        if yolink.check_system_online():
            attempts = 0
            while yolink.no_data() and attempts < 3:
                time.sleep(1)
                attempts = attempts + 1
            if attempts <= 5:
                state_data = yolink.get_data("state")
                if state_data and 'state' in state_data:
                    if state_data['state'] == 'normal':
                        return('normal')
                    elif state_data['state'] == 'alert':
                        return('alert')
                    elif state_data['state'] == 'off':
                        return('off')
                    else:
                        return('Unkown')
                else:
                    return('Unkown')
            else:
                return('Unkown')
    
    def getSupplyType(yolink):
        state_data = yolink.get_data("state")
        logging.debug(yolink.type+' - getSupplyType = {}'.format(state_data))
        try:
            if state_data and 'powerSupply' in state_data:
                if state_data['powerSupply'] == 'battery':
                    return('battery')
                else:
                    return('ext_supply')
        except Exception as e:
            logging.error('No supply type provided')
            return(None)   

    def getSirenDuration(yolink):
        state_data = yolink.get_data("state")
        logging.debug(yolink.type+' - getSirenDuration:{}'.format(state_data))
        try:
            if state_data and 'alarmDuation' in state_data:
                return (state_data['alarmDuation'])
            else:
                return (0)          
        except Exception as e:
            logging.error('No alarmDuration provided')
            return(None)   


    def getData(yolink):
        #yolink.online = yolink.getOnlineStatus()
        if yolink.check_system_online():   
            return(yolink.getData())


