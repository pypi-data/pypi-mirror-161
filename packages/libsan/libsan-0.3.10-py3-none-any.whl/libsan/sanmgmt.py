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

"""sanmgmt.py: Module to help manage SAN devices that are conifgured at /etc/san_top.conf."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import os
import libsan.host.mp
import libsan.host.fc
import libsan.host.scsi
import libsan.host.net
import libsan.host.linux
import libsan.misc.array
import libsan.switch.cisco.nxos
import libsan.switch.brocade.fos
import libsan.misc.size
import libsan.host.conf
import libsan.host.iscsi

DEFAULT_CONF = "/etc/san_top.conf"


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


def create_sanmgmt_for_mpath(mpath_name=None, san_conf=None):
    """
    Usage
        create_sanmgmt_for_mpath($mpath_name)
    Purpose
        Create SanMgmt object base on information of mpath mpath, will load
        the default configuration of SanMgmt via obj_sanmgmt->load_conf()
    Parameter
        mpath_name     # like 'mpatha'
            or
        undef           # will return the default object of libsan
    Returns
        libsan_obj     # object of libsan
            or
        undef
    """
    obj_sanmgmt = SanMgmt()
    h_wwpns = []
    t_wwpns = []
    t_iqns = []
    h_iqns = []
    iface_macs = []

    if mpath_name:
        mpath_info_dict = libsan.host.mp.multipath_query_all(mpath_name)
        if not mpath_info_dict:
            _print("FAIL: Could not find info for multipath %s" % mpath_name)
            return None
        if "t_wwpns" in list(mpath_info_dict.keys()):
            t_wwpns = mpath_info_dict["t_wwpns"]
        if "h_wwpns" in list(mpath_info_dict.keys()):
            h_wwpns = mpath_info_dict["h_wwpns"]
        if "t_iqns" in list(mpath_info_dict.keys()):
            t_iqns = mpath_info_dict["t_iqns"]
        if "h_iqns" in list(mpath_info_dict.keys()):
            h_iqns = mpath_info_dict["h_iqns"]
        if "iface_macs" in list(mpath_info_dict.keys()):
            iface_macs = mpath_info_dict["iface_macs"]
        # Map info well be used to create tmp LUN with the same settings as mpath_name
        if "map_info" in list(mpath_info_dict.keys()):
            obj_sanmgmt.map_info(mpath_info_dict["map_info"])

    else:
        h_wwpns = libsan.host.fc.h_wwpn_of_host()
        t_wwpns = libsan.host.fc.t_wwpn_of_host()
        h_iqns = libsan.host.iscsi.h_iqn_of_sessions()
        t_iqns = libsan.host.iscsi.t_iqn_of_sessions()
        iface_macs = libsan.host.iscsi.mac_of_iscsi_session()

    if t_wwpns and h_wwpns:
        obj_sanmgmt.h_wwpns(h_wwpns)
        obj_sanmgmt.t_wwpns(t_wwpns)
    if t_iqns and h_iqns:
        obj_sanmgmt.h_iqns(h_iqns)
        obj_sanmgmt.t_iqns(t_iqns)
        obj_sanmgmt.macs(iface_macs)

    obj_sanmgmt.load_conf(san_conf)
    return obj_sanmgmt


def create_sanmgmt_for_storage_array(storage_name, san_conf=None):
    """
    Usage
        create_sanmgmt_for_storage_array(storage_name)
    Purpose
        Create SanMgmt object base on information of mpath mpath, will load
        the default configuration of SanMgmt via obj_sanmgmt->load_conf()
    Parameter
        mpath_name     # like 'mpatha'
            or
        undef           # will return the default object of libsan
    Returns
        libsan_obj     # object of libsan
            or
        undef
    """

    san_conf_dict = _load_san_conf(san_conf)
    if not san_conf_dict:
        _print("FAIL: create_sanmgmt_for_storage_array() - Could read san config")
        return None
    sa_conf = None

    for san_cfg in san_conf_dict:
        dev_conf_dict = san_conf_dict[san_cfg]

        # We only want type of storage array
        if ("type" not in list(dev_conf_dict.keys()) or
                dev_conf_dict["type"] != "array"):
            continue
        if dev_conf_dict["ctrl_ip"] == storage_name:
            sa_conf = dev_conf_dict
            break

    if not sa_conf:
        _print("FAIL: create_sanmgmt_for_storage_array() - Could not find storage array with name %s" % storage_name)
        return None

    obj_sanmgmt = SanMgmt()
    t_iqns = []
    t_wwpns = []
    if "port_of" in list(sa_conf.keys()):
        for port in list(sa_conf["port_of"].keys()):
            if libsan.host.iscsi.is_iqn(port):
                t_iqns.append(port)
            if libsan.host.fc.is_wwn(port):
                t_wwpns.append(port)
    if t_iqns:
        obj_sanmgmt.t_iqns(t_iqns)
    if t_wwpns:
        obj_sanmgmt.t_wwpns(t_wwpns)

    obj_sanmgmt.load_conf(san_conf)
    return obj_sanmgmt


def _load_san_conf(san_conf=None):
    """
    Load the SAN storage configuration from config file
    default path for config file is /etc/san_top.conf
    """
    if not san_conf:
        san_conf = DEFAULT_CONF

    if not os.path.isfile(san_conf):
        _print("FAIL: Could not read %s" % san_conf)
        return None

    _print("INFO: SanMgmt Loading conf: %s" % san_conf)
    san_conf_dict = libsan.host.conf.load_config_as_json(san_conf)
    module_name_dict = dict()
    module_name_dict["switch"] = "libsan.switch"
    module_name_dict["array"] = "libsan.array"
    module_name_dict["physwitch"] = "libsan.physwitch"

    if "general" not in san_conf_dict:
        san_conf_dict["general"] = {}
    san_conf_dict["general"]["san_conf_file"] = san_conf

    # replace alias names by its value
    alias_dict = None
    if "alias" in san_conf_dict:
        alias_dict = san_conf_dict["alias"]
    if alias_dict:
        for entry in san_conf_dict:
            if entry == "alias":
                continue
            for sub_key in san_conf_dict[entry]:
                if san_conf_dict[entry][sub_key] in alias_dict:
                    san_conf_dict[entry][sub_key] = alias_dict[san_conf_dict[entry][sub_key]]

    # We create a list of ports that are defined for this item
    for san_hw in san_conf_dict:
        if san_hw == "general" or san_hw == "alias":
            continue
        hw_info = san_conf_dict[san_hw]
        # Use list as the dictionary will be updated
        for key in list(hw_info):
            key_value = hw_info[key]
            mac_key_regex = re.compile("mac_(.+)$")
            mac_match = mac_key_regex.match(key)
            if mac_match:
                mac = key_value
                mac = libsan.host.net.standardize_mac(mac)
                if mac:
                    # The entry is a MAC or WWPN address
                    if "port_of" not in hw_info:
                        hw_info["port_of"] = {}
                    if mac in hw_info["port_of"]:
                        _print("FAIL: MAC %s is specific more then once on %s item section" % (mac, key))
                        print(hw_info["port_of"])
                        return None
                    hw_info["port_of"][mac] = mac_match.group(1)
                    continue
                else:
                    _print("FAIL: Invalid MAC address %s on conf section %s" % (key_value, key))
                    return None

            wwpn_key_regex = re.compile("wwpn-(.+)$")
            wwpn_match = wwpn_key_regex.match(key)
            if wwpn_match:
                wwpn = key_value
                wwpn = libsan.host.fc.standardize_wwpn(wwpn)
                if wwpn:
                    if "port_of" not in hw_info:
                        hw_info["port_of"] = {}
                    if wwpn in hw_info["port_of"]:
                        _print("FAIL: WWPN %s is specific more then once on %s item section" % (wwpn, key))
                        print(hw_info["port_of"])
                        return None
                    hw_info["port_of"][wwpn] = wwpn_match.group(1)
                    continue
                else:
                    _print("FAIL: Invalid WWPN %s on conf section %s" % (key_value, key))
                    return None

            # For iSCSI target
            if libsan.host.iscsi.is_iqn(key_value):
                if "port_of" not in hw_info:
                    hw_info["port_of"] = {}
                hw_info["port_of"][key_value] = key
                continue
            # For physwitch
            simplex_key_regex = re.compile("^simplex_con_([^ ]+)$")
            simplex_match = simplex_key_regex.match(key)
            if simplex_match:
                if "simplex_con" not in hw_info:
                    hw_info["simplex_con"] = {}
                src_port = simplex_match.group(1)
                dst_port = key_value
                hw_info["simplex_con"][src_port] = dst_port
                continue

            duplex_key_regex = re.compile("^duplex_con_([^ ]+)$")
            duplex_match = duplex_key_regex.match(key)
            if duplex_match:
                if "duplex_con" not in hw_info:
                    hw_info["duplex_con"] = {}
                src_port = duplex_match.group(1)
                dst_port = key_value
                hw_info["duplex_con"][src_port] = dst_port
                hw_info["duplex_con"][dst_port] = src_port
                continue

    san_iscsi_conf = dict()
    san_iscsi_conf["hosts"] = {}
    for san_hw in san_conf_dict:
        if san_hw == "general" or san_hw == "alias":
            continue
        hw_info = san_conf_dict[san_hw]
        if "type" not in hw_info:
            continue
        if hw_info["type"] != "iscsi_initiator":
            if "model" not in hw_info:
                _print("FATAL: device %s does not have 'model' set on configuration" % san_hw)
                return None
            # for example model: EMC-VNX should search class on emc.vnx
            model = hw_info["model"].lower()
            module = module_name_dict[hw_info["type"]]
            m = re.match(r"(\S+)-(\S+)", model)
            if not m:
                _print("FATAL: model for %s is not on right format (vendor-model)" % model)
                return None
            vendor = m.group(1)
            model = m.group(2)
            module += ".%s.%s" % (vendor, model)
            # The name of the class defined under vendor module should be named as the model
            class_name = "%s" % model
            hw_info["class_name"] = "%s" % class_name
            hw_info["module_name"] = "%s" % module
        else:
            # TODO iscsi_conf
            san_iscsi_conf["hosts"][san_hw] = {}
            iscsi_host_conf = san_iscsi_conf["hosts"][san_hw]
            for option in hw_info:
                m_iface = re.match(r"^iface_(\d+)$", option)
                if m_iface:
                    if "ifaces" not in iscsi_host_conf:
                        iscsi_host_conf["ifaces"] = {}
                    if m_iface.group(1) not in iscsi_host_conf["ifaces"]:
                        iscsi_host_conf["ifaces"][m_iface.group(1)] = {}
                    iscsi_host_conf["ifaces"][m_iface.group(1)]["name"] = hw_info[option]

                m_iface = re.match(r"^iface_disc_mod_(\d+)$", option)
                if m_iface:
                    if "ifaces" not in iscsi_host_conf:
                        iscsi_host_conf["ifaces"] = {}
                    if m_iface.group(1) not in iscsi_host_conf["ifaces"]:
                        iscsi_host_conf["ifaces"][m_iface.group(1)] = {}
                    iscsi_host_conf["ifaces"][m_iface.group(1)]["disc_mod"] = hw_info[option]

                m_iface = re.match(r"^iface_iqn_(\d+)$", option)
                if m_iface:
                    if "ifaces" not in iscsi_host_conf:
                        iscsi_host_conf["ifaces"] = {}
                    if m_iface.group(1) not in iscsi_host_conf["ifaces"]:
                        iscsi_host_conf["ifaces"][m_iface.group(1)] = {}
                    iscsi_host_conf["ifaces"][m_iface.group(1)]["iqn"] = hw_info[option]

                m_iface = re.match(r"^iface_ip_(\d+)$", option)
                if m_iface:
                    if "ifaces" not in iscsi_host_conf:
                        iscsi_host_conf["ifaces"] = {}
                    if m_iface.group(1) not in iscsi_host_conf["ifaces"]:
                        iscsi_host_conf["ifaces"][m_iface.group(1)] = {}
                    iscsi_host_conf["ifaces"][m_iface.group(1)]["ip"] = hw_info[option]

                m_iface = re.match(r"^iface_mask_(\d+)$", option)
                if m_iface:
                    if "ifaces" not in iscsi_host_conf:
                        iscsi_host_conf["ifaces"] = {}
                    if m_iface.group(1) not in iscsi_host_conf["ifaces"]:
                        iscsi_host_conf["ifaces"][m_iface.group(1)] = {}
                    iscsi_host_conf["ifaces"][m_iface.group(1)]["mask"] = hw_info[option]

                m_iface = re.match(r"^iface_gateway_(\d+)$", option)
                if m_iface:
                    if "ifaces" not in iscsi_host_conf:
                        iscsi_host_conf["ifaces"] = {}
                    if m_iface.group(1) not in iscsi_host_conf["ifaces"]:
                        iscsi_host_conf["ifaces"][m_iface.group(1)] = {}
                    iscsi_host_conf["ifaces"][m_iface.group(1)]["gateway"] = hw_info[option]

                m_iface = re.match(r"^iface_mac_(\d+)$", option)
                if m_iface:
                    if "ifaces" not in iscsi_host_conf:
                        iscsi_host_conf["ifaces"] = {}
                    if m_iface.group(1) not in iscsi_host_conf["ifaces"]:
                        iscsi_host_conf["ifaces"][m_iface.group(1)] = {}
                    iscsi_host_conf["ifaces"][m_iface.group(1)]["mac"] = hw_info[option]

                m_iface = re.match(r"^iface_trans_(\d+)$", option)
                if m_iface:
                    if "ifaces" not in iscsi_host_conf:
                        iscsi_host_conf["ifaces"] = {}
                    if m_iface.group(1) not in iscsi_host_conf["ifaces"]:
                        iscsi_host_conf["ifaces"][m_iface.group(1)] = {}
                    iscsi_host_conf["ifaces"][m_iface.group(1)]["trans"] = hw_info[option]

                m_iface = re.match(r"^target_ip_(\d+)$", option)
                if m_iface:
                    if "ifaces" not in iscsi_host_conf:
                        iscsi_host_conf["ifaces"] = {}
                    if m_iface.group(1) not in iscsi_host_conf["ifaces"]:
                        iscsi_host_conf["ifaces"][m_iface.group(1)] = {}
                    iscsi_host_conf["ifaces"][m_iface.group(1)]["target_ip"] = hw_info[option]

            iscsi_host_conf["hostname"] = san_hw
            # print san_conf_dict["iscsi_conf"][entry]
            # if "iface" in san_conf_dict[entry]["iscsi_conf"].keys()
            #    san_conf_dict[entry]["iscsi_conf"]["iface"]
            continue
    san_conf_dict["iscsi_conf"] = san_iscsi_conf

    return san_conf_dict


def check_sw_conf(config_file=None, switch_id=None):
    """
    Check if information from configuration file matches
    what is set on switch
    The arguments are:
    \tconfig_file         Full path to file where is the config
    \tswitch_id:          ID of an specific switch (optional)
    Returns:
    \tTrue:               All configuration is correct
    \tFalse:              There was a problem
    """
    config = _load_san_conf(config_file)

    if not config:
        _print("FAIL: Could not read %s" % config_file)
        return False

    total_error = 0
    # if switch_id paramter is not given we check all switches
    if switch_id:
        switch_ids = [switch_id]
    else:
        switch_ids = config

    for key in switch_ids:
        if "type" not in config[key]:
            # Entry does not have type, for example alias, general...
            continue
        if config[key]["type"] != "switch":
            # We are only interested on switches
            continue

        if "skip_check" in list(config[key].keys()):
            if config[key]["skip_check"] == "1":
                print("INFO: skipping test on %s" % key)
                # We do not want to check this switch
                continue

        if "model" not in config[key]:
            _print("FAIL: switch %s does not have model option" % key)
            return False

        if "ctrl_ip" not in config[key]:
            _print("FAIL: switch %s does not ctrl_ip configured" % key)
            return False
        if "ctrl_user" not in config[key]:
            _print("FAIL: switch %s does not have ctrl_user configured" % key)
            return False
        if "ctrl_pass" not in config[key]:
            _print("FAIL: switch %s does not have ctrl_pass configured" % key)
            return False

        # We only support ssh
        if "ctrl_type" not in config[key]:
            _print("FAIL: switch %s does not have ctrl_type configured" % key)
            return False
        if "ssh" not in config[key]["ctrl_type"]:
            _print("FAIL: we do not support ctrl_type %s on %s" % (config[key]["ctrl_type"], key))
            return False

        ip = config[key]["ctrl_ip"]
        user = config[key]["ctrl_user"]
        passwd = config[key]["ctrl_pass"]

        switch_class = get_class(config[key]["module_name"], config[key]["class_name"])
        if switch_class:
            switch = switch_class(ip, user, passwd)
        else:
            # unsupported switch
            continue
        _print("INFO: Checking configuration for switch %s (%s)" % (key, ip))
        switch_error = 0

        wwpn_dict = switch.wwpn_2_port_id()
        if not wwpn_dict:
            # Did not find any WWPN entry
            continue
        # Let's check if the ports that are online on the switch match what we have on config
        for p_id in wwpn_dict:
            alias = libsan.host.conf.get_alias(config, wwpn_dict[p_id])
            if p_id not in config[key]:
                if not wwpn_dict[p_id]:
                    continue
                if alias:
                    print("WARN: Port '%s' is not defined on '%s' on file '%s' on switch has wwpn %s (%s)"
                          % (p_id, key, config_file, alias, wwpn_dict[p_id]))
                else:
                    print("WARN: Port '%s' is not defined on '%s' on file '%s' on switch has wwpn %s"
                          % (p_id, key, config_file, wwpn_dict[p_id]))
                continue
            # need to check if the wwpn on the switch port matches what we expect on config file
            if wwpn_dict[p_id] != config[key][p_id]:
                alias_cfg = libsan.host.conf.get_alias(config, config[key][p_id])
                if alias:
                    print("FAIL: switch %s port '%s' has wwpn '%s (%s)', but on config it expected to be '%s (%s)'"
                          % (key, p_id, alias, wwpn_dict[p_id], alias_cfg, config[key][p_id]))
                else:
                    print("FAIL: switch %s port '%s' has wwpn '%s', but on config it expected to be '%s'"
                          % (key, p_id, wwpn_dict[p_id], config[key][p_id]))
                switch_error += 1

        cap_dict = switch.capability()
        if cap_dict["eth_switch"]:
            mac_dict = switch.mac_2_port_id()
            if not mac_dict:
                # Did not find any MAC entry
                continue
            # Let's check if the ports that are online on the switch match what we have on config
            for p_id in list(mac_dict.keys()):
                if p_id not in list(config[key].keys()):
                    # Not sure when we use MAC, so do not need to give any warnings
                    # _print("WARN: Port '%s' is not defined on '%s' on file '%s' on switch has mac %s"
                    #    % (p_id, key, config_file, mac_dict[p_id]))
                    continue
                # need to check if the wwpn on the switch port matches what we expect on config file
                if mac_dict[p_id] != config[key][p_id]:
                    _print("FAIL: switch port '%s' has mac '%s', but on config it expected to be '%s'" % (
                        p_id, mac_dict[p_id], config[key][p_id]))
                    switch_error += 1
        if not switch_error:
            print("PASS: No problem found on %s" % key)
        total_error += switch_error
    if total_error:
        # _print("FAIL: Check switch configuration")
        return False
    # _print("PASS: Check switch configuration")
    return True


def choose_mpaths(mpath_name=None, exclude_boot_device=True, exclude_lvm_device=True):
    """
    choose_mpaths ()
    Usage
        choose_mpaths($mpath_name)
    Purpose
        If mpath_name defined, we just choose it only.
        Return $ref_choosed_mpath. Check the head of this pod for detailed data
        structure.
        We will choose all SAN mpath devices. If more then one device has
        same Vendor/Product, t_wwpn/h_wwpn or t_inq/h_iqn we choose only one of them
            t_wwpns, h_wwpns, single storage array.
        To choose mpath, we follow this rule:
            1. Each vendor/product.
            1. Each HBA. (h_wwpn)
            1. Each storage array even they are same vendor/product.
    Parameter
        mpath_name (optional)                   if given and mpath_name exist, return info for this mpath
        exclude_boot_device (default = True)    Do not return mpath that is used for boot
        exclude_lvm_device  (default = True)    Do not return any mpath that is used as LVM PV
    Returns
        ref_choosed_mpath
    """

    choosed_mp_infos = []
    choosed_mpath_dict = {}

    free_mpaths = libsan.host.mp.get_free_mpaths(
        exclude_boot_device=exclude_boot_device, exclude_lvm_device=exclude_lvm_device)
    if not free_mpaths:
        return None

    # If mpath name is given and it exists return it
    # If given mpath does not exist, return None
    if mpath_name:
        if mpath_name in list(free_mpaths.keys()):
            choosed_mpath_dict[mpath_name] = free_mpaths[mpath_name]
            return choosed_mpath_dict
        return None

    for mp_info in list(free_mpaths.values()):
        if not mp_info:
            continue

        # Add the first multipath device to the choosen list
        if not choosed_mp_infos:
            choosed_mp_infos.append(mp_info)
            continue

        # check vendor/product
        if "vendor" not in list(mp_info.keys()) or "product" not in list(mp_info.keys()):
            _print("WARN: %s has not vendor or product info. Skipping." % mp_info["mpath_name"])
            continue

        if not mp_info["h_wwpns"] and not mp_info["t_wwpns"] and not mp_info["h_iqns"] and not mp_info["t_iqns"]:
            _print("WARN: %s has not seem to be SAN device. Skipping." % mp_info["mpath_name"])
            continue

        # Flag to skip is info already exists on choosed_mp_infos
        found_info = False

        # If there is a device with same info, no need to add another one
        for choosed_mp_info in choosed_mp_infos:
            # _print("DEBUG: mp vendor: [%s] c_mp vendor: [%s]" % (mp_info["vendor"], choosed_mp_info["vendor"]))
            # _print("DEBUG: mp product: [%s] c_mp product: [%s]" % (mp_info["product"], choosed_mp_info["product"]))
            # _print("DEBUG: mp h_iqns: [%s] c_mp h_iqns: [%s]" % (",".join(mp_info["h_iqns"]),
            # ",".join(choosed_mp_info["h_iqns"])))
            if (mp_info["vendor"] == choosed_mp_info["vendor"] and
                    mp_info["product"] == choosed_mp_info["product"] and
                    libsan.misc.array.is_array_same(mp_info["h_wwpns"], choosed_mp_info["h_wwpns"]) and
                    libsan.misc.array.is_array_same(mp_info["t_wwpns"], choosed_mp_info["t_wwpns"]) and
                    # Equalogic has 1 target for each LUN, so if host has more then 1 LUN it will have more then 1 t_iqn
                    # array.is_array_same(mp_info["h_iqns"], choosed_mp_info["h_iqns"]) and
                    # array.is_array_same(mp_info["t_iqns"], choosed_mp_info["t_iqns"])):
                    libsan.misc.array.is_array_same(mp_info["h_iqns"], choosed_mp_info["h_iqns"])):
                found_info = True
                continue
        if not found_info:
            # If info from current mp_info is not included on choosed_mp_infos. we add it
            choosed_mp_infos.append(mp_info)

    if not choosed_mp_infos:
        _print("FAIL: choose_mpath(): no mpath choosed for testing")

    for choosed_mp_info in choosed_mp_infos:
        if "mpath_name" in list(choosed_mp_info.keys()):
            choosed_mpath_dict[choosed_mp_info["mpath_name"]] = choosed_mp_info

    return choosed_mpath_dict


def setup_iscsi():
    obj_sanmgmt = SanMgmt()
    return obj_sanmgmt.setup_iscsi()


def get_class(module, class_name):
    """
    Get a class dynamically
    """
    # importlib is not available on python 2.6 (RHEL-6)
    # import importlib
    # my_class = getattr(importlib.import_module(module), class_name)
    # return my_class
    try:
        mod = __import__("%s" % module, fromlist=[class_name])
        my_class = getattr(mod, class_name)
        return my_class
    except Exception as e:
        print(e)
        return None


class SanMgmt:
    """
    obj = SanMgmt()

    obj.h_wwpns( 'st05_01', '10:00:00:00:c9:95:2f:de' )
    obj.t_wwpns('netapp', '50:0a:09:85:99:4b:8d:c5')
    obj.macs( 'st51_nic_01', '08:00:27:05:37:71' )

    obj.load_conf("/etc/san_top.conf")

    # FC/FCoE/Ethernet Switch
    obj.link_trigger( action => "UP", addr => 'st51_01' )
    obj.link_trigger( action => "DOWN", addr => 'st51_01' )
    obj.link_all_up()


    # Storage Array
    lun_name = obj.lun_create("1GiB")
    ok       = obj.lun_map($lun_name)
    lun_name = obj.lun_create_and_map("1GiB")
    ok       = obj.lun_unmap($lun_name)
    ok       = obj.lun_unmap_regex($regex)
    ok       = obj.lun_remove($lun_name)
    new_lun_size_bytest = obj.lun_grow(
                                lun_name => lun_name,
                                increment => "1GiB" )
    new_lun_size_bytest = obj->lun_shrink(
                                lun_name => lun_name,
                                increment => "1GiB" )
    lun_size_bytes  = obj.lun_size_of($lun_name)
    lun_size_human  = obj.lun_size_of(lun_name=>$lun_name, human=>1)
    ref_scsi_info   = obj.query_scsi_info( recheck => 1 )
    ref_my_lun_info = obj.query_my_lun_info( recheck => 1 ) )

    # Layer 1/Physical Switch
    ok = obj.port_disconnect("st05_01")
    ok = obj.port_connect("st05_01")
    ok = obj.port_flap(
        addr      => "st05_02",
        up_time   => "100",
        down_time => "100",
        count     => "100"
      )


    # Misc
    ok = obj.rescan_host()
    """

    def __init__(self):
        self.san_conf_dict = {}  # Store current object settings
        self._h_iqns = []
        self._t_iqns = []
        self._h_wwpns = []
        self._t_wwpns = []
        self._macs = []
        self._addrs = []
        self._map_info = []

    def load_conf(self, san_conf=None):

        self.san_conf_dict = _load_san_conf(san_conf)
        if not self.san_conf_dict:
            self.san_conf_dict = {"general": {}}
            self.san_conf_dict["general"]["conf_loaded"] = False
            _print("FAIL: Could not load san config")
            return False

        self._load_sa_conf()

        addrs = []
        if self._addrs:
            addrs.extend(self._addrs)
        if self._macs:
            addrs.extend(self._macs)
        if self._h_wwpns:
            addrs.extend(self._h_wwpns)
        if self._t_wwpns:
            addrs.extend(self._t_wwpns)
        if self._t_iqns:
            addrs.extend(self._t_iqns)

        self._addrs = libsan.misc.array.dedup(addrs)

        # load switch config uses _addrs
        self._load_sw_conf()
        self._load_sw_conf(flag_physwitch="physwitch")

        for san_hw in self.san_conf_dict:
            if san_hw == "general":
                san_general_dict = self.san_conf_dict[san_hw]
                san_general_dict["conf_loaded"] = True

        return True

    def is_config_loaded(self):
        """
        """
        if "general" in self.san_conf_dict:
            if "conf_loaded" in self.san_conf_dict["general"]:
                return self.san_conf_dict["general"]["conf_loaded"]

        return False

    def _load_sa_conf(self):
        """
        Usage
            self->_load_sa_conf(san_conf)
        Purpose
            Load configuration file for storage array settings.
            We setup self.san_conf_dict["sa_conf"] base on WWPN/IQN and san_conf
            This method should not generate any output.
            check_conf() will warn user for any incorrect confure.
        Parameter
            san_conf           # the return reference of san_conf
        Returns
            True
                or
            False
        """
        san_conf_dict = self.san_conf_dict

        if not san_conf_dict:
            return False
        sa_conf_dict = {}
        san_conf_dict["sa_conf"] = sa_conf_dict
        san_general_dict = {}
        # search for general configuration
        if "general" in san_conf_dict:
            san_general_dict = san_conf_dict["general"]

        if "capability" not in san_conf_dict:
            san_conf_dict["capability"] = {}
        san_capability_dict = san_conf_dict["capability"]

        _targets = []
        if self._t_iqns:
            _targets.extend(self._t_iqns)
        if self._t_wwpns:
            _targets.extend(self._t_wwpns)

        _all_configured_tgt_ports = []

        for san_hw in san_conf_dict:
            dev_conf_dict = san_conf_dict[san_hw]
            if "type" not in dev_conf_dict:
                continue
            if dev_conf_dict["type"] != "array":
                continue
            # Check if array has port configured
            if "port_of" not in dev_conf_dict:
                continue
            dev_conf_dict["name"] = san_hw

            _all_configured_tgt_ports.extend(dev_conf_dict["port_of"])

            if _targets:
                # We are connected to some target
                for target in _targets:
                    valid_eqlogic_iscsi_prefix = False
                    # For Equallogic iSCSI array we check if target iqn matches a prefix
                    # defined on san_top.conf, as each LUN has their own t_iqn
                    if dev_conf_dict["model"] == "DELL-EQLOGIC":
                        for t in dev_conf_dict["port_of"]:
                            if re.match(t, target) and libsan.host.iscsi.is_iqn(target):
                                valid_eqlogic_iscsi_prefix = True
                    if (target in dev_conf_dict["port_of"] or valid_eqlogic_iscsi_prefix):
                        # Add SAN device to sa_config dict
                        if san_hw in sa_conf_dict:
                            # We already stored the configuration of this device
                            continue
                        if "ctrl_ip" not in dev_conf_dict:
                            _print("FAIL: _load_sa_conf() - ctrl_ip not set on %s" % san_hw)
                            continue
                        ip = dev_conf_dict["ctrl_ip"]

                        if "ctrl_user" not in dev_conf_dict:
                            _print("FAIL: _load_sa_conf() - ctrl_user not set on %s" % san_hw)
                            continue
                        user = dev_conf_dict["ctrl_user"]

                        if "ctrl_pass" not in dev_conf_dict:
                            _print("FAIL: _load_sa_conf() - ctrl_pass not set on %s" % san_hw)
                            continue
                        passwd = dev_conf_dict["ctrl_pass"]

                        tmo = None
                        if "ctrl_tmo" in dev_conf_dict:
                            tmo = dev_conf_dict["ctrl_tmo"]
                        # Initializing SAN class, the class_obj was set on _load_san_conf
                        array_class = get_class(dev_conf_dict["module_name"],
                                                dev_conf_dict["class_name"])
                        if array_class:
                            # san_dev parameter is needed for Equalogic to know to which device it should add
                            # the new target on lun_create
                            array_obj = array_class(ip, user, passwd, timeout=tmo, san_dev=san_hw)
                            if array_obj:
                                array_obj.set_san_conf_path(san_general_dict["san_conf_file"])
                                array_obj.set_sa_conf(dev_conf_dict)
                                dev_conf_dict["class_obj"] = array_obj
                                # _print("DEBUG: load_conf: %s uses class: %s.%s" %
                                #       (san_dev,
                                #        dev_conf_dict["module_name"],
                                #        dev_conf_dict["class_name"]))
                                san_capability_dict.update(array_obj.capability())
                            else:
                                _print("FAIL: %s could not initialize class %s.%s" %
                                       (san_hw, dev_conf_dict["module_name"], dev_conf_dict["class_name"]))
                        else:
                            _print("FAIL: could not load class %s.%s" %
                                   (dev_conf_dict["module_name"], dev_conf_dict["class_name"]))
                        sa_conf_dict[san_hw] = dev_conf_dict

        # remove target ports that are not configure as valid target port on san_top.conf file
        if self._t_iqns:
            # Replace t_wwpn list with a new list with only configured member
            _updated_t_iqns = []
            for t_iqn in self._t_iqns:
                for cfg_tgt_port in _all_configured_tgt_ports:
                    # iSCSI Equalogic creates new t_iqn for each LUN, so we just match the prefix
                    if (re.search("equallogic", t_iqn) and re.match(cfg_tgt_port, t_iqn) or
                            t_iqn == cfg_tgt_port):
                        _updated_t_iqns.append(t_iqn)
            self._t_iqns = _updated_t_iqns
        if self._t_wwpns:
            # Replace t_wwpn list with a new list with only configured member
            self._t_wwpns = [t_wwpn for t_wwpn in self._t_wwpns if
                             _all_configured_tgt_ports and t_wwpn in _all_configured_tgt_ports]

        return True

    def _load_sw_conf(self, flag_physwitch=None):
        """
        Usage
            self->_load_sw_conf(san_conf)
        Purpose
            Load configuration file for storage switch settings.
            We setup self.san_conf_dict["sw_conf"] base on WWPN/IQN and san_conf
            This method should not generate any output.
            check_conf() will warn user for any incorrect confure.
        Parameter
            san_conf           # the return reference of san_conf
        Returns
            True
                or
            False
        """
        san_conf_dict = self.san_conf_dict
        if not san_conf_dict:
            return False
        switch_type = "switch"
        obj_key = "sw_conf"
        if flag_physwitch and flag_physwitch == "physwitch":
            # It is a physical layer switch
            switch_type = "physwitch"
            obj_key = "physw_conf"

        sws_conf_dict = {}
        san_conf_dict[obj_key] = sws_conf_dict

        if "capability" not in san_conf_dict:
            san_conf_dict["capability"] = {}
        san_capability_dict = san_conf_dict["capability"]

        for san_hw in san_conf_dict:
            dev_conf_dict = san_conf_dict[san_hw]
            if "type" not in dev_conf_dict:
                continue
            if dev_conf_dict["type"] != switch_type:
                continue
            # Check if array has port configured
            if "port_of" not in dev_conf_dict:
                continue
            dev_conf_dict["name"] = san_hw
            # Need to process each port individually as they might have
            # different capability, like FC or eth ports
            for addr in dev_conf_dict["port_of"]:
                # In case there are duplicated address
                # do not process it more than once
                if addr in sws_conf_dict:
                    continue
                # We initialized the class providing addresses and the addr is not
                # included there, so we are not interested on it.
                # For example, from a mpath device
                if self._addrs and addr not in self._addrs:
                    continue
                ip = dev_conf_dict["ctrl_ip"]
                user = dev_conf_dict["ctrl_user"]
                passwd = dev_conf_dict["ctrl_pass"]
                # Initializing SAN class, the class_obj was set on _load_san_conf
                switch_class = get_class(dev_conf_dict["module_name"], dev_conf_dict["class_name"])
                if switch_class:
                    # _print("DEBUG: load config switch %s %s %s" % (ip, user, passwd))
                    switch_obj = switch_class(ip, user, passwd)
                    if switch_obj:
                        dev_conf_dict["class_obj"] = switch_obj
                        # _print("DEBUG: load_conf: %s uses class: %s.%s" %
                        #        (san_dev,
                        #        dev_conf_dict["module_name"],
                        #        dev_conf_dict["class_name"]))
                        # san_capability_dict["options"].update(switch_obj.capability())
                    else:
                        _print("FAIL: %s could not initialize class %s.%s" %
                               (san_hw, dev_conf_dict["module_name"], dev_conf_dict["class_name"]))
                else:
                    _print("FAIL: could not load class %s.%s" %
                           (dev_conf_dict["module_name"],
                            dev_conf_dict["class_name"]))
                    continue

                # Switch capability present in all switches
                all_sw_caps = ["link_down", "link_up", "switch_reboot",
                               "phy_port_disconnect", "phy_port_connect",
                               "phy_port_flap", "phy_port_oscillate",
                               "phy_switch_reboot"]
                if switch_obj:
                    # We only add the info if switch has the capability
                    switch_cap = switch_obj.capability()
                    for sw_cap in all_sw_caps:
                        if sw_cap in switch_cap and switch_cap[sw_cap]:
                            if sw_cap not in san_capability_dict:
                                san_capability_dict[sw_cap] = []
                            san_capability_dict[sw_cap].append(addr)

                need_sw_caps = None
                if libsan.host.fc.is_wwn(addr) and switch_obj:
                    need_sw_caps = ["fc_switch", "fc_physwitch"]
                if libsan.host.net.is_mac(addr) and switch_obj:
                    need_sw_caps = ["eth_switch"]
                switch_cap = switch_obj.capability()
                if need_sw_caps:
                    for sw_cap in need_sw_caps:
                        # We only add the info if switch has the capability
                        if sw_cap in switch_cap and switch_cap[sw_cap]:
                            if sw_cap not in san_capability_dict:
                                san_capability_dict[sw_cap] = []
                            san_capability_dict[sw_cap].append(addr)

                sws_conf_dict[san_hw] = dev_conf_dict

        return True

    def check_ports_ready(self):
        """
        Check if all ports that we will need for the test are UP on switch
        """
        _print("INFO: Checking if all ports that we need are UP...")
        h_wwpns = libsan.host.fc.h_wwpn_of_host()
        t_wwpns = libsan.host.fc.t_wwpn_of_host()

        if h_wwpns:
            for h_wwpn in h_wwpns:
                # Make sure Apcon link is UP before checking regular switches
                phy_sw = self.get_physw_self(h_wwpn)
                if phy_sw:
                    _print("INFO: phy switch checking port %s..." % h_wwpn)
                    if not self.phy_port_state(h_wwpn):
                        # Server port is not up
                        # We can try to bring it UP
                        self.phy_link_trigger(action="UP", addr=h_wwpn)
                        if not self.phy_port_state(h_wwpn):
                            _print("FAIL: phy switch we are not able to bring port %s UP" % h_wwpn)
                            return False
                sw = self.get_sw_self(h_wwpn)
                if sw:
                    _print("INFO: checking port %s..." % h_wwpn)
                    if self.port_state(h_wwpn) != "UP":
                        # Server port is not up
                        # We can try to bring it UP
                        self.link_trigger(action="UP", wwpn=h_wwpn)
                        if self.port_state(h_wwpn) != "UP":
                            _print("FAIL: We are not able to bring port %s UP" % h_wwpn)
                            return False
                    # If switch supports enable RCSN messages we want to make sure it is enabled
                    capability = self.get_sw_capability(h_wwpn)
                    if capability:
                        if "rcsn_enable" in capability and capability["rcsn_enable"]:
                            if not self.rcsn_trigger(action="ENABLE", wwpn=h_wwpn):
                                _print("FAIL: We are not able to enable RCSN on port %s" % h_wwpn)
                                return False
                else:
                    # port is not managed by us
                    continue
        if t_wwpns:
            for t_wwpn in t_wwpns:
                # Make sure Apcon link is UP before checking regular switches
                phy_sw = self.get_physw_self(t_wwpn)
                if phy_sw:
                    _print("INFO: phy switch checking port %s..." % t_wwpn)
                    if not self.phy_port_state(t_wwpn):
                        msg = "FAIL: Target phy switch port %s is NOT UP, " % t_wwpn
                        msg += "maybe some other test brought it DOWN on purpose"
                        _print(msg)
                        return False
                sw = self.get_sw_self(t_wwpn)
                if sw:
                    _print("INFO: checking port %s..." % t_wwpn)
                    if self.port_state(t_wwpn) != "UP":
                        _print(
                            "FAIL: Target port %s is NOT UP, maybe some other test brought it DOWN on purpose" % t_wwpn)
                        return False
                        # If switch supports enable RCSN messages we want to make sure it is enabled
                    capability = self.get_sw_capability(t_wwpn)
                    if capability:
                        if "rcsn_enable" in capability and capability["rcsn_enable"]:
                            if not self.rcsn_trigger(action="ENABLE", wwpn=t_wwpn):
                                _print("FAIL: We are not able to enable RCSN on port %s" % t_wwpn)
                                return False
                else:
                    # port is not managed by us
                    continue

        nics = libsan.host.net.get_nics()
        if nics:
            for nic in nics:
                if nic == "lo":
                    # skip loopback interface
                    continue
                mac = libsan.host.net.get_mac_of_nic(nic)
                if not mac:
                    _print("FAIL: Could not get MAC for interface %s" % nic)
                    continue
                sw = self.get_sw_self(mac)
                if sw:
                    _print("INFO: checking port %s..." % mac)
                    if self.port_state(mac) != "UP":
                        # Server port is not up
                        # We can try to bring it UP
                        self.link_trigger(action="link_up", addr=mac)
                        if self.port_state(mac) != "UP":
                            _print("FAIL: We are not able to bring port %s UP" % mac)
                            return False
                    # If switch supports enable RCSN messages we want to make sure it is enabled
                    capability = self.get_sw_capability(mac)
                    if capability:
                        if "rcsn_enable" in capability and capability["rcsn_enable"]:
                            if not self.rcsn_trigger(action="ENABLE", addr=mac):
                                _print("FAIL: We are not able to enable RCSN on port %s" % mac)
                                return False
                else:
                    # port is not managed by us
                    continue
        # TODO iSCSI Target MAC address

        _print("INFO: PASS all ports that we need are UP.")
        return True

    def h_wwpns(self, h_wwpns=None):
        """
        Usage
            obj.h_wwpns()              #For querying
            obj.h_wwpns(@h_wwpns)      #For setting
        Purpose
            Setup Host HBA WWPNs. Only useful you want to control remote
            server's FC SAN. If localhost is the server we are working, we will
            find out the Host HBA WWPNs via libsan.host.fc.
        Parameters
            @h_wwpns
        Returns
            List: h_wwpns
                or
            None
        """
        h_wwpns = h_wwpns or []
        # We are going to set h_wwpns
        if h_wwpns:
            self._h_wwpns = h_wwpns

        # Does not matter if we set the list or just and to read it, we always return the list
        return self._h_wwpns

    def t_wwpns(self, t_wwpns=None):
        """
        Usage
            obj.t_wwpns()              #For querying
            obj.t_wwpns(@t_wwpns)      #For setting
        Purpose
            Setup Setup Storage Array/Target WWPNs. Only useful you want to control remote
            server's FC SAN. If localhost is the server we are working, we will
            find out the Host HBA WWPNs via libsan.host.fc.
        Parameters
            @t_wwpns
        Returns
            List: t_wwpns
                or
            None
        """
        # We are going to set h_wwpns
        if t_wwpns:
            self._t_wwpns = t_wwpns

        # Does not matter if we set the list or just and to read it, we always return the list
        return self._t_wwpns

    def h_iqns(self, h_iqns=None):
        """
        Usage
            obj.h_iqns()              #For querying
            obj.h_iqns(h_iqns)        #For setting
        Purpose

        Parameters
            @t_wwpns
        Returns
            List: h_iqns
                or
            None
        """
        # We are going to set h_wwpns
        if h_iqns:
            self._h_iqns = h_iqns

        # Does not matter if we set the list or just and to read it, we always return the list
        return self._h_iqns

    def t_iqns(self, t_iqns=None):
        """
        Usage
            obj.t_iqns()              #For querying
            obj.t_iqns(t_iqns)        #For setting
        Purpose

        Parameters
            t_iqns
        Returns
            List: t_iqns
                or
            None
        """
        # We are going to set t_iqns
        if t_iqns:
            self._t_iqns = t_iqns

        # Does not matter if we set the list or just and to read it, we always return the list
        return self._t_iqns

    def macs(self, macs=None):
        """
        Usage
            obj.macs()                #For querying
            obj.macs(macs)      #For setting
        Purpose

        Parameters
            macs
        Returns
            List: macs
                or
            None
        """
        macs = macs or []
        # We are going to set t_iqns
        if macs:
            self._macs = macs

        # Does not matter if we set the list or just and to read it, we always return the list
        return self._macs

    def map_info(self, map_info=None):
        """
        Usage
            obj.map_info()                    #For querying
            obj.map_info(map_info_list)       #For setting
        Purpose

        Parameters
            list with map info
        Returns
            List: map_info_list
                or
            None
        """
        # We are going to set t_iqns
        if map_info:
            self._map_info = map_info

        # Does not matter if we set the list or just and to read it, we always return the list
        return self._map_info

    def capability(self):
        if "capability" not in self.san_conf_dict:
            self.san_conf_dict["capability"] = {}

        return self.san_conf_dict["capability"]

    def sa_names(self):
        """
        Usage
            obj->sa_name()
        Purpose
            Query out the name for the storage array.
        Parameter
            N/A
        Returns
            List:   Storage Array names, most of the cases it will have just 1 element
        """
        if "sa_conf" in self.san_conf_dict:
            return list(self.san_conf_dict["sa_conf"].keys())
        return None

    def sw_names(self):
        """
        Usage
            obj->sw_name()
        Purpose
            Query out the name for the storage switch.
        Parameter
            N/A
        Returns
            List:   Storage switch names
        """
        if "sw_conf" in self.san_conf_dict:
            return list(self.san_conf_dict["sw_conf"].keys())
        return None

    def physw_names(self):
        """
        Usage
            obj->physw_name()
        Purpose
            Query out the name for the apcon storage switch.
        Parameter
            N/A
        Returns
            List:   Storage switch names
        """
        if "physw_conf" in self.san_conf_dict:
            return list(self.san_conf_dict["physw_conf"].keys())
        return None

    def get_sa_self(self):
        """
        Return the Storage Array configuration for this obj
        Return None if there is more than 1 array configured
        """

        sa_self = None
        if "sa_conf" in self.san_conf_dict:
            sa_self = self.san_conf_dict["sa_conf"]
        if not sa_self:
            print("FAIL: This server has no storage array configured for it")
            return None
        if len(list(sa_self.keys())) > 1:
            _print("FAIL: get_sa_self - san config has more then 1 array")
            print(list(sa_self.keys()))
            return None
        for key in sa_self:
            # we know there is only 1 entry. we return it
            return sa_self[key]

    def get_sa_obj_self(self):
        sa_val = self.get_sa_self()
        if not sa_val:
            _print("FAIL: get_sa_obj_self(): Could not find an storage array to use")
            return None

        if "class_obj" not in sa_val:
            _print("FAIL: get_sa_obj_self() - SanMgmt did not load Storage class")
            return None

        sa_obj = sa_val["class_obj"]
        return sa_obj

    def get_sw_self(self, port):
        """
        Return the Switch that has 'port' connected to it
        """
        switches_dict = None
        if "sw_conf" in self.san_conf_dict:
            switches_dict = self.san_conf_dict["sw_conf"]
        if not switches_dict:
            return None
        if not port:
            _print("FAIL: get_sw_self() - requires port parameter")
            return None

        orig_port = port
        port = self._addr_of(port)
        if not port:
            _print("FAIL: get_sw_self() - %s is an invalid WWPN/MAC/IQN" % orig_port)
            return None

        for sw in switches_dict:
            if "port_of" in switches_dict[sw] and port in switches_dict[sw]["port_of"]:
                return switches_dict[sw]
        return None

    def get_sw_capability(self, port):
        """
        Return the switch capability of the switch connected to given port
        """

        # Get the switch connected to this port
        connected_sw = self.get_sw_self(port)
        if not connected_sw:
            _print("FAIL: get_sw_capability(): No switch in configuration is "
                   + "controlling %s, even though it pass config check..." % port)
            return None

        sw_obj = connected_sw["class_obj"]

        return sw_obj.capability()

    def get_sw_name(self, port):
        """
        Return the switch name of the switch connected to given port
        """

        # Get the switch connected to this port
        connected_sw = self.get_sw_self(port)
        if not connected_sw:
            _print("FAIL: get_sw_name(): No switch in configuration is "
                   + "controlling %s, even though it pass config check..." % port)
            return None

        sw_name = connected_sw["name"]

        return sw_name

    def get_physw_self(self, port):
        """
        Return the physical Switch that has 'port' connected to it
        """
        switches_dict = None
        if "physw_conf" in self.san_conf_dict:
            switches_dict = self.san_conf_dict["physw_conf"]
        if not switches_dict:
            return None
        if not port:
            _print("FAIL: get_physw_self() - requires port parameter")
            return None

        for sw in list(switches_dict.keys()):
            if "port_of" in list(switches_dict[sw].keys()) and port in list(switches_dict[sw]["port_of"].keys()):
                return switches_dict[sw]
        return None

    def wwid_of_lun(self, lun_name):
        """
        Usage
            obj->wwid_of_lun(lun_name)
        Purpose
            Find out the WWID (vpd 0x83) of certain LUN.
            Some storage array(eg. LIO) might not provide this info.
        Parameter
            lun_name       # LUN name
        Returns
            wwid
        """
        if not lun_name:
            _print("FAIL: wwid_of_lun() - requires lun_name parameter")
            return None

        lun_info = self.lun_info(lun_name)
        if lun_info:
            if "wwid" in list(lun_info.keys()):
                return lun_info["wwid"]
        _print("INFO: wwid_of_lun() - LUN %s has no WWID" % lun_name)
        print(lun_info)
        return None

    def scsi_id_of_lun(self, lun_name=None, h_wwpn=None, t_wwpn=None, h_iqn=None, t_iqn=None):
        """
        Usage
            obj.scsi_id_of_lun(lun_name=lun_name)
            obj.scsi_id_of_lun(lun_name=lun_name, h_wwpn=h_wwpn,
                t_wwpn=>$t_wwpn)
        #we should not support this method since the qla4xxx iqn issue
        #    obj.scsi_id_of_lun(lun_name=lun_name, h_iqn=h_iqn,
                t_iqn=t_iqn)
            obj.scsi_id_of_lun(lun_name=lun_name, iface=iface,
                t_iqn=t_iqn, target_ip=target_ip)   # TODO
        Purpose
            To uniquly identify a SCSI ID, we can use these info:
            1. h_wwpn, t_wwpn, wwid  # wwid can be found via lun_name
            2. h_wwpn, t_wwpn, lun_id    # lun_id can be found via lun_name
            3. t_iqn, target_ip, iface   # TODO
            If less info provided in parameters, we will return all SCSI ID matches.
            Some storage array does not provide wwid of certain LUN, if so, we use
            lun_id, h_wwpn, t_wwpn to identify SCSI ID out.
        Parameter
            lun_name               # then name used inside of storage array
            h_wwpn                 # like '10:00:00:00:c9:95:2f:df'
            t_wwpn                 # like '50:0a:09:86:99:4b:8d:c5'
            h_iqn                  # the IQN used by iscsi initiator
            t_iqn                  # the IQN used by iscsi target
        Returns
            scsi_ids
                or
            None
        """
        if not lun_name:
            _print("FAIL: scsi_id_of_lun() - requires lun_name parameter")
            return False
        h_wwpns = []
        t_wwpns = []
        h_iqns = []
        t_iqns = []

        if h_wwpn:
            h_wwpn = libsan.host.fc.standardize_wwpn(h_wwpn)
            if h_wwpn:
                h_wwpns.append(h_wwpn)
        else:
            wwpns = self.h_wwpns()
            if wwpns:
                # h_wwpns = wwpns
                pass

        if t_wwpn:
            t_wwpn = libsan.host.fc.standardize_wwpn(t_wwpn)
            if t_wwpn:
                t_wwpns.append(t_wwpn)
        else:
            wwpns = self.t_wwpns()
            if wwpns:
                # t_wwpns = wwpns
                pass

        if h_iqn:
            h_iqns.append(h_iqn)
        else:
            iqns = self.h_iqns()
            if iqns:
                # h_iqns = iqns
                pass

        if t_iqn:
            t_iqns.append(t_iqn)
        else:
            iqns = self.t_iqns()
            if iqns:
                t_iqns.append(iqns)

        wwid = self.wwid_of_lun(lun_name)

        lun_scsi_ids = None
        # found_scsi_ids = None
        if wwid:
            _print("INFO: LUN %s has WWID %s" % (lun_name, wwid))
            lun_scsi_ids = libsan.host.scsi.scsi_ids_of_wwid(wwid)

        # Not sure why this code is needed
        # for h_wwpn in h_wwpns:
        # zoned_t_wwpns = fc.t_wwpn_of(h_wwpn)
        # for t_wwpn in t_wwpns:
        # if t_wwpn not in zoned_t_wwpns:
        # continue
        # target_id = fc.fc_target_id_of_htwwpn(t_wwpn = t_wwpn, h_wwpn = h_wwpn)
        # _print("FATAL: scsi_id_of_lun - TODO")
        # _print("DEBUG: LUN %s has the following scsi ids" % lun_name)
        # print lun_scsi_ids
        # for h_iqn in h_iqns:
        # for t_iqn in t_iqns:
        # _print("DEBUG: searching for scsi_ids from iSCSI session with %s %s" % (h_iqn, t_iqn))
        # ses_scsi_ids = iscsi.scsi_ids_of_iscsi_session(h_iqn = h_iqn, t_iqn = t_iqn)
        # if not ses_scsi_ids:
        # continue
        # _print("DEBUG: found scsi_ids from iSCSI session with %s %s" % (h_iqn, t_iqn))
        # print ses_scsi_ids
        # if lun_scsi_ids:
        # for l_id in lun_scsi_ids:
        # _print("DEBUG: checking if %s is on ses_ids" % l_id)
        # print ses_scsi_ids
        # if l_id in ses_scsi_ids:
        # if not found_scsi_ids:
        # found_scsi_ids = []
        # found_scsi_ids.append(l_id)
        # else:
        # _print("FATAL: scsi_id_of_lun - TODO")

        # if not found_scsi_ids:
        # _print("FAIL: scsi_id_of_lun(): No SCSI disk found on host for %s" % lun_name)
        # return None

        return lun_scsi_ids

    def lun_query(self):
        """
        Get all a list with all LUN names
        """
        capability = self.capability()
        if not capability or "lun_query" not in capability or not capability["lun_query"]:
            # Storage array does not support lun_query
            if "sa_conf" in self.san_conf_dict:
                _print("FAIL: lun_query(). SanMgmt can not perform command on:")
                print(self.san_conf_dict["sa_conf"])
                if capability:
                    print(capability)
            return None

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FATAL: lun_query(): Failed to sa_obj even though it pass capability check")
            return None
        return sa_obj.query_all_luns()

    def lun_info(self, lun_name):
        """
        Query details of specific LUN
        """
        if not lun_name:
            _print("FAIL: lun_info() - requires lun_name parameter")
            return None

        if not self.is_config_loaded():
            _print("FAIL: lun_info() - Please call obj->load_conf() first")
            return None

        capability = self.capability()
        if not capability or "lun_info" not in capability or not capability["lun_info"]:
            _print("FAIL: lun_info(). SanMgmt can not perform command on")
            if "sa_conf" in self.san_conf_dict:
                print(self.san_conf_dict["sa_conf"])
            if capability:
                print(capability)
            return None

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: lun_info(): Failed to sa_obj even though it pass capability check")
            return None
        return sa_obj.lun_info(lun_name)

    def lun_create(self, size=None, lun_name=None, thinp=None):
        """
        Usage
            obj.lun_create($size)
            obj.lun_create(size=>size)
            obj.lun_create(size=>size,lun_name=>lun_name)
            obj.lun_create(size=>size,lun_name=>lun_name, thinp=>flag_thinp)
        Purpose
            Create LUN with size named as lun_name. Please be informed this
            method DO NOT map LUN to any host, please call obj->lun_map() or
            obj->lun_create_and_map().
            If lun_name is undefined, we will let Storage Array control module
            to generate base on their own configuration:
            If flag_thinp is defined, will try not reserse all space it requested
            by using Thin-Provisioning technology. It need storage array report
            capability of "lun_thinp"
        Parameters
            size       # size, accept example: "1B", "1KiB", "2.1GiB", "3GiB", "2TiB"
            lun_name   # the LUN name on storage array. like:
                        #   /vol/vol_storageqe/storageqe_06-19
        Returns
            lun_name
                or
            None
        """
        if not size:
            _print("FAIL: lun_create requires size parameter")
            return None
        if not self.is_config_loaded():
            _print("FAIL: lun_create() - Please call obj->load_conf() first")
            return None

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: lun_create(): Failed to sa_obj even though it pass capability check")
            return None

        capability = sa_obj.capability()
        if not capability or "lun_create" not in capability or not capability["lun_create"]:
            _print("FAIL: lun_create(). SanMgmt can not perform command on")
            if "sa_conf" in self.san_conf_dict:
                print(self.san_conf_dict["sa_conf"])
            if capability:
                print(capability)
            return None

        sa_val = self.get_sa_self()
        if not sa_val:
            _print("FAIL: lun_create(): Failed to sa_self even though it pass capability check")
            return None

        sa_model = sa_val["model"]
        if thinp:
            if "lun_thinp" not in capability or not capability["lun_thinp"]:
                _print("FAIL: lun_create() - Thin Provisioning of LUN not supported on %s" % sa_model)
                return None

        if not libsan.misc.size.size_human_check(size):
            _print("FAIL: lun_create() - Incorrect format for size '%s'.")
            print("acceptable formats are: 5B, 1KiB, 2.1MiB, 3GiB, 4TiB")
            return None

        size_bytes = libsan.misc.size.size_human_2_size_bytes(size)
        if not size_bytes:
            _print("FAIL: lun_create() - LUN size should be > 1 byte")
            return None

        _print("DEBUG: Create LUN with size %s bytes" % size_bytes)

        # _print("DEBUG: Storage array version: %s" % sa_obj.get_version())
        if lun_name:
            if "lun_path" in sa_val:
                lun_name = "%s%s" % (sa_val["lun_path"], lun_name)
        else:
            lun_name = "tmp"
            # Check if prefix option is set on config file
            if "auto_lun_create_prefix" in sa_val:
                lun_name = sa_val["auto_lun_create_prefix"]
            lun_name += libsan.host.linux.time_stamp()

        return sa_obj.lun_create(lun_name, size_bytes)

    def lun_remove(self, lun_name):
        """
        Usage
            obj->lun_remove(lun_name)
        Purpose
            Delete LUN lun_name from storage array
        Parameters
            lun_name        # the LUN name on storage array.
        Returns
            True
                or
            False
        """
        if not lun_name:
            _print("FAIL: lun_remove - requires lun_name parameter")
            return None

        if not self.is_config_loaded():
            _print("FAIL: lun_map() - Please call obj->load_conf() first")
            return None

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: lun_remove(): Failed to sa_obj even though it pass capability check")
            return None

        capability = sa_obj.capability()
        if not capability or "lun_remove" not in capability or not capability["lun_remove"]:
            _print("FAIL: lun_remove(). SanMgmt can not perform command on")
            if "sa_conf" in self.san_conf_dict:
                print(self.san_conf_dict["sa_conf"])
            if capability:
                print(capability)
            return None

        sa_val = self.get_sa_self()
        if not sa_val:
            _print("FAIL: lun_remove(): Failed to sa_self even though it pass capability check")
            return None

        # If we are removing lun for Equallogic array, we need to delete the target
        # as each LUN is one target...
        model = sa_val["model"]
        if model == "DELL-EQLOGIC":
            info_dict = self.lun_info(lun_name)
            t_iqns = libsan.host.iscsi.t_iqn_of_sessions()
            if info_dict and t_iqns:
                if info_dict["iscsi_name"] in t_iqns:
                    libsan.host.iscsi.node_logout("-T %s" % info_dict["iscsi_name"])
                if libsan.host.iscsi.is_target_discovered(info_dict["iscsi_name"]):
                    libsan.host.iscsi.node_delete("-T %s" % info_dict["iscsi_name"])

        # sometimes the removal can fail, specially if there is IO being execute there
        # try it few times
        attempt = 5
        while attempt > 0:
            if sa_obj.lun_remove(lun_name):
                return True
            libsan.host.linux.sleep(1)
            attempt -= 1
        _print("FAIL: Could not delete lun %s" % lun_name)
        return False

    def lun_map(self, lun_name, t_addr=None, i_addr=None, lun_id=None, rescan=False):
        """
        Usage
            obj->lun_map(lun_name, init_names)
            obj->lun_map(lun_name, init_names, rescan=>$flag_rescan)
        Purpose
            Map LUN lun_name to host initiator
        Parameters
            lun_name        # the LUN name on storage array.
            lun_id          # the LUN ID host should get
            $flag_rescan
        Returns
            True
                or
            False
        """
        if lun_id:
            pass

        if not lun_name:
            _print("FAIL: lun_map - requires lun_name and init_names parameters")
            return False

        if not self.is_config_loaded():
            _print("FAIL: lun_map() - Please call obj->load_conf() first")
            return False

        capability = self.capability()
        if not capability or "lun_map" not in capability or not capability["lun_map"]:
            _print("FAIL: lun_map(). SanMgmt can not perform command on")
            if "sa_conf" in self.san_conf_dict:
                print(self.san_conf_dict["sa_conf"])
            if capability:
                print(capability)
            return False

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: lun_map(): Failed to sa_obj even though it pass capability check")
            return None

        map_info = self.map_info()
        # There is no map info, probably because self was not created based on existing mpath device
        if not map_info or t_addr or i_addr:
            # If there is no mapping given we will try to map
            # every host to all targets, unless some target or initiator address is given
            map_info = []
            t_wwpns = self.t_wwpns()
            h_wwpns = self.h_wwpns()
            t_iqns = self.t_iqns()
            h_iqns = self.h_iqns()
            if t_addr:
                if libsan.host.fc.is_wwn(t_addr):
                    t_wwpns = [t_addr]
                elif libsan.host.iscsi.is_iqn(t_addr):
                    t_iqns = [t_addr]
                else:
                    _print("FAIL: lun_map() - Unsupported t_addr %s" % t_addr)
                    return False

            if i_addr:
                if libsan.host.fc.is_wwn(i_addr):
                    h_wwpns = [i_addr]
                elif libsan.host.iscsi.is_iqn(i_addr):
                    h_iqns = [i_addr]
                else:
                    _print("FAIL: lun_map() - Unsupported i_addr %s" % i_addr)
                    return False

            for t_wwpn in t_wwpns:
                for h_wwpn in h_wwpns:
                    map_info.append({"t_wwpn": t_wwpn, "h_wwpn": h_wwpn})
            for t_iqn in t_iqns:
                for h_iqn in h_iqns:
                    map_info.append({"t_iqn": t_iqn, "h_iqn": h_iqn})

        sa_obj.map_info = map_info
        if not sa_obj.lun_map(lun_name):
            return False

        # We only do this for iSCSI
        obj_t_iqns = self.t_iqns()
        obj_h_iqns = self.h_iqns()
        if obj_t_iqns and obj_h_iqns:
            # Equallogic creates new targets per each LUN
            # We need to discover this new target...
            info_dict = self.lun_info(lun_name)
            if not info_dict:
                _print("FAIL: lun_map() - Could not get info of lun %s" % lun_name)
                return False

            if "iscsi_name" in list(info_dict.keys()):
                new_t_iqn = info_dict["iscsi_name"]
                if not libsan.host.iscsi.is_target_discovered(new_t_iqn):
                    # We discover target using the same interface used on original target
                    disc_ifaces = libsan.host.iscsi.get_disc_ifaces_of_t_iqn(obj_t_iqns[0])
                    if not disc_ifaces:
                        _print(
                            "FAIL: lun_map() - Can not map %s because we could not find the interfaces used to connect "
                            "to original target %s"
                            % (new_t_iqn, obj_t_iqns[0]))
                        return False
                    ifaces = " ".join(disc_ifaces)
                    sa_val = self.get_sa_self()
                    if not sa_val:
                        _print("FAIL: lun_map(): Failed to sa_self even though it pass capability check")
                        return None
                    if "portal_ip" in list(sa_val.keys()):
                        if not libsan.host.iscsi.discovery_st(sa_val["portal_ip"], ifaces):
                            _print("FAIL: Could not discover iSCSI target after mapping new LUN")
                            return False
                    else:
                        # if portal_ip is not set try to connect using management address
                        if not libsan.host.iscsi.discovery_st(sa_val["ctrl_ip"], ifaces):
                            _print("FAIL: Could not discover iSCSI target after mapping new LUN")
                            return False
                if info_dict["iscsi_name"] not in libsan.host.iscsi.t_iqn_of_sessions():
                    if not libsan.host.iscsi.node_login("-T %s" % info_dict["iscsi_name"]):
                        _print("FAIL: Could not discover iSCSI target after mapping new LUN")
                        return False

        if rescan:
            hosts = libsan.host.scsi.get_hosts()
            for host in hosts:
                libsan.host.scsi.rescan_host(host)
            libsan.host.linux.wait_udev()

        return True

    def lun_unmap(self, lun_name, t_addr=None, i_addr=None, lun_id=None):
        """
        Usage
            obj->lun_unmap(lun_name, init_names)
            obj->lun_unmap(lun_name, init_names)
        Purpose
            Map LUN lun_name to host initiator
        Parameters
            lun_name        # the LUN name on storage array.
            lun_id          # the LUN ID host should get
            $flag_rescan
        Returns
            True
                or
            False
        """
        if lun_id:
            pass

        if not lun_name:
            _print("FAIL: lun_unmap - requires lun_name and init_names parameters")
            return False

        if not self.is_config_loaded():
            _print("FAIL: lun_unmap() - Please call obj->load_conf() first")
            return False

        capability = self.capability()
        if not capability or "lun_unmap" not in capability or not capability["lun_unmap"]:
            _print("FAIL: lun_unmap(). SanMgmt can not perform command on")
            if "sa_conf" in self.san_conf_dict:
                print(self.san_conf_dict["sa_conf"])
            if capability:
                print(capability)
            return False

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: lun_unmap(): Failed to sa_obj even though it pass capability check")
            return None

        map_info = self.map_info()
        # There is no map info, probably because self was not created based on existing mpath device
        if not map_info or t_addr or i_addr:
            # If there is no mapping given we will try to map
            # every host to all targets, unless some target or initiator address is given
            map_info = []
            t_wwpns = self.t_wwpns()
            h_wwpns = self.h_wwpns()
            t_iqns = self.t_iqns()
            h_iqns = self.h_iqns()
            if t_addr:
                if libsan.host.fc.is_wwn(t_addr):
                    t_wwpns = [t_addr]
                elif libsan.host.iscsi.is_iqn(t_addr):
                    t_iqns = [t_addr]
                else:
                    _print("FAIL: lun_unmap() - Unsupported t_addr %s" % t_addr)
                    return False

            if i_addr:
                if libsan.host.fc.is_wwn(i_addr):
                    h_wwpns = [i_addr]
                elif libsan.host.iscsi.is_iqn(i_addr):
                    h_iqns = [i_addr]
                else:
                    _print("FAIL: lun_unmap() - Unsupported i_addr %s" % i_addr)
                    return False

            for t_wwpn in t_wwpns:
                for h_wwpn in h_wwpns:
                    map_info.append({"t_wwpn": t_wwpn, "h_wwpn": h_wwpn})
            for t_iqn in t_iqns:
                for h_iqn in h_iqns:
                    map_info.append({"t_iqn": t_iqn, "h_iqn": h_iqn})

        sa_obj.map_info = map_info
        if not sa_obj.lun_unmap(lun_name):
            return False

        # If we are removing lun for Equallogic array, we need to delete the target
        # as each LUN is one target...
        sa_val = self.get_sa_self()
        if not sa_val:
            _print("FAIL: lun_unmap(): Failed to sa_self even though it pass capability check")
            return None
        model = sa_val["model"]
        if model == "DELL-EQLOGIC":
            info_dict = self.lun_info(lun_name)
            if info_dict:
                if info_dict["iscsi_name"] in libsan.host.iscsi.t_iqn_of_sessions():
                    libsan.host.iscsi.node_logout("-T %s" % info_dict["iscsi_name"])
                if libsan.host.iscsi.is_target_discovered(info_dict["iscsi_name"]):
                    libsan.host.iscsi.node_delete("-T %s" % info_dict["iscsi_name"])

        return True

    def lun_create_and_map(self, size=None, lun_name=None, rescan=None):
        """
        Usage
            obj.lun_create_and_map(size, init_names)
            obj.lun_create_and_map(size=size,lun_name=lun_name, init_name=ini_names)
            obj.lun_create_and_map(size=size,init_names=init_names)
            obj.lun_create_and_map(size=size,rescan=flag_rescan)
        Purpose
            Just automatically call lun_create() and lun_map(). If you want to
            rescan after creation, enable flag_rescan.
        Parameters
            size
            lun_name       # optional.
            lun_id         # optional.
            flag_rescan
        Returns
            lun_name
                or
            undef
        """

        lun_name = self.lun_create(size=size, lun_name=lun_name)
        if not lun_name:
            _print("FAIL: lun_create_and_map(): Skip mapping since LUN creation failed")
            return None
        if not self.lun_map(lun_name, rescan=rescan):
            _print("FAIL: lun_create_and_map - Could not map %s" % lun_name)
            _print("INFO: Deleting just created LUN")
            self.lun_remove(lun_name)
            return None
        return lun_name

    def get_controller_names(self):
        """
        """
        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: get_controller_names(): Failed to sa_obj even though it pass capability check")
            return None

        sa_conf_dict = sa_obj.get_sa_conf()

        if not sa_conf_dict:
            _print("FAIL: get_controller_names() - Controller is not configured on san_top config")
            return None

        ctrler_names = []
        ctrler_name_regex = re.compile("ctrl_ip_(.*)")
        for key in list(sa_conf_dict.keys()):
            m = ctrler_name_regex.match(key)
            if m:
                ctrler_names.append(m.group(1))
        return ctrler_names

    def sa_t_wwpn_2_ctrler(self):
        """

        """
        ctrlers = self.get_controller_names()
        if not ctrlers:
            return None

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: sa_t_wwpn_2_ctrler(): Failed to sa_obj for Storage Array")
            return None

        sa_conf_dict = sa_obj.get_sa_conf()

        sa_t_wwpn_2_ctrler = {}
        for ctrler in ctrlers:
            cfg_ctrl_name = "ctrl_ip_%s" % ctrler
            ctrler_ip = sa_conf_dict[cfg_ctrl_name]
            sa_t_wwpn_2_ctrler[ctrler] = sa_obj.sa_ctrler_t_wwpns(ctrler_ip)

        return sa_t_wwpn_2_ctrler

    def get_controller_ip_of_port(self, t_addr):
        """
        From a given port gets the controller IP address that uses it
        This information is from san_top config file
        """
        if not t_addr:
            _print("FAIL: get_controller_ip_of_port() - requires controller_port as parameter")
            return None

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: get_controller_ip_of_port(): Failed to sa_obj even though it pass capability check")
            return None

        sa_conf_dict = sa_obj.get_sa_conf()

        if "port_of" in sa_conf_dict and t_addr in list(sa_conf_dict["port_of"].keys()):
            ctrler_port = sa_obj.sa_conf_dict["port_of"][t_addr]
            # spa-fc1 becomes spa
            ctrler_name = re.sub("-.*", "", ctrler_port)
            cfg_ctrl_name = "ctrl_ip_%s" % ctrler_name
            if cfg_ctrl_name not in sa_conf_dict:
                _print("FAIL: sa_ctrler_check() - %s is not defined on config file" % cfg_ctrl_name)
                if "sa_conf" in self.san_conf_dict:
                    print(self.san_conf_dict["sa_conf"])
                return None
            ctrler_ip = sa_conf_dict[cfg_ctrl_name]
            return ctrler_ip
        return None

    def sa_ctrler_reboot(self, t_addr):
        """
        Usage
            obj->sa_ctrler_reboot(t_addr)
        Purpose
            Reboot controller with given wwwpn/iqn
        Parameters
            t_addr          # Controller WWPN or IQN
        Returns
            True
                or
            False
        """
        if not t_addr:
            _print("FAIL: sa_ctrler_reboot() - requires t_addr parameters")
            return False

        if not self.is_config_loaded():
            _print("FAIL: sa_ctrler_reboot() - Please call obj->load_conf() first")
            return False

        capability = self.capability()
        if not capability or "sa_ctrler_reboot" not in capability or not capability["sa_ctrler_reboot"]:
            _print("FAIL: sa_ctrler_reboot(). SanMgmt can not perform command on")
            if "sa_conf" in self.san_conf_dict:
                print(self.san_conf_dict["sa_conf"])
            if capability:
                print(capability)
            return False

        ctrler_ip = self.get_controller_ip_of_port(t_addr)
        if not ctrler_ip:
            _print("FAIL: sa_ctrler_reboot() - Could not find controller IP for port %s" % t_addr)
            return False

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: sa_ctrler_reboot(): Failed to sa_obj even though it pass capability check")
            return None

        if not sa_obj.sa_ctrler_reboot(ctrler_ip):
            return False
        return True

    def sa_ctrler_check(self, t_addr):
        """
        Usage
            obj->sa_ctrler_check(t_addr)
        Purpose
            Check controller with given wwwpn/iqn
        Parameters
            t_addr          # Controller WWPN or IQN
        Returns
            True
                or
            False
        """
        if not t_addr:
            _print("FAIL: sa_ctrler_check() - requires t_addr parameters")
            return None

        if not self.is_config_loaded():
            _print("FAIL: sa_ctrler_check() - Please call obj->load_conf() first")
            return None

        capability = self.capability()
        if not capability or "sa_ctrler_reboot" not in capability or not capability["sa_ctrler_reboot"]:
            _print("FAIL: sa_ctrler_check(). SanMgmt can not perform sa_ctrler_reboot, so do not allow ctrler_check")
            if "sa_conf" in self.san_conf_dict:
                print(self.san_conf_dict["sa_conf"])
            if capability:
                print(capability)
            return None

        sa_obj = self.get_sa_obj_self()
        if not sa_obj:
            _print("FAIL: sa_ctrler_check(): Failed to sa_obj even though it pass capability check")
            return None

        ctrler_ip = self.get_controller_ip_of_port(t_addr)
        if not ctrler_ip:
            _print("FAIL: sa_ctrler_check() - Could not find controller IP for port %s" % t_addr)
            return None

        return sa_obj.sa_ctrler_check(ctrler_ip)

    def sa_ctrler_wait(self, t_addr, timeout=1800, interval=30):
        """
        Usage
            obj->sa_ctrler_wait(t_addr)
        Purpose
            Wait for specific controller to be online
        Parameters
            t_addr          # Controller WWPN or IQN
        Returns
            True
                or
            False
        """
        if not t_addr:
            _print("FAIL: sa_ctrler_wait() - requires t_addr parameters")
            return False

        if not self.is_config_loaded():
            _print("FAIL: sa_ctrler_wait() - Please call obj->load_conf() first")
            return False

        capability = self.capability()
        if not capability or "sa_ctrler_reboot" not in capability or not capability["sa_ctrler_reboot"]:
            _print("FAIL: sa_ctrler_wait(). SanMgmt can not perform sa_ctrler_reboot, so do not allow sa_ctrler_wait")
            if "sa_conf" in self.san_conf_dict:
                print(self.san_conf_dict["sa_conf"])
            if capability:
                print(capability)
            return False

        ctrler_ip = self.get_controller_ip_of_port(t_addr)
        if not ctrler_ip:
            _print("FAIL: sa_ctrler_wait() - Could not find controller IP for port %s" % t_addr)
            if "sa_conf" in self.san_conf_dict:
                print(self.san_conf_dict["sa_conf"])
            return False

        loop_count = int(timeout / interval)
        while loop_count > 1:
            loop_count -= 1
            status = self.sa_ctrler_check(t_addr)
            if not status:
                _print("FAIL: sa_ctrler_wait() - Could not get status of controller %s" % ctrler_ip)
                return False
            if status == "online":
                return True
            _print("INFO: Controller still on status: %s (loop_count: %s)" % (status, loop_count))
            libsan.host.linux.sleep(interval)

        _print("FAIL: sa_ctrler_wait(): Timeout, controller %s still offline" % ctrler_ip)
        return False

    def iscsi_host_conf(self):
        """
        Based on hostname information get host iSCSI configuration
        """
        if not self.is_config_loaded():
            self.load_conf()

        if not self.is_config_loaded():
            _print("FAIL: iscsi_host_conf() - Config file was not loaded")
            return None

        host = libsan.host.linux.hostname()

        iscsi_conf_dict = None
        if "iscsi_conf" in self.san_conf_dict:
            iscsi_conf_dict = self.san_conf_dict["iscsi_conf"]["hosts"]

        if not iscsi_conf_dict:
            # _print("DEBUG: iscsi_host_conf() - no iSCSI host settings on san_conf_file")
            # print self.san_conf_dict.keys()
            return None

        if host not in list(iscsi_conf_dict.keys()):
            # _print("DEBUG: iscsi_host_conf() - there is no iSCSI settings for "
            #    + "%s on san_conf_file" % host)
            # print iscsi_conf_dict
            return None

        libsan.host.iscsi.install()

        host_iscsi_ifaces = libsan.host.iscsi.get_iscsi_iface_names()
        if not host_iscsi_ifaces:
            _print("FAIL: iscsi_host_conf() - Host does not have iSCSI interface")
            return None

        host_conf = iscsi_conf_dict[host]
        iface_name_ipv4_suffix = ".ipv4.0"
        # iface_name_ipv6_suffix = ".ipv6.0"
        for iface in list(host_conf["ifaces"].keys()):
            found_iface = False
            # iscsiadm might append IP version to interface name, we update server config to reflect it
            if "name" in list(host_conf["ifaces"][iface].keys()):
                iface_name = host_conf["ifaces"][iface]["name"]
                # Check if host has this interface
                for host_iface in host_iscsi_ifaces:
                    if iface_name == host_iface:
                        found_iface = True
                        break
                    ipv4_iface = "%s%s" % (iface_name, iface_name_ipv4_suffix)
                    if ipv4_iface == host_iface:
                        found_iface = True
                        host_conf["ifaces"][iface]["name"] = host_iface
                        break

                if not found_iface:
                    _print(
                        "FAIL: iscsi_host_conf() -%s is configured on san_top, but does not exist on host" % iface_name)
                    return None

        return host_conf

    def setup_iscsi(self):
        """
        Usage
            obj.setup_iscsi()
        Purpose
            Setup iSCSI Host base on san_conf
        Parameter
            san_conf     # conf file path
        Returns
            scsi_ids   # the iSCSI disks found
                or
            None
        """
        host_conf = self.iscsi_host_conf()
        if not host_conf:
            return False

        if "ifaces" not in list(host_conf.keys()):
            _print("FAIL: setup_iscsi() - there is no iSCSI iface defined on config file for host")
            print(host_conf)
            return False

        # Lowering iscsid timeout for sessions using multipath
        libsan.host.iscsi.multipath_timeo()

        success = True

        for iface in list(host_conf["ifaces"].keys()):
            iface_name = "default"
            portal = None
            iqn = None
            iface_ip = None
            subnet_mask = None
            gateway = None

            if "name" in list(host_conf["ifaces"][iface].keys()):
                iface_name = host_conf["ifaces"][iface]["name"]
            if "target_ip" in list(host_conf["ifaces"][iface].keys()):
                portal = host_conf["ifaces"][iface]["target_ip"]
            if "iqn" in list(host_conf["ifaces"][iface].keys()):
                iqn = host_conf["ifaces"][iface]["iqn"]
            if "ip" in list(host_conf["ifaces"][iface].keys()):
                iface_ip = host_conf["ifaces"][iface]["ip"]
            if "mask" in list(host_conf["ifaces"][iface].keys()):
                subnet_mask = host_conf["ifaces"][iface]["mask"]
            if "gateway" in list(host_conf["ifaces"][iface].keys()):
                gateway = host_conf["ifaces"][iface]["gateway"]

            if not iface_name or not portal or not iqn:
                _print(
                    "FAIL: setup_iscsi() - interface %s requires iface_name, portal and iqn info to be set "
                    "on config file" % iface)
                print(host_conf["ifaces"][iface])
                success = False
                continue

            if iface_ip:
                if not libsan.host.iscsi.iface_set_ip(iface_name, iface_ip, subnet_mask, gateway):
                    _print("FAIL: setup_iscsi() - Could not set IP for %s" % iface_name)
                    success = False
                    continue
            if not libsan.host.iscsi.iface_set_iqn(iqn, iface_name):
                _print("FAIL: setup_iscsi() - Could not set %s to iface %s" % (iqn, iface_name))
                success = False
                continue
            if not libsan.host.iscsi.discovery_st(portal, ifaces=iface_name, disc_db=True):
                _print(
                    "FAIL: setup_iscsi() - Could not discover any target on %s using iface %s" % (portal, iface_name))
                success = False
                continue
            if not libsan.host.iscsi.node_login():
                _print("FAIL: setup_iscsi() - Could not login to new discovered portals")
                success = False
                continue
            print("INFO: %s logged in successtully to %s" % (iface_name, portal))

        if success:
            return True
        return False

    @staticmethod
    def _addr_of(addr):
        """
        """
        if libsan.host.fc.standardize_wwpn(addr):
            return libsan.host.fc.standardize_wwpn(addr)
        if libsan.host.net.standardize_mac(addr):
            return libsan.host.net.standardize_mac(addr)
        if libsan.host.iscsi.is_iqn(addr):
            return addr
        _print("FAIL: %s is neither a valid WWPN/MAC address." % addr)
        return None

    def rcsn_trigger(self, action=None, wwpn=None, addr=None):
        """
        Usage
            obj.rcsn_trigger(action=action, addr=wwpn)
            obj.rcsn_trigger(action=action, addr=mac)
        Purpose
            Enable/Disable RCSN messages to be sent on this port
        Parameters
            action     # "ENABLE"   disable rcsn suppression or
                       # "DISABLE"  enable rcsn suppression
            addr       # MAC address or WWPN address
        Returns
            True
                or
            False
        """
        if wwpn:
            addr = wwpn

        if not addr or not action:
            _print("FAIL: link_trigger() - requires action and addr parameters")
            return False

        if not self.is_config_loaded():
            _print("FAIL: link_trigger() - Please call obj->load_conf() first")
            return False

        # make sure action is always uppercase
        action = action.upper()

        need_capability = None
        if action == "ENABLE":
            need_capability = "rcsn_enable"
        if action == "DISABLE":
            need_capability = "rcsn_disable"
        if not need_capability:
            _print("FAIL: rcsn_trigger() - Unsupported action: %s" % action)
            return False

        # Get the switch connected to this port
        connected_sw = self.get_sw_self(addr)
        if not connected_sw:
            _print("FAIL: rcsn_trigger(): No switch in configuration is "
                   + "controlling %s, even though it pass config check..." % addr)
            return False

        sw_obj = connected_sw["class_obj"]

        if need_capability not in sw_obj.capability():
            _print("FAIL: rcsn_trigger() - Switch does not support %s" % need_capability)
            print(connected_sw)
            return False

        if "port_of" in connected_sw and addr in connected_sw["port_of"]:
            return sw_obj.rcsn_trigger(action=action, port_id=connected_sw["port_of"][addr])

        _print("FAIL: rcsn_trigger() - Could not find which interface port %s is connected to" % addr)
        return False

    def rcsn_enable(self, addr):
        return self.rcsn_trigger(action="ENABLE", addr=addr)

    def rcsn_disable(self, addr):
        return self.rcsn_trigger(action="DISABLE", addr=addr)

    def link_trigger(self, action=None, wwpn=None, addr=None, check_state=True):
        """
        Usage
            obj.link_trigger(action=action, addr=wwpn, check_state=True)
            obj.link_trigger(action=action, addr=mac, check_state=True)
        Purpose
            Bring switch port UP or DOWN which connected to $wwpn.
        Parameters
            action     # "UP" or "DOWN"
            addr       # MAC address or WWPN address
        Returns
            True
                or
            False
        """
        if wwpn:
            addr = wwpn

        if not addr or not action:
            _print("FAIL: link_trigger() - requires action and addr parameters")
            return False

        if not self.is_config_loaded():
            _print("FAIL: link_trigger() - Please call obj->load_conf() first")
            return False

        # make sure action is always uppercase
        action = action.upper()

        # capability = self.capability()
        need_capability = None
        if action == "UP":
            need_capability = "link_up"
        if action == "DOWN":
            need_capability = "link_down"
        if not need_capability:
            _print("FAIL: link_trigger() - Unsupported action: %s" % action)
            return False

        # Get the switch connected to this port
        connected_sw = self.get_sw_self(addr)
        if not connected_sw:
            _print("FAIL: link_trigger(): No switch in configuration is "
                   + "controlling %s, even though it pass config check..." % addr)
            return False

        sw_obj = connected_sw["class_obj"]

        if need_capability not in sw_obj.capability():
            _print("FAIL: link_trigger() - Switch does not support %s" % need_capability)
            print(connected_sw)
            return False

        if "port_of" in connected_sw and addr in connected_sw["port_of"]:
            return sw_obj.link_trigger(action=action,
                                       port_id=connected_sw["port_of"][addr],
                                       check_state=check_state)

        _print("FAIL: link_trigger() - Could not find which interface port %s is connected to" % addr)
        return False

    def link_up(self, addr, check_state=True):
        return self.link_trigger(action="UP", addr=addr, check_state=check_state)

    def link_down(self, addr, check_state=True):
        return self.link_trigger(action="DOWN", addr=addr, check_state=check_state)

    def link_oscillate(self, addr, min_uptime=1, max_uptime=1, min_downtime=1,
                       max_downtime=1, count=100):
        """
        Usage
            obj.link_oscillate(addr, min_uptime, max_uptime, min_downtime, max_downtime, count)
        Purpose
            Oscilate link on a port. This method bring switch port up and down on specific interval.
        Parameters
            addr           # WWPN or MAC address
            min_uptime     # minimum time in second with the link up
            max_uptime     # maximum time in second with the link up
            min_downtime   # minimum time in second with the link down
            max_downtime   # maximum time in second with the link down
            count          # how many times should we oscillate the link. like '10'
        Returns
            True
                or
            False
        """
        if not addr:
            _print("FAIL: link_oscillate() - requires addr parameter")
            return False

        if not self.is_config_loaded():
            _print("FAIL: link_oscillate() - Please call obj->load_conf() first")
            return False

        # Get the switch connected to this port
        connected_sw = self.get_sw_self(addr)
        if not connected_sw:
            _print("FAIL: link_oscillate(): No switch in configuration is "
                   + "controlling %s" % addr)
            return False

        sw_obj = connected_sw["class_obj"]

        capability = sw_obj.capability()
        need_capability = "link_oscillate"
        flag_capability_pass = False
        if need_capability in list(capability.keys()):
            flag_capability_pass = True
        if not flag_capability_pass:
            _print("FAIL: link_oscillate() - Is not possible to execute %s on port %s" % (need_capability, addr))
            print(capability)
            return False

        _print("INFO: Going to start link oscillate on switch:")
        _print("\tmin uptime: %s" % min_uptime)
        _print("\tmax uptime: %s" % max_uptime)
        _print("\tmin downtime: %s" % min_downtime)
        _print("\tmax downtime: %s" % max_downtime)
        _print("\tcount: %s" % count)
        port_id = connected_sw["port_of"][addr]
        return sw_obj.port_oscillate(port_id, min_uptime, max_uptime,
                                     min_downtime, max_downtime, count)

    def port_state(self, addr):
        """
        Check switch port state on of a WWPN/MAC
        """
        # Get the switch connected to this port
        connected_sw = self.get_sw_self(addr)
        if not connected_sw:
            _print("FAIL: port_state(): No switch in configuration is "
                   + "controlling %s, even though it pass capability check..." % addr)
            return None

        sw_obj = connected_sw["class_obj"]
        if "port_of" in connected_sw and addr in connected_sw["port_of"]:
            return sw_obj.port_state(connected_sw["port_of"][addr])

        _print("FAIL: port_state() - Could not find which interface port %s is connected to" % addr)
        return None

    def phy_link_trigger(self, action=None, addr=None, check_state=True):
        """
        Usage
            obj.phy_link_trigger(action=>$action, addr=>wwpn)
            obj.phy_link_trigger(action=>$action, addr=>mac)
        Purpose
            Bring physical switch port UP or DOWN which connected to addr.
        Parameters
            action     # "UP" or "DOWN"
            addr       # Port ID
        Returns
            True
                or
            False
        """
        if not addr or not action:
            _print("FAIL: phy_link_trigger() - requires action and addr parameters")
            return False

        if not self.is_config_loaded():
            _print("FAIL: phy_link_trigger() - Please call obj->load_conf() first")
            return False

        # make sure action is always uppercase
        action = action.upper()
        capability = self.capability()
        need_capability = None
        if action == "UP":
            need_capability = "phy_port_connect"
        if action == "DOWN":
            need_capability = "phy_port_disconnect"
        if not need_capability:
            _print("FAIL: phy_link_trigger() - Unsupported action: %s" % action)
            return False

        flag_capability_pass = False
        if need_capability in list(capability.keys()):
            if addr in capability[need_capability]:
                flag_capability_pass = True
        if not flag_capability_pass:
            _print("FAIL: phy_link_trigger() - Is not possible to execute %s on port %s" % (need_capability, addr))
            print(capability)
            return False

        # Get the switch connected to this port
        connected_sw = self.get_physw_self(addr)
        if not connected_sw:
            _print("FAIL: phy_link_trigger(): No switch in configuration is "
                   + "controlling %s, even though it pass capability check..." % addr)
            return False

        sw_obj = connected_sw["class_obj"]
        if "port_of" in list(connected_sw.keys()) and addr in connected_sw["port_of"]:
            port_id = connected_sw["port_of"][addr]
            status = sw_obj.port_status(port_id)
            if not status:
                _print("FAIL: phy_link_trigger() - Could not get status of port %s" % status)
                return False
            if status != "Active":
                _print("FAIL: phy_link_trigger() - port %s has status %s, expected to be Active" % (port_id, status))
                return False

            if action == "DOWN":
                return sw_obj.port_disconnect(port_id, check_state=check_state)
            if action == "UP":
                if "simplex_con" in connected_sw:
                    if port_id in connected_sw["simplex_con"]:
                        dst_port = connected_sw["simplex_con"][port_id]
                        return sw_obj.port_connect(port_id, dst_port, "simplex",
                                                   check_state=check_state)
                if "duplex_con" in connected_sw:
                    if port_id in connected_sw["duplex_con"]:
                        dst_port = connected_sw["duplex_con"][port_id]
                        return sw_obj.port_connect(port_id, dst_port, "duplex",
                                                   check_state=check_state)

        _print("FAIL: phy_link_trigger() - Could not find which interface port %s is connected to" % addr)
        return False

    def phy_port_state(self, addr):
        """
        Check switch port state on of a WWPN/MAC
        """
        connected_sw = self.get_physw_self(addr)
        if not connected_sw:
            _print("FAIL: phy_port_state(): No switch in configuration is "
                   + "controlling %s, even though it pass capability check..." % addr)
            return None

        sw_obj = connected_sw["class_obj"]
        if "port_of" in connected_sw and addr in connected_sw["port_of"]:
            port_id = connected_sw["port_of"][addr]
            return sw_obj.connect_mode_of(port_id)
        return None

    def phy_link_oscillate(self, addr, min_uptime=1, max_uptime=1, min_downtime=1,
                           max_downtime=1, count=100):
        """
        Usage
            obj.phy_link_oscillate(addr, min_uptime, max_uptime, min_downtime, max_downtime, count)
        Purpose
            Oscilate a port. This method will bring phy switch down/up for count number of times.
        Parameters
            addr           # WWPN or MAC address
            min_uptime     # minimum time in second with the link up
            max_uptime     # maximum time in second with the link up
            min_downtime   # minimum time in second with the link down
            max_downtime   # maximum time in second with the link down
            count          # how many times should we oscillate the port. like '10'
        Returns
            True
                or
            False
        """
        if not addr:
            _print("FAIL: phy_link_oscillate() - requires addr parameter")
            return False

        if not self.is_config_loaded():
            _print("FAIL: phy_link_oscillate() - Please call obj->load_conf() first")
            return False

        capability = self.capability()
        need_capability = "phy_port_oscillate"
        flag_capability_pass = False
        if need_capability in list(capability.keys()):
            if addr in capability[need_capability]:
                flag_capability_pass = True
        if not flag_capability_pass:
            _print("FAIL: phy_link_oscillate() - Is not possible to execute %s on port %s" % (need_capability, addr))
            print(capability)
            return False

        # Get the switch connected to this port
        connected_sw = self.get_physw_self(addr)
        if not connected_sw:
            _print("FAIL: phy_link_oscillate(): No switch in configuration is "
                   + "controlling %s, even though it pass capability check..." % addr)
            return False
        _print("INFO: Going to start link oscillate on phy switch:")
        _print("\tmin uptime: %s" % min_uptime)
        _print("\tmax uptime: %s" % max_uptime)
        _print("\tmin downtime: %s" % min_downtime)
        _print("\tmax downtime: %s" % max_downtime)
        _print("\tcount: %s" % count)
        sw_obj = connected_sw["class_obj"]
        port_id = connected_sw["port_of"][addr]
        if "simplex_con" in list(connected_sw.keys()):
            if port_id in list(connected_sw["simplex_con"].keys()):
                dst_port = connected_sw["simplex_con"][port_id]
                return sw_obj.port_oscillate(port_id, dst_port, "simplex",
                                             min_uptime, max_uptime, min_downtime,
                                             max_downtime, count)
        if "duplex_con" in list(connected_sw.keys()):
            if port_id in list(connected_sw["duplex_con"].keys()):
                dst_port = connected_sw["duplex_con"][port_id]
                return sw_obj.port_oscillate(port_id, dst_port, "duplex",
                                             min_uptime, max_uptime, min_downtime,
                                             max_downtime, count)
        _print("FAIL: phy_link_oscillate() - Could not find which interface port %s is connected to" % addr)
        return False

    def phy_link_flap(self, addr, uptime, downtime, count):
        """
        Usage
            obj.phy_link_flap(addr, uptime, downtime, count)
        Purpose
            Flap a port. This method will wait until flap done.
            Some physical switch model (e.g. ApCon) has maximum time limited, they will
            be wraped down to maximum value.
        Parameters
            addr           # WWPN or MAC address
            uptime         # time to keep link up during flap in micro seconds
            downtime       # time to keep link down during flap in micro seconds
            count          # how many times should we flap the port. like '10'
        Returns
            True
                or
            False
        """
        if not addr or not uptime or not downtime or not count:
            _print("FAIL: phy_link_flap() - requires addr, uptime, downtime and count parameters")
            return False

        if not self.is_config_loaded():
            _print("FAIL: phy_link_flap() - Please call obj->load_conf() first")
            return False

        capability = self.capability()
        need_capability = "phy_port_flap"
        flag_capability_pass = False
        if need_capability in list(capability.keys()):
            if addr in capability[need_capability]:
                flag_capability_pass = True
        if not flag_capability_pass:
            _print("FAIL: phy_link_flap() - Is not possible to execute %s on port %s" % (need_capability, addr))
            print(capability)
            return False

        # Get the switch connected to this port
        connected_sw = self.get_physw_self(addr)
        if not connected_sw:
            _print("FAIL: phy_link_flap(): No switch in configuration is "
                   + "controlling %s, even though it pass capability check..." % addr)
            return False

        sw_obj = connected_sw["class_obj"]
        if "port_of" in list(connected_sw.keys()) and addr in connected_sw["port_of"]:
            return sw_obj.port_flap(connected_sw["port_of"][addr], uptime, downtime, count)

        _print("FAIL: phy_link_flap() - Could not find which interface port %s is connected to" % addr)
        return False
