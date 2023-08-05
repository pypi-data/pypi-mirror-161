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

"""lio.py: Module to manipulate LIO target (using targetcli)."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import libsan.host.fc
import libsan.host.linux
import re  # regex
from libsan.host.cmdline import run

regex_tgtcli_wwpn = "naa.\\S+"


def _print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    print(string)
    return


def _tgt_wwn_2_wwn(wwn):
    """On RHEL-6 targetcli stores WWN on WWN format,
    but on RHEL-7 it is something like: naa.200090e2baa397ca
    The arguments are:
    \tNone
    Returns:
    \\tString: WWN as: 20:00:90:e2:ba:a3:97:ca
    """
    # Converting Targetcli wwpn format to common format
    if libsan.host.linux.dist_name() == "RHEL" and libsan.host.linux.dist_ver() < 7:
        return wwn

    wwn_regex = r"naa\."
    wwn = re.sub(wwn_regex, "", wwn)
    # append ":" after every 2nd character
    wwn = re.sub(r"(\S{2})", r'\1:', wwn)
    # remove trail :
    wwn = re.sub(":$", "", wwn)
    return wwn


def _wwn_2_tgt_wwn(wwn):
    """On RHEL-6 targetcli stores WWN on WWN format,
    but on RHEL-7 it is something like: naa.200090e2baa397ca
    The arguments are:
    \tWWN:      20:00:90:e2:ba:a3:97:ca
    Returns:
    \\tString: target WWN foramt as: naa.200090e2baa397ca
    """
    # Converting Targetcli wwpn format to common format
    if libsan.host.linux.dist_name() == "RHEL" and libsan.host.linux.dist_ver() < 7:
        return wwn

    # remove all ':'
    wwn = re.sub(":", "", wwn)
    # append "naa." after every 2nd character
    wwn = "naa." + wwn
    return wwn


def lio_query(show_output=False):
    """Query all information from targetcli using targetcli ls
    The arguments are:
    \tNone
    Returns:
    \tdict: Return a dictionary with targetcli information
    """
    cmd = "targetcli ls"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not run targetcli")
        return None
    lio_data = output.split("\n")

    lio_field_regex = re.compile(r"o-\s(.*?)\s.*\[(.*)\]")
    # supported types for LIO
    lio_supported_types = ("backstores", "iscsi", "loopback", "tcm_fc")
    lio_supported_backstores = ("block", "fileio", "pscsi", "ramdisk", "user:qcow", "user:rbd", "user:zbc")

    lio_dict = {}
    data_type = None

    bs_type_dict = {}

    iscsi_dict = {}
    iscsi_init_iqn = None
    iscsi_tgt_iqn = None
    current_tpg = None
    iscsi_acls_dict = {}
    iscsi_luns = []
    iscsi_portals = []
    iscsi_processing_acls = False
    iscsi_processing_luns = False
    iscsi_processing_portals = False

    tcm_fc_dict = {}
    tcm_fc_wwn = None
    tcm_fc_init_wwn = None
    tcm_fc_acls_dict = {}
    tcm_fc_luns = []
    tcm_fc_processing_acls = False
    tcm_fc_processing_luns = False

    for data in lio_data:
        m = lio_field_regex.search(data)
        if not m:
            # Just ignore entry we can't parse
            # _print("FAIL: (%s) does not match LIO field format" % data)
            continue
        entry = m.group(1)
        entry_details = m.group(2)

        if entry == "/":
            # Skip root
            continue

        # print "INFO: LIO field %s" % entry
        if entry in lio_supported_types:
            data_type = entry
            # bs_type_dict = {}
            lio_dict[data_type] = {}
            continue
        if not data_type:
            _print("FATAL: %s is does not belong to any supported data type" % entry)
            continue
        # print "INFO: %s is subitem of %s" % (entry, data_type)
        # ################# PROCESSING BACKSTORES data type ####################
        if data_type == "backstores":
            if entry in lio_supported_backstores:
                # print "INFO: Processing backstores %s subtiems" % entry
                bs_type = entry
                bs_type_dict[bs_type] = {}
                lio_dict[data_type] = bs_type_dict
                continue
            if entry == "alua" or entry == "default_tg_pt_gp":
                continue
            details_regex = re.compile(r"(.*)\s+\((\S+)\)\s+(\S+)\s+(\S+)")
            details_dict = {}
            m = details_regex.search(entry_details)
            if m:
                details_dict["file_path"] = m.group(1)
                details_dict["lun_size"] = m.group(2)
            details_dict.update(lio_get_backstore_lun_details(bs_type, entry))
            if "wwn" in list(details_dict.keys()):
                details_dict["wwid"] = _lun_wwn2wwid(details_dict["wwn"])
            # print "BRUNO DEBUG backstore %s (%s)" % (entry, entry_details)
            bs_type_dict[bs_type][entry] = details_dict
            lio_dict[data_type] = bs_type_dict

        # ################# PROCESSING iSCSI data type ####################
        if data_type == "iscsi":
            iqn_regex = re.compile(r"iqn\..*")
            if iqn_regex.match(entry) and not iscsi_processing_acls:
                # print "INFO: Processing tcm_fc %s subtiems" % entry
                iscsi_tgt_iqn = entry
                # The target wwn is a dict key
                iscsi_dict[iscsi_tgt_iqn] = {}
                lio_dict[data_type] = iscsi_dict
                continue
            tpg_regex = re.compile(r"(tpg\d+)")
            m = tpg_regex.match(entry)
            if m:
                # print "INFO: Processing tcm_fc %s subtiems" % entry
                current_tpg = m.group(1)
                # The target wwn is a dict key
                iscsi_dict[iscsi_tgt_iqn][current_tpg] = {}
                iscsi_acls_dict = {}
                iscsi_luns = []
                iscsi_portals = []
                lio_dict[data_type] = iscsi_dict
                continue

            if entry == "acls":
                iscsi_dict[iscsi_tgt_iqn][current_tpg]["acls"] = {}
                iscsi_processing_acls = True
                iscsi_processing_luns = False
                iscsi_processing_portals = False
            if entry == "luns":
                iscsi_dict[iscsi_tgt_iqn][current_tpg]["luns"] = {}
                iscsi_processing_acls = False
                iscsi_processing_luns = True
                iscsi_processing_portals = False
                continue
            if entry == "portals":
                iscsi_dict[iscsi_tgt_iqn][current_tpg]["portals"] = {}
                iscsi_processing_acls = False
                iscsi_processing_luns = False
                iscsi_processing_portals = True
                continue
            # ################# PROCESSING ACLS ####################
            # If we are processing ACLs entry
            if iscsi_processing_acls:
                # print "BRUNO ISCSI ACL init (%s)" % entry
                if iqn_regex.match(entry):
                    iscsi_init_iqn = entry
                    iscsi_acls_dict[iscsi_init_iqn] = []
                    iscsi_dict[iscsi_tgt_iqn][current_tpg]["acls"] = iscsi_acls_dict
                    lio_dict[data_type] = iscsi_dict
                    continue
                map_regex = re.compile(r"mapped_(lun.*)$")
                # Check if it is lun mapping information
                m = map_regex.match(entry)
                if m:
                    # print "INFO: found mapped lun: %s" % m.group(1)
                    iscsi_acls_dict[iscsi_init_iqn].append(m.group(1))
                    iscsi_dict[iscsi_tgt_iqn][current_tpg]["acls"] = iscsi_acls_dict
                lio_dict[data_type] = iscsi_dict

            # ################# PROCESSING LUNs ####################
            # If we are processing LUNs entry
            if iscsi_processing_luns:
                iscsi_luns.append(entry)
                iscsi_dict[iscsi_tgt_iqn][current_tpg]["luns"] = iscsi_luns
                lio_dict[data_type] = iscsi_dict
                continue
            # ################# PROCESSING Portlas ####################
            # If we are processing Portals entry
            if iscsi_processing_portals:
                iscsi_portals.append(entry)
                iscsi_dict[iscsi_tgt_iqn][current_tpg]["portals"] = iscsi_portals
                lio_dict[data_type] = iscsi_dict
                continue

        # ################# PROCESSING TCM_FC data type ####################
        if data_type == "tcm_fc":
            # if tcm_fc_processing_luns is true, it is because we reached the end
            # of host wwn and now we are probably processing next host wwn
            # so do not test it on the if below
            tmp_entry = _tgt_wwn_2_wwn(entry)
            if libsan.host.fc.is_wwn(tmp_entry) and not tcm_fc_processing_acls:
                # print "INFO: Processing tcm_fc %s subtiems" % tmp_entry
                tcm_fc_wwn = tmp_entry
                # The target wwn is a dict key
                tcm_fc_dict[tcm_fc_wwn] = {}
                tcm_fc_processing_acls = False
                tcm_fc_processing_luns = False
                lio_dict[data_type] = tcm_fc_dict
                continue

            if entry == "acls":
                tcm_fc_acls_dict = {}
                tcm_fc_dict[tcm_fc_wwn]["acls"] = {}
                tcm_fc_processing_acls = True
                tcm_fc_processing_luns = False
                continue
            if entry == "luns":
                tcm_fc_luns = {}
                tcm_fc_dict[tcm_fc_wwn]["luns"] = {}
                tcm_fc_processing_luns = True
                tcm_fc_processing_acls = False
                continue
            # ################# PROCESSING ACLS ####################
            # If we are processing ACLs entry
            if tcm_fc_processing_acls:

                # It can be initiator, but be using tag instead of wwn
                # TODO: lio_is_fc_tag causes the whole query command to be slow
                # need to find a better way to do it
                tmp_entry = _tgt_wwn_2_wwn(entry)
                if libsan.host.fc.is_wwn(tmp_entry) or lio_is_fc_tag(tcm_fc_wwn, entry):
                    tcm_fc_init_wwn = tmp_entry
                    tcm_fc_acls_dict[tcm_fc_init_wwn] = {}
                    tcm_fc_dict[tcm_fc_wwn]["acls"] = tcm_fc_acls_dict
                    continue
                map_regex = re.compile(r"mapped_(lun.*)$")
                # Check if it is lun mapping information
                m = map_regex.match(entry)
                if m:
                    t_lun_id_regex = re.compile(r"(lun\d+)\s(\S+)/(\S+)")
                    t = t_lun_id_regex.match(entry_details)
                    if t:
                        # print "INFO: found mapped lun: %s" % m.group(1)
                        # print "INFO: entry_details %s" % entry_details
                        tcm_fc_acls_dict[tcm_fc_init_wwn][t.group(1)] = m.group(1)
                        tcm_fc_dict[tcm_fc_wwn]["acls"] = tcm_fc_acls_dict
                        # Update mapping info on backstore session
                        bs_type = t.group(2)
                        lun_name = t.group(3)
                        # print "INFO: tcm_fc acls: bs_type %s lun_name %s is mapped to %s/%s" %
                        # (bs_type, lun_name, tcm_fc_wwn, tcm_fc_init_wwn)
                        details_dict = lio_dict["backstores"][bs_type][lun_name]
                        mapping_dict = {"t_wwpn": tcm_fc_wwn, "h_wwpn": tcm_fc_init_wwn, "t_lun_id": t.group(1),
                                        "h_lun_id": m.group(1)}
                        if "mapping" not in list(details_dict.keys()):
                            details_dict["mapping"] = []
                        details_dict["mapping"].append(mapping_dict)

            # ################# PROCESSING LUNS that are added to target wwn ####################
            # If we are processing LUNs entry
            if tcm_fc_processing_luns:
                t_lun_info_regex = re.compile(r"(\S+)/(\S+)\s.*")
                t = t_lun_info_regex.match(entry_details)
                # print "INFO: entry_details tcm_fc luns %s" % entry_details
                if t:
                    # print "INFO: found mapped lun: %s" % m.group(1)
                    # print "INFO: entry_details %s" % entry_details
                    tcm_fc_luns[entry] = {}
                    tcm_fc_luns[entry]["bs_type"] = t.group(1)
                    tcm_fc_luns[entry]["lun_name"] = t.group(2)
                tcm_fc_dict[tcm_fc_wwn]["luns"] = tcm_fc_luns

            lio_dict[data_type] = tcm_fc_dict

    if show_output:
        print(lio_dict)
    return lio_dict


##################################################
# ############### BACKSTORES ######################
##################################################
def lio_create_backstore(bs_type=None, lun_name=None, lun_size=None,
                         device_name=None):
    """Create new backstore device
    The arguments are:
    \tNone
    Returns:
    \tTrue: Device was created
    \tFalse: There was some problem
    """
    created = False
    if bs_type == "block":
        created = _lio_create_backstore_block(lun_name, device_name)

    if bs_type == "fileio":
        created = _lio_create_backstore_fileio(lun_name, lun_size=lun_size)

    if bs_type == "pscsi":
        created = _lio_create_backstore_pscsi(lun_name, device_name)

    if not created:
        _print("FAIL: Could not create lun using (%s) on lio_create_backstore" % bs_type)
        return False

    if lun_name not in list(lio_get_backstores(bs_type).keys()):
        _print("FAIL: It seems %s was created, but it was not" % lun_name)
        return False

    return True


def lio_get_backstores(bs_type=None, lio_dict=None):
    """Return a dict with all backstores. If a backstore type
    is provided return a list of backstore of this type
    The arguments are:
    \tbs_type (Optional): Backstore type
    \tlio_dict (Optional): For optmization, if we already have the lio query no need to do it again
    Returns:
    \tList
    \t\tDict: if there are devices and backstore type was provided
    \tDict
    \t\tDict: All backstore devices
    """
    if not lio_dict:
        lio_dict = lio_query()

    if "backstores" not in list(lio_dict.keys()):
        _print("FAIL: there is not backstore defined on targetcli")
        print(lio_dict)
        return None

    if not bs_type:
        return lio_dict["backstores"]

    if bs_type not in list(lio_dict["backstores"].keys()):
        return None

    return lio_dict["backstores"][bs_type]


def lio_get_backstore_details(bs_type, lun_name, lio_dict=None):
    """Get the size of specifc Backstore device
    Returns:
    \tDic:      Detailed information about this device
    \tNone:     If something went wrong
    """

    bs_dict = lio_get_backstores(bs_type, lio_dict=lio_dict)
    if not bs_dict:
        return None

    if lun_name not in list(bs_dict.keys()):
        _print("FAIL: %s is not defined on %s" % (lun_name, bs_type))
        lio_dict = lio_query()
        print(lio_dict)
        return None

    return bs_dict[lun_name]


def lio_get_backstore_lun_details(bs_type, lun_name):
    """Get the detailed information about the lun
    """
    if not bs_type or not lun_name:
        _print("FAIL: lio_get_backstore_lun_details() - requires bs_type and lun_name")
        return None

    cmd = "targetcli /backstores/%s/%s info" % (bs_type, lun_name)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not get %s details for %s" % (bs_type, lun_name))
        return None

    details = output.split("\n")
    supported_details = dict()
    supported_details["dev"] = r"^dev: (\S+)"
    supported_details["name"] = r"^name: (\S+)"
    supported_details["size_bytes"] = r"^size: (\S+)"
    supported_details["write_back"] = r"^write_back: (\S+)"
    supported_details["wwn"] = r"^wwn: (\S+)"

    lun_details = {}
    for info in details:
        for sup_detail in supported_details:
            m = re.match(supported_details[sup_detail], info)
            if m:
                lun_details[sup_detail] = m.group(1)

    return lun_details


def _lun_wwn2wwid(wwn):
    """
    From the LUN WWN is possible to get WWID
    """
    wwid = wwn
    wwid = wwid.replace("-", "")
    # Just the first 26 bytes are the wwid
    wwid = wwid[:25]
    wwid = "36001405" + wwid
    return wwid


def lio_delete_backstore(bs_type=None, lun_name=None):
    """Delete backstore device
    The arguments are:
    \tBackstore type
    \tLUN name
    Returns:
    \tTrue: Device was delete
    \tFalse: There was some problem
    """
    deleted = False
    if bs_type == "block":
        deleted = _lio_delete_backstore_block(lun_name)

    if bs_type == "fileio":
        deleted = _lio_delete_backstore_fileio(lun_name)

    if bs_type == "pscsi":
        deleted = _lio_delete_backstore_pscsi(lun_name)

    if not deleted:
        _print("FAIL: Could not delete lun using (%s) on lio_create_backstore" % bs_type)
        return False

    if lun_name in list(lio_get_backstores(bs_type).keys()):
        _print("FAIL: It seems %s was deleted, but it was not" % lun_name)
        return False

    return True


# ## BLOCK ###
def _lio_create_backstore_block(lun_name, device):
    if not lun_name:
        print("FAIL: _lio_create_backstore_block needs lun_name parameter")
        return False
    if not device:
        print("FAIL: _lio_create_backstore_block needs device parameter")
        return False

    cmd = "targetcli /backstores/block create %s %s" % (lun_name, device)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not create block %s" % lun_name)
        return False
    return True


def _lio_delete_backstore_block(lun_name):
    cmd = "targetcli /backstores/block delete %s" % lun_name
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete block %s" % lun_name)
        return False

    return True


# ## FILEIO ###
def _lio_create_backstore_fileio(lun_name, file_name=None, lun_size=None):
    if not lun_name:
        _print("_lio_create_backstore_fileio() - requires lun_name parameter")
        return False

    if not file_name:
        # Set default backend file name
        file_name = "%s.img" % lun_name

    # disable spare, to force targetcli to allocate the whole file to avoid problem
    # of running out of disk space and not have enough space to store data
    cmd = "targetcli /backstores/fileio create %s %s sparse=false" % (lun_name, file_name)
    if lun_size:
        cmd = cmd + " %s" % lun_size

    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not create fileio %s" % lun_name)
        return False
    return True


def _lio_delete_backstore_fileio(lun_name):
    file_name = _lio_get_backstore_fileio_file(lun_name)

    cmd = "targetcli /backstores/fileio delete %s" % lun_name
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete fileio %s" % lun_name)
        return False

    if file_name:
        cmd = "rm -f %s" % file_name
        retcode = run(cmd, return_output=False, verbose=True)
        if retcode != 0:
            _print("WARN: could not delete file %s" % file_name)

    return True


def _lio_get_backstore_fileio_file(lun_name):
    """Get the file used by an specific LUN
    """
    cmd = "targetcli /backstores/fileio/%s ls" % lun_name
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not get fileio file %s" % lun_name)
        return None

    path_regex = re.compile(r"\[(.*)\s\(")
    m = path_regex.search(output)
    if m:
        return m.group(1)
    return None


# ## PSCSI ###
def _lio_create_backstore_pscsi(lun_name, device, lun_size=None):
    cmd = "targetcli /backstores/pscsi create %s %s" % (lun_name, device)
    if lun_size:
        cmd = cmd + " %sM" % lun_size

    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not create pscsi %s" % lun_name)
        return False
    return True


def _lio_delete_backstore_pscsi(lun_name):
    cmd = "targetcli /backstores/pscsi delete %s" % lun_name
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete pscsi %s" % lun_name)
        return False

    return True


##################################################
# ################# iSCSI ########################
##################################################
def lio_support_iscsi_target():
    """Check if host supports iSCSI target
    The arguments are:
    \tNone
    Returns:
    \tTrue: Host supports iscsi
    \tFalse: Host does not support iscsi
    """
    lio_dict = lio_query()

    if "iscsi" not in list(lio_dict.keys()):
        # Host does not support iSCSI target
        return False
    return True


# ## iSCSI target ###
def lio_iscsi_create_target(iqn):
    """Add the iqn to iSCSI target
    The arguments are:
    \tiqn:     Target IQN
    Returns:
    \tTrue: If target is added
    \tFalse: If some problem happened
    """
    if not lio_support_iscsi_target():
        _print("FAIL: server does not support iSCSI target")
        return False

    cmd = "targetcli /iscsi/ create %s" % iqn
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not create iSCSI target %s" % iqn)
        return False

    if iqn not in lio_iscsi_get_target():
        _print("FAIL: It seems to have added iSCSI target, but it did not")
        lio_dict = lio_query()
        print(lio_dict["iscsi"])
        return False
    # targetcli by default enable only IPv$ connection
    # we want also IPv6
    if not lio_iscsi_delete_target_portal(iqn, "tpg1", "0.0.0.0"):
        _print("FAIL: could not remove default iSCSI target portal")
        lio_dict = lio_query()
        print(lio_dict["iscsi"])

    if not lio_iscsi_create_target_portal(iqn, "tpg1", "::0"):
        _print("FAIL: could not create IPv6 iSCSI target portal")
        lio_dict = lio_query()
        print(lio_dict["iscsi"])
    return True


def lio_iscsi_get_target():
    """Return a list of all iSCSI targets configured
    The arguments are:
    \tNone
    Returns:
    \tlist: Return a list of IQNs that are configured
    """
    lio_dict = lio_query()

    if not lio_support_iscsi_target():
        # Host does not support iSCSI target
        return None

    return list(lio_dict["iscsi"].keys())


def lio_iscsi_target_set_parameter(tgt_iqn, tpg, group, attr_name, attr_value):
    """Set a parameter to an iSCSI target
    if tgt_iqn is not set, set it globally
    The arguments are:
    \ttgt_iqn       HOST IQN
    \ttpg           Target Portal Group
    \tgroup         eg: attribute, parameter, discovery_auth...
    \tattr_name     Attribute name
    \tattr_value    Attribute value
    Returns:
    \tTrue: If target is attribute is set
    \tFalse: If some problem happened
    """
    cmd = "targetcli /iscsi set %s %s=%s" % (group, attr_name, attr_value)
    if tgt_iqn:
        cmd = "targetcli /iscsi/%s/%s/ set %s %s=%s" % (tgt_iqn, tpg, group, attr_name, attr_value)

    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: Could not set iSCSI target attribute %s" % attr_name)
        return False
    return True


# ## iSCSI ACLS ###
def lio_iscsi_create_acl(tgt_iqn, tpg, init_iqn):
    """Add a initiator IQN to target IQN
    The arguments are:
    \ttgt_iqn:     Host IQN
    \ttpg:         Target Portal Group
    \tinit_iqn:    Initiator IQN
    Returns:
    \tTrue: If init IQN is created
    \tFalse: If some problem happened
    """
    cmd = "targetcli /iscsi/%s/%s/acls create %s add_mapped_luns=false" % (tgt_iqn, tpg, init_iqn)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not add iSCSI initiator %s" % init_iqn)
        return False
    return True


def lio_iscsi_delete_acl(tgt_iqn, tpg, init_iqn):
    """Remove a initiator IQN from target IQN
    The arguments are:
    \ttgt_iqn:     Host IQN
    \ttpg:         Target Portal Group
    \tinit_iqn:    Initiator IQN
    Returns:
    \tTrue: If init iqn is removed
    \tFalse: If some problem happened
    """
    cmd = "targetcli /iscsi/%s/%s/acls delete %s" % (tgt_iqn, tpg, init_iqn)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete iSCSI initiator %s" % init_iqn)
        return False

    return True


# ## iSCSI LUNs ###
def lio_iscsi_add_lun(tgt_iqn, tpg, bs_type, lun_name):
    """Add a LUN to target IQN
    The arguments are:
    \ttgt_iqn:      Host IQN
    \ttpg:          Target Portal Group
    \tbs_type:      Backstore type
    \tlun_name:     Lun Name
    Returns:
    \tTrue: If LUN is added
    \tFalse: If some problem happened
    """
    cmd = "targetcli /iscsi/%s/%s/luns create /backstores/%s/%s add_mapped_luns=false" % (
        tgt_iqn, tpg, bs_type, lun_name)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not add lun to iSCSI target %s" % tgt_iqn)
        return False

    return True


def lio_iscsi_remove_lun(tgt_iqn, tpg, lun_id):
    """Remove a LUN target IQN
    The arguments are:
    \ttgt_iqn:     Target IQN
    \ttpg:         Target Portal Group
    \tlun_id:      Lun ID
    Returns:
    \tTrue: If LUN is removed
    \tFalse: If some problem happened
    """
    cmd = "targetcli /iscsi/%s/%s/luns delete %s" % (tgt_iqn, tpg, lun_id)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete LUN from iSCSI target %s" % tgt_iqn)
        return False

    return True


def lio_iscsi_get_luns(tgt_iqn, tpg):
    """Return a list with all LUNs added to an iSCSI target.
    The arguments are:
    \tNone
    Returns:
    \tList: list of luns
    \tNone if something went wrong
    """
    if tgt_iqn not in lio_iscsi_get_target():
        print("FAIL: %s is not defined on targetcli" % tgt_iqn)
        return None

    lio_dict = lio_query()
    if "luns" not in list(lio_dict["iscsi"][tgt_iqn].keys()):
        print("INFO: target %s does not have any LUN\n")
        return None

    return lio_dict["tcm_fc"][tgt_iqn][tpg]["luns"]


# ## iSCSI Portals ###
def lio_iscsi_create_target_portal(tgt_iqn, tpg, portal_ip, portal_port="3260"):
    """Remove a Portal target IQN
    The arguments are:
    \ttgt_iqn:     Target IQN
    \ttpg:         Target Portal Group
    \tportal_ip:   IP of host allowed to connect. (0.0.0.0) any IPv4 address
    \tportal_port  Port to listen for connection, default 3260
    Returns:
    \tTrue: If Portal is created
    \tFalse: If some problem happened
    """
    lio_dict = lio_query()
    if "portals" not in list(lio_dict["iscsi"][tgt_iqn][tpg].keys()):
        print("INFO: target %s does not have support Portal" % tgt_iqn)
        return False

    portal = portal_ip + ":" + portal_port
    if portal in lio_dict["iscsi"][tgt_iqn][tpg]["portals"]:
        print("INFO: portal %s does already exist on target %s" % (portal, tgt_iqn))
        return True

    cmd = "targetcli /iscsi/%s/%s/portals create %s %s" % (tgt_iqn, tpg, portal_ip, portal_port)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete Portal from iSCSI target %s" % tgt_iqn)
        return False

    return True


def lio_iscsi_delete_target_portal(tgt_iqn, tpg, portal_ip, portal_port="3260"):
    """Remove a Portal target IQN
    The arguments are:
    \ttgt_iqn:     Target IQN
    \ttpg:         Target Portal Group
    \tportal_ip:   IP of host allowed to connect. (0.0.0.0) any IPv4 address
    \tportal_port  Port to listen for connection, default 3260
    Returns:
    \tTrue: If Portal is removed
    \tFalse: If some problem happened
    """
    lio_dict = lio_query()
    if "portals" not in list(lio_dict["iscsi"][tgt_iqn][tpg].keys()):
        print("INFO: target %s does not have support Portal" % tgt_iqn)
        return False

    portal = portal_ip + ":" + portal_port
    if portal not in lio_dict["iscsi"][tgt_iqn][tpg]["portals"]:
        print("INFO: portal %s does not exist on target %s" % (portal, tgt_iqn))
        return True

    cmd = "targetcli /iscsi/%s/%s/portals delete %s %s" % (tgt_iqn, tpg, portal_ip, portal_port)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete Portal from iSCSI target %s" % tgt_iqn)
        return False
    return True


# ## iSCSI LUNs mapping ###
def lio_iscsi_map_lun(tgt_iqn, tpg, init_iqn, init_lun_id, bs_type, lun_name):
    """Map a LUN to target IQN / Initiator IQN
    The arguments are:
    \ttgt_iqn:      Target IQN
    \ttpg:          Target Portal group
    \tinit_iqn:     Host IQN
    Returns:
    \tTrue: If LUN is mapped
    \tFalse: If some problem happened
    """

    lun_path = "/backstores/%s/%s" % (bs_type, lun_name)
    cmd = "targetcli /iscsi/%s/%s/acls/%s create %s %s" % (tgt_iqn, tpg, init_iqn, init_lun_id, lun_path)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not map lun to iSCSI target %s/%s" % (tgt_iqn, init_iqn))
        return False

    if not lio_iscsi_get_lun_map(tgt_iqn, init_iqn, tpg, init_lun_id):
        _print("FAIL: It seems to have mapped lun %s, but it did not" % init_lun_id)
        return False

    return True


def lio_iscsi_unmap_lun(tgt_iqn, init_iqn, tpg, init_lun_id):
    """Un map LUN from tgt_wwn/init_wwn
    The arguments are:
    \ttgt_iqn:      Target IQN
    \tinit_iqn:     Host IQN
    \ttpg:          Target Portal group
    \tinit_lun_id   LUN ID for the initiator
    Returns:
    \tTrue: If LUN is unmapped
    \tFalse: If some problem happened
    """
    cmd = "targetcli /iscsi/%s/%s/acls/%s delete %s" % (tgt_iqn, init_iqn, tpg, init_lun_id)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not unmap LUN from target %s/%s" % (tgt_iqn, init_iqn))
        return False

    if not lio_iscsi_get_lun_map(tgt_iqn, init_iqn, tpg, init_lun_id):
        _print("FAIL: It seems to have unmapped lun %s, but it did not" % init_lun_id)
        return False
    return True


def lio_iscsi_get_lun_map(tgt_iqn, init_iqn, tpg, tgt_lun_id):
    """Check if a LUN is mapped to target WWN / Initiator port
    The arguments are:
    \ttgt_iqn:      Target IQN
    \tinit_iqn:     Host IQN
    \ttpg:          Target Portal group no.
    \tinit_lun_id   LUN ID for the initiator
    Returns:
    \tTrue: If LUN is mapped
    \tFalse: If some problem happened
    """
    cmd = "targetcli /iscsi/%s/tpg%s/acls/%s ls | grep %s" % (tgt_iqn, tpg, init_iqn, tgt_lun_id)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not get mapping for lun %s on iSCSI target %s/%s" % (tgt_lun_id, tgt_iqn, init_iqn))
        return False

    if output == "":
        return False
    return True


def lio_add_iscsi_target(tgt_iqn=None, init_iqn=None, bs_type="fileio",
                         lun_name=None, lun_size="1G", device_name=None,
                         tgt_cnt=1, lun_cnt=1):
    """Create new iSCSI target, create LUNs and do LUN mapping
    The arguments are:
    \ttgt_iqn:          Target IQN, if not specified LIO will create a target IQN
    \tinit_iqn:         Initiator IQN, set LUN map to specific IQN, otherwise any IQN will access the LUN
    \tbs_type:          Backstores storage type, default: 'fileio'
    \tlun_name:         LUN name when creating the target, if not set default lun name will be used
    \tlun_size:         LUN size when using  fileio, default: 1G
    \tdevice_name:      Device name when using block device, for example LV name
    \ttgt_cnt:          Number of targets to create, default: 1
    \tlun_cnt:          Number of LUNs to create, default: 1
    Returns:
    \tTrue: if iSCSI target is created
    \tFalse: If some problem happened
    """

    new_tgt_iqns = []
    iqn_preffix = "iqn.2009-10.com.redhat:storage-"
    # need to create new iSCSI targets, first get the existing targets
    if not tgt_iqn:
        existing_targets = lio_iscsi_get_target()
        iqn_suffix = 0
        # Create new target_iqn names
        while len(new_tgt_iqns) < tgt_cnt:
            tmp_iqn = "%s%d" % (iqn_preffix, iqn_suffix)
            if tmp_iqn not in existing_targets:
                new_tgt_iqns.append(tmp_iqn)
            iqn_suffix += 1
    else:
        new_tgt_iqns = [tgt_iqn]

    for target_iqn in new_tgt_iqns:
        if not lio_iscsi_create_target(target_iqn):
            _print("FAIL: Could not create iSCSI target '%s'" % target_iqn)
            return False

        m = re.match(r"%s(\d+)" % iqn_preffix, target_iqn)
        if m:
            tgt_name = "tgt%d" % int(m.group(1))
        else:
            tgt_name = target_iqn.split(":")[1]

        for lun_num in range(1, lun_cnt + 1):
            tgt_lun_name = "%s_lun%d" % (tgt_name, lun_num)
            # If lun name was passed as argument, try to use it
            if lun_name:
                tgt_lun_name = lun_name

            if not lio_create_backstore(bs_type=bs_type, lun_name=tgt_lun_name, lun_size=lun_size,
                                        device_name=device_name):
                _print("FAIL: Could not create backstore for iSCSI target")
                return False

            tpg = "tpg1"

            if not lio_iscsi_add_lun(target_iqn, tpg, bs_type, tgt_lun_name):
                _print("FAIL: Could not add LUN to iSCSI target")
                return False

            # This is a global setting
            if not lio_iscsi_target_set_parameter(None, None, "discovery_auth", "enable", "0"):
                _print("FAIL: Could not set Attr to iSCSI target")
                return False

            if not lio_iscsi_target_set_parameter(target_iqn, tpg, "attribute", "authentication", "0"):
                _print("FAIL: Could not set Attr to iSCSI target")
                return False

            if not lio_iscsi_target_set_parameter(target_iqn, tpg, "attribute", "generate_node_acls", "1"):
                _print("FAIL: Could not set Attr to iSCSI target")
                return False

            if not lio_iscsi_target_set_parameter(target_iqn, tpg, "attribute", "demo_mode_write_protect", "0"):
                _print("FAIL: Could not set Attr to iSCSI target")
                return False

            lun_id = "0"
            if init_iqn:
                if not lio_iscsi_create_acl(target_iqn, tpg, init_iqn):
                    _print("FAIL: Could not create iSCSI initiator ACL")
                    return False
                if not lio_iscsi_map_lun(target_iqn, tpg, init_iqn, lun_id, bs_type, tgt_lun_name):
                    _print("FAIL: Could not map LUN to iSCSI initiator")
                    return False

    return True


def lio_setup_iscsi_target(tgt_iqn=None, init_iqn=None, bs_type="fileio",
                           lun_name=None, lun_size="1G", device_name=None,
                           tgt_cnt=1, lun_cnt=1):
    """Create a basic iSCSI target
    The arguments are:
    \ttgt_iqn:          Target IQN, if not specified LIO will create a target IQN
    \tinit_iqn:         Initiator IQN, set LUN map to specific IQN, otherwise any IQN will access the LUN
    \tbs_type:          Backstores storage type, default: 'fileio'
    \tlun_name:         LUN name when creating the target, if not set default lun name will be used
    \tlun_size:         LUN size when using  fileio, default: 1G
    \tdevice_name:      Device name when using block device, for example LV name
    \ttgt_cnt:          Number of targets to create, default: 1
    \tlun_cnt:          Number of LUNs to create, default: 1
    Returns:
    \tTrue: if iSCSI target is created
    \tFalse: If some problem happened
    """
    print("INFO: Creating basic iSCSI target...")
    lio_install()
    lio_restart()
    lio_clearconfig()

    ver = lio_version()
    print("INFO: Running targetcli version %s" % ver)

    if not lio_support_iscsi_target():
        _print("FAIL: Server does not support iSCSI target")
        return False

    lio_add_iscsi_target(tgt_iqn, init_iqn, bs_type, lun_name, lun_size, device_name, tgt_cnt, lun_cnt)

    return True


##################################################
# ################# TCM_FC ########################
##################################################
def lio_support_fc_target():
    """Check if host supports FC target
    The arguments are:
    \tNone
    Returns:
    \tTrue: Host supports tcm_fc
    \tFalse: Host does not support tcm_fc
    """
    lio_dict = lio_query()

    if "tcm_fc" not in list(lio_dict.keys()):
        # Host does not support FC target
        return False

    return True


# ## FC target ###
def lio_create_fc_target(wwn):
    """Add the wwn to tcm_fc target
    The arguments are:
    \twwn:     Host wwn
    Returns:
    \tTrue: If target is added
    \tFalse: If some problem happened
    """
    if not wwn:
        _print("FAIL: lio_create_fc_target() - requires wwn parameter")
        return False

    cmd = "targetcli /tcm_fc/ create %s" % wwn
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: lio_create_fc_target() - Could not create FC target %s" % wwn)
        return False

    if wwn not in lio_get_fc_target():
        lio_dict = lio_query()
        run("targetcli ls", return_output=False, verbose=True)
        _print("FAIL: lio_create_fc_target() - It seems to have added FC target, but it did not")
        print(lio_dict["tcm_fc"])
        print(lio_dict)

        return False

    return True


def lio_delete_fc_target(wwn):
    """Delete the wwn to tcm_fc target
    The arguments are:
    \twwn:     Host wwn
    Returns:
    \tTrue: If target is added
    \tFalse: If some problem happened
    """
    if not wwn:
        _print("FAIL: lio_delete_fc_target() - requires wwn parameter")
        return False

    cmd = "targetcli /tcm_fc/ delete %s" % wwn
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: lio_delete_fc_target() - Could not delete FC target %s" % wwn)
        return False

    if wwn in lio_get_fc_target():
        lio_dict = lio_query()
        run("targetcli ls", return_output=False, verbose=True)
        _print("FAIL: lio_delete_fc_target() - It seems to have deleted FC target, but it did not")
        print(lio_dict["tcm_fc"])
        print(lio_dict)

        return False

    return True


def lio_get_fc_target(lio_dict=None):
    """Return a list of all FC targets configured
    The arguments are:
    \tNone
    Returns:
    \tlist: Return a list of wwns that are configured
    """
    if not lio_dict:
        lio_dict = lio_query()

    if not lio_support_fc_target():
        # Host does not support FC target
        return None

    return list(lio_dict["tcm_fc"].keys())


# ## FC ACLS ###
def lio_create_fc_target_acl(tgt_wwn, init_wwn, lio_dict=None):
    """Add a initiator WWN to target WWN port
    The arguments are:
    \ttgt_wwn:     Host WWN
    \tinit_wwn:    Initiator WWN
    Returns:
    \tTrue: If init wwn is created
    \tFalse: If some problem happened
    """
    tgt_acls = lio_get_fc_target_acl(tgt_wwn, lio_dict=lio_dict)
    if tgt_acls and (init_wwn in tgt_acls):
        print("INFO: %s is already added to target %s" % (init_wwn, tgt_wwn))
        return True

    cmd = "targetcli /tcm_fc/%s/acls create %s add_mapped_luns=false" % (_wwn_2_tgt_wwn(tgt_wwn), init_wwn)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not add FC initiator %s" % init_wwn)
        return False

    return True


def lio_delete_fc_target_acl(tgt_wwn, init_wwn):
    """Remove a initiator WWN from target WWN port
    The arguments are:
    \ttgt_wwn:     Host WWN
    \tinit_wwn:    Initiator WWN
    Returns:
    \tTrue: If init wwn is removed
    \tFalse: If some problem happened
    """
    cmd = "targetcli /tcm_fc/%s/acls delete %s" % (_wwn_2_tgt_wwn(tgt_wwn), init_wwn)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete FC initiator %s" % init_wwn)
        return False

    return True


def lio_get_fc_target_acl(tgt_wwn, lio_dict=None):
    """Get all acls from an specifc target
    The arguments are:
    \ttgt_wwn:     Host WWN
    Returns:
    \tList: List of initiators
    \tNone: If some problem happened
    """
    if not tgt_wwn:
        _print("FAIL: lio_get_fc_target_acl() - requires tgt_wwpn as argument")
        return None
    if not lio_dict:
        lio_dict = lio_query()
    if not lio_dict["tcm_fc"][tgt_wwn]:
        _print("FAIL: %s does not exist" % tgt_wwn)
        print(lio_dict)
        return None

    if "acls" not in list(lio_dict["tcm_fc"][tgt_wwn].keys()):
        # _print("FAIL: %s does not have acls" % tgt_wwn)
        # print lio_dict
        return None

    return list(lio_dict["tcm_fc"][tgt_wwn]["acls"].keys())


# ## FC LUNs ###
def lio_create_fc_target_lun(tgt_wwn, bs_type, lun_name):
    """Add a LUN to target WWN port
    The arguments are:
    \ttgt_wwn:      Host WWN
    \tbs_type:      Backstore type
    \tlun_name:     Lun Name
    Returns:
    \tTrue: If LUN is created
    \tFalse: If some problem happened
    """
    cmd = "targetcli /tcm_fc/%s/luns create /backstores/%s/%s add_mapped_luns=false" % (
        _wwn_2_tgt_wwn(tgt_wwn), bs_type, lun_name)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not add lun to FC target %s" % tgt_wwn)
        return False

    return True


def lio_delete_fc_target_lun(tgt_wwn, lun_id):
    """Remove a initiator WWN from target WWN port
    The arguments are:
    \ttgt_wwn:     Target WWN
    \tlun_id:      Lun ID
    Returns:
    \tTrue: If LUN is removed
    \tFalse: If some problem happened
    """
    cmd = "targetcli /tcm_fc/%s/luns delete %s" % (_wwn_2_tgt_wwn(tgt_wwn), lun_id)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete LUN from target %s" % tgt_wwn)
        return False

    return True


def lio_get_fc_target_luns(tgt_wwn, lio_dict=None):
    """Return a dict with all backstores. If a backstore type
    is provided return a list of backstore of this type
    The arguments are:
    \tNone
    Returns:
    \tList: list of luns
    \tNone if something went wrong
    """
    if not lio_dict:
        lio_dict = lio_query()

    if tgt_wwn not in lio_get_fc_target(lio_dict=lio_dict):
        print("FAIL: %s is not defined on targetcli" % tgt_wwn)
        return None

    if "luns" not in list(lio_dict["tcm_fc"][tgt_wwn].keys()):
        print("INFO: target %s does not have any LUN\n" % tgt_wwn)
        return None

    return lio_dict["tcm_fc"][tgt_wwn]["luns"]


def lio_get_fc_target_lun_id(tgt_wwn, bs_type, lun_name, lio_dict=None):
    """Return the target LUN ID.
    The arguments are:
    \ttgt_wwn:      Target WWN
    \tbs_type:      Backstore Type
    \tlun_name:     LUN name
    Returns:
    \tString: LUN ID. eg: lun0
    \tNone if something went wrong
    """
    if not lio_dict:
        lio_dict = lio_query()

    t_luns_dict = lio_get_fc_target_luns(tgt_wwn, lio_dict)
    if not t_luns_dict:
        return None

    for lun_id in list(t_luns_dict.keys()):
        if (t_luns_dict[lun_id]["bs_type"] == bs_type and
                t_luns_dict[lun_id]["lun_name"] == lun_name):
            return lun_id
    return None


#    cmd = "targetcli /tcm_fc/%s/luns ls | grep %s/%s | awk '{print$2}'" % (_wwn_2_tgt_wwn(tgt_wwn), bs_type, lun_name)
#    retcode, output = run(cmd, return_output=True, verbose=False)
#    if (retcode != 0):
#        _print ("FAIL: Could not get lun %s for FC target %s" % (lun_name, tgt_wwn))
#        return None
#
#    if output == "":
#        return None
#    return output

# ## FC LUNs mapping ###
def lio_fc_lun_map(lun_name, bs_type, tgt_wwn, init_wwn, init_lun_id):
    """
    Map a LUN to a t_wwpn and h_wwpn
    """
    if (not lun_name or not bs_type or not tgt_wwn or not init_wwn or
            not init_lun_id):
        _print("FAIL: lio_fc_lun_map() - requires lun_name, bs_type, tgt_wwn, init_wwn, init_lun_id parameters")
        return False

    _print("INFO: Mapping LUN %s/%s to %s/%s..." % (bs_type, lun_name, tgt_wwn, init_wwn))
    lio_dict = lio_query()
    if tgt_wwn not in lio_get_fc_target(lio_dict=lio_dict):
        lio_create_fc_target(tgt_wwn)
        # update lio_dict with new fc target
        lio_dict = lio_query()

    if not lio_get_fc_target_lun_id(tgt_wwn, bs_type, lun_name, lio_dict=lio_dict):
        lio_create_fc_target_lun(tgt_wwn, bs_type, lun_name)
        # update lio_dict with new fc target
        lio_dict = lio_query()

    # Do not pass lio_dict as parameter as we need to query it again to get updatd info
    lun_id = lio_get_fc_target_lun_id(tgt_wwn, bs_type, lun_name, lio_dict=lio_dict)
    if not lun_id:
        _print("FAIL: lio_fc_lun_map() - Could not find lun %s/%s on target %s" %
               (bs_type, lun_name, tgt_wwn))
        lio_show()
        return False

    if not lio_create_fc_target_acl(tgt_wwn, init_wwn, lio_dict=lio_dict):
        _print("FAIL: Could not create ACL to host %s" % init_wwn)
        lio_show()
        return False

    if not lio_create_fc_target_map_lun(tgt_wwn, init_wwn, init_lun_id, lun_id, lio_dict=lio_dict):
        _print("FAIL: Could not map LUN %s to host %s" % (lun_name, init_wwn))
        return False

    _print("INFO: LUN %s mapped successfully" % lun_name)
    return True


def lio_create_fc_target_map_lun(tgt_wwn, init_wwn, init_lun_id, tgt_lun_id, lio_dict=None):
    """Map a LUN to target WWN / Initiator port
    The arguments are:
    \ttgt_wwn:      Target WWN
    \tinit_wwn:     Host WWN
    \tinit_lun_id   LUN ID for the initiator
    \ttgt_lun_id:   LUN ID on target
    Returns:
    \tTrue: If LUN is mapped
    \tFalse: If some problem happened
    """

    print("BRUNO lio_create_fc_target_map_lun")
    # print lio_get_fc_target_map_lun(tgt_wwn, init_wwn, tgt_lun_id)

    if lio_get_fc_target_map_lun(tgt_wwn, init_wwn, tgt_lun_id, lio_dict=lio_dict):
        _print("INFO: lun %s is already mapped to FC target %s/%s" % (tgt_lun_id, tgt_wwn, init_wwn))
        return True

    cmd = "targetcli /tcm_fc/%s/acls/%s create %s %s" % (
        _wwn_2_tgt_wwn(tgt_wwn), _wwn_2_tgt_wwn(init_wwn), init_lun_id, tgt_lun_id)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not map lun to FC target %s/%s" % (tgt_wwn, init_wwn))
        return False

    if not lio_get_fc_target_map_lun(tgt_wwn, init_wwn, tgt_lun_id):
        _print("FAIL: It seems to have mapped lun %s, but it did not" % tgt_lun_id)
        return False

    return True


def lio_fc_target_get_mapped_luns(tgt_wwn, init_wwn, lio_dict=None):
    """Get LUN mapping from tgt_wwn/init_wwn
    The arguments are:
    \ttgt_wwn:      Target WWN
    \tinit_wwn:     Host WWN
    Returns:
    \tDict:         Dictionary with tgt_lunid : init_lun_id
    \tNone:         No mapping was found
    """

    if not lio_dict:
        lio_dict = lio_query()

    if init_wwn not in lio_get_fc_target_acl(tgt_wwn, lio_dict=lio_dict):
        return None

    mapped_luns_dict = lio_dict["tcm_fc"][tgt_wwn]["acls"][init_wwn]
    if not mapped_luns_dict:
        return None
    return mapped_luns_dict


def lio_fc_target_unmap_lun(tgt_wwn, init_wwn, init_lun_id):
    """Un map LUN from tgt_wwn/init_wwn
    The arguments are:
    \ttgt_wwn:      Target WWN
    \tinit_wwn:     Host WWN
    \tinit_lun_id   LUN ID for the initiator
    Returns:
    \tTrue: If LUN is unmapped
    \tFalse: If some problem happened
    """
    cmd = "targetcli /tcm_fc/%s/acls/%s delete %s" % (_wwn_2_tgt_wwn(tgt_wwn), _wwn_2_tgt_wwn(init_wwn), init_lun_id)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not unmap LUN from target %s/%s" % (tgt_wwn, init_wwn))
        return False

    if lio_get_fc_target_map_lun(tgt_wwn, init_wwn, init_lun_id):
        _print("FAIL: It seems to have unmapped lun %s, but it did not" % init_lun_id)
        return False
    return True


def lio_get_fc_target_map_lun(tgt_wwn, init_wwn, tgt_lun_id, lio_dict=None):
    """Get initator LUN Id if a LUN is mapped to target WWN / Initiator port
    The arguments are:
    \ttgt_wwn:      Target WWN
    \tinit_wwn:     Host WWN
    \ttgt_lun_id:   LUN ID on target
    Returns:
    \tinit_lun_id: If LUN is mapped
    \tNone: If LUN is not mapped
    """

    # If lio dict is given as parameter we do not need to query lio output again
    if not lio_dict:
        lio_dict = lio_query()

    if init_wwn not in lio_get_fc_target_acl(tgt_wwn, lio_dict=lio_dict):
        return None

    # print "DEBUG lio_get_fc_target_map_lunt t: %s" % tgt_wwn
    # print "DEBUG lio_get_fc_target_map_lunt i: %s" % init_wwn
    # print "DEBUG lio_get_fc_target_map_lunt tgt_id: %s" % tgt_lun_id
    init_acls_dict = lio_dict["tcm_fc"][tgt_wwn]["acls"][init_wwn]
    if tgt_lun_id not in list(init_acls_dict.keys()):
        # _print ("FAIL: Could not get mapping for lun %s on FC target %s/%s" % (tgt_lun_id, tgt_wwn, init_wwn))
        return None

    return init_acls_dict[tgt_lun_id]


def lio_get_fc_target_lun_mapping(bs_type, lun_name, lio_dict=None):
    """Get the mapping information for an specifc LUN
    The arguments are:
    \tbs_type:      Backstore Type
    \tlun_name:     LUN name
    Returns:
    \tList:         A list with a dictionary for each mapping found
    \tNone:         If no mapping was found
    """
    if not lio_dict:
        lio_dict = lio_query()

    bs_details_dict = lio_get_backstore_details(bs_type, lun_name, lio_dict=lio_dict)
    if not bs_details_dict:
        # It does not exist
        return None

    if "mapping" not in list(bs_details_dict.keys()):
        return None

    return bs_details_dict["mapping"]


# ## FC tag ###
def lio_tag_fc_initiator(tgt_wwn, init_wwn, tag):
    """Create a tag for initiator wwn
    The arguments are:
    \ttgt_wwn:     Host wwn
    \tinit_wwn:    Initiator wwn
    \ttag:          tag for the initiator wwn
    Returns:
    \tTrue: If tag is created
    \tFalse: If some problem happened
    """
    cmd = "targetcli /tcm_fc/%s/acls tag %s %s" % (_wwn_2_tgt_wwn(tgt_wwn), _wwn_2_tgt_wwn(init_wwn), tag)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not tag FC initiator %s" % init_wwn)
        return False

    return True


def lio_untag_fc_initiator(tgt_wwn, tag):
    """Remove tag from initiator wwn
    The arguments are:
    \ttgt_wwn:     Host wwn
    \ttag:          tag for the initiator wwn
    Returns:
    \tTrue: If tag is created
    \tFalse: If some problem happened
    """
    cmd = "targetcli /tcm_fc/%s/acls untag %s" % (_wwn_2_tgt_wwn(tgt_wwn), tag)
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not untag FC tag %s" % tag)
        return False

    return True


def lio_is_fc_tag(tgt_wwn, tag):
    """Check if a tag is a FC initiator tag
    The arguments are:
    \twwn:     Host wwn
    Returns:
    \tTrue: If target is added
    \tFalse: If some problem happened
    """
    cmd = "targetcli /tcm_fc/%s/acls/%s" % (tgt_wwn, tag)
    retcode = run(cmd, return_output=False, verbose=False)
    if retcode != 0:
        return False
    return True


##################################################
# ################ LIO General ####################
##################################################
def lio_install():
    """Install targetcli tool
    The arguments are:
    \tNone
    Returns:
    \tTrue: If targetcli is installed correctly
    \tFalse: If some problem happened
    """
    ver = libsan.host.linux.dist_ver()
    if not ver:
        return False

    targetcli_pack = "targetcli"
    if libsan.host.linux.dist_name() == "RHEL" and ver < 7:
        targetcli_pack = "fcoe-target-utils"

    if not libsan.host.linux.install_package(targetcli_pack):
        _print("FAIL: Could not install %s" % targetcli_pack)
        return False

    return True


def lio_get_service_name():
    """Get service name that targetcli uses
    The arguments are:
    \tNone
    Returns:
    \tString: Name of the service
    \tNone: If some problem happened
    """
    targetcli_service = "target"
    ver = libsan.host.linux.dist_ver()
    if not ver:
        return None

    if libsan.host.linux.dist_name() == "RHEL" and ver < 7:
        targetcli_service = "fcoe-target"

    return targetcli_service


def lio_restart():
    """Restart LIO service
    The arguments are:
    \tNone
    Returns:
    \tTrue: Service started
    \tFalse: If some problem happened
    """
    targetcli_service = lio_get_service_name()
    if not targetcli_service:
        _print("FAIL: lio_restart() - Could not get LIO service name")
        return False

    if not libsan.host.linux.service_restart(targetcli_service):
        _print("FAIL: Could not restart LIO service")
        return False
    # sleep 5s to avoid service to not be restarted
    # target.service start request repeated too quickly, refusing to start.
    libsan.host.linux.sleep(5)
    return True


def lio_show():
    """List LIO configuration
    The arguments are:
    \tNone
    Returns:
    \tTrue: If listed config
    \tFalse: If some problem happened
    """
    cmd = "targetcli ls"
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not show LIO config")
        return False
    return True


def lio_saveconfig():
    """Save LIO configuration
    The arguments are:
    \tNone
    Returns:
    \tTrue: If config is saved
    \tFalse: If some problem happened
    """
    cmd = "targetcli saveconfig"
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not save LIO config")
        return False
    return True


def lio_clearconfig():
    """Clear LIO configuration
    The arguments are:
    \tNone
    Returns:
    \tTrue: If config is deleted
    \tFalse: If some problem happened
    """
    _print("INFO: Cleaning up LIO configuration")

    if not libsan.host.linux.is_installed('targetcli'):
        return True

    fileio_dict = lio_get_backstores("fileio")
    if fileio_dict:
        # Delete all files before cleaning configuration
        for lun in list(fileio_dict.keys()):
            lio_delete_backstore(bs_type="fileio", lun_name=lun)

    cmd = "targetcli clearconfig true"
    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        _print("FAIL: Could not delete LIO config")
        return False

    return True


def lio_version():
    """Get targetcli version
    The arguments are:
    \tNone
    Returns:
    \tString: TargetCli version
    \tNone: If some problem happened
    """
    cmd = "targetcli version"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: Could not get targetcli version")
        return None

    version_regex = re.compile(".* version (.*)$")
    m = version_regex.search(output)
    if m:
        return m.group(1)
    _print("FAIL: Could not parse targetcli version output (%s)" % output)
    return None


def lio_clean_up_targets(lio_dict=None):
    """
    Removing backstore might leave targets with empty mapping
    They should be removed
    """
    lio_dict = lio_query(lio_dict)
    fc_targets = lio_get_fc_target(lio_dict=lio_dict)
    if not fc_targets:
        # nothing to clean up
        return True
    # First we checked for initiators without mapping
    need_to_query_lio = False
    success = True
    for tgt in fc_targets:
        initiators = lio_get_fc_target_acl(tgt, lio_dict=lio_dict)
        if initiators:
            for init in initiators:
                if not lio_fc_target_get_mapped_luns(tgt, init, lio_dict=lio_dict):
                    _print("DEBUG: Should remove initiator %s from tgt %s" % (init, tgt))
                    if not lio_delete_fc_target_acl(tgt, init):
                        success = False
                    need_to_query_lio = True

    # Check again for targets without any initiator
    if need_to_query_lio:
        lio_dict = lio_query()
    fc_targets = lio_get_fc_target(lio_dict=lio_dict)
    for tgt in fc_targets:
        initiators = lio_get_fc_target_acl(tgt, lio_dict=lio_dict)
        if not initiators:
            _print("DEBUG: Should remove target %s" % tgt)
            if not lio_delete_fc_target(tgt):
                success = False

    return success


class TargetCLI:
    def __init__(self, path="", disable_check=False):
        self.disable_check = disable_check
        self.path = path
        if libsan.host.linux.dist_ver() < 7:
            _print("FATAL: TargetCLI is not supported on RHEL < 7.")

        if not libsan.host.linux.install_package("targetcli", check=False):
            _print("FATAL: Could not install targetcli package")

    @staticmethod
    def remove_nones(kwargs):
        return {k: v for k, v in kwargs.items() if v is not None}

    @staticmethod
    def _extract_args(kwargs, keys=None):
        keys = keys or ["return_output", "verbosity", "path"]
        arguments = dict()
        for key in keys:
            if key not in kwargs:
                continue
            arguments[key] = kwargs.pop(key)
        return arguments, kwargs

    def _run(self, cmd, verbosity=True, return_output=False, path=None):
        # Constructs the command to run and runs it

        if path is not None:
            self.path = path

        if cmd == "cd" and self.path is None:
            cmd = "targetcli cd"
        else:
            cmd = "targetcli " + self.path + " " + cmd

        if return_output:
            ret, data = run(cmd, verbose=verbosity, return_output=True)
            if ret != 0:
                _print("WARN: Running command: '%s' failed. Return with output." % cmd)
            return ret, data

        ret = run(cmd, verbose=verbosity)
        if ret != 0:
            _print("WARN: Running command: '%s' failed." % cmd)
        return ret

    def ls(self, depth="", **kwargs):
        return self._run("ls %s" % depth, **kwargs)

    def cd(self, **kwargs):
        return self._run("cd", **kwargs)

    def pwd(self, **kwargs):
        return self._run("pwd", **kwargs)

    def create(self, **kwargs):
        keys = None
        cmd = "create "
        arguments, kwargs = self._extract_args(kwargs)
        # the following ensures the ordering is correct in correct paths
        # True means it is required, False it is optional
        if "backstores/block" in self.path:
            keys = {"name": True, "dev": True, "readonly": False, "wwn": False}
        elif "backstores/fileio" in self.path:
            keys = {"name": True, "file_or_dev": True, "size": True, "write_back": False, "sparse": False,
                    "wwn": False}
        elif "backstores/pscsi" in self.path:
            keys = {"name": True, "dev": True}
        elif "backstores/ramdisk" in self.path:
            keys = {"name": True, "size": True, "nullio": False, "wwn": False}
        elif "backstores/user:qcow" in self.path:
            keys = {"name": True, "size": True, "cfgstring": True, "wwn": False, "hw_max_sectors": False,
                    "control": False}
        elif "backstores/user:rbd" in self.path:
            keys = {"name": True, "size": True, "cfgstring": True, "wwn": False, "hw_max_sectors": False,
                    "control": False}
        elif "backstores/user:zbc" in self.path:
            keys = {"name": True, "size": True, "cfgstring": True, "wwn": False, "hw_max_sectors": False,
                    "control": False}
        elif self.path.startswith("/iscsi/"):
            if "iqn" in self.path:
                if "acls" in self.path:
                    keys = {"wwn": True, "add_mapped_luns": False}
                elif "luns" in self.path:
                    keys = {"storage_object": True, "lun": False, "add_mapped_luns": False}
                elif "portals" in self.path:
                    keys = {"ip_address": False, "ip_port": False}
                else:
                    keys = {"tag": False}
            else:
                keys = {"wwn": False}
        elif self.path.startswith("/loopback"):
            if "naa" in self.path:
                if "luns" in self.path:
                    keys = {"storage_object": True, "lun": False, "add_mapped_luns": False}
            else:
                keys = {"wwn": False}
        else:
            keys = {"wwn": False}
        for key in keys:
            try:
                cmd += "%s=%s " % (key, kwargs[key])
            except KeyError:
                if not self.disable_check and keys[key]:
                    _print("FAIL: Create on path '%s' requires argument %s." % (self.path, key))
                    return 1
        return self._run(cmd, **arguments)

    def delete(self, **kwargs):
        keys = None
        cmd = "delete "
        arguments, kwargs = self._extract_args(kwargs)
        # the following ensures the ordering is correct in correct paths
        # True means it is required, False it is optional
        if "backstores/block" in self.path:
            keys = {"name": True}
        elif "backstores/fileio" in self.path:
            keys = {"name": True}
        elif "backstores/pscsi" in self.path:
            keys = {"name": True}
        elif "backstores/ramdisk" in self.path:
            keys = {"name": True}
        elif "backstores/user:qcow" in self.path:
            keys = {"name": True}
        elif "backstores/user:rbd" in self.path:
            keys = {"name": True}
        elif "backstores/user:zbc" in self.path:
            keys = {"name": True}
        elif self.path.startswith("/iscsi/"):
            if "iqn" in self.path:
                if "acls" in self.path:
                    keys = {"wwn": True}
                elif "luns" in self.path:
                    keys = {"lun": True}
                elif "portals" in self.path:
                    keys = {"ip_address": True, "ip_port": True}
                else:
                    keys = {"tag": True}
            else:
                keys = {"wwn": True}
        elif self.path.startswith("/loopback"):
            if "naa" in self.path:
                if "luns" in self.path:
                    keys = {"lun": True}
            else:
                keys = {"wwn": False}
        else:
            keys = {"wwn": True}

        for key in keys:
            try:
                cmd += "%s=%s " % (key, kwargs[key])
            except KeyError:
                if not self.disable_check and keys[key]:
                    _print("FAIL: Delete on path '%s' requires argument %s." % (self.path, key))
                    return 1

        return self._run(cmd, **arguments)

    def help(self, topic="", **kwargs):
        return self._run("help %s" % topic, **kwargs)

    def saveconfig(self, savefile=None, **kwargs):
        cmd = "saveconfig"
        if savefile:
            cmd += " %s" % savefile
        return self._run(cmd, **kwargs)

    def restoreconfig(self, savefile="/etc/target/saveconfig.json", clearexisting=False, **kwargs):
        return self._run("restoreconfig %s %s" % (savefile, clearexisting), **kwargs)

    def clearconfig(self, confirm=True, **kwargs):
        return self._run("clearconfig %s" % confirm, **kwargs)

    def sessions(self, action="", sid="", **kwargs):
        return self._run("sessions %s %s" % (action, sid), **kwargs)

    def exit(self, **kwargs):
        return self._run("exit", **kwargs)

    def get(self, group="", **kwargs):
        arguments, kwargs = self._extract_args(kwargs)
        cmd = "get %s %s" % (group, " ".join(kwargs.keys()))
        return self._run(cmd, **arguments)

    def set(self, group="", **kwargs):
        arguments, kwargs = self._extract_args(kwargs)
        params = ["%s='%s'" % (kwarg, kwargs[kwarg]) if kwargs[kwarg] != "" else "%s='%s'" % (kwarg, kwargs[kwarg]) for
                  kwarg in kwargs]
        cmd = "set %s %s" % (group, " ".join(params))
        return self._run(cmd, **arguments)

    def info(self, **kwargs):
        return self._run("info", **kwargs)

    def version(self, **kwargs):
        return self._run("version", **kwargs)

    def status(self, **kwargs):
        return self._run("status", **kwargs)

    def refresh(self, **kwargs):
        return self._run("refresh", **kwargs)

    def disable(self, **kwargs):
        return self._run("disable", **kwargs)

    def enable(self, **kwargs):
        return self._run("enable", **kwargs)

    def bookmarks(self, **kwargs):
        # How to use this?
        return self._run("bookmarks", **kwargs)

    def enable_iser(self, boolean="", **kwargs):
        return self._run("enable_iser %s" % boolean, **kwargs)

    def enable_offload(self, boolean="", **kwargs):
        return self._run("enable_offload %s" % boolean, **kwargs)

    def tag(self, wwn_or_tag="", new_tag="", **kwargs):
        return self._run("tag %s %s" % (wwn_or_tag, new_tag), **kwargs)

    def untag(self, wwn_or_tag="", **kwargs):
        return self._run("untag %s" % wwn_or_tag, **kwargs)
