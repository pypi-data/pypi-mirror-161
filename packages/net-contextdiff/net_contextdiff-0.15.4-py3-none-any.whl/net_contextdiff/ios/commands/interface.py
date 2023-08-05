# ios.commands.interface
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from deepops import deepsetdefault

from ..utils import interface_canonicalize, expand_set
from ...config import IndentedContextualCommand



# --- configuration command classes ---



class Cmd_Int(IndentedContextualCommand):
    match = r"interface (?P<int_name>\S+)"
    enter_context = "interface"

    def parse(self, cfg, int_name):
        int_name = interface_canonicalize(int_name)

        i = deepsetdefault(cfg, "interface", int_name)

        # IOS has an odd behaviour that, when an interface is created in
        # configure mode, it will default to shutdown or not, depending
        # on its type; in startup configurations, however, they are
        # always not shutdown
        #
        # we default to not shutdown, unless this has been explicitly
        # overridden: this has the effect of 'no shutdown'ing the
        # interface, if it is being created
        i.setdefault("shutdown", False)

        return i


class CmdContext_Int(IndentedContextualCommand):
    context = "interface"


class Cmd_Int_ARPTime(CmdContext_Int):
    match = r"arp timeout (?P<time>\d+)"

    def parse(self, cfg, time):
        cfg["arp-timeout"] = int(time)


class Cmd_Int_CDPEna(CmdContext_Int):
    match = r"(?P<no>no )?cdp enable"

    def parse(self, cfg, no):
        # we allow CDP to be 'no cdp enable' to clear the CDP status
        cfg["cdp-enable"] = not no


class Cmd_Int_ChnGrp(CmdContext_Int):
    match = r"channel-group (?P<id_>\d+)(?P<mode> .+)?"

    def parse(self, cfg, id_, mode):
        cfg["channel-group"] = int(id_), mode


class Cmd_Int_Desc(CmdContext_Int):
    match = r"description (?P<desc>.+)"

    def parse(self, cfg, desc):
        cfg["description"] = desc


class Cmd_Int_Encap(CmdContext_Int):
    match = r"encapsulation (?P<encap>dot1q \d+( native)?)"

    def parse(self, cfg, encap):
        # lower case the encapsulation definition as IOS stores 'dot1q'
        # as 'dot1Q'
        cfg["encapsulation"] = encap.lower()


class Cmd_Int_IPAccGrp(CmdContext_Int):
    match = r"ip access-group (?P<acl_name>\S+) (?P<dir_>in|out)"

    def parse(self, cfg, acl_name, dir_):
        cfg.setdefault("ip-access-group", {})[dir_] = acl_name


# ip address ...


class Cmd_Int_IPAddr(CmdContext_Int):
    match = r"ip address (?P<addr>\S+ \S+)"

    def parse(self, cfg, addr):
        cfg["ip-address"] = addr


class Cmd_Int_IPAddrSec(CmdContext_Int):
    match = r"ip address (?P<addr>\S+ \S+) secondary"

    def parse(self, cfg, addr):
        # secondary address - record it in a list
        cfg.setdefault("ip-address-secondary", set()).add(addr)


# ...


class Cmd_Int_IPFlowMon(CmdContext_Int):
    match = r"ip flow monitor (?P<flowmon>\S+) (?P<dir_>input|output)"

    def parse(self, cfg, flowmon, dir_):
        deepsetdefault(cfg, "ip-flow-monitor")[dir_] = flowmon


class Cmd_Int_IPHlprAddr(CmdContext_Int):
    match = r"ip helper-address (?P<addr>(global )?\S+)"

    def parse(self, cfg, addr):
        cfg.setdefault("ip-helper-address", set()).add(addr)


class Cmd_Int_IPIGMPVer(CmdContext_Int):
    match = r"ip igmp version (?P<ver>\S+)"

    def parse(self, cfg, ver):
        cfg["ip-igmp-version"] = ver


