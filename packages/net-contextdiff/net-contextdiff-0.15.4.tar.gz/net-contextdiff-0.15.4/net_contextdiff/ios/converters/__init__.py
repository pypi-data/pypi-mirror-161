# ios.converters
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



"""Cisco IOS configuration converters module.

This module contains the converters to change individual configuration
elements of a Cisco IOS configuration into another.
"""



from .interface import *
from .lists import *
from .other import *
from .router import *

from ...misc import get_all_subclasses



# the converters are all subclasses of DiffConvert which have the 'cmd'
# attribute defined
#
# CiscoIOSDiffConfig._add_converters() adds these into the list of
# converter classes

converters = [ c for c in get_all_subclasses(DiffConvert) if c.cmd is not None ]
