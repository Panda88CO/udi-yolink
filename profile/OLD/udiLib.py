#!/usr/bin/env python3
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')
import time
import re


def node_queue(self, data):
    self.n_queue.append(data['address'])

def wait_for_node_done(self):
    while len(self.n_queue) == 0:
        time.sleep(0.1)
    self.n_queue.pop()

def bool2ISY (self, data):
    if data:
        return(1)
    else:
        return(0)

def getValidName(self, name):
    name = bytes(name, 'utf-8').decode('utf-8','ignore')
    return re.sub(r"[^A-Za-z0-9_ ]", "", name)

# remove all illegal characters from node address
def getValidAddress(self, name):
    name = bytes(name, 'utf-8').decode('utf-8','ignore')
    return re.sub(r"[^A-Za-z0-9_]", "", name.lower()[:14])

def isy_value(self, value):
    if value == None:
        return (99)
    else:
        return(value)

def handleLevelChange(self, level):
    logging.info('New log level: {}'.format(level))
    logging.setLevel(level['level'])



def handleParams (self, userParam ):
    logging.debug('handleParams')
    self.Parameters.load(userParam)
    self.poly.Notices.clear()


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

def convert_temp_unit(self, tempStr):
    if tempStr.capitalize()[:1] == 'F':
        return(1)
    elif tempStr.capitalize()[:1] == 'K':
        return(2)
    else:
        return(0)
