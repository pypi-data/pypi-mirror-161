# application template

from .core import *
from .schedule import *
from .rest.restServer import *
from .interfaces.fileInterface import *

class Application(object):
    def __init__(self, name, globals,
                publish=True, port=restServicePort, state=False, metrics=False):
        self.name = name
        self.globals = globals                      # application global variables
        self.publish = publish                      # run REST server if true
        self.port = port                            # REST server port
        self.stateInterface = None                  # Interface resource for state file
        self.metrics = metrics                      # publish metrics if true
        self.event = threading.Event()              # state change event
        self.resources = Collection("resources")    # resources to be published by REST server
        self.schedule = Schedule("schedule")        # schedule of tasks to run
        self.startList = []                         # resources that need to be started
        if state:
            if not os.path.exists(stateDir):
                os.mkdir(stateDir)
            self.stateInterface = FileInterface("fileInterface", fileName=stateDir+self.name+".state")
            self.globals["stateInterface"] = self.stateInterface

    # start the application processes
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

    # define an Interface resource
    def interface(self, interface, event=False, start=False):
        self.globals[interface.name] = interface
        if event:
            interface.event = self.event
        if start:
            self.startList.append(interface)

    # define a Sensor or Control resource
    def control(self, control, event=False, publish=True, start=False):
        self.globals[control.name] = control
        if event:
            control.event = self.event
        if publish:
            self.resources.addRes(control)
        if start:
            self.startList.append(control)

    # define a Task resource
    def task(self, task, event=True, publish=True):
        self.schedule.addTask(task)
        self.globals[task.name] = self.schedule[task.name]
        if event:
            task.event = self.event
        if publish:
            self.resources.addRes(task)

    # apply a UI style to one or more resources
    def style(self, style, resources=[]):
        if resources == []:     # default is all resources
            resources = list(self.resources.values())
        for resource in listize(resources):
            resource.type = style

    # associate one or more resources with one or more UI groups
    def group(self, group, resources=[]):
        if resources == []:     # default is all resources
            resources = list(self.resources.values())
        for resource in listize(resources):
            resource.group = group

    # add a UI label to one or more resources
    def label(self, label=None, resources=[]):
        if resources == []:     # default is all resources
            resources = list(self.resources.values())
        for resource in listize(resources):
            if label:
                resource.label = label
            else:               # create a label from the name
                resource.label = labelize(resource.name)
