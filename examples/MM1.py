# import the openWNS module. Contains all sub-classes needed for
# configuration of openWNS
import openwns.OpenWNS
import openwns.queuingsystem

# create an instance of the openWNS configuration
# The variable must be called WNS!!!!
WNS = openwns.OpenWNS.OpenWNS()

WNS.simulationModel = openwns.queuingsystem.SimpleMM1(.1, .099)

WNS.maxSimTime = 1000
