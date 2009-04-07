import wns.WNS
import wns.EventScheduler
import wns.Node
import wns.Distribution
import wns.evaluation.default

import constanze.Constanze
import constanze.Node
import constanze.evaluation.default

import ip.Component

import ip
from ip.VirtualARP import VirtualARPServer
from ip.VirtualDHCP import VirtualDHCPServer
from ip.VirtualDNS import VirtualDNSServer
import ip
import ip.evaluation.default

import glue.support.Configuration
import glue.evaluation.csma
import copper.Copper

# create an instance of the WNS configuration
# The variable must be called WNS!!!!
WNS = wns.WNS.WNS()
WNS.outputStrategy = wns.WNS.OutputStrategy.DELETE

WNS.maxSimTime = 10.0

# must be < 250 (otherwise IPAddress out of range)
numberOfStations = 2

wire = copper.Copper.Wire("theWire")

# 11 MBit/s
speed = 54E6
meanPacketSize = 1500 * 8
loadFactor = 0.7
throughputPerStation = speed * loadFactor / numberOfStations

class Station(wns.Node.Node):
    phy = None
    dll = None
    nl = None
    load = None

    def __init__(self, wire, ber, speed, id):
        super(Station, self).__init__("node"+str(id))
        # create Components in a Node
        self.phy = copper.Copper.Transceiver(self, "phy", wire, ber, speed)
        self.dll = glue.support.Configuration.CSMACAComponent(self, "ShortCut", self.phy.dataTransmission, self.phy.notification, self.phy.dataTransmissionFeedback)
        domainName = "node" + str(id) + ".glue.wns.org"
        self.nl = ip.Component.IPv4Component(self, domainName + ".ip",domainName)
        self.nl.addDLL(_name = "glue",
                       # Where to get my IP Address
                       _addressResolver = ip.AddressResolver.VirtualDHCPResolver("theOnlySubnet"),
                       # ARP zone
                       _arpZone = "theOnlySubnet",
                       # We can deliver locally
                       _pointToPoint = False,
                       # DLL service names
                       _dllDataTransmission = self.dll.unicastDataTransmission,
                       _dllNotification = self.dll.unicastNotification)

        self.load = constanze.Node.ConstanzeComponent(self, "constanze")

# Create Nodes and components
for i in xrange(numberOfStations):
    station = Station(wire, wns.Distribution.Fixed(1E-5), speed, i)
    WNS.nodes.append(station)


for i in xrange(numberOfStations):
    cbr = constanze.Constanze.CBR(0.01, throughputPerStation, meanPacketSize)
    ipBinding = constanze.Node.IPBinding(WNS.nodes[i-1].nl.domainName, WNS.nodes[i].nl.domainName)
    WNS.nodes[i-1].load.addTraffic(ipBinding, cbr)
    ipListenerBinding = constanze.Node.IPListenerBinding(WNS.nodes[i-1].nl.domainName)
    listener = constanze.Node.Listener(WNS.nodes[i-1].nl.domainName + ".listener")
    WNS.nodes[i-1].load.addListener(ipListenerBinding, listener)

# one Virtual ARP Zone
varp = VirtualARPServer("vARP", "theOnlySubnet")
WNS.nodes = [varp] + WNS.nodes

vdhcp = VirtualDHCPServer("vDHCP@",
                          "theOnlySubnet",
                          "192.168.0.2", "192.168.254.253",
                          "255.255.0.0")

vdns = VirtualDNSServer("vDNS", "ip.DEFAULT.GLOBAL")
WNS.nodes.append(vdns)

WNS.nodes.append(vdhcp)

glue.evaluation.csma.installEvaluation(WNS, range(1, numberOfStations + 1))

ip.evaluation.default.installEvaluation(sim = WNS,
                                        maxPacketDelay = 0.5,     # s
                                        maxPacketSize = 2000*8,   # Bit
                                        maxBitThroughput = 10E6,  # Bit/s
                                        maxPacketThroughput = 1E6 # Packets/s
                                        )

constanze.evaluation.default.installEvaluation(sim = WNS,
                                               maxPacketDelay = 1.0,
                                               maxPacketSize = 16000,
                                               maxBitThroughput = 100e6,
                                               maxPacketThroughput = 10e6,
                                               delayResolution = 1000,
                                               sizeResolution = 2000,
                                               throughputResolution = 10000)

wns.evaluation.default.installEvaluation(sim = WNS)
