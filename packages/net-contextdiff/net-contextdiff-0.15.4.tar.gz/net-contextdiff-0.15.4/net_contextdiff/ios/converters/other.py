# ios.converters.all
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from ...diff import DiffConvert



# --- converter classes ---



# SYSTEM



class Cvt_Hostname(DiffConvert):
    cmd = "hostname",

    def remove(self, old):
        return "no hostname"

    def update(self, old, upd, new):
        return "hostname " + new



# [NO] SPANNING-TREE ...



class Cvt_NoSTP(DiffConvert):
    cmd = "no-spanning-tree-vlan", None

    def remove(self, old, tag):
        # removing 'no spanning-tree' enables spanning-tree
        return "spanning-tree vlan %d" % tag

    def update(self, old, upd, new, tag):
        # adding 'no spanning-tree' disables spanning-tree
        return "no spanning-tree vlan %d" % tag


class Cvt_STPPri(DiffConvert):
    cmd = "spanning-tree-vlan-priority", None

    def remove(self, old, tag):
        return "no spanning-tree vlan %d priority" % tag

    def update(self, old, upd, new, tag):
        return "spanning-tree vlan %d priority %d" % (tag, new)



# TRACK ...



# the track command is odd in that it doesn't allow the type of tracking
# object to be changed (e.g. from an interface to a route) and must be
# destroyed and created anew
#
# the parameters of the type of track can, however, be changed, e.g. the
# specific interface or route that's being tracked



class Cvt_Track(DiffConvert):
    cmd = "track", None

    def remove(self, old, track_num):
        return "no track " + str(track_num)


class Cvt_TrackUpdate(DiffConvert):
    cmd = "track", None
    ext = "type",

    def update(self, old, upd, new, track_num):
        # when the type of a tracking object is changed, it must be
        # deleted and the new type created
        return "no track " + str(track_num)


class DiffConvert_TrackCreate(DiffConvert):
    context = "track", None
    block = "track-create"
    trigger_blocks = { "track-sub" }


class Cvt_TrackInterface(DiffConvert_TrackCreate):
    cmd = "interface",

    def update(self, old, upd, new, track_num):
        return ["track %d interface %s %s"
                    % (track_num, new["interface"], new["capability"])]


class Cvt_TrackList(DiffConvert_TrackCreate):
    cmd = "list",

    def update(self, old, upd, new, track_num):
        if new["type"] == "bool":
            return ["track %d list boolean %s" % (track_num, new["op"])]

        return ValueError("invalid track list type:" + l["type"])


class Cvt_TrackRoute(DiffConvert_TrackCreate):
    cmd = "route",

    def update(self, old, upd, new, track_num):
        return ["track %d %s %s %s"
                    % (track_num, new["proto"], new["net"], new["measure"])]


class DiffConvert_TrackSub(DiffConvert):
    context = Cvt_Track.cmd
    block = "track-sub"

    def enter(self, track_num):
        return "track " + str(track_num),


class Cvt_Track_Delay(DiffConvert_TrackSub):
    cmd = "delay",

    def remove(self, old, obj):
        return [*self.enter(obj), " no delay"]

    def update(self, old, upd, new, obj):
        return [*self.enter(obj), " delay " + new]


class Cvt_Track_IPVRF(DiffConvert_TrackSub):
    cmd = "ip-vrf",

    def remove(self, old, obj):
        return [*self.enter(obj), " no ip vrf"]

    def update(self, old, upd, new, obj):
        return [*self.enter(obj), " ip vrf " + new]


class Cvt_Track_IPv6VRF(DiffConvert_TrackSub):
    cmd = "ipv6-vrf",

    def remove(self, old, obj):
        return [*self.enter(obj), " no ipv6 vrf"]

    def update(self, old, upd, new, obj):
        return [*self.enter(obj), " ipv6 vrf " + new]


class Cvt_Track_ListObj(DiffConvert_TrackSub):
    cmd = "object", None

    def remove(self, old, obj, sub_obj):
        return [*self.enter(obj), " no object " + sub_obj]

    def update(self, old, upd, new, obj, sub_obj):
        return [*self.enter(obj), " object " + sub_obj]



# VLAN ...



class Cvt_VLAN(DiffConvert):
    cmd = "vlan", None

    def remove(self, old, tag):
        return "no vlan %d" % tag

    def add(self, new, tag):
        return "vlan %d" % tag


class Cvt_VLAN_Name(DiffConvert):
    context = Cvt_VLAN.cmd
    cmd = "name",

    def remove(self, old, tag):
        return "vlan " + str(tag), " no name"

    def update(self, old, upd, new, tag):
        return "vlan " + str(tag), " name " + new



# VRF ...



class Cvt_VRF(DiffConvert):
    cmd = "vrf", None

    def remove(self, old, name):
        return "no vrf definition " + name

    def add(self, new,  name):
        return "vrf definition " + name


class DiffConvert_VRF(DiffConvert):
    context = Cvt_VRF.cmd

    def enter(self, vrf):
        return "vrf definition " + vrf,


class Cvt_VRF_RD(DiffConvert_VRF):
    cmd = "rd",

    def remove(self, old, vrf):
        return [*self.enter(vrf), " no rd " + old]

    def update(self, old, upd, new, vrf):
        l = list(super().enter(vrf))
        if old:
            l.append(" no rd " + old)
        l.append(" rd " + new)
        return l


class Cvt_VRF_RT(DiffConvert_VRF):
    cmd = "route-target", None, None

    def truncate(self, old, rem, new, vrf, dir_, rt):
        return [*self.enter(vrf), " no route-target %s %s" % (dir_, rt)]

    def update(self, old, upd, new, vrf, dir_, rt):
        return [*self.enter(vrf), " route-target %s %s" % (dir_, rt)]


class Cvt_VRF_AF(DiffConvert_VRF):
    cmd = "address-family", None

    def remove(self, old, vrf, af):
        return [*self.enter(vrf), " no address-family " + af]

    def add(self, new, vrf, af):
        return [*self.enter(vrf), " address-family " + af]


class DiffConvert_VRF_AF(DiffConvert_VRF):
    context = DiffConvert_VRF.context + Cvt_VRF_AF.cmd

    def enter(self, vrf, af):
        return [*super().enter(vrf), " address-family " + af]


class Cvt_VRF_AF_RT(DiffConvert_VRF_AF):
    cmd = "route-target", None, None

    def truncate(self, old, rem, new, vrf, af, dir_, rt):
        return [*self.enter(vrf, af), "  no route-target %s %s" % (dir_, rt)]

    def update(self, old, upd, new, vrf, af, dir_, rt):
        return [*self.enter(vrf, af), "  route-target %s %s" % (dir_, rt)]
