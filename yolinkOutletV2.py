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


class YoLinkOutl(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        
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
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:
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
                return(yolink.setDevice( data))
        else:
            return(False)
    
    def getDelays(yolink):
        yolink.online = yolink.getOnlineStatus()
        if yolink.online :
            return super().getDelays()


    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:       
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
        else:
            return('Unkown')

    def getEnergy(yolink):
        logging.debug(yolink.type+' - getEnergy')

        yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            return({'power':yolink.dataAPI[yolink.dData][yolink.dState]['power'], 'watt':yolink.dataAPI[yolink.dData][yolink.dState]['power']})
        else:
            return({'power': -1, 'watt':-1})
    
    
class YoLinkOutlet(YoLinkOutl):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)