class Cmd_Int_IPMcastBdry(CmdContext_Int):
    match = r"ip multicast boundary (?P<acl>\S+)"

    def parse(self, cfg, acl):
        cfg["ip-multicast-boundary"] = acl


# ip ospf ...


class Cmd_Int_IPOSPFArea(CmdContext_Int):
    match = r"ip ospf (?P<proc>\d+) area (?P<area>[.0-9]+)"

    def parse(self, cfg, proc, area):
        a = deepsetdefault(cfg, "ip-ospf", "area")
        a["process"] = int(proc)
        a["id"]  = area


class Cmd_Int_IPOSPFAuth(CmdContext_Int):
    match = r"ip ospf authentication( (?P<auth>\S+))?"

    def parse(self, cfg, auth):
        cfg.setdefault("ip-ospf", {})["authentication"] = auth


class Cmd_Int_IPOSPFCost(CmdContext_Int):
    match = r"ip ospf cost (?P<cost>\d+)"

    def parse(self, cfg, cost):
        cfg.setdefault("ip-ospf", {})["cost"] = int(cost)


class Cmd_Int_IPOSPFDeadIvl(CmdContext_Int):
    match = r"ip ospf dead-interval (?P<interval>\d+)"

    def parse(self, cfg, interval):
        cfg.setdefault("ip-ospf", {})["dead-interval"] = int(interval)


class Cmd_Int_IPOSPFHelloIvl(CmdContext_Int):
    match = r"ip ospf hello-interval (?P<interval>\d+)"

    def parse(self, cfg, interval):
        cfg.setdefault("ip-ospf", {})["hello-interval"] = int(interval)


class Cmd_Int_IPOSPFMsgDigKey(CmdContext_Int):
    match = r"ip ospf message-digest-key (?P<id_>\d+) md5 (?P<md5>.+)"

    def parse(self, cfg, id_, md5):
        m = deepsetdefault(cfg, "ip-ospf", "message-digest-key")
        m[int(id_)] = md5


class Cmd_Int_IPOSPFNet(CmdContext_Int):
    match = (r"ip ospf network (?P<net>broadcast|non-broadcast|"
             r"point-to-multipoint|point-to-point)")

    def parse(self, cfg, net):
        cfg.setdefault("ip-ospf", {})["network"] = net


# ip pim ...


class Cmd_Int_IPPIMMode(CmdContext_Int):
    match = r"ip pim (?P<mode>(sparse|dense|sparse-dense)-mode)"

    def parse(self, cfg, mode):
        cfg.setdefault("ip-pim", {})["mode"] = mode


class Cmd_Int_IPPIMBSRBdr(CmdContext_Int):
    match = r"ip pim bsr-border"

    def parse(self, cfg):
        cfg.setdefault("ip-pim", {})["bsr-border"] = True


# ...


class Cmd_Int_IPProxyARP(CmdContext_Int):
    match = r"(?P<no>no )?ip proxy-arp"

    def parse(self, cfg, no):
        cfg["ip-proxy-arp"] = not no


class Cmd_Int_IPVerifyUni(CmdContext_Int):
    match = r"ip verify unicast (?P<opt>.+)"

    def parse(self, cfg, opt):
        cfg["ip-verify-unicast"] = opt


class Cmd_Int_IPv6Addr(CmdContext_Int):
    match = r"ipv6 address (?P<addr>\S+)"

    def parse(self, cfg, addr):
        # IPv6 addresses involve letters so we lower case for
        # consistency
        cfg.setdefault("ipv6-address", set()).add(addr.lower())


class Cmd_Int_IPv6MultBdry(CmdContext_Int):
    match = r"ipv6 multicast boundary scope (?P<scope>\S+)"

    def parse(self, cfg, scope):
        cfg["ipv6-multicast-boundary-scope"] = scope


