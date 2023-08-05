NET-CONTEXTDIFF
===============

This package contains two main elements used to compare text-based
configuration files (or other files in simple text in a similar format) where
they are structured using indented blocks of directives/commands, typically for
network devices:

* a parser to read in configuration files and stored them in a dictionary --
  the parser utilises the hierarchical nature of the configuration to
  understand that the same command name might mean different things in
  different contexts

* a comparator that takes two configuration dictionaries (typically produced by
  the parser, above) - a source and a target configuration - and writes out
  a configuration file (or update command set) to transform the source
  configuration into the destination - this uses a series of 'converters' to
  handle the difference for each configuration element (e.g. changing the
  description assigned to an interface)

Each of these are written as abstract base classes that can be inherited from
to crete concrete classes for each platform, but the base processing of the
parsing and comparing should be consistent, requiring only the specific
commands to be handled.

Currently, Cisco IOS is the only concrete platform and only a subset so far
(the comparator is still being tweaked to handle this all relatively
straightforwardly, before all the commands are implemented).  There are
currently some odd commands and edge cases which are awkward to handle without
some improvements to the core process.

The scripts also support a system whereby 'excludes' can be specified, to
exclude those elements of the configuration dictionary which should not be
compared, if a known difference exists that cannot be resolved, either as an
interim divergence, or a permanent exception.
