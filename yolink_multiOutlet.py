import hashlib
import time
import json
import requests
import sys
from yolink_devices import YoLinkDevice
#from logger import getLogger
#log = getLogger(__name__)

"""
Object representatiaon for YoLink Device
"""
class MultiOutlet(YoLinkDevice):

    def __init__(self, yolinkURL, csid, csseckey, serial_num, CSname, yolink_client, IDstring):
        super().__init__(yolinkURL, csid, csseckey, serial_num)
        self.url = yolinkURL
        self.csid = csid
        self.csseckey = csseckey
        self.serial_number = serial_num

        self.data = {}
        #self.header = {}
        self.device_data = {}

        yolink_client.subscribe_data(self.mqttResponseStr)
        yolink_client.subscribe_data(self.mqttReportStr)
        time.sleep(1)


    def setState(self, portList, output):
        print('setState')
        data = {}
        data["method"] = self.get_type()+str('.setState')
        data["time"] = str(int(time.time())*1000)
        data["token"]= self.get_token()
        data["params"] =  {}
        portCtrl = 0
        for port in portList:
            portCtrl = portCtrl + pow(2, port)
        data["params"]["chs"] =  int(portCtrl)
        if output.upper() == 'ON':
            state = 'open'
        else:
            state = 'closed'
        data["params"]["state"] = state
        data["targetDevice"] =  self.get_id()
        dataTemp = str(json.dumps(data))
        self.yolink_client.publish_data(self.mqttRequestStr, dataTemp)



    def getState(self):
        print('getState')
        data= {}
        data["method"] = self.get_type()+str('.getStates')
        data["time"] = str(int(time.time())*1000)
        data["token"]= self.get_token()
        data["targetDevice"] =  self.get_id()
        dataTemp = str(json.dumps(data))
        self.yolink_client.publish_data(self.mqttRequestStr, dataTemp)

    '''
    def get_name(self):
        return str(self.device_data['name'])

    def get_type(self):
        return str(self.device_data['type'])

    def get_id(self):
        return str(self.device_data['deviceId'])

    def get_uuid(self):
        return str(self.device_data['deviceUDID'])

    def get_token(self):
        return str(self.device_data['token'])

    def build_device_api_request_data(self):
        """
        Build header + payload to enable sensor API
        """
        self.data["method"] = 'Manage.addYoLinkDevice'
        self.data["time"] = str(int(time.time())*1000)
        #self.data["time"] = str(int(time.time()))
        self.data["params"] = {'sn': self.serial_number}

        self.header['Content-type'] = 'application/json'
        self.header['ktt-ys-brand'] = 'yolink'
        self.header['YS-CSID'] = self.csid

        # MD5(data + csseckey)
        self.header['ys-sec'] = str(hashlib.md5((json.dumps(self.data) +
            self.csseckey).encode('utf-8')).hexdigest())

        print("Header:{0} Data:{1}\n".format(self.header, self.data))

    def enable_device_api(self):
        """
        Send request to enable the device API
        """
        response = requests.post(self.url, data=json.dumps(self.data), headers=self.header)
        #print(response.status_code)

        response = json.loads(response.text)
        print(response)

        self.device_data = response['data']

        if (response['code'] == '000000'):
            print("Successfully enabled device API")
            print("Name:{0} DeviceId:{1}".format(
                self.device_data['name'],
                self.device_data['deviceId']))
        else:
            print("Failed to enable API response!")
            print(response)
            sys.exit()
    '''
   

    def getMethods(self, type):
        '''
        Returs a list of supported methods for the given device type
        '''
        tempList = []
        if type == 'Hub':
            tempList = ['getState', 'setWiFi']
        elif type == 'InfraredRemoter':
            tempList = ['setState', 'learn', 'send', 'setTimeZone', 'setSchedule', 'getSchedule',]
        elif type == 'Outlet':
            tempList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getVersion', 'startUpgrade']
        elif type == 'Switch':
            tempList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getVersion', 'startUpgrade']
        elif type == 'Manipulator':
            tempList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getVersion', 'startUpgrade']            
        elif type == 'Sprinkler':
            tempList = ['getState', 'setState', 'setManualWater', 'getSchedules', 'setSchedules', 'getVersion', 'startUpgrade']
        elif type == 'MultiOutlet':
            tempList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getVerison', 'startUpgrade']
        elif type == 'DoorSensor':
            tempList = ['getState' ]            
        elif type == 'LeakSensor':
            tempList = ['getState']
        elif type == 'MotionSensor':
            tempList = ['getState']         
        elif type == 'THSensor':
            tempList = ['getState' ]
        elif type == 'COSmokeSensor':
            tempList = ['getState' ]       
        elif type == 'Thermostat':
            tempList = ['getState', 'setState', 'getSchedules', 'setSchedules','setTimeZone', 'setECO', 'getVerison', 'startUpgrade']     
        elif type == 'GarageDoor':
            tempList = ['toggle' ]
        elif type == 'CSDevice':
            tempList = ['sendCommand', 'downlink' ]
        else:
            print('Not Supported device type : ' + str(type))
        return(tempList)

    typeList = [ 'Hub','InfraredRemoter', 'Outlet', 'Switch','Manipulator','Sprinkler',  'MultiOutlet'
                ,'DoorSensor','LeakSensor', 'MotionSensor','THSensor', 'COSmokeSensor', 'Thermostat'
                , 'GarageDoor', 'CSDevice'  ]

    def UpData (self, id, type, method):
        print(id, type, method)