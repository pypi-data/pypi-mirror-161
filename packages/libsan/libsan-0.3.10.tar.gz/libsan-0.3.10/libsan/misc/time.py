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

"""time.py: Module to convert time."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re
from datetime import datetime


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def time_2_sec(time_str):
    """
    Usage
        time_2_sec(time_str)
    Purpose
        Convert time_str into seconds. Support days, hours, minutes and seconds
        in this format:
            1h2m3s
    Parameter
        time_str       # like "1d2h3m4s"
    Return
        time in seconds:    like 93784
    """
    if time_str is None:
        _print("FAIL: time_2_sec() - requires time_str parameter")
        return None

    time_str = str(time_str)
    if re.match(r"\d+$", time_str):
        return int(time_str)

    seconds = None

    # for example 4d
    m = re.search(r"(\d+)d", time_str)
    if m:
        if seconds is None:
            seconds = 0
        seconds += 24 * 60 * 60 * int(m.group(1))

    # for example 2h
    m = re.search(r"(\d+)h", time_str)
    if m:
        if seconds is None:
            seconds = 0
        seconds += 60 * 60 * int(m.group(1))

    # for example 1m
    m = re.search(r"(\d+)m", time_str)
    if m:
        if seconds is None:
            seconds = 0
        seconds += 60 * int(m.group(1))

    # for example 10s
    m = re.search(r"(\d+)s", time_str)
    if m:
        if seconds is None:
            seconds = 0
        seconds += int(m.group(1))

    if seconds is None:
        _print("FAIL: time_2_sec() - Could not parse '%s'" % time_str)
        return None

    return seconds


def sec_2_time(seconds):
    """
    Usage
        sec_2_time(seconds)
    Purpose
        Convert time in seconds to a more human format.
    Parameter
        seconds       # like 93784
    Return
        time in human format:    like "1d2h3m4s"
    """
    if seconds is None:
        _print("FAIL: sec_2_time() - requires seconds as parameter")
        return None

    # it can't be converted to int
    if not re.match(r"\d+$", str(seconds)):
        _print("FAIL: sec_2_time() - %s is not a valid parameter" % seconds)
        return None

    # make sure it is int
    seconds = int(seconds)

    secs = seconds % 60
    time_str = "%02ds" % secs
    if seconds > 59:
        minutes = seconds / 60
        mins = minutes % 60
        time_str = "%02dm%s" % (mins, time_str)
        if minutes > 59:
            hours = minutes / 60
            hrs = hours % 24
            time_str = "%02dh%s" % (hrs, time_str)
            if hours > 23:
                days = hours / 24
                time_str = "%02dd%s" % (days, time_str)
    return time_str


def get_time(in_seconds=False):
    """
    Get the current time
    Parameter
        in_seconds       # Boolean: Return time in second (default: False)
    Return
        Current time:   #By default as 20160714034418 (yyyymmddHHMMSS)
    """
    now = datetime.now()

    ts = now.strftime('%Y%m%d%H%M%S')
    if in_seconds:
        ts = int(now.strftime('%s'))
    return ts
