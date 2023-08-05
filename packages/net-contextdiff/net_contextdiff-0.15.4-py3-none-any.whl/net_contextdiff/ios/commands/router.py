# ios.commands.router
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from deepops import deepsetdefault
import netaddr

from ..utils import interface_canonicalize
from ...config import IndentedContextualCommand



# --- functions ---



def neighbor_canonicalize(nbr):
    """Canonicalise a BGP neighbor identifier - these can be descriptive
    names (for a peer-group) or an IP address.  In the case of IPv6, we
    need to ensure the case is consistent, so we upper case it.

    If the name is not an IPv6 address, we return it as-is.
    """

    if netaddr.valid_ipv6(nbr):
        return str(netaddr.IPAddress(nbr, 6)).upper()

    return nbr



# --- configuration command classes ---



# IP[V6] ROUTE ...



class Cmd_IPRoute(IndentedContextualCommand):
    match = (r"ip route( vrf (?P<vrf>\S+))? (?P<base>\S+) (?P<netmask>\S+)"
             r"( (?P<int_name>[-A-Za-z]+\d+))?( (?P<router>\S+))?"
             r"( (?P<metric1>\d+))?( tag (?P<tag>\d+))?( (?P<metric2>\d+))?")

    def parse(self, cfg, vrf, base, netmask, int_name, router, metric1, tag,
              metric2):
        # get a canonical form of the destination network and interface name
        net = str(netaddr.IPNetwork(base + "/" + netmask))
        int_name = interface_canonicalize(int_name) if int_name else None

        # build a unique hashable indentifier for the next hop of this
        # route (i.e. interface and router address, if available)
        #
        # the actual contents are not important (although can be used in
        # a rule) but are needed to determine which routes are being
        # added, removed and changed (in terms of metric, tag, etc.) by
        # comparing the identifiers
        id = (int_name or "-") + " " + (router or "-")

        r = { "interface": int_name, "router": router }
        if metric1 or metric2:
            r["metric"] = int(metric1 or metric2)
        if tag:
            r["tag"] = tag

        deepsetdefault(cfg, "ip-route", vrf, net)[id] = r


class Cmd_IPv6Route(IndentedContextualCommand):
    match = (r"ipv6 route( vrf (?P<vrf>\S+))? (?P<net>\S+)"
             r"( (?P<int_name>[-A-Za-z]+\d+))?( (?P<router>\S+))?"
             r"( (?P<metric1>\d+))?( tag (?P<tag>\d+))?( (?P<metric2>\d+))?")

    def parse(self, cfg, vrf, net, int_name, router, metric1, tag, metric2):
        net = str(netaddr.IPNetwork(net))
        router = str(netaddr.IPAddress(router)) if router else None
        int_name = interface_canonicalize(int_name) if int_name else None

        id = (int_name or "-") + " " + (router or "-")

        r = { "interface": int_name, "router": router }
        if metric1 or metric2:
            r["metric"] = int(metric1 or metric2)
        if tag:
            r["tag"] = int(tag)


        deepsetdefault(cfg, "ipv6-route", vrf, net)[id] = r



# ROUTER BGP ...



class Cmd_RtrBGP(IndentedContextualCommand):
    # ASNs can be in 'n' as well as 'n.n' format so we can't just use an
    # integer
    match = r"router bgp (?P<asn>\d+(\.\d+)?)"
    enter_context = "router-bgp"

    def parse(self, cfg, asn):
        return deepsetdefault(cfg, "router", "bgp", asn)


class CmdContext_RtrBGP(IndentedContextualCommand):
    context = "router-bgp"


class CmdContext_RtrBGP_NbrFallOver(CmdContext_RtrBGP):
    match = (r"neighbor (?P<nbr>\S+) fall-over"
             r" (bfd (?P<bfd>single-hop|multi-hop)|route-map (?P<rtmap>\S+))")

    def parse(self, cfg, nbr, bfd, rtmap):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))["fall-over"] = (
                { "bfd": bfd } if bfd else { "route-map": rtmap } )


