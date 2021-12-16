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
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            yolink.refreshSchedules()
        else:
            logging.error('Outlet not online')
       
        #self.refreshFWversion()
        #print(' YoLinkSW - finished intializing')
 
    def updateStatus(self, data):
        self.updateCallbackStatus(data, False)

    def setState(yolink, state):
        logging.debug(yolink.type + ' - setState')
        outlet = str(state)
        if yolink.getOnlineStatus():
            if 'setState'  in yolink.methodList:          
                if outlet.lower() not in yolink.stateList:
                    logging.error('Unknows state passed')
                    return(False, yolink.dataAPI[yolink.dOnline])
                if outlet.lower() == 'on':
                    state = 'open'
                if state.lower() == 'off':
                    state = 'closed'
                data = {}
                data['params'] = {}
                data['params']['state'] = state.lower()
                return(yolink.setDevice( data), yolink.dataAPI[yolink.dOnline])
        else:
            return(False, yolink.dataAPI[yolink.dOnline])
    
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
                    return('ON', yolink.dataAPI[yolink.dOnline])
                elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'closed':
                    return('OFF', yolink.dataAPI[yolink.dOnline])
                else:
                    return('Unkown', yolink.dataAPI[yolink.dOnline])
            else:
                return('Unkown', yolink.dataAPI[yolink.dOnline])
        else:
            return('Unkown', yolink.dataAPI[yolink.dOnline])

    def getEnergy(yolink):
        logging.debug(yolink.type+' - getEnergy')
        if yolink.getOnlineStatus():
            return({'power':yolink.dataAPI[yolink.dData][yolink.dState]['power'], 'watt':yolink.dataAPI[yolink.dData][yolink.dState]['power']})
        else:
            return({'power': -1, 'watt':-1}, yolink.dataAPI[yolink.dOnline])
    
    
class YoLinkOutlet(YoLinkOutl):
    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey,  deviceInfo, self.updateStatus, yolink_URL, mqtt_URL, mqtt_port)
        self.initNode()


    def updateStatus(self, data):
        self.updateCallbackStatus(data, True)