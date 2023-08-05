# net_contextdiff.__main__


# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>
#
# This script compares Cisco IOS configuration files and outputs a
# configuration file which will convert the former into the latter.



from net_contextdiff import __version__

import argparse
import sys

from deepops import deepmerge, deepget
import yaml

from net_contextdiff.ios import CiscoIOSConfig, CiscoIOSDiffConfig
from net_contextdiff.misc import deepselect



# --- constants ---



# PLATFORMS = dict
#
# This dictionary specifies the available platforms available to compare
# configurations in.  The dictionary is keyed on the user-specified platform
# name and specifies two values in a tuple, giving the object classes to be
# used for that platform: the first is the parser an the second is the
# difference comparator.

PLATFORMS = {
    "ios": (CiscoIOSConfig, CiscoIOSDiffConfig)
}



# --- functions ---



def diffconfig(diff, devicename, old_filename, new_filename, output_filename,
               no_output, dump_rules, debug_parser, debug_convert):

    """This function compares the old and new configurations for the
    specified device and writes a difference configuration file (one
    that transforms the configuration of a running device from the old
    to the new state).

    The filenames for the configuration files, as well as the output
    are taken from the arguments parsed above and stored in global
    variables used directly by this function.

    The function returns True iff the parsing and comparison succeeded.
    Most problems result in the function aborting with an exception,
    but some minor warnings may be ignored and the program continue
    with devices.

    Keyword arguments:

    diff -- the DiffConfig object to do the convert the configuration

    devicename -- the name of the device being converted, or None if
    it's not known

    old_filename -- filename of the source configuration

    new_filename -- filename of the target configuration

    output_filename -- name of the file to write the conversion
    configuration to or None for standard output

    no_output -- a boolean set to True iff no output file is to be
    written

    dump_rules, debug_parser, debug_convert -- the equivalent
    variables to command line arguments
    """


    # reset the rules list for this conversion - this is the same
    # list each time, except the devicename changes and may cause
    # some of the rules to change

    diff.init_rules_active()
    diff.add_rules_active(rule_specs, devicename)

    if dump_rules >= 2:
        num = 0
        for spec, tree in diff.get_rules():
            print(">> rule num: %d spec: %s" % (num, spec))
            print(yaml.dump(tree, default_flow_style=False)
                        if tree else "<none>\n", sep="\n")

            num += 1


    # read in the old and new configurations

    from_cfg = config_parser_class(filename=old_filename, debug=debug_parser)

    to_cfg = (config_parser_class(filename=new_filename, debug=debug_parser)
                  if new_filename else None)


    # find the differences

    diffs, diffs_tree = diff.convert(from_cfg, to_cfg)


    # if output is suppressed, just stop with success here

    if no_output:
        return diffs_tree


    # write the differences to a file or standard output

    if output_filename:
        if debug_convert:
            print("debug: writing to output file:", output_filename)

        with open(output_filename, "w") as output_file:
            if diffs:
                print(diffs, file=output_file)

    else:
        if debug_convert:
            print("debug: writing to standard output")

        if diffs:
            print(diffs)


    return diffs_tree



# --- command line arguments ---



# create the parser and add in the available command line options

