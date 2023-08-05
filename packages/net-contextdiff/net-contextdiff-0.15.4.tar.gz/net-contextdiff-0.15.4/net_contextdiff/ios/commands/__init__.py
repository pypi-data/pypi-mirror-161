# ios.commands
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



"""Cisco IOS configuration commands module.

This module parses Cisco IOS configuration files into a dictionary.
"""



from .interface import *
from .lists import *
from .other import *
from .router import *

from ...misc import get_all_subclasses



# commands is the list of commands to add to the parser - it is all
# subclasses of Cmd (IndentedContextualCommand) which have the 'match'
# attribute defined
#
# the CiscoIOSConfig class adds these to the object upon instantiation,
# by the _add_commands() method.

commands = [ c for c in get_all_subclasses(IndentedContextualCommand)
                 if c.match is not None ]
