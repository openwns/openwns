# import the openWNS module. Contains all sub-classes needed for
# configuration of openWNS
import openwns.OpenWNS
import openwns.queuingsystem

# create an instance of the openWNS configuration
# The variable must be called WNS!!!!
WNS = openwns.OpenWNS.OpenWNS()

# mean service time (negative exponentially distributed) for one job in [s]
meanServiceTime = 0.099

# mean inter arrival time (negative exponentially distributed) of the jobs in [s]
meanInterArrivalTime = 0.100

# create the M/M/1 simulation model
WNS.simulationModel = openwns.queuingsystem.SimpleMM1(meanInterArrivalTime, meanServiceTime)

# set simtime to 1000 seconds
WNS.maxSimTime = 1000