class Cmd_Int_IPv6PIMBSRBdr(CmdContext_Int):
    match = r"ipv6 pim bsr border"

    def parse(self, cfg):
        cfg.setdefault("ipv6-pim", {})["bsr-border"] = True


class Cmd_Int_IPv6TrafFilt(CmdContext_Int):
    match = r"ipv6 traffic-filter (?P<acl_name>\S+) (?P<dir_>in|out)"

    def parse(self, cfg, acl_name, dir_):
        cfg.setdefault("ipv6-traffic-filter", {})[dir_] = acl_name


class Cmd_Int_IPv6VerifyUni(CmdContext_Int):
    match = r"ipv6 verify unicast (?P<opt>.+)"

    def parse(self, cfg, opt):
        cfg["ipv6-verify-unicast"] = opt


# mpls ...


class Cmd_Int_MPLSIP(CmdContext_Int):
    match = r"mpls ip"

    def parse(self, cfg):
        cfg["mpls-ip"] = None


# mtu ...


class Cmd_Int_MTU(CmdContext_Int):
    match = r"mtu (?P<size>\d+)"

    def parse(self, cfg, size):
        cfg["mtu"] = int(size)


# ospfv3 ...


class Cmd_Int_OSPFv3Area(CmdContext_Int):
    match = r"ospfv3 (?P<proc>\d+) (?P<proto>ipv[46]) area (?P<area>[.0-9]+)"

    def parse(self, cfg, proc, proto, area):
        a = deepsetdefault(cfg, "ospfv3", "area", proto)
        a["process"] = int(proc)
        a["id"] = area


class Cmd_Int_OSPFv3Cost(CmdContext_Int):
    match = r"ospfv3 cost (?P<cost>\d+)"

    def parse(self, cfg, cost):
        cfg.setdefault("ospfv3", {})["cost"] = int(cost)


class Cmd_Int_OSPFv3DeadIvl(CmdContext_Int):
    match = r"ospfv3 dead-interval (?P<interval>\d+)"

    def parse(self, cfg, interval):
        cfg.setdefault("ospfv3", {})["dead-interval"] = int(interval)


class Cmd_Int_OSPFv3HelloIvl(CmdContext_Int):
    match = r"ospfv3 hello-interval (?P<interval>\d+)"

    def parse(self, cfg, interval):
        cfg.setdefault("ospfv3", {})["hello-interval"] = int(interval)


class Cmd_Int_OSPFv3Net(CmdContext_Int):
    match = (r"ospfv3 network (?P<net>broadcast|non-broadcast|"
             r"point-to-multipoint|point-to-point)")

    def parse(self, cfg, net):
        cfg.setdefault("ospfv3", {})["network"] = net


# ...


class Cmd_Int_ServPol(CmdContext_Int):
    match = (r"service-policy( type (?P<type_>\S+))? (?P<dir_>input|output)"
             r" (?P<policy>\S+)")

    def parse(self, cfg, type_, dir_, policy):
        deepsetdefault(cfg, "service-policy", dir_)[type_] = policy


class Cmd_Int_Shutdown(CmdContext_Int):
    match = r"(?P<no>no )?shutdown"

    def parse(self, cfg, no):
        cfg["shutdown"] = not no


# standby ...


class Cmd_Int_StandbyIP(CmdContext_Int):
    match = r"standby (?P<grp>\d+) ip (?P<addr>\S+)"

    def parse(self, cfg, grp, addr):
        deepsetdefault(
            cfg, "standby", "group", int(grp))["ip"] = addr


class Cmd_Int_StandbyIPSec(CmdContext_Int):
    match = r"standby (?P<grp>\d+) ip (?P<addr>\S+) secondary"

    def parse(self, cfg, grp, addr):
        deepsetdefault(
            cfg, "standby", "group", int(grp), "ip-secondary",
            last=set()).add(addr)


class Cmd_Int_StandbyIPv6(CmdContext_Int):
    match = r"standby (?P<grp>\d+) ipv6 (?P<addr>\S+)"

    def parse(self, cfg, grp, addr):
        deepsetdefault(
            cfg, "standby", "group", int(grp), "ipv6", last=set()).add(addr)


