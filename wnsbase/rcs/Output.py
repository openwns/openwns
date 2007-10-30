###############################################################################
# This file is part of openWNS (open Wireless Network Simulator)
# _____________________________________________________________________________
#
# Copyright (C) 2004-2007
# Chair of Communication Networks (ComNets)
# Kopernikusstr. 16, D-52074 Aachen, Germany
# phone: ++49-241-80-27910,
# fax: ++49-241-80-22242
# email: info@openwns.org
# www: http://www.openwns.org
# _____________________________________________________________________________
#
# openWNS is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 2 as published by the
# Free Software Foundation;
#
# openWNS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

class Output:
	def __init__(self, sout, serr):
		self.sout = sout
		self.serr = serr
		self.hasError = False

	def __str__(self):
		s = ""
		error = ""
		for it in self.serr:
			error += it
		if error != "":
			raise("An error during TLA action occured:\n\n" + error )
		for i in self.sout:
			s += i
		return s.strip("\n")

	def __iter__(self):
		for s in self.sout, self.serr:
			line = s.readline()
			while line:
				if s == self.serr:
					self.hasError = True
				yield line.strip('\n')
				line = s.readline()

	def realtimePrint(self, prepend=""):
		for it in self:
			print prepend + it
		if self.hasError:
			raise("An error during TLA action occured!")
