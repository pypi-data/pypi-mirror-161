# ios.converters.interface
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from ..utils import is_int_physical

from ...diff import DiffConvert



# --- converter classes ---



class Cvt_Int(DiffConvert):
    cmd = "interface", None

    def remove(self, old, int_name):
         # if the interface is physical, we can't delete it ...
        if is_int_physical(int_name):
            # ... but, if there was something in the old configuration
            # other than just it being shut down, we 'default' it
            if old.keys() != { "shutdown" }:
                return "default interface " + int_name

            # the only thing in the old configuration was that it was
            # shutdown, so we ignore this
            return

        return "no interface " + int_name

    def add(self, new, int_name):
        return "interface " + int_name


class DiffConvert_Int(DiffConvert):
    context = Cvt_Int.cmd

    def enter(self, int_name):
        return "interface " + int_name,


# we put the 'interface / shutdown' at the start to shut it down before
# we do any [re]configuration

class Cvt_Int_Shutdown(DiffConvert_Int):
    cmd = "shutdown",
    block = "int-shutdown"

    def update(self, old, upd, new, int_name):
        # we only 'shutdown' if we are disabling the port ('no shutdown'
        # happens at the end of interface configuration)
        if new:
            return [*self.enter(int_name), " shutdown"]


# we do VRF changes on an interface before we do any IP configuration,
# otherwise it will be removed

class Cvt_Int_VRFFwd(DiffConvert_Int):
    cmd = "vrf-forwarding",
    block = "int-vrf"
    trigger_blocks = { "int-addr" }

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no vrf forwarding"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " vrf forwarding " + new]


class Cvt_Int_ARPTime(DiffConvert_Int):
    cmd = "arp-timeout",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no arp timeout"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " arp timeout " + str(new)]


class Cvt_Int_CDPEna(DiffConvert_Int):
    cmd = "cdp-enable",

    def remove(self, old, int_name):
        # if the 'cdp enable' option is not present, that doesn't mean
        # it's disabled but just that it's not specified, so we assume
        # the default is for it to be enabled
        return [*self.enter(int_name), " cdp enable"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name),
                " " + ("" if upd else "no ") + "cdp enable"]


class Cvt_Int_ChnGrp(DiffConvert_Int):
    cmd = "channel-group",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no channel-group"]

    def update(self, old, upd, new, int_name):
        id_, mode = new
        return [*self.enter(int_name),
                " channel-group %d%s" % (id_, mode if mode else "")]


class Cvt_Int_Desc(DiffConvert_Int):
    cmd = "description",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no description"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " description " + new]


class Cvt_Int_Encap(DiffConvert_Int):
    cmd = "encapsulation",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no encapsulation " + old]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " encapsulation " + new]


class Cvt_Int_IPAccGrp(DiffConvert_Int):
    cmd = "ip-access-group", None

    def remove(self, old, int_name, dir_):
        return [*self.enter(int_name), " no ip access-group " + dir_]

    def update(self, old, upd, new, int_name, dir_):
        return [*self.enter(int_name), " ip access-group %s %s" % (new, dir_)]


# ip-address ...


class Cvt_Int_IPAddr(DiffConvert_Int):
    cmd = "ip-address",
    block = "int-addr"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip address"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip address " + new]


class Cvt_Int_IPAddrSec(DiffConvert_Int):
    cmd = "ip-address-secondary", None
    block = "int-addr"

    def remove(self, old, int_name, addr):
        return [*self.enter(int_name), " no ip address %s secondary" % addr]

    def update(self, old, upd, new, int_name, addr):
        return [*self.enter(int_name), " ip address %s secondary" % addr]


# ...


class Cvt_Int_IPFlowMon(DiffConvert_Int):
    cmd = "ip-flow-monitor", None

    def remove(self, old, int_name, dir_):
        return [*self.enter(int_name),
                " no ip flow monitor %s %s" % (old, dir_)]

    def update(self, old, upd, new, int_name, dir_):
        l = [*self.enter(int_name)]

        # we must remove the old flow monitor before setting a new one
        if old:
            l += [" no ip flow monitor %s %s" % (old, dir_)]

        l += [" ip flow monitor %s %s" % (new, dir_)]
        return l


class Cvt_Int_IPHlprAddr(DiffConvert_Int):
    cmd = "ip-helper-address", None

    def remove(self, old, int_name, addr):
        return [*self.enter(int_name), " no ip helper-address " + addr]

    def update(self, old, upd, new, int_name, addr):
        return [*self.enter(int_name), " ip helper-address " + addr]


