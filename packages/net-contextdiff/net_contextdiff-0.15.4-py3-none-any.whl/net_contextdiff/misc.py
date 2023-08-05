# misc
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from deepops import deepget

from functools import reduce



# --- functions ---



def get_all_subclasses(c):
    """Return all subclasses of the specified class.

    The returned list will be in depth-first order but otherwise
    unsorted (e.g. A, then X(A), then Y(X) then Z(A) then B).
    """

    l = []
    for s in c.__subclasses__():
        l.append(s)
        l.extend(get_all_subclasses(s))
    return l



def deepselect(d, *p):
    """Return the specified portion of the nested structure d given by
    the path p, as per deepops.deepget() but also prefix the path as a
    leading path.

    This has the effect of returning structure d with only the portion
    given by p and nothing else and is useful for highlighting the path
    into the structure.

    If the path could not be found, None is returned, without the path
    prefix, highlighting that it was not found (as opposed to being
    empty).  This is useful in the context this is used.
    """

    # copy and reverse the path so we can use reduce() to fold right
    r = list(p)
    r.reverse()

    # try to get the path into the structure, returning None if it was
    # not found (not prefixing the path), to illustrate that the key
    # could not be found
    try:
        d_sub = deepget(d, *p, default_error=True)
    except KeyError:
        return None

    # build the path in with the final value as the deepget()
    return reduce(lambda d, k: { k: d }, r, d_sub)
