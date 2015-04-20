#! /usr/bin/env python

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import shutil
import subprocess
import tempfile
import textwrap

ASTROMETRY_COMMAND = 'solve-field'

class AstrometryNetUnsolvedField(subprocess.CalledProcessError):
    """ Raised if Astrometry.net could not solve the field """

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "{0}: could not solve field".format(self.path)

def _check_installation():
    """ Check whether Astrometry.net is installed. """

    kwargs = dict(
        initial_indent=" " * 11,
        subsequent_indent=" " * 11,
        width=72
        )

    error_wrap = textwrap.TextWrapper(**kwargs)

    ASTROMETRY_MISSING = """
    ERROR: Astrometry.net commands could not be found.

    In order to use the astrometry_wrapper module, you will first need to
    download, build and install the Astrometry.net software from:

        http://astrometry.net/

    and ensure that the Astrometry.net commands (e.g. solve-field, backend,
    augment-xylist, etc.) are in your $PATH. Your current $PATH variable
    contains the following paths, but none of them contain the Astrometry.net
    commands:

        PATH = {path}

    If the Astrometry.net commands are in one of these directories, then please
    report this as an issue with astrometry-wrapper.
    """.format(path=error_wrap.fill(os.environ['PATH']).strip())

    for dir_ in os.environ['PATH'].split(':'):
        if os.path.exists(dir_ + '/solve-field'):
            installed = True
            break

    else:
        print(ASTROMETRY_MISSING)
        import sys
        sys.exit(1)

def solve_field(path):
    """ Do astrometry on a FITS image using a local build of Astrometry.net.

    Use a local build of the Astrometry.net software [1] in order to compute
    the astrometric solution of a FITS image. Returns the path to a temporary
    file containing a copy of the input FITS image with the WCS solution. If
    Astrometry.net is unable so solve the image, AstrometryNetUnsolvedField
    is raised.

    In order for this function to work, you must have built and installed the
    Astrometry.net code in your machine [2]. The main high-level command-line
    user interface, 'solve-field', is expected to be available in your PATH;
    otherwise, an error is raised. You also need to download the appropriate
    index files [3], which are considerably heavy. At the time of this writing,
    the entire set of indexes built from the 2MASS catalog [4] has a total size
    of ~32 gigabytes.

    [1] http://astrometry.net/
    [2] http://astrometry.net/doc/build.html
    [3] http://astrometry.net/doc/readme.html#getting-index-files
    [4] http://data.astrometry.net/4200/

    """

    _check_installation()

    basename = os.path.basename(path)
    root, ext = os.path.splitext(basename)
    # Place all output files in this directory
    kwargs = dict(prefix = root + '_', suffix = '_astrometry.net')
    output_dir = tempfile.mkdtemp(**kwargs)

    # Path to the temporary FITS file containing the WCS header
    kwargs = dict(prefix = '{0}_astrometry_'.format(root), suffix = ext)
    with tempfile.NamedTemporaryFile(**kwargs) as fd:
        output_path = fd.name

    # If the field solved, Astrometry.net creates a <base>.solved output file
    # that contains (binary) 1. That is: if this file does not exist, we know
    # that an astrometric solution could not be found.
    solved_file = os.path.join(output_dir, root + '.solved')

    # --dir: place all output files in the specified directory.
    # --no-plots: don't create any plots of the results.
    # --new-fits: the new FITS file containing the WCS header.
    # --no-fits2fits: don't sanitize FITS files; assume they're already valid.
    # --overwrite: overwrite output files if they already exist.

    args = [ASTROMETRY_COMMAND, path,
            '--dir', output_dir,
            '--no-plots',
            '--new-fits', output_path,
            '--no-fits2fits',
            '--overwrite']

    try:
        subprocess.check_call(args)

        # .solved file must exist and contain a binary one
        with open(solved_file, 'rb') as fd:
            if ord(fd.read()) != 1:
                raise AstrometryNetUnsolvedField(path)

        return output_path

    except subprocess.CalledProcessError as e:
        raise e
    # If .solved file doesn't exist or contain one
    except (IOError, AstrometryNetUnsolvedField):
        raise AstrometryNetUnsolvedField(path)
    finally:
        shutil.rmtree(output_dir)
