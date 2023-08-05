# ios.utils
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



"""Cisco IOS utility functions.

This module contains functions to help parsing Cisco IOS configuration
files.
"""



# --- imports ---



import difflib
import re

from netaddr import IPNetwork

from net_contextdiff.config import (
    IndentedContextualCommand, IndentedContextualConfig)



# --- interface functions ---



# interface names and their canonical representations - the canonical
# versions don't have to be how Cisco IOS always displays them, in any
# particular context, but just so they can consistently matched against

_INTERFACE_CANONICALS = {
    "ethernet": "Eth",
    "fastethernet": "Fa",
    "gigabitethernet": "Gi",
    "tengigabitethernet": "Te",
    "twentyfivegigethernet": "Twe",
    "fortygigabitethernet": "Fo",
    "hundredgigethernet": "Hu",
    "port-channel": "Po",
    "vl": "Vlan",
}



# regular expression for matching interface names and separating the
# time (e.g. 'Ethernet') from the number (e.g. '1' or '1/1.1')

_INTERFACE_NAME_RE = re.compile(r"([-a-z]+)([0-9/.]*)$")



def interface_canonicalize(name):
    """This function takes an interface name (including type and
    number) and returns a canonical version of it, handling
    abbreviations or case differences.

    At the moment, this just handles a defined set of names but it
    should really be more general and handle arbitrary short versions.
    """

    match = _INTERFACE_NAME_RE.match(name.lower())

    if match:
        type_, num = match.groups()
        type_ = _INTERFACE_CANONICALS.get(type_, type_).capitalize()
        name = type_ + num

    return name



# --- ACL functions ---



def _ipnet4_to_ios(ipnet4):
    """This function converts an IPv4 IPNetwork object into its
    canonical representation in Cisco IOS in a standard access-list.

    Conversions are '0.0.0.0/0' to 'any' and single host networks (i.e.
    simple addresses) into a plain address with no mask.
    """

    if ipnet4 == IPNetwork("0.0.0.0/0"):
        return "any"

    if ipnet4.prefixlen == 32:
        return str(ipnet4.ip)

    return str(ipnet4.ip) + " " + str(ipnet4.hostmask)



# IPV4 STANDARD ACCESS CONTROL LIST RULES



# regular expression for matching an IPv4 standard ACL rule, compiled
# once for efficiency

_IP_ACL_STD_RULE_RE = re.compile(
    r"^"
    r"(?P<action>permit|deny)"
    r" +"

    # we match "0.0.0.0 255.255.255.255" as "any" because the
    # netaddr module assumes the mask is a netmask (= /32) rather
    # than a hostmask, in this case
    r"((?P<any>any|0\.0\.0\.0 255\.255\.255\.255)|"
        r"(?:host )?(?P<host>[0-9.]+)|"
        r"(?P<net>[0-9.]+) (?P<mask>[0-9.]+))"

    r"$")


def _ip_acl_std_rule_parse(rule):
    """Parse an IPv4 standard ACL rule, returning a 2-element tuple
    consisting of the action ('permit' or 'deny') and an IPNetwork
    object, specifying the address/network to match.
    """


    match = _IP_ACL_STD_RULE_RE.match(rule)

    if not match:
        raise ValueError(
            "failed to parse IPv4 standard ACL rule: " + rule)


    # match some special cases and, if not those, match as a
    # network/hostmask

    if match.group("any"):
        ipnet4 = IPNetwork("0.0.0.0/0")

    elif match.group("host"):
        ipnet4 = IPNetwork(match.group("host"))

    else:
        ipnet4 = IPNetwork(match.group("net") + "/" + match.group("mask"))


    return match.group("action"), ipnet4