class Cvt_Int_IPIGMPVer(DiffConvert_Int):
    cmd = "ip-igmp-version",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip igmp version"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip igmp version " + new]


class Cvt_Int_IPMcastBdry(DiffConvert_Int):
    cmd = "ip-multicast-boundary",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip multicast boundary"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip multicast boundary " + new]


# ip-ospf ...


class Cvt_Int_IPOSPFArea(DiffConvert_Int):
    cmd = "ip-ospf", "area"

    def remove(self, old, int_name):
        return [*self.enter(int_name),
                " no ip ospf %d area %s" % (old["process"], old["id"])]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name),
                " ip ospf %d area %s" % (new["process"], new["id"])]


class Cvt_Int_IPOSPFAuth(DiffConvert_Int):
    cmd = "ip-ospf", "authentication"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf authentication"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf authentication " + new]


class Cvt_Int_IPOSPFCost(DiffConvert_Int):
    cmd = "ip-ospf", "cost"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf cost"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf cost " + str(new)]


class Cvt_Int_IPOSPFDeadIvl(DiffConvert_Int):
    cmd = "ip-ospf", "dead-interval"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf dead-interval"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf dead-interval " + str(new)]


class Cvt_Int_IPOSPFHelloIvl(DiffConvert_Int):
    cmd = "ip-ospf", "hello-interval"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf hello-interval"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf hello-interval " + str(new)]


class Cvt_Int_IPOSPFMsgDigKey(DiffConvert_Int):
    cmd = "ip-ospf", "message-digest-key", None

    def remove(self, old, int_name, id_):
        return [*self.enter(int_name),
                " no ip ospf message-digest-key " + str(id_)]

    def update(self, old, upd, new, int_name, id_):
        return [*self.enter(int_name),
                " ip ospf message-digest-key %d md5 %s" % (id_, new)]


class Cvt_Int_IPOSPFNet(DiffConvert_Int):
    cmd = "ip-ospf", "network"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf network"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf network " + new]


# ip-pim ...


class Cvt_Int_IPPIMMode(DiffConvert_Int):
    cmd = "ip-pim", "mode"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip pim " + old]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip pim " + new]


class Cvt_Int_IPPIMBSRBdr(DiffConvert_Int):
    cmd = "ip-pim", "bsr-border"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip pim bsr-border"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip pim bsr-border"]


# ...


class Cvt_Int_IPProxyARP(DiffConvert_Int):
    cmd = "ip-proxy-arp",

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name),
                " " + ("" if upd else "no ") + "ip proxy-arp"]


class Cvt_Int_IPVerifyUni(DiffConvert_Int):
    cmd = "ip-verify-unicast",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip verify unicast"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip verify unicast " + new]


class Cvt_Int_IPv6Addr(DiffConvert_Int):
    cmd = "ipv6-address", None

    def remove(self, old, int_name, addr):
        return [*self.enter(int_name), " no ipv6 address " + addr]

    def update(self, old, upd, new, int_name, addr):
        return [*self.enter(int_name), " ipv6 address " + addr]


class Cvt_Int_IPv6MultBdry(DiffConvert_Int):
    cmd = "ipv6-multicast-boundary-scope",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ipv6 multicast boundary scope"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ipv6 multicast boundary scope " + new]


# mpls ...


class Cvt_Int_MPLSIP(DiffConvert_Int):
    cmd = "mpls-ip",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no mpls ip "]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " mpls ip "]


# mtu ...


class Cvt_Int_MTU(DiffConvert_Int):
    cmd = tuple()
    ext = "mtu",

    def remove(self, old, int_name):
        # if interface is in a port-channel, the MTU is set in the
        # port-channel interface
        if "channel-group" in old:
            return None

        return [*self.enter(int_name), " no mtu"]

    def update(self, old, upd, new, int_name):
        if old and "channel-group" in old:
            return None

        return [*self.enter(int_name), " mtu " + str(self.get_ext(new))]


# ospfv3 ...


class Cvt_Int_OSPFv3Area(DiffConvert_Int):
    cmd = "ospfv3", "area", None

    def remove(self, old, int_name, proto):
        return [*self.enter(int_name),
                " no ospfv3 %d %s area %s"
                    % (old["process"], proto, old["id"])]

    def update(self, old, upd, new, int_name, proto):
        return [*self.enter(int_name),
                " ospfv3 %d %s area %s" % (new["process"], proto, new["id"])]


class Cvt_Int_OSPFv3Cost(DiffConvert_Int):
    cmd = "ospfv3", "cost"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ospfv3 cost"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ospfv3 cost " + str(new)]


