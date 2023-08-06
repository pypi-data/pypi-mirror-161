"""
Wrapper for Python iterators and iterables that implements a list-like
random-access interface by caching retrieved items for later reuse.
"""
from __future__ import annotations
from typing import Any, Union, Optional, Iterable
import doctest
import collections.abc

class reiter(collections.abc.Iterator, collections.abc.Iterable):
    """
    Wrapper class for `iterators <https://docs.python.org/3/glossary.html#term-iterator>`__
    and `iterables <https://docs.python.org/3/glossary.html#term-iterable>`__ that provides
    an interface enabling repeated iteration and random access by index of the sequence of
    items contained within.
    """
    _iterated = None
    _iterable = None
    _complete = None

    def __new__(cls, iterable: Iterable):
        """
        Constructor that wraps an iterator or iterable. An instance of this
        class yields the same sequence of items as the wrapped object.

        >>> xs = iter([1, 2, 3])
        >>> ys = reiter(xs)
        >>> list(ys)
        [1, 2, 3]

        Unlike iterators and some iterable objects (including those that are
        built-in and those that are user-defined), an instance of this class
        *always* allows iteration over its items any number of times.

        >>> list(ys), list(ys)
        ([1, 2, 3], [1, 2, 3])

        Furthermore, it is also possible to access elements using their
        index.

        >>> xs = iter([1, 2, 3])
        >>> ys = reiter(xs)
        >>> ys[0], ys[1], ys[2]
        (1, 2, 3)

        An instance of this class can be constructed from another instance
        of this class.

        >>> list(reiter(reiter(iter([1, 2, 3]))))
        [1, 2, 3]

        The type of an instance of this class can be checked in the
        usual manner, and an instance of this class cannot be constructed
        from a value or object that is not an iterator or iterable.

        >>> isinstance(reiter(xs), reiter)
        True
        >>> reiter(123)
        Traceback (most recent call last):
          ...
        TypeError: supplied object is not iterable
        """
        if isinstance(iterable, reiter):
            return iterable

        if not isinstance(iterable, collections.abc.Iterator):
            try:
                iterable = iter(iterable)
            except TypeError:
                raise TypeError('supplied object is not iterable') from None

        instance = super().__new__(cls)
        instance._iterable = iterable # At this point, this must be an iterator.
        instance._iterated = []
        instance._complete = False
        return instance

    def __next__(self: reiter) -> Any:
        """
        Substitute definition of the corresponding method for iterators
        that also caches the retrieved item before returning it.

        >>> xs = reiter(iter([1, 2, 3]))
        >>> next(xs), next(xs), next(xs)
        (1, 2, 3)

        Any attempt to retrieve items once the sequence of items is exhausted
        raises an exception in the usual manner.

        >>> next(xs)
        Traceback (most recent call last):
          ...
        StopIteration

        However, all items yielded during iteration can be accessed by
        their index, and it is also possible to iterate over them again.

        >>> xs[0], xs[1], xs[2]
        (1, 2, 3)
        >>> [x for x in xs]
        [1, 2, 3]
        >>> [x for x in xs], [x for x in xs]
        ([1, 2, 3], [1, 2, 3])
        """
        try:
            item = self._iterable.__next__()
            self._iterated.append(item)
            return item
        except StopIteration:
            self._complete = True
            raise

    def __getitem__(self: reiter, index: Union[int, slice]) -> Any:
        """
        Returns the item at the supplied index or the items within the range
        of the supplied slice, retrieving additional items from the iterator
        (and caching them) as necessary.

        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs[2]
        3
        >>> xs[1]
        2
        >>> xs = reiter(range(10))
        >>> xs[0]
        0
        >>> xs = reiter(range(10))
        >>> xs[10]
        Traceback (most recent call last):
          ...
        IndexError: index out of range
        >>> xs['abc']
        Traceback (most recent call last):
          ...
        ValueError: index must be integer or slice

        Use of slice notation is supported, but it should be used carefully.
        Omitting a lower or upper bound may require retrieving (and caching)
        all items.

        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs[0:2]
        [1, 2]
        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs[:2]
        [1, 2]
        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs[0:]
        [1, 2, 3]
        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs[:]
        [1, 2, 3]
        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs[2:0:-1]
        [3, 2]
        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs[2::-1]
        [3, 2, 1]
        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs[::-1]
        [3, 2, 1]
        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs[:0:-1]
        [3, 2]
        """
        if isinstance(index, int):
            upper = index
            if len(self._iterated) <= upper:
                while len(self._iterated) <= upper:
                    try:
                        self._iterated.append(next(self._iterable))
                    except StopIteration:
                        self._complete = True
                        break

            if upper >= len(self._iterated):
                raise IndexError('index out of range')

            return self._iterated[upper] # pylint: disable=unsubscriptable-object

        if isinstance(index, slice):
            if index.step is None or index.step > 0:
                while index.stop is None or len(self._iterated) < index.stop:
                    try:
                        self._iterated.append(next(self._iterable))
                    except StopIteration:
                        self._complete = True
                        break
            else:
                # In this case, it must be that ``index.step < 0``. Thus, all
                # items are retrieved in order to support wrapping around the
                # first item.
                while True:
                    try:
                        self._iterated.append(next(self._iterable))
                    except StopIteration:
                        self._complete = True
                        break

            return self._iterated[index] # pylint: disable=unsubscriptable-object

        raise ValueError('index must be integer or slice')

    def __iter__(self: reiter) -> Iterable:
        """
        Builds a new iterator that begins at the first cached element and
        continues from there. This method is an effective way to "reset" the
        instance of this class so that the built-in :obj:`next` function can be
        used again.

        >>> xs = reiter(iter([1, 2, 3]))
        >>> next(xs)
        1
        >>> next(xs)
        2
        >>> next(xs)
        3
        >>> next(xs)
        Traceback (most recent call last):
          ...
        StopIteration
        >>> xs = iter(xs)
        >>> next(xs), next(xs), next(xs)
        (1, 2, 3)
        """
        for item in self._iterated: # pylint: disable=not-an-iterable
            yield item
        while True:
            try:
                item = self._iterable.__next__()
                self._iterated.append(item)
                yield item
            except StopIteration:
                self._complete = True
                break

    def has(self: reiter, index: Optional[int] = None) -> bool:
        """
        Returns a boolean indicating whether a next item is available,
        or if an item exists at the specified index.

        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs.has(), xs.has(), xs.has(), xs.has()
        (True, True, True, False)

        If an explicit index is supplied, a boolean value is returned
        indicating whether an item exists at that position in the sequence
        within the wrapped iterator or iterable.

        >>> xs.has(2)
        True
        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs.has(2)
        True
        >>> xs.has(3)
        False
        """
        index = len(self._iterated) if index is None else index
        try:
            _ = self[index] # Consume an item.
            return True
        except (StopIteration, IndexError):
            return False

    def length(self: reiter) -> Optional[int]:
        """
        Returns the length of this instance, if *all* items have been
        retrieved. If not all items have been retrieved, ``None`` is
        returned.

        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs.length() is None
        True
        >>> next(xs)
        1
        >>> xs.length() is None
        True
        >>> next(xs), next(xs)
        (2, 3)
        >>> next(xs)
        Traceback (most recent call last):
          ...
        StopIteration
        >>> xs.length()
        3

        Invoking the :obj:`has` method until the instance is exhausted
        is sufficient to ensure that all items have been retrieved.

        >>> xs = reiter(iter([1, 2, 3]))
        >>> xs.has(), xs.has(), xs.has(), xs.has()
        (True, True, True, False)
        >>> xs.length()
        3
        """
        if self._complete:
            return len(self._iterated)

        # If not all items have been retrieved from the iterable,
        # there is not yet a defined length.
        return None

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
