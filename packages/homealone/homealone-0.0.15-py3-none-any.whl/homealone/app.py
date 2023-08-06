# application template

from .core import *
from .schedule import *
from .rest.restServer import *
from .rest.restProxy import *
from .interfaces.fileInterface import *

class Application(object):
    def __init__(self, name, globals,
                publish=True, port=restServicePort,
                state=False, metrics=False,
                proxy=False, watch=[], ignore=[]):
        self.name = name
        self.globals = globals                      # application global variables
        self.publish = publish                      # run REST server if true
        self.port = port                            # REST server port
        self.state = state
        self.stateInterface = None                  # Interface resource for state file
        self.metrics = metrics                      # publish metrics if true
        self.event = threading.Event()              # state change event
        self.resources = Collection("resources", event=self.event)    # resources to be published by REST server
        self.schedule = Schedule("schedule")        # schedule of tasks to run
        self.startList = []                         # resources that need to be started
        self.proxy = proxy
        self.restProxy = None
        self.proxyResources = None

        if state:
            if not os.path.exists(stateDir):
                os.mkdir(stateDir)
            self.stateInterface = FileInterface("stateInterface", fileName=stateDir+self.name+".state")
            self.stateInterface.start()
            self.globals["stateInterface"] = self.stateInterface
        if proxy:
            self.proxyResources = Collection("proxyResources", event=self.event)
            self.restProxy = RestProxy("restProxy", self.proxyResources, watch=watch, ignore=ignore, event=self.event)

    # start the application processes
    def run(self):
        if self.proxy:
            self.restProxy.start()
        for resource in self.startList:
            resource.start()
        if list(self.schedule.keys()) != []:
            self.schedule.start()
        if self.publish:
            self.restServer = RestServer(self.name, self.resources, port=self.port, event=self.event, label=self.name)
            self.restServer.start()

    # define an Interface resource
    def interface(self, interface, event=False, start=False):
        self.globals[interface.name] = interface
        if event:
            interface.event = self.event
        if start:
            self.startList.append(interface)

    # define a Sensor or Control resource
    def resource(self, resource, id=None, event=False, publish=True, start=False):
        if not id:
            id = camelize(resource.name)
        self.globals[id] = resource
        if event:
            resource.event = self.event
        if publish:
            self.resources.addRes(resource)
        if start:
            self.startList.append(resource)

    # define a Sensor or Control resource that is proxied from another server
    def proxyResource(self, resource, id=None):
        if not id:
            id = camelize(resource.name)
        self.globals[id] = resource
        resource.resources = self.proxyResources

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
