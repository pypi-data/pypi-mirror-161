from __future__ import absolute_import, division, print_function, unicode_literals

# Copyright (C) 2018 Red Hat, Inc.
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

"""dmpd.py: Module to manipulate LVM thinp and cache metadata devices and snapshot eras."""

__author__ = "Jakub Krysl"
__copyright__ = "Copyright (c) 2017 Red Hat, Inc. All rights reserved."

import re  # regex
import os
import sys
import libsan.host.lvm
from libsan.host.cmdline import run
from libsan.host.cli_tools import Wrapper
import libsan.host.linux


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def _get_devices():
    lv_list = libsan.host.lvm.lv_query()
    return lv_list


def _get_active_devices():
    cmd = "ls /dev/mapper/"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not find active dm devices")
        return False
    devices = output.split()
    return devices


def _get_device_path(vg_name, lv_name):
    device_path = vg_name + "-" + lv_name
    if "/dev/mapper/" not in device_path:
        device_path = "/dev/mapper/" + device_path
    return device_path


def _check_device(vg_name, lv_name):
    devices = _get_devices()
    device_list = [f["name"] for f in devices]
    if lv_name not in device_list:
        _print("FAIL: %s is not a device" % lv_name)
        return False
    for x in devices:
        if x["name"] == lv_name and x["vg_name"] == vg_name:
            _print("INFO: Found device %s in group %s" % (lv_name, vg_name))
            return True
    return False


def _activate_device(vg_name, lv_name):
    devices_active = _get_active_devices()
    if vg_name + "-" + lv_name not in devices_active:
        ret = libsan.host.lvm.lv_activate(lv_name, vg_name)
        if not ret:
            _print("FAIL: Could not activate device %s" % lv_name)
            return False
        _print("INFO: device %s was activated" % lv_name)
    _print("INFO: device %s is active" % lv_name)
    return True


def _fallocate(_file, size, command_message):
    cmd = "fallocate -l %sM %s" % (size, _file)
    try:
        retcode = run(cmd)
        if retcode != 0:
            _print("FAIL: Command failed with code %s." % retcode)
            _print("FAIL: Could not create file to %s metadata to." % command_message)
            return False
    except OSError as e:
        print("command failed: ", e, file=sys.stderr)
        return False
    return True


