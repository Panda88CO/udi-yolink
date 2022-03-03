
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
    def __init__ (self):
        self.delayTimes = []
        self.updateInterval = 5
        self.timeRemain = []
        self.timerRunning = False
        self.lock = Lock()
        self.callback = None
        self.timer = RepeatTimer(self.updateInterval, self.timeUpdate )

    def timerCallback (self,  callback, updateInterval = 5):
        self.callback = callback
        self.updateInterval = updateInterval
        #self.timer = RepeatTimer(self.updateInterval, self.timeUpdate )

    def addDelays(self, delayTimes):
        self.lock.acquire()
        if not self.timerRunning:
            self.timer.start()
            self.timerRunning = True
   
        for indx in range(0,len(delayTimes)):
            alreadyExists = False
            ch = delayTimes[indx]['ch']
            for delayIndx in range(0,len(self.timeRemain)):
                if ch == self.timeRemain[delayIndx]['ch']:
                    alreadyExists = True
                    if 'on' in delayTimes[indx]:
                        self.timeRemain[delayIndx]['on'] = int(delayTimes[indx]['on']*60)
                    if 'off' in delayTimes[indx]:
                        self.timeRemain[delayIndx]['off'] = int(delayTimes[indx]['off']*60)
                    if 'delayOn' in delayTimes[indx]:
                        self.timeRemain[delayIndx]['on'] = int(delayTimes[indx]['delayOn']*60)
                    if 'delayOff' in delayTimes[indx]:
                        self.timeRemain[delayIndx]['off'] = int(delayTimes[indx]['delayOff']*60)
            if not alreadyExists:
                self.timeRemain.append(delayTimes[indx])
        self.lock.release()

   

    def timerReportInterval (self, reportInterval):
        self.lock.acquire()
        if self.timerRunning:
            self.timer.cancel()
        self.timer = RepeatTimer(reportInterval, self.timeUpdate )
        self.timer.start()
        self.timerRunning = True
        self.lock.release() 
        
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
        if self.callback:
            self.callback(self.timeRemain)
        self.lock.release()
    
    def stop(self):
        self.timer.cancel()

    def timeRemaining(self):
        return(self.timeRemain)



    