class CmdContext_RtrBGP_NbrPwd(CmdContext_RtrBGP):
    match = r"neighbor (?P<nbr>\S+) password( (?P<enc>\d)) (?P<pwd>\S+)"

    def parse(self, cfg, nbr, enc, pwd):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))["password"] = {
                "encryption": int(enc), "password": pwd
            }


class CmdContext_RtrBGP_NbrPrGrp(CmdContext_RtrBGP):
    match = r"neighbor (?P<nbr>\S+) peer-group"

    def parse(self, cfg, nbr):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))["type"] = "peer-group"


class CmdContext_RtrBGP_NbrPrGrpMbr(CmdContext_RtrBGP):
    match = r"neighbor (?P<nbr>\S+) peer-group (?P<grp>\S+)"

    def parse(self, cfg, nbr, grp):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))["peer-group"] = grp


class CmdContext_RtrBGP_NbrRemAS(CmdContext_RtrBGP):
    match = r"neighbor (?P<nbr>\S+) remote-as (?P<rem_as>\d+(\.\d+)?)"

    def parse(self, cfg, nbr, rem_as):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))["remote-as"] = rem_as


class CmdContext_RtrBGP_NbrUpdSrc(CmdContext_RtrBGP):
    match = r"neighbor (?P<nbr>\S+) update-source (?P<int_name>\S+)"

    def parse(self, cfg, nbr, int_name):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))["update-source"] = (
                int_name)


# router bgp ... address-family ... [vrf ...]


class Cmd_RtrBGP_AF(CmdContext_RtrBGP):
    match = (r"address-family (?P<af>ipv[46]( (?P<cast>unicast|multicast))?|"
             r"vpnv4|vpnv6)( vrf (?P<vrf>\S+))?")

    enter_context = "router-bgp-af"

    def parse(self, cfg, af, cast, vrf):
        # unicast/multicast is optional - if omitted, we assume unicast
        if not cast:
            af += " unicast"

        # we put addres families in the global routing table in a VRF
        # called '_default'
        return deepsetdefault(
                   cfg, "vrf", vrf or "_default", "address-family", af)


class CmdContext_RtrBGP_AF(IndentedContextualCommand):
    context = "router-bgp-af"


class CmdContext_RtrBGP_AF_NbtAct(CmdContext_RtrBGP_AF):
    match = r"neighbor (?P<nbr>\S+) activate"

    def parse(self, cfg, nbr):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))["activate"] = None


class CmdContext_RtrBGP_AF_NbrAddPath(CmdContext_RtrBGP_AF):
    match = (r"neighbor (?P<nbr>\S+) additional-paths"
             r"(( (?P<snd>send))?( (?P<rcv>receive))?|( (?P<dis>disable)))")

    def parse(self, cfg, nbr, snd, rcv, dis):
        # additional paths is a set of all matching types (or 'disable')
        s = deepsetdefault(cfg, "neighbor", neighbor_canonicalize(nbr))[
            "additional-paths"] = { a for a in (snd, rcv, dis) if a }


class CmdContext_RtrBGP_AF_NbrAdvAddPath(CmdContext_RtrBGP_AF):
    match = (r"neighbor (?P<nbr>\S+) advertise additional-paths"
             r"( (?P<all>all))?"
             r"( (?P<best>best( (?P<best_n>\d+))))?"
             r"( (?P<grp_best>group-best))?")

    def parse(self, cfg, nbr, all, best, best_n, grp_best):
        a = deepsetdefault(cfg, "neighbor", neighbor_canonicalize(nbr),
                           "advertise-additional-paths")

        if all:
            a["all"] = True
        if best:
            a["best"] = best_n
        if grp_best:
            a["group-best"] = True


class CmdContext_RtrBGP_AF_NbrFltLst(CmdContext_RtrBGP_AF):
    match = (r"neighbor (?P<nbr>\S+) filter-list (?P<list_>\d+)"
             r" (?P<dir_>in|out)")

    def parse(self, cfg, nbr, list_, dir_):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr), "filter-list")[
                dir_] = int(list_)


