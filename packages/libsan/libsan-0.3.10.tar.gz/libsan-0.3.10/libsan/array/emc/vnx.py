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

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

""" vnx.py: Module to handle commands on EMC VNX Array.
    We assume  NaviSphere (naviseccli) is installed """

import re  # regex
import libsan.misc.size
import libsan.host.linux
import libsan.misc.array
import libsan.host.fc
import libsan.host.iscsi
from libsan.host.cmdline import run


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


def _lun_uid2wwid(uid):
    """
    Usage
        _lun_uid2wwid(uid)
    Purpose
        Convert VNC UID to WWID.
        1. It simply add 3 at the front
        2. remove all :
    Parameter
        uid:        # like 60:06:01:60:A3:26:11:00:DD:C5:51:79:9F:F8:E1:11
    Returns
        wwid:       # like '360060160a3261100008c2782b292e211'
    """
    if not uid:
        return None

    wwid = "3%s" % uid

    wwid = wwid.replace(":", "")
    wwid = wwid.lower()
    return wwid


def _uid2wwnn_wwpn(uid):
    """
    Convert UID format to WWNN and WWPN
    Return a dict
    """
    if not uid:
        _print("FAIL: _uid2wwnn_wwpn() - requires uid as parameter")
        return None
    uid = libsan.host.fc.standardize_wwpn(uid)
    if not uid:
        # uid for example, can be an iqn
        # _print("FAIL: _uid2wwnn_wwpn() - Could not standardize uid")
        return None

    emc_wwpn_regex = "(?:[0-9a-f]{2}:){7}[0-9a-f]{2}"
    emc_wwnn_regex = emc_wwpn_regex
    emc_hba_id = re.compile("(%s):(%s)" % (emc_wwnn_regex, emc_wwpn_regex))

    m = emc_hba_id.match(uid)
    if not m:
        return None

    ret = dict()
    ret["wwnn"] = libsan.host.fc.standardize_wwpn(m.group(1))
    ret["wwpn"] = libsan.host.fc.standardize_wwpn(m.group(2))
    return ret


