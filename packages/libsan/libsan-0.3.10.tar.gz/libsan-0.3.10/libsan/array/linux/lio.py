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

"""lio.py: Module to handle commands on LIO Array."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import ast
import libsan.misc.size
import libsan.host.ssh
import libsan.misc.array


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


class lio:
    """
    Class to manage LIO array
    """
    host = None
    user = None
    passwd = None

    san_conf_path = None
    sa_conf_dict = None

    lio_dict = {}
    map_info = []

    def __init__(self, hostname, username, password, timeout=None, san_dev=None):
        # san_dev is here because we need it for DELL Equalogic array class
        self.san_dev_name = san_dev
        self.host = hostname
        self.user = username
        self.passwd = password
        self.timeout = timeout
        self.san_conf_path = None
        # _print("DEBUG: LIO version is %s" % self.get_version())

    def set_san_conf_path(self, san_conf_path):
        self.san_conf_path = san_conf_path
        return True

    def set_sa_conf(self, sa_conf_dict):
        self.sa_conf_dict = sa_conf_dict
        return True

    def get_sa_conf(self):
        return self.sa_conf_dict

    def _run(self, cmd, return_output=False, verbose=True):
        _print("INFO: Connecting to %s for command:" % self.host)
        print(cmd)
        session = libsan.host.ssh.connect(self.host, user=self.user, passwd=self.passwd)
        if not session:
            _print("FAIL: Could not connect to array (%s)" % self.host)
            if return_output:
                return 127, None
            return 127

        # If return_output is True, ret will be a tuple
        ret = libsan.host.ssh.run_cmd(session, cmd, return_output=return_output, verbose=verbose,
                                      invoke_shell=False, timeout=self.timeout)
        libsan.host.ssh.disconnect(session)
        return ret

    def get_version(self):
        """
        Return LIO version running on array
        """

        # Return the version of the first group we found
        ret, version = self._run("stlio version", return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: Getting LIO version")
            return None
        return version

    def query_all(self, recheck=False):
        if not recheck and self.lio_dict:
            return self.lio_dict

        cmd = "python -c \"import libsan.host.lio as lio;"
        cmd += "lio.lio_query(show_output=True)\""
        # cmd = "stlio get_all_luns_info"
        ret, lio_dict = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: query_all() - could not get all info")
            print(lio_dict)
            return None

        # Converting str to dict type
        try:
            lio_dict = ast.literal_eval(lio_dict)
        except Exception as e:
            print(e)
            _print("FAIL: Could not convert lio_query output to dict")
            print(lio_dict)
            return None

        self.lio_dict = lio_dict
        return lio_dict

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
        cap_dict["lun_remove"] = True
        cap_dict["lun_grow"] = False
        cap_dict["lun_shrink"] = False
        cap_dict["lun_trepass"] = False
        cap_dict["lun_thinp"] = False
        cap_dict["sa_ctrler_reboot"] = False
        return cap_dict

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
            if luns_dict[lun_name]["backstore_type"] == "fileio":
                return True
        # cmd = "stlio lun_info --bs_type fileio --lun_name %s" % lun_name
        # ret, output = self._run(cmd, return_output = True, verbose = False)
        # if ret != 0:
        #    return False
        return False

    @staticmethod
    def _lun_wwn2wwid(lun_info_dict):
        """
        From the LUN WWN is possible to get WWID
        """
        if not lun_info_dict:
            return None

        if "wwn" not in lun_info_dict:
            return None
        wwid = lun_info_dict["wwn"]
        wwid = wwid.replace("-", "")
        # Just the first 26 bytes are the wwid
        wwid = wwid[:25]
        wwid = "36001405" + wwid
        return wwid

    def lun_info(self, lun_name):
        """
        Query detailed information of specific LUN
        """
        if not lun_name:
            _print("FAIL: lun_info - requires lun_name")
            return None

        # used to match regex for each session information that we support
        # supported_lun_info = {"name"    : "^.*/(\S+) has size:",
        #                       "size_human": "^.* has size: (\S+)",
        #                       "wwn"    : "^.* has wwn: (\S+)"}

        # cmd = "stlio lun_info --bs_type fileio --lun_name %s" % lun_name
        # ret, output = self._run(cmd, return_output = True, verbose = True)
        # if ret != 0:
        #   _print("FAIL: lun_info() - lun does not exist")
        #   return None

        # if not output:
        #   return None

        # lines = output.split("\n")
        # lun_info_dict = None

        # line_id = 0
        # n_lines = len(lines)
        # while line_id < n_lines:
        #   line = lines[line_id].rstrip('\n')
        #   line_id += 1
        #   print "DEBUG parse: try %s - %s" % (line)
        #   if not line:
        #       continue

        #   for key in supported_lun_info.keys():
        #       m = re.match(supported_lun_info[key], line)
        #       if not m:
        #           continue
        #       if not lun_info_dict:
        #           lun_info_dict = {}
        #       print "Found %s: %s" % (key, m.group(1))
        #       lun_info_dict[key] = m.group(1)

        #   if "wwn" in lun_info_dict.keys():
        #       wwid = self._lun_wwn2wwid(lun_info_dict)
        #       if wwid:
        #           lun_info_dict["wwid"] = wwid
        luns_dict = self.query_all_lun_info()
        if not luns_dict:
            _print("FAIL: lun_info() - Could not query all lun info")
            return None
        if lun_name in list(luns_dict.keys()):
            if luns_dict[lun_name]["backstore_type"] == "fileio":
                return luns_dict[lun_name]

        _print("INFO lun_info(): Could not find LUN %s with type fileio" % lun_name)
        return None

    def query_all_luns(self):
        luns_info = self.query_all_lun_info()
        if not luns_info:
            return None

        return sorted(luns_info.keys())

    def query_all_lun_info(self, recheck=False):
        """
        Query all LUNs from LIO, the way we are storing the info will be a problem
        If we have LUN with same name on different backstores
        """
        lio_dict = self.query_all(recheck)
        if not lio_dict:
            _print("FAIL: query_all_lun_info() - could not get all lun info")
            print(lio_dict)
            return None
        all_lun_info_dict = {}

        if "backstores" not in list(lio_dict.keys()):
            return None

        for bs_type in list(lio_dict["backstores"].keys()):
            bs_luns = lio_dict["backstores"][bs_type]
            if not bs_luns:
                # This backstore has no LUN configured
                continue
            for lun in list(bs_luns.keys()):
                lun_info = dict()
                lun_info["lun_name"] = lun
                lun_info["backstore_type"] = bs_type
                lun_info["wwid"] = None

                if "wwid" in list(bs_luns[lun].keys()):
                    lun_info["wwid"] = bs_luns[lun]["wwid"]

                if "lun_size" in list(bs_luns[lun].keys()):
                    lun_info["size"] = libsan.misc.size.size_human_2_size_bytes(bs_luns[lun]["lun_size"])
                    lun_info["size_human"] = bs_luns[lun]["lun_size"]

                if "file_path" in list(bs_luns[lun].keys()):
                    lun_info["file_path"] = bs_luns[lun]["file_path"]

                if "mapping" in list(bs_luns[lun].keys()):
                    lun_info["map_infos"] = bs_luns[lun]["mapping"]

                all_lun_info_dict[lun] = lun_info

        # infos = output.split("\n")
        # lun_regex = re.compile("(\S+)/(\S+)")
        # map_regex = re.compile("(\S+) is mapped to (\S+)\(lun(\d+)\)/(\S+)\(lun(\d+)\)")
        # details_regex = re.compile("(\S+) has size: (\S+)")
        # for info in infos:
        #   if not info:
        #       #We might get empty line
        #       continue
        #   m = lun_regex.match(info)
        #   if not m:
        #       _print("FAIL: %s does not seem to contain a lun format" % info)
        #       continue
        #   bs_type = m.group(1)
        #   lun_name = m.group(2)
        #   if lun_name not in all_lun_info_dict.keys():
        #       all_lun_info_dict[lun_name] = {}
        #   lun_info = all_lun_info_dict[lun_name]
        #   lun_info["lun_name"] = lun_name
        #   lun_info["backstore_type"] = bs_type
        #   lun_info["wwid"] = None
        #   if "map_infos" not in lun_info.keys():
        #       lun_info["map_infos"] = []

        #   m = map_regex.match(info)
        #   if m:
        #       map_infos = {}
        #       map_infos["t_wwpns"] = [m.group(2)]
        #       map_infos["t_wwpn"] = m.group(2)
        #       map_infos["h_wwpns"] = [m.group(4)]
        #       map_infos["h_wwpn"] = m.group(4)
        #       map_infos["lun_id"] = m.group(5)
        #       map_infos["t_lun_id"] = m.group(3)
        #       map_infos["lun_name"] = lun_name
        #       map_infos["backstore_type"] = bs_type
        #       lun_info["map_infos"].append(map_infos)

        #   m = details_regex.match(info)
        #   if m:
        #       lun_info["size"] = size_human_2_size_bytes(m.group(2))
        #       lun_info["size_human"] = m.group(2)
        return all_lun_info_dict

    def lun_create(self, name, size):
        """
        Create new LUN on array if LUN does not exist
        """
        _print("INFO: Creating fileio LUN %s with size %s" % (name, size))
        if not name or not size:
            _print("FAIL: usage lun_create(name, size)")
            return None

        if self._lun_exist(name):
            _print("INFO: LUN %s already exist" % name)
            return None

        size_bytes = libsan.misc.size.size_human_2_size_bytes(size)
        if not size_bytes:
            _print("FAIL: lun_create() - Could not convert %s to bytes" % size)
            return None

        # cmd = "stlio lun_create --bs_type fileio --lun_name %s --lun_size %s " % (name, size_bytes)
        cmd = "python -c \"import libsan.host.lio as lio; " \
              "lio.lio_create_backstore(\\\"%s\\\",\\\"%s\\\", \\\"%s\\\")\"" % ("fileio", name, size_bytes)
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            print(output)
            return None
        # Need to update our volumes
        vol_dict = self.query_all_lun_info(recheck=True)
        if name not in list(vol_dict.keys()):
            self.lun_remove(name)
            _print("FAIL: thought LUN %s was created, but it was not" % name)
            print(vol_dict)
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
        cmd = "python -c \"import libsan.host.lio as lio;"
        cmd += " lio.lio_delete_backstore(\\\"%s\\\",\\\"%s\\\")\"" % ("fileio", name)
        # cmd = "stlio lun_delete --bs_type fileio --lun_name %s" % (name)
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            print(output)
            return False
        # Need to update our volumes
        vol_dict = self.query_all_lun_info(recheck=True)
        if name in list(vol_dict.keys()):
            _print("FAIL: thought LUN %s was deleted, but it was not" % name)
            return False

        # When deleting backstores, mapping information is there, even if there
        # is no lun mapped to it. Should clean up this
        cmd = "python -c \"import libsan.host.lio as lio;"
        cmd += " lio.lio_clean_up_targets()\""
        # cmd = "stlio lun_delete --bs_type fileio --lun_name %s" % (name)
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: \"%s\" command" % cmd)
            print(output)
            return False
        return True

    def lun_map(self, name):
        """
        Map a LUN to an h_wwpn
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

        for map_info in self.map_info:
            if ("t_wwpn" not in list(map_info.keys()) or
                    "h_wwpn" not in list(map_info.keys())):
                _print("FAIL: lun_map() - Do not know how to map using")
                print(map_info)
                return False

            t_wwpn = map_info["t_wwpn"]
            h_wwpn = map_info["h_wwpn"]
            free_lun_id = self._next_free_h_lun_id(t_wwpn, h_wwpn)

            _print("INFO: Mapping LUN %s to %s/%s (host ID %d)" % (name, t_wwpn, h_wwpn, free_lun_id))

            cmd = "python -c \"import libsan.host.lio as lio;"
            cmd += (" lio.lio_fc_lun_map(\\\"%s\\\",\\\"%s\\\",\\\"%s\\\",\\\"%s\\\",\\\"%s\\\")\""
                    % (name, "fileio", t_wwpn, h_wwpn, free_lun_id))

            # cmd = ("stlio lun_map --bs_type fileio --lun_name %s --t_wwn %s --h_wwn %s --h_lun_id %s" %
            # (name, t_wwpn, h_wwpn, free_lun_id))
            ret, output = self._run(cmd, return_output=True, verbose=False)
            if ret != 0:
                _print("FAIL: \"%s\" command" % cmd)
                print(output)
                return False

        self.query_all_lun_info(recheck=True)
        return True

    # TODO
    @staticmethod
    def lun_unmap(name, iqn):

        # Unmap a LUN to an IQN

        _print("DEBUG: lun_unmap() - TODO!!! %s %s" % (name, iqn))
        return False

    def _next_free_h_lun_id(self, t_wwpn, h_wwpn):
        """
        Check LIO target and see what is the Host LUN ID that we could use
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
