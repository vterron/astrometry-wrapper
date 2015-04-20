#! /usr/bin/env python

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy import units

import functools
import os
import re
import warnings

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

def _get_coordinates(header, rak, deck):
    """ Read the celestial coordinates from a FITS header.

    Return an astropy.coordinates.SkyCoord object with the right ascension and
    declination read from the specified FITS keywords. If both coordinates are
    not in decimal degrees, they are assumed to be in sexagesimal (hour angles
    and degrees, respectively).

    """

    ra  = str(header[rak])
    dec = str(header[deck])
    coords = functools.partial(SkyCoord, ra, dec)

    regexp = "\d{1,3}\.?\d"
    match_degrees = functools.partial(re.match, regexp)
    if match_degrees(ra) and match_degrees(dec):
        return coords(unit=(units.deg, units.deg))

    # Assume (at least for now) that it's in sexagesimal
    return coords(unit=(units.hourangle, units.deg))

def solve(path, rak = 'RA', deck = 'DEC', radius = 1):
    """ A convenience function to solve images without thinking.

    This is a convenience wrapper around solve-field, Astrometry.net's main
    high-level command-line user interface. There are no parameters to tweak,
    neither nothing written to standard output or error: Astrometry.net just
    runs silently, returning the path to a temporary copy of the input image
    with the WCS solution added to its FITS header.

    In order to speed up solve-field as much as possible, the search is
    restricted to those indexes within 'radius' degrees of the field center,
    via the 'rak' and 'deck' FITS keywords. These two keywords are expected to
    contain the right ascension and declination of the center of the image. A
    warning is emitted if they are set to a value other than None but they do
    not contain anything that can be interpreted as celestial coordinates.

    """

    options = dict()

    if None not in (rak, deck):

        hdulist = fits.open(path)
        header = hdulist[0].header

        try:
            coords = _get_coordinates(header, rak, deck)
            options['ra']  = coords.ra.degree
            options['dec'] = coords.dec.degree
            options['radius'] = radius

        except KeyError as e:
            options.clear()
            msg = ("{0}: could not read field center coordinates from FITS "
                   "header ({1}); solve-field will run blindly".format(
                       path, str(e)))
            warnings.warn(msg)

    with open(os.devnull, 'wb') as fd:
        return commands.solve_field(path,
                                    stdout=fd,
                                    stderr=fd,
                                    **options)
