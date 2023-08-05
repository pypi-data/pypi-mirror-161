# ios.converters.router
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



import netaddr

from ...diff import DiffConvert



# --- converter classes ---



# IP[V6] ROUTE ...



class Cvt_IPRoute(DiffConvert):
    cmd = "ip-route", None, None, None

    def _cmd(self, vrf, net, r):
        n = netaddr.IPNetwork(net)

        return ("ip route"
                + ((" vrf " + vrf) if vrf else "")
                + " " + str(n.network) + " " + str(n.netmask)
                + ((" " + r["interface"]) if "interface" in r else "")
                + ((" " + r["router"]) if "router" in r else "")
                + ((" " + str(r["metric"])) if "metric" in r else "")
                + ((" tag " + str(r["tag"])) if "tag" in r else ""))

    def remove(self, old, vrf, net, id):
        return "no " + self._cmd(vrf, net, old)

    def update(self, old, upd, new, vrf, net, id):
        return self._cmd(vrf, net, new)


class Cvt_IPv6Route(DiffConvert):
    cmd = "ipv6-route", None, None, None

    def _cmd(self, vrf, net, r):
        return ("ipv6 route"
                + ((" vrf " + vrf) if vrf else "")
                + " " + net
                + ((" " + r["interface"]) if "interface" in r else "")
                + ((" " + r["router"]) if "router" in r else "")
                + ((" " + str(r["metric"])) if "metric" in r else "")
                + ((" tag " + str(r["tag"])) if "tag" in r else ""))

    def remove(self, old, vrf, net, id):
        return "no " + self._cmd(vrf, net, old)

    def update(self, old, upd, new, vrf, net, id):
        return self._cmd(vrf, net, new)



# ROUTER OSPF ...



class Cvt_RtrOSPF(DiffConvert):
    cmd = "router", "ospf", None

    def remove(self, old, proc):
        return "no router ospf " + str(proc)

    def add(self, new, proc):
        return "router ospf " + str(proc)


class DiffConvert_RtrOSPF(DiffConvert):
    context = "router", "ospf", None

    def enter(self, proc):
        return "router ospf " + str(proc),


class Cvt_RtrOSPF_Id(DiffConvert_RtrOSPF):
    cmd = "id",

    def remove(self, old, proc):
        return [*self.enter(proc), " no router-id"]

    def update(self, old, upd, new, proc):
        return [*self.enter(proc), " router-id " + new]


class Cvt_RtrOSPF_AreaNSSA(DiffConvert_RtrOSPF):
    cmd = "area", None, "nssa"

    def remove(self, old, proc, area):
        return [*self.enter(proc), " no area %s nssa" % area]

    def update(self, old, upd, new, proc, area):
        s = ""
        if "no-redistribution" in new: s += " no-redistribution"
        if "no-summary" in new: s += " no-summary"
        return [*self.enter(proc), " area %s nssa%s" % (area, s)]


class Cvt_RtrOSPF_PasvInt_Dflt(DiffConvert_RtrOSPF):
    cmd = "passive-interface", "default"

    def remove(self, old, proc):
        return [*self.enter(proc),
                " %spassive-interface default" % ("no " if old else "")]

    def update(self, old, upd, new, proc):
        return [*self.enter(proc),
                " %spassive-interface default" % ("" if new else "no ")]


class Cvt_RtrOSPF_PasvInt_Int(DiffConvert_RtrOSPF):
    cmd = "passive-interface", "interface", None

    def remove(self, old, proc, int_name):
        return [*self.enter(proc),
                " %spassive-interface %s" % ("no " if old else "", int_name)]

    def update(self, old, upd, new, proc, int_name):
        return [*self.enter(proc),
                " %spassive-interface %s" % ("" if new else "no ", int_name)]



# ROUTER OSPFV3 ...



class Cvt_RtrOSPFv3(DiffConvert):
    cmd = "router", "ospfv3", None

    def remove(self, old, proc):
        return "no router ospfv3 " + str(proc)

    def add(self, new, proc):
        return "router ospfv3 " + str(proc)


class DiffConvert_RtrOSPFv3(DiffConvert):
    context = "router", "ospfv3", None

    def enter(self, proc):
        return "router ospfv3 " + str(proc),


class Cvt_RtrOSPFv3_Id(DiffConvert_RtrOSPFv3):
    cmd = "id",

    def remove(self, old, proc):
        return [*self.enter(proc), " no router-id"]

    def update(self, old, upd, new, proc):
        return [*self.enter(proc), " router-id " + new]


class Cvt_RtrOSPFv3_AreaNSSA(DiffConvert_RtrOSPFv3):
    cmd = "area", None, "nssa"

    def remove(self, old, proc, area):
        return [*self.enter(proc), " no area %s nssa" % area]

    def update(self, old, upd, new, proc, area):
        s = ""
        if "no-redistribution" in new: s += " no-redistribution"
        if "no-summary" in new: s += " no-summary"
        return [*self.enter(proc), " area %s nssa%s" % (area, s)]


class Cvt_RtrOSPFv3_AF(DiffConvert_RtrOSPFv3):
    cmd = "address-family", None

    def remove(self, old, vrf, af):
        return [*self.enter(vrf), " no address-family " + af]

    def add(self, new, vrf, af):
        return [*self.enter(vrf), " address-family " + af]


class DiffConvert_RtrOSPFv3_AF(DiffConvert_RtrOSPFv3):
    context = DiffConvert_RtrOSPFv3.context + Cvt_RtrOSPFv3_AF.cmd

    def enter(self, vrf, af):
        return [*super().enter(vrf), " address-family " + af]


class Cvt_RtrOSPFv3_AF_PasvInt_Dflt(DiffConvert_RtrOSPFv3_AF):
    cmd = "passive-interface", "default"

    def remove(self, old, proc, af):
        return [*self.enter(proc, af),
                " %spassive-interface default" % ("no " if old else "")]

    def update(self, old, upd, new, proc, af):
        return [*self.enter(proc, af),
                "  %spassive-interface default" % ("" if new else "no ")]


class Cvt_RtrOSPFv3_AF_PasvInt_Int(DiffConvert_RtrOSPFv3_AF):
    cmd = "passive-interface", "interface", None

    def remove(self, old, proc, af, int_name):
        return [*self.enter(proc, af),
                "  %spassive-interface %s" % ("no " if old else "", int_name)]

    def update(self, old, upd, new, proc, af, int_name):
        return [*self.enter(proc, af),
                "  %spassive-interface %s" % ("" if new else "no ", int_name)]
