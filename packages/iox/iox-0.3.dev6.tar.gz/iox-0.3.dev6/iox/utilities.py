
import numpy as np
import pandas as pd


# Unpack
def unpack(a):
    """
    Unpack a higher dimensional structure into a few variables. For instance, a dataframe with an index and a single
    column could be unpacked into the variable "x" for the index and "y" for the first column.

    Parameters
    ----------
    a : pd.DataFrame

    Returns
    -------
    np.ndarray
        Unpacked data
    """
    if isinstance(a, pd.DataFrame):
        return a.reset_index().T.to_numpy()
    else:
        raise AttributeError


def wherein(a, b):
    return pd.Series(np.arange(len(b)), index=b)[a].to_numpy()



# Convenience zfill function
def zfill(a, width=None):
    if width is None:
        return a
    elif hasattr(a, '__getitem__'):
        return np.char.zfill(list(map(str, a)), width)
    else:
        return str(a).zfill(width)


# Convenience zfill range function
def zfillr(n, width=None):
    return zfill(range(n), width)


if __name__ == '__main__':
    print(zfill(range(5), 2))