def ip_acl_std_canonicalize(l):
    """This function sorts an IPv4 standard access-list into a canoncial
    form so two lists can be compared.  The list is supplied and
    returned as a new list of IOS rules.  Note that it is not sorted in
    place), as parsed by _ip_acl_std_rule_parse().

    IPv4 standard ACLs are complicated in IOS due to its tendancy to
    reorganise the rules, after they're entered.  It always preserves
    the semantics of the list (never putting an overlapping 'permit' and
    'deny' in the wrong order), but it can move rules which don't
    interact around.  Presumably this is done to optimise processing.

    The solution adopted here is to build the ACLs up in blocks.  Each
    block is a set of rules where the address portions don't overlap;
    these are built, sorting each block into address order, before
    adding the sorted rules in the block into the resulting list.

    The result is lists which are not necessarily in the same order as
    they were constructed, nor how IOS stores them, but two lists should
    at least be in the same order so they can be directly compared.

    This function is applied to each list, after the configuration is
    read, and the returned list used to replace the order in which the
    rules were read.
    """


    # initialise the returned (canonical list)
    result = []

    # initialise the current block of non-overlapping rules
    block = []

    # go through the rules in the supplied list
    for rule in l:
        # parse the rule into action string and IPNetwork
        action, net = _ip_acl_std_rule_parse(rule)

        # find out if this rule overlaps with the network of a rule
        # already in the block
        overlap = [ None for _, chk_net
                         in block
                         if ((net.first <= chk_net.last)
                             and (net.last >= chk_net.first)) ]

        if overlap:
            # we had an overlap, add the current block to the returned
            # list and reinitialise it with just this new rule
            result.extend(block)
            block = [(action, net)]

        else:
            # add this rule to the current block and re-sort it on the
            # addresses of the rules in it
            block.append( (action, net) )
            block.sort(key=(lambda rule: rule[1]))

    # we've reached the end, so store the rules in the current block on
    # the end of the list
    result.extend(block)

    # convert the rules back into IOS text format and return them as a
    # list
    return [ (action + " " + _ipnet4_to_ios(net)) for action, net in result ]



# IPV4 EXTENDED ACCESS CONTROL LIST RULES



# regular expression for matching an IPv4 extended ACL rule, compiled
# once for efficiency

_IP_ACL_EXT_RULE_RE = re.compile(
    r"^"
    r"(?P<action>permit|deny)"
    r" +"
    r"(?P<protocol>ip|icmp|tcp|udp|igmp|pim|gre|esp)"
    r" "
    r"(?P<src_addr>any|host ([0-9.]+)|([0-9.]+) ([0-9.]+))"
    r"( ("
        # 'eq' and 'neq' can support a list of services - we need to match
        # them non-greedy
        r"((?P<src_port_listop>eq|neq) (?P<src_port_list>\S+( \S+)*?))|"

        r"((?P<src_port_1op>lt|gt) (?P<src_port_num>\S+))|"
        r"range (?P<src_port_low>\S+) (?P<src_port_high>\S+)"
    r"))?"
    r" "
    r"(?P<dst_addr>any|host ([0-9.]+)|([0-9.]+) ([0-9.]+))"
    r"( ("
        r"((?P<dst_port_listop>eq|neq) (?P<dst_port_list>\S+( \S+)*?))|"
        r"((?P<dst_port_1op>lt|gt) (?P<dst_port_num>\S+))|"
        r"range (?P<dst_port_low>\S+) (?P<dst_port_high>\S+)|"
        r"(?P<icmp_type>echo(-reply)?)"
    r"))?"
    r"(?P<established> established)?"
    r"(?P<qos> (dscp \S+))?"
    r"(?P<log> (log|log-input))?"
    r"$"
)



# _SERVICE_PORTS = dict
#
# Dictionary mapping service names (as displayed/usable in an access-
# list rule) into a port number.
#
# TODO: this list is not complete but parses all the rules we currently
# have in use.  It should be expanded at some point to all services.

