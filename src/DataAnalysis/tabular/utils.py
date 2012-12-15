"""
Miscellaneous utilities:  uniqify, listunion, listintersection, perminverse

"""

import numpy as np

__all__ = ['uniqify', 'listunion', 'listintersection', 'perminverse']

def uniqify(seq, idfun=None):
    """
    Relatively fast pure Python uniqification function that preservs ordering.

    **Parameters**

            **seq** :  sequence

                    Sequence object to uniqify.

            **idfun** :  function, optional

                    Optional collapse function to identify items as the same.

    **Returns**

            **result** :  list

                    Python list with first occurence of each item in `seq`, in 
                    order.

    """
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def listunion(ListOfLists):
    """
    Take the union of a list of lists.

    Take a Python list of Python lists::

            [[l11,l12, ...], [l21,l22, ...], ... , [ln1, ln2, ...]]

    and return the aggregated list::

            [l11,l12, ..., l21, l22 , ...]

    For a list of two lists, e.g. `[a, b]`, this is like::

            a.extend(b)

    **Parameters**

            **ListOfLists** :  Python list

                    Python list of Python lists.

    **Returns**

            **u** :  Python list

                    Python list created by taking the union of the
                    lists in `ListOfLists`.

    """
    u = []
    for s in ListOfLists:
        if s != None:
            u.extend(s)
    return u

def listintersection(ListOfLists):
    u = ListOfLists[0]
    for l in ListOfLists[1:]:
        u = [ll for ll in u if ll in l]
    return u

def perminverse(s):
    '''
    Fast inverse of a (numpy) permutation.

    **Paramters**

            **s** :  sequence

                    Sequence of indices giving a permutation.

    **Returns**

            **inv** :  numpy array

                    Sequence of indices giving the inverse of permutation `s`.

    '''
    X = np.array(range(len(s)))
    X[s] = range(len(s))
    return X
    

def fromarrays(X,type=None,**kwargs):
   _array = np.rec.fromarrays(X,**kwargs)
   if type is not None:
       _array = _array.view(type)
   return _array
   
   
def fromrecords(X,type=None,**kwargs):
   _array = np.rec.fromrecords(X,**kwargs)
   if type is not None:
       _array = _array.view(type)
   return _array
   