class vnx:
    """
    Class to manage VNX array
    """
    host = None
    user = None
    passwd = None

    navi_cli_path = "/opt/Navisphere/bin/naviseccli"
    navi_scope = 0
    ctrl_storage_pool = None

    san_conf_path = None
    sa_conf_dict = {}

    luns_dict = {}
    storage_groups_dict = {}
    ssports = []

    map_info = []
    BLOCK_SIZE_EMC_VNX_VNX = 512

    # Used for getall command
    get_all_output = None

    def __init__(self, hostname, username, password, timeout=None, san_dev=None):
        # san_dev is here because we need it for DELL Equalogic array class
        self.san_dev_name = san_dev
        self.host = hostname
        self.user = username
        self.passwd = password
        self.timeout = timeout

    def set_san_conf_path(self, san_conf_path):
        self.san_conf_path = san_conf_path
        return True

    def set_sa_conf(self, sa_conf_dict):
        self.sa_conf_dict = sa_conf_dict
        if self.sa_conf_dict:
            if "navi_cli_path" in list(self.sa_conf_dict.keys()):
                self.navi_cli_path = self.sa_conf_dict["navi_cli_path"]

            if "navi_scope" in list(self.sa_conf_dict.keys()):
                self.navi_scope = self.sa_conf_dict["navi_scope"]

            if "navi_scope" in list(self.sa_conf_dict.keys()):
                self.navi_scope = self.sa_conf_dict["navi_scope"]

            if "ctrl_storage_pool" in list(self.sa_conf_dict.keys()):
                self.ctrl_storage_pool = self.sa_conf_dict["ctrl_storage_pool"]

        return True

    def get_sa_conf(self):
        return self.sa_conf_dict

    def _run(self, cmd, ctrler=None, return_output=False, verbose=True):
        if not ctrler:
            ctrler = self.host

        _print("INFO: Connecting to %s for command:" % ctrler)

        navi_prefix = ("%s -User %s -Scope %s -h %s -Password %s" % (self.navi_cli_path, self.user,
                                                                     self.navi_scope, ctrler, self.passwd))
        if self.timeout:
            navi_prefix += " -t %s" % self.timeout

        print(cmd)
        cmd = "%s %s" % (navi_prefix, cmd)
        # If return_output is True, ret will be a tuple
        ret = run(cmd, return_output=return_output, verbose=verbose)
        # ret = ssh.run_cmd(session, cmd, return_output = return_output, verbose = verbose,
        #                  invoke_shell = False, timeout=self.timeout)
        # ssh.disconnect(session)
        return ret

    @staticmethod
    def get_version():
        """
        Return Firmware version running on array
        """
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
        cap_dict["lun_thinp"] = True
        cap_dict["sa_ctrler_reboot"] = True
        return cap_dict

    def _get_all(self, recheck=False):
        """
        """
        if self.get_all_output and not recheck:
            return self.get_all_output

        cmd = "getall"
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            print(output)
            return None

        if not output:
            return None

        self.get_all_output = None
        self.get_all_output = output.split("\n")
        return self.get_all_output

    def query_all_luns(self, recheck=False):
        """
        """
        all_luns_info = self.query_all_lun_info(recheck=recheck)
        if not all_luns_info:
            return None
        return sorted(all_luns_info.keys())

    def query_all_lun_info(self, recheck=False):
        """
        Query all LUNs on array and store its information on a dict
        """

        # If we do not need to recheck and port info exist we return it
        # if self.luns_dict and not recheck:
        #    return self.luns_dict

        self.luns_dict = {}

        # If not recheck, it will return exiting information
        getall_info = self._get_all(recheck=recheck)
        if not getall_info:
            return None

        storage_grp_info = self.query_all_storage_group_info()
        # _print("DEBUG: query_all_lun_info() - dump storage grps:")
        # print storage_grp_info

        _lun_section_regex = re.compile(r"All logical Units Information")
        _raid_section_regex = re.compile(r"All RAID Groups Information")
        _lun_id_regex = re.compile(r"LOGICAL UNIT NUMBER (\d+)$")
        # If no name was given to the LUN they will be called like "LUN 10"
        # so they might contain space characters
        _lun_name_regex = re.compile(r"Name\s+(\S+.*)$")
        _lun_capacity_regex = re.compile(r"LUN Capacity\(Blocks\):\s+(\d+)$")
        _lun_default_owner_regex = re.compile(r"Default [Oo]wner: +SP ([A-Z]+)")
        _lun_current_owner_regex = re.compile(r"Current [Oo]wner: +SP ([A-Z]+)")
        _lun_uid_regex = re.compile(r"UID:[ \t]+([0-9A-F:]+)$")

        flag_all_lun_info_begin = False
        lun_info = None

        # Lun ID is the first item that is listed for a LUN
        # We store it to the lun info once we get the LUN name
        lun_id = None

        for info in getall_info:
            if _lun_section_regex.match(info):
                flag_all_lun_info_begin = True
                continue
            if _raid_section_regex.match(info):
                flag_all_lun_info_begin = False
                continue

            if not flag_all_lun_info_begin:
                continue

            # _print("DEBUG: LUN info '%s'" % info)
            m = _lun_id_regex.match(info)
            if m:
                lun_id = m.group(1)
                continue

            m = _lun_name_regex.match(info)
            if m:
                if m.group(1) in list(self.luns_dict.keys()):
                    _print("FAIL: query_all_lun_info() - Found lun name (%s) twice" % m.group(1))
                    print(getall_info)
                    continue
                self.luns_dict[m.group(1)] = {}
                lun_info = self.luns_dict[m.group(1)]
                lun_info["name"] = m.group(1)
                lun_info["lun_id"] = lun_id
                continue

            # Skip while LUN name is not found
            if not lun_info:
                continue

            m = _lun_capacity_regex.match(info)
            if m:
                if not lun_info:
                    _print("FAIL: Does not know to which lun add capacity: %s" % m.group(1))
                    continue
                if "size" in list(lun_info.keys()) or "size_human" in list(lun_info.keys()):
                    _print("FAIL: query_all_lun_info() - It looks like we are parsing LUN info for LUN: %s twice" %
                           lun_info["name"])
                    return None
                lun_info["size"] = int(m.group(1)) * self.BLOCK_SIZE_EMC_VNX_VNX
                lun_info["size_human"] = libsan.misc.size.size_bytes_2_size_human(lun_info["size"])
                continue

            m = _lun_default_owner_regex.match(info)
            if m:
                if not lun_info:
                    _print("FAIL: Does not know to which lun add default owner: %s" % m.group(1))
                    continue
                lun_info["default_sp"] = m.group(1)

            m = _lun_current_owner_regex.match(info)
            if m:
                if not lun_info:
                    _print("FAIL: Does not know to which lun add current owner: %s" % m.group(1))
                    continue
                lun_info["current_sp"] = m.group(1)
                continue
            m = _lun_uid_regex.match(info)
            if m:
                if not lun_info:
                    _print("FAIL: Does not know to which lun add wwid: %s" % m.group(1))
                    continue
                lun_info["wwid"] = _lun_uid2wwid(m.group(1))

        # add map info
        # _print("DEBUG: Query all info - updating map info")
        # print storage_grp_info["st61_intel x520 boot"]
        for lun_info in list(self.luns_dict.values()):
            lun_info["map_infos"] = []

            if not storage_grp_info:
                continue

            for key in list(storage_grp_info.keys()):
                grp_info = storage_grp_info[key]
                if "map_infos" not in list(grp_info.keys()):
                    continue

                for grp_map_info in grp_info["map_infos"]:
                    if grp_map_info["t_lun_id"] == lun_info["lun_id"]:
                        # _print("DEBUG: processing map for st group %s for lun %s" % (key, lun_info["name"]))
                        # Check for intiiator information
                        if "hba_infos" in list(grp_info.keys()):
                            for hba_info in grp_info["hba_infos"]:
                                # _print ("DEBUG: %s" % hba_info)
                                map_info = dict()
                                map_info["st_group_name"] = key
                                # map_info["t_lun_id"] = grp_map_info["t_lun_id"]
                                map_info["h_lun_id"] = grp_map_info["h_lun_id"]
                                map_info["sp_name"] = hba_info["sp_name"]
                                map_info["sp_port"] = hba_info["sp_port"]
                                if "t_wwpn" in list(hba_info.keys()):
                                    map_info["t_wwpn"] = hba_info["t_wwpn"]
                                if "h_wwpn" in list(hba_info.keys()):
                                    map_info["h_wwpn"] = hba_info["h_wwpn"]

                                if "t_iqn" in list(hba_info.keys()):
                                    map_info["t_iqn"] = hba_info["t_iqn"]
                                if "h_iqn" in list(hba_info.keys()):
                                    map_info["h_iqn"] = hba_info["h_iqn"]

                                # if map_info not in lun_info["map_infos"]:
                                lun_info["map_infos"].append(map_info)
                        else:
                            # the mapping can be done with only host and target lun IDs
                            if "h_lun_id" in list(grp_map_info.keys()):
                                map_info = dict()
                                map_info["st_group_name"] = key
                                map_info["t_lun_id"] = grp_map_info["t_lun_id"]
                                map_info["h_lun_id"] = grp_map_info["h_lun_id"]
                                lun_info["map_infos"].append(map_info)

        return self.luns_dict

    def query_all_spport_info(self, recheck=False):
        """
        Query all SPPORt on array and store its information on a dict
        """

        # If we do not need to recheck and port info exist we return it
        # if self.ssports and not recheck:
        #    return self.ssports

        self.ssports = []

        # If not recheck, it will return exiting information
        getall_info = self._get_all(recheck=recheck)
        if not getall_info:
            return None

        _spport_section_regex = re.compile(r"Information about each SPPORT:")
        _sp_info_section_regex = re.compile(r"^SP Information:$")
        _spport_name_regex = re.compile(r"SP Name:\s+(SP \S+)$")
        _spport_port_id_regex = re.compile(r"SP Port ID:\s+(\d+)$")
        _spport_port_uid_regex = re.compile(r"SP UID:\s+(\S+)$")

        flag_all_spport_info_begin = False
        ssport_info = None

        # Lun ID is the first item that is listed for a LUN
        # We store it to the lun info once we get the LUN name

        for info in getall_info:
            if _spport_section_regex.match(info):
                flag_all_spport_info_begin = True
                continue
            if _sp_info_section_regex.match(info):
                flag_all_spport_info_begin = False
                continue

            if not flag_all_spport_info_begin:
                continue

            m = _spport_name_regex.match(info)
            if m:
                ssport_info = {}
                self.ssports.append(ssport_info)
                ssport_info["name"] = m.group(1)
                # Fix naming to match san top name standard
                # use lower case
                ssport_info["name"] = ssport_info["name"].lower()
                # remove spaces
                ssport_info["name"] = ssport_info["name"].replace(" ", "")
                continue

            # Skip while LUN name is not found
            if not ssport_info:
                continue

            m = _spport_port_id_regex.match(info)
            if m:
                if not ssport_info:
                    _print("FAIL: Does not know to which ssport add ID: %s" % m.group(1))
                    continue
                ssport_info["port_id"] = m.group(1)
                continue

            m = _spport_port_uid_regex.match(info)
            if m:
                if not ssport_info:
                    _print("FAIL: Does not know to which ssport add uid: %s" % m.group(1))
                    continue
                ssport_info["uid"] = m.group(1)
                port_info = _uid2wwnn_wwpn(m.group(1))
                if port_info:
                    ssport_info["wwnn"] = port_info["wwnn"]
                    ssport_info["wwpn"] = port_info["wwpn"]

        return self.ssports

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

    def lun_create(self, name, size):
        """
        Create new LUN on array if LUN does not exist
        Purpose
            Perform LUN creation on EMC VNX. This method only create LUN
            on strorage array, you need call lun_map() or lun_create_and_map().

            If $lun_name is undefined, we will use the lowest free LUN ID.

            Before this method return, we will update lun info by call
            query_all_lun_info().
            We need the output of these commands on EMC VNX.
                lun -create type "Thin"
                    -capacity int(size / 512) -sq bc \
                    -poolId ctrl_storage_pool \
                    -name lun_name
        Parameters
            size        # size, accept exapmle: "1KiB" "2GiB" "3MiB"
                        # http://physics.nist.gov/cuu/Units/binary.html
            lun_name    # the LUN name on storage array. like:
                        #  tmp_lun_20160411192741815629
        Return
            lun_name
            or
            None
        """
        size = int(size)
        _print("INFO: Creating LUN %s with size %s" % (name, size))
        if not name or not size:
            _print("FAIL: usage lun_create(name, size)")
            return None

        # We are always using Thin provisioning
        thinp_str = "Thin"

        if self._lun_exist(name):
            _print("INFO: LUN %s already exist" % name)
            return None

        size_bytes = size

        if not size_bytes:
            _print("FAIL: lun_create() - Could not convert %s to bytes" % size)
            return None

        capacity = int(size / self.BLOCK_SIZE_EMC_VNX_VNX)
        if not capacity or self.ctrl_storage_pool is None:
            _print("FAIL: lun_create() - missing capacity or ctrl storage pool parameter")
            return None

        cmd = ("lun -create -type %s -poolId %s -sq bc -name %s -capacity %s -sp a -aa 1" %
               (thinp_str, self.ctrl_storage_pool, name, capacity))

        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: lun_create() - \"%s\" command" % cmd)
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
        Purpose
            Remove LUN on EMC VNX.
            We depend on these commands:
                lun -destroy -name lun_name -o
            If that LUN is mapped, we ill unmap it before we destroy it.
        Parameters
            lun_name
        Returns
            True       #remove pass or no such lun exsit
                or
            False
        """
        if not name:
            _print("FAIL: usage lun_remove(name)")
            return False

        self.query_all_lun_info(recheck=True)
        if not self._lun_exist(name):
            _print("INFO: LUN %s do NOT exist" % name)
            return True

        lun_info_dict = self.lun_info(name)
        if not lun_info_dict:
            _print("FAIL: Could not get information for LUN %s" % name)
            return False

        # Need to unmap mapped groups
        unmap_st_grps = []
        if "map_infos" in list(lun_info_dict.keys()):
            for lun_map_info in lun_info_dict["map_infos"]:
                if lun_map_info["st_group_name"] not in unmap_st_grps:
                    unmap_st_grps.append(lun_map_info["st_group_name"])

        if unmap_st_grps:
            for unmap_grp in unmap_st_grps:
                if not self.lun_unmap(name, st_grp_name=unmap_grp):
                    _print("FAIL: lun_remove() - Could not unmap LUN %s from '%s'" % (name, unmap_grp))
                    return False

        _print("INFO: Deleting LUN %s" % name)
        cmd = "lun -destroy -name %s -o" % name
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            print(output)
            return False
        # VNX takes a while to update lun info
        max_wait = 10
        while max_wait:
            libsan.host.linux.sleep(5)
            # Need to update our volumes
            luns_dict = self.query_all_lun_info(recheck=True)
            if name not in list(luns_dict.keys()):
                _print("INFO: LUN %s got removed" % name)
                return True
            _print("INFO: LUN %s still exist, keep waiting %s" % (name, max_wait))
            max_wait -= 1
        _print("FAIL: Thought LUN %s was deleted, but it is still on array" % name)
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

        st_grps_dict = self.query_all_storage_group_info()
        if not st_grps_dict:
            _print("FAIL: lun_map() - Could not find any storage group on VXN array")
            return False

        # To which storage group we should map the LUN
        st_grps2map = []
        # Check to to which storage group the LUN should be mapped
        for map_info in self.map_info:
            if ("t_wwpn" in list(map_info.keys()) and
                    "h_wwpn" in list(map_info.keys())):
                for st_grp in list(st_grps_dict.keys()):
                    if "hba_infos" not in list(st_grps_dict[st_grp].keys()):
                        continue
                    # _print("DEBUG: st_grp:")
                    # print st_grps_dict[st_grp]
                    for hba_info in st_grps_dict[st_grp]["hba_infos"]:
                        if "h_wwpn" in list(hba_info.keys()) and hba_info["h_wwpn"] == map_info["h_wwpn"]:
                            if st_grps_dict[st_grp]["name"] not in st_grps2map:
                                # _print("DEBUG: lun_map")
                                # print hba_info
                                st_grps2map.append(st_grps_dict[st_grp]["name"])

            if ("t_iqn" in list(map_info.keys()) and
                    "h_iqn" in list(map_info.keys())):
                for st_grp in list(st_grps_dict.keys()):
                    if "hba_infos" not in list(st_grps_dict[st_grp].keys()):
                        continue
                    # _print("DEBUG: st_grp:")
                    # print st_grps_dict[st_grp]
                    for hba_info in st_grps_dict[st_grp]["hba_infos"]:
                        if "h_iqn" in list(hba_info.keys()) and hba_info["h_iqn"] == map_info["h_iqn"]:
                            if st_grps_dict[st_grp]["name"] not in st_grps2map:
                                # _print("DEBUG: lun_map")
                                # print hba_info
                                st_grps2map.append(st_grps_dict[st_grp]["name"])

            if not st_grps2map:
                _print("FAIL: lun_map() - Do not know how to map using")
                print(map_info)
                _print("Storage groups on VNX array:")
                print(st_grps_dict)
                return False

        lun_info_dict = self.lun_info(name)
        if not lun_info_dict:
            _print("FAIL: Could not query LUN %s info" % name)
            return False

        for my_stgrp in st_grps2map:
            # print st_grps_dict[my_stgrp]
            stgrp_mapped = False
            if "map_infos" in list(lun_info_dict.keys()):
                for lun_map_info in lun_info_dict["map_infos"]:
                    # Just skip print info multiple times
                    if stgrp_mapped:
                        continue
                    if lun_map_info["st_group_name"] == my_stgrp:
                        # LUN already mapped to this storage group
                        _print("INFO: LUN %s is already mapped to '%s'" % (name, my_stgrp))
                        stgrp_mapped = True
                        continue
            if stgrp_mapped:
                continue
            # Search for lowest lun_id it can assign to host
            if lun_id is None:
                _lun_ids = []
            if "map_infos" in list(st_grps_dict[my_stgrp].keys()):
                for map_info in st_grps_dict[my_stgrp]["map_infos"]:
                    if "h_lun_id" in list(map_info.keys()):
                        _lun_ids.append(map_info["h_lun_id"])

            lun_id = libsan.misc.array.lowest_free_number(_lun_ids)
            # _print("DEBUG: lun_map() - map st_grp %s h_lun_id %s t_lun_id %s" % (my_stgrp, lun_id,
            # lun_info_dict["lun_id"]))
            _print("INFO: Mapping LUN %s to '%s'" % (name, my_stgrp))
            cmd = "storagegroup -addhlu -gname '%s' -hlu %s -alu %s" % (my_stgrp, lun_id, lun_info_dict["lun_id"])
            ret, output = self._run(cmd, return_output=True, verbose=False)
            if ret != 0:
                _print("FAIL: \"%s\" command" % cmd)
                print(output)
                return False

        # make sure all h_wwpns that we need to map are mapped
        self.query_all_lun_info(recheck=True)
        lun_info_dict = self.lun_info(name)
        if not lun_info_dict:
            _print("FAIL: lun_map() - Could not query LUN %s" % name)
            return False
        if "map_infos" not in list(lun_info_dict.keys()):
            _print("FAIL: lun_map() - Could not find map info for LUN %s" % name)
            return False

        lun_map_infos = lun_info_dict["map_infos"]
        # _print("DEBUG: lun_map() - found lun maps:")
        # print lun_map_infos
        # print lun_info_dict

        found_map = False
        h_wwpn = None
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
                _print("FAIL: Tought it mapped %s to lun %s, but it did not" % (h_wwpn, name))
                return False

        return True

    def lun_unmap(self, name, st_grp_name=None):
        """
        Unmap a LUN to an IQN
        """
        if not name:
            _print("FAIL: usage lun_unmap(name)")
            return False

        if not self._lun_exist(name):
            _print("INFO: lun_unmap() - LUN %s do NOT exist" % name)
            return False

        if not self.map_info and not st_grp_name:
            _print("FAIL: lun_unmap() - There is no mapping info to use")
            return False

        st_grps_dict = self.query_all_storage_group_info()

        # To which igroups we should map the LUN
        st_grps2map = []
        if st_grp_name:
            st_grps2map.append(st_grp_name)
        else:
            # Check to to which storage group the LUN should be mapped
            for map_info in self.map_info:
                if ("t_wwpn" in list(map_info.keys()) and
                        "h_wwpn" in list(map_info.keys())):
                    for st_grp in list(st_grps_dict.keys()):
                        if "hba_infos" not in list(st_grps_dict[st_grp].keys()):
                            continue
                        # _print("DEBUG: st_grp:")
                        # print st_grps_dict[st_grp]
                        for hba_info in st_grps_dict[st_grp]["hba_infos"]:
                            if "h_wwpn" in list(hba_info.keys()) and hba_info["h_wwpn"] == map_info["h_wwpn"]:
                                if st_grps_dict[st_grp]["name"] not in st_grps2map:
                                    # _print("DEBUG: lun_map")
                                    # print hba_info
                                    st_grps2map.append(st_grps_dict[st_grp]["name"])

                if ("t_iqn" in list(map_info.keys()) and
                        "h_iqn" in list(map_info.keys())):
                    for st_grp in list(st_grps_dict.keys()):
                        if "hba_infos" not in list(st_grps_dict[st_grp].keys()):
                            continue
                        # _print("DEBUG: st_grp:")
                        # print st_grps_dict[st_grp]
                        for hba_info in st_grps_dict[st_grp]["hba_infos"]:
                            if "h_iqn" in list(hba_info.keys()) and hba_info["h_iqn"] == map_info["h_iqn"]:
                                if st_grps_dict[st_grp]["name"] not in st_grps2map:
                                    # _print("DEBUG: lun_map")
                                    # print hba_info
                                    st_grps2map.append(st_grps_dict[st_grp]["name"])

                if not st_grps2map:
                    _print("FAIL: lun_map() - Do not know how to map using")
                    print(map_info)
                    return False

        lun_info_dict = self.lun_info(name)
        if not lun_info_dict:
            _print("FAIL: lun_unmap() - Could not query LUN %s" % name)
            return False
        if "map_infos" not in list(lun_info_dict.keys()):
            _print("INFO: lun_unmap() - LUN %s is not mapped to any storage group" % name)
            return True

        for my_stgrp in st_grps2map:
            # Check if lun is mapped to this group
            unmapped_st_grp = False
            for lun_map_info in lun_info_dict["map_infos"]:
                if my_stgrp != lun_map_info["st_group_name"]:
                    continue
                # This storage group have already been removed
                # for example, storage group is mapped to different ports
                if unmapped_st_grp:
                    continue
                # _print("DEBUG: lun_unmap() - unmap st_grp '%s' h_lun_id %s" % (my_stgrp, lun_map_info["h_lun_id"]))
                # print st_grps_dict[my_stgrp]
                _print("INFO: Unmapping LUN %s from '%s'" % (name, my_stgrp))
                cmd = "storagegroup -removehlu -gname '%s' -hlu %s -o" % (my_stgrp, lun_map_info["h_lun_id"])
                ret, output = self._run(cmd, return_output=True, verbose=False)
                if ret != 0:
                    _print("FAIL: \"%s\" command" % cmd)
                    print(output)
                    return False
                unmapped_st_grp = True

        # make sure all h_wwpns that we need to map are mapped
        luns_dict = self.query_all_lun_info(recheck=True)
        if "map_infos" not in list(luns_dict[name].keys()):
            # LUN is not mapped to any initiator
            return True
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
            if found_map:
                _print("FAIL: Tought it unmapped lun %s, but it did not" % name)
                print(map_info)
                return False

        return True

    # ####### Storage Groups ##############

    def query_all_storage_group_info(self, recheck=False):
        """
        Query all Storage Group info on array and store its information on a dict
        """

        # If we do not need to recheck and port info exist we return it
        # if self.storage_groups_dict and not recheck:
        #    return self.storage_groups_dict

        self.storage_groups_dict = {}

        # If not recheck, it will return exiting information
        getall_info = self._get_all(recheck=recheck)
        if not getall_info:
            return None

        ssport_list = self.query_all_spport_info()

        _storage_grp_section_regex = re.compile(r"All Storage Groups Information")
        _raid_section_regex = re.compile(r"All RAID Groups Information")
        # VNX accepts group name with spaces...
        _storage_grp_name_regex = re.compile(r"Storage Group Name:\s+(.*)$")
        _storage_grp_hba_sp_regex = re.compile(r"HBA/SP Pairs:")
        _storage_grp_hli_alu_regex = re.compile(r"HLU/ALU Pairs:")

        flag_all_storage_grp_info_begin = False
        flag_initiators_begin = False
        flag_map_begin = False
        st_grp_info = None

        for info in getall_info:
            # _print("DEBUG: query_all_storage_group_info() %s" % info)
            if _storage_grp_section_regex.match(info):
                flag_all_storage_grp_info_begin = True
                continue
            if _raid_section_regex.match(info):
                flag_all_storage_grp_info_begin = False
                continue

            if not flag_all_storage_grp_info_begin:
                continue

            # _print("DEBUG: Storage Grp info '%s'" % info)

            m = _storage_grp_name_regex.match(info)
            if m:
                self.storage_groups_dict[m.group(1)] = {}
                st_grp_info = self.storage_groups_dict[m.group(1)]
                st_grp_info["name"] = m.group(1)
                flag_initiators_begin = False
                # _print("DEBUG: Storage Grp name: %s" % m.group(1))
                continue

            if _storage_grp_hba_sp_regex.match(info):
                flag_initiators_begin = True
                continue

            if flag_initiators_begin:
                # _print("DEBUG: query_all_storage_group_info() - Initiator info '%s'" % info)
                m = re.match(r"\s+(\S+)\s+(SP \S+)\s+(\S+)$", info)
                # _print("DEBUG: query_all_storage_group_info() - process initiators %s" % info)
                if m:
                    if not st_grp_info:
                        _print(
                            "FAIL: query_all_storage_group_info() - Does not know to which storage group add HBA "
                            "info: %s" % info)
                        continue
                    hba_info = {}
                    wwn_info = _uid2wwnn_wwpn(m.group(1))
                    if wwn_info:
                        hba_info["h_wwpn"] = wwn_info["wwpn"]
                    elif libsan.host.iscsi.is_iqn(m.group(1)):
                        hba_info["h_iqn"] = m.group(1)
                    hba_info["sp_name"] = m.group(2)
                    hba_info["sp_port"] = m.group(3)
                    # Check wwpn of this port
                    if ssport_list:
                        for ssport in ssport_list:
                            if ("port_id" in list(ssport.keys()) and
                                    ssport["name"] == hba_info["sp_name"] and
                                    ssport["port_id"] == hba_info["sp_port"]):
                                wwn_info = _uid2wwnn_wwpn(ssport["uid"])
                                if wwn_info:
                                    hba_info["t_wwpn"] = ssport["wwpn"]
                                elif libsan.host.iscsi.is_iqn(ssport["uid"]):
                                    hba_info["t_iqn"] = ssport["uid"]
                    if "hba_infos" not in list(st_grp_info.keys()):
                        st_grp_info["hba_infos"] = []
                    # Check if entry already exist
                    found_info = False
                    for h_info in st_grp_info["hba_infos"]:
                        if (h_info["sp_name"] == hba_info["sp_name"] and
                                h_info["sp_port"] == hba_info["sp_port"] and
                                ("h_wwpn" in list(hba_info.keys()) and h_info["h_wwpn"] == hba_info["h_wwpn"] or
                                 "h_iqn" in list(hba_info.keys()) and h_info["h_iqn"] == hba_info["h_iqn"])):
                            found_info = True
                    if not found_info:
                        st_grp_info["hba_infos"].append(hba_info)

            if _storage_grp_hli_alu_regex.match(info):
                flag_map_begin = True
                flag_initiators_begin = False
                continue
            # If line has : this is part of some other information
            if re.search(":", info):
                flag_map_begin = False
                continue

            if flag_map_begin:
                # _print("DEBUG: query_all_storage_group_info() - Map info '%s'" % info)
                m = re.match(r"\s+(\d+)\s+(\d+)", info)
                if m:
                    if not st_grp_info:
                        _print(
                            "FAIL: query_all_storage_group_info() - Does not know to which storage group add "
                            "map: %s - %s" % (m.group(1), m.group(2)))
                        continue
                    map_info = dict()
                    map_info["h_lun_id"] = m.group(1)
                    map_info["t_lun_id"] = m.group(2)
                    if "map_infos" not in list(st_grp_info.keys()):
                        st_grp_info["map_infos"] = []
                    if map_info not in st_grp_info["map_infos"]:
                        st_grp_info["map_infos"].append(map_info)

        return self.storage_groups_dict

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

        ssport_list = self.query_all_spport_info()

        if not ssport_list:
            return None
        ctrler_name_regex = re.compile(r"ctrl_ip_(\S+)")
        ctrler_name = None
        if self.sa_conf_dict:
            # Search if there is a controller name defined for this controller
            for key in list(self.sa_conf_dict.keys()):
                if self.sa_conf_dict[key] == ctrler_ip:
                    m = ctrler_name_regex.match(key)
                    if m:
                        ctrler_name = m.group(1)

        if not ctrler_name:
            _print("FAIL: Could not find controller name configured for %s" % ctrler_ip)
            print(self.sa_conf_dict)
            return None

        for ssport in ssport_list:
            if (ssport["name"] == ctrler_name and
                    "wwpn" in list(ssport.keys())):
                if ssport["wwpn"] not in t_wwpns:
                    t_wwpns.append(ssport["wwpn"])

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

        cmd = "rebootSP -o"
        ret, output = self._run(cmd, ctrler=ctrler_ip, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: sa_ctrler_reboot() \"%s\" command" % cmd)
            print(output)
            return False

        # Let's check if controller is down
        timeout = 120
        interval = 10
        loop_count = timeout / interval
        while loop_count > 1:
            loop_count -= 1
            status = self.sa_ctrler_check(ctrler_ip)
            if not status or status == "offline":
                return True
            libsan.host.linux.sleep(interval)

        _print("FAIL: sa_ctrler_reboot() - Controller has not rebooted")
        print(output)
        return False

    def sa_ctrler_check(self, ctrler_ip):
        """
        Usage
        self.sa_ctrler_check(ctrler_name)
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

        status = "offline"
        cmd = "getagent"
        ret, output = self._run(cmd, ctrler=ctrler_ip, return_output=True, verbose=False)
        if ret != 0:
            return status

        if not output:
            return "offline"
        lines = output.split("\n")
        online_regex = re.compile(r"Agent Rev:")
        for line in lines:
            if online_regex.search(line):
                status = "online"
        return status
