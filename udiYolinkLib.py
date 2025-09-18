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
import json
import math

def updateEpochTime(self, command=None ):
    logging.info('updateEpochTime ')
    #unit = int(command.get('value'))
    self.my_setDriver('TIME', int(time.time()))
    
def convert_temp_unit(self, tempStr):
    if tempStr.capitalize()[:1] == 'F':
        return(1)
    elif tempStr.capitalize()[:1] == 'K':
        return(2)
    else:
        return(0)


def save_cmd_state(self, cmd_state):
    logging.debug('save_cmd_state {} - {}'.format(cmd_state, self.address))
    temp = {}
    temp['cmd_state'] = cmd_state
    try:
        with open(str(self.address)+'.json', 'w') as file:
            json.dump(temp, file)
    except IOError as e:
        logging.error('An error occurred saving command state: {}'.format(e))


def save_cmd_struct(self, cmd_struct):
    logging.debug('save_cmd_struct  {} - {}'.format(cmd_struct, self.address))
    try:
        with open(str(self.address)+'.json', 'w') as file:
            json.dump(cmd_struct, file)
    except IOError as e:
        logging.error('An error occurred saving command state: {}'.format(e))



def retrieve_cmd_state(self):
    logging.debug('retrieve_cmd_state - {}'.format(self.address))
    try:
        with open(str(self.address)+'.json', 'r') as file:
            temp = json.load(file)
            self.cmd_state = temp['cmd_state']
    except FileNotFoundError:
        self.cmd_state = 0
        self.save_cmd_state(self.cmd_state)
    logging.debug('retrieve_cmd_state - state = {}'.format(self.cmd_state))
    return(self.cmd_state)


def retrieve_cmd_struct(self):
    logging.debug('retrieve_cmd_state - {}'.format(self.address))
    try:
        with open(str(self.address)+'.json', 'r') as file:
            temp_struct = json.load(file)
            
    except FileNotFoundError:
        temp_struct = {}
        
    logging.debug('retrieve_cmd_state - state = {}'.format(temp_struct))
    return(temp_struct)


def node_queue(self, data):
    self.n_queue.append(data['address'])

def wait_for_node_done(self):
    while len(self.n_queue) == 0:
        time.sleep(0.1)
    self.n_queue.pop()

def my_setDriver(self, key, value, Unit=None):
    logging.debug(f'my_setDriver : {key} {value} {Unit}')
    try:
        if value is None:
            logging.debug('None value passed = seting 99, UOM 25')
            self.node.setDriver(key, 99, True, True, 25)
        else:
            if Unit:
                self.node.setDriver(key, value, True, True, Unit)
            else:
                self.node.setDriver(key, value, True, True)
    except ValueError: #A non number was passed 
        self.node.setDriver(key, 99, True, True, 25)
        

def mask2key (self, mask):
    logging.debug('mask2key : {}'.format(mask))
    return(int(round(math.log2(mask),0)))
    
def daysToMask (yolink, dayList):
    daysValue = 0 
    i = 0
    for day in yolink.daysOfWeek:
        if day in dayList:
            daysValue = daysValue + pow(2,i)
        i = i+1
    return(daysValue)

def maskToDays(yolink, daysValue):
    daysList = []
    for i in range(0,7):
        mask = pow(2,i)
        if (daysValue & mask) != 0 :
            daysList.append(yolink.daysOfWeek[i])
    return(daysList)

def w_unit2ISY(self, unit):
    if isinstance(unit, int):
        return(unit)
    else:
        return(None)
    

def bool2Nbr (self, data):
    if data is True:
        return(1)
    elif data is False:
        return(0)
    else:
        return(99)

def bool2ISY (self, data):
    if data is True:
        return(1)
    elif data is False:
        return(0)
    else:
        return(99)

def bool2nbr(self, type):
    if type is True:
        return (1)
    elif type is False:
        return(0)
    else:
        return(99)

def state2Nbr(self, val):
    if val == 'normal':
        return(0)
    elif val == 'alert':
        return(1)
    else:
        return(99)

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
    logging.debug('check_name_in_drivers: {}'.format(name))
    found = False
    for drv in enumerate(self.node.drivers):
        logging.debug('check_name_in_drivers: {}'.format(drv))
        if drv['driver'] == name:
            found = True
    return(found)


