# import the necessary modules

# openwns contains the Simulator class, which is needed for every
# simulation
import openwns

# openws.queuingsystem contains the simulation model called
# "SimpleMM1" which is used in this example
import openwns.queuingsystem


### Simulation setup
#
# Q: queue with unlimited size
#
# W: worker, the job processing time is negative-exponentially
#    distributed
#
# The jobs arrive at the system with an inter arrival time that is
# negative-exponentially distributed.
#
#             ----
# new jobs --> Q |-->(W)-->
#             ----
#


# create the M/M/1 simulation model configuration (time in seconds)
mm1 = openwns.queuingsystem.SimpleMM1Step1(meanJobInterArrivalTime = 0.100,
                                           meanJobProcessingTime   = 0.099)

# create simulator configuration
sim = openwns.Simulator(simulationModel = mm1,
                        maxSimTime      = 10.0)

sim.eventSchedulerMonitor = None

# set the configuration for this simulation
openwns.setSimulator(sim)
