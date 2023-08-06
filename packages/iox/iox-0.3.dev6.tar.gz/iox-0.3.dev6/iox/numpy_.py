
from fileinput import input as input_
import logging
import numpy as np
from pathogen import vglob

# Establish logger
_logger = logging.getLogger('iox.numpy')


# Globular loadtxt
def loadtxt(fname, glob=None, verbose=False, **kwargs):
    """
    A refactoring of :func:`numpy.loadtxt` that allows for globbing files.

    If there are no glob variables, then result of glob will be sorted. If there are glob variables, then they will
    be in order as defined. See :func:`pathogen.vglob` for more information.

    Parameters
    ----------
    fname : file, str, or pathlib.Path
        Name of file.
    glob : bool or dict
        Does `fname` need to be globbed? This uses Pathogen's `vglob` function.
        (Default: None)
    verbose : bool
        Should information about the read-in be displayed?
    **kwargs
        Optional keyword parameters to pass to :func:`numpy.loadtxt`.

    Returns
    -------
    pandas.Series
        Read file
    """

    # If glob, change fname to include all globbed files
    if glob:
        # Convert glob to a empty dictionary if necessary
        if not isinstance(glob, dict):
            glob = {}

        # Glob first; if glob is empty, throw an error
        fname_glob = vglob(fname, errors='raise', **glob)
        if not fname_glob:
            raise FileNotFoundError(fname)

        # Sort glob as long as there are no glob variables
        if len(glob) == 0:
            fname_glob = sorted(fname_glob)

        # Output if verbose
        if verbose:
            print(f'glob: {list(fname_glob)}')

        # Update fname to include all globbed files
        fname = input_(fname_glob)

    # Utilize numpy to read-in the file(s)
    data = np.loadtxt(fname, **kwargs)

    # If verbose, note the shape of the data
    if verbose:
        print(f'file loaded with shape {data.shape}')

    # Return
    return data
