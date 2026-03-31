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


class YoLinkInfraredRemoter(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        
        #yolink.methodList = ['getState', 'learn', 'send'   ]
        #yolink.methodList = ['getState', 'send' , 'learn', 'getSchedule', 'setSchedule']
        #yolink.eventList = ['StatusChange', 'Report', 'getState']
        #yolink.stateList = []#['open', 'closed', 'on', 'off']
        #yolink.ManipulatorName = 'IREvent'
        #yolink.eventTime = 'Time'
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
        res = yolink.get_data('success')
        return(res)

    def getIRstatus_info (yolink):
        logging.debug('{} - getIRinfo'.format(yolink.type))
        info = {}
        info['success'] = yolink.get_data('success')
        info['errorCode'] = yolink.get_data('errorCode')
        info['key'] = yolink.get_data('key')
        info['IRtype'] = yolink.get_data('IRtype')

        return(info)

    def updateStatus(yolink, data):
        try:
            # NEEDS UPDATE 
            logging.debug('{} - updateStatus: {}'.format(yolink.type, data))

            yolink.updateCallbackStatus(data, False)
            data_section = yolink.data.setdefault(yolink.dData, {})
            logging.debug(f'updateStatus 1 {data}')
            #yolink.data[yolink.dData]['key'] = None
            #yolink.data[yolink.dData]['success'] = None
            #yolink.data[yolink.dData]['errorCode'] = None
            #yolink.data[yolink.dData]['IRtype'] = None
            time.sleep(0.5)
            #logging.debug(f'updateStatus 2 {data}')
            if 'method' in data:
                logging.debug(f'method detected`')
                if '.learn' in data['method']:
                    logging.debug('.learn detected')
                    if 'data' in data:
                        if 'success' in data['data']:
                            data_section['success'] = data['data']['success']
                        if 'errorCode' in data:
                            data_section['errorCode'] = data['data']['errorCode']
                        if 'key' in data:
                            data_section['key'] = data['data']['key']    
                        #yolink.data[yolink.dData]['IRtype'] = 'learn' 
                        
                        #yolink.learn_started = False  ## Not sure 
                if 'getState' in data['method']:
                    logging.debug('.getState detected')
                    if 'data' in data:
                        if 'battery' in data['data']:
                            data_section['battery'] = data['data']['battery']
                            logging.debug('battery: {}'.format(data_section['battery']))
                        if 'keys' in data['data']:
                            data_section['keys'] = data['data']['keys']
                            nbr_codes = 0
                            for indx in range(0,64):
                                if data_section['keys'][indx]:
                                    nbr_codes = nbr_codes + 1
                            yolink.nbr_codes = nbr_codes
                            logging.debug('keys: {} - {}'.format( yolink.nbr_codes, data_section['keys']))
                        #yolink.data[yolink.dData]['IRtype'] = None
                if 'send' in data['method']:
                    logging.debug('.send detected')
                    if 'data' in data:
                        if 'success' in data['data']:
                            data_section['success']  = data['data']['success']
                        if 'errorCode' in data:
                            data_section['errorCode'] = data['data']['errorCode']
                        if 'key' in data:
                            data_section['key'] = data['data']['key']
                        #yolink.data[yolink.dData]['IRtype'] = 'send'        

            if 'event' in data:
                logging.debug(f'event detected {json.dumps(data, sort_keys=True, indent=4, separators=(",", ": "))}')
                if '.learn' in data['event']:
                    if 'data' in data:
                        if 'success' in data['data']:
                            yolink.learn_started = data['data']['success']
                            data_section['success'] = yolink.learn_started
                        if 'errorCode' in data:
                            data_section['errorCode'] = data['data']['errorCode']
                        if 'key' in data:
                            data_section['key'] = data['data']['key']     
                        data_section['IRtype'] = 'learn'          
            logging.debug('{} - updateStatus after callback: {}'.format(yolink.type, data_section))                   
        except Exception as E:
            logging.error('{} - Exception - {} '.format(yolink.type, E))
            logging.error(yolink.data.get(yolink.dData, {}))

    def getBattery(yolink):
        try:
            battery = yolink.get_data('battery')
            if battery is None:
                battery = yolink.get_data('battery', 'state')
            return(battery)
        except Exception as E:
            logging.error('battery not defined : {}'.format(E))
       
    def get_code_dict(yolink):
        keys = yolink.get_data('keys')
        logging.debug(f'YoLinkInfraredRem get_code_dict {keys}')
        code_dict = {}
        if isinstance(keys, list):
            for code in range(0, len(keys)):
                code_dict[code] = keys[code]
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
    

    def check_learn_completed(yolink, code):
        logging.debug('YoLinkInfraredRem check_learn_completed {}'.format(code))
        try:
            logging.debug('Analyzed Message: {}'.format(yolink.getLastDataPacket()))
            key = yolink.get_data('key' )
            errorCode = yolink.get_data('errorCode' )
            success = yolink.get_data('success' )
            if  key == code:

                if errorCode == 'started':
                    logging.debug('Learn in progress')
                    return('learning')
                else:
                    logging.error('Error code {}'.format(errorCode))
                if success:
                    return('success')
                else:
                    return('failure')
            else:
                return('ignore')  


        except Exception as E:
            logging.error('YoLinkInfraredRem check_learn_completed - Exception: {}'.format(E))
            return('exception')
    
    def check_code_learned(yolink, code):
        logging.debug('YoLinkInfraredRem check_code_learned {}'.format(code))
        try:
            keys = yolink.get_data('keys')
            if isinstance(keys, list) and len(keys) >= code:
                return(keys[code-1])

        except:
            logging.debug('Keys not retrieved yet')

        yolink.refreshDevice()
        time.sleep(2)
        keys = yolink.get_data('keys')
        if isinstance(keys, list) and len(keys) >= code:
            return(keys[code-1])
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
        last_msg = yolink.getLastDataPacket()
        if isinstance(last_msg, dict) and last_msg != {}:
            if 'method' in last_msg:
                if '.getState' in last_msg['method']:
                    return('update_data')
                elif '.send'  in last_msg['method']:
                    return('send')
                elif '.learn'  in last_msg['method']:
                    return('learn')
                else:
                    logging.error('{} - get_last_message_type -unsupported method: {}'.format(yolink.type,last_msg['method']))
            elif 'event' in last_msg:
                if '.learn' in last_msg['event']:
                    return('learn')
                if '.Report' in last_msg['event']:
                    return('report')
                else:
                    logging.error('{} - get_last_message_type -unsupported event: {}'.format(yolink.type,last_msg['event']))
        else:
            return(None)
    '''
    def get_learn_status(yolink):
        logging.debug( '{} - get_learn_status'.format(yolink.type))
        temp = {}
        if yolink.data[yolink.dData]['key'] != None:
            temp['key'] = yolink.data[yolink.dData]['key']
            temp['success'] = yolink.data[yolink.dData]['success']
            temp['errorCode'] = yolink.data[yolink.dData]['errorCode']
        return(temp)
    '''
    def get_send_status(yolink):
        logging.debug( '{} - get_send_status'.format(yolink.type))

        temp = {}
        key = yolink.get_data('key')
        success = yolink.get_data('success')
        error_code = yolink.get_data('errorCode')
        if key is not None:
            temp['key'] = key
        if success is not None:
            temp['success'] = success
        if error_code is not None:
            temp['errorCode'] = error_code
        return(temp)

    def get_nbr_keys(yolink):
        logging.debug( '{} - get_nbr_keys'.format(yolink.type))
        keys = 0
        keys_data = yolink.get_data('keys')
        if isinstance(keys_data, list):
            for key in range(0, len(keys_data)):
                if keys_data[key]:
                    keys = keys + 1
        yolink.nbr_codes = keys
        return(keys)


        