_SERVICE_PORTS = {
    "bootps": 67,
    "bootpc": 68,
    "discard": 9,
    "domain": 53,
    "exec": 512,
    "finger": 79,
    "ftp": 21,
    "ftp-data": 20,
    "gopher": 70,
    "ident": 113,
    "isakmp": 500,
    "lpd": 515,
    "mail": 25,
    "netbios-ns": 137,
    "netbios-ss": 139,
    "non500-isakmp": 4500,
    "ntp": 123,
    "pop2": 109,
    "pop3": 110,
    "smtp": 25,
    "snmp": 161,
    "snmptrap": 162,
    "sunrpc": 111,
    "syslog": 514,
    "tftp": 69,
    "www": 80
}



def _port_canonicalize(service):
    """Converts a Cisco service named 'service' (as displayed/usable in
    an access-list rule) into a port number and return it as an
    integer.

    If the service name is not defined, it is assumed to already be
    numeric and is converted to an integer and returned.  If this
    conversion fails, an exception will be raised (whch probably
    indicates a service that is missing from the list).
    """

    return _SERVICE_PORTS.get(service) or int(service)



def ip_acl_ext_rule_canonicalize(rule):
    """Parse an IPv4 extended ACL rule, returning a 'normalised'
    form of the rule as a string.  The normalised form should allow
    two ACL rules which mean the same thing to be compared using a
    simple string comparison.

    This process mainly involves extracting the port entries and
    [potentially] translating them into port numbers, if they're named
    services (which can be used in rules, plus IOS will translate a
    numbered service to a name, if one matches).

    Note that no attempt is made to check the rule for validity.
    """


    match = _IP_ACL_EXT_RULE_RE.match(rule)

    if not match:
        raise ValueError(
            "failed to parse IPv4 extended ACL rule: " + rule)


    action, protocol, src_addr, dst_addr = match.group(
        "action", "protocol", "src_addr", "dst_addr")


    # match.group() will return an error if a named group does not exist
    # in the regexp; match.groupdict(), however, will return a default
    # value (None, if not specified) for named groups that do not exist
    #
    # as such, we need to check if the retrieved groups are blank or
    # not, for optional/alternative parts of a rule

    groups = match.groupdict()


    src_port = ""

    if groups["src_port_listop"]:
        # if 'eq' or 'neq' was found for the source port, it will be one
        # or more services, separated by spaces - we need to split the
        # list up and turn each one into a port number, then join the
        # list back together again

        src_port = (
            " %s %s" % (
                groups["src_port_listop"],
                " ".join([str(_port_canonicalize(s))
                              for s
                              in groups["src_port_list"].split(" ")])))

    elif groups["src_port_1op"]:
        src_port = " %s %d" % (
                       groups["src_port_1op"],
                       _port_canonicalize(groups["src_port_num"]))

    elif groups["src_port_low"]:
        src_port = " range %d %d" % (
                        _port_canonicalize(groups["src_port_low"]),
                        _port_canonicalize(groups["src_port_high"]))


    dst_port = ""

    if groups["dst_port_listop"]:
        dst_port = (
            " %s %s" % (
                groups["dst_port_listop"],
                " ".join([str(_port_canonicalize(s))
                              for s
                              in groups["dst_port_list"].split(" ")])))

    elif groups["dst_port_1op"]:
        dst_port = " %s %d" % (
                        groups["dst_port_1op"],
                        _port_canonicalize(groups["dst_port_num"]))

    elif groups["dst_port_low"]:
        dst_port = " range %d %d" % (
                        _port_canonicalize(groups["dst_port_low"]),
                        _port_canonicalize(groups["dst_port_high"]))

    # the destination port could also be an ICMP message type
    elif groups["icmp_type"]:
        dst_port = " " + groups["icmp_type"]


    established = groups["established"] or ""

    qos = groups["qos"] or ""

    log = groups["log"] or ""


    return (action + " " + protocol
            + " " + src_addr + src_port
            + " " + dst_addr + dst_port + established + qos + log)



# IPV6 EXTENDED ACCESS CONTROL LIST RULES



# regular expression for matching an IPv6 access-list rule, compiled
# once for efficiency
#
# TODO: we know this doesn't match some of the more complicated rules
# (such as the CP policing ones matching ICMPv6 types) but we're
# excluding those in the output, anyway, so we just ignore them - as
# such, we don't match the end of string ('$')