class CmdContext_RtrBGP_AF_NbrMaxPfx(CmdContext_RtrBGP_AF):
    match = (r"neighbor (?P<nbr>\S+) maximum-prefix (?P<max>\d+)"
             r"( (?P<thresh>\d+))?")

    def parse(self, cfg, nbr, max, thresh):
        m = deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr), "maximum-prefix")
        m["max"] = int(max)
        if thresh:
            m["threshold"] = int(thresh)


class CmdContext_RtrBGP_AF_NbrNHSelf(CmdContext_RtrBGP_AF):
    match = r"neighbor (?P<nbr>\S+) next-hop-self"

    def parse(self, cfg, nbr):
        deepsetdefault(cfg, "neighbor", nbr)["next-hop-self"] = True


class CmdContext_RtrBGP_AF_NbrPrGrp(CmdContext_RtrBGP_AF):
    match = r"neighbor (?P<nbr>\S+) peer-group"

    def parse(self, cfg, nbr):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))["type"] = "peer-group"


class CmdContext_RtrBGP_AF_NbrPrGrpMbr(CmdContext_RtrBGP_AF):
    match = r"neighbor (?P<nbr>\S+) peer-group (?P<grp>\S+)"

    def parse(self, cfg, nbr, grp):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))["peer-group"] = grp


class CmdContext_RtrBGP_AF_NbrPfxLst(CmdContext_RtrBGP_AF):
    match = (r"neighbor (?P<nbr>\S+) prefix-list (?P<list_>\S+)"
             r" (?P<dir_>in|out)")

    def parse(self, cfg, nbr, list_, dir_):
        deepsetdefault(cfg, "neighbor", nbr, "prefix-list")[dir_] = list_


class CmdContext_RtrBGP_AF_NbrRtMap(CmdContext_RtrBGP_AF):
    match = r"neighbor (?P<nbr>\S+) route-map (?P<rtmap>\S+) (?P<dir_>in|out)"

    def parse(self, cfg, nbr, rtmap, dir_):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr), "route-map")[dir_] = (
                rtmap)


class CmdContext_RtrBGP_AF_NbrSndCmty(CmdContext_RtrBGP_AF):
    match = (r"neighbor (?P<nbr>\S+) send-community"
             r"( (?P<cmty>standard|extended|both))?")

    def parse(self, cfg, nbr, cmty):
        # this command adjusts the current state of the setting rather
        # than replacing it (e.g. entering "extended" when only
        # "standard" is set will change to "both")
        #
        # we don't worry about that but track each setting independently
        c = deepsetdefault(cfg, "neighbor", neighbor_canonicalize(nbr),
                           "send-community", last=set())
        if cmty in (None, "standard", "both"):
            c.add("standard")
        if cmty in ("extended", "both"):
            c.add("extended")


class CmdContext_RtrBGP_AF_NbrSoftRecfg(CmdContext_RtrBGP_AF):
    match = r"neighbor (?P<nbr>\S+) soft-reconfiguration inbound"

    def parse(self, cfg, nbr):
        deepsetdefault(
            cfg, "neighbor", neighbor_canonicalize(nbr))[
                "soft-reconfiguration"] = "inbound"


class CmdContext_RtrBGP_AF_Redist(CmdContext_RtrBGP_AF):
    match = (r"redistribute (?P<proto>static|connected|ospf \d+|ospfv3 \d+)"
             r"( route-map (?P<rtmap>\S+))?( metric (?P<met>\d+))?")

    def parse(self, cfg, proto, rtmap, met):
        r = deepsetdefault(cfg, "redistribute", proto)
        if rtmap:
            r["route-map"] = rtmap
        if met:
            r["metric"] = int(met)



# ROUTER OSPF ...



class Cmd_RtrOSPF(IndentedContextualCommand):
    match = r"router ospf (?P<proc>\d+)"
    enter_context = "router-ospf"

    def parse(self, cfg, proc):
        return deepsetdefault(cfg, "router", "ospf", int(proc))


class CmdContext_RtrOSPF(IndentedContextualCommand):
    context = "router-ospf"


