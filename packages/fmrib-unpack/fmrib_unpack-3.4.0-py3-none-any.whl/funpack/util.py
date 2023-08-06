#!/usr/bin/env python
#
# util.py - Miscellaneous utility functions.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains a collection of miscellaneous utility functions,
classes, and constants.
"""


import                    os
import                    re
import                    sys
import                    enum
import                    site
import                    time
import                    shutil
import                    logging
import                    warnings
import                    functools
import                    contextlib
import itertools       as it
import os.path         as op
import subprocess      as sp
import multiprocessing as mp

import numpy           as np

# The stdlib resource module is only
# available on unix-like platforms.
try:
    import resource
except ImportError:
    resource = None


log = logging.getLogger(__name__)


CTYPES = enum.Enum(
    'CTYPES',
    ['sequence',
     'integer',
     'continuous',
     'categorical_single',
     'categorical_single_non_numeric',
     'categorical_multiple',
     'categorical_multiple_non_numeric',
     'time',
     'date',
     'text',
     'compound',
     'unknown'])
"""The ``CTYPES`` enum defines all the types that ``funpack`` is aware of.
"""


DATA_TYPES = {

    # We have to use floating point for
    # integer types because pandas uses
    # nan to represent missing data.
    CTYPES.integer                          : np.float32,
    CTYPES.continuous                       : np.float32,
    CTYPES.categorical_single               : np.float32,
    CTYPES.categorical_multiple             : np.float32,
    CTYPES.sequence                         : np.uint32,
    CTYPES.categorical_single_non_numeric   : str,
    CTYPES.categorical_multiple_non_numeric : str,
    CTYPES.text                             : str,
    CTYPES.compound                         : str,
}
"""Default internal data type to use for the different variable types.
Used by the :func:`columnTypes` function. These types may be overridden
by the ``InternalType`` column of the variable table, which is populated
from the ``funpack/data/type.txt`` file (see :func:`.loadTableBases`).
"""


def parseColumnName(name):
    """Parses a UK Biobank column name, returns the components.

    Two column naming formats are supported. The name is expected to be
    a string of one of the following forms::

        variable-visit.instance
        variable.instance
        f.variable.visit.instance

    where ``variable`` and ``visit`` are integers. ``instance`` is typically
    also an integer, but non-numeric values for ``instance`` are
    accepted. This (and the second form above) is to allow parsing of derived
    columns (see e.g. the :func:`.processing_functions.binariseCategorical`
    processing function).

    Some variables have the form::

        f.variable..visit.instance

    For these variables, the visit is interpreted as a negative number.

    If ``name`` does not have one of the above forms, a :exc:`ValueError` is
    raised.

    .. note:: For the vast majority of biobank variables, the second number in
              a column name (``visit`` above) corresponds to the assessment
              visit. However, there are a small number of variables which are
              not associated with a specific visit, and thus for which this
              number does not correspond to a visit (e.g. variable 40006), but
              to some other coding.

              Confusingly, the UK Biobank showcase refers to the coding that a
              variable adheres to as an "instancing", whilst also using the
              term "instance" to refer to the columns of multi-valued
              variables - the ``instance`` element of the column name.

              The "instancing" that a variable uses is contained in the
              ``Instancing`` column of the variable table. Variables for which
              the ``visit`` component of their column names do correspond
              to an actual visit have an instancing equal to 2.

    :arg name: Column name
    :returns:  A tuple containing:

                - variable ID
                - visit number
                - instance (may be an integer or a string)
    """

    def parse_norm(grps):
        vid      = int(grps[0])
        visit    = int(grps[2])
        instance =     grps[3]
        if grps[1] is not None:
            visit = -visit
        return vid, visit, instance

    def parse_deriv(grps):
        vid      = int(grps[0])
        instance =     grps[1]
        return vid, 0, instance

    patterns = [
        (r'([0-9]+)-(-)?([0-9]+)\.(.+)',          parse_norm),
        (r'([0-9]+)\.(.+)',                       parse_deriv),
        (r'f\.([0-9]+)\.(\.)?([0-9]+)\.([0-9]+)', parse_norm)
    ]

    for pat, parse in patterns:

        pat   = re.compile(pat)
        match = pat.fullmatch(name)

        if match is None:
            continue

        vid, visit, instance = parse(match.groups())

        # accept numeric/non-numeric instance
        try:
            instance = int(instance)
        except ValueError:
            pass

        break

    if match is None:
        raise ValueError('Invalid column name: {}'.format(name))

    return (vid, visit, instance)


def generateColumnName(variable, visit, instance):
    """Generate a column name for the given variable, visit and instance.

    :arg variable: Integer variable ID
    :arg visit:    Visit number
    :arg instance: Instance number
    """
    return '{}-{}.{}'.format(variable, visit, instance)


def findConfigDir(dirname='configs'):
    """Returns the first entry from ``findConfigDirs``. If
    ``$FUNPACK_CONFIG_DIR`` is set, it will be returned. Otherwise, it will
    be the location of the `funpack/configs/` directory as described in
    :func:`findConfigDirs`.
    """
    return findConfigDirs(dirname)[0]


def findConfigDirs(dirname='configs'):
    """Returns a list of candidate FUNPACK configuration directories.

    The FUNPACK FMRIB configuration installs its config/table files into
    ``<python>/lib/python<X.Y>/site-packages/funpack/configs/``. If
    FUNPACK is installed into that Python environment, this directory
    will be alongside the FUNPACK source code.

    However, if FUNPACK is being executed from a source checkout, we have to
    use ``site.getsitepackages`` to find the location of the config directory.

    The ``dirname`` argument may also be set to ``plugins``, in which case the
    path to the ``funpack.plugins`` module will be returned.

    The ``$FUNPACK_CONFIG_DIR`` environment variable can also be used to
    point to a configuration directory - if set, the returned list will include
    ``$FUNPACK_CONFIG_DIR/`` at the beginning.

    A ``RuntimeError`` is raised if the config directory cannot be found.
    """
    # The user can refer to "built-in" config
    # files just by giving a file path
    # with/without suffix, relative to one of
    # the following locations (in order of
    # precedence):
    #
    #   - in $FUNPACK_CONFIG_DIR, or
    #   - if we are running from a git checkout, installed in the running
    #     python env (<pyenv>/lib/pythonX.Y/site-packages/funpack/configs/), or
    #   - within the funpack package directory, (<thisdir>/configs/)

    cfgdirs    = []
    candidates = []

    if 'FUNPACK_CONFIG_DIR' in os.environ:
        candidates.append(os.environ['FUNPACK_CONFIG_DIR'])
    candidates.extend(op.join(sitedir, 'funpack', dirname)
                      for sitedir in site.getsitepackages())
    candidates.append(op.join(op.dirname(__file__), dirname))

    for candidate in candidates:
        if op.isdir(candidate):
            cfgdirs.append(candidate)

    if len(cfgdirs) == 0:
        raise RuntimeError('Cannot find FUNPACK configuration directory!')

    return cfgdirs


def findTableFile(filename):
    """Searches for a FUNPACK table tile - see :func:`findConfigFile`. """
    return findConfigFile(filename, '.tsv')


def findPluginFile(filename):
    """Searches for a FUNPACK plugin tile - see :func:`findConfigFile`. """
    return findConfigFile(filename, '.py', dirname='plugins')


def findConfigFile(filename, suffix='.cfg', dirname='configs'):
    """Searches for a FUNPACK configuration file in a number of locations.

    :arg filename: Name of file to search for
    :arg suffix:   Suffix to append, if the filename is specfied without one
                   (must include the leading period).
    :arg dirname:  Name of internal/built-in directory to search - assumed to
                   be within the ``funpack`` package directory, e.g.
                   ``funpack/configs/``.
    :returns:      Absolute path to the found file, or ``filename`` unmodified
                   if a match was not found.
    """

    # Make things easier for users of this function
    if filename is None:
        return filename

    # Suffix is just appended straight onto the
    # file name, so empty string is a no-op
    if suffix is None:
        suffix = ''

    # config files may be absolute / relative
    # paths to an arbitrary location
    if op.isfile(filename):
        return op.abspath(filename)

    cfgdirs = findConfigDirs(dirname)

    # Built-in config files can be specified
    # with (in order of precedence):
    #
    #  - file path with suffix (e.g. "fmrib/categories.tsv")
    #  - file path without suffix (e.g. "fmrib/categories")
    #  - file path without suffix, with dots instead of slashes
    #    (e.g. "fmrib.categories")
    candidates = [filename,
                  f'{filename}{suffix}',
                  f'{filename.replace(".", op.sep)}{suffix}']

    for cfgdir, cand in it.product(cfgdirs, candidates):
        cand = op.abspath(op.join(cfgdir, cand))
        if op.isfile(cand):
            return cand

    # Can't find the file - return the
    # path unmodified, which will result
    # in an error at some other point.
    return filename


def parseMatlabRange(r):
    """Parses a string containing a MATLAB-style ``start:stop`` or
    ``start:step:stop`` range, where the ``stop`` is inclusive).

    :arg r:   String containing MATLAB_style range.
    :returns: List of integers in the fully expanded range.
    """
    elems = [int(e) for e in r.split(':')]

    if len(elems) == 3:
        start, step, stop = elems
        if   step > 0: stop += 1
        elif step < 0: stop -= 1

    elif len(elems) == 2:
        start, stop  = elems
        stop        += 1
        step         = 1
    elif len(elems) == 1:
        start = elems[0]
        stop  = start + 1
        step  = 1
    else:
        raise ValueError('Invalid range string: {}'.format(r))

    return list(range(start, stop, step))


def dedup(seq):
    """Remove duplicates from a sequence, preserving order.
    Returns a list.
    """
    newseq = []
    for i in seq:
        if i not in newseq:
            newseq.append(i)
    return newseq


def wc(fname):
    """Uses ``wc`` to count the number of lines in ``fname``.

    :arg fname: Name of the file to check
    :returns:   Number of lines in ``fname``.
    """

    with timed('Row count', log):
        if shutil.which('wc'):
            nrows = sp.check_output(['wc', '-l', fname]).split()[0]
        else:
            nrows = 0
            with open(fname) as f:
                for _ in f:
                    nrows = nrows + 1
    return int(nrows)


def cat(files, outfile):
    """Uses ``cat`` to concatenate ``files``, saving the output to ``outfile``.

    :arg files:   Sequence of files to concatenate.
    :arg outfile: Name of file to save output to.
    """
    with timed('Concatenate files', log):
        if shutil.which('cat'):
            with open(outfile, 'w') as outf:
                cmd = ['cat'] + list(files)
                sp.run(cmd, check=True, stdout=outf)
        else:
            with open(outfile, 'w') as outf:
                for infile in files:
                    with open(infile, 'r') as inf:
                        while True:
                            buf = inf.read(16777216)
                            if buf:
                                outf.write(buf)
                            else:
                                break


def inMainProcess():
    """Returns ``True`` if the running process is the main (parent) process.
    Returns ``False`` if the running process is a child process (e.g. a
    ``multiprocessingg`` worker process).
    """
    return mp.current_process().pid == inMainProcess.pid


# Save the main process
# ID, so inMainProcess
# can compare against it
inMainProcess.pid = mp.current_process().pid



@contextlib.contextmanager
def timed(op=None, logger=None, lvl=None, fmt=None):
    """Context manager which times a section of code, and prints a log
    message afterwards.

    :arg op:      Name of operation which is being timed

    :arg logger:  Logger object to use - defaults to :attr:`log`.

    :arg lvl:     Log level - defaults to ``logging.INFO``.

    :arg fmt:     Custom message. If not provided, a default message is used.
                  Must be a ``'%'``-style format string which accepts two
                  parameters: the elapsed time (``%s``), and the memory usage
                  (``%i``)..
    """

    if fmt is None:
        fmt = '[{}] completed in %s (%+iMB)'.format(op)

    if logger is None:
        logger = log

    if lvl is None:
        lvl = logging.INFO

    if op is not None:
        logger.log(lvl, 'Running task [%s]', op)

    # ru_maxrss appears to be bytes under
    # macos, and kilobytes under linux
    if sys.platform == 'darwin': memdenom = 1048576.0
    else:                        memdenom = 1024.0

    if resource is not None:
        startmem  = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    else:
        startmem = 0

    starttime = time.time()

    yield

    endtime = time.time()

    if resource is not None:
        endmem  = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    else:
        endmem = 0

    hours   = int( (endtime - starttime) / 3600)
    minutes = int(((endtime - starttime) % 3600) / 60)
    seconds = int(((endtime - starttime) % 3600) % 60)
    timestr = '{:d} seconds'.format(seconds)

    if minutes > 0: timestr = '{} minutes, {}'.format(minutes, timestr)
    if hours   > 0: timestr = '{} hours, {}'  .format(hours,   timestr)

    mbytes = (endmem - startmem) / memdenom

    if minutes: logger.log(lvl, fmt, timestr, mbytes)
    else:       logger.log(lvl, fmt, timestr, mbytes)


def deprecated(message):
    """Decorator used to mark a function or method as deprecated """

    def wrapper(func):

        warnings.filterwarnings('default', category=DeprecationWarning)

        def decorator(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return functools.update_wrapper(decorator, func)

    return wrapper


class Singleton:
    """Manages a reference to a single instance of a class.

    This is not a true singleton - there are no restrictions against multiple
    instances being created. However, a reference is only held to the first
    created instance.

    The ``Singleton`` class is used as the base class for :class:`.DataTable`,
    to allow for shared-memory access to the ``DataTable`` by worker processes.
    """


    def __new__(cls, *args, **kwargs):
        """Create a new instance and save a ref to it, if one does not yet
        exist.
        """
        new = super().__new__(cls)

        if Singleton.instance() is None:
            Singleton.setInstance(new)

        return new


    @classmethod
    def instance(cls):
        """Return a reference to the singleton instance, or ``None`` if one
        does not exist.
        """
        return getattr(cls, '_{}_singleton'.format(cls.__name__), None)


    @classmethod
    def setInstance(cls, inst):
        """Set/override the singleton instance. """
        setattr(cls,  '_{}_singleton'.format(cls.__name__), inst)
