"""intervals
from https://ideone.com/JhYhNC

Union, intersection, set difference and symmetric difference
of possibly overlapping or touching integer intervals.
Intervals are defined right-open. (1, 4) -> 1, 2, 3

e.g.
union([(1, 4), (7, 9)], (3, 5)) -> [(1, 5), (7, 9)]
intersection([(1, 4), (7, 9)], (3, 5)) -> [(3, 4)]
set_difference([(1, 4), (7, 9)], (3, 5)) -> [(1, 3), (7, 9)]
set_difference([(3, 5)], [(1, 4), (7, 9)]) -> [(4, 5)]
symmetric_difference([(1, 4), (7, 9)], (3, 5)) -> [(1, 3), (4, 5), (7, 9)]

see: http://e...content-available-to-author-only...a.org/wiki/Set_theory#Basic_concepts_and_notation
"""

import copy
from collections import namedtuple
from itertools import accumulate, chain, islice, repeat
from operator import itemgetter
import unittest


class Intervals(object):
    """Holds a non overlapping list of intervals.
    One single interval is just a pair.
    Overlapping or touching intervals are automatically merged.
    """

    def __init__(self, interval_list=()):
        """Raises a ValueError if the length of one of the
        intervals in the list is negative.
        """
        if any(begin > end for begin, end in interval_list):
            raise ValueError('Invalid interval')
        self._interval_list = _merge_interval_lists(
            interval_list, [], OP_UNION)

    def __repr__(self):
        """Just write out all included intervals.
        """
        return 'Intervals ' + str(self._interval_list)

    def get(self, copy_content=True):
        """Return the list of intervals.
        """
        return copy.copy(self._interval_list) if copy_content \
            else self._interval_list


def union(a, b):
    """Merge a and b (union).
    """
    return Intervals(_merge_interval_lists(
        a.get(False), b.get(False), OP_UNION))


def intersections(a, b):
    """Intersects a and b.
    """
    return Intervals(_merge_interval_lists(
        a.get(False), b.get(False), merge_type=OP_INTERSECTIONS))


def set_difference(a, b):
    """Removes b from a.
    Set difference is not commutative.
    """
    return Intervals(_merge_interval_lists(
        a.get(False), b.get(False), merge_type=OP_SET_DIFFERENCE))


def symmetric_difference(a, b):
    """Symmetric difference of a and b.
    """
    return Intervals(_merge_interval_lists(
        a.get(False), b.get(False), merge_type=OP_SYMMETRIC_DIFFERENCE))


def compose(func_1, func_2, unpack=False):
    """
    compose(func_1, func_2, unpack=False) -> function

    The function returned by compose is a composition of func_1 and func_2.
    That is, compose(func_1, func_2)(5) == func_1(func_2(5)).
    """
    if not callable(func_1):
        raise TypeError("First argument to compose must be callable.")
    if not callable(func_2):
        raise TypeError("Second argument to compose must be callable.")

    if unpack:
        def composition(*args, **kwargs):
            return func_1(*func_2(*args, **kwargs))
    else:
        def composition(*args, **kwargs):
            return func_1(func_2(*args, **kwargs))
    return composition


# Helper to avoid repetitive lambdas.
def check_for(cond):
    return lambda val: val == cond


# http://e...content-available-to-author-only...a.org/wiki/Identity_function
identity = lambda x: x

# Depending on the operation carried out,
# the criteria for interval begins and ends in the result differ.
# E.g:
#      a = | - - - - |      | - - - |
#      b =     | - - - - |
# counts = 1   2     1   0  1       0   (union, intersection, sym diff)
# counts = 1   0    -1   0  1       0   (set diff)
# union  = | - - - - - - |  | - - - |
# inter  =     | - - - - |
# sym d  =           | - |
# set d  = | - |            | - - - |
#
# One can see that union begins if the count changes from 0 to 1
# and ends if the count changes from 1 to 0
# An intersection begins at a change from 1 to 2 and ends with 2 to 1.
# A symmetric difference begins at every change to one
# and ends at every change away from one.
# The conditions for the set difference are the same as for the union.
set_op = namedtuple('set_op', ['transform', 'begin', 'end'])

OP_UNION = set_op(
    transform=identity,
    begin=check_for((0, 1)),
    end=check_for((1, 0)))

OP_INTERSECTIONS = set_op(
    transform=identity,
    begin=check_for((1, 2)),
    end=check_for((2, 1)))

OP_SYMMETRIC_DIFFERENCE = set_op(
    transform=identity,
    begin=lambda change: change[1] == 1,
    end=lambda change: change[1] != 1)

OP_SET_DIFFERENCE = set_op(
    # If we want to calculate the set difference
    # we invert the second interval list,
    # i.e. swap begin and end.
    transform=compose(tuple, reversed),
    begin=check_for((0, 1)),
    end=check_for((1, 0)))


