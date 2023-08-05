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


"""ontap.py: Module to handle commands on NetApp Ontap Array."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import base64
import libsan.host.fc
import libsan.host.linux
import libsan.misc.array
import libsan.host.ssh
import libsan.misc.size

"""
This module was tested on Ontap version 8.2
"""


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


def _size_human_2_size_netapp(size_human):
    if not size_human:
        _print("FAIL: _size_human_2_size_netapp() - requires size_human parameter")
        return None

    if not libsan.misc.size.size_human_check(size_human):
        _print("FAIL: _size_human_2_size_netapp() - Checking input")
        return None

    m = libsan.misc.size.size_human_regex.match(size_human)
    if m.group(2):
        unit = m.group(2)
        unit = unit.replace("i", "")
        unit = unit.lower()
        return "%s%s" % (m.group(1), unit)
    return None


def _lun_serial2wwid(serial):
    """
    Usage
        _lun_serial2wwid(netapp_serial)
    Purpose
        Convert netapp serial to WWID.
        1. Convert serial to hex string
        2. add '360a98000' at the head
    Parameter
        $netapp_serial  # like '2FiCl+BOAef9'
    Returns
        wwid
    """
    if not serial:
        return None

    # toHex = lambda x:"".join([hex(ord(c))[2:].zfill(2) for c in x])
    wwid = serial

    # wwid = toHex(wwid)
    wwid = base64.b16encode(type("").encode(wwid))
    wwid = "360a98000" + wwid.decode()
    return wwid.lower()


class ontap:
    """
    Class to manage Ontap array
    """
    host = None
    user = None
    passwd = None

    san_conf_path = None
    sa_conf_dict = {}

    luns_dict = {}
    igroups_dict = {}
    map_info = []

    def __init__(self, hostname, username, password, timeout=None, san_dev=None):
        # san_dev is here because we need it for DELL Equalogic array
        self.san_dev_name = san_dev
        self.host = hostname
        self.user = username
        self.passwd = password
        self.timeout = timeout
        self.san_conf_path = None
        # _print("DEBUG: Ontap version is %s" % self.get_version())

    def set_san_conf_path(self, san_conf_path):
        self.san_conf_path = san_conf_path
        return True

    def set_sa_conf(self, sa_conf_dict):
        self.sa_conf_dict = sa_conf_dict
        return True

    def get_sa_conf(self):
        return self.sa_conf_dict

    def _run(self, cmd, ctrler=None, return_output=False, verbose=True):
        if not ctrler:
            ctrler = self.host

        session = libsan.host.ssh.connect(ctrler, user=self.user, passwd=self.passwd)
        if not session:
            _print("FAIL: Could not connect to Storage Array (%s) - user: (%s) "
                   "pass: (%s)" % (self.host, self.user, self.passwd))
            if return_output:
                return 127, None
            return 127

        # If return_output is True, ret will be a tuple
        _print("INFO: Connecting to %s for command:" % ctrler)
        print(cmd)
        ret = libsan.host.ssh.run_cmd(session, cmd, return_output=return_output, verbose=verbose,
                                      invoke_shell=False, timeout=self.timeout)
        libsan.host.ssh.disconnect(session)
        return ret

    def get_version(self):
        """
        Return Ontap version running on array
        """
        cmd = "sysconfig"
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: Getting Ontap version")
            return None
        lines = output.split("\n")
        release_regex = re.compile(r"NetApp Release ([0-9]+)([^ ]+)")
        for line in lines:
            m = release_regex.search(line)
            if m:
                return "Version: %s%s" % (m.group(1), m.group(2))
        return None

    @staticmethod
    def capability():
        """
        Indicates supported operation on array
        """
        cap_dict = dict()
        cap_dict["lun_info"] = True
        cap_dict["lun_query"] = True
        cap_dict["lun_create"] = True
        cap_dict["lun_map"] = True
        cap_dict["lun_unmap"] = True
        cap_dict["lun_remove"] = True
        cap_dict["lun_grow"] = False
        cap_dict["lun_shrink"] = False
        cap_dict["lun_trepass"] = False
        cap_dict["lun_thinp"] = False
        cap_dict["sa_ctrler_reboot"] = True
        return cap_dict

    def query_all_luns(self, recheck=False):
        """
        """
        return sorted(self.query_all_lun_info(recheck=recheck).keys())

    def query_all_lun_info(self, recheck=False):
        """
        Query all LUNs on array and store its information on a dict
        """

        # If we do not need to recheck and port info exist we return it
        if self.luns_dict and not recheck:
            return self.luns_dict

        self.luns_dict = {}

        cmd = "lun show -v"
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            print(output)
            return None

        if not output:
            return None
        # regex = lun_name, netapp_size, size_bytes, and extra options
        # netapp size could be 2g or 2.1g, for example
        _lun_basic_regex = re.compile(r"\s+(/vol/\S+)\s+(\S+[kmgt])\s+\((\d+)\)\s+\((.*)\)?")
        # _lun_basic_regex = re.compile("\s+(/vol/\S+)\s+(\d+[kmgt])\s+\((\d+)\)\s+\(.*\)")
        _lun_serial_regex = re.compile(r"\s+Serial\#:\s+(\S+)")
        _lun_map_regex = re.compile(r"\s+Maps:\s+(\S+)=(\S+)")

        luns_info = output.split("\n")
        lun_info = None

        igroups_info = self.query_all_igroup_info()

        for info in luns_info:
            m = _lun_basic_regex.match(info)
            if m:
                self.luns_dict[m.group(1)] = {}
                lun_info = self.luns_dict[m.group(1)]
                lun_info["name"] = m.group(1)
                lun_info["size_netapp"] = m.group(2)
                lun_info["size_human"] = libsan.misc.size.size_bytes_2_size_human(m.group(3))
                lun_info["size"] = m.group(3)
                continue
            m = _lun_serial_regex.match(info)
            if m:
                if not lun_info:
                    _print("FAIL: Does not know to which lun add serial: %s" % m.group(1))
                    continue
                lun_info["serial"] = m.group(1)
                lun_info["wwid"] = _lun_serial2wwid(m.group(1))
                continue
            m = _lun_map_regex.match(info)
            if m:
                if not lun_info:
                    _print("FAIL: Does not know to which lun add map: %s" % m.group(1))
                    continue
                if "map_infos" not in list(lun_info.keys()):
                    lun_info["map_infos"] = []

                maps = re.findall(r'(\S+)=(\S+)', info)
                for map1 in maps:
                    igroup_name = map1[0]
                    lun_id = map1[1]
                    if igroup_name in list(igroups_info.keys()):
                        igroup_info = igroups_info[igroup_name]

                        if igroup_info["type"] == "iSCSI":
                            for h_iqn in igroup_info["members"]:
                                map_info = dict()
                                map_info["igroup_name"] = igroup_name
                                map_info["t_lun_id"] = lun_id
                                map_info["h_iqn"] = h_iqn
                                lun_info["map_infos"].append(map_info)

                        if igroup_info["type"] == "FCP":
                            for h_wwpn in igroup_info["members"]:
                                map_info = dict()
                                map_info["igroup_name"] = igroup_name
                                map_info["t_lun_id"] = lun_id
                                map_info["h_wwpn"] = h_wwpn
                                lun_info["map_infos"].append(map_info)
                continue

        return self.luns_dict

    def _lun_exist(self, lun_name):
        """
        Test if LUN exist
        If LUN does not exist return error
        """
        if not lun_name:
            _print("FAIL: _lun_exist - requires lun_name")
            return False

        luns_dict = self.query_all_lun_info()
        if not luns_dict:
            _print("FAIL: _lun_exist() - Could not query all lun info")
            return False

        if lun_name in list(luns_dict.keys()):
            return True
        return False

    def lun_info(self, lun_name):
        """
        Query detailed information of specific LUN
        """
        if not lun_name:
            _print("FAIL: lun_info - requires lun_name")
            return None

        luns_dict = self.query_all_lun_info()
        if not luns_dict:
            _print("FAIL: lun_info() - Could not query all lun info")
            return None
        if lun_name in list(luns_dict.keys()):
            return luns_dict[lun_name]

        _print("INFO lun_info(): Could not find LUN %s" % lun_name)
        return None

    def lun_create(self, name, size, flag_thinp=False):
        """
        Create new LUN on array if LUN does not exist
        """
        _print("INFO: Creating LUN %s with size %s" % (name, size))
        if not name or not size:
            _print("FAIL: usage lun_create(name, size)")
            return None

        if self._lun_exist(name):
            _print("INFO: LUN %s already exist" % name)
            return None

        size_human = libsan.misc.size.size_bytes_2_size_human(size)
        size_netapp = _size_human_2_size_netapp(size_human)
        size_bytes = size

        if not size_bytes:
            _print("FAIL: lun_create() - Could not convert %s to bytes" % size)
            return None

        if not size_netapp:
            _print("FAIL: lun_create() - Could not convert %s to NetApp syze" % size)
            return None
        cmd = "lun create -s %s -t linux" % size_netapp
        if flag_thinp:
            cmd += "    -o reserve"
        cmd += " %s" % name
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            print(output)
            return None
        # Need to update our volumes
        luns_dict = self.query_all_lun_info(recheck=True)
        if name not in list(luns_dict.keys()):
            self.lun_remove(name)
            _print("FAIL: thought LUN %s was created, but it was not" % name)
            print(list(luns_dict.keys()))
            return None

        _print("INFO: LUN %s created successfully" % name)
        return name

    def lun_remove(self, name):
        """
        Delete a LUN on array if LUN exists
        """
        if not name:
            _print("FAIL: usage lun_remove(name)")
            return False

        if not self._lun_exist(name):
            _print("INFO: LUN %s do NOT exist" % name)
            return True

        _print("INFO: Deleting LUN %s" % name)
        cmd = "lun destroy -f %s" % name
        max_attempt = 10
        # Sometimes the deletion fials, for example when there is IO on the LUN
        # we can try to delete it few times before giving up
        while max_attempt:
            max_attempt -= 1
            ret, output = self._run(cmd, return_output=True, verbose=False)
            print(output)
            if ret != 0:
                _print("FAIL: \"%s\" command" % cmd)
                print(output)
                libsan.host.linux.sleep(30)
                # try to delete again
                continue
            # Need to update our volumes
            luns_dict = self.query_all_lun_info(recheck=True)
            if name in list(luns_dict.keys()):
                _print("FAIL: thought LUN %s was deleted, but it was not. %d attempts left." % (name, max_attempt))
                print(luns_dict[name])
                libsan.host.linux.sleep(30)
                # try to delete again
                continue
            else:
                # The LUN was deleted
                return True
        return False

    def lun_map(self, name, lun_id=None):
        """
        Map a LUN to an igroup
        """
        if not name:
            _print("FAIL: usage lun_map(name)")
            return False

        if not self._lun_exist(name):
            _print("INFO: LUN %s do NOT exist" % name)
            return False

        if not self.map_info:
            _print("FAIL: lun_map() - There is no mapping info to use")
            return False

        igroups = self.query_all_igroup_info()
        initiator = None
        # To which igroups we should map the LUN
        igroups2map = []
        # Check to to which igroups the LUN should be mapped
        for map_info in self.map_info:
            if ("t_wwpn" in list(map_info.keys()) and
                    "h_wwpn" in list(map_info.keys())):
                initiator = map_info["h_wwpn"]

            if ("t_iqn" in list(map_info.keys()) and
                    "h_iqn" in list(map_info.keys())):
                initiator = map_info["h_iqn"]

            if not initiator:
                _print("FAIL: lun_map() - Do not know how to map using")
                print(map_info)
                return False

            for igroup in list(igroups.keys()):
                if initiator in igroups[igroup]["members"]:
                    if igroups[igroup]["name"] not in igroups2map:
                        igroups2map.append(igroups[igroup]["name"])

        for my_igroup in igroups2map:
            # _print("DEBUG: Mapping LUN %s to %s" % (name, my_igroup))
            cmd = "lun map %s %s" % (name, my_igroup)
            if lun_id:
                cmd += " %s" % lun_id
            ret, output = self._run(cmd, return_output=True, verbose=False)
            if ret != 0:
                _print("FAIL: \"%s\" command" % cmd)
                print(output)
                return False

        # make sure all h_wwpns that we need to map are mapped
        luns_dict = self.query_all_lun_info(recheck=True)
        lun_map_infos = luns_dict[name]["map_infos"]
        found_map = False
        for map_info in self.map_info:
            for lun_map_info in lun_map_infos:
                if "h_wwpn" in list(map_info.keys()):
                    h_wwpn = map_info["h_wwpn"]
                    if h_wwpn in lun_map_info["h_wwpn"]:
                        found_map = True
                if "h_iqn" in list(map_info.keys()):
                    h_iqn = map_info["h_iqn"]
                    if h_iqn in lun_map_info["h_iqn"]:
                        found_map = True
            if not found_map:
                _print("FAIL: Thought it mapped lun %s, but it did not" % name)
                return False

        return True

    def lun_unmap(self, name):
        """
        Unmap a LUN to an IQN
        """
        if not name:
            _print("FAIL: usage lun_unmap(name)")
            return False

        if not self._lun_exist(name):
            _print("INFO: lun_unmap() - LUN %s do NOT exist" % name)
            return False

        if not self.map_info:
            _print("FAIL: lun_unmap() - There is no mapping info to use")
            return False

        igroups = self.query_all_igroup_info()
        initiator = None
        # To which igroups we should map the LUN
        igroups2map = []
        # Check to to which igroups the LUN should be mapped
        for map_info in self.map_info:
            if ("t_wwpn" in list(map_info.keys()) and
                    "h_wwpn" in list(map_info.keys())):
                initiator = map_info["h_wwpn"]

            if ("t_iqn" in list(map_info.keys()) and
                    "h_iqn" in list(map_info.keys())):
                initiator = map_info["h_iqn"]

            if not initiator:
                _print("FAIL: lun_unmap() - Do not know how to unmap using")
                print(map_info)
                return False

            for igroup in list(igroups.keys()):
                if initiator in igroups[igroup]["members"]:
                    if igroups[igroup]["name"] not in igroups2map:
                        igroups2map.append(igroups[igroup]["name"])

        for my_igroup in igroups2map:
            # _print("DEBUG: Mapping LUN %s to %s" % (name, my_igroup))
            cmd = "lun unmap %s %s" % (name, my_igroup)
            ret, output = self._run(cmd, return_output=True, verbose=False)
            if ret != 0:
                _print("FAIL: \"%s\" command" % cmd)
                print(output)
                return False

        # make sure all h_wwpns that we need to map are mapped
        luns_dict = self.query_all_lun_info(recheck=True)
        if "map_infos" not in list(luns_dict[name].keys()):
            # LUN is not mapped to any initiator
            return True
        lun_map_infos = luns_dict[name]["map_infos"]
        found_map = False
        for map_info in self.map_info:
            for lun_map_info in lun_map_infos:
                initiator = None
                if "h_wwpn" in list(map_info.keys()):
                    initiator = map_info["h_wwpn"]
                    if initiator in lun_map_info["h_wwpn"]:
                        found_map = True
                if "h_iqn" in list(map_info.keys()):
                    initiator = map_info["h_iqn"]
                    if initiator in lun_map_info["h_iqn"]:
                        found_map = True
            if not found_map:
                _print("FAIL: lun_unmap() - Tought it unmapped %s from lun %s, but it did not" % (initiator, name))
                return False

        return True

    def _next_free_h_lun_id(self, t_wwpn, h_wwpn):
        """
        Check Ontap target and see what is the Host LUN ID that we could use
        """
        if not t_wwpn or not h_wwpn:
            _print("FAIL: _next_free_h_lun_id() - requires t_wwpn and h_wwpn")
            return None

        good_lun_id = 0
        all_lun_info = self.query_all_lun_info()
        if not all_lun_info:
            # No LUN is mapped, so return 0
            return good_lun_id

        found_lun_ids = []
        for lun in all_lun_info:
            if "map_infos" not in list(all_lun_info[lun].keys()):
                # LUN is not mapped
                continue
            for map_info in all_lun_info[lun]["map_infos"]:
                if (map_info["t_wwpn"] == t_wwpn and
                        map_info["h_wwpn"] == h_wwpn):
                    lun_id = map_info["h_lun_id"]
                    lun_id = lun_id.replace("lun", "")
                    found_lun_ids.append(lun_id)

        if not found_lun_ids:
            return good_lun_id

        return libsan.misc.array.lowest_free_number(found_lun_ids)

    # ####### IGROUP ##############

    def query_all_igroup_info(self, recheck=False):
        """
        Query all igroups on array and store its information on a dict
        """

        # If we do not need to recheck and port info exist we return it
        if self.igroups_dict and not recheck:
            return self.igroups_dict

        self.igroups_dict = {}

        cmd = "igroup show -v"
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            print(output)
            return None

        if not output:
            return None

        _igroup_basic_regex = re.compile(r"\s+(\S+)\s+\((\S+)\):$")
        _igroup_os_type_regex = re.compile(r"\s+Os Type:\s+(\S+)")
        _igroup_member_regex = re.compile(r"\s+Member:\s+(\S+)")

        igroups_info = output.split("\n")
        igroup_info = None
        for info in igroups_info:
            m = _igroup_basic_regex.match(info)
            if m:
                self.igroups_dict[m.group(1)] = {}
                igroup_info = self.igroups_dict[m.group(1)]
                igroup_info["name"] = m.group(1)
                igroup_info["type"] = m.group(2)
                continue
            m = _igroup_os_type_regex.match(info)
            if m:
                if not igroup_info:
                    _print("FAIL: Does not know to which igroup add os_type: %s" % m.group(1))
                    continue
                igroup_info["os_type"] = m.group(1)
                continue
            m = _igroup_member_regex.match(info)
            if m:
                if not igroup_info:
                    _print("FAIL: Does not know to which igroup add member: %s" % m.group(1))
                    continue
                if "members" not in list(igroup_info.keys()):
                    igroup_info["members"] = []
                igroup_info["members"].append(m.group(1))
                continue

        return self.igroups_dict

    # ####### Controllers ##############

    def sa_ctrler_t_wwpns(self, ctrler_ip):
        """
        Usage
            self.sa_ctrler_t_wwpns(ctrler_ip)
        Parameter
            ctrler_ip    # like 10.10.1.2
        Purpose
            Login to controller and list t_wwpns in the controller
        Returns
            A list of t_wwpns
        """

        t_wwpns = []

        cmd = "fcp show adapter"
        ret, output = self._run(cmd, ctrler=ctrler_ip, return_output=True, verbose=False)
        if ret != 0:
            return None

        if not output:
            return None
        lines = output.split("\n")
        online_regex = re.compile(r"FC Portname:\s+(\S+)")

        for line in lines:
            m = online_regex.search(line)
            if m:
                _print("DEBUG: sa_ctrler_t_wwpns() - %s" % line)
                t_wwpn = libsan.host.fc.standardize_wwpn(m.group(1))
                if t_wwpn:
                    t_wwpns.append(t_wwpn)
        return t_wwpns

    def sa_ctrler_reboot(self, ctrler_ip):
        """
        Usage
            self.sa_ctrler_reboot(ctrler_ip)
        Purpose
            Reboot certain controller. This function does not wait controller become
            online.
        Parameter
            ctrler_ip    # like 10.10.1.2
        Returns
            True
            or
            False
        """

        cmd = "reboot -t 0"
        self._run(cmd, ctrler=ctrler_ip, return_output=True, verbose=False)
        return True

    def sa_ctrler_check(self, ctrler_ip):
        """
        Usage
        self.sa_ctrler_check(ctrler_ip)
        Purpose
            Check whether controller is online or not. We depend on this command:
                getagent
        Parameter
            ctrler_ip    # like 10.10.1.2
        Returns
            ctrler_status  # 'online' or 'offline'
            or
            None
        """

        fcp_status = "offline"
        cmd = "fcp status"
        ret, output = self._run(cmd, ctrler=ctrler_ip, return_output=True, verbose=False)
        if ret != 0:
            return "offline"
        if not output:
            return "offline"
        lines = output.split("\n")
        online_regex = re.compile(r"FCP service is running")
        for line in lines:
            if online_regex.search(line):
                fcp_status = "online"

        iscsi_status = "offline"
        cmd = "iscsi status"
        ret, output = self._run(cmd, ctrler=ctrler_ip, return_output=True, verbose=False)
        if ret != 0:
            return "offline"
        if not output:
            return "offline"
        lines = output.split("\n")
        online_regex = re.compile(r"iSCSI service is running")
        for line in lines:
            if online_regex.search(line):
                iscsi_status = "online"

        ctrler_status = "offline"
        cmd = "uptime"
        ret, output = self._run(cmd, ctrler=ctrler_ip, return_output=True, verbose=False)
        if ret != 0:
            ctrler_status = "offline"
        if not output:
            ctrler_status = "offline"
        lines = output.split("\n")
        # Try to match online output
        # ' 10:17am up 13 mins, 0 NFS ops, 0 CIFS ops, 0 HTTP ops, 3521 FCP ops, 0 iSCSI ops'
        online_regex = re.compile(r"\s+\S+\sup\s+\S+")
        for line in lines:
            if online_regex.match(line):
                ctrler_status = "online"
        if ctrler_status == "offline":
            _print("INFO: Controller %s is offline" % ctrler_ip)
            print(lines)
        if fcp_status == "online" and iscsi_status == "online" and ctrler_status == "online":
            return "online"
        return "offline"
