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

"""scsi.py: Module to manipulate SCSI devices."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import os.path
import re  # regex
import libsan.host.mp
import libsan.host.linux
import libsan.host.lvm
import libsan.host.net
import libsan.misc.array
import libsan.misc.size
from libsan.host.cmdline import run
from os import listdir, readlink

# I'm still note sure whether to use /sys/class/scsi_disk or /sys/class/scsi_device

sys_disk_path = "/sys/class/scsi_disk"
host_path = "/sys/class/scsi_host"

# add /lib/udev to PATH because scsi_id is located there on RHEL7
os.environ['PATH'] += ":/lib/udev"


def get_regex_scsi_id():
    return "([0-9]+):([0-9]+):([0-9]+):([0-9]+)"


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


def is_scsi_device(scsi_device):
    """
    """
    if re.match("^sd[a-z]+$", scsi_device):
        return True
    else:
        return False


def get_scsi_disk_ids():
    """Return an array of scsi_ids. If an scsi_device name is given as
    parameter, then just the id of the device is returned (TODO)
    The arguments are:
    \tNone
    \tDevice name: eg. sda
    Returns:
    \tarray: Return an array of SCSI IDs
    """
    cmd = "ls %s" % sys_disk_path
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    device_ids = output.split()
    return device_ids


def get_scsi_disk_name(device_id):
    if not device_id:
        _print("FAIL: get_scsi_disk_name() requires scsi_device_id as parameter")
        return None

    cmd = "ls %s/%s/device/block" % (sys_disk_path, device_id)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    device_name = output
    return device_name


def get_scsi_disk_vendor(device_id):
    if not device_id:
        _print("FAIL: get_scsi_disk_vendor() requires scsi_device_id as parameter")
        return None

    cmd = "cat %s/%s/device/vendor" % (sys_disk_path, device_id)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    device_vendor = output
    return device_vendor


def get_scsi_disk_model(device_id):
    if not device_id:
        _print("FAIL: get_scsi_disk_model() requires scsi_device_id as parameter")
        return None

    cmd = "cat %s/%s/device/model" % (sys_disk_path, device_id)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    device_model = output
    return device_model


def query_all_scsi_disks(scsi_disk=None):
    """
    Query information of all SCSI disks and return them as a dict
    SCSI ID is the dict key.
    If an SCSI disk is given as argument, return its info
    Parameter:
    \tscsi_disk (option):        SCSI disk name. eg: 'sda'
    """
    disk_ids = get_scsi_disk_ids()
    if not disk_ids:
        # Could not find any SCSI device
        return None

    scsi_disks = {}
    for disk_id in disk_ids:
        scsi_name = get_scsi_disk_name(disk_id)
        if scsi_disk and scsi_name and scsi_disk != scsi_name:
            # optmization in case we requested specific disk, do not query all
            continue
        if not scsi_name:
            _print("WARN: Could not get scsi_name for disk_id '%s'." % disk_id)
            scsi_wwid = scsi_wwn = udev_wwn = size_bytes = state = timeout = None
        else:
            scsi_wwid = wwid_of_disk(scsi_name)
            scsi_wwn = wwn_of_disk(scsi_name)
            udev_wwn = udev_wwn_of_disk(scsi_name)
            size_bytes = size_of_disk(scsi_name)
            state = disk_sys_check(scsi_name)
            timeout = timeout_of_disk(scsi_name)
        scsi_vendor = get_scsi_disk_vendor(disk_id)
        scsi_model = get_scsi_disk_model(disk_id)
        m = re.match(get_regex_scsi_id(), disk_id)
        host_id = None
        driver = None
        if m:
            host_id = m.group(1)
            driver = scsi_driver_of_host_id(host_id)
        scsi_info = {"name": scsi_name,
                     "wwid": scsi_wwid,
                     "wwn": scsi_wwn,  # Uses scsi_id to query WWN
                     "udev_wwn": udev_wwn,  # Used udevadm to query WWN
                     "size": size_bytes,
                     "size_human": libsan.misc.size.size_bytes_2_size_human(size_bytes),
                     "state": state,
                     "timeout": timeout,
                     "vendor": scsi_vendor,
                     "model": scsi_model,
                     "host_id": host_id,
                     "driver": driver,
                     "scsi_id": disk_id}
        scsi_disks[disk_id] = scsi_info

    if scsi_disk:
        for disk_id in list(scsi_disks.keys()):
            if scsi_disk == scsi_disks[disk_id]["name"]:
                return scsi_disks[disk_id]
        return None

    return scsi_disks


def get_scsi_name_by_vendor(vendor):
    """
    Query information of all SCSI disks and return all scsi device names that
    are from the requested vendor
    Parameter:
    \tvendor:        SCSI disk Vendor. eg: 'LIO'
    Return:
    \tList:          List of SCSI names
    """
    if not vendor:
        _print("FAIL: get_scsi_name_by_vendor() - requires vendor parameter")
        return None

    all_scsi_disks_info = query_all_scsi_disks()
    if not all_scsi_disks_info:
        return None
    scsi_names = []
    for scsi_info in list(all_scsi_disks_info.values()):
        if "vendor" in list(scsi_info.keys()):
            if scsi_info["vendor"] == vendor:
                scsi_names.append(scsi_info["name"])
    return scsi_names


def scsi_host_of_scsi_name(scsi_name):
    """
    """
    if not scsi_name:
        _print("FAIL: scsi_host_of_scsi_name() - requires scsi_name parameter")
        return None

    scsi_disk_info = query_all_scsi_disks(scsi_name)
    if not scsi_disk_info:
        _print("WARN: scsi_host_of_scsi_name() did not query info for %s" % scsi_name)
        return None
    return scsi_disk_info["host_id"]


def scsi_name_2_scsi_id(scsi_name):
    """
    """
    if not scsi_name:
        _print("FAIL: scsi_name_2_scsi_id() - requires scsi_name parameter")
        return None

    scsi_disk_info = query_all_scsi_disks(scsi_name)
    if not scsi_disk_info:
        _print("WARN: scsi_name_2_scsi_id() did not query info for %s" % scsi_name)
        return None
    return scsi_disk_info["scsi_id"]


def delete_disk(device_name):
    """
    device_name:    eg. sda
    """
    if not device_name:
        _print("FAIL: delete_disk() requires scsi_device_name as parameter")
        return None

    device_id = scsi_name_2_scsi_id(device_name)
    if not device_id:
        _print("FAIL: delete_disk() could not find disk %s" % device_name)
        return None

    cmd = "echo \"1\" >  %s/%s/device/delete" % (sys_disk_path, device_id)
    retcode = run(cmd, verbose=False)
    if retcode != 0:
        return None
    return True


def get_hosts(somethings=None):
    """
    Return a list with all SCSI hosts.
    The arguments are:
    \tNone
    or
    \tscsi_disk     eg. sda
    or
    \tscsi_id       eg. 3:0:0:1
    Returns:
    \tHost list     if no problem executing command
    \tNone          if something went wrong
    """

    cmd = "ls %s" % host_path
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    # remove 'host' prefix
    output = re.sub("host", "", output)
    all_host_ids = output.split()
    if not somethings:
        return all_host_ids

    scsi_host_ids = None
    # If somethings is a single string, convert it to list
    for something in somethings if not isinstance(somethings, type("")) else [somethings]:
        if something is None:
            _print("FAIL: get_hosts() - Invalid input")
            print(somethings)
            return None
        m = re.match(get_regex_scsi_id(), something)
        if m and m.group(1) in all_host_ids:
            if not scsi_host_ids:
                scsi_host_ids = []
            if m.group(1) not in scsi_host_ids:
                scsi_host_ids.append(m.group(1))
        else:
            # Assume it is scsi_disk name, such as sda
            scsi_id = scsi_name_2_scsi_id(something)
            m = re.match(get_regex_scsi_id(), scsi_id)
            if m and m.group(1) in all_host_ids:
                if not scsi_host_ids:
                    scsi_host_ids = []
                if m.group(1) not in scsi_host_ids:
                    scsi_host_ids.append(m.group(1))

    if not scsi_host_ids:
        return None
    scsi_host_ids = libsan.misc.array.dedup(scsi_host_ids)
    return scsi_host_ids


def query_scsi_host_info(host_id):
    """
    Usage
        query_scsi_host_info(scsi_host_id)
    Purpose
        Save sysfs info of "/sys/class/scsi_host/host$scsi_host_id" to
            scsi_host_info
        We also check these folders:
            /sys/class/iscsi_host/host$scsi_host_id/
            /sys/class/fc_host/host$scsi_host_id/
    Parameter
        scsi_host_id           # like '0' for host0
    Returns
        scsi_host_info
            or
        None
    """
    if not host_id:
        _print("FAIL: query_scsi_host_info() - requires host_id")
        return None

    sysfs_folder = "/sys/class/scsi_host/host%s" % host_id
    if not os.path.isdir(sysfs_folder):
        _print("FAIL: %s is not a valid directory" % host_id)
        return None

    scsi_host_info = dict()
    scsi_host_info["scsi_host_id"] = host_id
    scsi_host_info["pci_id"] = pci_id_of_host_id(host_id)
    scsi_host_info["driver"] = scsi_driver_of_host_id(host_id)

    param_files = [f for f in listdir(sysfs_folder) if os.path.isfile(os.path.join(sysfs_folder, f))]
    for param in param_files:
        ret, output = run("cat %s/%s" % (sysfs_folder, param), return_output=True, verbose=False)
        if ret != 0:
            # For some reason could not read the file
            continue
        scsi_host_info[param] = ", ".join(output.split("\n"))

    sysfs_hosts = ["/sys/class/iscsi_host/host%s" % host_id, "/sys/class/fc_host/host%s" % host_id]
    for sysfs_host in sysfs_hosts:
        if not os.path.isdir(sysfs_host):
            continue
        host_files = [x for x in listdir(sysfs_host) if os.path.isfile(os.path.join(sysfs_host, x))]
        for param in host_files:
            ret, output = run("cat %s/%s" % (sysfs_host, param), return_output=True, verbose=False)
            if ret != 0:
                # For some reason could not read the file
                continue
            scsi_host_info[param] = ", ".join(output.split("\n"))

    return scsi_host_info


def scsi_driver_of_host_id(host_id):
    """
    """
    if not host_id:
        _print("FAIL: scsi_driver_of_host_id() - requires host_id parameter")
        return None
    scsi_drv_sysfs = "/sys/class/scsi_host/host%s/proc_name" % host_id
    if not os.path.isfile(scsi_drv_sysfs):
        _print("FAIL: %s is not a valid path" % scsi_drv_sysfs)
        return None

    _, output = run("cat %s" % scsi_drv_sysfs, return_output=True, verbose=False)
    scsi_driver = output
    if scsi_driver == "(null)" or scsi_driver == "":
        # Driver information was not exported, let try to find it out some other way
        lpfc_sysfs_file = "/sys/class/scsi_host/host%s/lpfc_drvr_version" % host_id
        if os.path.isfile(lpfc_sysfs_file):
            return "lpfc"

        driver_sysfs_file = "/sys/class/scsi_host/host%s/driver_name" % host_id
        if os.path.isfile(driver_sysfs_file):
            _, output = run("cat %s" % driver_sysfs_file, return_output=True, verbose=False)
            return output

        model_sysfs_file = "/sys/class/scsi_host/host%s/model_name" % host_id
        if os.path.isfile(model_sysfs_file):
            _, output = run("cat %s" % model_sysfs_file, return_output=True, verbose=False)
            if re.match("^QLE", output):
                return "qla2xxx"

        symbolic_sysfs_file = "/sys/class/fc_host/host%s/symbolic_name" % host_id
        if os.path.isfile(symbolic_sysfs_file):
            _, output = run("cat %s" % symbolic_sysfs_file, return_output=True, verbose=False)
            if re.search("bnx2fc", output):
                return "bnx2fc"

        pci_id = pci_id_of_host_id(host_id)
        if pci_id:
            lspci_regex = r"Kernel modules:\s+(\S+)"
            _, output = run("lspci -s \"%s\" -v | grep \"Kernel modules:\"" % pci_id, return_output=True, verbose=False)
            if output:
                m = re.search(lspci_regex, output)
                if m:
                    return m.group(1)

        _print("FAIL: Could not get driver name for SCSI host%s" % host_id)
        return None
    else:
        # Intel cards export driver name as fcoe, but the network driver used is ixgbe for transport is ixgbe
        if scsi_driver == "fcoe":
            drv_version_path = "/sys/class/fc_host/host%s/driver_version" % host_id
            _, output = run("cat %s" % drv_version_path, return_output=True, verbose=False)
            if re.search("ixgbe", output):
                return "ixgbe"
    return scsi_driver


def pci_id_of_host_id(host_id):
    """
    Usage
        pci_id_of(scsi_host_id);
    Purpose
        Find out which PCI ID providing the SCSI Host via:
            readlink("/sys/class/scsi_host/host'scsi_host_id'");
    Parameter
        $scsi_host_id           # like '0' for host0
    Returns
        pci_id                 # like '0000:00:1c.0'
    """
    if not host_id:
        _print("FAIL: pci_id_of_host_id() - requires host_id parameter")
        return None
    sys_path = "/sys/class/scsi_host/host%s" % host_id
    if not os.path.exists(sys_path):
        _print("FAIL: %s is not a valid path" % sys_path)
        return None

    link_path = readlink(sys_path)

    regex_pci_id = libsan.host.linux.get_regex_pci_id()
    m = re.search("(%s)/host%s/scsi_host" % (regex_pci_id, host_id), link_path)
    # _print("DEBUG: pci_id_of_host_id - %s" % link_path)
    if m:
        return m.group(1)

    # for example ixgbe need to check the PCI ID from the network device
    # check for network interface name
    net_regex = re.compile(r"devices/virtual/net/(.*)\.")
    m = net_regex.search(link_path)
    if m:
        return libsan.host.net.get_pci_id_of_nic(m.group(1))

    return None


def rescan_host(host=None, verbose=True):
    """
    Rescan for devices for specific host
    If no host is given it will scan all SCSI hosts
    The arguments are:
    \tHost:      eg. 1 for host1
    Returns:
    \tTrue if no problem executing command
    \tFalse if something went wrong
    """
    host_list = []
    if host:
        host_list = [host]
    else:
        scsi_hosts = get_hosts()
        for host in scsi_hosts:
            host_list.append(host)

    error = 0

    if not host_list:
        _print("WARN: No host found on server to rescan")
        return True

    for host in host_list:
        if verbose:
            _print("INFO: Rescanning host%s" % host)
        cmd = "echo \"- - -\" > %s/host%s/scan" % (host_path, host)
        retcode, _ = run(cmd, return_output=True, verbose=verbose)
        if retcode != 0:
            error += 1
            _print("FAIL: there was some problem scanning host%s" % host)

    if error:
        return False

    return True


def rescan_disk(scsi_disk=None):
    """
    Rescan an specific SCSI disk.
    If no disk is given, rescann all SCSI disks
    echo 1 > /sys/block/<scsi_disk>/device/rescan
    \tHost:      eg. 1 for host1
    Returns:
    \tTrue if no problem executing command
    \tFalse if something went wrong
    """
    scsi_disks = []

    if scsi_disk:
        scsi_disks = [scsi_disk]
    else:
        ids = get_scsi_disk_ids()
        for _id in ids:
            scsi_disks.append(get_scsi_disk_name(_id))

    error = 0
    for scsi_disk in scsi_disks:
        cmd = "echo 1 > /sys/block/%s/device/rescan" % scsi_disk
        retcode, _ = run(cmd, return_output=True)
        if retcode != 0:
            _print("FAIL: Could not rescan %s" % scsi_disk)
            error += 1

    if error:
        return False

    return True


def size_of_disk(scsi_disk):
    """
    Usage
        size_of_disk(disk)
    Purpose
        Given an scsi_disk name. Eg. sda
    Parameter
        scsi_disk
    Returns
        size in bytes

    """
    if not scsi_disk:
        return None

    cmd = "cat /sys/block/%s/queue/logical_block_size" % scsi_disk
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: size_of_disk() - Could not get size for disk %s" % scsi_disk)
        print(output)
        return None
    if not output:
        return None
    logical_block_size = output

    cmd = "cat /sys/block/%s/size" % scsi_disk
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: size_of_disk() - Could not get sectore size for disk %s" % scsi_disk)
        print(output)
        return None
    if not output:
        return None

    sector_size = output

    return int(logical_block_size) * int(sector_size)


def wwid_of_disk(scsi_disk=None):
    """
    Usage
        wwid_of_disk(disk)
    Purpose
        Given an scsi_disk name. Eg. sda, mpatha
    Parameter
        scsi_disk   device to get wwid for
    Returns
        wwid:       eg. 360fff19abdd9f5fb943525d45126ca27
    """
    if not scsi_disk:
        _print("FAIL: wwid_of_disk() - requires scsi_disk parameter")
        return None

    if libsan.host.linux.is_dm_device(scsi_disk):
        return libsan.host.linux.get_udev_property(scsi_disk, 'DM_SERIAL')

    return libsan.host.linux.get_udev_property(scsi_disk, 'ID_SERIAL')


def scsi_ids_of_wwid(wwid):
    """
    Usage
        scsi_ids_of_wwid(wwid)
    Purpose
        Find out all SCSI ID for WWID.
    Parameter
        wwid
    Returns
        scsi_ids
    """

    if not wwid:
        _print("FAIL: scsi_ids_of_wwid(): Got NULL input for WWID")
        return None

    scsi_ids = None
    all_scsi_info = query_all_scsi_disks()
    if not all_scsi_info:
        # Could not find any SCSI device
        return None

    for _id in list(all_scsi_info.keys()):
        if all_scsi_info[_id]["wwid"] == wwid:
            if not scsi_ids:
                scsi_ids = []
            scsi_ids.append(_id)
    if scsi_ids:
        scsi_ids = libsan.misc.array.dedup(scsi_ids)
    return scsi_ids


def wwn_of_disk(scsi_disk):
    """
    Usage
        wwn_of_disk(disk)
    Purpose
        Given an scsi_disk name. Eg. sda
    Parameter
        scsi_disk
    Returns
        wwid:       eg. 0x60a980003246694a412b45673342616e
    """
    if not scsi_disk:
        _print("FAIL: wwn_of_disk() - requires scsi_disk parameter")
        return None

    key_regex = "ID_WWN_WITH_EXTENSION=(.*)"

    # cmd = "udevadm info --name=%s --query=all" % scsi_disk
    # retcode, output = run(cmd, return_output=True, verbose=False)
    # if (retcode != 0):
    # #_print("FAIL: wwn_of_disk() - Could not query %s" % scsi_disk)
    # #print output

    # return None

    # udev_wwn = None
    # lines = output.split("\n")
    # for line in lines:
    # m = re.search(key_regex, line)
    # if m:
    # udev_wwn = m.group(1)

    cmd = "scsi_id --whitelisted --export /dev/%s" % scsi_disk
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        # _print("FAIL: wwn_of_disk() - Could not query %s" % scsi_disk)
        # print output
        return None

    lines = output.split("\n")
    for line in lines:
        m = re.search(key_regex, line)
        if m:
            scsi_wwn = m.group(1)
            return scsi_wwn

    # if udev_wwn and scsi_wwn:
    # if udev_wwn == scsi_wwn:
    # return udev_wwn
    # _print("udevadm WWN is %s" % udev_wwn)
    # _print("scsi_id WWN is %s" % scsi_wwn)
    # _print("FAIL: wwn_of_disk() - udevadm WWN and scsi_id WWN for %s do not match" % scsi_disk)
    # return None

    return None


def udev_wwn_of_disk(scsi_disk):
    """
    Usage
        udev_wwn_of_disk(disk)
    Purpose
        Given an scsi_disk name. Eg. sda
    Parameter
        scsi_disk
    Returns
        wwid:       eg. 0x60a980003246694a412b45673342616e
    """
    if not scsi_disk:
        _print("FAIL: udev_wwn_of_disk() - requires scsi_disk parameter")
        return None

    key_regex = "ID_WWN_WITH_EXTENSION=(.*)"

    cmd = "udevadm info --name=%s --query=all" % scsi_disk
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        # _print("FAIL: udev_wwn_of_disk() - Could not query %s" % scsi_disk)
        # print output
        return None

    lines = output.split("\n")
    for line in lines:
        m = re.search(key_regex, line)
        if m:
            udev_wwn = m.group(1)
            return udev_wwn
    return None


def query_scsi_driver_info(driver):
    """
    """
    if not driver:
        _print("FAIL: query_scsi_driver_info() - requires driver parameter")
        return None

    all_scsi_host_ids = get_hosts()
    if not all_scsi_host_ids:
        _print("FAIL: query_scsi_driver_info() - Host does not have any SCSI host")
        return None

    driver_host_ids = []
    # Check which SCSI hosts are using the driver we want
    for host_id in all_scsi_host_ids:
        if scsi_driver_of_host_id(host_id) == driver:
            driver_host_ids.append(host_id)

    if not driver_host_ids:
        _print("FAIL:  No SCSI disk found from driver %s" % driver)
        return None

    scsi_driver_info = dict()
    scsi_driver_info["scsi_host"] = {}
    for host_id in driver_host_ids:
        scsi_driver_info["scsi_host"][host_id] = query_scsi_host_info(host_id)

    scsi_driver_info["driver_name"] = driver
    # Add general driver info to this dict
    scsi_driver_info.update(libsan.host.linux.get_driver_info(driver))

    return scsi_driver_info


def get_free_disks(exclude_boot_device=True, exclude_lvm_device=True, exclude_mpath_device=True, filter_only=None):
    """
    Return a dict of free SCSI devices.
    By default it excludes devices used for boot, lvm or multipath
    Optional "filter_only" argument should be a dict. Eg. filter_only={'state': 'running'}
    """
    all_scsi_disks = query_all_scsi_disks()
    if not all_scsi_disks:
        # could not find any SCSI disk
        return None

    pvs = libsan.host.lvm.pv_query()
    boot_dev = libsan.host.linux.get_boot_device()
    boot_wwid = None
    # if for some reason we boot from a single disk, but this disk is part of multipath device
    # the mpath device should be skipped as well
    if boot_dev:
        boot_wwid = libsan.host.linux.get_device_wwid(boot_dev)

    all_mp_info = None
    if (libsan.host.mp.is_multipathd_running()) and exclude_mpath_device:
        all_mp_info = libsan.host.mp.multipath_query_all()
        if all_mp_info and "by_wwid" not in list(all_mp_info.keys()):
            # Fail querying mpath, setting it back to None
            all_mp_info = None

    chosen_disks = {}
    for scsi_disk in list(all_scsi_disks.keys()):
        scsi_info = all_scsi_disks[scsi_disk]
        # Skip if mpath device is used for boot
        if boot_wwid == scsi_info["wwid"] and exclude_boot_device:
            _print("DEBUG: get_free_disks() - skip %s as it is used for boot" % scsi_info["name"])
            continue

        # Skip if disk is used by multipath
        if all_mp_info and scsi_info["wwid"] in list(all_mp_info["by_wwid"].keys()) and exclude_mpath_device:
            _print("DEBUG: get_free_disks() - skip %s as it is used for mpath" % scsi_info["name"])
            continue
        # Skip if filter_only is specified
        filtered = False
        if filter_only is not None:
            for key in filter_only:
                if scsi_info[key] != filter_only[key]:
                    _print("DEBUG: get_free_disks() - filtered %s as %s is not %s" % (
                        scsi_info["name"], key, filter_only[key]))
                    filtered = True
                    continue
        if filtered:
            continue

        chosen_disks[scsi_info["name"]] = scsi_info

        # Skip if it is used by LVM
        if pvs and exclude_lvm_device:
            for pv in list(pvs.keys()):
                if '/' + get_scsi_disk_name(scsi_disk) in pv:
                    _print("DEBUG: get_free_disks() - skip %s as it is used for LVM" % scsi_info["name"])
                    chosen_disks.pop(scsi_info["name"])

    return chosen_disks


def scsi_device_2_scsi_name(scsi_device):
    """
    Convert an specific SCSI device to scsi_name
    Eg. /dev/sdap1 => sda
    """
    scsi_dev_regex = r"/dev\/(sd.*)"
    m = re.match(scsi_dev_regex, scsi_device)
    if m:
        # remove partition if it has
        device_name = m.group(1)
        m = re.match(r"(.*)\d+", device_name)
        if m:
            device_name = m.group(1)
        return device_name
    # does not seem to be a valid SCSI device
    return None


def disk_sys_trigger(scsi_disk, action):
    """
    Usage
        disk_sys_trigger(scsi_disk, action)
    Purpose
        Bring disk online/offline, via
            /sys/block/sdX/device/state
        action cound be 'UP|DOWN|other', for UP, we change it into 'running'.
        for DOWN, we change it into 'offline'.
    Parameter
        scsi_disk      # like 'sda'
        action         # 'UP|DOWN|other'
    Returns
        True               # got expected /sys/block/sdX/device/state
            or
        False
    """
    if not scsi_disk or not action:
        _print("FAIL: disk_sys_trigger() - requires scsi_disk and action parameters")
        return False

    sys_path = "/sys/block/%s/device/state" % scsi_disk
    if not os.path.isfile(sys_path):
        _print("FAIL: No such file: %s" % sys_path)
        return False

    if action == "UP":
        action = "running"
    if action == "DOWN":
        action = "offline"

    cmd = "echo %s > %s" % (action, sys_path)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: disk_sys_trigger() - Could not execute %s" % cmd)
        print(output)
        return None

    # cmd = "cat %s 2>/dev/null" % sys_path
    new_state = disk_sys_check(scsi_disk)
    if not new_state:
        _print("FAIL: disk_sys_trigger() - Could not get state of %s" % scsi_disk)
        return False

    if action != new_state:
        _print("FAIL: disk_sys_trigger() - Current state is '%s' expected '%s'" % (new_state, action))
        return False

    return True


def disk_sys_check(scsi_disk):
    """
    Usage
        disk_sys_check(scsi_disk)
    Purpose
        Check state of specific disk
            /sys/block/sdX/device/state
    Parameter
        scsi_disk      # like 'sda'
    Returns
        running/offline       # got expected /sys/block/sdX/device/state
            or
        None
    """
    if not scsi_disk:
        _print("FAIL: disk_sys_check() - requires scsi_disk parameter")
        return None

    sys_path = "/sys/block/%s/device/state" % scsi_disk
    if not os.path.isfile(sys_path):
        _print("FAIL: disk_sys_check() - No such file: %s" % sys_path)
        return None

    cmd = "cat %s 2>/dev/null" % sys_path
    _, state = run(cmd, return_output=True, verbose=False)
    if not state:
        _print("FAIL: disk_sys_check() - Could not read from %s" % sys_path)
        return None

    return state


def timeout_of_disk(scsi_disk):
    """
    Usage
        timeout_of_disk(scsi_disk)
    Purpose
        Check timeout of specific disk
            /sys/block/sdX/device/timeout
    Parameter
        scsi_disk      # like 'sda'
    Returns
        timeout in seconds       # got expected /sys/block/sdX/device/timeout
            or
        None
    """
    if not scsi_disk:
        _print("FAIL: timeout_of_disk() - requires scsi_disk parameter")
        return None

    sys_path = "/sys/block/%s/device/timeout" % scsi_disk
    if not os.path.isfile(sys_path):
        _print("FAIL: timeout_of_disk() - No such file: %s" % sys_path)
        return None

    cmd = "cat %s 2>/dev/null" % sys_path
    _, timeout = run(cmd, return_output=True, verbose=False)
    if not timeout:
        _print("FAIL: timeout_of_disk() - Could not read from %s" % sys_path)
        return None

    return timeout