class Cvt_Int_OSPFv3DeadIvl(DiffConvert_Int):
    cmd = "ospfv3", "dead-interval"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ospfv3 dead-interval"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ospfv3 dead-interval " + str(new)]


class Cvt_Int_OSPFv3HelloIvl(DiffConvert_Int):
    cmd = "ospfv3", "hello-interval"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ospfv3 hello-interval"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ospfv3 hello-interval " + str(new)]


class Cvt_Int_OSPFv3Net(DiffConvert_Int):
    cmd = "ospfv3", "network"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ospfv3 network"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ospfv3 network " + new]


# ...


class Cvt_Int_IPv6PIMBSRBdr(DiffConvert_Int):
    cmd = "ipv6-pim", "bsr-border"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ipv6 pim bsr border"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ipv6 pim bsr border"]


class Cvt_Int_IPv6TrafFilt(DiffConvert_Int):
    cmd = "ipv6-traffic-filter", None

    def remove(self, old, int_name, dir_):
        return [*self.enter(int_name), " no ipv6 traffic-filter " + dir_]

    def update(self, old, upd, new, int_name, dir_):
        return [*self.enter(int_name),
               " ipv6 traffic-filter %s %s" % (new, dir_)]


class Cvt_Int_IPv6VerifyUni(DiffConvert_Int):
    cmd = "ipv6-verify-unicast",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ipv6 verify unicast"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ipv6 verify unicast " + new]


class Cvt_Int_ServPol(DiffConvert_Int):
    cmd = "service-policy", None, None

    def type_str(self, type_):
        # we only specify the 'type' if one is set (the default is a
        # policer)
        return (" type " + type_) if type_ else ""

    def remove(self, old, int_name, dir_, type_):
        return [*self.enter(int_name),
                " no service-policy%s %s %s"
                    % (self.type_str(type_), dir_, old)]

    def update(self, old, upd, new, int_name, dir_, type_):
        l = [*self.enter(int_name)]

        # we cannot just replace a service-policy: we need to remove the
        # old one first
        if old:
            l.append(" no service-policy%s %s %s"
                         % (self.type_str(type_), dir_, old))

        l.append(" service-policy%s %s %s"
                     % (self.type_str(type_), dir_, new))

        return l


# standby ...


class Cvt_Int_StandbyIP(DiffConvert_Int):
    cmd = "standby", "group", None, "ip"
    block = "int-addr"

    def remove(self, old, int_name, grp):
        return [*self.enter(int_name), " no standby %d ip" % grp]

    def update(self, old, upd, new, int_name, grp):
        return [*self.enter(int_name), " standby %d ip %s" % (grp, new)]


class Cvt_Int_StandbyIPSec(DiffConvert_Int):
    cmd = "standby", "group", None, "ip-secondary", None
    block = "int-addr"

    def remove(self, old, int_name, grp, addr):
        return [*self.enter(int_name),
                " no standby %d ip %s secondary" % (grp, addr)]

    def update(self, old, upd, new, int_name, grp, addr):
        return [*self.enter(int_name),
                " standby %d ip %s secondary" % (grp, addr)]


class Cvt_Int_StandbyIPv6(DiffConvert_Int):
    cmd = "standby", "group", None, "ipv6", None
    block = "int-addr"

    def remove(self, old, int_name, grp, addr):
        return [*self.enter(int_name),
                " no standby %d ipv6 %s" % (grp, addr)]

    def update(self, old, upd, new, int_name, grp, addr):
        return [*self.enter(int_name),
                " standby %d ipv6 %s" % (grp, addr)]


class Cvt_Int_StandbyPreempt(DiffConvert_Int):
    cmd = "standby", "group", None, "preempt"

    def remove(self, old, int_name, grp):
        return [*self.enter(int_name), " no standby %d preempt" % grp]

    def update(self, old, upd, new, int_name, grp):
        return [*self.enter(int_name), " standby %d preempt" % grp]


class Cvt_Int_StandbyPri(DiffConvert_Int):
    cmd = "standby", "group", None, "priority"

    def remove(self, old, int_name, grp):
        return [*self.enter(int_name), " no standby %d priority" % grp]

    def update(self, old, upd, new, int_name, grp):
        return [*self.enter(int_name), " standby %d priority %d" % (grp, new)]


class Cvt_Int_StandbyTimers(DiffConvert_Int):
    cmd = "standby", "group", None, "timers"

    def remove(self, old, int_name, grp):
        return [*self.enter(int_name), " no standby %d timers" % grp]

    def update(self, old, upd, new, int_name, grp):
        return [*self.enter(int_name), " standby %d timers %s" % (grp, new)]


