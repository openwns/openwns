# This defines the recipients for the Bazaar post push hook. It is
# expected to be found in the ./config directory within the branch
# that you push
#
# Each entry in the recipients list is a pair of regular expression
# and space separated email address string. The regular expression
# is matched against the location that you push to. If it matches than
# emails are sent to the recipients.

recipients = [(".*@bazaar.launchpad.net/~comnets.*",
               "develop@openwns.org"),
	      (".*bazaar.comnets.rwth-aachen.de/openWNS.'",
               "software@comnets.rwth-aachen.de")]
