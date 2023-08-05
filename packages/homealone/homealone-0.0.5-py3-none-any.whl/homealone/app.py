# application template

from .core import *
from .schedule import *
from .rest.restServer import *
from .interfaces.fileInterface import *

class HomeAlone(object):
    def __init__(self, name, globals,
                publish=True, port=restServicePort, state=False, metrics=False):
        self.name = name
        self.globals = globals
        self.publish = publish
        self.port = port
        self.stateInterface = None
        self.metrics = metrics
        self.event = threading.Event()
        self.resources = Collection("resources")
        self.schedule = Schedule("schedule")
        self.startList = []
        config(self.globals)
        if state:
            if not os.path.exists(stateDir):
                os.mkdir(stateDir)
            self.stateInterface = FileInterface("fileInterface", fileName=stateDir+self.name+".state")
            self.globals["stateInterface"] = self.stateInterface

    def run(self):
        if self.stateInterface:
            self.stateInterface.start()
        for resource in self.startList:
            resource.start()
        if list(self.schedule.keys()) != []:
            self.schedule.start()
        if self.publish:
            self.restServer = RestServer(self.name, self.resources, event=self.event, port=self.port)
            self.restServer.start()

    def interface(self, interface, event=False, start=False):
        self.globals[interface.name] = interface
        if event:
            interface.event = self.event
        if start:
            self.startList.append(interface)

    def control(self, control, event=False, publish=True, start=False):
        self.globals[control.name] = control
        if event:
            control.event = self.event
        if publish:
            self.resources.addRes(control)
        if start:
            self.startList.append(control)

    def task(self, task, event=True, publish=True):
        self.schedule.addTask(task)
        self.globals[task.name] = self.schedule[task.name]
        if event:
            task.event = self.event
        if publish:
            self.resources.addRes(task)

    def style(self, style, resources=[]):
        if resources == []:
            resources = list(self.resources.values())
        for resource in listize(resources):
            resource.type = style

    def group(self, group, resources=[]):
        if resources == []:
            resources = list(self.resources.values())
        for resource in listize(resources):
            resource.group = group

    def label(self, label=None, resources=[]):
        if resources == []:
            resources = list(self.resources.values())
        for resource in resources:
            resource.label = labelize(resource.name)

# Read configuration files and set global variables
def config(globals):
    try:
        for configFileName in os.listdir(confDir):
            try:
                with open(confDir+configFileName) as configFile:
                    configLines = [configLine.rstrip('\n') for configLine in configFile]
                debugConfOpen = True
                for configLine in configLines:
                    if (len(configLine) > 0) and (configLine[0] != "#"):
                        try:
                            (key, value) = configLine.split("=")
                            globals[key.strip()] = eval(value)
                            if globals["debugEnable"] and globals["debugConf"]:   # can't use debugging module because of circular references
                                if debugConfOpen:   # log the file open retroactively if debugConf got set
                                    log("config open", configFileName)
                                    debugConfOpen = False
                                log("config read", configLine)
                        except Exception as ex:
                            log("config", "error evaluating", configLine, str(ex))
            except Exception as ex:
                log("config", "error reading", confDir+configFileName, str(ex))
    except:
        log("config", "no config directory", confDir)
