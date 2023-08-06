
from functools import partial
import logging
import numpy as np
import pandas as pd
from pathogen import Path, vglob
import time

# Establish logger
_logger = logging.getLogger('iox.pandas')


def create_index(df, by=None, sort=False):
    """
    https://stackoverflow.com/a/60080363

    Parameters
    ----------
    df : pandas.DataFrame
    by : str or list
    sort : bool

    Returns
    -------
    numpy.array
    """

    if by is not None:
        if sort:
            df.sort_values(by, inplace=True)
        # n_unique = len(df[by].drop_duplicates())
        return df.groupby(by, sort=False).cumcount(ascending=True).to_numpy()
    else:
        # n_unique = 1
        return np.arange(len(df))

    # return np.tile(np.arange(len(df) / n_unique, dtype='int'), n_unique)


# This is a placeholder for now... it might change
def id_from_category(series):
    """
    Turn a category into a numerical ID.
    https://stackoverflow.com/questions/38088652/pandas-convert-categories-to-numbers

    Parameters
    ----------
    series : pandas.Series

    Returns
    -------
    pandas.Series
    """

    # Input must be pandas.Series
    if not isinstance(series, pd.Series):
        raise AttributeError(f'expected pandas.Series, received {type(series)}')

    # Return category code
    return series.astype('category').cat.codes


# Note: signature should match read_table...
def read_csv(fname, **kwargs):
    """
    Read csv into :class:`pandas.DataFrame`. See :func:`read_table` for list of optional parameters.

    Parameters
    ----------
    fname : str
        Name of file.

    Returns
    -------
    pandas.DataFrame
        Data read in.
    """

    # Indicate that separator is a comma
    if 'sep' != kwargs:
        kwargs['sep'] = ','

    # Read table
    return read_table(fname, **kwargs)


# TODO enable fname to be stored in the DataFrame? Is this a bad idea?
def read_table(fname, glob=None, sep='\s+', header=None, ignore_index=True, reindex=False, **kwargs):  # noqa
    """
    Read table into :class:`pandas.DataFrame`.

    Parameters
    ----------
    fname : str
        Name of file.
    glob : bool or dict
        Does `fname` need to be globbed? Uses pathogen's `vglob`. (Default: None)
    sep : str
        Character used to separate columns? (Default: white space)
    header : bool
        (Default: None)
    reindex : bool
        (Default: False)

    Returns
    -------
    pandas.DataFrame
        Data read in.
    """

    # If glob, change fname to include all globbed files
    if glob:
        # Convert glob to a empty dictionary if necessary
        if not isinstance(glob, dict):
            glob = {}

        # vglob has 1 protected name, which is "path"
        if 'path' in glob:
            raise AttributeError('`path` cannot be used as a glob variable')

        # Glob first; if glob is empty, throw an error
        fname_glob = vglob(fname, errors='raise', **glob)
        if not fname_glob:
            raise FileNotFoundError(fname)

        # Sort glob
        # fnames = sorted(fname_glob)
        fnames = fname_glob

    # Otherwise, turn fname into a list
    # TODO evaluate if creating this list is right, or if we should short-circuit the read-in
    else:
        fnames = [fname]

    # Log files and start timer
    _logger.info(f'processing file(s): {fnames}')
    start_time = time.time()

    # Cycle over fnames and read in
    # TODO be careful here -- we want to avoid storing multiple copies of data
    kwargs['sep'] = sep
    kwargs['header'] = header
    data = list(map(partial(pd.read_table, **kwargs), fnames))
    # data = [pd.read_table(fname, **kwargs).assign({**Path(fname).metadata}) for fname in fnames]
    if glob:
        data = [table.assign(**Path(fname).metadata) for fname, table in zip(fnames, data)]

    # Concatenate
    data = data[0] if len(data) == 1 else pd.concat(data, ignore_index=ignore_index)

    # Log the shape of the data and the runtime
    end_time = time.time()
    _logger.info(f'files loaded with shape {data.shape} in {int(end_time - start_time)} seconds')

    # If header is None and index_col is defined, reset columns (so starts at 0 and not 1)
    if header is None and kwargs.get('index_col', None) is not None:
        offset = 0 if not glob else len(Path(fnames[0]).metadata)
        n_raw_columns = len(data.columns) - offset
        data.columns = list(range(n_raw_columns)) + list(Path(fnames[0]).metadata.keys())

    # Reindex?
    if reindex:
        data = data.reset_index(drop=True)
        if 'index' not in data.columns:
            data.index.name = 'index'

    # Return
    return data


def to_table(df, fname, split=None):
    if split is None:
        raise AttributeError('split=None not yet supported')

    for value in df[split].unique():
        mask = df[split] == value
        df.loc[mask, split].to_csv(fname.format(value), index=False, header=None)
