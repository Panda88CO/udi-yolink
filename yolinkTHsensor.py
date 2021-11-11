import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

class YoLinkTHSensor(YoLinkMQTTDevice):

    def __init__(yolink, csName, csid, csseckey,  deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)    
        yolink.methodList = ['THSensor.getState' ]
        yolink.eventList = ['THSensor.Report']
        yolink.tempName = 'THEvent'
        yolink.temperature = 'Temperature'
        yolink.humidity = 'Humidity'
        yolink.eventTime = 'Time'
        yolink.type = 'THSensor'

        time.sleep(2)
        yolink.refreshSensor()
        
    def refreshSensor(yolink):
        logging.debug(yolink.type+ ' - refreshSensor')
        return(yolink.refreshDevice( ))
    '''
    def updateStatus(yolink, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in yolink.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                     yolink.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in yolink.eventList:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)
                    eventData = {}
                    eventData[yolink.tempName] = yolink.getState()
                    eventData[yolink.temperature] = yolink.getTempValueC()
                    eventData[yolink.humidity] = yolink.getHumidityValue()
                    eventData[yolink.eventTime] = data[yolink.messageTime]
                    yolink.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))
    '''

    def getTempValueF(yolink):
        return(yolink.getInfoValue('temperature')*9/5+32)
    
    def getTempValueC(yolink):
        return(yolink.getInfoValue('temperature'))

    def getHumidityValue(yolink):
        return(yolink.getInfoValue('humidity'))

    def getAlarms(yolink):
        return(yolink.getInfoValue('alarms'))

    def probeState(yolink):
         return(yolink.getState() )

    def probeData(yolink):
        return(yolink.getData() )