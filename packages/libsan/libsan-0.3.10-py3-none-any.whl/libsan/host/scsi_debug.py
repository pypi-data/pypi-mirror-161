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

"""scsi_debug.py: Module to manipulate devices created by scsi_debug module."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import libsan.host.linux
import libsan.host.mp
import libsan.host.scsi
import re  # regex
from libsan.host.cmdline import run


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    return


def scsi_debug_load_module(options=None):
    module_cmd = "scsi_debug"
    if libsan.host.linux.is_module_loaded(module_cmd):
        _print("WARN: scsi_debug_load_module() - Module is already loaded")
        return True

    if options:
        module_cmd += " %s" % options

    if not libsan.host.linux.load_module(module_cmd):
        _print("FAIL: scsi_debug_load_module() - Could not load %s" % module_cmd)
        return False
    # Wait a bit, for example for multipath to create the device
    libsan.host.linux.sleep(2)
    return True


def scsi_debug_unload_module():
    module_name = "scsi_debug"
    if not libsan.host.linux.is_module_loaded(module_name):
        # Module is not loaded, return success
        return True

    if libsan.host.mp.is_multipathd_running():
        mpaths = libsan.host.mp.mpath_names_of_vendor("Linux")
        for mpath in mpaths:
            libsan.host.mp.remove_mpath(mpath)
            # Wait a bit, for example for multipath to remove the device
            libsan.host.linux.sleep(2)

    if not libsan.host.linux.unload_module(module_name):
        _print("FAIL: scsi_debug_load_module() - Could not unload %s" % module_name)
        return False
    return True


def get_scsi_debug_devices():
    """
    Return a list of scsi_debug devices
    """
    module_name = "scsi_debug"
    vendor = "Linux"
    if not libsan.host.linux.is_module_loaded(module_name):
        return None

    mpaths = libsan.host.mp.mpath_names_of_vendor(vendor)
    if mpaths:
        return mpaths

    scsi_devices = libsan.host.scsi.get_scsi_name_by_vendor(vendor)
    if scsi_devices:
        return scsi_devices

    return None


def scsi_debug_set_param(param, value):
    """
    Set specific value to scsi debug parameter
    """
    if param is None or value is None:
        _print("FAIL: scsi_debug_set_param() - requires param_name and value")
        return False

    if (run("echo '%s' > /sys/bus/pseudo/drivers/scsi_debug/%s" % (value, param),
            verbose=False) != 0):
        _print("FAIL: scsi_debug_set_param() - Could not set %s with value %s" % (param, value))
        return False
    return True


def scsi_debug_insert_failure(every_nth, opts):
    """
    Purpose:
    \tEnable/Disable failure on scsi_debug device
    Parameter:
    \tA dictionary with all option to be set
    \tThe supported paramenters are defined at: http://sg.danny.cz/sg/sdebug26.html
    \topts: 1 - "noisy"
    \t2-"medium error"
    \t4 - ignore "nth"
    \t8 - cause "nth" read or write command to yield a RECOVERED_ERROR
    \t16 -  cause "nth" read or write command to yield a ABORTED_COMMAND
    every_nth: how often the failure is inserted
    Return:
    \tTrue: if success
    \tFalse: if some problem occurred
    """

    if not every_nth:
        every_nth = 0
    if not opts:
        opts = 0

    if not scsi_debug_set_param("every_nth", every_nth):
        _print("FAIL: scsi_debug_insert_failure() - Could not set every_nth with value: %s" % every_nth)
        return False
    if not scsi_debug_set_param("opts", opts):
        _print("FAIL: scsi_debug_insert_failure() - Could not set opts with value: %s" % opts)
        return False
    return True


def self_test():
    """
    """
    if not scsi_debug_load_module():
        _print("FAIL: self_test() - Could not load the module")
        return False

    if not get_scsi_debug_devices():
        _print("FAIL: self_test() - Could not find any scsi debug device")
        scsi_debug_unload_module()
        return False

    if not scsi_debug_insert_failure(0, 0):
        _print("FAIL: self_test() - Could not set parameters")
        scsi_debug_unload_module()
        return False

    if not scsi_debug_unload_module():
        _print("FAIL: self_test() - Could not unload the module")
        return False

    return True
