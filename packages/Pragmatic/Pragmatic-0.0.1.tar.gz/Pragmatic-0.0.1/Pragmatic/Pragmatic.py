# -*- coding: ascii -*-


"""Pragmatic.Pragmatic: provides entry point main()."""


__version__ = "0.0.1"


import sys
from .Stuff import Stuff


def Main():
	print("Executing bootstrap version %s." % __version__)
	print("List of argument strings: %s" % sys.argv[1:])
	print("Stuff and Boo():\n%s\n%s" % (Stuff, Boo()))


class Boo(Stuff):
	pass