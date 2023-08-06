import syslog
import os
import time
import threading
import traceback

from .env import *

# log a message to syslog or stdout
def log(*args):
    message = args[0]+" "   # first argument is the object doing the logging
    for arg in args[1:]:
        message += arg.__str__()+" "
    if sysLogging:
        syslog.syslog(message)
    else:
        print(time.strftime("%b %d %H:%M:%S", time.localtime())+" "+message)

# log the traceback for an exception
def logException(name, ex):
    tracebackLines = traceback.format_exception(None, ex, ex.__traceback__)
    log(name+":")
    for tracebackLine in tracebackLines:
        log(tracebackLine)

# thread object that logs a stack trace if there is an uncaught exception
class LogThread(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runTarget = self.run
        self.run = self.logThread

    def logThread(self):
        try:
            self.runTarget()
        except Exception as ex:
            logException("thread "+threading.currentThread().name, ex)

# convenience function to create and start a thread
def startThread(name, target, **kwargs):
    thread = LogThread(name=name, target=target, **kwargs)
    thread.start()

# log a debug message conditioned on a specified global variable
def debug(*args):
    try:
        if debugEnable:   # global debug flag enables debugging
            if globals()[args[0]]:  # only log if the specified debug variable is True
                log(*args[1:])
    except KeyError:
        pass

# log a stack trace conditioned on a specified global variable
def debugTraceback(debugType, debugName):
    try:
        if debugEnable:   # global debug flag enables debugging
            if globals()[debugType]:
                s = inspect.stack()
                for f in s:
                    log(debugName, f[1], f[2], f[3], f[4])
    except KeyError:
        pass

# wait for the network to be available
def waitForDns():
    wasWaiting = False
    while True:
        try:
            metricsHost = socket.gethostbyname(localController)
            if wasWaiting:
                log("DNS is up")
            return
        except:
            log("Waiting for DNS")
            wasWaiting = True
            time.sleep(1)

# create a human friendly label from a camel case name
def labelize(name):
    label = ""
    for char in name:
        if label:
            if label[-1].islower() and (char.isupper() or char.isnumeric()):
                label += " "
        label += char.lower()
    return label.capitalize()

# get the value of a variable from a file
def getValue(fileName, item):
    return json.load(open(fileName))[item]
