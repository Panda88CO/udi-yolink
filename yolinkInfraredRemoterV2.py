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


class YoLinkInfraredRem(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        
        #yolink.methodList = ['getState', 'learn', 'send'   ]
        yolink.methodList = ['getState', 'send' , 'learn']
        yolink.eventList = ['StatusChange', 'Report', 'getState']
        yolink.stateList = []#['open', 'closed', 'on', 'off']
        yolink.ManipulatorName = 'IREvent'
        yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
        yolink.learn_started = False
        yolink.nbr_codes = 0
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
    def get_status_code(yolink):
        logging.debug('{} - get_error_code'.format(yolink.type))
        if 'success' in yolink.dataAPI[yolink.dData]:
            if  yolink.dataAPI[yolink.dData]['success']:
                return('success')
            if 'errorCode' in yolink.dataAPI[yolink.dData]:
                return(yolink.dataAPI[yolink.dData]['errorCode'])
            else:
                return('unknown')

    def getIRstatus_info (yolink):
        logging.debug('{} - getIRinfo'.format(yolink.type))
        info = {}
        info['success'] = yolink.dataAPI[yolink.dData]['success'] 
        info['errorCode'] = yolink.dataAPI[yolink.dData]['errorCode']
        info['key'] = yolink.dataAPI[yolink.dData]['key']
        info['IRtype'] = yolink.dataAPI[yolink.dData]['IRtype'] 

        return(info)

    def updateStatus(yolink, data):
        try:
            logging.debug('{} - updateStatus: {}'.format(yolink.type, data))
            yolink.updateCallbackStatus(data, False)
            yolink.dataAPI[yolink.dData]['key'] = None
            yolink.dataAPI[yolink.dData]['success'] = None
            yolink.dataAPI[yolink.dData]['errorCode'] = None
            yolink.dataAPI[yolink.dData]['IRtype'] = None
            
            if 'method' in data:
                if '.learn' in data['method']:
                    if 'data' in data:
                        if 'success' in data['data']:
                            yolink.dataAPI[yolink.dData]['success'] = data['data']['success']
                        if 'errorCode' in data:
                            yolink.dataAPI[yolink.dData]['errorCode']= data['data']['errorCode']
                        if 'key' in data:
                            yolink.dataAPI[yolink.dData]['key'] = data['data']['key']    
                        yolink.dataAPI[yolink.dData]['IRtype'] = 'learn' 
                        yolink.learn_started = False  ## Not sure 
                if 'getState' in data['method']:
                    if 'data' in data:
                        if 'battery' in data['data']:
                            yolink.dataAPI[yolink.dData]['battery'] = data['data']['battery']
                            logging.debug('battery: {}'.format(yolink.dataAPI[yolink.dData]['battery']))
                        if 'keys' in data['data']:
                            yolink.dataAPI[yolink.dData]['keys'] = data['data']['keys']
                            nbr_codes = 0
                            for indx in range(0,64):
                                if yolink.dataAPI[yolink.dData]['keys'][indx]:
                                    nbr_codes = nbr_codes + 1
                            yolink.nbr_codes = nbr_codes
                            logging.debug('keys: {} - {}'.format( yolink.nbr_codes, yolink.dataAPI[yolink.dData]['keys']))
                        yolink.dataAPI[yolink.dData]['IRtype'] = None
                if 'send' in data['method']:
                    if 'data' in data:
                        if 'success' in data['data']:
                            yolink.dataAPI[yolink.dData]['success']  = data['data']['success']
                        if 'errorCode' in data:
                            yolink.dataAPI[yolink.dData]['errorCode']= data['data']['errorCode']
                        if 'key' in data:
                            yolink.dataAPI[yolink.dData]['key'] = data['data']['key']
                        yolink.dataAPI[yolink.dData]['IRtype'] = 'send'        

            if 'event' in data:
                if '.learn' in data['event']:
                    if 'data' in data:
                        if 'success' in data['data']:
                            yolink.learn_started = data['data']['success']
                            yolink.dataAPI[yolink.dData]['success'] = yolink.learn_started
                        if 'errorCode' in data:
                            yolink.dataAPI[yolink.dData]['errorCode'] = data['data']['errorCode']
                        if 'key' in data:
                            yolink.dataAPI[yolink.dData]['key'] = data['data']['key']     
                        yolink.dataAPI[yolink.dData]['IRtype'] = 'learn'          
            logging.debug('{} - updateStatus after callback: {}'.format(yolink.type, yolink.dataAPI[yolink.dData]))                   
        except Exception as E:
            logging.error('{} - Exception - {} '.format(yolink.type, E))
            logging.error (yolink.dataAPI[yolink.dData])

    def getBattery(yolink):
        try:
            return(yolink.dataAPI[yolink.dData]['battery'])
        except Exception as E:
            logging.error('battery not defined : {}'.format(E))
       
    def get_code_dict(yolink):
        logging.debug(f'YoLinkInfraredRem get_code_dict {yolink.dataAPI[yolink.dData]}')
        code_dict = {}
        if 'keys' in yolink.dataAPI[yolink.dData]:
            for code in range(0,len(yolink.dataAPI[yolink.dData]['keys'])):
                code_dict[code] =  yolink.dataAPI[yolink.dData]['keys'][code]
        return(code_dict)
           
    
    def learn(yolink, code):
        yolink.send_learn(code)
        
    
    def send_learn(yolink, code):
        logging.debug('YoLinkInfraredRem learn_code {}'.format(code))
        if yolink.learn_started == False:
            if  0 <= code <= 63:
                attempt = 1

                if 'send' in yolink.methodList:
                    methodStr = yolink.type+'.learn'
                    worked = True
                data = {}
                data['params'] = {}
                data['params']['key'] = code
                data['time'] = str(int(time.time_ns()//1e6))
                data['method'] = methodStr
                data["targetDevice"] =  yolink.deviceInfo['deviceId']
                data["token"]= yolink.deviceInfo['token']
                yolink.yoAccess.publish_data(data) 
                yolink.learn_started = True
                return(True)

            else:
                logging.error('Code {} out of range (0-63)'.format(code))
                yolink.learn_started = False
                return (False)
        else:
            logging.error('previous send_learn not completed - cannot start another')
    
    
    def check_code_learned(yolink, code):
        logging.debug('YoLinkInfraredRem check_code_learned {}'.format(code))
        try:
            return(yolink.dataAPI[yolink.dData]['keys'][code-1])
                
        except:
            logging.debug('Keys not retrieved yet')
            yolink.refreshDevice()
            time.sleep(2)
            if 'keys' in yolink.dataAPI[yolink.dData]:
                return(yolink.dataAPI[yolink.dData]['keys'][code-1])
            else:
                return(False)

    def send_code(yolink, code) -> bool:
        logging.debug('YoLinkInfraredRem send_code {}'.format(code))
        
        try:

            if 'send' in yolink.methodList:
                methodStr = yolink.type+'.send'
                data = {}
                data['params'] = {}
                data['params']['key'] = code
                data['time'] = str(int(time.time_ns()//1e6))
                data['method'] = methodStr
                data["targetDevice"] =  yolink.deviceInfo['deviceId']
                data["token"]= yolink.deviceInfo['token']
                yolink.yoAccess.publish_data(data) 
                return(True)
        except  Exception as E:
            logging.error('YoLinkInfraredRem send_code - Exception: {}'.format(E))
            return(False)
        

    def get_last_message_type(yolink):
        logging.debug( '{} - get_last_message_type'.format(yolink.type))
        if yolink.dataAPI[yolink.lastMessage] != {}:
            if 'method' in yolink.dataAPI[yolink.lastMessage]:
                if '.getState' in yolink.dataAPI[yolink.lastMessage]['method']:
                    return('update_data')
                elif '.send'  in yolink.dataAPI[yolink.lastMessage]['method']:
                    return('send')
                elif '.learn'  in yolink.dataAPI[yolink.lastMessage]['method']:
                    return('learn')               
                else:
                    logging.error('{} - get_last_message_type -unsupported method: {}'.format(yolink.type,yolink.dataAPI[yolink.lastMessage]['method']))
            elif 'event' in yolink.dataAPI[yolink.lastMessage]:
                if '.learn' in yolink.dataAPI[yolink.lastMessage]['event']:
                    return('learn')
                if '.Report' in yolink.dataAPI[yolink.lastMessage]['event']:
                    return('report')            
                else:
                    logging.error('{} - get_last_message_type -unsupported event: {}'.format(yolink.type,yolink.dataAPI[yolink.lastMessage]['event']))
        else:
            return(None)
    '''
    def get_learn_status(yolink):
        logging.debug( '{} - get_learn_status'.format(yolink.type))
        temp = {}
        if yolink.dataAPI[yolink.dData]['key'] != None:
            temp['key'] = yolink.dataAPI[yolink.dData]['key']
            temp['success'] = yolink.dataAPI[yolink.dData]['success']
            temp['errorCode'] = yolink.dataAPI[yolink.dData]['errorCode']
        return(temp)
    '''
    def get_send_status(yolink):
        logging.debug( '{} - get_send_status'.format(yolink.type))
        
        temp = {}
        if yolink.dataAPI[yolink.dData]['key'] != None:
            temp['key'] = yolink.dataAPI[yolink.dData]['key']
            temp['success'] = yolink.dataAPI[yolink.dData]['success']
            temp['errorCode'] = yolink.dataAPI[yolink.dData]['errorCode']
        return(temp)

    def get_nbr_keys(yolink):
        logging.debug( '{} - get_nbr_keys'.format(yolink.type))
        keys = 0
        for key in range (0,len(yolink.dataAPI[yolink.dData]['keys'])):
            if yolink.dataAPI[yolink.dData]['keys'][key]:
                keys = keys + 1
        yolink.nbr_codes = keys
        return(keys)


        
class YoLinkInfraredRemoter(YoLinkInfraredRem):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    #def updateStatus(yolink, data):
    #    yolink.updateCallbackStatus(data, True)