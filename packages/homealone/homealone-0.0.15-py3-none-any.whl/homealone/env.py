# initialize the global variables that define the environment
import os
import socket
import sys

# network
hostname = socket.gethostname()
localController = "localhost"

# directory structure
rootDir = sys.path[0]+"/"        # directory containing this application
keyDir = rootDir+"keys/"
stateDir = rootDir+"state/"
soundDir = rootDir+"sounds/"
dataDir = rootDir+"data/"

# logging and debugging
sysLogging = True
debugEnable = False

# Localization
latLong = (0.0, 0.0)
elevation = 0 # elevation in feet
tempScale = "F"

# optionally import local variables
try:
    from conf import *
except ImportError:
    pass
