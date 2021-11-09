import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)


class YoLinkGarageDoorToggle(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        self.methodList = ['toggle' ]
        self.eventList = ['Report']
        self.ToggleName = 'GarageEvent'
        self.eventTime = 'Time'
        self.type = 'GarageDoor'
        time.sleep(1)
        

    def toggleDevice(self):
        logging.debug(self.type+' - toggle')
        data={}
        return(self.setDevice(data))



    def updateStatus(self, data):
        logging.debug(' YoLinkGarageDoorCtrl updateStatus')  
        #special case 
        if 'method' in  data:
            if  data['method'] == 'GarageDoor.toggle' and  data['code'] == '000000':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)
                    #self.updateGarageCtrlStatus(data)

        elif 'event' in data: # not sure events exits
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)
                    eventData = {}
                    eventData[self.ToggleName] = self.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    