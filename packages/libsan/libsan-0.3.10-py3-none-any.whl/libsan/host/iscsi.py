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

"""iscsi.py: Module to manipulate iSCSI devices."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import augeas
import libsan.host.mp
import libsan.host.linux
import libsan.host.scsi
import libsan.host.net
from libsan.host.cmdline import run

# used to match regex for each session information that we support
supported_discovery_info = {"address": r".*DiscoveryAddress: (\S+)",
                            "target": r".*Target: (\S+)",
                            "portal": r".*Portal: (\S+):(\S+),(\S+)",
                            "iface": r".*Iface Name: (\S+)"}

# used to match regex for each session information that we support
supported_session_info = {"t_iqn": r".*Target: (\S+)",
                          "h_iqn": r".*Iface Initiatorname: (\S+)",
                          "iface": r".*Iface Name: (\S+)",
                          "transport": r".*Iface Transport: (\S+)",
                          "iface_ip": r".*Iface IPaddress: (\S+)",
                          "mac": r".*Iface HWaddress: (\S+)",
                          "sid": r".*SID: (\S+)",
                          "host": r".*Host Number: (\S+).*State: (\S+)",  # eg. Host Number: 6	State: running
                          "disks": r".*Attached scsi disk (\S+).*State: (\S+)",
                          # eg. Attached scsi disk sdb		State: running
                          "target_ip": r".*Current Portal: (\S+):[0-9]+,",
                          "persist_ip": r".*Persistent Portal: (\S+):[0-9]+,",
                          # negotiated parameters
                          "header_digest": r".*HeaderDigest: (\S+)",
                          "data_digest": r".*DataDigest: (\S+)",
                          "max_recv": r".*MaxRecvDataSegmentLength: (\S+)",
                          "max_xmit": r".*MaxXmitDataSegmentLength: (\S+)",
                          "first_burst": r".*FirstBurstLength: (\S+)",
                          "max_burst": r".*MaxBurstLength: (\S+)",
                          "immediate_data": r".*ImmediateData: (\S+)",
                          "initial_r2t": r".*InitialR2T: (\S+)",
                          "max_outst_r2t": r".*MaxOutstandingR2T: (\S+)"}

host_path = "/sys/class/iscsi_host/"


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def is_iqn(iqn):
    if re.match(r"^iqn\.", iqn):
        return True
    return False


def install():
    """Install iscsiadm tool
    The arguments are:
    \tNone
    Returns:
    \tTrue: If iscsiadm is installed correctly
    \tFalse: If some problem happened
    """
    pack = "iscsi-initiator-utils"
    if not libsan.host.linux.install_package(pack):
        _print("FAIL: Could not install %s" % pack)
        return False

    return True


# Return an array with all iscsi_hosts numbers
def get_iscsi_hosts():
    cmd = "ls " + host_path
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    # remove 'host' prefix
    output = re.sub("host", "", output)
    host_array = output.split()
    return host_array


# iSCSI discovery ###
def query_discovery():
    """Query all iSCSI targets
    The arguments are:
    \tNone
    Returns:
    \tDict:    Dict with all discovered targets
    \tNone:    If some problem happened
    """
    cmd = "iscsiadm -m discovery -P1"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        # If no target is found iscsiadm returns error code
        return None
    lines = output.split("\n")

    supported_discovery_modes = ["SENDTARGETS", "iSNS", "STATIC", "FIRMWARE"]
    supported_mode_type = {"SENDTARGETS": "sendtargets", "iSNS": "isns"}

    discovery_info_dict = {}
    discovery_address = None
    disc_mode = None
    target_name = None

    for line in lines:
        # print "(%s)" % line
        # Check if it is discovery mode information
        m = re.match("(^.*):", line)
        if m:
            if m.group(1) in supported_discovery_modes:
                disc_mode = m.group(1)
                # We will use DiscoveryAddress as key
                discovery_info_dict[disc_mode] = {}
                discovery_address = None
                continue

        # We will use TargetAddress as key for the target dictionary
        m = re.match(supported_discovery_info["address"], line)
        if m:
            discovery_address = m.group(1)
            if discovery_address not in list(discovery_info_dict[disc_mode].keys()):
                discovery_info_dict[disc_mode][discovery_address] = {}
            disc_addr_regex = re.compile(r"(\S+),(\S+)")
            d = disc_addr_regex.match(discovery_address)
            if d:
                discovery_info_dict[disc_mode][discovery_address]["disc_addr"] = d.group(1)
                discovery_info_dict[disc_mode][discovery_address]["disc_port"] = d.group(2)

            if disc_mode in list(supported_mode_type.keys()):
                discovery_info_dict[disc_mode][discovery_address]["mode"] = supported_mode_type[disc_mode]
            continue

        m = re.match(supported_discovery_info["target"], line)
        if m:
            # FIRMWARE discovery might not use discovery address
            if not discovery_address:
                discovery_address = "NotSet"
                discovery_info_dict[disc_mode][discovery_address] = {}

            target_name = m.group(1)
            if "targets" not in list(discovery_info_dict[disc_mode][discovery_address].keys()):
                discovery_info_dict[disc_mode][discovery_address]["targets"] = {}
            discovery_info_dict[disc_mode][discovery_address]["targets"][target_name] = {}
            continue

        m = re.match(supported_discovery_info["portal"], line)
        if m:
            discovery_info_dict[disc_mode][discovery_address]["targets"][target_name]["portal"] = {}
            discovery_info_dict[disc_mode][discovery_address]["targets"][target_name]["portal"]["address"] = m.group(1)
            discovery_info_dict[disc_mode][discovery_address]["targets"][target_name]["portal"]["port"] = m.group(2)
            continue

        m = re.match(supported_discovery_info["iface"], line)
        if m:
            iface = m.group(1)
            if "iface" not in list(discovery_info_dict[disc_mode][discovery_address]["targets"][target_name].keys()):
                discovery_info_dict[disc_mode][discovery_address]["targets"][target_name]["iface"] = []
            discovery_info_dict[disc_mode][discovery_address]["targets"][target_name]["iface"].append(iface)
            continue
            # print "Found %s: %s" % (key, m.group(1))

    return discovery_info_dict


def discovery_st(target, ifaces=None, disc_db=False):
    """Discover iSCSI target
    The arguments are:
    \ttarget:   Address of target to be discovered
    \tifaces:   iSCSI interfaces to be used, separated by space (optional)
    \tdisc_db:  if should use discoverydb instead of discovery (optional)
    Returns:
    \tTrue:     If it discovered an iSCSI target
    \tFalse:    If some problem happened
    """
    print("INFO: Executing Discovery_ST() with these arges:")
    print("\tTarget: %s" % target)
    if ifaces:
        print("\tIfaces: %s" % ifaces)

    disc_opt = "discovery"
    operation = None

    if disc_db:
        disc_opt = "discoverydb -D"
        operation = "new"

    cmd = "iscsiadm -m %s -p %s" % (disc_opt, target)
    if operation:
        cmd += " -o %s" % operation

    if ifaces:
        interfaces = ifaces.split(" ")
        for interface in interfaces:
            cmd += " -I %s" % interface
    cmd += " -t st"
    retries = 0
    retcode, data = run(cmd, return_output=True, verbose=True)
    while retcode == 0 and "(err 29)" in data and retries < 5:
        retcode, data = run(cmd, return_output=True, verbose=True)
        retries += 1
    if retcode != 0 or retries == 5:
        _print("FAIL: Could not discover iSCSI target")
        return False
    return True


def is_target_discovered(t_iqn):
    """Check if an iSCSI target is already discovered
    The arguments are:
    \tiSCSI Target:   iQN of iSCSI target
    Returns:
    \tTrue:     If target is discovered
    \tFalse:    If was not found
    """
    if not t_iqn:
        _print("FAIL: is_target_discovered() - requires target iqn as parameter")

    disc_dict = query_discovery()
    if not disc_dict:
        return False

    for disc_type in list(disc_dict.keys()):
        for disc_addr in list(disc_dict[disc_type].keys()):
            if "targets" not in list(disc_dict[disc_type][disc_addr].keys()):
                continue
            if t_iqn in list(disc_dict[disc_type][disc_addr]["targets"].keys()):
                # Target is already discovered we do not need to do anything
                return True
    return False


def get_disc_ifaces_of_t_iqn(t_iqn):
    """
    From given target IQN, return the interfaces that discovered it
    The arguments are:
    \tiSCSI Target:   iQN of iSCSI target
    Returns:
    \tList ifaces:     Discovered interfaces
    \tNone:             If iface was not found
    """

    if not t_iqn:
        _print("FAIL: get_t_iqn_disc_ifaces() - requires target iqn")
        return None

    if not is_target_discovered(t_iqn):
        _print("FAIL: get_t_iqn_disc_ifaces() - target iqn: %s is not discovered" % t_iqn)
        return None

    disc_dict = query_discovery()
    for disc_type in list(disc_dict.keys()):
        for disc_addr in list(disc_dict[disc_type].keys()):
            if "targets" not in list(disc_dict[disc_type][disc_addr].keys()):
                continue
            if t_iqn in list(disc_dict[disc_type][disc_addr]["targets"].keys()):
                if "iface" in list(disc_dict[disc_type][disc_addr]["targets"][t_iqn].keys()):
                    return disc_dict[disc_type][disc_addr]["targets"][t_iqn]["iface"]
    return None


def delete_discovery_target_portal(portal, port="3260", tp="st"):
    """Delete discovered iSCSI target
    The arguments are:
    \tportal:   Address of target to be discovered
    \tport:     Port of iSCSI target to be deleted
    \ttp:       Discovery type, sendtargets, isns...
    Returns:
    \tTrue:     If deleted discovered iSCSI target
    \tFalse:    If some problem happened
    """
    _print("INFO: Deleting target portal: %s" % portal)
    if libsan.host.net.get_ip_version(portal) == 6:
        # IF IPv6 we need to append "[" and "]" to the address
        portal = "[" + portal + "]"

    cmd = "iscsiadm -m discoverydb --type %s --portal \"%s:%s\" -o delete" % (tp, portal, port)
    retcode, _ = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete discover iSCSI target")
        return False
    return True


def clean_up(portal="all"):
    """Remove iSCSI session and discover information for specific target
    The arguments are:
    \ttarget:   Address of target to be removed
    Returns:
    \tTrue:     If iSCSI target is removed
    \tFalse:    If some problem happened
    """

    error = 0
    # TODO: iSCSI boot clean up
    if is_iscsi_boot():
        boot_dev = libsan.host.linux.get_boot_device()
        if not boot_dev:
            _print("FAIL: clean_up() - Could not determine boot device")
            return False

        boot_wwid = libsan.host.linux.get_device_wwid(boot_dev)
        if not boot_wwid:
            _print("FAIL: clean_up() - Could not determine boot WWID for %s" % boot_dev)
            return False

        ses_ids = get_all_session_ids()
        if not ses_ids:
            _print("FAIL: is_iscsi_boot() - It is iSCSI boot, but did not find any session ID")
            return False

        if portal == "all":
            # Logout from all iSCSI session, that do not have boot device
            for ses_id in ses_ids:
                iscsi_wwids = scsi_wwid_of_iscsi_session(sid=ses_id)
                if boot_wwid in iscsi_wwids:
                    _print("INFO: Can't log out of session %s, because it is used for iSCSI boot" % ses_id)
                else:
                    _print("INFO: Logging out of session %s" % ses_id)
                    session_logout(ses_id)
                    # TODO Clean up discovery info
        else:
            # TODO Logout single portal from iSCSI boot
            _print("FAIL: clean_up() - Does not know how to clean up portal %s for iSCSI boot" % portal)
            return False

        return True

    # Not iSCSI boot
    if portal == "all":
        # log out of all iSCSI sessions
        if get_all_session_ids():
            # There is at least one session
            if not node_logout():
                _print("FAIL: Could not logout from %s iSCSI target" % portal)
                error += 1
    else:
        if not node_logout(portal=portal):
            _print("FAIL: Could not logout from %s iSCSI target" % portal)
            error += 1

    disc_dict = query_discovery()
    # If there is discovery information
    if disc_dict:
        # We will search for this portal on sendtargets and iSNS
        for mode in list(disc_dict.keys()):
            if mode != "SENDTARGETS" and mode != "iSNS":
                # We only delete discover info for st and isns
                continue
            m_dict = disc_dict[mode]
            # Search for all discovered address if they match the one given
            for addr in list(m_dict.keys()):
                d_dict = m_dict[addr]

                disc_addr = d_dict["disc_addr"]
                port = d_dict["disc_port"]
                if disc_addr == portal or portal == "all":
                    if not delete_discovery_target_portal(disc_addr, port=port, tp=d_dict["mode"]):
                        _print("FAIL: Deleting iSCSI target %s" % d_dict["disc_addr"])
                        error += 1

    if error:
        return False
    return True


# iSCSI session ###
# def query_sessions():
#    #cmd output: tcp: [21] 127.0.0.1:3260,1 iqn.2009-10.com.redhat:storage-1 (non-flash)
#    cmd = "iscsiadm -m session"
#    retcode, output = run(cmd, return_output=True, verbose=False)
#    if (retcode != 0):
#        return None
#    lines = output.split("\n")
#    session_regex = re.compile("(\S+):\s[(\d+)]\s(\S+):(\S+),(\d+),(\S+)")
#    sessions_dict = {}
#    for line in lines:
#        m = session_regex.search(line)
#        if m:
#            sid = m.group(2)
#            ses_dict = {}
#            ses_dict["driver"] = m.group(1)
#            ses_dict["portal"] = m.group(3)
#            ses_dict["portal_port"] = m.group(4)
#            ses_dict["target_iqn"] = m.group(6)
#            sessions[sid] = ses_dict
#    return sessions_dict

def get_all_session_ids():
    cmd = "iscsiadm -m session -P1"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        # _print ("INFO: there is no iSCSI session")
        return None
    lines = output.split("\n")

    session_ids = []

    for line in lines:
        m = re.match(supported_session_info["sid"], line)
        if not m:
            continue
        # print "Found session id: %s" %m.group(1)
        session_ids.append(m.group(1))
    return session_ids


def query_iscsi_session(sid):
    """
    Query information from an specific iSCSI session
    The arguments are:
    \tsid:      Session ID
    Returns:
    \tDict:     A dictionary with session info
    \tNone:     If some problem happened
    """
    if not sid:
        _print("FAIL: query_iscsi_session() - requires sid as argument")
        return None

    regex_session_scsi_id = "^[ \t]+scsi([0-9]+) Channel ([0-9]+) Id ([0-9])+ Lun: ([0-9]+)$"
    cmd = "iscsiadm -m session -P3 -S -r %s" % sid
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        return None
    lines = output.split("\n")

    session_info_dict = {}
    # dict with disk name and its status
    session_disks_dict = {}
    # store host number and status
    session_host_dict = {}
    for line in lines:
        # print "(%s)" % line

        m = re.match(regex_session_scsi_id, line)
        if m:
            host_id = m.group(1)
            target_id_only = m.group(2)
            bus_id_only = m.group(3)
            lun_id = m.group(4)
            target_id_only = re.sub("^0+(?=.)", "", target_id_only)
            scsi_id = "%s:%s:%s:%s" % (host_id, target_id_only, bus_id_only, lun_id)

            if "scsi_id_info" not in list(session_info_dict.keys()):
                session_info_dict["scsi_id_info"] = {}
            session_info_dict["scsi_id_info"][scsi_id] = {}
            session_info_dict["scsi_id_info"][scsi_id]["scsi_id"] = scsi_id

        # Could be more than one scsi disk, will add as dict
        m = re.match(supported_session_info["disks"], line)
        if m:
            disk_dict = dict()
            # disk_dict["scsi_name"] = m.group(1)
            disk_dict["status"] = m.group(2)
            disk_dict["wwid"] = libsan.host.scsi.wwid_of_disk(m.group(1))
            session_disks_dict[m.group(1)] = disk_dict
            continue

        # Could be more than one scsi disk, will add as dict
        m = re.match(supported_session_info["host"], line)
        if m:
            session_host_dict[m.group(1)] = m.group(2)
            continue
        # Generic search for keys and values
        for key in list(supported_session_info.keys()):
            m = re.match(supported_session_info[key], line)
            if not m:
                continue
            # print "Found %s: %s" % (key, m.group(1))
            session_info_dict[key] = m.group(1)
            if session_info_dict[key] == "<empty>":
                session_info_dict[key] = None
                if key == "mac":
                    # Try to get based on iface IP address
                    if "iface_ip" in list(session_info_dict.keys()):
                        nic = libsan.host.net.get_nic_of_ip(session_info_dict["iface_ip"])
                        if nic:
                            session_info_dict[key] = libsan.host.net.get_mac_of_nic(nic)
    # added info for the specific session
    session_info_dict["disks"] = session_disks_dict
    session_info_dict["host"] = session_host_dict
    return session_info_dict


def query_all_iscsi_sessions():
    """
    First we get all iSCSI ids, later on we get the information of each session individually
    """

    session_ids = get_all_session_ids()
    if not session_ids:
        return None

    iscsi_sessions = {}
    # Collecting info from each session
    for sid in session_ids:
        session_info_dict = query_iscsi_session(sid)
        iscsi_sessions[sid] = session_info_dict

    # print iscsi_sessions
    return iscsi_sessions


def session_logout(sid=None):
    """
    """
    cmd = "iscsiadm -m session -u"
    if sid:
        cmd += " -r %s" % sid
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print(output)
        _print("FAIL: session_logout() - Could not logout from session")
        return None
    return True


def get_iscsi_session_by_scsi_id(scsi_id):
    """
    Return the Session Dict that has the scsi_id
    """
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    for ses in sessions:
        if "scsi_id_info" not in list(sessions[ses].keys()):
            continue
        if scsi_id in list(sessions[ses]["scsi_id_info"].keys()):
            return sessions[ses]
    return None


def h_iqn_of_sessions():
    """
    Usage
        h_iqn_of_sessions()
    Purpose
        Get the Host IQNs of all active iSCSI sessions
    Parameter
        None
    Returns
        List:   h_iqns
            or
        None
    """
    h_iqns = None
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    for key in list(sessions.keys()):
        info = sessions[key]
        if "h_iqn" in list(info.keys()):
            if not h_iqns:
                h_iqns = []
            if info["h_iqn"] not in h_iqns:
                h_iqns.append(info["h_iqn"])
    return h_iqns


def t_iqn_of_sessions():
    """
    Usage
        t_iqn_of_sessions()
    Purpose
        Get the Target IQNs of all active iSCSI sessions
    Parameter
        None
    Returns
        List:   t_iqns
            or
        None
    """
    t_iqns = None
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    for key in list(sessions.keys()):
        info = sessions[key]
        if "t_iqn" in list(info.keys()):
            if not t_iqns:
                t_iqns = []
            if info["t_iqn"] not in t_iqns:
                t_iqns.append(info["t_iqn"])
    return t_iqns


def mac_of_iscsi_session():
    """
    Usage
        mac_of_iscsi_session()
    Purpose
        We only check host IQN in active iSCSI session.
    Parameter
        None
    Returns
        List:   macs
            or
        None
    """
    macs = None
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    for key in list(sessions.keys()):
        info = sessions[key]
        if "mac" in list(info.keys()):
            if not macs:
                macs = []
            if info["mac"] != "<empty>" and info["mac"] and info["mac"] not in macs:
                macs.append(info["mac"])
    return macs


def scsi_names_of_iscsi_session(h_iqn=None, t_iqn=None, sid=None):
    """
    Usage
        scsi_names_of_iscsi_session();
        scsi_names_of_iscsi_session(sid=1);
        scsi_names_of_iscsi_session(h_iqn=h_iqn, t_iqn=t_iqn);
    # we should not support this method since the h_iqn for qla4xxx
    #    scsi_names_of_iscsi_session(t_iqn=t_iqn, h_iqn=h_iqn);
        scsi_names_of_iscsi_session(iface=iface,target_ip=target_ip,;
            t_iqn=t_iqn);
        scsi_names_of_iscsi_session(session_id=session_id);
    Purpose
        Query out all SCSI device names for certain iscsi session.
    Parameter
        h_iqn                  # the IQN used by the host
        t_iqn                  # the IQN used by iscsi target
        sid                    # the iSCSI session ID
    Returns
        scsi_names
            or
        None
    """
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    if sid:
        if sid in list(sessions.keys()):
            if "disks" in list(sessions[sid].keys()):
                return list(sessions[sid]["disks"].keys())
        return None

    scsi_names = None
    if not h_iqn and not t_iqn:
        for sid in list(sessions.keys()):
            if "disks" in list(sessions[sid].keys()):
                if not scsi_names:
                    scsi_names = []
                scsi_names.extend(list(sessions[sid]["disks"].keys()))
        return scsi_names

    if h_iqn and t_iqn:
        for sid in list(sessions.keys()):
            if (sessions[sid]["h_iqn"] == h_iqn and
                    sessions[sid]["t_iqn"] == t_iqn):
                if "disks" in list(sessions[sid].keys()):
                    if not scsi_names:
                        scsi_names = []
                    scsi_names.extend(list(sessions[sid]["disks"].keys()))
        return scsi_names

    _print("FAIL: scsi_names_of_iscsi_session() - Unsupported parameters given")
    return None


def scsi_wwid_of_iscsi_session(h_iqn=None, t_iqn=None, sid=None):
    """
    Usage
        scsi_wwid_of_iscsi_session();
        scsi_wwid_of_iscsi_session(sid=1);
        scsi_wwid_of_iscsi_session(h_iqn=h_iqn, t_iqn=t_iqn);
    # we should not support this method since the h_iqn for qla4xxx
    #    scsi_wwid_of_iscsi_session(t_iqn=t_iqn, h_iqn=h_iqn);
        scsi_wwid_of_iscsi_session(iface=iface,target_ip=target_ip,;
            t_iqn=t_iqn);
        scsi_wwid_of_iscsi_session(session_id=session_id);
    Purpose
        Query out all SCSI WWIDs for certain iscsi session.
    Parameter
        h_iqn                  # the IQN used by the host
        t_iqn                  # the IQN used by iscsi target
        sid                    # the iSCSI session ID
    Returns
        wwids
            or
        None
    """
    wwids = None
    if sid:
        sid = str(sid)
        session_info = query_iscsi_session(sid)
        if not session_info:
            return None
        if "disks" in list(session_info.keys()):
            if not wwids:
                wwids = []
            for scsi_name in list(session_info["disks"].keys()):
                wwid = session_info["disks"][scsi_name]["wwid"]
                if wwid and wwid not in wwids:
                    wwids.append(wwid)
            return wwids
        return None

    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    if not h_iqn and not t_iqn:
        for sid in list(sessions.keys()):
            if "disks" in list(sessions[sid].keys()):
                if not wwids:
                    wwids = []
                for scsi_name in list(sessions[sid]["disks"].keys()):
                    wwid = libsan.host.scsi.wwid_of_disk(scsi_name)
                    if wwid and wwid not in wwids:
                        wwids.append(wwid)
        return wwids

    if h_iqn and t_iqn:
        for sid in list(sessions.keys()):
            if (sessions[sid]["h_iqn"] == h_iqn and
                    sessions[sid]["t_iqn"] == t_iqn):
                if "disks" in list(sessions[sid].keys()):
                    if not wwids:
                        wwids = []
                    for scsi_name in list(sessions[sid]["disks"].keys()):
                        wwid = libsan.host.scsi.wwid_of_disk(scsi_name)
                        if wwid and wwid not in wwids:
                            wwids.append(wwid)
        return wwids

    _print("FAIL: scsi_wwid_of_iscsi_session() - Unsupported parameters given")
    return None


def is_iscsi_boot():
    """
    """
    iscsi_wwids = scsi_wwid_of_iscsi_session()
    if not iscsi_wwids:
        return False
    boot_dev = libsan.host.linux.get_boot_device()
    if not boot_dev:
        _print("FAIL: is_iscsi_boot() - Could not determine boot device")
        return False

    boot_wwid = libsan.host.linux.get_device_wwid(boot_dev)
    if not boot_wwid:
        _print("WARN: is_iscsi_boot() - Could not determine boot WWID for %s" % boot_dev)
        return False

    if boot_wwid in iscsi_wwids:
        return True

    return False


# iSCSI node ###
def node_login(options=None, target=None, portal=None, udev_wait_time=15):
    """Login to an iSCSI portal, or all discovered portals
    The arguments are:
    \target:    iSCSI targets to be used, separated by space (optional)
    \toptions:   extra paramters. eg: "-T <target> -p <portal>"
    Returns:
    \tTrue:     If iSCSI node is logged in
    \tFalse:    If some problem happened
    """

    # Going to delete discovered target information
    _print("INFO: Performing iSCSI login")
    cmd = "iscsiadm -m node -l"
    if options:
        cmd += " %s" % options

    if target:
        for target in target.split():
            cmd += " -T %s" % target

    if portal:
        cmd += " -p %s" % portal

    retcode, output = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not login to iSCSI target")
        print(output)
        return False

    libsan.host.linux.wait_udev(udev_wait_time)
    return True


def node_logout(options=None, target=None, portal=None):
    """Logout from an iSCSI node
    The arguments are:
    \toptions:   extra paramters. eg: "-T <target> -p <portal>"
    Returns:
    \tTrue:     If iSCSI node is removed
    \tFalse:    If some problem happened
    """
    ses_dict = query_all_iscsi_sessions()
    if not ses_dict:
        # There is no session to logout just skip
        return True
    _print("INFO: Performing iSCSI logout")
    # Going to logout discovered target information
    cmd = "iscsiadm -m node -u"
    if options:
        cmd += " %s" % options

    if target:
        cmd += " -T %s" % target

    if portal:
        cmd += " -p %s" % portal

    retcode, output = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not logout from iSCSI target")
        print(output)
        return False
    return True


def node_delete(options=None):
    """
    Delete node information
    """
    if not options:
        _print("FAIL: node_delete() - requires portal and/or target parameters")
        return False

    # Going to logout discovered target information
    cmd = "iscsiadm -m node -o delete"
    if options:
        cmd += " %s" % options

    retcode, _ = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete node iSCSI target")
        return False
    return True


# iSCSI iface ###
def iface_query_all_info(iface_name=None):
    """
    Return a dict with interface names as key with detailed information of
    interface
    """
    if iface_name:
        ifaces = [iface_name]
    else:
        ifaces = get_iscsi_iface_names()

    if not ifaces:
        return None

    all_iface_dict = {}
    iface_info_regex = re.compile(r"iface\.(\S+) = (\S+)")

    for iface in ifaces:
        cmd = "iscsiadm -m iface -I %s" % iface
        retcode, output = run(cmd, return_output=True, verbose=False)
        if retcode != 0:
            _print("FAIL: Could not delete node iSCSI target")
            continue
        details = output.split("\n")
        for info in details:
            m = iface_info_regex.match(info)
            if not m:
                continue
            if iface not in list(all_iface_dict.keys()):
                all_iface_dict[iface] = {}
            value = m.group(2)
            if value == "<empty>":
                value = None
            all_iface_dict[iface][m.group(1)] = value

    if iface_name:
        if iface_name not in list(all_iface_dict.keys()):
            return None
        return all_iface_dict[iface_name]

    return all_iface_dict


def iface_update(iface, name, value):
    """Updates iSCSI interface parameter
    The arguments are:
    \tiface # Interface name (-I $)
    \tname  # Name of parameter (-n iface.$)
    \tvalue  # Value to set (-v $)
    Returns:
    \tTrue:     If value is set successfully
    \tFalse:    If some problem happened
    """
    if not iface or not name or not value:
        _print("FAIL: iface_update() - required parameters: iface, name, value")
        return False

    cmd = "iscsiadm -m iface -I %s -o update -n iface.%s -v %s" % (iface, name, value)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not set %s to %s on iface %s" % (name, value, iface))
        print(output)
        return False

    return True


def iface_set_iqn(iqn, iface='default'):
    """
    Set IQN in /etc/iscsi/initiatorname or for specific iface
    Return:
        True
        of
        False
    """
    if not iqn:
        _print("FAIL: iface_set_iqn() - requires iqn to be set")
        return False

    if iface == 'default':
        try:
            with open("/etc/iscsi/initiatorname.iscsi", "w", encoding='UTF-8') as i:
                i.write("InitiatorName=" + str(iqn))
        except Exception as e:
            _print("FAIL: Could not set iqn in /etc/iscsi/initiatorname.iscsi " + e.__str__())
            return False
        libsan.host.linux.service_restart("iscsid")

        return True

    if not iface_update(iface, 'initiatorname', iqn):
        return False

    return True


def iface_set_ip(iface, ip, mask=None, gw=None):
    """
    Set IP information for specific iface
    Return:
        True
        of
        False
    """
    if not iface or not ip:
        _print("FAIL: iface_set_ip() - requires iface and ip parameters")
        return False

    if not iface_update(iface, 'ipaddress', ip):
        return False

    if mask:
        if not iface_update(iface, 'subnet_mask', mask):
            return False

    if gw:
        if not iface_update(iface, 'gateway', gw):
            return False

    return True


def get_iscsi_iface_names():
    """
    Return a list with the name of all iSCSI interfaces on the host
    """
    cmd = "iscsiadm -m iface | cut -d \" \" -f 1"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not read iSCSI interfaces")
        print(output)
        return None
    ifaces = output.split("\n")
    return ifaces


def set_iscsid_parameter(**kwargs):
    """
    Change parameter in iscsid.conf file and restarts iscsid service
    Use dictionary with parameter:value as argument
    """

    aug = augeas.Augeas()
    if not kwargs:
        print('FAIL: Missing dictionary with parameter(s) and value(s)')
        return False

    for key in list(kwargs.keys()):
        print(80 * '#')
        print('INFO: Setting %s to %s in iscsid.conf' % (key, kwargs[key]))
        print(80 * '#')

        aug.set('/files/etc/iscsi/iscsid.conf/' + key, kwargs[key])

    aug.save()

    if not libsan.host.linux.service_restart("iscsid"):
        _print('FAIL: Unable to restart iscsid service')
        return False

    for key in list(kwargs.keys()):
        value_check = aug.get('/files/etc/iscsi/iscsid.conf/' + key)
        if value_check == kwargs[key]:
            print('INFO: %s set successfully to %s' % (key, kwargs[key]))

        else:
            _print('FAIL: Not able to set iscsid.conf/%s' % key)
            return False

    return True


def set_chap(target_user, target_pass, initiator_user=None, initiator_pass=None):
    """Set CHAP authentication.
    Arguments:
    target_user, target_pass -- Username and password used for 1-way authentication.

    initiator_user, initiator pass -- optional, used for 2-way bi-directional authentication.
    """

    if not target_user or not target_pass:
        print('FAIL: set_chap() - requires username and password')
        return False

    parameters = {'node.session.auth.authmethod': 'CHAP',
                  'node.session.auth.username': target_user,
                  'node.session.auth.password': target_pass,
                  'discovery.sendtargets.auth.authmethod': 'CHAP',  # NetApp array requires discovery authentication
                  'discovery.sendtargets.auth.username': target_user,
                  'discovery.sendtargets.auth.password': target_pass}

    if initiator_user and initiator_pass:
        print('INFO: Setting mutual two-way CHAP authentication')
        parameters['node.session.auth.username_in'] = initiator_user
        parameters['node.session.auth.password_in'] = initiator_pass
        parameters['discovery.sendtargets.auth.username_in'] = initiator_user
        parameters['discovery.sendtargets.auth.password_in'] = initiator_pass

    if not set_iscsid_parameter(**parameters):
        print('FAIL: Unable to set CHAP authentication')
        return False

    if not libsan.host.linux.service_restart("iscsid"):
        print('FAIL: Unable to restart iscsid service')
        return False

    print('INFO: CHAP authentication enabled')
    return True


def disable_chap():
    """Disable CHAP authentication in iscsid.conf and restarts the service"""

    aug = augeas.Augeas()

    # Removing all previously set auth parameters. Commented-out lines stays intact
    parameters = ['node.session.auth.authmethod',
                  'node.session.auth.username',
                  'node.session.auth.password',
                  'discovery.sendtargets.auth.authmethod',
                  'discovery.sendtargets.auth.username',
                  'discovery.sendtargets.auth.password',
                  'node.session.auth.username_in',
                  'node.session.auth.password_in',
                  'discovery.sendtargets.auth.username_in',
                  'discovery.sendtargets.auth.password_in']

    for param in parameters:
        aug.remove('/files/etc/iscsi/iscsid.conf/' + param)

    aug.save()

    if not libsan.host.linux.service_restart("iscsid"):
        print('FAIL: Unable to restart iscsid service')
        return False


def multipath_timeo(seconds=None):
    """"
    If multipath is used for iSCSI session, session replacement
    timeout time should be decreased from default 120 seconds
    https://access.redhat.com/solutions/1171203
    multipathd service should be running when calling this
    The arguments are:
    \tSeconds - default 10 or number of seconds
    Returns:
    \tTrue: Successfully modified iscsid config file.
    \tFalse: There was some problem.
    """

    param = 'node.session.timeo.replacement_timeout'

    if not seconds:
        seconds = 10
    seconds = str(seconds)

    if libsan.host.mp.is_multipathd_running():
        print('INFO: multipathd is running')
    else:
        print('FAIL: multipathd is not running')
        return False

    if not libsan.host.linux.service_restart("iscsid"):
        _print('FAIL: Unable to restart iscsid service')
        return False

    if not set_iscsid_parameter(**{param: seconds}):
        return False

    return True


def create_iscsi_iface(iface_name, mac=None):
    """
    Create a new iSCSI interface, assign mac if specified
    """
    if not iface_name:
        _print("FAIL: create_iscsi_iface() - requires iface name as parameter")
        return False

    if iface_name in get_iscsi_iface_names():
        _print("INFO: iSCSI interface '%s' already exists" % iface_name)
        return True

    cmd = "iscsiadm -m iface -o new -I %s" % iface_name
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not create iSCSI interface")
        print(output)
        return False

    if mac is not None:
        if not iface_update(iface_name, 'hwaddress', mac):
            return False

    return True


def clone_iscsi_iface(new_iface_name, base_iface):
    print("Cloning iface: %s to %s" % (base_iface, new_iface_name))
    if not create_iscsi_iface(new_iface_name):
        return False

    iface_info = iface_query_all_info(base_iface)
    if iface_info is None:
        print("FAIL: Could not query all info about iface: %s" % base_iface)
        return False

    if iface_info["hwaddress"] is not None:
        if not iface_update(new_iface_name, "hwaddress", iface_info["hwaddress"]):
            return False

    if iface_info["transport_name"] is not None:
        if not iface_update(new_iface_name, "transport_name", iface_info["transport_name"]):
            return False

    if iface_info["initiatorname"] is not None:
        if not iface_update(new_iface_name, "initiatorname", iface_info["initiatorname"]):
            return False

    if iface_info["ipaddress"] is not None:
        if not iface_update(new_iface_name, "ipaddress", iface_info["ipaddress"]):
            return False

    print("successully cloned %s. new iface: %s" % (base_iface, new_iface_name))
    return True


def remove_iscsi_iface(iface_name):
    if iface_name not in get_iscsi_iface_names():
        _print("INFO: iSCSI interface '%s' does not exist" % iface_name)
        return False

    cmd = "iscsiadm -m iface -o delete -I %s" % iface_name
    retcode = run(cmd, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not remove iSCSI interface")
        return False

    return True


def node_iface_info(iface_name):
    cmd = "iscsiadm -m node -I %s" % iface_name
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not get iface info!")
        print(output)
        return False

    return True

# iSCSI disks ###


def get_all_iscsi_disks():
    sessions = query_all_iscsi_sessions()
    disks = []
    if not sessions:
        # there is no iSCSI session
        return None

    # search for disks in each session
    for sid in list(sessions.keys()):
        ses = sessions[sid]
        if ses["disks"]:
            # disk names are key values
            disks.extend(list(ses["disks"].keys()))

    return disks


def get_session_id_from_disk(disk_name):
    for sid in query_all_iscsi_sessions():
        session = query_iscsi_session(sid)
        if not session:
            _print("FAIL: Could not query iscsi session sid: '%s'." % sid)
        if disk_name in session["disks"]:
            return session["sid"]
    _print("FAIL: Could not find disk '%s' in iscsi sessions." % disk_name)
    return None