class Cvt_Int_StandbyTrk(DiffConvert_Int):
    cmd = "standby", "group", None, "track", None

    def remove(self, old, int_name, grp, obj):
        return [*self.enter(int_name), " no standby %d track %s" % (grp, obj)]

    def update(self, old, upd, new, int_name, grp, obj):
        return [*self.enter(int_name),
                " standby %d track %s%s"
                    % (grp, obj, (" " + new) if new else "")]


class Cvt_Int_StandbyVer(DiffConvert_Int):
    cmd = "standby", "version"
    block = "int-pre"

    def update(self, old, upd, new, int_name):
        # only set this here if we're switching to version >= 2 (so we
        # can potentially use any high-numbered groups)
        if new < 2:
            return
        return [*self.enter(int_name), " standby version " + str(new)]


class Cvt_Int_NoStandbyVer(DiffConvert_Int):
    cmd = "standby", "version"
    block = "int-post"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no standby version"]

    def update(self, old, upd, new, int_name):
        # only set this here if we're switching to version < 2 (so we
        # need to do it after removing all the high-numbered groups)
        if new >= 2:
            return
        return [*self.enter(int_name), " standby version " + str(new)]


# ...


class Cvt_Int_StormCtrl(DiffConvert_Int):
    cmd = "storm-control", None

    def remove(self, old, int_name, traffic):
        return [*self.enter(int_name),
                " no storm-control %s level" % traffic]

    def update(self, old, upd, new, int_name, traffic):
        return [*self.enter(int_name),
                " storm-control %s level %.2f" % (traffic, new)]


# switchport ...


class Cvt_Int_SwPort(DiffConvert_Int):
    cmd = "switchport",

    def remove(self, old, int_name):
        # if the 'switchport' option is not present, that doesn't mean
        # it's disabled but just that it's not specified, so we assume
        # the default is for it to be disabled
        #
        # TODO: this is the case for routers (which we're concerned
        # about here) but not switches: we'd probably need a separate
        # platform for this
        return [*self.enter(int_name), " no switchport"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name),
                " " + ("" if upd else "no ") + "switchport"]


class Cvt_Int_SwPortMode(DiffConvert_Int):
    cmd = "switchport-mode",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no switchport mode"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " switchport mode " + new]


class Cvt_Int_SwPortNoNeg(DiffConvert_Int):
    cmd = "switchport-nonegotiate",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no switchport nonegotiate"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " switchport nonegotiate"]


class Cvt_Int_SwPortTrkNtv(DiffConvert_Int):
    # we just match the interface as we need to look inside it to see if
    # the interface is part of a channel group
    cmd = tuple()
    ext = "switchport-trunk-native",

    def remove(self, old, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in old:
            return None

        return [*self.enter(int_name), " no switchport trunk native vlan"]

    def update(self, old, upd, new, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in new:
            return None

        return [*self.enter(int_name),
                " switchport trunk native vlan " + str(self.get_ext(new))]


class Cvt_Int_SwPortTrkAlw(DiffConvert_Int):
    # we just match the interface as we need to look inside it to see if
    # the interface is part of a channel group
    cmd = tuple()
    ext = "switchport-trunk-allow",

    def remove(self, old, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in old:
            return None

        # we're removing all commands allowing VLANs which is a special
        # case as this actually means 'allow all'
        return [*self.enter(int_name), " no switchport trunk allowed vlan"]

    def truncate(self, old, rem, new, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in old:
            return None

        l = [*self.enter(int_name)]
        for tag in sorted(self.get_ext(rem)):
            l.append(" switchport trunk allowed vlan remove " + str(tag))
        return l

    def update(self, old, upd, new, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in new:
            return None

        l = [*self.enter(int_name)]

        # if this list was not there before, all VLANs were allowed by
        # default so we need to reset the list to 'none' and then add
        # the ones which are specifically listed
        if not old:
            l.append(" switchport trunk allowed vlan none")

        for tag in sorted(self.get_ext(upd)):
            l.append(" switchport trunk allowed vlan add " + str(tag))

        return l


# ...


class Cvt_Int_XConn(DiffConvert_Int):
    cmd = "xconnect",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no xconnect"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " xconnect " + new]


# we put the 'interface / no shutdown' at the end to only enable the
# interface once it's been correctly [re]configured

class Cvt_Int_NoShutdown(DiffConvert_Int):
    cmd = "shutdown",
    block = "int-noshutdown"

    def update(self, old, upd, new, int_name):
        # we only 'no shutdown' if we are enabling the port ('shutdown'
        # happens at the start of interface configuration)
        if not new:
            return [*self.enter(int_name), " no shutdown"]