class Cmd_Int_StandbyPreempt(CmdContext_Int):
    match = r"standby (?P<grp>\d+) preempt"

    def parse(self, cfg, grp):
        deepsetdefault(
            cfg, "standby", "group", int(grp))["preempt"] = True


class Cmd_Int_StandbyPri(CmdContext_Int):
    match = r"standby (?P<grp>\d+) priority (?P<pri>\d+)"

    def parse(self, cfg, grp, pri):
        deepsetdefault(
            cfg, "standby", "group", int(grp))["priority"] = int(pri)


class Cmd_Int_StandbyTimers(CmdContext_Int):
    match = r"standby (?P<grp>\d+) timers (?P<timers>\d+ \d+)"

    def parse(self, cfg, grp, timers):
        deepsetdefault(
            cfg, "standby", "group", int(grp))["timers"] = timers


class Cmd_Int_StandbyTrk(CmdContext_Int):
    match = r"standby (?P<grp>\d+) track (?P<obj>\d+)( (?P<extra>.+))?"

    def parse(self, cfg, grp, obj, extra):
        deepsetdefault(
            cfg, "standby", "group", int(grp), "track")[obj] = extra


class Cmd_Int_StandbyVer(CmdContext_Int):
    match = r"standby version (?P<ver>\d)"

    def parse(self, cfg, ver):
        deepsetdefault(cfg, "standby")["version"] = int(ver)


# ...


class Cmd_Int_StormCtrl(CmdContext_Int):
    match = r"storm-control (?P<traffic>\S+) level (?P<level>[0-9.]+)"

    def parse(self, cfg, traffic, level):
        deepsetdefault(cfg, "storm-control")[traffic] = float(level)


# switchport ...


class Cmd_Int_SwPort(CmdContext_Int):
    match = r"(?P<no>no )?switchport"

    def parse(self, cfg, no):
        cfg["switchport"] = not no


class Cmd_Int_SwPortMode(CmdContext_Int):
    match = r"switchport mode (?P<mode>\S+)"

    def parse(self, cfg, mode):
        cfg["switchport-mode"] = mode


class Cmd_Int_SwPortNoNeg(CmdContext_Int):
    match = r"switchport nonegotiate"

    def parse(self, cfg):
        cfg["switchport-nonegotiate"] = True


class Cmd_Int_SwPortTrkNtv(CmdContext_Int):
    match = r"switchport trunk native vlan (?P<vlan>\d+)"

    def parse(self, cfg, vlan):
        cfg["switchport-trunk-native"] = int(vlan)


class Cmd_Int_SwPortTrkAlw(CmdContext_Int):
    match = (r"switchport trunk allowed vlan "
             r"((?P<complete>(none|all))|(?P<add>add )?(?P<vlans>[0-9,-]+))")

    def parse(self, cfg, complete, add, vlans):
        if complete:
            # 'all' is the same as no configuration present
            if complete == "all":
                if "switchport-trunk-allow" in cfg:
                    cfg.pop("switchport-trunk-allow")

            # 'none' is explicitly no VLANs
            elif complete == "none":
                cfg["switchport-trunk-allow"] = set()

        elif add:
            cfg.setdefault("switchport-trunk-allow", set()).update(
                expand_set(vlans))

        else:
            cfg["switchport-trunk-allow"] = expand_set(vlans)


# ...


class Cmd_Int_VRFFwd(CmdContext_Int):
    match = (r"vrf forwarding (?P<name>\S+)")

    def parse(self, cfg, name):
        cfg["vrf-forwarding"] = name


class Cmd_Int_XConn(CmdContext_Int):
    match = r"xconnect (?P<remote>[0-9.]+ \d+ .+)"

    def parse(self, cfg, remote):
        cfg["xconnect"] = remote
