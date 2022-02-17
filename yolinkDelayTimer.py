
import time

from threading import Timer, Lock

from  datetime import datetime
from typing import List
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
    def __init__ (self,  ):
        self.delayTimes = []
        self.updateInterval = 5
        self.timeRemain = []
        self.timer = RepeatTimer(self.updateInterval, self.timeUpdate )
        #self.timer.start()
        self.timerRunning = False
        self.lock = Lock()
        
    def add(self, delayTimes, callback):
        self.callback = callback
        if not self.timerRunning:
            self.timer.start()
            self.timerRunning = True
        self.lock.acquire()
        for delay in range(0,len(delayTimes)):
# should overwrite 

            self.timeRemain.append(delayTimes[delay])
        self.lock.release()

    def timerReportInterval (self, reportInterval):
        self.updateInterval = reportInterval


    def timeUpdate(self):
        noDelays = True
        self.lock.acquire()
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
            self.timerRunning = False
        self.callback(self.timeRemain)
        self.lock.release()
    
    def stop(self):
        self.timer.cancel()

    def timeRemain(self):
        return(self.timeRemain)



    