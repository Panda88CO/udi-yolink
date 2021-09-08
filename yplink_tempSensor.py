from sys import unraisablehook
import time
import json
import requests
#import sys

class yoLinkTempSensor (object):
    def __init__ (self, targetDevice, token):
        self.url = url
        self.csid = csid
        self.csseckey = csseckey
        self.serial_number = serial_number

        self.targetDevice = targetDevice
        self.token - token

        self.data = {}
        self.header = {}

        self.device_data = {}

    def getData(self):
        self.data["method"] = 'THSensor.getState'
        self.data["time"] = str(int(time.time())*1000)
        #self.data["params"] = {'sn': self.serial_number}
        self.data["targetDevice"] = self.targetDevice
        self.data["token"]= self.token

        self.header['Content-type'] = 'application/json'
        self.header['ktt-ys-brand'] = 'yolink'
        self.header['YS-CSID'] = self.csid

        # MD5(data + csseckey)
        self.header['ys-sec'] = str(hashlib.md5((json.dumps(self.data) +
            self.csseckey).encode('utf-8')).hexdigest())

        print("Header:{0} Data:{1}\n".format(self.header, self.data))
