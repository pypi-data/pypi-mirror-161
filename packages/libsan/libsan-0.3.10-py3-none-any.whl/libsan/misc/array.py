from __future__ import absolute_import, division, print_function, unicode_literals
# Copyright (C) 2016 Red Hat, Inc.
# This file is part of libsan.
#
# libsan is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libsan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libsan.  If not, see <http://www.gnu.org/licenses/>.

"""array.py: Module to manage Arrays or Lists."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."


def dedup(array):
    """
    Remove duplicated entries from a list
    """
    if not array:
        return None
    # order preserving
    checked = []
    for e in array:
        if e not in checked:
            checked.append(e)
    return checked


def is_array_same(list1, list2):
    """
    Check if 2 unordered lists have the same elements
    """
    if set(list1) == set(list2):
        return True
    return False


def lowest_free_number(list_numbers):
    """
    From a list of integers return the lowest available number
    Start with 0,
    Example:
        input: [0, 1, 2, 4, 5, 6]
        ouput: 3
        input: [0, 1, 2, 3, 4, 5, 6]
        ouput: 7
    """
    if not list_numbers:
        return 0

    int_list = []
    # if items are not int, try to convert them to int
    for entry in list_numbers:
        int_list.append(int(entry))

    size_list = len(int_list)
    for i in range(size_list):
        if i not in int_list:
            return i

    return size_list
