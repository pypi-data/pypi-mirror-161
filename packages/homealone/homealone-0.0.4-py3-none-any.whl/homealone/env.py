import os
import socket

# directory structure
hostname = socket.gethostname()
rootDir = os.path.expanduser("~")+"/"
confDir = rootDir+"conf/"
keyDir = rootDir+"keys/"
stateDir = rootDir+"state/"
soundDir = rootDir+"sounds/"
dataLogDir = rootDir+"data/"
dataLogFileName = ""

# global variables that must be set here
sysLogging = False
debugEnable = False

# Localization - define these in the config file
latLong = (0.0, 0.0)
elevation = 0 # elevation in feet
tempScale = "F"
localController = "localhost"
