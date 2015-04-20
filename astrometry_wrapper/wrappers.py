#! /usr/bin/env python

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import .commands

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
