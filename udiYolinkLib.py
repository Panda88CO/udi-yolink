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
    

def bool2ISY (self, data):
    if data:
        return(1)
    else:
        return(0)


def isy_value(self, value):
    if value == None:
        return (99)
    else:
        return(value)
    
def daylist2bin(self, daylist):
    sum = 0
    if 'sun' in daylist:
        sum = sum + 1
    if 'mon' in daylist:
        sum = sum + 2       
    if 'tue' in daylist:
        sum = sum + 4
    if 'wed' in daylist:
        sum = sum + 8
    if 'thu' in daylist:
        sum = sum + 16
    if 'fri' in daylist:
        sum = sum + 32
    if 'sat' in daylist:
        sum = sum + 64
    return(sum)

def prep_schedule(self, query):
    logging.debug('prep_schedule {} '.format(query))
    params = {}
    onH = 25
    onM = 0     
    onS = 0
    offH = 25
    offM = 0   
    offS = 0
    include_sec = False
    #query = command.get("query")
    if 'port.uom25' in query:
        port = int(query.get('port.uom25'))-1
        params['ch'] = port
    schedule_selected = int(query.get('index.uom25'))
    tmp = int(query.get('active.uom25'))
    activated = (tmp == 1)
    if 'onH.uom19' in query:
        onH = int(query.get('onH.uom19'))
    if 'onM.uom44' in query:    
        onM = int(query.get('onM.uom44'))
    if 'offH.uom19' in query:
        offH = int(query.get('offH.uom19'))
    if 'offM.uom44' in query:    
        offM = int(query.get('offM.uom44'))  
    if 'onS.' in query:
        include_sec = True
        if 'onS.uom57' in query:            
            onS = int(query.get('onS.uom57'))
        else:
            onS = 0
    if 'offS.' in query:            
        include_sec = True  
        if 'offS.uom57' in query:            
            offS = int(query.get('onS.uom57'))
        else:
            offS = 0
          
    binDays = int(query.get('bindays.uom25'))

    
    params['index'] = str(schedule_selected )
    params['isValid'] = activated 
    params['on'] = str(onH)+':'+str(onM)
    params['off'] = str(offH)+':'+str(offM)
    if include_sec:
        params['on'] = params['on'] + ':' + str(onS)
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

def check_name_in_drivers(self,  name):
    found = False
    for drv in enumerate(self.node.drivers):
        if drv['driver'] == name:
            found = True
    return(found)


def update_schedule_data(self, sch_info):
    logging.info('update_schedule_data {}'.format(sch_info)) 
    #logging.debug('drivers: {} - {}'.format(self.drivers, self.node.drivers)) 

    if sch_info:
        if 'ch' in sch_info:
            self.node.setDriver('GV12', int(sch_info['ch']))

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
        if self.check_name_in_drivers('GV12'):
            self.node.setDriver('GV12', 99, True, True, 25)
        self.node.setDriver('GV13', 99)
        self.node.setDriver('GV14', 99)
        self.node.setDriver('GV15', 99,True, True, 25)
        self.node.setDriver('GV16', 99,True, True, 25)
        self.node.setDriver('GV17', 99,True, True, 25)
        self.node.setDriver('GV18', 99,True, True, 25)
        self.node.setDriver('GV19', 0)
        if self.check_name_in_drivers('GV10'):
            self.node.setDriver('GV10', 99, True, True, 25)
            self.node.setDriver('GV11', 99, True, True, 25)


def send_rel_temp_to_isy(self, temperature, stateVar):
    logging.debug('convert_temp_to_isy - {}'.format(temperature))
    logging.debug('ISYunit={}, Mess_unit={}'.format(self.ISY_temp_unit , self.messana_temp_unit ))
    if self.ISY_temp_unit == 0: # Celsius in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.node.setDriver(stateVar, round(temperature,1), True, True, 4)
        else: # messana = Farenheit
            self.node.setDriver(stateVar, round(temperature*5/9,1), True, True, 17)
    elif  self.ISY_temp_unit == 1: # Farenheit in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.node.setDriver(stateVar, round((temperature*9/5),1), True, True, 4)
        else:
            self.node.setDriver(stateVar, round(temperature,1), True, True, 17)
    else: # kelvin
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.node.setDriver(stateVar, round((temperature,1), True, True, 4))
        else:
            self.node.setDriver(stateVar, round((temperature)*9/5,1), True, True, 17)


def send_temp_to_isy (self, temperature, stateVar):
    logging.debug('convert_temp_to_isy - {}'.format(temperature))
    logging.debug('ISYunit={}, Mess_unit={}'.format(self.ISY_temp_unit , self.messana_temp_unit ))
    if self.ISY_temp_unit == 0: # Celsius in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.node.setDriver(stateVar, round(temperature,1), True, True, 4)
        else: # messana = Farenheit
            self.node.setDriver(stateVar, round((temperature-32)*5/9,1), True, True, 17)
    elif  self.ISY_temp_unit == 1: # Farenheit in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.node.setDriver(stateVar, round((temperature*9/5+32),1), True, True, 4)
        else:
            self.node.setDriver(stateVar, round(temperature,1), True, True, 17)
    else: # kelvin
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.node.setDriver(stateVar, round((temperature+273.15,1), True, True, 4))
        else:
            self.node.setDriver(stateVar, round((temperature+273.15-32)*9/5,1), True, True, 17)
