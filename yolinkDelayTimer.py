
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
    def __init__ (self, startTime, updateInterval, callback):
        self.startTime = startTime
        self.updateInterval = updateInterval
        self.callback = callback
        self.timeRemain = startTime 
        self.timer = RepeatTimer(self.updateInterval, self.TimeUpdate )
        self.timer.start()
        

    def TimeUpdate(self):
        self.timeRemain = self.timeRemain - self.updateInterval
        if self.timeRemain <= 0:
            self.timer.cancel()
            self.timeRemain = 0
        self.callback(self.timeRemain)
    
    def stop(self):
        self.timer.cancel()

    def TimeRemain(self):
        return(self.timeRemain)



    