_IPV6_ACL_RULE_RE = re.compile(
    r"^"
    r"(?P<action>permit|deny)"
    r"( "
        r"(?P<protocol>ipv6|icmp|tcp|udp|\d+)"
    r")?"
    r" "
    r"(?P<src_addr>any|host [0-9A-Fa-f:]+|[0-9A-Fa-f:]+/\d+)"
    r"( ("
        r"((?P<src_port_1op>eq|lt|gt|neq) (?P<src_port_num>\S+))|"
        r"range (?P<src_port_low>\S+) (?P<src_port_high>\S+)"
    r"))?"
    r" "
    r"(?P<dst_addr>any|host [0-9A-Fa-f:]+|[0-9A-Fa-f:]+/\d+)"
    r"( ("
        r"((?P<dst_port_1op>eq|lt|gt|neq) (?P<dst_port_num>\S+))|"
        r"range (?P<dst_port_low>\S+) (?P<dst_port_high>\S+)|"
        r"(?P<icmp_type>echo(-reply)?)"
    r"))?"
    r"(?P<established> established)?"
    r"(?P<log> (log|log-input))?"
)


def ipv6_acl_rule_canonicalize(rule):
    """Parse an IPv6 ACL rule, returning a 'normalised' form of the rule
    as a string.  The normalised form should allow two ACL rules which
    mean the same thing to be compared using a simple string comparison.

    This process mainly involves extracting the port entries and
    [potentially] translating them into port numbers, if they're named
    services (which can be used in rules, plus IOS will translate a
    numbered service to a name, if one matches).

    Note that no attempt is made to check the rule for validity.
    """


    match = _IPV6_ACL_RULE_RE.match(rule)

    if not match:
        raise ValueError("failed to parse IPv6 ACL rule: " + rule)


    action, protocol, src_addr, dst_addr = match.group(
        "action", "protocol", "src_addr", "dst_addr")


    # if the protocol was not specified, we default to 'ipv6'

    if protocol is None:
        protocol = "ipv6"


    # lower case the source and destination addresses since IPv6
    # addresses can either be in upper or lower case (usually upper, in
    # IOS); we choose lower here, though, to avoid upper-casing the
    # keywords 'host' and 'any'

    src_addr = src_addr.lower()
    dst_addr = dst_addr.lower()


    # match.group() will return an error if a named group does not exist
    # in the regexp; match.groupdict(), however, will return a default
    # value (None, if not specified) for named groups that do not exist
    #
    # as such, we need to check if the retrieved groups are blank or
    # not, for optional/alternative parts of a rule

    groups = match.groupdict()


    src_port = ""

    if groups["src_port_num"]:
        src_port = " %s %d" % (
                       groups["src_port_1op"],
                       _port_canonicalize(groups["src_port_num"]))

    elif groups["src_port_low"]:
        src_port = " range %d %d" % (
                       _port_canonicalize(groups["src_port_low"]),
                       _port_canonicalize(groups["src_port_high"]))


    dst_port = ""

    if groups["dst_port_num"]:
        dst_port = " %s %d" % (
                       groups["dst_port_1op"],
                       _port_canonicalize(groups["dst_port_num"]))

    elif groups["dst_port_low"]:
        dst_port = " range %d %d" % (
                       _port_canonicalize(groups["dst_port_low"]),
                       _port_canonicalize(groups["dst_port_high"]))


    elif groups["icmp_type"]:
        dst_port = " " + groups["icmp_type"]


    established = groups["established"] or ""

    log = groups["log"] or ""


    return (action + " " + protocol
            + " " + src_addr + src_port
            + " " + dst_addr + dst_port + established)



# --- other functions ---



