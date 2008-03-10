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

class StatisticsProbeBus(openwns.probebus.ProbeBus):

    nameInFactory = "PythonProbeBus"

    def __init__(self, outputFilename):
        openwns.probebus.ProbeBus.__init__(self,"")
        self.reportErrors = True
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

# create the M/M/1 (step4) simulation model configuration (time in seconds)
# we reuse step3 and only change the configuration!
mm1 = openwns.queuingsystem.SimpleMM1Step3(meanJobInterArrivalTime = 0.100,
                                           meanJobProcessingTime   = 0.099)

# Replace the default LoggingProbeBus configured in SimpleMM1Step3 by
# our StatisticsProbeBus
statisticsProbeBus = StatisticsProbeBus("SimpleMM1Step5.output")
loggingProbeBus = openwns.probebus.LoggingProbeBus()

# create simulator configuration
sim = openwns.Simulator(simulationModel = mm1,
                        maxSimTime      = 1000.0)

sim.eventSchedulerMonitor = None

sim.environment.probeBusRegistry.insertProbeBus("openwns.queuingsystem.MM1.sojournTime",
                                                statisticsProbeBus)
sim.environment.probeBusRegistry.insertProbeBus("openwns.queuingsystem.MM1.sojournTime",
                                                loggingProbeBus)

sim.environment.probeBusRegistry = openwns.probebus.ProbeBusRegistry(openwns.probebus.MasterProbeBus())
# set the configuration for this simulation
openwns.setSimulator(sim)