parser = argparse.ArgumentParser(
    # override the program name as running this as a __main__ inside a module
    # directory will use '__main__' by default - this name isn't necessarily
    # correct, but it looks better than that
    prog="net-contextdiff",

    # we want the epilog help output to be printed as it and not reformatted or
    # line wrapped
    formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument(
    "-r", "--rules-tree-filename",
    metavar="FILENAME",
    help="read rules data from a YAML file (assumed to be an "
         "'excludes' list by default - see -s option)")

parser.add_argument(
    "-s", "--rule-spec",
    metavar="PATH",
    action="append",
    default=[],
    help="add a rule to the rules list; rules are in the form '!path' "
         "and processed in order: '!' excludes the specified items and "
         "omitting it includes ONLY the specified items; the 'path' is "
         "a dictionary path, with keys separated by colons; the path "
         "is into the file read with -r; default can be viewed with "
         "-R option)")

parser.add_argument(
    "-e", "--explain",
    action="store_true",
    help="explain which converter paths match a configuration change")

parser.add_argument(
    "-q", "--quiet",
    action="store_true",
    help="when generating configuration for multiple devices, don't "
         "print the name of each device, as it's generated")

parser.add_argument(
    "-O", "--no-output",
    action="store_true",
    help="do not write changes output file - used to test parsing, "
         "exclude and conversion process")

parser.add_argument(
    "-R", "--dump-rules",
    action="count",
    default=0,
    help="dump the tree of items to be included and excluded from the "
         "comparisons, based on the rules (multiple levels increase "
         "verbosity up to a maximum of 2)")

parser.add_argument(
    "-C", "--dump-config",
    action="store_true",
    help="dump the configuration dictionary after parsing")

parser.add_argument(
    "-D", "--dump-diff",
    action="store_true",
    help="dump the difference (removes and updates) between the from "
         "and to configurations")

parser.add_argument(
    "-T", "--dump-diff-tree",
    action="store_true",
    help="dump the differences across all compared files as a YAML "
         "tree - this is useful for using in an exclude file")

parser.add_argument(
    "-S", "--subtree-dump-filter",
    metavar="key",
    nargs="*",
    default=[],
    help="limit dump options to subtree of configuration dictionary "
         "with a path specified as list of keys; '-' can be used to "
         "represent None and values that are parsable as integers will "
         "be converted to integers")

parser.add_argument(
    "-P", "--debug-parser",
    action="count",
    default=0,
    help="increase debugging of contextual parsing (multiple uses "
         "increase verbosity up to a maxmimum of 3)")

parser.add_argument(
    "-V", "--debug-convert",
    action="count",
    default=0,
    help="increase debugging of the difference converstion action "
         "processing (multiple uses increase verbosity up to a "
         "maximum of 4)")

parser.add_argument(
    "platform",
    choices=PLATFORMS,
    help="platform used for configuration files")

parser.add_argument(
    "old_filename",
    metavar="old",
    help="source (old / 'from') configuration file; '%%' can be used "
         "to substitute in the name of the device into the filename")

parser.add_argument(
    "new_filename",
    nargs="?",
    default=None,
    metavar="new",
    help="target (new / 'to') configuration file; '%%' can be used to "
         "substitute in the name of the device into the filename; if "
         "omitted just parse the file and assume 'debug' mode")

parser.add_argument(
    "output_filename",
    nargs="?",
    metavar="output",
    help="write differences configuration to named file instead of "
         "stdout; '%%' can be used to substitute in the name of the "
         "device into the filename")

parser.add_argument(
    "devicenames",
    metavar="devicename",
    nargs="*",
    help="name(s) of the device(s) to calculate differences in the "
         "configuration for")

parser.add_argument(
    "-v", "--version",
    action="version",
    version=("%(prog)s " + __version__))


# parse the supplied command line against these options, storing the results

args = parser.parse_args()

config_parser_class, config_diff_class = PLATFORMS[args.platform]

rules_tree_filename = args.rules_tree_filename
rule_specs = args.rule_spec
explain = args.explain
quiet = args.quiet
no_output = args.no_output
dump_rules = args.dump_rules
dump_config = args.dump_config
dump_diff = args.dump_diff
dump_diff_tree = args.dump_diff_tree
subtree_dump_filter = args.subtree_dump_filter
debug_parser = args.debug_parser
debug_convert = args.debug_convert
old_filename = args.old_filename
new_filename = args.new_filename
output_filename = args.output_filename
devicenames = args.devicenames


# if the rule specifications were not specified, assume this set by
# default (we can't add_argument(default=...) option because the
# 'action="append"' option just adds user-specified items to it)

if not rule_specs:
    rule_specs = [
        "!rules:exclude:ALL",
        "!rules:exclude:%",
        "rules:include:ALL",
        "rules:include:%",
    ]


# if a subtree was specified for debugging 'dump' options, handle some
# special cases of the elements in the path:
#
# * a single dash ('-') is treated as None
#
# * if the element can be converted to an integer, do that, rather than
#   treat it as a string
#
# these are to cope with limitations on the parsing available in the
# ArgumentParser class compared with the flexibility and ambiguity of
# the configuration dictionary

if subtree_dump_filter:
    def try_int_else_str(s):
        "Convert a single path element from a string into another type."

        if s == "-":
            return None

        try:
            return int(s)
        except ValueError:
            pass

        return s

    subtree_dump_filter = [ try_int_else_str(s) for s in subtree_dump_filter]

    print(subtree_dump_filter)


# check a couple of nonsensical configurations aren't being use related
# to multiple devices

if not len(devicenames):
    if old_filename.find("%") != -1:
        print("error: no device names specified, so operating on a single "
              "file, yet old filename has '%' character",
              file=sys.stderr)

        exit(1)


    if new_filename and (new_filename.find("%") != -1):
        print("error: no device names specified, so operating on a single "
              "file, yet new filename has '%' character",
              file=sys.stderr)

        exit(1)


    if output_filename and (output_filename.find("%") != -1):
        print("error: no device names specified, so operating on a single "
              "file, yet 'output' filename has '%' character",
              file=sys.stderr)

        exit(1)


elif len(devicenames) > 1:
    if old_filename.find("%") == -1:
        print("warning: multiple device names specified but old filename "
              "does not contain '%' - same file will be read",
              file=sys.stderr)

    if new_filename and (new_filename.find("%") == -1):
        print("warning: multiple device names specified but new filename "
              "does not contain '%' - same file will be read",
              file=sys.stderr)


    if not output_filename:
        print("warning: multiple device names specified but outputting to "
              "standard output - all configurations will be concatenated",
              file=sys.stderr)

    elif output_filename.find("%") == -1:
        print("error: multiple device names specified but 'output' filename "
              "does not contain '%' - same file would be overwritten",
              file=sys.stderr)

        exit(1)



# --- setup ---



# create the diff object once at the start

diff = config_diff_class(
           explain, dump_config, dump_diff, debug_convert, subtree_dump_filter)


# if a rules tree file was specified, read that in

if rules_tree_filename:
    diff.add_rules_tree_file(rules_tree_filename)


# dump the rule tree, if debugging enabled for it (this will include any
# rules included by default, in the class)

if dump_rules >= 1:
    print(">> rule tree:")
    print(yaml.dump(deepselect(diff.get_rules_tree(), *subtree_dump_filter),
                    default_flow_style=False))
    print(">> rule specs:")
    for spec in rule_specs:
        print("->", spec)

    print()



# --- compare ---



# if we have a list of device names (even just one), we iterate through
# them, else we just process the one file we've been given

if devicenames:
    # initialise the tree of aggregated differences across al the
    # compared configuration files

    all_diffs_tree = {}


    for devicename in devicenames:
        if not quiet:
            print(devicename)


        # do the actual conversion

        diffs_tree = diffconfig(
                      diff, devicename,
                      old_filename.replace("%", devicename),
                      new_filename.replace("%", devicename),
                      output_filename.replace("%", devicename),
                      no_output, dump_rules, debug_parser,
                      debug_convert)


        # add the differences in this conversion to the aggregate tree

        deepmerge(all_diffs_tree, diffs_tree)


else:
    all_diffs_tree = diffconfig(
        diff, None, old_filename, new_filename, output_filename, no_output,
        dump_rules, debug_parser, debug_convert)


# if the option to enable dumping of the differences tree is enabled, do
# that

if dump_diff_tree:
    print("=> differences tree:")
    print(yaml.dump(all_diffs_tree, default_flow_style=False))


exit(0)
