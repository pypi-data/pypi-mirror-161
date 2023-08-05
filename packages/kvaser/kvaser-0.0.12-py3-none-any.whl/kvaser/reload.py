import importlib
import re
import sys

def reload(pkg, verbose=False):
    """Reload package modules

    Examples
    ----------
    >>> kvaser.reload('mypackage')

    See Also
    ----------
    importlib.reload

    Returns
    ----------
    None

    Parameters
    ----------
    pkg: string
       Regular expression for module name(s)
    verbose: logical
       Print extra information
    """

    mod = list(filter(lambda x: re.match(pkg, x),
                      list(sys.modules.keys())))
    for m in mod:
        try:
            importlib.reload(sys.modules[m])
            if verbose:
                print(m)
        except Exception as e:
            if verbose:
                print(e)
