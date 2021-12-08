
import time


from yolink_mqtt_class import YoLinkMQTTDevice

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)


class YoLinkGarageDoorCtrl(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)
        yolink.methodList = ['toggle' ]
        yolink.eventList = ['Report']
        yolink.ToggleName = 'GarageEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'GarageDoor'
        time.sleep(1)
        
    def toggleDevice(yolink):
        logging.debug(yolink.type+' - toggle')
        data={}
        return(yolink.setDevice(data))

    def updataStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)
    '''
    def updateStatus(yolink, data):
        logging.debug(' YoLinkGarageDoorCtrl - updateStatus')  
        #special case 
        if 'method' in  data:
            if  data['method'] == 'GarageDoor.toggle' and  data['code'] == '000000':
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)
                    #yolink.updateGarageCtrlStatus(data)

        elif 'event' in data: # not sure events exits
            if data['event'] in yolink.eventList:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)
                    eventData = {}
                    eventData[yolink.ToggleName] = yolink.getState()
                    eventData[yolink.eventTime] = yolink.data[yolink.messageTime]
                    yolink.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))
    '''
    
class YoLinkGarageDoorToggle(YoLinkGarageDoorCtrl):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)
        #yolink.initNode()


    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)