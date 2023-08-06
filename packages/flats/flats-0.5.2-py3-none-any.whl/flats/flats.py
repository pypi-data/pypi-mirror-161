"""
Minimal library that enables flattening of nested instances of
container types.
"""
from __future__ import annotations
from typing import Union, Optional, Sequence, Iterable
import collections.abc
import doctest

def _is_container(instance: Union[Iterable, Sequence]) -> bool:
    """
    Return a boolean value indicating whether the supplied object is considered
    an instance of a container type (according to this library).
    """
    if isinstance(instance, (
            tuple, list, set, frozenset,
            collections.abc.Iterable, collections.abc.Generator
        )):
        return True

    try:
        _ = instance[0]
        return True
    except: # pylint: disable=bare-except
        return False

def flats(xss: Iterable, depth: Optional[int] = 1) -> Iterable:
    """
    Flatten an instance of a container type that is the root of a tree of nested
    instances of container types, returning as an :obj:`~collections.abc.Iterable`
    the sequence of all objects or values (that are not of a container type)
    encountered during an in-order traversal.

    :param xss: Iterable (usually of container instances) to be flattened.
    :param depth: Number of layers to flatten (*i.e.*, amount by which the depth of
        the nested structure should be reduced).

    >>> list(flats([[1, 2, 3], [4, 5, 6, 7]]))
    [1, 2, 3, 4, 5, 6, 7]

    Any instance of :obj:`~collections.abc.Iterable` or :obj:`~types.GeneratorType`
    (including instances of the built-in types :obj:`tuple`, :obj:`list`, :obj:`set`,
    :obj:`frozenset`, :obj:`range`, :obj:`bytes`, and :obj:`bytearray`) is considered
    an instance of a container type.

    >>> list(flats(frozenset({frozenset({1, 2, 3}), frozenset({4, 5, 6, 7})})))
    [1, 2, 3, 4, 5, 6, 7]
    >>> list(flats(((1, 2, 3), (4, 5, 6, 7))))
    [1, 2, 3, 4, 5, 6, 7]

    The nested instances need not be of the same type.

    >>> list(flats([(1, 2, 3), (4, 5, 6, 7)]))
    [1, 2, 3, 4, 5, 6, 7]
    >>> tuple(flats([{1}, {2}, {3}, frozenset({4}), iter([5, 6, 7])]))
    (1, 2, 3, 4, 5, 6, 7)
    >>> list(flats(['abc', 'xyz']))
    ['a', 'b', 'c', 'x', 'y', 'z']
    >>> list(flats([range(3), range(3)]))
    [0, 1, 2, 0, 1, 2]
    >>> list(flats([bytes([0, 1, 2]), bytes([3, 4, 5])]))
    [0, 1, 2, 3, 4, 5]
    >>> list(flats([bytearray([0, 1, 2]), bytearray([3, 4, 5])]))
    [0, 1, 2, 3, 4, 5]

    The optional ``depth`` argument can be used to limit the depth at which nested
    instances of a container type are not recursively traversed. For example, setting
    ``depth`` to ``1`` is sufficient to flatten any list of lists into a list. Thus,
    ``1`` **is the default value** for ``depth``.

    >>> list(flats([[[1, 2], 3], [4, 5, 6, 7]], depth=1))
    [[1, 2], 3, 4, 5, 6, 7]
    >>> list(flats([[[1, 2], 3], [4, 5, 6, 7]], depth=2))
    [1, 2, 3, 4, 5, 6, 7]
    >>> list(flats([[[1, 2], [3]], [[4, 5], [6, 7]]], depth=2))
    [1, 2, 3, 4, 5, 6, 7]
    >>> list(flats([(1, 2, 3), (4, 5, 6, 7)], depth=3))
    [1, 2, 3, 4, 5, 6, 7]

    Setting ``depth`` to ``0`` returns unmodified the contents of the supplied instance
    of a container type (though, for consistency, these results are still returned as
    an iterable).

    >>> list(flats([[[1, 2], 3], [4, 5, 6, 7]], depth=0))
    [[[1, 2], 3], [4, 5, 6, 7]]

    If ``depth`` is set to ``float('inf')``, recursive traversal of instances of
    container types occurs to any depth (until an instance of a non-container type is
    encountered).

    >>> list(flats([[[1, [2]], 3], [4, [[[5]]], 6, 7]], depth=float('inf')))
    [1, 2, 3, 4, 5, 6, 7]

    If the value of the ``depth`` argument is not a non-negative integer, an exception
    is raised.

    >>> list(flats([(1, 2, 3), (4, 5, 6, 7)], depth='abc'))
    Traceback (most recent call last):
      ...
    TypeError: depth must be an integer or infinity
    >>> list(flats([(1, 2, 3), (4, 5, 6, 7)], depth=-1))
    Traceback (most recent call last):
      ...
    ValueError: depth must be a non-negative integer or infinity

    User-defined container types are also supported.

    >>> class wrap():
    ...     def __init__(self, xs): self.xs = xs
    ...     def __getitem__(self, key): return self.xs[key]
    ...     def __repr__(self): return 'wrap(' + str(self.xs) + ')'
    >>> wrap(list(flats(wrap([wrap([1, 2]), wrap([3, 4])]))))
    wrap([1, 2, 3, 4])
    """
    # pylint: disable=too-many-branches
    if depth == 1: # Most common case is first for efficiency.
        for xs in xss:
            if _is_container(xs):
                for x in xs:
                    yield x
            else:
                yield xs
    elif depth == 0: # For consistency, base case is also a generator.
        for xs in xss:
            yield xs
    else: # General recursive case.
        for xs in xss:
            if isinstance(depth, int) and depth >= 1:
                if _is_container(xs):
                    for x in flats(xs, depth=(depth - 1)):
                        yield x
                else:
                    yield xs
            elif depth == float('inf'):
                if _is_container(xs):
                    for x in flats(xs, depth=float('inf')):
                        yield x
                else:
                    yield xs
            elif isinstance(depth, int) and depth < 0:
                raise ValueError('depth must be a non-negative integer or infinity')
            elif depth != float('inf') and not isinstance(depth, int):
                raise TypeError('depth must be an integer or infinity')

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
