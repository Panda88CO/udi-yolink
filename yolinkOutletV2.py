import json
import time

from yolink_mqtt_classV3 import YoLinkMQTTDevice
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
        #time.sleep(2)
        
        #yolink.refreshState()
        #input()
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()

    '''
    def initNode(yolink):
        attemps = 0
        maxAttemts = 3
        yolink.refreshState()
        time.sleep(1)
        #yolink.online = yolink.getOnlineStatus()
        while not yolink.online and attemps <= maxAttemts:
            yolink.refreshState()
            time.sleep(1)
        if yolink.online:    
            logging.error('Outlet not online')
        #else:
        #   yolink.refreshSchedules()
        #self.refreshFWversion()
        #print(' YoLinkSW - finished intializing')
    '''
    
    def updateStatus(self, data):
        
        self.updateCallbackStatus(data, False)

    def setState(yolink, state):
        logging.debug(yolink.type + ' - setState')
        outlet = str(state)
        #yolink.online = yolink.getOnlineStatus()
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
    

    def getState(yolink):
        logging.debug(yolink.type+' - getState :{}'.format(yolink.dataAPI))
        dev_state = 'Unknown'
        #yolink.online = yolink.getOnlineStatus()
        try:
            if yolink.online or  'lastMessage' in yolink.dataAPI:
                logging.debug(yolink.type+' - getState online')
                #while yolink.dataAPI[yolink.dData][yolink.dState]  == {} and attempts < 3:
                #    time.sleep(1)
                #    attempts = attempts + 1
                logging.debug(yolink.type+' - getState data {}'.format(yolink.dataAPI[yolink.dData]))    
                #logging.debug(yolink.type+' - getState data  state {}'.format(yolink.dataAPI[yolink.dData][yolink.dState]))    
                if yolink.dState in yolink.dataAPI[yolink.dData]:
                    if isinstance(yolink.dataAPI[yolink.dData][yolink.dState], dict):
                        #logging.debug('DICT - {} '.format(yolink.dataAPI[yolink.dData][yolink.dState]))
                        temp = 'state' in yolink.dataAPI[yolink.dData][yolink.dState]

                        logging.debug('if  - {} '.format(temp))

                        if 'state' in yolink.dataAPI[yolink.dData][yolink.dState]:
                            #logging.debug('state  - {} '.format(yolink.dataAPI[yolink.dData][yolink.dState]['state']))
                            if  yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'open':
                                dev_state = 'ON'
                            elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'closed':
                                dev_state = 'OFF'

                        else:
                            dev_state = 'Unknown'
                        #logging.debug('dev_state  - {} '.format(dev_state))
                    else:
                        if  yolink.dataAPI[yolink.dData][yolink.dState] == 'open':
                            dev_state = 'ON'
                        elif yolink.dataAPI[yolink.dData][yolink.dState] == 'closed':
                            dev_state = 'OFF'
                        else:
                            dev_state = 'Unknown'
                else:
                    dev_state = 'Unknown'
            logging.debug(yolink.type+' - getState - return {} '.format(dev_state))
            return(dev_state)
        except Exception as e:
            logging.error('Exception - {} - {} '.format(yolink.type+' - getState' , e))
            return ('Unknown')
        
        
    def getEnergy(yolink):
        logging.debug(yolink.type+' - getEnergy : {}'.format(yolink.dataAPI))

        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:   
            try:    
                return({'power':yolink.dataAPI[yolink.dData][yolink.dState]['power'], 'watt':yolink.dataAPI[yolink.dData][yolink.dState]['watt']})
            except:
                return(None)
    
    
class YoLinkOutlet(YoLinkOutl):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)