def expand_set(s):
    """This function exapands a string giving a set of numbers,
    separated by commas, which can include ranges from low to high,
    using hyphens.  The return value will be the set of numbers
    expressed.

    For example, given a string of "1,3-5", a set containing 1, 3, 4
    and 5 will be returned.
    """

    t = set()

    for i in s.split(","):
        i_range = i.split("-")

        if len(i_range) == 1:
            t.add(int(i))
        else:
            t.update(range(int(i_range[0]), int(i_range[1]) + 1))

    return t



# --- list differ ---



# create a differ object (we use it each time we do a comparison, so
# just create it once, at the start)
#
# this is only used by compare_lists(), below, so we don't need to
# export it

_differ = difflib.Differ()



def explain_diffs(old, new, indent="", prefix="", to_str_func=None):
    """This function compares two lists (typically an access-list or
    prefix-list) and returns the commands to create the new list but
    interspersed with comments that explain the differences.

    The 'indent' string is added to the start of every line (including
    the comments) and is typically set to a space character, for 'ip
    access-list ...', where the rules are in a subcontext, but left the
    empty string for things like 'ip prefix-list ...', where they are
    not.

    The 'prefix' is added after the indent, before the text of each
    line.  It is not included on lines with comments.  It would be set
    to the empty string for 'ip access-list ...' (where no extra string
    is required) or something like 'ip prefix-list NAME ', where this
    is required on the same line.  Note that it must contain a trailing
    space, if one is required, between it and the line.

    If either of the two lists supplied are None, an empty list is
    assumed, either removing or adding all the entries.

    The optional 'to_str_func' argument is used to convert list elements
    to strings, in advance of the comparison.  This is useful when the
    data in the lists is stored in a structured form (such as a tuple or
    dictionary).  The argument takes a function which is passed the
    element and must return a string.

    The return value is a list of lines these explaining comments
    inserted.  The lines without comments will create the new list.
    """

    # if either old or new missing, default them to the empty list
    old = old or []
    new = new or []

    # if we have a string conversion function, apply that and convert
    # the result to a list (it would otherwise be a generator which does
    # not have a length and can only be iterated through)
    if to_str_func:
        old = list(to_str_func(i) for i in old)
        new = list(to_str_func(i) for i in new)

    # initialise the returned list
    r = []

    # keep track of if the last operation was to add an entry - we use
    # this to add markers at the beginning and end of an added block
    last_add = False

    # work through the differences between the two lists using
    # difflib.Differ.compare, which adds a character at the start,
    # explaining if a line is added, removed or the same, followed by
    # a space
    for line in _differ.compare(old, new):
        op, text = line[0], line[2:]

        if op == " ":
            # line is the same

            # if we were previously adding lines, indicate we're not
            # any more
            if last_add:
                r.append(indent + "!= ...")
                last_add = False

            # add this line
            r.append(indent + prefix + text)

        elif op == "+":
            # line is being added

            # if we're not already in a block of added lines, add a
            # comment, indicating that we're beginning doing that
            if not last_add:
                r.append(indent + "!+ ...")
                last_add = True

            # add this line
            r.append(indent + prefix + text)

        elif op == "-":
            # line is being removed

            # doesn't matter if we were already in a block, adding
            # lines or not, we're not doing that any more
            last_add = False

            # add a comment giving the line being removed
            r.append(indent + "!- " + prefix + text)

    # return the resulting list of lines
    return r



# --- other functions ---



# regular expression for matching physical interface names
#
# note that it will only match interfaces of the form
# "<type><num>[/<num2>[/<num3>[/...]]]" and this excludes subinterfaces,
# where the final number with have a dot in it

_INTERFACE_PHYSICAL_RE = re.compile("^(Mgmt|Eth|Fa|Gi|Te|Twe|Fo|Hu)\d+(/\d+)*$",
                                    re.IGNORECASE)


def is_int_physical(i):
    """This function returns if a particular interface is physical or
    not.  The names it matches are those that the are used as the
    canonical ones in the parser.

    The purpose of this function is primarily to work out if an
    interface can be deleted with "no interface ..." so excludes
    subinterfaces of physical interfaces.
    """

    return _INTERFACE_PHYSICAL_RE.match(i)
