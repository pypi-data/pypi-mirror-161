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

"""fc.py: Module to manipulate FC devices."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import libsan.host.linux
import libsan.host.scsi
import os.path
import re  # regex
import os
from libsan.host.cmdline import run

host_path = "/sys/class/fc_host/"

remote_port_path = "/sys/class/fc_remote_ports/"

regex_target_id = re.compile(r"target(\d+):(\d+):(\d+)")
regex_target = re.compile(r"(\d+):(\d+):(\d+)")
wwn_regex = re.compile(r"(?:[0-9a-f]{2}:){7}[0-9a-f]{2}")


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def is_wwn(wwn):
    """Checks if the entry is on valid WWN format.
    example: 10:00:5c:b9:01:c1:ec:71
    The arguments are:
    \ta WWN
    Returns:
    \tTrue if it is a valid WWN
    \tFalse if the entry is not valid
    """
    m = wwn_regex.match(wwn)
    if m:
        return True
    return False


def standardize_wwpn(wwpn):
    """
    Usage
        standardize_wwpn(wwpn)
    Purpose
        Convert all possiable format wwpn into stand type:
            (?:[0-9a-f]{2}:){7}[0-9a-f]{2} #like: 10:00:00:00:c9:95:2f:de
        Return STRING or ARRAY base on context.
    Parameter
        wwpn           # any format wwpn, like "500A0981894B8DC5"
    Returns
        wwpn
    """
    if not wwpn:
        return None
    wwpn = wwpn.lower()
    if is_wwn(wwpn):
        return wwpn
    wwpn = re.sub("0x", "", wwpn)
    # remove all : characters from the entry, later on they will be added in correct order
    wwpn = wwpn.replace(":", "")
    # append ":" every 2nd character
    wwpn = ":".join(wwpn[i:i + 2] for i in range(0, len(wwpn), 2))
    if is_wwn(wwpn):
        return wwpn
    return None


def query_all_fc_disks(host_id=None):
    """
    Return SCSI disk info all all FC/FCoE devices
    """

    hosts = get_fc_hosts()
    if not hosts:
        # there is not FC/FCoE session
        return None

    if host_id:
        hosts = [host_id]

    scsi_disks = libsan.host.scsi.query_all_scsi_disks()
    fc_disks = {}
    for scsi_id in list(scsi_disks.keys()):
        scsi_disk = scsi_disks[scsi_id]
        if scsi_disk["host_id"] in hosts:
            fc_disks[scsi_id] = scsi_disk
    return fc_disks


def scsi_wwid_of_fc_disks():
    """
    Return a list of all WWIDs of FC/FCoE disks
    """
    disks_info = query_all_fc_disks()
    if not disks_info:
        return None
    wwids = []
    for info in list(disks_info.values()):
        if "wwid" not in list(info.keys()):
            continue
        if info["wwid"] and info["wwid"] not in wwids:
            wwids.append(info["wwid"])
    return wwids


def is_fc_boot():
    """
    Check if it boots from FC/FCoE device
    """
    fc_wwids = scsi_wwid_of_fc_disks()
    if not fc_wwids:
        return False

    boot_dev = libsan.host.linux.get_boot_device()
    if not boot_dev:
        _print("FAIL: is_fc_boot() - Could not determine boot device")
        return False

    boot_wwid = libsan.host.linux.get_device_wwid(boot_dev)
    if not boot_dev:
        _print("WARN: is_fc_boot() - Could not determine boot WWID for %s" % boot_dev)
        return False

    if boot_wwid in fc_wwids:
        return True

    return False


# Return an array with all fc_hosts numbers
def get_fc_hosts():
    cmd = "ls " + host_path
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    # remove 'host' prefix
    output = re.sub("host", "", output)
    host_array = output.split()
    return host_array


def get_fc_host_wwpn(host):
    """
    Return the WWPN of specific host
    """
    host_port_path = "/sys/class/fc_host/host%s/port_name" % host
    cmd = "cat " + host_port_path
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    wwpn = standardize_wwpn(output)
    return wwpn


def fc_host_id_of_wwpn(wwpn):
    """
    Given a WWPN, return its host id
    """
    if not wwpn:
        _print("FAIL: fc_host_id_of_wwpn() - requires wwpn parameter")
        return None
    fc_hosts = get_fc_hosts()
    for fc_host in fc_hosts:
        if get_fc_host_wwpn(fc_host) == wwpn:
            return fc_host

    return None


def h_wwpn_of_host(host=None):
    """
    h_wwpn_of_host
    Usage:
        h_wwpn_of_host(host)
        h_wwpn_of_host()
    Purpose:
        Return a list with the WWPN of specific host
        If no host is given return all WwPNs
    Parameter
        host (options)
    Return
        List:   WWPNs
        None:   Could not find any WWPN
    """
    wwpns = None
    if host:
        hosts = [host]
    else:
        hosts = get_fc_hosts()
    if not hosts:
        return None
    for host in hosts:
        wwpn = get_fc_host_wwpn(host)
        if wwpn:
            if not wwpns:
                wwpns = []
            wwpns.append(wwpn)
    return wwpns


def get_rports():
    rports = os.listdir(remote_port_path)
    if not rports:
        return None
    return rports


def get_fc_host_remote_ports(host):
    cmd = "ls %s | grep rport-%s" % (remote_port_path, host)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    r_ports_array = output.split()
    return r_ports_array


def wwpn_of_rport(r_port):
    cmd = "cat %s/%s/port_name" % (remote_port_path, r_port)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    wwpn = standardize_wwpn(output)
    return wwpn


def rport_of_h_wwpn_t_wwpn(h_wwpn, t_wwpn):
    """
        Return the remote port of given wwpn
    Return:
        r_port       #like rport-7:0-0
            or
        None
    """
    h_wwpn = standardize_wwpn(h_wwpn)
    if not h_wwpn:
        return None
    t_wwpn = standardize_wwpn(t_wwpn)
    if not t_wwpn:
        return None

    host_id = fc_host_id_of_wwpn(h_wwpn)
    if not host_id:
        return None

    # Get all remote ports from this host
    host_rports = get_fc_host_remote_ports(host_id)
    if not host_rports:
        return None

    for rport in host_rports:
        r_wwpn = wwpn_of_rport(rport)
        if not r_wwpn:
            # _print("FAIL: rport_of_h_wwpn_t_wwpn() - Could not get wwpn of rport %s" % rport)
            continue
        if t_wwpn == r_wwpn:
            return rport
    return None


def fc_target_id_of_wwpn(wwpn):
    """
    """
    if not wwpn:
        _print("FAIL: fc_target_id_of_wwpn() - requires wwpn parameter")
        return None
    t_ids = None

    # Get target id of all ports
    rport_id_2_target_id_dict = rport_id_2_target_id()
    if not rport_id_2_target_id_dict:
        return None

    fc_hosts = get_fc_hosts()
    if not fc_hosts:
        return None

    for fc_host in fc_hosts:
        r_ports = get_fc_host_remote_ports(fc_host)
        if not r_ports:
            continue
        for r_port in r_ports:
            if wwpn_of_rport(r_port) == wwpn:
                if not t_ids:
                    t_ids = []
                if r_port in list(rport_id_2_target_id_dict.keys()):
                    t_ids.append(rport_id_2_target_id_dict[r_port])

    return t_ids


def t_wwpn_of_host(host=None):
    """
    t_wwpn_of
    Usage:
        t_wwpn_of(host)
        t_wwpn_of()
    Purpose:
        Return a list with the WWPN of targets of specific host
        If no host is given return all WwPNs
    Parameter
        host (options)
    Return
        List:   WWPNs
        None:   Could not find any WWPN
    """
    wwpns = None
    if host:
        hosts = [host]
    else:
        hosts = get_fc_hosts()
    if not hosts:
        return None

    # Host wwpns are shwon on remote port, we should not return them as target ports
    h_wwpns = h_wwpn_of_host()

    for host in hosts:
        r_ports = get_fc_host_remote_ports(host)
        if r_ports:
            for r_port in r_ports:
                wwpn = wwpn_of_rport(r_port)
                if not wwpn:
                    # _print("FAIL: Could not find wwpn for r_port %s" % r_port)
                    continue
                if wwpn in h_wwpns:
                    # We actually found our own WWPN, skip it
                    continue
                if not wwpns:
                    wwpns = []
                if wwpn not in wwpns:
                    wwpns.append(wwpn)
    return wwpns


def fc_target_id_of_htwwpn(t_wwpn=None, h_wwpn=None):
    """
    Usage
        fc_target_id_of_htwwpn(h_wwpn=>h_wwpn, t_wwpn=>t_wwpn)
    Purpose
        Query out the target_id came from h_wwpn and t_wwpn. As FC has FSPF,
        protocol, we will only got ONE target_id for 1 combination.
    Parameter
        h_wwpn         # Host HBA WWPN
        t_wwpn         # Storage Array front point WWPN
    Returns
        target_id      # like "0:1:0"
            or
        None           # error
    """
    if not t_wwpn or not h_wwpn:
        _print("FAIL: fc_target_id_of_htwwpn() - requires t_wwpn and h_wwpn parameters")
        return None

    scsi_host_id = fc_host_id_of_wwpn(h_wwpn)
    target_ids = fc_target_id_of_wwpn(t_wwpn)
    if not target_ids:
        _print("FAIL: fc_target_id_of_htwwpn(): No FC target assigned to " +
               "target WWPN %s" % t_wwpn)
        return None

    for t_id in target_ids:
        m = regex_target.match(t_id)
        if m:
            if scsi_host_id == m.group(1):
                return t_id
    return None


def scsi_disk_of_htwwpn_wwid(h_wwpn, t_wwpn, wwid):
    """
    Get the scsi disk name connected to specific host and target port and has
    given wwid
    """
    if not h_wwpn or not t_wwpn or not wwid:
        print("FAIL: scsi_disk_of_htwwpn_wwid() - requires h_wwpn, t_wwpn and wwid as parameters")
        return None

    target_id = fc_target_id_of_htwwpn(t_wwpn=t_wwpn, h_wwpn=h_wwpn)
    if not target_id:
        return None

    scsi_disk_ids = libsan.host.scsi.scsi_ids_of_wwid(wwid)
    if not scsi_disk_ids:
        return False

    for scsi_disk_id in scsi_disk_ids:
        if re.match(r"%s:\d+$" % target_id, scsi_disk_id):
            disk_name = libsan.host.scsi.get_scsi_disk_name(scsi_disk_id)
            if not disk_name:
                _print("FAIL: Could not get SCSI disk name of: %s" % scsi_disk_id)
                return False
            return disk_name
    return None


def get_fc_host_rport_targets(host, r_port):
    cmd = "ls /sys/bus/scsi/devices/host%s/%s | grep target" % (host, r_port)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    output = re.sub("target", "", output)
    r_port_targets_array = output.split()
    return r_port_targets_array


def get_fc_host_rport_target_devices(host, r_port, target):
    if not host or not r_port or not target:
        _print("FAIL: get_fc_host_rport_target_devices. Usage: host, r_port, target")
        return None

    cmd = "ls /sys/bus/scsi/devices/host%s/%s/target%s | grep \"%s\"" % (host, r_port, target, target)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    output = re.sub("target", "", output)
    devices_array = output.split()
    return devices_array


def rport_id_2_target_id():
    """
    Usage
        rport_id_2_target_id()
    Purpose
        For lpfc card, their rport_id is different from target_id.
        This function will return this reference:
            rport_id_2_target_id = {
                rport_id : target_id
            }
        Only the rport which provide FC target will return.
    Returns
        rport_id_2_target_id
            or
        None
    """
    if not os.path.isdir(remote_port_path):
        return None

    rport_id_2_target_id_dict = None
    rports = get_rports()
    if not rports:
        return None
    for rport in rports:
        # search for targets connected to this rport
        rport_target_sys_root_path = "%s/%s/device" % (remote_port_path, rport)
        entries = os.listdir(rport_target_sys_root_path)

        for entry in entries:
            m = regex_target_id.match(entry)
            if m:
                if not rport_id_2_target_id_dict:
                    rport_id_2_target_id_dict = {}
                rport_id_2_target_id_dict[rport] = "%s:%s:%s" % (m.group(1), m.group(2), m.group(3))

    return rport_id_2_target_id_dict


def fc_host_transport_type(scsi_host_id):
    """
    """
    if not scsi_host_id:
        _print("FAIL: fc_host_transport_type - requires scsi_host_id")
        return None

    host_model2transport = {"QLE2462": "FC",
                            "QLE8262": "FCoE",
                            "QLE8362": "FCoE",
                            "CN1000Q": "FCoE",
                            "QLogic-1020": "FCoE",
                            "554FLR-SFP+": "FCoE",
                            "Intel 82599": "FCoE"}
    host_info = libsan.host.scsi.query_scsi_host_info(scsi_host_id)
    # Check first if we can find what transport by HBA model
    model_keys = ["model", "model_name"]
    for key in model_keys:
        if key in list(host_info.keys()):
            if host_info[key] in list(host_model2transport.keys()):
                return host_model2transport[host_info[key]]

    # Second option try to parse model description
    if "model_description" in list(host_info.keys()):
        fc_regex1 = re.compile("Fibre Channel")
        fc_regex2 = re.compile(" FC ")
        fcoe_regex = re.compile("FCoE")
        if fc_regex1.search(host_info["model_description"]):
            return "FC"
        if fc_regex2.search(host_info["model_description"]):
            return "FC"
        if fcoe_regex.search(host_info["model_description"]):
            return "FCoE"

    if "model_desc" in list(host_info.keys()):
        fc_regex1 = re.compile("Fibre Channel")
        fc_regex2 = re.compile(" FC ")
        fcoe_regex = re.compile("FCoE")
        if fc_regex1.search(host_info["model_desc"]):
            return "FC"
        if fc_regex2.search(host_info["model_desc"]):
            return "FC"
        if fcoe_regex.search(host_info["model_desc"]):
            return "FCoE"

    if "modeldesc" in list(host_info.keys()):
        fc_regex = re.compile("Fibre Channel")
        fcoe_regex = re.compile("FCoE")
        if fc_regex.search(host_info["modeldesc"]):
            return "FC"
        if fcoe_regex.search(host_info["modeldesc"]):
            return "FCoE"

    if "protocol" in list(host_info.keys()):
        if host_info["protocol"] == "fc":
            return "FC"
        if host_info["protocol"] == "fcoe":
            return "FCoE"

    if "symbolic_name" in list(host_info.keys()):
        fc_regex = re.compile("Fibre Channel")
        fcoe_regex = re.compile("fcoe")
        if fc_regex.search(host_info["symbolic_name"]):
            return "FC"
        if fcoe_regex.search(host_info["symbolic_name"]):
            return "FCoE"

    if "driver" in list(host_info.keys()):
        if host_info["driver"] == "bnx2fc":
            return "FCoE"

    _print("DEBUG: Could not figure out if controller %s is FC or FCoE" % scsi_host_id)
    print(host_info)
    return "(TODO)FC/FCoE"


def get_value_rport_parameter(r_port, r_port_param):
    """
    Usage
        get_value_rport_parameter(r_port, r_port_param)
    Purpose
        Query out the r_port_param via sys:
        /sys/class/fc_remote_ports/rport-3:0-0/dev_loss_tmo
    Parameters
        r_port:         # like "rport0:0-1"
        r_port_param    # like "dev_loss_tmo"
    Returns
        parameter value
            or
        None
    """
    if not r_port or not r_port_param:
        _print("FAIL: get_value_rport_parameter() - requires r_port and r_port_param as parameter")
        return None

    sys_r_port_param = "%s/%s/%s" % (remote_port_path, r_port, r_port_param)
    if not os.path.isfile(sys_r_port_param):
        _print("FAIL: get_value_rport_parameter() - File '%s' does not exist" % sys_r_port_param)
        return None

    ret, value = run("cat %s" % sys_r_port_param, return_output=True, verbose=False)
    if ret != 0:
        _print("FAIL: get_value_rport_parameter() - Could not read %s" % sys_r_port_param)
        # print command output
        print(value)
        return None

    return value


def set_value_rport_parameter(r_port, r_port_param, value):
    """
    Usage
        set_value_rport_parameter(r_port, r_port_param, value)
    Purpose
        Write value to r_port_param via sys:
        /sys/class/fc_remote_ports/rport-3:0-0/dev_loss_tmo
    Parameters
        r_port:         # like "rport-0:0-1"
        r_port_param    # like "dev_loss_tmo"
        value           # like "60"
    Returns
        True
            or
        False
    """
    if not r_port or not r_port_param or value is None:
        _print("FAIL: set_value_rport_parameter() - requires r_port, r_port_param and value as parameter")
        return False

    sys_r_port_param = "%s/%s/%s" % (remote_port_path, r_port, r_port_param)
    if not os.path.isfile(sys_r_port_param):
        _print("FAIL: set_value_rport_parameter() - File '%s' does not exist" % sys_r_port_param)
        return False

    ret, output = run("echo %s > %s" % (value, sys_r_port_param), return_output=True, verbose=False)
    if ret != 0:
        _print("FAIL: set_value_rport_parameter() - Could not set %s to %s" % (sys_r_port_param, value))
        # print command output
        print(output)
        return False
    return True
