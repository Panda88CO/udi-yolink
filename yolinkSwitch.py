import json
import time


from yolink_mqtt_class import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)




class YoLinkSW(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)
        
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        yolink.eventList = ['StatusChange', 'Report', 'getState']
        yolink.stateList = ['open', 'closed', 'on', 'off']
        yolink.eventTime = 'Time'
        yolink.type = 'Switch'
        time.sleep(3)
        #print('yolink.refreshState')
        #yolink.refreshState()
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()
        #print(' YoLinkSW - finished initailizing')

    ''' Assume no event support needed if using MQTT'''
    def updataStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def initNode(yolink):

        yolink.refreshState()
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            yolink.refreshSchedules()
        else:
            logging.error('Switch not online')
        #yolink.refreshFWversion()
        #print(' YoLinkSW - finished intializing')
 
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def getDelays(yolink):
        return super().getDelays()

    def setState(yolink, state):
        logging.debug(yolink.type+' - setState')

        if 'setState'  in yolink.methodList:          
            if state.lower() not in yolink.stateList:
                logging.error('Unknows state passed')
                return(False, yolink.dataAPI[yolink.dOnline])
            if state.lower() == 'on':
                state = 'open'
            if state.lower() == 'off':
                state = 'closed'
            data = {}
            data['params'] = {}
            data['params']['state'] = state.lower()
            return(yolink.setDevice( data), yolink.dataAPI[yolink.dOnline])
        else:
            return(False, yolink.dataAPI[yolink.dOnline])
    

    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        attempts = 0

        while yolink.dState not in yolink.dataAPI[yolink.dData] and attempts < 5:
            time.sleep(1)
            attempts = attempts + 1
        if attempts < 5 and 'state' in yolink.dataAPI[yolink.dData][yolink.dState]:
            if  yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'open':
                return('ON')
            elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'closed':
                return('OFF')
            else:
                return('Unkown')
        else:
            return('Unkown')
    '''
    def getEnergy(yolink):
        logging.debug(yolink.type+' - getEnergy')
        return({'power':yolink.dataAPI[yolink.dData][yolink.dState]['power'], 'watt':yolink.dataAPI[yolink.dData][yolink.dState]['power']})
    '''

class YoLinkSwitch(YoLinkSW):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey,  deviceInfo, yolink.updateStatus, yolink_URL, mqtt_URL, mqtt_port)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)

