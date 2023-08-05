# ios.converters.lists
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from ..utils import explain_diffs

from ...diff import DiffConvert



# --- converter classes ---



# IP[V6] ACCESS-LIST ...



class Cvt_IPACL_Std(DiffConvert):
    cmd = "ip-access-list-standard", None

    def remove(self, old, acl_name):
        return "no ip access-list standard " + acl_name

    def update(self, old, upd, new, acl_name):
        return ["no ip access-list standard " + acl_name,
                "ip access-list standard " + acl_name,
                *explain_diffs(old, new, indent=" ")]


class Cvt_IPACL_Ext(DiffConvert):
    cmd = "ip-access-list-extended", None

    def remove(self, old, acl_name):
        return "no ip access-list extended " + acl_name

    def update(self, old, upd, new, acl_name):
        return ["no ip access-list extended " + acl_name,
                "ip access-list extended " + acl_name,
                *explain_diffs(old, new, indent=" ")]


class Cvt_IPv6ACL_Ext(DiffConvert):
    cmd = "ipv6-access-list", None

    def remove(self, old, acl_name):
        return "no ipv6 access-list " + acl_name

    def update(self, old, upd, new, acl_name):
        return ["no ipv6 access-list " + acl_name,
                "ipv6 access-list " + acl_name,
                *explain_diffs(old, new, indent=" ")]



# IP AS-PATH ACCESS-LIST ...



class Cvt_IPASPathACL(DiffConvert):
    cmd = "ip-as-path-access-list", None

    def to_str(self, rule):
        action, re = rule
        return action + " " + re

    def remove(self, old, num):
        return "no ip as-path access-list " + str(num)

    def update(self, old, upd, new, num):
        r = []
        if old:
            r += ["no ip as-path access-list " + str(num)]
        r += explain_diffs(old, new, prefix="ip as-path access-list %d " % num,
                           to_str_func=self.to_str)
        return r



# IP[V6] PREFIX-LIST ...



class Cvt_IPPfxList(DiffConvert):
    cmd = "ip-prefix-list", None

    def remove(self, old, pfx_name):
        return "no ip prefix-list " + pfx_name

    def update(self, old, upd, new, pfx_name):
        return ["no ip prefix-list " + pfx_name,
                *explain_diffs(
                    old, new, prefix="ip prefix-list %s " % pfx_name)]


class Cvt_IPv6PfxList(DiffConvert):
    cmd = "ipv6-prefix-list", None

    def remove(self, old, pfx_name):
        return "no ipv6 prefix-list " + pfx_name

    def update(self, old, upd, new, pfx_name):
        return ["no ipv6 prefix-list " + pfx_name,
                *explain_diffs(
                    old, new, prefix="ipv6 prefix-list %s " % pfx_name)]
