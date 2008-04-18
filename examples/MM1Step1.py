# import the necessary modules
# begin example "wns.queuingsystem.mm1step1.py.example"

# openwns contains the Simulator class, which is needed for every
# simulation
import openwns
# ^ this import reads the file __init__.py in
#   ./sandbox/*/lib/PyConfig/openwns/__init__.py
# There the class definition for Simulator is set,
# which is a class OpenWNS defined in simulator.py

# openws.queuingsystem contains the simulation model called
# "SimpleMM1" which is used in this example
import openwns.queuingsystem
# ^ this import reads the file in
#   ./sandbox/*/lib/PyConfig/openwns/queuingsystem.py
# which has been copied into the sandbox by "./playground install" from
#   ${OPENWNSBASE}/framework/library/PyConfig/openwns/queuingsystem.py
#   ${COMNETSWNSBASE}/framework/libwns--main--1.0/PyConfig/openwns/queuingsystem.py
# It is interesting and good for your learning of openwns
# to have a look into that file and understand Python classes
# and constructors (__init__)

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
# ^ here a Python object is created and stored in the "mm1" variable
# The class definition is in queuingsystem.py (see location above)
# By this syntax the constructor (__init__) is called with two parameters.
# The constructor sets the parameters into member variables

# create simulator configuration
sim = openwns.Simulator(simulationModel = mm1,
                        maxSimTime      = 10.0)
# ^ This object is created from a class Simulator defined in
# ./framework/library/PyConfig/openwns/__init__.py

sim.eventSchedulerMonitor = None

# set the configuration for this simulation
openwns.setSimulator(sim)
# ^ function defined in
# ./framework/library/PyConfig/openwns/simulator.py

# after reading all this, the Python interpreter,
# which is embedded inside the compiled openwns core,
# has all variables in memory.
# The contents are now available in "PyConfig Views"
# The simulation core then starts to setup the C++ class objects
# and hands over a PyConfig subview to each object,
# each specific for this particular object.
