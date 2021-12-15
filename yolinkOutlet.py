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


class YoLinkOutl(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__( csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)
        
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdate'   ]
        yolink.eventList = ['StatusChange', 'Report', 'getState']
        yolink.stateList = ['open', 'closed', 'on', 'off']
        yolink.ManipulatorName = 'OutletEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'Outlet'
        time.sleep(2)
        
        #yolink.refreshState()
        #input()
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()


    def initNode(yolink):
        yolink.refreshState()
        if yolink.getOnlineStatus():
            yolink.refreshSchedules()

        #self.refreshFWversion()
        #print(' YoLinkSW - finished intializing')
 
    def updateStatus(self, data):
        self.updateCallbackStatus(data, False)

    def setState(yolink, state):
        logging.debug(yolink.type + ' - setState')

        if yolink.getOnlineStatus():
            if 'setState'  in yolink.methodList:          
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
                return(yolink.setDevice( data))
        else:
            return(False)
    
    def getDelays(yolink):
        if yolink.getOnlineStatus():
            return super().getDelays()


    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        if yolink.getOnlineStatus():       
            attempts = 0
            while yolink.dataAPI[yolink.dData][yolink.dState]  == {} and attempts < 5:
                time.sleep(1)
                attempts = attempts + 1
            if attempts <= 5 and yolink.dataAPI[yolink.dData][yolink.dState]:
                if  yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'open':
                    return('ON')
                elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'closed':
                    return('OFF')
                else:
                    return('Unkown')
            else:
                return('Unkown')
    
    def getEnergy(yolink):
        logging.debug(yolink.type+' - getEnergy')
        if yolink.getOnlineStatus():
            return({'power':yolink.dataAPI[yolink.dData][yolink.dState]['power'], 'watt':yolink.dataAPI[yolink.dData][yolink.dState]['power']})
        else:
            return({'power': -1, 'watt':-1})
    
    
class YoLinkOutlet(YoLinkOutl):
    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey,  deviceInfo, self.updateStatus, yolink_URL, mqtt_URL, mqtt_port)
        self.initNode()


    def updateStatus(self, data):
        self.updateCallbackStatus(data, True)