# ios.config
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



"""Cisco IOS configuration module.

This module parses Cisco IOS configuration files into a dictionary.
"""



# --- imports ---



from net_contextdiff.config import IndentedContextualConfig

from .commands import commands
from .utils import ip_acl_std_canonicalize



# --- constants ---



# this dictionary specifies the settings in a portchannel interface
# which will propagate out to the member interfaces
#
# these settings are copied from the portchannel interface to the
# member interfaces, after a configuration is read

INTERFACE_PORTCHANNEL_MEMBER_CFG = [
    "storm-control",
    "switchport",
    "switchport-mode",
    "switchport-nonegotiate",
    "switchport-trunk-native",
    "switchport-trunk-allow",
]



# --- classes ----



class CiscoIOSConfig(IndentedContextualConfig):
    "This concrete class parses Cisco IOS configuration files."


    def _add_commands(self):
        """This method is called by the constructor to add commands for
        the IOS platform.

        The commands are stored in a global (to the module) level list
        of classes.
        """

        for cmd_class in commands:
            self._add_command(cmd_class)


    def _post_parse_file(self):
        """Extend the inherited method to flush any pending IPv4
        standard ACL rules into the configuration.
        """

        super()._post_parse_file()


        # go through the pending IPv4 standard ACLs and store them (we
        # convert this to a list as _acl4_std_flush() will change the
        # dictionary during iteration and we only need the names)

        if "ip-access-list-standard" in self:
            ip_acl_std = self["ip-access-list-standard"]
            for name in ip_acl_std:
                ip_acl_std[name] = ip_acl_std_canonicalize(ip_acl_std[name])


        # go through the interfaces and copy settings from the
        # portchannel interface, if that interface is a member of one

        for int_name in self.get("interface", {}):
            # get the dictionary for this interface

            int_ = self["interface"][int_name]


            # if this interface is a portchannel member ...

            if "channel-group" in int_:
                id_ = int_["channel-group"][0]


                # get the corresponding portchannel interface this is a
                # member of

                po_int = self["interface"].get("Po%d" % id_, {})


                # copy the settings which propagate to the members into
                # this interface

                for setting in INTERFACE_PORTCHANNEL_MEMBER_CFG:
                    if setting in po_int:
                        int_[setting] = po_int[setting]