class Cmd_RtrOSPF_Id(CmdContext_RtrOSPF):
    match = r"router-id (?P<id_>[.0-9]+)"

    def parse(self, cfg, id_):
        cfg["id"] = id_


class Cmd_RtrOSPF_AreaNSSA(CmdContext_RtrOSPF):
    match = (r"area (?P<area>\S[.0-9]+)"
             r" nssa(?P<no_redist> no-redistribution)?"
             r"(?P<no_summ> no-summary)?")

    def parse(self, cfg, area, no_redist, no_summ):
        a = set()
        if no_redist: a.add("no-redistribution")
        if no_summ: a.add("no-summary")
        deepsetdefault(cfg, "area", area)["nssa"] = a


class Cmd_RtrOSPF_PasvInt(CmdContext_RtrOSPF):
    match = r"(?P<no>no )?passive-interface (?P<int_name>\S+)"

    def parse(self, cfg, no, int_name):
        p = deepsetdefault(cfg, "passive-interface")
        if int_name == "default":
            if not no:
                p["default"] = True
        else:
            deepsetdefault(
                p, "interface")[interface_canonicalize(int_name)] = not no



# ROUTER OSPFV3 ...



class Cmd_RtrOSPFv3(IndentedContextualCommand):
    match = r"router ospfv3 (?P<proc>\d+)"
    enter_context = "router-ospfv3"

    def parse(self, cfg, proc):
        return deepsetdefault(cfg, "router", "ospfv3", int(proc))


class CmdContext_RtrOSPFv3(IndentedContextualCommand):
    context = "router-ospfv3"


class Cmd_RtrOSPFv3_Id(CmdContext_RtrOSPFv3):
    match = r"router-id (?P<id_>[.0-9]+)"

    def parse(self, cfg, id_):
        cfg["id"] = id_


class Cmd_RtrOSPFv3_AreaNSSA(CmdContext_RtrOSPFv3):
    match = (r"area (?P<area>\S[.0-9]+)"
             r" nssa(?P<no_redist> no-redistribution)?"
             r"(?P<no_summ> no-summary)?")

    def parse(self, cfg, area, no_redist, no_summ):
        a = set()
        if no_redist: a.add("no-redistribution")
        if no_summ: a.add("no-summary")
        deepsetdefault(cfg, "area", area)["nssa"] = a


class Cmd_RtrOSPFv3_AF(CmdContext_RtrOSPFv3):
    # "unicast" on the end is effectively ignored
    match = r"address-family (?P<af>ipv4|ipv6)( unicast)?"
    enter_context = "router-ospfv3-af"

    def parse(self, cfg, af):
        return deepsetdefault(cfg, "address-family", af)


class CmdContext_RtrOSPFv3_AF(CmdContext_RtrOSPFv3):
    context = "router-ospfv3-af"


class Cmd_RtrOSPFv3_AF_PasvInt(CmdContext_RtrOSPFv3_AF):
    match = r"(?P<no>no )?passive-interface (?P<int_name>\S+)"

    def parse(self, cfg, no, int_name):
        p = deepsetdefault(cfg, "passive-interface")
        if int_name == "default":
            if not no:
                p["default"] = True
        else:
            deepsetdefault(
                p, "interface")[interface_canonicalize(int_name)] = not no


class Cmd_RtrOSPFv3_PasvInt(CmdContext_RtrOSPFv3):
    match = r"(?P<no>no )?passive-interface (?P<int_name>\S+)"

    def parse(self, cfg, no, int_name):
        # the handling of this command outside of an address-family
        # block is a bit odd - it isn't stored at the router process
        # level but in the address family block and only affects the
        # currently defined address families, so if an address family
        # is added later, this will not propagate down
        for af in cfg.get("address-family", []):
            p = deepsetdefault(cfg, "address-family", af, "passive-interface")
            if int_name == "default":
                if not no:
                    p["default"] = True
            else:
                deepsetdefault(
                    p, "interface")[interface_canonicalize(int_name)] = not no