def update_schedule_data(self, sch_info, selected_schedule):
    logging.info('update_schedule_data {}'.format(sch_info)) 

    def check_name_in_drivers( name):
        found = False
        for indx, drv in enumerate(self.node.drivers):
            if drv['driver'] == name:
                found = True
                return(found)
        return(found)
    if sch_info:
        if 'ch' in sch_info:
            self.my_setDriver('GV12', int(sch_info['ch']))

        self.my_setDriver('GV13', selected_schedule)
        if sch_info['isValid']:
            self.my_setDriver('GV14', 1)
        else:
            self.my_setDriver('GV14', 0)
        timestr = sch_info['on']
        timelist =  timestr.split(':')
        if len(timelist) == 2:
            hour = int(timelist[0])
            minute = int(timelist[1])
            if hour == 25:
                self.my_setDriver('GV15', 98, 25)
                self.my_setDriver('GV16', 98, 25)
            else:
                self.my_setDriver('GV15', int(hour),19)
                self.my_setDriver('GV16', int(minute), 44)
        elif len(timelist) == 3:
            hour = int(timelist[0])
            minute = int(timelist[1])
            second = int(timelist[2])
            if hour == 25:
                self.my_setDriver('GV15', 98, 25)
                self.my_setDriver('GV16', 98, 25)
                self.my_setDriver('GV21', 98, 25)
            else:
                self.my_setDriver('GV15', hour, 19)
                self.my_setDriver('GV16', minute, 44)
                self.my_setDriver('GV21', second, 57)

        timestr = sch_info['off']
        logging.debug('timestr : {}'.format(timestr))
        timelist =  timestr.split(':')
        if len(timelist) == 2:
            hour = int(timelist[0])
            minute = int(timelist[1])
            if hour == 25:
                self.my_setDriver('GV17', 98, 25)
                self.my_setDriver('GV18', 98, 25)
            else:
                self.my_setDriver('GV17', int(hour), 19)
                self.my_setDriver('GV18', int(minute), 44)
        elif len(timelist) == 3:
            hour = int(timelist[0])
            minute = int(timelist[1])
            second = int(timelist[2])     
            if hour == 25:
                self.my_setDriver('GV17', 98, 25)
                self.my_setDriver('GV18', 98, 25)
                self.my_setDriver('GV22', 98, 25)
            else:
                self.my_setDriver('GV17', hour, 19)
                self.my_setDriver('GV18', minute, 44)
                self.my_setDriver('GV22', second, 57)
        self.my_setDriver('GV19',  int(sch_info['week']))

    else:
        logging.debug('No schdule exist for the selected index')
        if check_name_in_drivers('GV12'):
            self.my_setDriver('GV12', 99, 25)
        self.my_setDriver('GV13', selected_schedule) 
        self.my_setDriver('GV14', 99)
        self.my_setDriver('GV15', 99, 25)
        self.my_setDriver('GV16', 99, 25)
        self.my_setDriver('GV17', 99, 25)
        self.my_setDriver('GV18', 99, 25)
        self.my_setDriver('GV19', 0)
        if check_name_in_drivers('GV10'):
            self.my_setDriver('GV10', 99, 25)
            self.my_setDriver('GV11', 99, 25)


def send_rel_temp_to_isy(self, temperature, stateVar):
    logging.debug('convert_temp_to_isy - {}'.format(temperature))
    logging.debug('ISYunit={}, Mess_unit={}'.format(self.ISY_temp_unit , self.messana_temp_unit ))
    if self.ISY_temp_unit == 0: # Celsius in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.my_setDriver(stateVar, round(temperature,1), 4)
        else: # messana = Farenheit
            self.my_setDriver(stateVar, round(temperature*5/9,1), 17)
    elif  self.ISY_temp_unit == 1: # Farenheit in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.my_setDriver(stateVar, round((temperature*9/5),1),  4)
        else:
            self.my_setDriver(stateVar, round(temperature,1), 17)
    else: # kelvin
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.my_setDriver(stateVar, round((temperature,1), 4))
        else:
            self.my_setDriver(stateVar, round((temperature)*9/5,1),  17)


def send_temp_to_isy (self, temperature, stateVar):
    logging.debug('convert_temp_to_isy - {}'.format(temperature))
    logging.debug('ISYunit={}, Mess_unit={}'.format(self.ISY_temp_unit , self.messana_temp_unit ))
    if self.ISY_temp_unit == 0: # Celsius in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.my_setDriver(stateVar, round(temperature,1),  4)
        else: # messana = Farenheit
            self.my_setDriver(stateVar, round((temperature-32)*5/9,1),  17)
    elif  self.ISY_temp_unit == 1: # Farenheit in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.my_setDriver(stateVar, round((temperature*9/5+32),1), 4)
        else:
            self.my_setDriver(stateVar, round(temperature,1),  17)
    else: # kelvin
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            self.my_setDriver(stateVar, round((temperature+273.15,1), 4))
        else:
            self.my_setDriver(stateVar, round((temperature+273.15-32)*9/5,1),  17)
