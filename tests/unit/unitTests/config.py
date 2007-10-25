# import the WNS module. Contains all sub-classes needed for
# configuration of WNS
import wns.WNS

# create an instance of the WNS configuration
# The variable must be called WNS!!!!
WNS = wns.WNS.WNS()

WNS.outputStrategy = wns.WNS.OutputStrategy.DELETE
WNS.masterLogger.enabled = False
# set this to zero in the tests to avoid starting the PeriodicRealTimeout
# 1) if gui is enabled a PeriodicRealTimeout will be started
# 2) this will queue a command
# 3) the command will be deleted during tests (due to resetting the EventScheduler)
# 4) in RISE::shutdown() the PeriodicRealTimeout wants to remove the Command (which has already been removed)
# 5) assure in PeriodicRealTimeout will fire ...

