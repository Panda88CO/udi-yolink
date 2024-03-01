#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

from os import truncate
#import udi_interface
#import sys
import time
import math

def node_queue(self, data):
    self.n_queue.append(data['address'])

def wait_for_node_done(self):
    while len(self.n_queue) == 0:
        time.sleep(0.1)
    self.n_queue.pop()

def mask2key (self, mask):
    logging.debug('mask2key : {}'.format(mask))
    return(int(round(math.log2(mask),0)))
    

def prep_schedule(self, query):
    onH = 25
    onM = 0     
    onS = 0
    offH = 25
    offM = None    
    offS = None    
    #query = command.get("query")
    schedule_selected = int(query.get('index.uom25'))
    tmp = int(query.get('active.uom25'))
    activated = (tmp == 1)
    if 'onH.uom19' in query:
        onH = int(query.get('onH.uom19'))
        onM = int(query.get('onM.uom44'))
    if 'stopH.uom19' in query:
        offH = int(query.get('offH.uom19'))
        offM = int(query.get('offM.uom44'))  
    if 'onS.uom57' in query:
        onS = int(query.get('onS.uom57'))
    if 'offS.uom57' in query:
        offS = int(query.get('onS.uom57'))
            
    binDays = int(query.get('bindays.uom25'))

    params = {}
    params['index'] = str(schedule_selected )
    params['isValid'] = activated 
    params['on'] = str(onH)+':'+str(onM)
    if onS:
        params['on'] = params['on'] + ':' + str(onS)
    params['off'] = str(offH)+':'+str(offM)

    if offS:
            params['off'] =  params['off'] + ':' + str(offS)

    params['week'] = binDays
    #self.yolink.setSchedule(self.schedule_selected, params)
    return(schedule_selected, params)

def activate_schedule(self, query):
    logging.info('activate_schedule {}'.format(query))       
    #query = command.get("query")
    schedule_selected = int(query.get('index.uom25'))
    tmp = int(query.get('active.uom25'))
    activated = (tmp == 1)
    #self.yolink.activateSchedule(schedule_selected, activated)
    return(activated, schedule_selected)

def update_schedule_data(self, sch_info):
    logging.info('update_schedule_data {}'.format(sch_info))    
    if sch_info:
        self.node.setDriver('GV13', int(sch_info['index']))
        if sch_info['isValid']:
            self.node.setDriver('GV14', 1)
        else:
            self.node.setDriver('GV14', 0)
        timestr = sch_info['on']
        timelist =  timestr.split(':')
        if len(timelist) == 2:
            hour = int(timelist[0])
            minute = int(timelist[1])
            if hour == 25:
                self.node.setDriver('GV15', 98,True, True, 25)
                self.node.setDriver('GV16', 98,True, True, 25)
            else:
                self.node.setDriver('GV15', int(hour),True, True, 19)
                self.node.setDriver('GV16', int(minute),True, True, 44)
        elif len(timelist) == 3:
            hour = int(timelist[0])
            minute = int(timelist[1])
            second = int(timelist[2])            
            if hour == 25:
                self.node.setDriver('GV15', 98,True, True, 25)
                self.node.setDriver('GV16', 98,True, True, 25)
                self.node.setDriver('GV10', 98,True, True, 25)
            else:
                self.node.setDriver('GV15', hour,True, True, 19)
                self.node.setDriver('GV16', minute,True, True, 44)
                self.node.setDriver('GV10', second,True, True, 57)

        timestr = sch_info['off']
        logging.debug('timestr : {}'.format(timestr))
        timelist =  timestr.split(':')
        if len(timelist) == 2:
            hour = int(timelist[0])
            minute = int(timelist[1])
            if hour == 25:
                self.node.setDriver('GV17', 98,True, True, 25)
                self.node.setDriver('GV18', 98,True, True, 25)
            else:
                self.node.setDriver('GV17', int(hour),True, True, 19)
                self.node.setDriver('GV18', int(minute),True, True, 44)
        elif len(timelist) == 3:
            hour = int(timelist[0])
            minute = int(timelist[1])
            second = int(timelist[2])            
            if hour == 25:
                self.node.setDriver('GV17', 98,True, True, 25)
                self.node.setDriver('GV18', 98,True, True, 25)
                self.node.setDriver('GV11', 98,True, True, 25)
            else:
                self.node.setDriver('GV17', hour,True, True, 19)
                self.node.setDriver('GV18', minute,True, True, 44)
                self.node.setDriver('GV11', second,True, True, 57)
        self.node.setDriver('GV19',  int(sch_info['week']))

    else:
        self.node.setDriver('GV13', 99)
        self.node.setDriver('GV14', 99)
        self.node.setDriver('GV15', 99,True, True, 25)
        self.node.setDriver('GV16', 99,True, True, 25)
        self.node.setDriver('GV17', 99,True, True, 25)
        self.node.setDriver('GV18', 99,True, True, 25)
        self.node.setDriver('GV19', 0)    
        if 'GV10' in self.drivers:
            self.node.setDriver('GV10', True, True, 25)
            self.node.setDriver('GV11', True, True, 25)
