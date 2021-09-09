#!/usr/bin/env python3

import argparse
import os
import sys
import yaml as yaml

#from logger import getLogger
from yolink_devices import YoLinkDevice
from yolink_mqtt_client import YoLinkMQTTClient
#log = getLogger(__name__)

def main(argv):
    '''
    usage = ("{FILE} "
            "--url <API_URL> "
            "--csid <ID> "
            "--csseckey <SECKEY> "
            "--mqtt_url <MQTT_URL> "
            "--mqtt_port <MQTT_PORT> "
            "--topic <MQTT_TOPIC>").format(FILE=__file__)
    '''
    '''
    CSID : 60dd7fa7960d177187c82039
    CSName : Panda88
    CSSecKey : 3f68536b695a435d8a1a376fc8254e70
    SVR_URL : https://api.yosmart.com 
    API Doc : http://www.yosmart.com/doc/lorahomeapi/#/YLAS/
    '''
    yolinkURL =  'https://api.yosmart.com/openApi' 
    mqttURL = 'api.yosmart.com'
    csid = '60dd7fa7960d177187c82039'
    csseckey = '3f68536b695a435d8a1a376fc8254e70'

    topic = 'Panda88/report'
    csName = 'Panda88'

    description = 'Enable Sensor APIs and subscribe to MQTT broker'
    '''
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument("-u", "--url",       help="Device API URL",    required=True)
    parser.add_argument("-i", "--csid",      help="Unique Identifier", required=True)
    parser.add_argument("-k", "--csseckey",  help="Security Key",      required=True)
    parser.add_argument("-m", "--mqtt_url",  help="MQTT Server URL",   required=True)
    parser.add_argument("-p", "--mqtt_port", help="MQTT Server Port",  required=True)
    parser.add_argument("-t", "--topic",     help="Broker Topic",      required=True)
        
    args = parser.parse_args()
    print("{0}\n".format(args))
    '''
    device_hash = {}
    device_serial_numbers = ['9957FD6097124EE99B5E6B61A847C67D', '86788EB527034A78B9EA472323EE2433','34E320948EF746AF98EF8AF6E72F2996', 'AAF5A97CF38B4AD4BE840F293CAA55BE']
    '''
    with open(os.path.abspath('yolink_data.yml'), 'r') as fp:
        data = yaml.safe_load(fp)
        device_serial_numbers = data['DEVICE_SERIAL_NUMBERS']
    '''
    for serial_num in device_serial_numbers:
        yolink_device = YoLinkDevice(yolinkURL, csid, csseckey, serial_num)
        yolink_device.build_device_api_request_data()
        yolink_device.enable_device_api()

        device_hash[yolink_device.get_id()] = yolink_device

    print(device_hash)







    yolink_client = YoLinkMQTTClient(csid, csseckey, topic, mqttURL, 8003, device_hash)
    yolink_client.connect_to_broker()

if __name__ == '__main__':
    main(sys.argv)
