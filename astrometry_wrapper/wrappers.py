#! /usr/bin/env python

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from . import commands

def find_sources(path, type = 'fits'):
    """ Detect astronomical objects in a FITS image. """

    types = 'fits', 'plain', 'numpy'
    if type.lower() not in (types):
        msg = "'type' must be one of {0}".format('|'.join(types))
        raise ValueError(msg)

    sources_table = commands.image2xy(path)
    if type == 'fits':
        return sources_table

    try:

        if type == 'plain':
            raise NotImplementedError
            # [TODO] Read to a temporary plain-text file, return its path

        else:
            assert type == 'numpy'
            raise NotImplementedError
            # [TODO] Return into a NumPy array, return its path

    finally:
        os.unlink(sources_table)

def solve(path):
    """ A convenience function to solve images without thinking.

    This is a convenience wrapper around solve-field, Astrometry.net's main
    high-level command-line user interface. There are no parameters to tweak,
    neither nothing written to standard output or error: Astrometry.net just
    runs silently, returning the path to a temporary copy of the input image
    with the WCS solution added to its FITS header.

    """

    with open(os.devnull, 'wb') as fd:
        return commands.solve_field(path, stdout=fd, stderr=fd)
