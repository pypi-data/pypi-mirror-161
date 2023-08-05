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

"""dm.py: Module to manipulate Device mapper devices."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
from libsan.host.cmdline import run


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def dm_show_status(dm_device=None):
    """Show dmsetup status.
    The arguments are:
    \tdm_device:           Device name (optional)
    Returns:
    \tTrue
    or
    \tFalse
    """
    cmd = "dmsetup status"
    if dm_device:
        cmd += " %s" % dm_device

    retcode, _ = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not show dmsetup status")
        return False
    return True


def dm_query_status(dm_device=None):
    """Query dmsetup status and return a dictonary with table output for each device.
    The arguments are:
    \tdm_device:           Device name (optional)
    Returns:
    \tdict: Return a dictionary with status info for each device
    """
    cmd = "dmsetup status"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not list status")
        return None
    devices = output.split("\n")

    status_basic_format_regex = r"(.*):\s+(\d+)\s+(\d+)\s+(\S+)"
    # Thin formats are available on: https://www.kernel.org/doc/Documentation/device-mapper/thin-provisioning.txt
    status_thin_format_regex = status_basic_format_regex + r"\s+(\d+)\s+(\d+|-)"
    status_thin_pool_format_regex = status_basic_format_regex + r"\s+(\d+)\s+(\d+)\/(\d+)\s+(\d+)\/(\d+)(.*)"
    status_multipath_format_regex = status_basic_format_regex+r"\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.*)"

    dev_status_dict = {}
    for device in devices:
        m = re.match(status_basic_format_regex, device)
        if not m:
            _print("FAIL: dm_query_status() - (%s) does not match dmsetup status output format" % device)
            continue
        dm_type = m.group(4)
        dm_status_format_dict = {}
        if dm_type == "linear":
            dm_status_format_dict = {"logical_start_sector": m.group(2),
                                     "num_sec": m.group(3),
                                     "target_type": dm_type}
        elif dm_type == "thin":
            t = re.match(status_thin_format_regex, device)
            if not t:
                _print("FAIL: (%s) does not match dmsetup a valid %s table output format" % (device, dm_type))
                continue
            dm_status_format_dict = {"logical_start_sector": t.group(2),
                                     "num_sec": t.group(3),
                                     "target_type": dm_type,
                                     "nr_mapped_sec": t.group(5),
                                     "highest_mapped_sec": t.group(6)}
        elif dm_type == "thin-pool":
            t = re.match(status_thin_pool_format_regex, device)
            if not t:
                _print("FAIL: (%s) does not match dmsetup a valid %s table output format" % (device, dm_type))
                continue
            dm_status_format_dict = {"logical_start_sector": t.group(2),
                                     "num_sec": t.group(3),
                                     "target_type": dm_type,
                                     "trans_id": t.group(5),
                                     "used_metadata": t.group(6),
                                     "total_metadata": t.group(7),
                                     "used_data_block": t.group(8),
                                     "total_data_block": t.group(9),
                                     "metadata": t.group(10)}
        elif dm_type == "multipath":
            t = re.match(status_multipath_format_regex, device)
            if not t:
                _print("FAIL: (%s) does not match dmsetup a valid %s table output format" % (device, dm_type))
                continue
            dm_status_format_dict = {"logical_start_sector": m.group(2),
                                     "num_sec": m.group(3),
                                     "target_type": dm_type,
                                     "nr_status_feature": t.group(5),
                                     "all_io_queued": t.group(6),
                                     "nr_att_init_grp": t.group(7),
                                     "nr_hw_handlers": t.group(8),
                                     "nr_path_grps": t.group(9),
                                     "active_path_grp": t.group(10)}
            remaining_data = t.group(11)

            status_multipath_path_args_format_regex = r'\s+(\S+)'
            status_multipath_path_format_regex = r'\s+(\S+)\s+(\S+)\s+(\S+)'
            status_multipath_grp_header_format_regex = r'\s?(\S)\s+(\d+)\s+(\d+)\s+(\d+)'

            nr_groups = int(dm_status_format_dict["nr_path_grps"])
            for group_nr in range(1, int(nr_groups) + 1):
                grp_match = re.match(status_multipath_grp_header_format_regex, remaining_data)
                if not grp_match:
                    _print("FAIL: dm_query_status() - Could not parse group multipath data")
                    return None
                if "path_grp" not in list(dm_status_format_dict.keys()):
                    dm_status_format_dict["path_grp"] = {}
                dm_status_format_dict["path_grp"][group_nr] = {}
                path_grp = dm_status_format_dict["path_grp"][group_nr]
                path_grp["state"] = grp_match.group(1)
                path_grp["nr_grp_status_arg"] = grp_match.group(2)
                path_grp["nr_paths"] = grp_match.group(3)
                path_grp["nr_path_status_arg"] = grp_match.group(4)
                nr_paths = int(path_grp["nr_paths"])  # FIXME: Expected type 'Union[int, slice]', got 'str' instead
                remaining_data = re.sub(status_multipath_grp_header_format_regex, "", remaining_data, 1)
                for p_nr in range(1, int(nr_paths) + 1):
                    path_match = re.match(status_multipath_path_format_regex, remaining_data)
                    if not path_match:
                        _print("FAIL: dm_query_status() - Could not parse path multipath data")
                        return None
                    if "path" not in list(path_grp.keys()):
                        path_grp["path"] = {}
                    path_grp["path"][p_nr] = {}  # FIXME: Expected type 'Union[int, slice]', got 'str' instead
                    path = path_grp["path"][p_nr]  # FIXME: Expected type 'Union[int, slice]', got 'str' instead
                    path["device"] = path_match.group(1)
                    path["state"] = path_match.group(2)
                    path["failure_cnt"] = path_match.group(3)
                    remaining_data = re.sub(status_multipath_path_format_regex, "", remaining_data, 1)
                    for _ in range(1, int(grp_match.group(4)) + 1):
                        path_arg_match = re.match(status_multipath_path_args_format_regex, remaining_data)
                        if not path_arg_match:
                            _print("FAIL: dm_query_status() - Could not parse path args multipath data")
                            return None
                        if "path_status_args" not in list(path.keys()):
                            path["path_status_args"] = ""
                        path["path_status_args"] += "%s " % path_arg_match.group(1)
                        remaining_data = re.sub(status_multipath_path_args_format_regex, "", remaining_data, 1)
                    # remove trailing space from the end of string
                    if "path_status_args" in list(path.keys()):
                        path["path_status_args"] = path["path_status_args"].strip()

        else:
            _print("FAIL: dm_query_status() - (%s) can't parse status for device type %s" % (device, dm_type))

        dev_status_dict[m.group(1)] = dm_status_format_dict
    if dm_device:
        if dm_device in list(dev_status_dict.keys()):
            return dev_status_dict[dm_device]
        return None
    return dev_status_dict


def dm_show_table(dm_device=None):
    """Show dmsetup table.
    The arguments are:
    \tdm_device:           Device name (optional)
    Returns:
    \tTrue
    or
    \tFalse
    """
    cmd = "dmsetup table"
    if dm_device:
        cmd += " %s" % dm_device

    retcode, _ = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not show dmsetup table")
        return False
    return True


def dm_query_table(dm_device=None):
    """Query dmsetup table and return a dictonary with table output for each device.
    The arguments are:
    \tdm_device:           Device name (optional)
    Returns:
    \tdict: Return a dictionary with table info for each device
    """
    cmd = "dmsetup table"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not list table")
        return None
    devices = output.split("\n")

    # Basic format information is found on man dmsetup under "TABLE FORMAT" section
    # format of dmsetup table: logical_start_sector num_sectors target_type target_args
    table_basic_format_regex = r"(.*):\s+(\S+)\s+(\S+)\s+(\S+)"
    # format for linear type
    table_linear_format_regex = table_basic_format_regex + r"\s+(\S+)\s+(\S+)$"
    # vgtest-thin1: 0 2097152 thin 253:5 1
    table_thin_format_regex = table_basic_format_regex + r"\s+(\S+)\s+(\S+)$"
    # vgtest-test_pool-tpool: 0 1638400 thin-pool 253:3 253:4 512 0 1 error_if_no_space
    table_thin_pool_format_regex = table_basic_format_regex + r"\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)$"
    # delayed: 0 20971520 delay 7:0 0 100
    table_delay_format_regex = table_basic_format_regex + r"\s+(\S+)\s+(\S+)\s+(\S+)$"

    dev_table_dict = {}
    for device in devices:
        m = re.match(table_basic_format_regex, device)
        if not m:
            _print("FAIL: (%s) does not match dmsetup table output format" % device)
            continue
        dm_type = m.group(4)
        dm_table_format_dict = {}
        if dm_type == "linear":
            t = re.match(table_linear_format_regex, device)
            if not t:
                _print("FAIL: (%s) does not match dmsetup a valid linear table output format" % device)
                continue
            dm_table_format_dict = {"logical_start_sector": t.group(2),
                                    "num_sec": t.group(3),
                                    "target_type": dm_type,
                                    "dev": t.group(5),
                                    "start_sec": t.group(6)}
        elif dm_type == "thin":
            t = re.match(table_thin_format_regex, device)
            if not t:
                _print("FAIL: (%s) does not match dmsetup a valid %s table output format" % (device, dm_type))
                continue
            dm_table_format_dict = {"logical_start_sector": t.group(2),
                                    "num_sec": t.group(3),
                                    "target_type": dm_type,
                                    "pool_dev": t.group(5),
                                    "dev_num": t.group(6)}
        elif dm_type == "thin-pool":
            t = re.match(table_thin_pool_format_regex, device)
            if not t:
                _print("FAIL: (%s) does not match dmsetup a valid %s table output format" % (device, dm_type))
                continue
            dm_table_format_dict = {"logical_start_sector": t.group(2),
                                    "num_sec": t.group(3),
                                    "target_type": dm_type,
                                    "metadata_dev": t.group(5),
                                    "data_dev": t.group(6),
                                    "data_block_size": t.group(7),
                                    "low_water_mark": t.group(8),
                                    "target_args": t.group(9)}
        elif dm_type == "delay":
            t = re.match(table_delay_format_regex, device)
            if not t:
                _print("FAIL: (%s) does not match dmsetup a valid %s table output format" % (device, dm_type))
                continue
            dm_table_format_dict = {"logical_start_sector": t.group(2),
                                    "num_sec": t.group(3),
                                    "target_type": dm_type,
                                    "dev": t.group(5),
                                    "start_sec": t.group(6),
                                    "delay": t.group(7)}
        elif dm_type == "multipath":
            # multipath table format see: http://christophe.varoqui.free.fr/refbook.html
            device_params = device.split(" ")
            dm_table_format_dict = dict()
            dm_table_format_dict["logical_start_sector"] = m.group(2)
            dm_table_format_dict["num_sec"] = m.group(3)
            dm_table_format_dict["target_type"] = dm_type
            dm_table_format_dict["nr_status_feature"] = int(device_params[4])
            # set index to next entry after nr_status_feature
            param_index = 4 + 1
            if dm_table_format_dict["nr_status_feature"] > 0:
                dm_table_format_dict["features"] = []
                for _ in range(dm_table_format_dict["nr_status_feature"]):
                    dm_table_format_dict["features"].append(device_params[param_index])
                    param_index += 1

            dm_table_format_dict["nr_hw_handlers"] = int(device_params[param_index])
            param_index += 1
            if dm_table_format_dict["nr_hw_handlers"] > 0:
                dm_table_format_dict["hw_handlers"] = []
                for _ in range(dm_table_format_dict["nr_hw_handlers"]):
                    dm_table_format_dict["hw_handlers"].append(device_params[param_index])
                    param_index += 1

            dm_table_format_dict["nr_path_grps"] = int(device_params[param_index])
            param_index += 1
            dm_table_format_dict["try_next_path_grp"] = device_params[param_index]
            param_index += 1

            remaining_data = ""
            for _ in range(len(device_params) - param_index):
                remaining_data += "%s " % device_params[param_index]
                param_index += 1
            remaining_data = remaining_data.strip()

            table_multipath_grp_header_format_regex = r'\s?(\S+)\s+(\d+)\s+(\d+)\s+(\d+)'
            table_multipath_path_header_format_regex = r'\s?(\S+)'
            table_multipath_path_args_format_regex = r'\s?(\S+)'
            nr_groups = dm_table_format_dict["nr_path_grps"]
            for group_nr in range(1, int(nr_groups) + 1):
                grp_match = re.match(table_multipath_grp_header_format_regex, remaining_data)
                if not grp_match:
                    _print("FAIL: dm_query_table() - Could not parse group multipath data")
                    return None
                if "path_grp" not in list(dm_table_format_dict.keys()):
                    dm_table_format_dict["path_grp"] = {}
                dm_table_format_dict["path_grp"][group_nr] = {}
                path_grp = dm_table_format_dict["path_grp"][group_nr]
                path_grp["path_selector"] = grp_match.group(1)
                path_grp["nr_selector_args"] = grp_match.group(2)
                path_grp["nr_paths_grp"] = grp_match.group(3)
                path_grp["nr_path_args"] = grp_match.group(4)
                # remove processed data
                remaining_data = re.sub(table_multipath_grp_header_format_regex, "", remaining_data, 1)
                for path_nr in range(1, int(path_grp["nr_paths_grp"]) + 1):
                    path_match = re.match(table_multipath_path_header_format_regex, remaining_data)
                    if not path_match:
                        _print("FAIL: dm_query_table() - Could not parse path multipath data")
                        return None
                    if "path" not in list(dm_table_format_dict.keys()):
                        dm_table_format_dict["path"] = {}
                    dm_table_format_dict["path"][path_nr] = {}
                    path = dm_table_format_dict["path"][path_nr]
                    path["device"] = path_match.group(1)

                    remaining_data = re.sub(table_multipath_path_header_format_regex, "", remaining_data, 1)
                    for _ in range(1, int(path_grp["nr_path_args"]) + 1):
                        arg_match = re.match(table_multipath_path_args_format_regex, remaining_data)
                        if not arg_match:
                            _print("FAIL: dm_query_table() - Could not parse path arg multipath data")
                            return None
                        if "path_status_args" not in list(path.keys()):
                            path["path_status_args"] = ""
                        path["path_status_args"] += "%s " % arg_match.group(1)
                        remaining_data = re.sub(table_multipath_path_args_format_regex, "", remaining_data, 1)
                    if "path_status_args" in list(path.keys()):
                        # remove trailing space
                        path["path_status_args"] = path["path_status_args"].strip()

        else:
            _print("FAIL: dm_query_table() - (%s) can't parse table for device type '%s'" % (device, dm_type))
        dev_table_dict[m.group(1)] = dm_table_format_dict

    if dm_device:
        if dm_device in list(dev_table_dict.keys()):
            return dev_table_dict[dm_device]
        return None
    return dev_table_dict


def dm_get_table_device(dm_name):
    """
    Get table information for specific device.
    The table info is not parsed
    """
    if not dm_name:
        return None
    cmd = "dmsetup table %s" % dm_name
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not query table for %s" % dm_name)
        return None

    return output


def dm_set_target_type(dm_name, target_type):
    """Change the target type of an specific DM device
    it is necessary to suspend the device before loading new table
    The arguments are:
    \tDevice name: eg. VG-lv_home
    Returns:
    \tBoolean:
    \t\tTrue in case of success
    \t\tFalse in case of failure
    """
    table_format_regex = r"(\S+)\s+(\S+)\s+(\S+)\s(.*)$"
    table_info = dm_get_table_device(dm_name)
    if not table_info:
        # Could not get table for device name
        return False

    # We need to suspend the device first
    if not dm_suspend_dev(dm_name):
        return False

    m = re.match(table_format_regex, table_info)
    if not m:
        _print("FAIL: dm_set_target_type() - (%s) does not match dmsetup table output format" % table_info)
        return False
    # load the table with new target type
    new_table = "\"%s %s %s %s\"" % (m.group(1), m.group(2), target_type, m.group(4))

    cmd = "dmsetup load %s --table %s" % (dm_name, new_table)
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: dm_set_target_type() - could not load table on %s" % dm_name)
        dm_resume_dev(dm_name)
        return False

    if not dm_resume_dev(dm_name):
        return False

    return True


def dm_suspend_dev(dm_name):
    """Executes dmsetup suspend to suspend an specific DM device
    The arguments are:
    \tDevice name: eg. VG-lv_home
    Returns:
    \tBoolean:
    \t\tTrue in case of success
    \t\tFalse in case of failure
    """
    cmd = "dmsetup suspend %s" % dm_name
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: could not suspend %s" % dm_name)
        return False

    return True


def dm_resume_dev(dm_name):
    """Executes dmsetup resume to suspend an specific DM device
    The arguments are:
    \tDevice name: eg. VG-lv_home
    Returns:
    \tBoolean:
    \t\tTrue in case of success
    \t\tFalse in case of failure
    """
    cmd = "dmsetup resume %s" % dm_name
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: could not resume %s" % dm_name)
        return False

    return True


def dm_message_dev(dm_name, message):
    """Executes dmsetup message to send a message to an specific DM device
    The arguments are:
    \tDevice name: eg. mpatha
    Returns:
    \tBoolean:
    \t\tTrue in case of success
    \t\tFalse in case of failure
    """
    cmd = "dmsetup message %s %s" % (dm_name, message)
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: could not send message to %s" % dm_name)
        return False

    return True


def dm_remove(dm_name):
    """Remove the the specified device
    The arguments are:
    \tDevice name: eg. Device mapped device name
    Returns:
    \tBoolean:
    \t\tTrue in case of success
    \t\tFalse in case of failure
    """
    devs = dm_query_table()
    if dm_name not in list(devs.keys()):
        # device name does not exist
        return True

    cmd = "dmsetup remove %s" % dm_name
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: could not remove %s" % dm_name)
        return False
    return True
