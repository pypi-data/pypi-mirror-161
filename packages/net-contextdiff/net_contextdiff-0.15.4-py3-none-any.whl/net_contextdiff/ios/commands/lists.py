# ios.commands.lists
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from deepops import deepsetdefault

from ..utils import ip_acl_ext_rule_canonicalize, ipv6_acl_rule_canonicalize
from ...config import IndentedContextualCommand



# --- configuration command classes ---



# IP ACCESS-LIST STANDARD



class Cmd_ACLStdRule(IndentedContextualCommand):
    match = r"access-list (?P<num>\d{1,2}|1[3-9]\d{2}) (?P<rule>.+)"

    def parse(self, cfg, num, rule):
        deepsetdefault(
            cfg, "ip-access-list-standard", num, last=[]).append(rule)


class Cmd_IPACL_Std(IndentedContextualCommand):
    match = r"ip access-list standard (?P<acl_name>.+)"
    enter_context = "ip-acl_std"

    def parse(self, cfg, acl_name):
        return deepsetdefault(
                   cfg, "ip-access-list-standard", acl_name, last=[])


class Cmd_IPACL_Std_Rule(IndentedContextualCommand):
    context = "ip-acl_std"
    match = r"(?P<rule>(permit|deny) +.+)"

    def parse(self, cfg, rule):
        cfg.append(rule)


class Cmd_ACLExtRule(IndentedContextualCommand):
    match = r"access-list (?P<num>1\d{2}|2[0-6]\d{2}) (?P<rule>.+)"

    def parse(self, cfg, num, rule):
        deepsetdefault(
            cfg, "ip-access-list-extended", num, last=[]
            ).append(ip_acl_ext_rule_canonicalize(rule))


class Cmd_IPACL_Ext(IndentedContextualCommand):
    match = r"ip access-list extended (?P<name>.+)"
    enter_context = "ip-acl_ext"

    def parse(self, cfg, name):
        return deepsetdefault(cfg, "ip-access-list-extended", name, last=[])


class Cmd_IPACL_Ext_Rule(IndentedContextualCommand):
    context = "ip-acl_ext"
    match = r"(?P<rule>(permit|deny) +.+)"

    def parse(self, cfg, rule):
        cfg.append(ip_acl_ext_rule_canonicalize(rule))



# IPV6 ACCESS-LIST ...



class Cmd_IPv6ACL(IndentedContextualCommand):
    match = r"ipv6 access-list (?P<name>.+)"
    enter_context = "ipv6-acl"

    def parse(self, cfg, name):
        return deepsetdefault(cfg, "ipv6-access-list", name, last=[])


class Cmd_IPv6ACL_Rule(IndentedContextualCommand):
    context = "ipv6-acl"
    match = r"(?P<rule>(permit|deny) +.+)"

    def parse(self, cfg, rule):
        cfg.append(ipv6_acl_rule_canonicalize(rule))



# IP AS-PATH ACCESS-LIST ...



class Cmd_IPASPathACL(IndentedContextualCommand):
    match = (r"ip as-path access-list (?P<num>\d+) (?P<action>permit|deny)"
             r" (?P<re>\S+)")

    def parse(self, cfg, num, action, re):
        l = deepsetdefault(cfg, "ip-as-path-access-list", int(num), last=[])
        l.append( (action, re) )



# IP[V6] PREFIX-LIST ...



class Cmd_IPPfx(IndentedContextualCommand):
    match = r"ip prefix-list (?P<list_>\S+) (seq \d+ )?(?P<rule>.+)"

    def parse(self, cfg, list_, rule):
        deepsetdefault(cfg, "ip-prefix-list", list_, last=[]).append(rule)


class Cmd_IPv6Pfx(IndentedContextualCommand):
    match = r"ipv6 prefix-list (?P<list_>\S+) (seq \d+ )?(?P<rule>.+)"

    def parse(self, cfg, list_, rule):
        deepsetdefault(
            cfg, "ipv6-prefix-list", list_, last=[]).append(rule.lower())
