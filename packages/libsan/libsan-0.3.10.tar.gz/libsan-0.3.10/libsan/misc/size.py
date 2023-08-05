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

"""size.py: Module to convert human size <=> bytes."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex

size_human_regex = re.compile(r"([\-0-9\.]+)(Ki|Mi|Gi|Ti|Ei|Zi){0,1}B$")


def _print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def size_human_check(size_human):
    size_human = str(size_human)
    m = size_human_regex.match(size_human)
    if not m:
        _print("FAIL: size_human_check() - incorrect number format %s" % size_human)
        return False
    return True


def size_human_2_size_bytes(size_human):
    """
    Usage
        size_human_2_size_bytes(size_human)
    Purpose
        Convert human readable stander size to B
    Parameter
        size_human     # like '1KiB'
    Returns
        size_bytes     # like 1024
    """
    if not size_human:
        return None

    # make sure size_human is a string, could be only numbers, for example
    size_human = str(size_human)
    if not re.search(r"\d", size_human):
        # Need at least 1 digit
        return None

    m = size_human_regex.match(size_human)
    if not m:
        if re.match(r"^\d+$", size_human):
            # Assume size is already in bytes
            return size_human
        _print("FAIL: '%s' is an invalid human size format" % size_human)
        return None

    fraction = 0
    # check if number is fractional
    f = re.match(r"(\d+)\.(\d+)", m.group(1))
    if f:
        number = int(f.group(1))
        fraction = int(f.group(2))
    else:
        number = int(m.group(1))

    unit = m.group(2)
    if not unit:
        unit = 'B'

    for valid_unit in ['B', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if unit == valid_unit:
            if unit == 'B':
                # cut any fraction if was given, as it is not valid
                return str(number)
            return int(number + fraction)
        number *= 1024
        fraction *= 1024
        fraction /= 10
    return int(number + fraction)


def size_bytes_2_size_human(num):
    if not num:
        return None

    # Even if we receive string we convert so we can process it
    num = int(num)
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB']:
        if abs(num) < 1024.0:
            size_human = "%3.1f%s" % (num, unit)
            # round it down removing decimal numbers
            size_human = re.sub(r"\.\d+", "", size_human)
            return size_human
        num /= 1024.0
    # Very big number!!
    size_human = "%.1f%s" % (num, 'Yi')
    # round it down removing decimal numbers
    size_human = re.sub(r"\.\d+", "", size_human)
    return size_human
