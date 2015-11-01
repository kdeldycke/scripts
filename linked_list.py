#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Implement a linked-list.

Haven't implemented a linked list in low-level language (C for instance) since
2003. And I did not produce any significant C code in the last 10 years.

My day-to-day language is Python. For which list/set/dict structures are a
solved-problem. Implementing a linked-list in Python is silly.

Still, that's the assignment. So let's do it anyway ! :)

OK, now what ? I can't really implement a low-level linked-list, as pointer
facilities are not explicit and are all hidden behind standard assignations
in Python.

Should I implement an object-oriented structure to persist linked-list ?
Why not. Now that's what I call a challenge. A silly challenge, but a challenge
nonetheless.

Finally, if you're looking for an idiomatic package, with a proper testing
suite and CLI, I advise you to check out the following toy project:
    https://github.com/kdeldycke/chessboard

As a bonus, you'll find there a glimpse of my commit habits.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)


# Package metadata.
__version__ = '0.0.1'


class Node(object):

    """ Node instances are atomic elements composing a linked-list. """

    def __init__(self, value):
        """ Set default node attributes. """
        self.value = value
        self.next_node = None


class LinkedList(object):

    """ Implement a list storing values in a chain of linked nodes.

    General philosophy: try to make this class user-firendly by re-using
    methods names available for built-in Python list-like types.

    Future enhancements: override standard operator via __magic__ methods.
    """

    # Stupid constant for recursive reverse initialization, cause it's late
    # and I feel lazy re-factoring a working recursive reverse, only to support
    # cleaner initial conditions.
    INIT = 'init'

    def __init__(self, sequence=None):
        """ Initial empty linked-list has no root node. """
        self.root_node = None
        if sequence:
            for item in sequence:
                self.insert(item)

    @property
    def last_node(self):
        """ Get last node of the linked list. """
        node = self.root_node
        while node and node.next_node:
            node = node.next_node
        return node

    @property
    def nodes(self):
        """ Iterate the linked list and return each node. """
        node = self.root_node
        while node:
            yield node
            node = node.next_node

    def insert(self, value):
        """ Append a value at the end of the linked list. """
        new_node = Node(value)
        if not self.last_node:
            self.root_node = new_node
        else:
            self.last_node.next_node = new_node

    @property
    def values(self):
        """ Iterate the whole linked list and return values of each node. """
        for node in self.nodes:
            yield node.value

    def contains(self, item):
        """ Check if an item is in our linked-list. """
        for value in self.values:
            if item == value:
                return True
        return False

    def iterative_reverse(self):
        """ Reverse the whole chain of nodes iteratively. """
        previous_node = None
        node = self.root_node
        while node:
            next_node = node.next_node
            node.next_node = previous_node
            previous_node = node
            node = next_node
        self.root_node = previous_node

    def recursive_reverse(self, node=INIT):
        """ Reverse the whole chain of nodes recursively. """
        if node == self.INIT:
            node = self.root_node
        if not node:
            return
        if not node.next_node:
            self.root_node = node
            return
        self.recursive_reverse(node.next_node)
        node.next_node.next_node = node
        node.next_node = None


class LinkedSet(LinkedList):

    """ Same as a linked-list, but enforce uniqueness. """

    def insert(self, value):
        """ Only insert a value if and only if not already in a node. """
        if value not in self.values:
            super(LinkedSet, self).insert(value)

    # Alias add() method to insert().
    add = insert


def main():
    """ Unit tests.

    Should have been put in a proper Python unittest suite. But I'm lazy so
    let's put eveything in a plain single source file.
    """
    print("Testing LinkedList class.")

    # Check that the linked list eat everything and keeps order.
    ll1 = LinkedList()
    ll1.insert(42)
    ll1.insert(None)
    ll1.insert('')
    ll1.insert('Pass the Peas')
    assert list(ll1.values) == [42, None, '', 'Pass the Peas']

    # Test empty list.
    ll2 = LinkedList()
    assert list(ll2.values) == []

    # Test constructor from a list-like object.
    ll3 = LinkedList([1, 2, 3, 5])
    assert list(ll3.values) == [1, 2, 3, 5]
    ll4 = LinkedList('abcd')
    assert list(ll4.values) == ['a', 'b', 'c', 'd']

    # Test content lookup.
    ll5 = LinkedList('super')
    assert ll5.contains('p')
    assert not ll5.contains('z')

    print("Testing LinkedSet class.")

    # Check that the linked set eat everything and keeps order.
    ls1 = LinkedSet()
    ls1.insert(42)
    ls1.insert(None)
    ls1.insert('')
    ls1.insert('Pass the Peas')
    # Insert duplicate values.
    ls1.insert(None)
    ls1.insert('')
    # Test add alias.
    ls1.add(None)
    ls1.add('')
    assert list(ls1.values) == [42, None, '', 'Pass the Peas']

    # Test empty set.
    ls2 = LinkedSet()
    assert list(ls2.values) == []

    # Test constructor from a list-like object.
    ls3 = LinkedSet([1, 2, 2, 3, 5, 1])
    assert list(ls3.values) == [1, 2, 3, 5]
    ls4 = LinkedSet('abcdddadb')
    assert list(ls4.values) == ['a', 'b', 'c', 'd']

    # Test content lookup.
    ls5 = LinkedSet('super')
    assert ls5.contains('p')
    assert not ls5.contains('z')

    print("Testing reversing nodes.")

    # Test iterative reverse.
    lr1 = LinkedList()
    lr1.insert(1)
    lr1.insert(2)
    lr1.insert(3)
    lr1.insert(4)
    assert list(lr1.values) == [1, 2, 3, 4]
    lr1.iterative_reverse()
    assert list(lr1.values) == [4, 3, 2, 1]

    # Test empty list iterative reversal.
    lr2 = LinkedList()
    assert list(lr2.values) == []
    lr2.iterative_reverse()
    assert list(lr2.values) == []

    # Test recursive reverse.
    lr3 = LinkedList()
    lr3.insert(1)
    lr3.insert(2)
    lr3.insert(3)
    lr3.insert(4)
    assert list(lr3.values) == [1, 2, 3, 4]
    lr3.recursive_reverse()
    assert list(lr3.values) == [4, 3, 2, 1]

    # Test empty list recursive reversal.
    lr4 = LinkedList()
    assert list(lr4.values) == []
    lr4.recursive_reverse()
    assert list(lr4.values) == []

    print("Everything's working ! :)")


if __name__ == "__main__":
    main()
