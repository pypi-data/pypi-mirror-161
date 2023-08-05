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


"""eqlogic.py: Module to handle commands on EqualLogic Array."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import sys
import libsan.misc.size
import libsan.host.ssh
import libsan.host.conf
import libsan.array.dell.eqlparse_show


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


def _size_human_2_size_eqlogic(size):
    """
    Convert size to size Equallogic expects. Eg 2GiB to 2G
    """
    size_human = libsan.misc.size.size_bytes_2_size_human(size)
    if not libsan.misc.size.size_human_check(size_human):
        _print("FAIL: %s is not on human size format")
        return None
    size_eql = re.sub("iB", "", size_human)
    return size_eql


def _size_eqlogic_2_size_human(size_eql):
    """
    Convert size Equallogic to Human. Eg 2GB to 2GiB
    """
    if not size_eql:
        return None
    m = re.match(r"(\S+[M|G|T])B?$", size_eql)
    if not m:
        _print("FAIL: _size_eqlogic_2_size_human() - Invalid Eqlogic size format: %s" % size_eql)
        return None
    size_human = "%siB" % m.group(1)
    return size_human


def parse_ret(data):
    # remove command on 1st line and last line with 'grub>'
    return data.split("\r\n")[1:-1]


class eqlogic:
    """
    Class to manage Equallogic array
    """
    host = None
    user = None
    passwd = None

    san_conf_path = None
    san_dev_name = None

    volume_dict = None
    member_dict = None
    luns = []

    map_info = []

    def __init__(self, hostname, username, password, timeout=None, san_dev=None):
        self.host = hostname
        self.user = username
        self.passwd = password
        self.timeout = timeout
        if self.timeout:
            self.timeout = float(self.timeout)
        self.san_conf_path = None
        # san_dev is the nake on san_top for this device
        self.san_dev_name = san_dev
        self.sa_conf_dict = None

    def set_san_conf_path(self, san_conf_path):
        self.san_conf_path = san_conf_path
        return True

    def set_sa_conf(self, sa_conf_dict):
        self.sa_conf_dict = sa_conf_dict
        return True

    def get_sa_conf(self):
        return self.sa_conf_dict

    def _run(self, cmd, return_output=False, verbose=True):
        # Create the session and log in
        session = libsan.host.ssh.connect(self.host, user=self.user, passwd=self.passwd)
        if not session:
            _print("FAIL: Could not connect to switch (%s)" % self.host)
            if return_output:
                return 127, None
            return 127

        try:
            ret = libsan.host.ssh.run_cmd(session, cmd=cmd, return_output=return_output, verbose=verbose,
                                          timeout=self.timeout, cr="\n\r", invoke_shell=True, expect="> ")
        except Exception as e:
            print(e)
            print("Unexpected error:", sys.exc_info()[0])
            # _print("FAIL: Timeout executing command on address: %s" % (self.host))
            print(cmd)
            if return_output:
                return 1, "Exception on ssh"
            return 1
        libsan.host.ssh.disconnect(session)

        if return_output:
            ret_code, output = ret
            output = "\n".join(parse_ret(output))
            return ret_code, output

        return ret

    def query_members(self, recheck=False):
        """
        Query all LUNs on array and store its information on a dict
        """

        # If we do not need to recheck and port info exist we return it
        if self.member_dict and not recheck:
            return self.member_dict

        cmd = "member show"
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            if output:
                print(output)
            return None
        self.member_dict = libsan.array.dell.eqlparse_show.parse_show(output)

        return self.member_dict

    def get_version(self):
        """
        Return FW version of the array
        """
        member_dict = self.query_members()
        if not member_dict:
            return None

        # Return the version of the first group we found
        for key in member_dict.keys():
            if "version" in member_dict[key].keys():
                return member_dict[key]["version"]

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
        cap_dict["lun_grow"] = True
        cap_dict["lun_shrink"] = True
        cap_dict["lun_trepass"] = False
        cap_dict["lun_thinp"] = True
        cap_dict["sa_ctrler_reboot"] = False
        return cap_dict

    def query_all_luns(self):
        """
        Query all LUNs on array and store its information on a dict
        """

        # If we do not need to recheck and port info exist we return it
        # if self.luns and not recheck:
        #    return self.luns

        cmd = "volume show -volume"
        _print("INFO: Running command %s on %s" % (cmd, self.host))
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            print(output)
            return None
        _print("INFO: finished querying all volumes")
        output_dict = libsan.array.dell.eqlparse_show.parse_show(output)
        if not output_dict:
            return None

        self.luns = []
        for lun_name in output_dict.keys():
            self.luns.append(lun_name)

        return sorted(self.luns)

    def query_all_lun_info(self):
        """
        Query all LUNs on array and store its information on a dict
        """

        # If we do not need to recheck and port info exist we return it
        # if self.volume_dict and not recheck:
        #    return self.volume_dict

        luns = self.query_all_luns()
        if not luns:
            return None
        _print("INFO: Going to query info for each LUN, this might take a while...")
        for lun_name in luns:
            if not self.volume_dict:
                self.volume_dict = {}
            self.volume_dict[lun_name] = self.lun_info(lun_name)
            # lun_info = self.volume_dict[lun_name]
            # lun_info["name"] = lun_name
        _print("INFO: finished querying all volumes info")
        return self.volume_dict

    def _lun_exist(self, lun_name):
        """
        Test if LUN exist
        If LUN does not exist return error
        """
        if not lun_name:
            _print("FAIL: _lun_exist - requires lun_name")
            return False

        # cmd = "volume show %s" % lun_name
        # ret, output = self._run(cmd, return_output = True, verbose = False)
        # if ret != 0:
        #    return False
        # print output
        # return True
        if self.lun_info(lun_name):
            return True
        return False

    @staticmethod
    def _lun_wwid(lun_info_dict):
        """
        From the LUN iSCSI name it is possible to convert it to wwid
        """
        if not lun_info_dict:
            return None
        # wwid = None
        lun_name = lun_info_dict["name"]
        # Last \S+ usually is the lun name, but could be different if volume was renamed...
        # Has to be non greedy match
        eql_wwid_iqn_regex = re.compile(r"^iqn\..*equallogic:(\S+?)-(\S+?)-(\S+?)-(\S+?)-\S+$")
        m = eql_wwid_iqn_regex.match(lun_info_dict["iscsi_name"])
        if m:
            match1 = m.group(1)
            match2 = m.group(2)
            match3 = m.group(3)
            match4 = m.group(4)
            if len(match4) % 2 != 0:
                match4 += match3[0]
                # as we added the character to the other match, we remove from this one
                match3 = match3[1:]
            if len(match3) % 2 != 0:
                match3 += match2[0]
                # as we added the character to the other match, we remove from this one
                match2 = match2[1:]
            if len(match2) % 2 != 0:
                match2 += match1[0]
                # as we added the character to the other match, we remove from this one
                match1 = match1[1:]
            if len(match1) % 2 != 0:
                match1 += "Z"
                print(lun_info_dict["iscsi_name"])
                _print("FATAL: _lun_wwid() could not parse wwid")
            match1 = "".join(reversed([match1[i:i + 2] for i in range(0, len(match1), 2)]))
            match2 = "".join(reversed([match2[i:i + 2] for i in range(0, len(match2), 2)]))
            match3 = "".join(reversed([match3[i:i + 2] for i in range(0, len(match3), 2)]))
            match4 = "".join(reversed([match4[i:i + 2] for i in range(0, len(match4), 2)]))
            wwid = "3" + match1 + match2 + match3 + match4
        else:
            print(lun_info_dict)
            _print("FAIL: _lun_wwid() - Could not get wwid of %s" % lun_name)
            return None
            # _print("DEBUG: lun_wwid: wwid %s" % wwid)
        return wwid

    def lun_info(self, lun_name):
        """
        Query detailed information of specific LUN
        """
        # used to match regex for each session information that we support
        # supported_lun_info = {"name"    : "^Name: (\S+)",
        #                    "size_human": "^Size: (\S+)",
        #                    "iscsi_name": "^iSCSI Name: (\S+)",
        #                    "status"    : "^Status: (\S+)"}
        supported_lun_info = ["name", "size", "iscsi_name", "status"]

        if not lun_name:
            _print("FAIL: lun_info - requires lun_name")
            return None

        cmd = "volume show %s" % lun_name
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: lun_info() - lun does not exist")
            return None

        if not output:
            return None

        output_dict = libsan.array.dell.eqlparse_show.parse_show(output)
        if not output_dict:
            return None

        if "_volume_information_" not in output_dict:
            return None
        vol_info_dict = output_dict["_volume_information_"]
        lun_info_dict = {}
        for key in vol_info_dict.keys():
            if key in supported_lun_info:
                lun_info_dict[key] = vol_info_dict[key]

        lun_info_dict["size_human"] = _size_eqlogic_2_size_human(lun_info_dict["size"])
        lun_info_dict["size_eqlogic"] = lun_info_dict["size"]
        # Replace eqlogic size for size in bytes
        lun_info_dict["size"] = libsan.misc.size.size_human_2_size_bytes(lun_info_dict["size_human"])

        if "_access_records_" in output_dict:
            map_infos = output_dict["_access_records_"]
            map_info = None
            for key in map_infos.keys():
                map_info = dict()
                map_info["t_iqn"] = lun_info_dict["iscsi_name"]
                map_info["h_iqn"] = map_infos[key]["initiator"]
                map_info["id"] = map_infos[key]["id"]
                if "map_infos" not in lun_info_dict:
                    lun_info_dict["map_infos"] = []
            lun_info_dict["map_infos"].append(map_info)
        # lines = output.split("\n")
        # lun_info_dict = None

        # line_id = 0
        # n_lines = len(lines)
        # while line_id < n_lines:
        # line = lines[line_id].rstrip('\n')
        # line_id += 1
        # #print "DEBUG parse: try %s - %s" % (line)
        # if not line:
        # continue

        # for key in supported_lun_info.keys():
        # m = re.match(supported_lun_info[key], line)
        # if not m:
        # continue
        # if not lun_info_dict:
        # lun_info_dict = {}
        # #print "Found %s: %s" % (key, m.group(1))
        # lun_info_dict[key] = m.group(1)
        # #If next line does not look like a parameter, it is probably because
        # #Equallogic wrapped the previous line, for example on iSCSI alias scenario
        # if (line_id) < n_lines:
        # next_line = lines[line_id].rstrip('\n')
        # if not re.search(": ", next_line):
        # lun_info_dict[key] += next_line

        if "iscsi_name" in lun_info_dict:
            wwid = self._lun_wwid(lun_info_dict)
            if wwid:
                lun_info_dict["wwid"] = wwid

        return lun_info_dict

    def lun_create(self, name, size, permission="read-write", status="online", sec_size="512"):
        """
        Create new LUN on array if LUN does not exist
        """
        if not name or not size:
            _print("FAIL: usage lun_create(name, size)")
            return None

        size_eql = _size_human_2_size_eqlogic(size)
        if not size_eql:
            _print("FAIL: Could not get human size %s on Equallogic format" % size)
            return None

        if self._lun_exist(name):
            _print("FAIL: lun_create() - LUN %s already exist" % name)
            return None

        cmd = "volume create %s %s %s %s sector-size %s" % (name, size_eql, permission, status, sec_size)
        ret, output = self._run(cmd, return_output=True, verbose=True)
        if ret != 0:
            _print("FAIL: lun_create() - \"%s\" command" % cmd)
            print(output)
            return None
        # Need to update our volumes
        # luns = self.query_all_luns(recheck=True)
        # if name not in luns:
        if not self._lun_exist(name):
            _print("FAIL: lun_create() - thought LUN %s was created, but it was not" % name)
            return None

        # As new target is created, we need to update san conf file
        # _print("DEBUG: lun_create san_conf_file: %s" % self.san_conf_path)
        info_dict = self.lun_info(name)
        if not self.san_conf_path:
            _print("WARN: lun_create() - Could not find path for san_conf file")
            return name

        if not self.san_dev_name:
            _print("WARN: lun_create() - it seems %s is not configured on %s" % (self.host, self.san_conf_path))
        else:
            libsan.host.conf.config_add_entry(
                self.san_dev_name, "iscsi_iqn_%s" % name, info_dict["iscsi_name"], self.san_conf_path)
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

        vol_dict = self.lun_info(name)
        if not vol_dict:
            _print("FAIL: Could not get info for %s" % name)
            return False

        if vol_dict["status"] != "offline":
            _print("INFO: Setting LUN %s offline before deleting it..." % name)
            if not self._lun_change_status(name, "offline"):
                _print("FAIL: Could not set %s offline")
                return False

        cmd = "volume delete %s" % name
        ret, output = self._run(cmd, return_output=True, verbose=True)
        if ret != 0:
            _print("FAIL: lun_remove() - \"%s\" command" % cmd)
            print(output)
            return False
        # Need to update our volumes
        # luns = self.query_all_luns(recheck=True)
        # if name in luns:
        if self._lun_exist(name):
            _print("FAIL: lun_remove() - thought LUN %s was deleted, but it was not" % name)
            return False

        if not self.san_conf_path:
            _print("WARN: lun_remove() - Could not find path for san_conf file")
            return True

        if not self.san_dev_name:
            _print("WARN: lun_remove() - it seems %s is not configured on %s" % (self.host, self.san_conf_path))
        else:
            # As lun is remove so is the target, we need to update san conf file
            libsan.host.conf.config_remove_entry(self.san_dev_name, "iscsi_iqn_%s" % name, self.san_conf_path)
        return True

    def lun_map(self, name):
        """
        Map a LUN to an IQN
        """
        if not name:
            _print("FAIL: lun_map() - requires lun_name as parameter")
            return False

        if not self.map_info:
            _print("FAIL: lun_map() - There is no mapping info to use")
            return False

        # vol_dict = self.query_all_lun_info()
        # if name not in vol_dict.keys():
        if not self._lun_exist(name):
            _print("FAIL: lun_map - LUN %s do NOT exist" % name)
            return False

        iqns_2_map = []
        for map_info in self.map_info:
            if "h_iqn" not in map_info.keys():
                _print("FAIL: lun_map() - Does not know how to map using")
                print(map_info)
                continue
            if map_info["h_iqn"] not in iqns_2_map:
                iqns_2_map.append(map_info["h_iqn"])

        map_infos = self.lun_query_access(name)
        for iqn in iqns_2_map:
            # Check if this IQN is already mapped to the LUN
            if map_infos:
                for map_info in map_infos:
                    if "h_iqn" not in map_info.keys():
                        continue
                    if iqn == map_info["h_iqn"]:
                        _print("WARN: LUN %s is already mapped to %s" % (name, iqn))
                        return True

            cmds = ["volume select %s" % name, "access create initiator %s" % iqn]
            ret, output = self._run(cmds, return_output=True, verbose=True)
            if ret != 0:
                _print("FAIL: \"%s\" command" % ", ".join(cmds))
                print(output)
                return False
        # Update map details
        # self.volume_dict[name] = self.lun_info(name)
        return True

    def lun_unmap(self, name):
        """
        Unmap a LUN to an IQN
        """
        if not name:
            _print("FAIL: usage lun_unmap(name)")
            return False

        # vol_dict = self.query_all_lun_info()
        # if name not in vol_dict.keys():
        if not self._lun_exist(name):
            _print("FAIL: lun_unmap - LUN %s do NOT exist" % name)
            return False

        if not self.map_info:
            _print("FAIL: lun_map() - There is no mapping info to use")
            return False

        iqns_2_unmap = []
        for map_info in self.map_info:
            if "h_iqn" not in map_info.keys():
                _print("FAIL: lun_map() - Does not know how to map using")
                print(map_info)
                continue
            if map_info["h_iqn"] not in iqns_2_unmap:
                iqns_2_unmap.append(map_info["h_iqn"])

        # access_dict = self.lun_query_access(name)
        map_infos = self.lun_query_access(name)
        if not map_infos:
            _print("FAIL: Could not find any map information for this LUN")
            return False
        # To unmap we need to know the ID of the IQN
        access_id = None
        error = 0
        for iqn in iqns_2_unmap:
            # Check if this IQN is mapped to the LUN
            for map_info in map_infos:
                if "h_iqn" not in map_info.keys():
                    continue
                if iqn == map_info["h_iqn"]:
                    access_id = map_info["id"]

                if not access_id:
                    _print("WARN: LUN %s is not mapped to %s" % (name, iqn))
                    return True

                cmds = ["volume select %s" % name, "access delete %s" % access_id]
                ret, output = self._run(cmds, return_output=True, verbose=True)
                if ret != 0:
                    _print("FAIL: \"%s\" command" % ", ".join(cmds))
                    print(output)
                    error += 1
        if error:
            return False
        return True

    def lun_query_access(self, name):
        """
        Query access information for a LUN
        """
        if not name:
            _print("FAIL: usage lun_query_access(name)")
            return None

        if not self._lun_exist(name):
            _print("FAIL: lun_query_access() - LUN %s do NOT exist" % name)
            return None

        # cmds = ["volume select %s" % (name), "access show"]
        # ret, output = self._run(cmds, return_output = True, verbose = False)
        # if ret != 0:
        #    _print("FAIL: \"%s\" command" % ", ".join(cmds))
        #    print output
        #    return None
        #
        # access_dict = eqlparse_show.parse_show(output)
        # if "_access_records_" not in access_dict:
        #    return None
        # return access_dict["_access_records_"]
        info_dict = self.lun_info(name)
        if not info_dict:
            _print("FAIL: lun_query_access() - Could not query info for %s" % name)
            return None
        if "map_infos" in info_dict:
            return info_dict["map_infos"]
        return None

    def _lun_change_status(self, lun_name, status):
        """
        Have to run volume select lun_name and then set the status
        """
        if not lun_name or not status:
            _print("FAIL: _lun_change_status() - requires lun_name and status parameter")
            return False
        # Before I thought I need to run volume select first and then set status,
        # but it seems it can be done in a single command line
        cmds = ["volume select %s %s" % (lun_name, status)]
        ret, output = self._run(cmds, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % ", ".join(cmds))
            print(output)
            return False
        # Need to update info of our volume
        # self.volume_dict[name] = self.lun_info(name)
        return True
