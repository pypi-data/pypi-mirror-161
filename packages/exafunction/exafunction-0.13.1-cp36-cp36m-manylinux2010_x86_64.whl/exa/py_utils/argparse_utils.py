# Copyright Exafunction, Inc.

""" Utility classes for argparse """

import argparse


# This is for compatibility with Python 3.6/3.7
# This needs to be registered on every parser and subparser that uses it.
class ExtendAction(argparse.Action):
    """Reimplementation of the "extend" action"""

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        items.extend(values)
        setattr(namespace, self.dest, items)