def get_help(cmd):
    commands = ["cache_check", "cache_dump", "cache_metadata_size", "cache_repair", "cache_restore", "era_check",
                "era_dump", "era_invalidate", "era_restore", "thin_check", "thin_delta", "thin_dump", "thin_ls",
                "thin_metadata_size", "thin_repair", "thin_restore", "thin_rmap", "thin_show_duplicates", "thin_trim"]
    if cmd not in commands:
        _print("FAIL: Unknown command %s" % cmd)
        return False

    command = "%s -h" % cmd
    retcode = run(command, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not get help for %s." % cmd)
        return False

    return True


def get_version(cmd):
    commands = ["cache_check", "cache_dump", "cache_metadata_size", "cache_repair", "cache_restore", "era_check",
                "era_dump", "era_invalidate", "era_restore", "thin_check", "thin_delta", "thin_dump", "thin_ls",
                "thin_metadata_size", "thin_repair", "thin_restore", "thin_rmap", "thin_show_duplicates", "thin_trim"]
    if cmd not in commands:
        _print("FAIL: Unknown command %s" % cmd)
        return False

    command = "%s -V" % cmd
    retcode = run(command, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not get version of %s." % cmd)
        return False

    return True


def _get_dev_id(dev_id, path=None, lv_name=None, vg_name=None):
    dev_ids = []

    if path is None:
        retcode, data = thin_dump(source_vg=vg_name, source_lv=lv_name, formatting="xml", return_output=True)
        if not retcode:
            _print("FAIL: Could not dump metadata from %s/%s" % (vg_name, lv_name))
            return False
        data_lines = data.splitlines()
        for line in data_lines:
            blocks = line.split()
            for block in blocks:
                if not block.startswith("dev_"):
                    continue
                else:
                    dev_ids.append(int(block[8:-1]))

    else:
        with open(path, "r", encoding='UTF-8') as meta:
            for line in meta:
                blocks = line.split()
                for block in blocks:
                    if not block.startswith("dev_"):
                        continue
                    else:
                        dev_ids.append(int(block[8:-1]))

    if dev_id in dev_ids:
        return True

    return False


def _metadata_size(source=None, lv_name=None, vg_name=None):
    if source is None:
        cmd = "lvs -a --units m"
        ret, data = run(cmd, return_output=True)
        if ret != 0:
            _print("FAIL: Could not list LVs")
        data_line = data.splitlines()
        for line in data_line:
            cut = line.split()
            if not cut or lv_name != cut[0] and vg_name != cut[1]:
                continue
            cut = cut[3]
            cut = cut.split("m")
            size = float(cut[0])
            run(cmd)
            return int(size)
        _print("FAIL: Could not find %s %s in lvs, setting size to 100m" % (lv_name, vg_name))
        return 100
    else:
        return int(os.stat(source).st_size) / 1000000


###########################################
# cache section
###########################################

def cache_check(source_file=None, source_vg=None, source_lv=None, quiet=False, super_block_only=False,
                clear_needs_check_flag=False, skip_mappings=False, skip_hints=False, skip_discards=False, verbose=True):
    """Check cache pool metadata from either file or device.
    The arguments are:
    \tsource_file
    \tsource_vg VG name
    \tsource_lv LV name
    \tquiet Mute STDOUT
    \tsuper_block_only
    \tclear_needs_check_flag
    \tskip_mappings
    \tskip_hints
    \tskip_discards
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """

    options = ""

    if not source_file and (not source_vg or not source_lv):
        _print("FAIL: cache_check requires either source_file OR source_vg and source_lv.")
        return False

    if not source_file:
        ret = _check_device(source_vg, source_lv)
        if not ret:
            return False
        ret = _activate_device(source_vg, source_lv)
        if not ret:
            return False
        device = _get_device_path(source_vg, source_lv)
    else:
        if not os.path.isfile(source_file):
            _print("FAIL: Source file is not a file.")
            return False
        device = source_file

    if quiet:
        options += "--quiet "

    if super_block_only:
        options += "--super-block-only "

    if clear_needs_check_flag:
        options += "--clear-needs-check-flag "

    if skip_mappings:
        options += "--skip-mappings "

    if skip_hints:
        options += "--skip-hints "

    if skip_discards:
        options += "--skip-discards "

    cmd = "cache_check %s %s" % (device, options)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not check %s metadata" % device)
        return False

    return True


def cache_dump(source_file=None, source_vg=None, source_lv=None, output=None, repair=False, verbose=True,
               return_output=False):
    """Dumps cache metadata from device of source file to standard output or file.
    The arguments are:
    \tsource_file
    \tsource_vg VG name
    \tsource_lv LV name
    \toutput specify output xml file
    \treturn_output see 'Returns', not usable with output=True
    \trepair Repair the metadata while dumping it
    Returns:
    \tOnly Boolean if return_output False:
    \t\tTrue if success
    \t'tFalse in case of failure
    \tBoolean and data if return_output True
    """
    options = ""
    data = None

    if return_output and output:
        _print("INFO: Cannot return to both STDOUT and file, returning only to file.")
        return_output = False

    if return_output:
        ret_fail = (False, None)
    else:
        ret_fail = False

    if not source_file and (not source_vg or not source_lv):
        _print("FAIL: cache_dump requires either source_file OR source_vg and source_lv.")
        return ret_fail

    if not source_file:
        ret = _check_device(source_vg, source_lv)
        if not ret:
            return ret_fail
        ret = _activate_device(source_vg, source_lv)
        if not ret:
            return ret_fail
        device = _get_device_path(source_vg, source_lv)
    else:
        if not os.path.isfile(source_file):
            _print("FAIL: Source file is not a file.")
            return ret_fail
        device = source_file

    if output:
        if not os.path.isfile(output):
            size = _metadata_size(source_file, source_lv, source_vg)
            ret = _fallocate(output, size + 1, "dump")
            if not ret:
                return ret_fail
        options += "-o %s " % output

    if repair:
        options += "--repair"

    cmd = "cache_dump %s %s" % (device, options)
    if return_output:
        retcode, data = run(cmd, return_output=True, verbose=verbose)
    else:
        retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not dump %s metadata." % device)
        return ret_fail

    if return_output:
        return True, data
    return True


def cache_repair(source_file=None, source_vg=None, source_lv=None, target_file=None, target_vg=None, target_lv=None,
                 verbose=True):
    """Repairs cache metadata from source file/device to target file/device
    The arguments are:
    \tsource as either source_file OR source_vg and source_lv
    \ttarget as either target_file OR target_vg and target_lv
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """

    if not source_file and (not source_vg or not source_lv):
        _print("FAIL: cache_repair requires either source_file OR source_vg and source_lv as source.")
        return False

    if not target_file and (not target_vg or not target_lv):
        _print("FAIL: cache_repair requires either target_file OR target_vg and target_lv as target.")
        return False

    if not source_file:
        ret = _check_device(source_vg, source_lv)
        if not ret:
            return False
        ret = _activate_device(source_vg, source_lv)
        if not ret:
            return False
        source = _get_device_path(source_vg, source_lv)
    else:
        if not os.path.isfile(source_file):
            _print("FAIL: Source file is not a file.")
            return False
        source = source_file

    if not target_file:
        ret = _check_device(target_vg, target_lv)
        if not ret:
            return False
        ret = _activate_device(target_vg, target_lv)
        if not ret:
            return False
        target = _get_device_path(target_vg, target_lv)
    else:
        if not os.path.isfile(target_file):
            size = _metadata_size(source_file, source_lv, source_vg)
            ret = _fallocate(target_file, size + 1, "repair")
            if not ret:
                return False
        target = target_file

    cmd = "cache_repair -i %s -o %s" % (source, target)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not repair metadata from %s to %s" % (source, target))
        return False

    return True


def cache_restore(source_file, target_vg=None, target_lv=None, target_file=None, quiet=False, metadata_version=None,
                  omit_clean_shutdown=False, override_metadata_version=None, verbose=True):
    """Restores cache metadata from source xml file to target device/file
    The arguments are:
    \tsource_file Source xml file
    \ttarget as either target_file OR target_vg and target_lv
    \tquiet Mute STDOUT
    \tmetadata_version Specify metadata version to restore
    \tomit_clean_shutdown Disable clean shutdown
    \toverride_metadata_version DEBUG option to override metadata version without checking
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """

    options = ""

    if source_file is None:
        _print("FAIL: cache_restore requires source file.")
        return False

    if not target_file and (not target_vg or not target_lv):
        _print("FAIL: cache_restore requires either target_file OR target_vg and target_lv as target.")
        return False

    if not os.path.isfile(source_file):
        _print("FAIL: Source file is not a file.")
        return False

    if not target_file:
        ret = _check_device(target_vg, target_lv)
        if not ret:
            return False
        ret = _activate_device(target_vg, target_lv)
        if not ret:
            return False
        target = _get_device_path(target_vg, target_lv)
    else:
        if not os.path.isfile(target_file):
            size = _metadata_size(source_file)
            ret = _fallocate(target_file, size + 1, "restore")
            if not ret:
                return False
        target = target_file

    if quiet:
        options += "--quiet "

    if metadata_version:
        options += "--metadata-version %s " % metadata_version

    if omit_clean_shutdown:
        options += "--omit-clean-shutdown "

    if override_metadata_version:
        options += "--debug-override-metadata-version %s" % override_metadata_version

    cmd = "cache_restore -i %s -o %s %s" % (source_file, target, options)

    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not restore metadata from %s to %s" % (source_file, target))
        return False

    return True


###########################################
# thinp section
###########################################

def thin_check(source_file=None, source_vg=None, source_lv=None, quiet=False, super_block_only=False,
               clear_needs_check_flag=False, skip_mappings=False, ignore_non_fatal_errors=False, verbose=True):
    """Check thin pool metadata from either file or device.
    The arguments are:
    \tsource_file
    \tsource_vg VG name
    \tsource_lv LV name
    \tquiet Mute STDOUT
    \tsuper_block_only
    \tclear_needs_check_flag
    \tskip_mappings
    \tignore_non_fatal_errors
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """

    options = ""

    if not source_file and (not source_vg or not source_lv):
        _print("FAIL: thin_check requires either source_file OR source_vg and source_lv.")
        return False

    if not source_file:
        ret = _check_device(source_vg, source_lv)
        if not ret:
            return False
        ret = _activate_device(source_vg, source_lv)
        if not ret:
            return False
        device = _get_device_path(source_vg, source_lv)
    else:
        if not os.path.isfile(source_file):
            _print("FAIL: Source file is not a file.")
            return False
        device = source_file

    if quiet:
        options += "--quiet "

    if super_block_only:
        options += "--super-block-only "

    if clear_needs_check_flag:
        options += "--clear-needs-check-flag "

    if skip_mappings:
        options += "--skip-mappings "

    if ignore_non_fatal_errors:
        options += "--ignore-non-fatal-errors "

    cmd = "thin_check %s %s" % (device, options)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not check %s metadata" % device)
        return False

    return True


def thin_ls(source_vg, source_lv, no_headers=False, fields=None, snapshot=False, verbose=True):
    """List information about thin LVs on thin pool.
    The arguments are:
    \tsource_vg VG name
    \tsource_lv LV name
    \tfields list of fields to output, default is all
    \tsnapshot If use metadata snapshot, able to run on live snapshotted pool
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """

    options = ""

    if not source_vg or not source_lv:
        _print("FAIL: thin_ls requires source_vg and source_lv.")
        return False

    ret = _check_device(source_vg, source_lv)
    if not ret:
        return False
    ret = _activate_device(source_vg, source_lv)
    if not ret:
        return False
    device = _get_device_path(source_vg, source_lv)

    if no_headers:
        options += "--no-headers "

    fields_possible = ["DEV", "MAPPED_BLOCKS", "EXCLUSIVE_BLOCKS", "SHARED_BLOCKS", "MAPPED_SECTORS",
                       "EXCLUSIVE_SECTORS", "SHARED_SECTORS", "MAPPED_BYTES", "EXCLUSIVE_BYTES", "SHARED_BYTES",
                       "MAPPED", "EXCLUSIVE", "TRANSACTION", "CREATE_TIME", "SHARED", "SNAP_TIME"]
    if fields is None:
        options += " --format \"%s\" " % ",".join([str(i) for i in fields_possible])
    else:
        for field in fields:
            if field not in fields_possible:
                _print("FAIL: Unknown field %s specified." % field)
                _print("INFO: Possible fields are: %s" % ", ".join([str(i) for i in fields_possible]))
                return False
        options += " --format \"%s\" " % ",".join([str(i) for i in fields])

    if snapshot:
        options += "--metadata-snap"

    cmd = "thin_ls %s %s" % (device, options)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not list %s metadata" % device)
        return False

    return True


def thin_dump(source_file=None, source_vg=None, source_lv=None, output=None, repair=False, formatting=None,
              snapshot=None, dev_id=None, skip_mappings=False, verbose=True, return_output=False):
    """Dumps thin metadata from device of source file to standard output or file.
    The arguments are:
    \tsource_file
    \tsource_vg VG name
    \tsource_lv LV name
    \toutput specify output xml file
    \treturn_output see 'Returns', not usable with output=True
    \trepair Repair the metadata while dumping it
    \tformatting Specify output format [xml, human_readable, custom='file']
    \tsnapshot (Boolean/Int) Use metadata snapshot. If Int provided, specifies block number
    \tdev_id ID of the device
    Returns:
    \tOnly Boolean if return_output False:
    \t\tTrue if success
    \t'tFalse in case of failure
    \tBoolean and data if return_output True
    """
    options = ""
    data = None

    if return_output and output:
        _print("INFO: Cannot return to both STDOUT and file, returning only to file.")
        return_output = False

    if return_output:
        ret_fail = (False, None)
    else:
        ret_fail = False

    if not source_file and (not source_vg or not source_lv):
        _print("FAIL: thin_dump requires either source_file OR source_vg and source_lv.")
        return ret_fail

    if not source_file:
        ret = _check_device(source_vg, source_lv)
        if not ret:
            return ret_fail
        ret = _activate_device(source_vg, source_lv)
        if not ret:
            return ret_fail
        device = _get_device_path(source_vg, source_lv)
    else:
        if not os.path.isfile(source_file):
            _print("FAIL: Source file is not a file.")
            return ret_fail
        device = source_file

    if output:
        if not os.path.isfile(output):
            size = _metadata_size(source_file, source_lv, source_vg)
            ret = _fallocate(output, size + 1, "dump")
            if not ret:
                return ret_fail
        options += "-o %s " % output

    if repair:
        options += "--repair "

    if snapshot:
        if isinstance(snapshot, bool):
            options += "--metadata-snap "
        elif isinstance(snapshot, int):
            options += "--metadata-snap %s " % snapshot
        else:
            _print("FAIL: Unknown snapshot value, use either Boolean or Int.")
            return ret_fail

    if formatting:
        if formatting in ["xml", "human_readable"]:
            options += "--format %s " % formatting
        elif formatting.startswith("custom="):
            if not os.path.isfile(formatting[8:-1]):
                _print("FAIL: Specified custom formatting file is not a file.")
                return ret_fail
            options += "--format %s " % formatting
        else:
            _print("FAIL: Unknown formatting specified, please use one of [xml, human_readable, custom='file'].")
            return ret_fail

    if dev_id:
        if isinstance(dev_id, int):
            if _get_dev_id(dev_id, source_file, source_lv, source_vg):
                options += "--dev-id %s " % dev_id
            else:
                _print("FAIL: Unknown dev_id value, device with ID %s does not exist." % dev_id)
                return ret_fail
        else:
            _print("FAIL: Unknown dev_id value, must be Int.")
            return ret_fail

    if skip_mappings:
        options += "--skip-mappings "

    cmd = "thin_dump %s %s" % (device, options)
    if return_output:
        retcode, data = run(cmd, return_output=True, verbose=verbose)
    else:
        retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not dump %s metadata." % device)
        return ret_fail

    if return_output:
        return True, data
    return True


def thin_restore(source_file, target_vg=None, target_lv=None, target_file=None, quiet=False, verbose=True):
    """Restores thin metadata from source xml file to target device/file
    The arguments are:
    \tsource_file Source xml file
    \ttarget as either target_file OR target_vg and target_lv
    \tquiet Mute STDOUT
    \tmetadata_version Specify metadata version to restore
    \tomit_clean_shutdown Disable clean shutdown
    \toverride_metadata_version DEBUG option to override metadata version without checking
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """

    options = ""

    if source_file is None:
        _print("FAIL: thin_restore requires source file.")
        return False

    if not target_file and (not target_vg or not target_lv):
        _print("FAIL: thin_restore requires either target_file OR target_vg and target_lv as target.")
        return False

    if not os.path.isfile(source_file):
        _print("FAIL: Source file is not a file.")
        return False

    if not target_file:
        ret = _check_device(target_vg, target_lv)
        if not ret:
            return False
        ret = _activate_device(target_vg, target_lv)
        if not ret:
            return False
        target = _get_device_path(target_vg, target_lv)
    else:
        if not os.path.isfile(target_file):
            size = _metadata_size(source_file)
            ret = _fallocate(target_file, size + 1, "restore")
            if not ret:
                return False
        target = target_file

    if quiet:
        options += "--quiet"

    cmd = "thin_restore -i %s -o %s %s" % (source_file, target, options)

    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not restore metadata from %s to %s" % (source_file, target))
        return False

    return True


def thin_repair(source_file=None, source_vg=None, source_lv=None, target_file=None, target_vg=None, target_lv=None,
                verbose=True):
    """Repairs thin metadata from source file/device to target file/device
    The arguments are:
    \tsource as either source_file OR source_vg and source_lv
    \ttarget as either target_file OR target_vg and target_lv
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """

    if not source_file and (not source_vg or not source_lv):
        _print("FAIL: thin_repair requires either source_file OR source_vg and source_lv as source.")
        return False

    if not target_file and (not target_vg or not target_lv):
        _print("FAIL: thin_repair requires either target_file OR target_vg and target_lv as target.")
        return False

    if not source_file:
        ret = _check_device(source_vg, source_lv)
        if not ret:
            return False
        ret = _activate_device(source_vg, source_lv)
        if not ret:
            return False
        source = _get_device_path(source_vg, source_lv)
    else:
        if not os.path.isfile(source_file):
            _print("FAIL: Source file is not a file.")
            return False
        source = source_file

    if not target_file:
        ret = _check_device(target_vg, target_lv)
        if not ret:
            return False
        ret = _activate_device(target_vg, target_lv)
        if not ret:
            return False
        target = _get_device_path(target_vg, target_lv)
    else:
        if not os.path.isfile(target_file):
            size = _metadata_size(source_file, source_lv, source_vg)
            ret = _fallocate(target_file, size + 1, "repair")
            if not ret:
                return False
        target = target_file

    cmd = "thin_repair -i %s -o %s" % (source, target)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not repair metadata from %s to %s" % (source, target))
        return False

    return True


def thin_rmap(region, source_file=None, source_vg=None, source_lv=None, verbose=True):
    """Output reverse map of a thin provisioned region of blocks from metadata device.
    The arguments are:
    \tsource_vg VG name
    \tsource_lv LV name
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """

    if not source_file and (not source_vg or not source_lv):
        _print("FAIL: thin_rmap requires either source_file OR source_vg and source_lv as source.")
        return False

    if not source_file:
        ret = _check_device(source_vg, source_lv)
        if not ret:
            return False
        ret = _activate_device(source_vg, source_lv)
        if not ret:
            return False
        device = _get_device_path(source_vg, source_lv)
    else:
        if not os.path.isfile(source_file):
            _print("FAIL: Source file is not a file.")
            return False
        device = source_file

    regions = region.split(".")
    try:
        int(regions[0])
        if regions[1] != '':
            raise ValueError
        int(regions[2])
        if regions[3] is not None:
            raise ValueError
    except ValueError:
        print("FAIL: Region must be in format 'INT..INT'")
        return False
    except IndexError:
        pass
    # region 1..-1 must be valid, using usigned 32bit ints
    if int(regions[0]) & 0xffffffff >= int(regions[2]) & 0xffffffff:
        print("FAIL: Beginning of the region must be before its end.")
        return False
    options = "--region %s" % region

    cmd = "thin_rmap %s %s" % (device, options)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not output reverse map from %s metadata device" % device)
        return False

    return True


def thin_trim(data_vg, data_lv, metadata_vg=None, metadata_lv=None, metadata_file=None, verbose=True):
    """Issue discard requests for free pool space.
    The arguments are:
    \tdata_vg VG name of data device
    \tdata_lv LV name of data device
    \tmetadata_vg VG name of metadata device
    \t metadata_lv LV name of metadata device
    \tmetadata_file file with metadata
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """
    options = ""

    if not data_vg or not data_lv:
        _print("FAIL: thin_trim requires data_vg and data_lv.")
        return False

    if not metadata_file and (not metadata_vg or not metadata_lv):
        _print("FAIL: thin_trim requires either metadata_file OR metadata_vg and metadata_lv as target.")
        return False

    ret = _check_device(data_vg, data_lv)
    if not ret:
        return False

    ret = _activate_device(data_vg, data_lv)
    if not ret:
        return False

    if not metadata_file:
        ret = _check_device(metadata_vg, metadata_lv)
        if not ret:
            return False
        ret = _activate_device(metadata_vg, metadata_lv)
        if not ret:
            return False
        metadata_dev = _get_device_path(metadata_vg, metadata_lv)
    else:
        if not os.path.isfile(metadata_file):
            _print("FAIL: metadata_file %s is not a file." % metadata_file)
            return False
        metadata_dev = metadata_file

    data_dev = _get_device_path(data_vg, data_lv)
    cmd = "thin_trim --data-dev %s --metadata-dev %s %s" % (data_dev, metadata_dev, options)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not discard free pool space on device %s with metadata device %s." %
               (data_dev, metadata_dev))
        return False

    return True


def thin_delta(thin1, thin2, source_file=None, source_vg=None, source_lv=None, snapshot=False, verbosity=False,
               verbose=True):
    """Print the differences in the mappings between two thin devices..
    The arguments are:
    \tsource_vg VG name
    \tsource_lv LV name
    \tthin1 numeric identificator of first thin volume
    \tthin2 numeric identificator of second thin volume
    \tsnapshot (Boolean/Int) Use metadata snapshot. If Int provided, specifies block number
    \tverbosity Provide extra information on the mappings
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """

    options = ""

    if not source_file and (not source_vg or not source_lv):
        _print("FAIL: thin_delta requires either source_file OR source_vg and source_lv.")
        return False

    if not source_file:
        ret = _check_device(source_vg, source_lv)
        if not ret:
            return False
        ret = _activate_device(source_vg, source_lv)
        if not ret:
            return False
        device = _get_device_path(source_vg, source_lv)
    else:
        if not os.path.isfile(source_file):
            _print("FAIL: Source file is not a file.")
            return False
        device = source_file

    if snapshot:
        if isinstance(snapshot, bool):
            options += "--metadata-snap "
        elif isinstance(snapshot, int):
            options += "--metadata-snap %s " % snapshot
        else:
            _print("FAIL: Unknown snapshot value, use either Boolean or Int.")
            return False

    if verbosity:
        options += "--verbose"

    if _get_dev_id(thin1, source_file, source_lv, source_vg) and _get_dev_id(thin2, source_file, source_lv, source_vg):
        cmd = "thin_delta %s --thin1 %s --thin2 %s %s" % (options, thin1, thin2, device)
        retcode = run(cmd, verbose=verbose)
        if retcode != 0:
            _print("FAIL: Could not get differences in mappings between two thin LVs.")
            return False
    else:
        _print("FAIL: Specified ID does not exist.")
        return False
    return True


class DMPD(Wrapper):
    def __init__(self, disable_check=True):
        self.disable_check = disable_check

        pkg = "device-mapper-persistent-data"
        if not libsan.host.linux.is_installed(pkg):
            if not libsan.host.linux.install_package(pkg, check=False):
                _print("FATAL: Could not install %s package" % pkg)

        self.commands = {"cache_check": "cache_check",
                         "cache_dump": "cache_dump",
                         "cache_metadata_size": "cache_metadata_size",
                         "cache_repair": "cache_repair",
                         "cache_restore": "cache_restore",
                         "cache_writeback": "cache_writeback",
                         "thin_check": "thin_check",
                         "thin_delta": "thin_delta",
                         "thin_dump": "thin_dump",
                         "thin_ls": "thin_ls",
                         "thin_metadata_size": "thin_metadata_size",
                         "thin_repair": "thin_repair",
                         "thin_restore": "thin_restore",
                         "thin_rmap": "thin_rmap",
                         "thin_trim": "thin_trim"}
        self.commands["all"] = list(self.commands.keys())
        self.arguments = {
            "help": [self.commands["all"], " --help"],
            "version": [self.commands["all"], " --version"],
            "verbose": [self.commands["all"], " --verbose"],
            "block_size": [["cache_metadata_size", "thin_metadata_size"], " --block-size&"],
            "buffer_size": [["cache_writeback"], " --buffer-size-meg&"],
            "clear_needs_check_flag": [["cache_check", "thin_check"], " --clear-needs-check-flag"],
            "data_dev": [["thin_trim"], " --data-dev&"],
            "debug_override_metadata_version": [["cache_restore"], " --debug-override-metadata-version&"],
            "dev_id": [["thin_dump"], " --dev-id&"],
            "device_size": [["cache_metadata_size"], " --device-size&"],
            "fast_device": [["cache_writeback"], " --fast-device&"],
            "format": [["thin_ls", "thin_dump"], " --format&"],
            "ignore_non_fatal_errors": [["thin_check"], " --ignore-non-fatal-errors"],
            "input": [["cache_repair", "cache_restore", "thin_repair", "thin_restore"], " -i&"],
            "list_failed_blocks": [["cache_writeback"], " --list-failed-blocks"],
            "max_hint_width": [["cache_metadata_size"], " --max-hint-width&"],
            "max_thins": [["thin_metadata_size"], " --max-thins&"],
            "metadata_dev": [["thin_trim"], " --metadata-dev&"],
            "metadata_device": [["cache_writeback"], " --metadata-device&"],
            "metadata_snap": [["thin_dump", "thin_delta"], " --metadata-snap&"],
            "metadata_version": [["cache_restore"], " --metadata-version&"],
            "no_headers": [["thin_ls"], " --no-headers"],
            "no_metadata_update": [["cache_writeback"], " --no-metadata-update"],
            "nr_blocks": [["cache_metadata_size"], " --nr-blocks&"],
            "numeric_only": [["thin_metadata_size"], " --numeric-only"],
            "numeric_only_type": [["thin_metadata_size"], " --numeric-only="],
            "omit_clean_shutdown": [["cache_restore"], " --omit-clean-shutdown"],
            "origin_device": [["cache_writeback"], " --origin-device&"],
            "output": [["cache_dump", "cache_repair", "cache_restore", "thin_dump", "thin_repair", "thin_restore"],
                       " -o&"],
            "override_mapping_root": [["thin_check"], " --override-mapping-root&"],
            "pool_size": [["thin_metadata_size"], " --pool-size&"],
            "quiet": [["cache_check", "cache_restore", "thin_check", "thin_restore"], " --quiet"],
            "region": [["thin_rmap"], " --region&"],
            "repair": [["cache_dump", "thin_dump"], " --repair"],
            "skip_discards": [["cache_check"], " --skip-discards"],
            "skip_hints": [["cache_check"], " --skip-hints"],
            "skip_mappings": [["thin_check", "thin_dump"], " --skip-mappings"],
            "snap1": [["thin_delta"], " --snap1&"],
            "snap2": [["thin_delta"], " --snap2&"],
            "snapshot": [["thin_ls", "thin_dump", "thin_delta"], " --metadata-snap"],
            "super_block_only": [["cache_check", "thin_check"], " --super-block-only"],
            "thin1": [["thin_delta"], " --thin1&"],
            "thin2": [["thin_delta"], " --thin2&"],
            "unit": [["thin_metadata_size"], " --unit&"]
        }

        Wrapper.__init__(self, self.commands, self.arguments, self.disable_check)

    @staticmethod
    def _remove_nones(kwargs):
        return {k: v for k, v in kwargs.items() if v is not None}

    def _get_possible_arguments(self, command=None):
        return super(DMPD, self)._get_possible_arguments(command.split()[0])

    def _run(self, cmd, verbosity=True, return_output=False, **kwargs):
        # Constructs the command to run and runs it
        cmd = self._add_arguments(cmd, **kwargs)

        ret = run(cmd, verbose=verbosity, return_output=return_output)
        if isinstance(ret, tuple) and ret[0] != 0:
            _print("WARN: Running command: '%s' failed. Return with output." % cmd)
        elif isinstance(ret, int) and ret != 0:
            _print("WARN: Running command: '%s' failed." % cmd)
        return ret

    def cache_check(self, source_file=None, source_vg=None, source_lv=None, **kwargs):
        cmd = "cache_check "
        if source_file:
            cmd += "%s " % source_file
        if source_vg and source_lv:
            cmd += "%s " % _get_device_path(source_vg, source_lv)
        return self._run(cmd, **self._remove_nones(kwargs))

    def cache_dump(self, source_file=None, source_vg=None, source_lv=None, **kwargs):
        cmd = "cache_dump "
        if source_file:
            cmd += "%s " % source_file
        if source_vg and source_lv:
            cmd += "%s " % _get_device_path(source_vg, source_lv)
        return self._run(cmd, **self._remove_nones(kwargs))

    def cache_metadata_size(self, **kwargs):
        cmd = "cache_metadata_size "
        return self._run(cmd, **self._remove_nones(kwargs))

    def cache_repair(self, **kwargs):
        cmd = "cache_repair "
        return self._run(cmd, **self._remove_nones(kwargs))

    def cache_restore(self, **kwargs):
        cmd = "cache_restore "
        return self._run(cmd, **self._remove_nones(kwargs))

    def cache_writeback(self, **kwargs):
        cmd = "cache_writeback "
        return self._run(cmd, **self._remove_nones(kwargs))

    def thin_check(self, source_file=None, source_vg=None, source_lv=None, **kwargs):
        cmd = "thin_check "
        if source_file:
            cmd += "%s " % source_file
        if source_vg and source_lv:
            cmd += "%s " % _get_device_path(source_vg, source_lv)
        return self._run(cmd, **self._remove_nones(kwargs))

    def thin_delta(self, source_file=None, source_vg=None, source_lv=None, **kwargs):
        cmd = "thin_delta "
        if source_file:
            cmd += "%s " % source_file
        if source_vg and source_lv:
            cmd += "%s " % _get_device_path(source_vg, source_lv)
        return self._run(cmd, **self._remove_nones(kwargs))

    def thin_dump(self, source_file=None, source_vg=None, source_lv=None, **kwargs):
        cmd = "thin_dump "
        if source_file:
            cmd += "%s " % source_file
        if source_vg and source_lv:
            cmd += "%s " % _get_device_path(source_vg, source_lv)
        return self._run(cmd, **self._remove_nones(kwargs))

    def thin_ls(self, source_vg=None, source_lv=None, **kwargs):
        cmd = "thin_ls "
        if source_vg and source_lv:
            cmd += _get_device_path(source_vg, source_lv)
        return self._run(cmd, **self._remove_nones(kwargs))

    def thin_metadata_size(self, **kwargs):
        cmd = "thin_metadata_size "
        return self._run(cmd, **self._remove_nones(kwargs))

    def thin_repair(self, **kwargs):
        cmd = "thin_repair "
        return self._run(cmd, **self._remove_nones(kwargs))

    def thin_restore(self, **kwargs):
        cmd = "thin_restore "
        return self._run(cmd, **self._remove_nones(kwargs))

    def thin_rmap(self, source_file=None, source_vg=None, source_lv=None, **kwargs):
        cmd = "thin_rmap "
        if source_file:
            cmd += "%s " % source_file
        if source_vg and source_lv:
            cmd += "%s " % _get_device_path(source_vg, source_lv)
        return self._run(cmd, **self._remove_nones(kwargs))

    def thin_trim(self, **kwargs):
        cmd = "thin_trim "
        return self._run(cmd, **self._remove_nones(kwargs))
