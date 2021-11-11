import json
import time
import logging

from yolink_mqtt_class import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)


class YoLinkMultiOutlet(YoLinkMQTTDevice):

    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)
        yolink.maxSchedules = 6
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdates'   ]
        yolink.eventList = ['StatusChange', 'Report']
        yolink.type = 'MultiOutlet'
        yolink.ManipulatorName = 'MultiOutletEvent'
        yolink.eventTime = 'Time'
        time.sleep(3)
        yolink.refreshMultiOutlet() # needed to get number of ports on device
        yolink.refreshSchedules()
        #yolink.refreshFWversion()

    '''
    def getSchedules (yolink):
        return(yolink.dataAPI['data']['schedules'])  

    def getDelays (yolink):
        return(yolink.dataAPI['data']['delays'])  
    '''

    '''
    def updateStatus(yolink, data):
        logging.debug(yolink.type+' - updateStatus')
        if 'method' in  data:
            if  (data['method'] == 'MultiOutlet.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)             
            elif  (data['method'] == 'MultiOutlet.setState' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)                                       
            elif  (data['method'] == 'MultiOutlet.setDelay' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateDelayStatus(data)
            elif  (data['method'] == 'MultiOutlet.getSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateScheduleStatus(data)
            elif  (data['method'] == 'MultiOutlet.setSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()): 
                    yolink.updateScheduleStatus(data)
            elif  (data['method'] == 'MultiOutlet.getVersion' and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateFWStatus(data)

            else:
                logging.debug('Unsupported Method passed' + str(json.dumps(data)))
        elif 'event' in data:
            if data['event'] == 'MultiOutlet.StatusChange':
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateMultiStatusData(data)    

            elif data['event'] == 'MultiOutlet.Report':
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateMultiStatusData(data)  

            else :
                logging.debug('Unsupported Event passed' + str(json(data)))
    '''                                    

    def refreshMultiOutlet(yolink):
        return(yolink.refreshDevice())
    

    def setMultiOutletState(yolink, portList, value ):
        logging.debug( yolink.type+'- setMultiOutletState')
        # portlist a a listof ports being changed port range 0-7
        # vaue is state that need to change 2 (ON/OFF)
        status = True
        port = 0
        for i in portList:
            if i <= yolink.nbrPorts and i >= 0 :
                port = port + pow(2, i)
            else:
                logging.error('wrong port number (range 0- '+str(yolink.nbrPorts)+'): ' + str(i))
                status = False
        if value.upper() == 'ON' or value.upper() == 'OPEN':
            state = 'open'
        elif value.upper() == 'OFF' or value.upper() == 'CLOSED' :
            state = 'closed'
        else:
            logging.error('Unknows state passed')
            status = False
        if status:
            data={}
            data["params"] = {}
            data["params"]["chs"] =  port
            data["params"]['state'] = state
            yolink.setDevice( 'MultiOutlet.setState', data, yolink.updateStatus)
        return(status)
    

   

    def getMultiOutletState(yolink):
        logging.debug(yolink.type+' - getMultiOutletState')
        yolink.refreshMultiOutlet()
        temp = yolink.getInfoAPI()
        states= {}
        for port in range(0,yolink.nbrPorts):
            if 'delays' in temp['data']:
                delay = None
                for ch in  temp['data']['delays']:
                    if ch['ch'] == port:
                        delay = ch
                states['port'+str(port)]= {'state':temp['data']['state'][port], 'delays':delay}
        #print(states)
        return(states)

    def getMultiOutletData(yolink):
        logging.debug(yolink.type+' - getMultiOutletState')
  
    '''
    def refreshFWversion(yolink):
        logging.debug('refreshFWversion - not currently supported')
        #return(yolink.refreshDevice('MultiOutlet.getVersion',  yolink.updateStatus))

    def startUpgrade(yolink):
        logging.debug('startUpgrade - not currently supported')
    
    def checkStatusChanges(yolink):
        logging.debug('checkStatusChanges')
    '''

    '''
    def resetDelayList (yolink):
        yolink.delayList = []

    def appendDelay(yolink, delay):
        # to remove a delay program it to 0 
        try:
            invalid = False
            if 'port' in delay  and 'OnDelay' in delay and 'OffDelay' in delay:
                if delay['port'] <0 and delay['port'] >= yolink.nbrPorts:
                    invalid = True
                if 'OnDelay' in delay:
                    if delay['OnDelay'] < 0:
                        invalid = True
                if 'OffDelay' in delay:
                    if delay['OffDelay'] < 0:
                        invalid = True
            elif  'OnDelay' in delay and 'OffDelay' in delay:
                if 'OnDelay' in delay:
                    if delay['OnDelay'] < 0:
                        invalid = True
                if 'OffDelay' in delay:
                    if delay['OffDelay'] < 0:
                        invalid = True
                delay['port'] = 1 #use channel 1 for non-multi port devices
            else:
                logging.debug('Missing or wrong input parameters: ' + str(delay))
            if not invalid:
                yolink.delayList.append(delay)
            return(invalid)
        except logging.exception as E:
            logging.debug('Exception appendDelay : ' + str(E))

    def prepareDelayData(yolink):
        data={}
        data['params'] = {}
        nbrDelays = len(yolink.delayList)
        data["params"]["delays"] = []
        if nbrDelays > 0:
            for delayNbr in range (0,nbrDelays):
                #temp = yolink.delayList[delayNbr]
                temp = {}
                temp['ch'] = yolink.delayList[delayNbr]['port']
                temp['on'] = yolink.delayList[delayNbr]['OnDelay']
                temp['off'] = yolink.delayList[delayNbr]['OffDelay']
                
                data["params"]["delays"].append(temp)
                #temp['on'] = tmp['OnDelay']
                #temp['off'] = tmp['OffDelay']
                #data["params"]["delays"].append(temp)
        return(data)
    '''