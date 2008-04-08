# import the necessary modules

# openwns contains the Simulator class, which is needed for every
# simulation
import openwns

# openws.queuingsystem contains the simulation model called
# "SimpleMM1" which is used in this example
import openwns.queuingsystem

import openwns.probebus

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

class StatisticsProbeBus(openwns.probebus.PythonProbeBus):

    def __init__(self, outputFilename):
        openwns.probebus.PythonProbeBus.__init__(self, self.accepts, self.onMeasurement, self.output)
        self.outputFilename = outputFilename
        self.sum = 0.0
        self.trials = 0

    def accepts(self, time, context):
        return True

    def onMeasurement(self, time, measurement, context):
        self.sum += measurement
        self.trials += 1

    def output(self):
        f = open(self.outputFilename, "w")
        f.write("Number of trials: %s\n" % str(self.trials))
        f.write("Mean value : %s\n" % str(self.sum/self.trials))
        f.close()

class FilterProbeBus(openwns.probebus.PythonProbeBus):

    def __init__(self, contextFilterKey, contextFilterValue):
        openwns.probebus.PythonProbeBus.__init__(self, self.accepts)
        self.contextFilterKey = contextFilterKey
        self.contextFilterValue = contextFilterValue
        
    def accepts(self, time, context):
        return context[self.contextFilterKey] == self.contextFilterValue

# create the M/M/1 (step4) simulation model configuration (time in seconds)
# we reuse step3 and only change the configuration!
mm1 = openwns.queuingsystem.SimpleMM1Step6(meanJobInterArrivalTime = 0.100,
                                           meanJobProcessingTime   = 0.099)

# This is our logger
loggingProbeBus = openwns.probebus.LoggingProbeBus()

# ProbeBusses may observe another probe bus. The observing probe bus sees all
# data that the observed probe bus accepts. The observing probe bus may accept
# only a subset of these measurement.
#
# We now use a FilterProbeBus to select only measurements from low priority jobs
#
#                  < ====   Decoupled by   ==== >
#                         ProbeBusRegistry
# +------------------+    +--------------+    +-----------------+    +-------------------+
# |MeasurementSource | -> |MasterProbeBus| -> |FilterProbeBus   | -> |StatisticsProbeBus |
# |                  |    |              |    |accepts jobs with|    |only sees jobs with|
# |                  |    |              |    |priority == 0    |    |priority == 0      |
# +------------------+    +--------------+    +-----------------+    +-------------------+

# accepts only low priority
lowPriorityFilter = FilterProbeBus('priority', 0)
lowPriorityStats  = StatisticsProbeBus("SimpleMM1Step6_lowPriority.output")
# let StatisticsProbeBus observe the FilterProbeBus
lowPriorityStats.observe(lowPriorityFilter)

# Same here but for high priority
highPriorityFilter = FilterProbeBus('priority', 1)
highPriorityStats  = StatisticsProbeBus("SimpleMM1Step6_highPriority.output")
highPriorityStats.observe(highPriorityFilter)

# create simulator configuration
sim = openwns.Simulator(simulationModel = mm1,
                        maxSimTime      = 100.0)

sim.eventSchedulerMonitor = None

sim.environment.probeBusRegistry = openwns.probebus.ProbeBusRegistry(openwns.probebus.MasterProbeBus())

sim.environment.probeBusRegistry.insertProbeBus("openwns.queuingsystem.MM1.sojournTime",
                                                lowPriorityFilter)

sim.environment.probeBusRegistry.insertProbeBus("openwns.queuingsystem.MM1.sojournTime",
                                                highPriorityFilter)

sim.environment.probeBusRegistry.insertProbeBus("openwns.queuingsystem.MM1.sojournTime",
                                                loggingProbeBus)

# The resulting ProbeBusTree looks like this

# Source -> MasterProbeBus +-> FilterProbeBus[priority==0] -> StatisticsProbeBus[filename="SimpleMM1Step6_lowPriority.output"]
#                          |
#                          |-> FilterProbeBus[priority==1] -> StatisticsProbeBus[filename="SimpleMM1Step6_highPriority.output"]
#                          |
#                          +-> LoggingProbeBus

# set the configuration for this simulation
openwns.setSimulator(sim)
