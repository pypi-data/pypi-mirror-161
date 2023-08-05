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


"""snapper.py: Module to manage snapper tool."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import sys
import os
from libsan.host.cmdline import run


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    sys.stdout.flush()
    return


def _has_snapper():
    if run("which snapper", verbose=False) != 0:
        return False
    return True


def snapper_query_configs(verbose=False):
    """
    Query all info for all snapshot from a configuration
    Return a dict, the key is the snapshot number
    """

    if not _has_snapper():
        _print("FATAL: snapper_query_configs() - snapper is not installed")
        return False

    cmd = "snapper list-configs"
    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: snapper_query_configs() - Could not query configs")
        print(output)
        return None

    if not output:
        return None

    lines = output.split("\n")

    # example of output
    # snapper list-configs
    # Config  | Subvolume
    # --------+----------
    # bugtest | /mnt/test

    # First line before receiving snapshot details
    begin_data_regex = re.compile(r"-*\+-*")
    config_name_index = 0
    subvolume_index = 1

    query_dict = {}

    found_configs = False
    for line in lines:
        # _print("DEBUG: '%s'" % line)
        # skip until find first line containing snapshots
        if not found_configs and not begin_data_regex.match(line):
            continue
        if begin_data_regex.match(line):
            # _print("DEBUG: found begin")
            found_configs = True
            continue

        # separate snap info into a list
        config_info = line.split("|")
        if not config_info:
            continue

        config_name = config_info[config_name_index].strip()
        config_subvolume = config_info[subvolume_index].strip()
        query_dict[config_name] = {}
        config_dict = query_dict[config_name]
        config_dict["name"] = config_name
        config_dict["subvolume"] = config_subvolume
        # Set empty values to None
        for key in list(config_dict.keys()):
            if config_dict[key] == "":
                config_dict[key] = None

    return query_dict


def snapper_list_configs():
    """
    List all config defined on host
    """
    if not _has_snapper():
        _print("FATAL: snapper_list_configs() - snapper is not installed")
        return False

    cmd = "snapper list-configs"
    retcode, _ = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: snapper_list_configs() - Could not list configs")
        # print output
        return False

    return True


def snapper_create_config(config_name, fs_type, subvolume, verbose=False):
    if not config_name or not fs_type or not subvolume:
        _print("FAIL: snapper_create_config() - requires config_name, fs_type, sub_volume as parameters")
        return False

    if not _has_snapper():
        _print("FATAL: snapper_create_config() - snapper is not installed")
        return False

    cmd = "snapper -c %s create-config -f '%s' %s" % (config_name, fs_type, subvolume)
    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: snapper_create_config() - Could not create config")
        print(output)
        return False

    return True


def snapper_delete_config(config_name, verbose=False):
    if not config_name:
        _print("FAIL: snapper_delete_config() - requires config_name as parameter")
        return False

    if not _has_snapper():
        _print("FATAL: snapper_delete_config() - snapper is not installed")
        return False

    configs = snapper_query_configs()
    if not configs or config_name not in list(configs.keys()):
        _print("INFO: snapper_delete_config() - config %s does not exist" % config_name)
        return True

    cmd = "snapper -c %s delete-config" % config_name
    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: snapper_delete_config() - Could not delete config")
        print(output)
        return False

    return True


def snapper_list(config_name):
    """
    List all snapshot for specific config name
    """
    if not config_name:
        _print("FAIL: snapper_list() - requires config_name as parameter")
        return False

    if not _has_snapper():
        _print("FATAL: snapper_list() - snapper is not installed")
        return False

    cmd = "snapper -c %s list" % config_name
    retcode, _ = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: snapper_list() - Could not list configs")
        # print output
        return False

    return True


def snapper_create(config_name, snap_type, pre_num=None, verbose=False):
    """
    Create an snapshot on specific config name
    Return snapshot number
    """
    if not config_name or not snap_type:
        _print("FAIL: snapper_create() - requires config_name and type as parameters")
        return None

    if not _has_snapper():
        _print("FATAL: snapper_create() - snapper is not installed")
        return None

    cmd = "snapper -c %s create -p -t %s" % (config_name, snap_type)
    if snap_type == "post":
        if not pre_num:
            _print("FAIL: snapper_create() - snapshot type %s requires pre_num parameter" % snap_type)
            return None
        cmd += " --pre-num %s" % pre_num
    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: snapper_create() - Could not create snap")
        print(output)
        return None

    return output


def snapper_delete(config_name, snap_num, sync=True, verbose=False):
    """
    Delete an snapshot on specific config name
    Return
        True
    or
        False
    """
    if not config_name or not snap_num:
        _print("FAIL: snapper_delete() - requires config_name and snap_num as parameters")
        return None

    if not _has_snapper():
        _print("FATAL: snapper_delete() - snapper is not installed")
        return None

    cmd = "snapper -c %s delete" % config_name
    if sync:
        cmd += " -s"
    cmd += " %s" % snap_num
    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: snapper_delete() - Could not delete snap %s" % snap_num)
        print(output)
        return False

    return True


def snapper_status(config_name, first_snap, last_snap):
    """
    Show what changed between 2 snapshot versions on specific config name
    Return
        True
    or
        False
    """
    if not config_name or not first_snap or not last_snap:
        _print("FAIL: snapper_status() - requires config_name, first_snap and last_snap as parameters")
        return False

    if not _has_snapper():
        _print("FATAL: snapper_status() - snapper is not installed")
        return False

    cmd = "snapper -c %s status %s..%s" % (config_name, first_snap, last_snap)
    retcode, _ = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: snapper_status() - Could not get status")
        # print output
        return False

    return True


def snapper_diff(config_name, first_snap, last_snap):
    """
    Show diff on on content between 2 snapshot versions on specific config name
    Return
        True
    or
        False
    """
    if not config_name or not first_snap or not last_snap:
        _print("FAIL: snapper_diff() - requires config_name, first_snap and last_snap as parameters")
        return False

    if not _has_snapper():
        _print("FATAL: snapper_diff() - snapper is not installed")
        return False

    cmd = "snapper -c %s diff %s..%s" % (config_name, first_snap, last_snap)
    retcode, _ = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: snapper_diff() - Could not get diff")
        # print output
        return False

    return True


def snapper_query_snapshots(config_name, verbose=False):
    """
    Query all info for all snapshot from a configuration
    Return a dict, the key is the snapshot number
    """
    if not _has_snapper():
        _print("FATAL: snapper_query_snapshots() - snapper is not installed")
        return False

    if not config_name:
        _print("FAIL: snapper_query_snapshots() - requires config_name as parameter")
        return None

    cmd = "snapper -c %s list" % config_name
    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: snapper_query_snapshots() - Could not query snapshots for config %s" % config_name)
        print(output)
        return None

    if not output:
        return None

    lines = output.split("\n")

    # example of output
    # snapper -c bugtest -t 0 list
    # Type   | # | Pre # | Date                         | User | Cleanup | Description | Userdata
    # -------+---+-------+------------------------------+------+---------+-------------+---------
    # single | 0 |       |                              | root |         | current     |
    # pre    | 1 |       | Fri 15 Jul 2016 10:23:09 EDT | root |         |             |
    # pre    | 2 |       | Fri 15 Jul 2016 10:23:10 EDT | root |         |             |

    # First line before receiving snapshot details
    begin_data_regex = re.compile(r"-*\+-*\+-*\+-*\+-*\+-*\+-*\+-*")
    snap_type_index = 0
    snap_num_index = 1
    snap_pre_index = 2
    snap_date_index = 3
    snap_user_index = 4
    snap_cleanup_index = 5
    snap_desc_index = 6
    snap_userdata_index = 7

    query_dict = {}

    found_snapshots = False
    for line in lines:
        # _print("DEBUG: '%s'" % line)
        # skip until find first line containing snapshots
        if not found_snapshots and not begin_data_regex.match(line):
            continue
        if begin_data_regex.match(line):
            # _print("DEBUG: found begin")
            found_snapshots = True
            continue

        # separate snap info into a list
        snap_info = line.split("|")
        if not snap_info:
            continue

        query_dict[snap_info[snap_num_index]] = {}
        snap_dict = query_dict[snap_info[snap_num_index]]
        snap_dict["type"] = snap_info[snap_type_index].strip()
        snap_dict["number"] = snap_info[snap_num_index].strip()
        snap_dict["pre"] = snap_info[snap_pre_index].strip()
        snap_dict["date"] = snap_info[snap_date_index].strip()
        snap_dict["user"] = snap_info[snap_user_index].strip()
        snap_dict["cleanup"] = snap_info[snap_cleanup_index].strip()
        snap_dict["description"] = snap_info[snap_desc_index].strip()
        snap_dict["userdata"] = snap_info[snap_userdata_index].strip()
        # Set empty values to None
        for key in list(snap_dict.keys()):
            if snap_dict[key] == "":
                snap_dict[key] = None

    return query_dict


def snapper_enable_debug_mode():
    """
    Enable snapperd to run on debug mode
    """

    if not _has_snapper():
        _print("FATAL: snapper_enable_debug_mode() - snapper is not installed")
        return False

    snapper_cfg_file = "/usr/share/dbus-1/system-services/org.opensuse.Snapper.service"
    debug_parm = "/usr/sbin/snapperd -d"

    if not os.path.isfile(snapper_cfg_file):
        _print("FAIL: snapper_enable_debug_mode(): Could not find file %s" % snapper_cfg_file)
        return False

    if debug_parm in open(snapper_cfg_file, encoding='UTF-8').read():
        # Already enabled
        return True

    cmd = "sed -ie 's/^Exec=.*/Exec=\\/usr\\/sbin\\/snapperd -d/' %s" % snapper_cfg_file
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: snapper_enable_debug_mode() - command to set snapper -d failed")
        print(output)
        return False

    if debug_parm in open(snapper_cfg_file, encoding='UTF-8').read():
        return True

    return False


def snapper_disable_debug_mode():
    """
    Disable snapperd to run on debug mode
    """

    if not _has_snapper():
        _print("FATAL: snapper_disable_debug_mode() - snapper is not installed")
        return False

    snapper_cfg_file = "/usr/share/dbus-1/system-services/org.opensuse.Snapper.service"
    debug_parm = "/usr/sbin/snapperd -d"

    if not os.path.isfile(snapper_cfg_file):
        _print("FAIL: snapper_disable_debug_mode(): Could not find file %s" % snapper_cfg_file)
        return False

    if debug_parm not in open(snapper_cfg_file, encoding='UTF-8').read():
        # Already disabled
        return True

    cmd = "sed -ie 's/^Exec=.*/Exec=\\/usr\\/sbin\\/snapperd/' %s" % snapper_cfg_file
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: snapper_disable_debug_mode() - command to set snapper failed")
        print(output)
        return False

    if debug_parm not in open(snapper_cfg_file, encoding='UTF-8').read():
        return True

    return False
