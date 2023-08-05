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

"""mp.py: Module to manage multipath devices."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import os.path
import re

import augeas

import libsan.host.fc
import libsan.host.iscsi
import libsan.host.linux
import libsan.host.lvm
import libsan.host.net
import libsan.host.scsi
import libsan.misc.size
from libsan.host.cmdline import run

multipath_conf_path = '/etc/multipath.conf'
aug_conf_path = "/files/etc/multipath.conf"


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)

    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def mp_service_name():
    """
    Return the name of mutlipath service
    """
    return "multipathd"


def mp_start_service():
    """
    Start multipath service
    """
    return libsan.host.linux.service_start(mp_service_name())


def mp_stop_service():
    """
    Stop multipath service
    """
    return libsan.host.linux.service_stop(mp_service_name())


def is_multipathd_running():
    """
    Check if multipathd is running
    """
    return libsan.host.linux.is_service_running(mp_service_name())


def is_mpath_device(mpath_name, print_fail=True):
    """
    Checks if given device is multipath.
    :param mpath_name: name of device to check
    :param print_fail: Should we print "FAIL: ..." in case of fail?
    :return: True / False
    """
    cmd = "multipath -l %s" % mpath_name
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        if print_fail:
            _print("FAIL: Could not execute \"%s\"" % cmd)
        return None

    # There could be error in the output, so we need to check if we really found the mpath device.
    # 'multipath -l device_name' always should return device_name at the beginning if found
    if output and len(output) > 0 and output.startswith("%s " % mpath_name):
        return True
    return False


def get_mpath_of_disk(disk):
    """Get the multipath device of a disk
    The arguments are:
    \tDisk:   Disk
    Returns:
    \tString: Return the name of multipath device
    """
    if libsan.host.linux.dist_name() == "RHEL" and libsan.host.linux.dist_ver() < 7:
        device = "/dev/%s" % disk
        mmnum_cmd = "ls -l %s | awk '{print \"(\"$5,$6\")\"}'" % device
        retcode, output = run(mmnum_cmd, return_output=True, verbose=False)
        if retcode != 0:
            _print("FAIL: Could not get device information for %s" % device)
            print(output)
            return None
        deps_cmd = r"dmsetup deps | grep \"%s\" | awk -v device=%s '{print $1}' | tr -d \"\:\"" % (output, device)
        retcode, output = run(deps_cmd, return_output=True, verbose=False)
        if retcode != 0:
            _print("FAIL: Could not get dmsetup information for %s" % device)
            print(output)
            return None
        mpath = output
    else:
        # BZ891921 - Multipath provides the mpath device of given scsi block device
        cmd = "pidof multipathd"
        retcode, output = run(cmd, return_output=True, verbose=False)
        if retcode != 0:
            _print("FAIL: For some reason multipathd is not running")
            print(output)
            return None
        fmt = "\"%d %m\""
        cmd = "multipathd show paths format %s | egrep \"^%s\" | awk '{print$2}'" % (fmt, disk)
        retcode, output = run(cmd, return_output=True, verbose=False)
        if retcode != 0:
            _print("FAIL: to find multipath of disk %s" % disk)
            print(output)
            return None
        mpath = output

    if not mpath:
        _print("WARN: Could not find multipath for %s" % disk)
        return None
    return mpath


def get_disks_of_mpath(mpath_name):
    """
    Return all SCSI devices that belong to this mpath
    """
    if not mpath_name:
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        return None

    if "disk" not in list(mpath_dict.keys()):
        _print("WARN: mpath %s has no disk" % mpath_name)
        return None

    return list(mpath_dict["disk"].keys())


def get_disks_of_mpath_by_wwpn(mpath_name, wwpn):
    """
    From an specific mpath device, return the devices
    connected to this WWPN
    """
    if not mpath_name or not wwpn:
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        return None

    scsi_devices = []
    wwpn = libsan.host.fc.standardize_wwpn(wwpn)
    if wwpn:
        if "disk" in list(mpath_dict.keys()):
            port_entries = ["h_wwpn", "t_wwpn"]
            for disk in list(mpath_dict["disk"].keys()):
                for port_entry in port_entries:
                    if port_entry in list(mpath_dict["disk"][disk].keys()):
                        if (mpath_dict["disk"][disk][port_entry] and
                                wwpn in mpath_dict["disk"][disk][port_entry]):
                            scsi_devices.append(disk)
    return scsi_devices


def get_disks_of_mpath_by_iqn(mpath_name, iqn):
    """
    From an specific mpath device, return the devices
    connected to this IQN
    """
    if not mpath_name or not iqn:
        return None

    if not libsan.host.iscsi.is_iqn(iqn):
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        return None

    scsi_devices = []
    if "disk" in list(mpath_dict.keys()):
        port_entries = ["h_iqn", "t_iqn"]
        for disk in list(mpath_dict["disk"].keys()):
            for port_entry in port_entries:
                if port_entry in list(mpath_dict["disk"][disk].keys()):
                    if (mpath_dict["disk"][disk][port_entry] and
                            iqn in mpath_dict["disk"][disk][port_entry]):
                        scsi_devices.append(disk)
    return scsi_devices


def get_disks_of_mpath_by_mac(mpath_name, mac):
    """
    From an specific mpath device, return the devices
    connected to this MAC
    """
    if not mpath_name or not mac:
        return None

    if not libsan.host.net.is_mac(mac):
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        return None

    scsi_devices = []
    if "disk" in list(mpath_dict.keys()):
        port_entries = ["iface_mac"]
        for disk in list(mpath_dict["disk"].keys()):
            for port_entry in port_entries:
                if port_entry in list(mpath_dict["disk"][disk].keys()):
                    if (mpath_dict["disk"][disk][port_entry] and
                            mac in mpath_dict["disk"][disk][port_entry]):
                        scsi_devices.append(disk)
    return scsi_devices


def multipath_query_all(mpath_name=None):
    # Not sure with of these 2 commands I should use
    # multipath -ll
    # will force multipath to issue it's own (synchronous) path checker call,
    # and report that result.
    # multipathd show top
    # multipath will not run a checker on the paths. It will simply report the
    # current state. This means that you get the results from the last time
    # that multipathd ran the path checker.  If there is no IO going to the
    # device, the kernel won't return an error on the path, and so you will
    # not see any errors until the next checker is run after you bring the
    # port down.
    cmd = "multipath -ll"
    if mpath_name:
        cmd += " %s" % mpath_name
    # cmd = "multipathd -k\"show top\""
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not execute \"%s\"" % cmd)
        return None

    if not output:
        # _print("FAIL: Got no output from \"%s\"" % cmd)
        return None

    regex_mpath = r"^(?:create\:\ ){0,1}"  # might have when ceating mpath
    regex_mpath += r"(?:reload\:\ ){0,1}"  # might have when ceating mpath
    regex_mpath += r"([^ ]+?)\ +"  # 1. mpath_name
    regex_mpath += r"(?:\((\S+)\)\ +){0,1}"  # 2. wwid if different from #1
    regex_mpath += r"(?:(dm\-[0-9]+)\ +){0,1}"  # 3. dm_name if known
    regex_mpath += r"(?:([^,]+),){0,1}"  # 4. vendor, might not have
    regex_mpath += r"(?:([^,]+)){0,1}$"  # 5. product,  might not have

    regex_feature = r"size=([0-9\.]+[A-Z])\ +"  # 1. size
    regex_feature += r"features=\'([^\']+)\'\ +"  # 2. features
    regex_feature += r"hwhandler=\'([^\']+)\'\ +"  # 3. hardware handler
    regex_feature += r"(?:wp=([rw]+)){0,1}"  # 4. write permission if known

    regex_pg = r"[^a-z]+policy=\'([^\`]+)\'\ +"  # 1. policy of this PG path_selector
    regex_pg += r"(?:prio=([0-9\-]+)\ +){0,1}"  # 2. priority of this PG if known
    regex_pg += r"(?:status=([a-z]+)){0,1}"  # 3. status of this PG if known (active or enable, etc)

    regex_disk = r"[^0-9]+"
    regex_disk += r"([0-9]+:[0-9]+:[0-9]+:[0-9]+)\ +"  # 1. scsi_id
    regex_disk += r"([a-z]+)\ +"  # 2. dev_name
    regex_disk += r"([0-9]+:[0-9]+)\ +"  # 3. major:minor
    regex_disk += r"(?:([a-z]+)\ +){0,1}"  # 4. dm_status if known, kernel level
    #   failed or active
    regex_disk += r"(?:([a-z]+)\ +){0,1}"  # 5. path_status if known, maintained
    #   by multipathd path_checker
    #   ready  or ghost or
    #   faulty or shaky
    regex_disk += r"(?:([a-z]+)){0,1}"  # 6. online_status: running or offline

    _mpath_name = None
    pg_id = None
    size = None
    size_human = None
    size_bytes = None
    wwid = None

    all_mpath_dict = dict()
    all_mpath_dict['by_wwid'] = {}
    all_mpath_dict['by_mpath_name'] = {}
    all_mpath_dict['by_scsi_id'] = {}
    mpath_dict = {}

    scsi_host_id_2_driver = {}
    scsi_host_id_2_h_wwpn = {}
    fc_target_id_2_t_wwpn = {}

    all_scsi_host_ids = libsan.host.scsi.get_hosts()

    for host_id in all_scsi_host_ids:
        scsi_driver = libsan.host.scsi.scsi_driver_of_host_id(host_id)
        if scsi_driver:
            scsi_host_id_2_driver[host_id] = scsi_driver
        scsi_host_id_2_h_wwpn[host_id] = libsan.host.fc.get_fc_host_wwpn(host_id)
        t_wwpns_of_host = libsan.host.fc.t_wwpn_of_host(host_id)
        if t_wwpns_of_host:
            for t_wwpn in t_wwpns_of_host:
                t_ids = libsan.host.fc.fc_target_id_of_wwpn(t_wwpn)
                if t_ids:
                    for t_id in t_ids:
                        fc_target_id_2_t_wwpn[t_id] = t_wwpn

    lines = output.split("\n")

    for line in lines:
        m = re.match(regex_feature, line)
        if m:
            if not wwid or not mpath_dict:
                continue
            size = m.group(1)
            size_human = size + "iB"
            size_bytes = libsan.misc.size.size_human_2_size_bytes(size_human)
            mpath_dict["size_mp"] = size
            mpath_dict["size_human"] = size_human
            mpath_dict["size_bytes"] = size_bytes
            mpath_dict["feature"] = m.group(2)
            mpath_dict["hw_handleer"] = m.group(3)
            mpath_dict["permission"] = m.group(4)
            mpath_dict["disk"] = {}
            mpath_dict["t_wwpns"] = []
            mpath_dict["h_wwpns"] = []
            mpath_dict["t_iqns"] = []
            mpath_dict["h_iqns"] = []
            mpath_dict["map_info"] = []
            mpath_dict["iface_macs"] = []
            mpath_dict["iface_names"] = []
            mpath_dict["target_ips"] = []
            mpath_dict["persist_ips"] = []
            mpath_dict["transport_types"] = []
            mpath_dict["scsi_drivers"] = []
            mpath_dict["host_ids"] = []
            # _print("\n\nDEBUG - Feature - query all mpath [%s]" % line)
            # print all_mpath_dict["by_mpath_name"]

            continue

        m = re.match(regex_pg, line)
        if m:
            if not wwid or not mpath_dict:
                continue
            pg_id += 1
            mpath_dict["path_group"][pg_id] = {}
            mpath_dict["path_group"][pg_id]["wwid"] = wwid
            mpath_dict["path_group"][pg_id]["mpath_name"] = _mpath_name
            mpath_dict["path_group"][pg_id]["wwid"] = wwid
            mpath_dict["path_group"][pg_id]["pg_id"] = pg_id
            mpath_dict["path_group"][pg_id]["policy"] = m.group(1)
            mpath_dict["path_group"][pg_id]["prio"] = m.group(2)
            mpath_dict["path_group"][pg_id]["status"] = m.group(3)
            mpath_dict["path_group"][pg_id]["disk"] = {}
            # _print("\n\nDEBUG - PG : query all mpath [%s]" % line)
            # print all_mpath_dict["by_mpath_name"]

            continue

        m = re.match(regex_disk, line)
        if m:
            if not wwid or not mpath_dict or not pg_id:
                continue
            scsi_id = m.group(1)
            scsi_disk = m.group(2)
            major_minor = m.group(3)
            dm_status = m.group(4)
            path_status = m.group(5)
            online_status = m.group(6)
            # host ID is the first numbers of scsi_id
            host_id = None
            m = re.match(r"(\d+):.*", scsi_id)
            if m:
                host_id = m.group(1)

            t_wwpn = None
            h_wwpn = None
            h_iqn = None
            t_iqn = None
            iface_name = None
            iface_mac = None
            target_ip = None
            persist_ip = None
            scsi_driver = "N/A"

            match_scsi_id = re.search(libsan.host.scsi.get_regex_scsi_id(), line)
            if match_scsi_id:
                scsi_host_id = match_scsi_id.group(1)
                fc_target_id = "%s:%s:%s" % (match_scsi_id.group(1), match_scsi_id.group(2), match_scsi_id.group(3))
                if scsi_host_id in list(scsi_host_id_2_driver.keys()):
                    scsi_driver = scsi_host_id_2_driver[scsi_host_id]

                if scsi_host_id in list(scsi_host_id_2_h_wwpn.keys()):
                    h_wwpn = scsi_host_id_2_h_wwpn[scsi_host_id]

                if h_wwpn:
                    if fc_target_id in list(fc_target_id_2_t_wwpn.keys()):
                        t_wwpn = fc_target_id_2_t_wwpn[fc_target_id]
                else:
                    iscsi_session = libsan.host.iscsi.get_iscsi_session_by_scsi_id(scsi_id)
                    if iscsi_session:
                        h_iqn = iscsi_session["h_iqn"]
                        t_iqn = iscsi_session["t_iqn"]
                        iface_name = iscsi_session["iface"]
                        iface_mac = iscsi_session["mac"]
                        target_ip = iscsi_session["target_ip"]
                        persist_ip = iscsi_session["persist_ip"]

            disk_info_dict = dict()
            disk_info_dict["scsi_id"] = scsi_id
            disk_info_dict["host_id"] = host_id
            disk_info_dict["scsi_disk"] = scsi_disk
            disk_info_dict["scsi_driver"] = scsi_driver
            disk_info_dict["pg_id"] = pg_id
            disk_info_dict["mpath_name"] = _mpath_name
            disk_info_dict["wwid"] = wwid
            disk_info_dict["dm_status"] = dm_status
            disk_info_dict["path_status"] = path_status
            disk_info_dict["online_status"] = online_status
            disk_info_dict["major_minor"] = major_minor
            disk_info_dict["size"] = size
            disk_info_dict["size_human"] = size_human
            disk_info_dict["size_bytes"] = size_bytes
            disk_info_dict["t_wwpn"] = t_wwpn
            disk_info_dict["h_wwpn"] = h_wwpn
            disk_info_dict["t_iqn"] = t_iqn
            disk_info_dict["h_iqn"] = h_iqn
            disk_info_dict["iface_name"] = iface_name
            disk_info_dict["iface_mac"] = iface_mac
            disk_info_dict["target_ip"] = target_ip
            disk_info_dict["persist_ip"] = persist_ip
            disk_info_dict["transport_type"] = "UNKNOWN"

            if h_iqn:
                disk_info_dict["transport_type"] = "iSCSI"

            if h_wwpn:
                disk_info_dict["transport_type"] = libsan.host.fc.fc_host_transport_type(
                    libsan.host.fc.fc_host_id_of_wwpn(h_wwpn))

            if scsi_driver == "scsi_debug":
                disk_info_dict["transport_type"] = "scsi_debug"

            # Each disk has its own information, we should add each disk from mpath info to mpath info
            if disk_info_dict["transport_type"] not in mpath_dict["transport_types"]:
                mpath_dict["transport_types"].append(disk_info_dict["transport_type"])

            if scsi_driver:
                if scsi_driver not in mpath_dict["scsi_drivers"]:
                    mpath_dict["scsi_drivers"].append(scsi_driver)

            if host_id:
                if host_id not in mpath_dict["host_ids"]:
                    mpath_dict["host_ids"].append(host_id)

            if t_wwpn:
                if t_wwpn not in mpath_dict["t_wwpns"]:
                    mpath_dict["t_wwpns"].append(t_wwpn)

            if h_wwpn:
                if h_wwpn not in mpath_dict["h_wwpns"]:
                    mpath_dict["h_wwpns"].append(h_wwpn)

            if h_wwpn and t_wwpn:
                map_info = {"t_wwpn": t_wwpn, "h_wwpn": h_wwpn}
                mpath_dict["map_info"].append(map_info)

            if t_iqn:
                if t_iqn not in mpath_dict["t_iqns"]:
                    mpath_dict["t_iqns"].append(t_iqn)

            if h_iqn:
                if h_iqn not in mpath_dict["h_iqns"]:
                    mpath_dict["h_iqns"].append(h_iqn)

            if h_iqn and t_iqn:
                map_info = {"t_iqn": t_iqn, "h_iqn": h_iqn}
                mpath_dict["map_info"].append(map_info)

            if iface_mac:
                if iface_mac not in mpath_dict["iface_macs"]:
                    mpath_dict["iface_macs"].append(iface_mac)

            if iface_name:
                if h_iqn not in mpath_dict["iface_names"]:
                    mpath_dict["iface_names"].append(iface_name)

            if target_ip:
                if target_ip not in mpath_dict["target_ips"]:
                    mpath_dict["target_ips"].append(target_ip)

            if persist_ip:
                if persist_ip not in mpath_dict["persist_ips"]:
                    mpath_dict["persist_ips"].append(persist_ip)

            mpath_dict["disk"][disk_info_dict["scsi_disk"]] = disk_info_dict
            mpath_dict["path_group"][pg_id]["disk"][scsi_id] = disk_info_dict
            all_mpath_dict["by_scsi_id"][scsi_id] = disk_info_dict
            # _print("\n\nDEBUG - Disk: query all mpath [%s]" % line)
            # print all_mpath_dict["by_mpath_name"]

            continue

        # as regex_mpath is a agressive regex, we leave it at the last
        # one to check.
        m = re.match(regex_mpath, line)
        if m:
            if re.match(r"^\|", line):
                continue

            _mpath_name = m.group(1)
            pg_id = 0
            wwid = _mpath_name
            if m.group(2):
                wwid = m.group(2)

            dm_name = None
            if m.group(3):
                dm_name = m.group(3)

            vendor_raw = None
            vendor = vendor_raw
            if m.group(4):
                vendor_raw = m.group(4)
                vendor = re.sub("[ ]+$", "", vendor_raw)

            product_raw = None
            product = product_raw
            if m.group(5):
                product_raw = m.group(5)
                product = re.sub("[ ]+$", "", product_raw)

            mpath_dict = dict()
            mpath_dict["mpath_name"] = _mpath_name
            mpath_dict["wwid"] = wwid
            mpath_dict["dm_name"] = dm_name
            mpath_dict["vendor"] = vendor
            mpath_dict["vendor_raw"] = vendor_raw
            mpath_dict["product"] = product
            mpath_dict["product_raw"] = product_raw
            mpath_dict["h_wwpns"] = []
            mpath_dict["t_wwpns"] = []
            mpath_dict["disk"] = {}
            mpath_dict["path_group"] = {}
            mpath_dict["transport_types"] = []

            all_mpath_dict["by_wwid"][wwid] = mpath_dict
            all_mpath_dict["by_mpath_name"][_mpath_name] = mpath_dict
            # _print("\n\nDEBUG: query all mpath [%s]" % line)
            # print all_mpath_dict["by_mpath_name"]
            continue
    if mpath_name:
        if mpath_name in list(all_mpath_dict["by_mpath_name"].keys()):
            return all_mpath_dict["by_mpath_name"][mpath_name]
        return None

    return all_mpath_dict


def mpath_name_of_wwid(wwid):
    """
    """
    if not wwid:
        _print("FAIL: mpath_name_of_wwid() - requires wwid parameter")
        return None

    mp_devs = multipath_query_all()
    if not mp_devs:
        return None

    if wwid in list(mp_devs["by_wwid"].keys()):
        return mp_devs["by_wwid"][wwid]["mpath_name"]

    return None


def mpath_names_of_vendor(vendor):
    """
    Given a Vendor return a list with all multipath device names with this vendor
    """
    if not vendor:
        _print("FAIL: mpath_names_of_vendor() - requires vendor parameter")
        return None

    mp_devs = multipath_query_all()
    if not mp_devs:
        return None

    mpaths = []
    for mpath_info in list(mp_devs["by_mpath_name"].values()):
        if "vendor" in list(mpath_info.keys()) and mpath_info["vendor"] == vendor:
            mpaths.append(mpath_info["mpath_name"])

    return mpaths


def mpath_check_disk_status(mpath_name, scsi_disk):
    """
    Check the online status of an specific SCSI disk from a mpath device
    """
    if not mpath_name or not scsi_disk:
        _print("FAIL: mpath_check_disk_status() - requires mpath_name and scsi_disk parameters")
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        _print("FAIL: mpath_check_disk_status() - Could not get mpath info for %s" % mpath_name)
        return None

    if "disk" not in list(mpath_dict.keys()):
        _print("FAIL: mpath_check_disk_status() - Could not find any SCSI disk for %s" % mpath_name)
        return None

    for disk in list(mpath_dict["disk"].keys()):
        if scsi_disk == mpath_dict["disk"][disk]["scsi_disk"]:
            return mpath_dict["disk"][disk]["online_status"]

    return None


def mpath_check_disk_dm_status(mpath_name, scsi_disk):
    """
    Check the dm status of an specific SCSI disk from a mpath device
    """
    if not mpath_name or not scsi_disk:
        _print("FAIL: mpath_check_disk_dm_status() - requires mpath_name and scsi_disk parameters")
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        _print("FAIL: mpath_check_disk_dm_status() - Could not get mpath info for %s" % mpath_name)
        return None

    if "disk" not in list(mpath_dict.keys()):
        _print("FAIL: mpath_check_disk_dm_status() - Could not find any SCSI disk for %s" % mpath_name)
        return None

    for disk in list(mpath_dict["disk"].keys()):
        if scsi_disk == mpath_dict["disk"][disk]["scsi_disk"]:
            return mpath_dict["disk"][disk]["dm_status"]

    return None


def mpath_check_disk_path_status(mpath_name, scsi_disk):
    """
    Check the path status of an specific SCSI disk from a mpath device
    """
    if not mpath_name or not scsi_disk:
        _print("FAIL: mpath_check_disk_path_status() - requires mpath_name and scsi_disk parameters")
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        _print("FAIL: mpath_check_disk_path_status() - Could not get mpath info for %s" % mpath_name)
        return None

    if "disk" not in list(mpath_dict.keys()):
        _print("FAIL: mpath_check_disk_path_status() - Could not find any SCSI disk for %s" % mpath_name)
        return None

    for disk in list(mpath_dict["disk"].keys()):
        if scsi_disk == mpath_dict["disk"][disk]["scsi_disk"]:
            return mpath_dict["disk"][disk]["path_status"]

    return None


def mpath_get_active_disk(mpath_name):
    """
    From specific mpath device get which disk is the active one
    Return
    \tList of active SCSI disks
    """
    if not mpath_name:
        _print("FAIL: mpath_get_active_disk() - requires mpath_name parameter")
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        _print("FAIL: mpath_get_active_disk() - Could not get mpath info for %s" % mpath_name)
        return None

    if "disk" not in list(mpath_dict.keys()):
        _print("FAIL: mpath_get_active_disk() - Could not find any SCSI disk for %s" % mpath_name)
        return None

    active_disks = []
    for disk in list(mpath_dict["disk"].keys()):
        pg = mpath_dict["disk"][disk]["pg_id"]
        if mpath_dict["path_group"][pg]["status"] == "active":
            active_disks.append(disk)

    if active_disks:
        return active_disks

    _print("FAIL: mpath_get_active_disk() - Could not find any active disk for %s" % mpath_name)
    return None


def get_free_mpaths(exclude_boot_device=True, exclude_lvm_device=True):
    """
    Return a dict of free mpath devices
    """
    all_mp_info = multipath_query_all()
    if not all_mp_info:
        # could not query multipath devices
        return None

    if "by_wwid" not in list(all_mp_info.keys()):
        # mpath device was not found
        print(list(all_mp_info.keys()))
        return None

    pvs = libsan.host.lvm.pv_query()
    boot_dev = libsan.host.linux.get_boot_device()
    boot_wwid = None
    # if for some reason we bot from a single disk, but this disk is part of multipath device
    # the mpath device should be skipped as well
    if boot_dev:
        boot_wwid = libsan.host.linux.get_device_wwid(boot_dev)

    choosed_mpaths = {}

    for mp_wwid in list(all_mp_info["by_wwid"].keys()):
        mp_info = all_mp_info["by_wwid"][mp_wwid]
        # Skip if mpath device is used for boot
        if boot_wwid == mp_info["wwid"] and exclude_boot_device:
            _print("DEBUG: get_free_mpaths() - skip %s as it is used for boot" % mp_info["mpath_name"])
            continue

        # Skip if it is used by LVM
        if pvs and exclude_lvm_device:
            for pv in list(pvs.keys()):
                if mpath_device_2_mpath_name(pv) == mp_info["mpath_name"]:
                    _print("DEBUG: get_free_mpaths() - skip %s as it is used for LVM" % mp_info["mpath_name"])
                    continue

        choosed_mpaths[mp_info["mpath_name"]] = mp_info

    return choosed_mpaths


def h_wwpns_of_mpath(mpath_name):
    """
    Return the h_wwpns of specific mpath device
    """
    if not mpath_name:
        _print("FAIL: h_wwpns_of_mpath() - requires mpath_name parameter")
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        _print("FAIL: h_wwpns_of_mpath() - Could not get mpath info for %s" % mpath_name)
        return None

    if "h_wwpns" in mpath_dict:
        return mpath_dict["h_wwpns"]
    return None


def t_wwpns_of_mpath(mpath_name):
    """
    Return the h_wwpns of specific mpath device
    """
    if not mpath_name:
        _print("FAIL: t_wwpns_of_mpath() - requires mpath_name parameter")
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        _print("FAIL: t_wwpns_of_mpath() - Could not get mpath info for %s" % mpath_name)
        return None

    if "t_wwpns" in mpath_dict:
        return mpath_dict["t_wwpns"]
    return None


def iface_macs_of_mpath(mpath_name):
    """
    Return the iface_macs_of_mpath of specific mpath device
    """
    if not mpath_name:
        _print("FAIL: iface_macs_of_mpath() - requires mpath_name parameter")
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        _print("FAIL: iface_macs_of_mpath() - Could not get mpath info for %s" % mpath_name)
        return None

    if "iface_macs" in mpath_dict:
        return mpath_dict["iface_macs"]
    return None


def transport_types_of_mpath(mpath_name):
    """
    Return the transport_types of specific mpath device
    """
    if not mpath_name:
        _print("FAIL: transport_types_of_mpath() - requires mpath_name parameter")
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        _print("FAIL: transport_types_of_mpath() - Could not get mpath info for %s" % mpath_name)
        return None

    if "transport_types" in mpath_dict:
        return mpath_dict["transport_types"]
    return None


def multipath_show(mpath_name=None):
    cmd = "multipath -ll"
    if mpath_name:
        cmd += " %s" % mpath_name
    run(cmd)


def multipath_reload(mpath_name=None):
    """
    Usage
    multipath_reload()
    Purpose
        Execute 'multipath -r'
    Parameter
        N/A
    Returns
        1
            or
        undef
    Exceptions
        N/A
    """
    cmd = "multipath -r"
    if mpath_name:
        cmd += " %s" % mpath_name
    ret = run(cmd, verbose=True)
    if ret != 0:
        return False

    return True


def remove_mpath(mpath_name):
    """
    Remove specific mpath
    """
    if not mpath_name:
        _print("FAIL: remove_mpath() - requires mpath_name parameter")
        return False
    retcode = run("multipath -f %s" % mpath_name)
    if retcode != 0:
        _print("FAIL: Could not remove mpath %s" % mpath_name)
        return False
    return True


def flush_all():
    """
    Flush all unused multipath device maps
    """
    cmd = "multipath -F"
    ret = run(cmd, verbose=True)
    if ret != 0:
        return False

    return True


def multipath_backup_conf(bak_file):
    """
    backup_mp_conf ()
    Usage
    backup_mp_conf(bak_file)
    Purpose
    Check if bak_file exists, if not, copy current to it.
    Parameter
    bak_file       # like "/etc/multipath.conf.bak"
    Returns
    true
        or
    False           # file exists or source file not exists;
    Exceptions
    N/A
    """
    mpath_conf = '/etc/multipath.conf'

    if not os.path.isfile(mpath_conf):
        _print("FAIL: %s does not exist" % mpath_conf)
        return False

    if os.path.isfile(bak_file):
        _print("FAIL: mpath backup file %s already exists" % bak_file)
        return False

    _print("INFO: Backing up %s to %s" % (mpath_conf, bak_file))
    cmd = "cp -f %s %s" % (mpath_conf, bak_file)
    ret, output = run(cmd, return_output=True)
    if ret != 0:
        _print("FAIL: Could not backup %s" % mpath_conf)
        print(output)
        return False

    return True


def multipath_restore_conf(bak_file):
    """
    multipath_restore_conf ()
    Usage
    multipath_restore_conf(bak_file)
    Purpose
    Check if bak_file exists, if so, copy it to '/etc/multipath.conf'
    and reload mpath conf.
    Parameter
    bak_file       # like "/etc/multipath.conf.bak"
    Returns
    True
        or
    False           # file exists or source file not exists;
    Exceptions
    N/A
    """
    if not os.path.isfile(bak_file):
        _print("FAIL: %s does not exist" % bak_file)
        return False

    _print("INFO: Restoring multipath configuration from %s" % bak_file)
    cmd = "cp -f %s %s" % (bak_file, multipath_conf_path)
    ret, output = run(cmd, return_output=True)
    if ret != 0:
        _print("FAIL: Could not restore backup from %s" % bak_file)
        print(output)
        return False

    multipath_reload_conf()
    return True


def multipath_reload_conf():
    """
    Usage
    multipath_reload_conf()
    Purpose
        Execute "multiapthd -k'reconfig'" to load configuration.
        After that execute 'multipath -r'
    Parameter
        N/A
    Returns
        1
            or
        undef
    Exceptions
        N/A
    """
    cmd = "multipathd -k'reconfig'"
    ret = run(cmd, verbose=True)

    multipath_reload()
    if ret != 0:
        return False

    return True


def multipath_setup_blacklist():
    """
    multipath_setup_blacklist ()
    Usage
    multipath_setup_blacklist()
    Purpose
    Add 'wwid .*' into blacklist and all exists mpath wwid to
    'blacklist_exceptions'. This will prevent mpath take over newly
    created LUN. This function DO NOT backup configuration, use
    backup_mp_conf() in stead.
    Parameter
    N/A
    Returns
    1
        or
    undef
    Exceptions
    N/A
    """
    all_mp_info_dict = multipath_query_all()
    if not all_mp_info_dict:
        return False
    current_wwids = list(all_mp_info_dict["by_wwid"].keys())
    if not current_wwids:
        return False

    if not mpath_conf_add('/blacklist/wwid', ".*"):
        return False

    for wwid in current_wwids:
        if not mpath_conf_add('/blacklist_exceptions/wwid', wwid):
            return False

    _print("INFO: Reloading updated multipath configuration")
    multipath_reload_conf()
    return True


def mpath_conf_add(path, value):
    """
    Checks if the specified path/value is present in config, and adds it if not.
    Use this if the path is not unique - eg. multiple wwid's can be listed.
    For valid options use 'man multipath.conf'

    :param path: eg. "/blacklist/wwid"
    :param value: eg. "<device wwid>"
    :returns: boolean
    :raises IOError: Augeas save fails. Check if multipath.conf changes are valid
    """

    aug = augeas.Augeas()
    full_path = aug_conf_path + path

    matched = aug.match(full_path + "[. = '%s']" % value)

    if not matched:
        try:
            aug.set(full_path + '[last() + 1]', value)
            aug.save()
            aug.close()
        except IOError:
            _print('FAIL: Unable to add %s to %s, Check if multipath.conf changes are valid' % (value, path))
            return False
        except Exception as e:
            print("Exception: %s" % e)
            return False

    return True


def mpath_conf_remove(path, value):
    """
    Remove parameter from multipath config.
    For valid options use 'man multipath.conf'

    :param path: eg. "/blacklist/wwid"
    :param value: eg. "<device wwid>"
    :returns: boolean
    :raises IOError: Augeas save fails. Check if multipath.conf changes are valid.
    """

    aug = augeas.Augeas()
    full_path = aug_conf_path + path

    try:
        aug.remove(full_path + "[. = '%s']" % value)
        aug.save()
        aug.close()
    except IOError:
        _print('FAIL: Unable to remove %s / %s, Check if multipath.conf changes are valid' % (path, value))
        return False
    except Exception as e:
        print("Exception: %s" % e)
        return False

    return True


def mpath_conf_set(path, value):
    """
    Change multipath.conf parameters.
    For valid options use 'man multipath.conf'

    :param path: eg. "/defaults/path_selector"
    :param value: eg. "round-robin"
    :returns: boolean
    :raises IOError: Augeas save fails. Check if multipath.conf changes are valid.
    """

    aug = augeas.Augeas()
    full_path = aug_conf_path + path

    try:
        aug.set(full_path, value)
        aug.save()
        aug.close()
    except IOError:
        _print('FAIL: multipath.conf - unable to set %s / %s' % (path, value))
        return False
    except Exception as e:
        print("Exception: %s" % e)
        return False

    return True


def mp_query_conf(config_str):
    """
    Parse string containing multipath config to a dict
    """
    regex_option = r"^[ \t]*"
    regex_option += r"([^\ #=\t]+)"
    regex_option += r"[\ \t]+"
    regex_option += r"(?:'|\"){0,1}"
    regex_option += r"([^'\"]+)"
    regex_option += r"(?:'|\"){0,1}"
    regex_option += r"(?:\#.*){0,1}"  # we remove '|"

    regex_section = r"[ \t]*([a-z_]+)[ \t]*\{"
    if not config_str:
        return None

    config_dict = {}

    current_section = None
    section_name = None
    for line in config_str.split("\n"):
        m = re.match(regex_section, line)
        if m:
            key = m.group(1)
            if key == "device":
                if not section_name:
                    continue
                if "devs" not in list(config_dict[section_name].keys()):
                    config_dict[section_name]["devs"] = []
                # We are in a sub section, need to update current_section
                tmp_dict = {}
                config_dict[section_name]["devs"].append(tmp_dict)
                # poiting current_section to last item in the list
                current_section = config_dict[section_name]["devs"][-1]
                continue

            if key == "multipath":
                if not section_name:
                    continue
                if "mpaths" not in list(config_dict[section_name].keys()):
                    config_dict[section_name]["mpaths"] = []
                # We are in a sub section, need to update current_section
                tmp_dict = {}
                config_dict[section_name]["mpaths"].append(tmp_dict)
                # poiting current_section to last item in the list
                current_section = config_dict[section_name]["mpaths"][-1]
                continue

            if key not in config_dict:
                config_dict[key] = {}
            current_section = config_dict[key]
            section_name = key
            continue
        m = re.match(regex_option, line)
        if m:
            key = m.group(1)
            value = m.group(2)
            if current_section is None:
                continue
            if key == "devnode":
                if "devnodes" not in list(current_section.keys()):
                    current_section["devnodes"] = []
                current_section["devnodes"].append(value)
                continue

            match_section = re.match("^blacklist", section_name)
            if key == "wwid" and match_section:
                if "wwids" not in list(current_section.keys()):
                    current_section["wwids"] = []
                current_section["wwids"].append(value)
                continue

            current_section[key] = value
            continue

    return config_dict


def mp_query_saved_conf():
    """
    Usage
        mp_query_saved_conf()
    Purpose
        Load multipath config file and return it as a dict
    Parameter
        N/A
    Returns
        mp_conf_dict
    """
    if not os.path.isfile(multipath_conf_path):
        _print("FAIL: %s does not exist" % multipath_conf_path)
        return None

    cfg_text = _load_config(multipath_conf_path)
    if not cfg_text:
        return None

    return mp_query_conf(cfg_text)


def _load_config(config_file):
    """
    Parse multipath config file to dict
    """
    mpath_cfg_file = open(config_file, encoding='UTF-8')
    mpath_cfg = mpath_cfg_file.read()

    return mpath_cfg


def _save_config(config_dict, config_file=multipath_conf_path):
    """
    Convert multipath config dict to string and save to file
    """
    config_str = ""
    if "defaults" in list(config_dict.keys()):
        config_str += "defaults {\n"
        for key in list(config_dict["defaults"].keys()):
            config_str += "\t%s %s\n" % (key, config_dict["defaults"][key])
        config_str += "}\n"

    blacklist_sections = ["blacklist", "blacklist_exceptions"]
    for b_section in blacklist_sections:
        if b_section in list(config_dict.keys()):
            config_str += "%s {\n" % b_section

            if "devnodes" in list(config_dict[b_section].keys()):
                for node in config_dict[b_section]["devnodes"]:
                    config_str += "\tdevnode \"%s\"\n" % node

            if "wwids" in list(config_dict[b_section].keys()):
                for wwid in config_dict[b_section]["wwids"]:
                    config_str += "\twwid \"%s\"\n" % wwid

            if "devs" in list(config_dict[b_section].keys()):
                for device in config_dict[b_section]["devs"]:
                    config_str += "\tdevice {\n"
                    for key in list(device.keys()):
                        config_str += "\t\t%s %s\n" % (key, device[key])
                    config_str += "\t}\n"

            config_str += "}\n"

    if "devices" in list(config_dict.keys()):
        config_str += "devices {\n"
        for vendor in list(config_dict["devices"].keys()):
            for product in config_dict["devices"][vendor]:
                config_str += "\tdevice {\n"
                for name in list(product.keys()):
                    config_str += "\t\t%s %s\n" % (name, product[name])
                config_str += "\t}\n"
        config_str += "}\n"

    if "multipaths" in list(config_dict.keys()):
        config_str += "multipaths {\n"
        for key in list(config_dict["multipaths"].keys()):
            config_str += "\tmultipath {\n"
            for wwid in config_dict["multipaths"][key]:
                config_str += "\t\t%s %s\n" % (key, wwid)
            config_str += "}\n"
        config_str += "}\n"

    f = open(config_file, "w", encoding='UTF-8')
    f.write(config_str)
    f.close()

    return True


def mpath_device_2_mpath_name(mpath_device):
    """
    Convert an specific multipath device to mpath_name
    Eg. /dev/mapper/mpathap1 => mpatha
    """
    multipath_dev_regex = r"/dev/mapper\/(.*)"
    m = re.match(multipath_dev_regex, mpath_device)
    if m:
        # need to remove partition information
        # Multipath names has changed on RHEL7 and if a device name ends in letter the
        # partition number is just append to the device number, if it ends in digit
        # it appends 'p' before the partition number
        # So we can have device partitions as below...
        # device_name = "mapper/360a98000572d5765636f69746f6a4f6a1"
        # device_name = "mapper/360a98000572d5765636f69746f6a4f61p1"
        device_name = m.group(1)
        m = re.match(r"(.*)p?\d", device_name)
        if not m:
            # does not seem to be a valid mpath device
            return None
        device_name = m.group(1)
        # remove trailing p if it exist
        device_name = re.sub(r"(\S+)p$", r"\1", device_name)
        return device_name
    return None
