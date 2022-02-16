
import time

from threading import Timer

from  datetime import datetime
from dateutil.tz import *

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)


"""
Object for handling Delay - background timer 
"""
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


"""
Object for handling Delay - cbackground countdowm timer 
Requires call back to handle updates
"""
class CountdownTimer(object):
    def __init__ (self, delayTimes,  callback):
        self.delayTimes = delayTimes
        self.updateInterval = 5
        self.callback = callback
        self.timeRemain = delayTimes 
        self.timer = RepeatTimer(self.updateInterval, self.timeUpdate )
        self.timer.start()
        
    def timerReportInterval (self, reportInterval):
        self.updateInterval = reportInterval


    def timeUpdate(self):
        noDelays = True
        for delay in range(0,len(self.timeRemain)):
            if 'delayOn' in self.timeRemain[delay]:
                self.timeRemain[delay]['delayOn'] -= self.updateInterval
                if self.timeRemain[delay]['delayOn'] > 0:
                    noDelays = False
                else:
                    self.timeRemain[delay]['delayOn'] = 0
            if 'on' in self.timeRemain[delay]:
                self.timeRemain[delay]['on'] -= self.updateInterval
                if self.timeRemain[delay]['on'] > 0:
                    noDelays = False
                else:
                    self.timeRemain[delay]['on'] = 0
            if 'delayOff' in self.timeRemain[delay]:
                self.timeRemain[delay]['delayOff'] -= self.updateInterval
                if self.timeRemain[delay]['delayOff'] > 0:
                    noDelays = False
                else:
                    self.timeRemain[delay]['delayOff'] = 0       
            if 'off' in self.timeRemain[delay]:
                self.timeRemain[delay]['off'] -= self.updateInterval
                if self.timeRemain[delay]['off'] > 0:
                    noDelays = False
                else:
                    self.timeRemain[delay]['off'] = 0           
        if noDelays:
            self.timer.cancel()
        self.callback(self.timeRemain)
    
    def stop(self):
        self.timer.cancel()

    def timeRemain(self):
        return(self.timeRemain)



    