# class Intervals makes sure, by always building the union first,
# that no invalid a's or b's are fed here.
def _merge_interval_lists(a, b, merge_type):
    """Merges two lists of intervals in O(n*log(n)).
    Overlapping or touching intervals are simplified to one.

    Arguments:
    a and b -- The interval lists to merge.
    merge_type -- Can be:
                  OP_UNION,
                  OP_INTERSECTIONS,
                  OP_SYMMETRIC_DIFFERENCE, or
                  OP_SET_DIFFERENCE.

    Return the sorted result as a list.
    """

    # Adjust the operand for the selected operator.
    b = map(merge_type.transform, b)

    # Separately sort begins and ends
    # and pair them with the implied change
    # of the count of currently open intervals.
    # e.g. (1, 4), (7, 9), (3, 5) ->
    #     begins = [(1, 1), (3, 1), (7, 1)]
    #     ends = [(4, -1), (5, -1), (9, -1)]
    both = list(chain(a, b))
    begins = zip(sorted(map(itemgetter(0), both)),
                 repeat(1))
    ends = zip(sorted(map(itemgetter(1), both)),
               repeat(-1))

    # Sort begins and ends together.
    # If the value is the same, begins come before ends
    # to ensure touching intervals being merged to one.
    # In our example above this means:
    # edges = [(1, 4), (3, 1), (4, -1), (5, -1), (7, 1), (9, -1)]
    edges = sorted(chain(begins, ends), key=lambda x: (x[0], -x[1]))

    # The number of opened intervals after each edge.
    counts = list(accumulate(map(itemgetter(1), edges)))
    # The changes of opened intervals at each edge.
    changes = zip(chain([0], counts), counts)
    # Just the x positions of the edges.
    xs = map(itemgetter(0), edges)
    xs_and_changes = list(zip(xs, changes))

    # Now we filter out the begins and ends from the changes
    # and get their x positions.
    res_begins = map(itemgetter(0),
                     starfilter(lambda x, change: merge_type.begin(change),
                                xs_and_changes))
    res_ends = map(itemgetter(0),
                   starfilter(lambda x, change: merge_type.end(change),
                              xs_and_changes))

    # The result is then just pairing up the sorted begins and ends.
    result = pairwise(sorted(chain(res_begins, res_ends)), False)

    # No empty intervals in the result.
    def length_greater_than_zero(interval):
        return interval[0] < interval[1]

    return list(filter(length_greater_than_zero, result))


class TestIntervals(unittest.TestCase):

    def test_ctor(self):
        # Check ctors sanity check.
        self.assertRaises(ValueError, Intervals, [(2, 4), (3, 1)])

    def test_add_behind(self):
        # Check adding right of the last interval.
        intervals = Intervals([(0, 2)])
        intervals = union(intervals, Intervals([(3, 4)]))
        self.assertEqual(intervals.get(), [(0, 2), (3, 4)])

    def test_add_in_front(self):
        # Check adding left to the first interval.
        intervals = Intervals([(3, 4)])
        intervals = union(intervals, Intervals([(1, 2)]))
        self.assertEqual(intervals.get(), [(1, 2), (3, 4)])

    def test_add_in_between(self):
        # Check adding between two intervals.
        intervals = Intervals([(1, 2)])
        intervals = union(intervals, Intervals([(6, 9)]))
        intervals = union(intervals, Intervals([(3, 5)]))
        self.assertEqual(intervals.get(), [(1, 2), (3, 5), (6, 9)])

    def test_add_touching(self):
        # Check adding a interval touching an existing one.
        intervals = Intervals([(1, 3)])
        intervals = union(intervals, Intervals([(3, 5)]))
        self.assertEqual(intervals.get(), [(1, 5)])

    def test_add_overlapping(self):
        # Check adding a interval overlapping an existing one.
        intervals = Intervals([(1, 4)])
        intervals = union(intervals, Intervals([(3, 5)]))
        self.assertEqual(intervals.get(), [(1, 5)])

    def test_add_overlapping_multiple(self):
        # Check adding a interval overlapping multiple existing ones.
        intervals = Intervals([(1, 4)])
        intervals = union(intervals, Intervals([(5, 7)]))
        intervals = union(intervals, Intervals([(8, 10)]))
        intervals = union(intervals, Intervals([(3, 9)]))
        self.assertEqual(intervals.get(), [(1, 10)])

    def test_add_swallow(self):
        # Check adding a interval completely covering an existing one.
        intervals = Intervals([(2, 3)])
        intervals = union(intervals, Intervals([(1, 4)]))
        self.assertEqual(intervals.get(), [(1, 4)])

    def test_sub(self):
        # Check removing an interval
        intervals = Intervals([(0, 3)])
        intervals = union(intervals, Intervals([(5, 7)]))
        intervals = set_difference(intervals, Intervals([(2, 6)]))
        self.assertEqual(intervals.get(), [(0, 2), (6, 7)])

    def test_intersections(self):
        # Check adding right of the last interval.
        intervals = Intervals([(0, 3)])
        intervals = union(intervals, Intervals([(5, 7)]))
        intervals = intersections(intervals, Intervals([(2, 6)]))
        self.assertEqual(intervals.get(), [(2, 3), (5, 6)])

    def test_symmetric_difference(self):
        # Check symmetric difference
        intervals = Intervals([(0, 3)])
        intervals = union(intervals, Intervals([(5, 7)]))
        intervals = symmetric_difference(intervals, Intervals([(2, 6)]))
        self.assertEqual(intervals.get(), [(0, 2), (3, 5), (6, 7)])


def tuple_wise(iterable, size, step):
    """Tuples up the elements of iterable.

    Arguments:
    iterable -- source data
    size -- size of the destination tuples
    step -- step to do in iterable per destination tuple

    tuple_wise(s, 3, 1): "s -> (s0,s1,s2), (s1,s2,s3), (s3,s4,s5), ...
    tuple_wise(s, 2, 4): "s -> (s0,s1), (s4,s5), (s8,s9), ...
    """
    return zip(
        *(islice(iterable, start, None, step)
          for start in range(size)))


def pairwise(iterable, overlapping):
    """Pairs up the elements of iterable.
    overlapping: "s -> (s0,s1), (s2,s3), (s4,s5), ...
    not overlapping: "s -> (s0,s1), (s1,s2), (s2,s3), ...
    """
    return tuple_wise(iterable, 2, 1 if overlapping else 2)


def starfilter(function, iterable):
    """starfilter <--> filter  ==  starmap <--> map"""
    return (item for item in iterable if function(*item))


if __name__ == '__main__':
    unittest.main(verbosity=2)
