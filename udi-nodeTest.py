#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate
import udi_interface
import sys
import time
from yolinkSwitch import YoLinkSW
logging = udi_interface.LOGGER
Custom = udi_interface.Custom
polyglot = None
Parameters = None
n_queue = []
count = 0

'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''

class TestYoLinkNode(udi_interface.Node):
    #def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, devInfo):
    def  __init__(self, polyglot, primary, address, name):
        super(TestYoLinkNode, self).__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('TestYoLinkNode INIT')
        csid = '60dd7fa7960d177187c82039'
        csseckey = '3f68536b695a435d8a1a376fc8254e70'
        csName = 'Panda88'
        devInfo = { "deviceId": "d88b4c0100034906",
                    "deviceUDID": "e091320786e5447099c8b1c93ce47a60",
                    "name": "S Playground Switch",
                    "token": "7f43fbce-dece-4477-9660-97804b278190",
                    "type": "Switch"
                    }
        mqtt_URL= 'api.yosmart.com'
        mqtt_port = 8003
        yolink_URL ='https://api.yosmart.com/openApi'

        
        self.poly = polyglot
        self.count = 0
        self.n_queue = []

        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        #polyglot.subscribe(polyglot.START, self.start, address)
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)

        self.yoSwitch  = YoLinkSW(csName, csid, csseckey, devInfo, self.updateStatus)
        self.yoSwitch.refreshState()
        self.yoSwitch.refreshSchedules()

        #self.yolinkDev = YoLinkSwitch(csName, csid, csseckey, devInfo)
        #YoLinkSwitch.__init__( csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, devInfo, self.updateStatus)
        #super(YoLinkSwitch, self).__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, devInfo, self.updateStatus)

        time.sleep(3)
        #self.switchState = self.yoSwitch.getState()
        #self.switchPower = self.yoSwitch.getEnergy()
        #udi_interface.__init__(self, polyglot, primary, address, name)


    def updateStatus(self, data):
        logging.debug('updateStatus - TestYoLinkNode')
        self.yoSwitch.updateCallbackStatus(data)
        print(data)
        node = polyglot.getNode('my_address')
        if node is not None:
            state =  self.yoSwitch.getState()
            print(state)
            if state.upper() == 'ON':
                node.setDriver('GV0', 1, True, True)
            else:
                node.setDriver('GV0', 0, True, True)
            tmp =  self.yoSwitch.getEnergy()
            print(tmp)
            power = tmp['power']
            watt = tmp['watt']
            print ('power ' + str(power) + ', watt ' +str(watt))
            node.setDriver('GV1', power, True, True)
            node.setDriver('GV2', watt, True, True)
            self.pollDelays()

    def pollDelays(self):
        delays =  self.yoSwitch.getDelays()
        print(delays)
        while True and delays != None:
            delayActve = False
            if 'on' in delays:
                if delays['on'] != 0:
                    delayActve = True
                node.setDriver('GV3', delays['on'], True, True)
            if 'off' in delays:
                if delays['off'] != 0:
                    delayActve = True
                node.setDriver('GV4', delays['off'], True, True)               
            if not delayActve:
                break
            time.sleep(30) # shortPoll???

    

    id = 'test'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 30}, 
            {'driver': 'GV2', 'value': 0, 'uom': 33}, 
            {'driver': 'GV3', 'value': 0, 'uom': 44},
            {'driver': 'GV4', 'value': 0, 'uom': 44},
            ]

    def noop(self):
        logging.info('Discover not implemented')

    commands = {'DISCOVER': noop}

'''
node_queue() and wait_for_node_event() create a simple way to wait
for a node to be created.  The nodeAdd() API call is asynchronous and
will return before the node is fully created. Using this, we can wait
until it is fully created before we try to use it.
'''
def node_queue(data):
    n_queue.append(data['address'])

def wait_for_node_event():
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop()

'''
Read the user entered custom parameters. In this case, it is just
the 'multiplier' value.  Save the parameters in the global 'Parameters'
'''
def parameterHandler(params):
    global Parameters

    Parameters.load(params)


'''
This is where the real work happens.  When we get a shortPoll, increment the
count, report the current count in GV0 and the current count multiplied by
the user defined value in GV1. Then display a notice on the dashboard.
'''
def poll(polltype):
    global count
    global Parameters

    if 'shortPoll' in polltype:
       # self.yolinkDev.refreshDevice()

        # be fancy and display a notice on the polyglot dashboard
        polyglot.Notices['count'] = 'Current count is {}'.format(count)


'''
When we are told to stop, we update the node's status to False.  Since
we don't have a 'controller', we have to do this ourselves.
'''
def stop():
    nodes = polyglot.getNodes()
    for n in nodes:
        nodes[n].setDriver('ST', 0, True, True)
    polyglot.stop()

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)
        #polyglot.subscribe(polyglot.STOP, stop)
        #polyglot.subscribe(polyglot.POLL, poll)

        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()
        polyglot.updateProfile()

        '''
        Here we create the device node.  In a real node server we may
        want to try and discover the device or devices and create nodes
        based on what we find.  Here, we simply create our node and wait
        for the add to complete.
        '''
        csid = '60dd7fa7960d177187c82039'
        csseckey = '3f68536b695a435d8a1a376fc8254e70'
        csName = 'Panda88'
        devInfo = { "deviceId": "d88b4c0100034906",
                    "deviceUDID": "e091320786e5447099c8b1c93ce47a60",
                    "name": "S Playground Switch",
                    "token": "7f43fbce-dece-4477-9660-97804b278190",
                    "type": "Switch"
                    }
        mqtt_URL= 'api.yosmart.com'
        mqtt_port = 8003
        yolink_URL ='https://api.yosmart.com/openApi'


        #node = TestYoLinkNode(polyglot, 'my_address', 'my_address', 'yolinkSwitch', csName , csid, csseckey, devInfo )
        node = TestYoLinkNode(polyglot, 'my_address', 'my_address', 'yolinkSwitch')
        polyglot.addNode(node)
        wait_for_node_event()

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

