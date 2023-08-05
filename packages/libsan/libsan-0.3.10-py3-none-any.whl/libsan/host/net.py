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

"""net.py: Module to manipulate network devices."""

import re  # regex
import augeas
import os.path
import netifaces
import ipaddress
import libsan.host.linux
from os import listdir, readlink
from os.path import join, lexists
from libsan.host.cmdline import run

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

sysfs_class_net_path = "/sys/class/net"


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


def is_mac(mac):
    """
    Check if given MAC is  on valid format
    """
    if standardize_mac(mac):
        return True
    return False


def get_nics():
    """
    Return list of all NICs on the server
    """
    ifaces = netifaces.interfaces()  # pylint: disable=c-extension-no-member
    if ifaces is None:  # No NIC on this server
        return None

    return ifaces


def get_mac_of_nic(nic):
    """
    Given a NIC name return its MAC address
    """

    try:
        mac = netifaces.ifaddresses(nic)[netifaces.AF_LINK][0]['addr']  # pylint: disable=c-extension-no-member
        return mac
    except Exception as e:
        print(repr(e))
        return None


def get_nic_of_mac(mac_address):
    """
    Give an MAC address return the server interface name
    """
    if not mac_address:
        _print("FAIL: get_nic_of_mac() - requires mac as argument")
        return None

    mac = mac_address.lower()

    if not is_mac(mac):
        _print("FAIL: get_nic_of_mac() - %s does not seem to be a valid MAC" % mac)
        return None

    nics = get_nics()
    if not nics:
        return None

    for nic in nics:
        if mac == get_mac_of_nic(nic):
            return nic

    return None


def get_ip_address_of_nic(nic):
    """
    Get IPv4 of specific network interface
    """
    try:
        ip = netifaces.ifaddresses(nic)[netifaces.AF_INET][0]['addr']  # pylint: disable=c-extension-no-member
        return ip
    except KeyError as e:
        print('KeyError - Iface probably does not have a IP address - %s' % str(e))
    except Exception as e:
        print(repr(e))
    return None


def get_ipv6_address_of_nic(nic):
    """
    Get IPv6 of specific network interface
    """
    try:
        ip = netifaces.ifaddresses(nic)[netifaces.AF_INET6][0]['addr']  # pylint: disable=c-extension-no-member
        return ip
    except KeyError as e:
        print('KeyError - Iface probably does not have a IPv6 address - %s' % str(e))
    except Exception as e:
        print(repr(e))
    return None


def get_nic_of_ip(ip):
    """
    Given an IP address return the NIC name using it
    """
    if not ip:
        return None

    nics = get_nics()
    if not nics:
        return None

    for nic in nics:
        if ip == get_ip_address_of_nic(nic):
            return nic
    return None


def nic_2_driver():
    """Return a dictionary where nic name is the key and driver name is the value.
Will skip sub interfaces, loop device, tun, vboxnet0.
The arguments are:
\tNone
\treturn_output (Dict): Return a dictionary
Returns:
\tdict: Return dict containing all NICs
"""
    nic_dict = {}
    for nic in listdir(sysfs_class_net_path):
        if (nic == "." or nic == ".." or
                nic == "lo" or  # loop
                re.match("^tun[0-9]+", nic) or  # TUN NIC
                re.match("^vboxnet[0-9]+", nic) or  # virtualbox NIC.
                re.search(r"\.", nic)):  # sub-interface
            continue
        nic_dict[nic] = driver_of_nic(nic)
    # print nic_dict
    return nic_dict


# End of nic_2_driver()

def driver_of_nic(nic):
    """Given a specific NIC name it returns its driver name
Find out the driver of certain NIC via sysfs file:
    /sys/class/net/eth0/device/driver   # it's a link.
The arguments are:
\tnic: NIC name, e.g. eth0
Returns:
\tstr: Driver name
"""
    nic = phy_nic_of(nic)
    nic_file = join(sysfs_class_net_path, nic)
    if not lexists(nic_file):
        print("FAIL: No such NIC exists: %s" % nic)
        print(nic_file)
        return None
    driver_file = "/sys/class/net/%s/device/driver" % nic
    if not lexists(driver_file):
        print("FAIL: path %s does not exist" % driver_file)
        return None
    # from a symlink get real path
    real_path = os.readlink(driver_file)
    m = re.match(".*drivers/(.*)$", real_path)
    if not m:
        print("FAIL: Could not find driver name for %s" % nic)
        return None
    return m.group(1)


# End of driver_of_nic()


def phy_nic_of(nic):
    """Translate sub-interface of NIC 'eth0.802-fcoe' to physical NIC 'eth0'.
The arguments are:
\tnic: NIC name, e.g. eth0.802-fcoe
Returns:
\tstr: phy NIC, e.g. eth0
    """
    if not nic:
        return None
    phy_nic = re.sub(r"\..+$", "", nic)
    return phy_nic


def get_pci_id_of_nic(nic):
    """
    From a specific network interface return its PCI ID
    """
    regex_pci_id = libsan.host.linux.get_regex_pci_id()
    sys_path = "%s/%s" % (sysfs_class_net_path, nic)
    link_path = readlink(sys_path)
    # _print("DEBUG: get_pci_id_of_nic - %s" % link_path)
    m = re.search("(%s)/net/%s" % (regex_pci_id, nic), link_path)
    if m:
        return m.group(1)
    return None


def get_ip_version(addr):
    """Given an address, tries to check if it is IPv6 or not
The arguments are:
\taddr:     Network address
Returns:
\t4:        If it is a valid IPv4 address
\t6:        If it is a valid IPv6 address
\tNone:     addr is not an IPv4 or IPv6 address
    """
    try:
        ipver = ipaddress.ip_address(addr).version
        return ipver
    except Exception as e:
        print(repr(e))
        return None


def standardize_mac(mac):
    """
    Usage
        standardize_mac(mac)
    Purpose
        Convert all possiable format mac into stand type:
            (?:[0-9A-F]{2}:){5}[0-9A-F]{2} #like: F0:DE:F1:0D:D3:C9
        Return STRING or ARRAY base on context.
    Parameter
        mac           # any format mac, like "0005.73dd.9a19"
    Returns
        mac
            or
        None
    """
    if not mac:
        return None
    regex_standard_mac = "^(?:[0-9A-F]{2}:){5}[0-9A-F]{2}$"

    mac = mac.lower()
    mac = re.sub("^0x", "", mac)
    mac = re.sub("[^0-9A-Fa-f]", "", mac)
    # If mac given has no ':' we will add it
    if re.match("[0-9a-f]{12}", mac):
        mac_regex = re.compile("(.{2})")
        mac = mac_regex.sub(r"\g<1>:", mac)
        mac = re.sub(":$", "", mac)

    if re.match(regex_standard_mac, mac, re.IGNORECASE):
        return mac

    return None


def convert_netmask(netmask='255.255.255.0'):
    """
    Converts subnet mask to CIDR prefix.
    \t netmask: common subnet mask
    """
    try:
        cidr = ipaddress.IPv4Network((0, netmask)).prefixlen
        return cidr
    except ValueError as e:
        print(e)
        return None


def if_down(nic_or_mac):
    """
    Bring the interface down
    Parameters:
    \t Interface name or it's MAC address
    """
    if not nic_or_mac:
        _print("FAIL: if_down() - requires nic or mac as argument")
        return None

    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
    else:
        nic = nic_or_mac

    if run("ifdown %s" % nic):
        return True
    return False


def if_up(nic_or_mac):
    """
    Bring the interface up
    Parameters:
    \t Interface name or it's MAC address
    """
    if not nic_or_mac:
        _print("FAIL: if_up() - requires nic or mac as argument")
        return None

    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
    else:
        nic = nic_or_mac

    if run("ifup %s" % nic):
        return True
    return False


def set_ifcfg(nic_or_mac, **kwargs):
    """
    Edit or create ifcfg files: IP, prefix, gateway, defroute...
    Parameters:
    \t nic_or_mac: interface name or mac address
    \t key=value: e.g. IPADDR='10.37.151.7'
    """

    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
        if not nic:
            print("FAIL: Couldn't find NIC from MAC.")
            return False
    else:
        nic = nic_or_mac

    aug = augeas.Augeas()
    ifcfg = '/files/etc/sysconfig/network-scripts/ifcfg-' + nic + '/'
    if kwargs is not None:
        for key in kwargs:
            print("INFO: Setting %s to %s for %s" % (key, kwargs[key], nic))
            aug.set(ifcfg + key, kwargs[key])

    try:
        aug.save()
    except augeas.AugeasIOError:
        print('FAIL: unable to save changes in ' + ifcfg)
        return False

    if_down(nic)
    if_up(nic)
    return True


def get_default_iface():
    """
    Returns tuple with ip and interface.
    example: ('10.1.1.1', 'eno1')
    """
    try:
        gateways = netifaces.gateways()  # pylint: disable=c-extension-no-member
        return gateways['default'][netifaces.AF_INET]  # pylint: disable=c-extension-no-member
    except Exception as e:
        print(repr(e))
        return None


def set_iface(nic_or_mac, **kwargs):
    """
    Same as set_ifcfg, without using Augeas
    Modifying ifcfg files; Not creating new
    Parameters:
    \t nic_or_mac: interface name or mac address
    \t key=value: e.g. IPADDR='10.37.151.7'
    """
    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
        if not nic:
            print("FAIL: Couldn't find NIC from MAC.")
            return False
    else:
        nic = nic_or_mac
    print("INFO: Setting parameters for %s:" % nic)
    for kwarg in kwargs:
        print("\t%s: %s" % (kwarg, kwargs[kwarg]))
    try:
        with open('/etc/sysconfig/network-scripts/ifcfg-' + nic, encoding='UTF-8') as conf:
            lines = conf.readlines()
        dictionary = {k: v[:-1] for k, v in (item.split("=") for item in lines)}
        if kwargs is not None:
            dictionary.update(kwargs)
        with open('/etc/sysconfig/network-scripts/ifcfg-' + nic, "w", encoding='UTF-8') as conf:
            conf.writelines([x + "=" + str(dictionary[x]) + "\n" for x in dictionary])
    except (IndexError, ValueError, KeyError) as e:
        print(e)
        return False

    if_down(nic)
    if_up(nic)
    return True


def nm_get_conn(nic_or_mac):
    """
    Returns NetworkManager connection UUID
    \t nic_or_mac: interface name or mac address
    """
    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
        if not nic:
            print("FAIL: Couldn't find NIC from MAC.")
            return None
    else:
        nic = nic_or_mac

    conn = nm_get_conn_from_dev(nic)
    if not conn:
        print('WARN: %s not used in any active connection. Trying connections with same name' % nic)
        # Check connection with same name as device
        if nm_get_conn_iface(nic) == nic:
            return nm_get_conn_uuid(nic)
        return None
    conn = str(conn)
    return nm_get_conn_uuid(conn)


def nm_get_conn_iface(conn):
    """
    Returns interface name used by NM connection
    \t conn: connection id or uuid
    """
    cmd = "nmcli -g connection.interface-name con show \'%s\'" % conn
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Couldn't get connection.interface-name for connection " + conn)
        print(output)
        return None
    return output


def nm_get_conn_uuid(conn):
    """
    Returns NetworkManager connection UUID
    \t conn: connection id
    """
    cmd = "nmcli -g connection.uuid conn show \'%s\'" % conn
    print(cmd)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Couldn't get NM connection uuid using " + conn)
        print(output)
        return None
    return output


def nm_get_conn_from_dev(nic):
    """
    Returns connection id(name) using specified device.
    \t nic: network interface - device
    """
    nic = str(nic)
    cmd = "nmcli -g GENERAL.CONNECTION device show " + nic

    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Couldn't get NM connection using device " + nic)
        print(output)
        return None
    return output


def nm_get_dev_from_conn(conn):
    """
    Returns a device used by specified connection
    \t conn: networkmanager connection id(name) or uuid
    """
    conn = str(conn)
    cmd = "nmcli -g connection.interface-name con show \'%s\'" % conn

    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Couldn't get device used by NM connection " + conn)
        print(output)
        return None
    return output


def nm_conn_up(conn):
    """
    Uses nmcli to activate connection
    \t conn: connection id(name) or uuid
    """
    cmd = "nmcli conn up \"%s\"" % conn
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Unable to activate the connection: %s" % conn)
        return False
    print(output)
    return True


def nm_conn_down(conn):
    """
    Uses nmcli to deactivate connection
    \t conn: connection id(name) or uuid
    """
    cmd = "nmcli conn down \"%s\"" % conn
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Unable to deactivate the connection: %s" % conn)
        return False
    print(output)
    return True


def nm_conn_reload():
    """
    Runs `nmcli conn reload`. Does not support RHEL6
    """
    cmd = "nmcli conn reload"
    retcode = run(cmd, verbose=False)
    if retcode != 0:
        print("FAIL: Unable to reload NetworkManager")
        return False
    return True


def nm_conn_show(conn):
    """
    Use nmcli conn to show all connection parameters. Does not support RHEL6
    \t conn: networkmanager connection id(name) or uuid
    """
    if not conn:
        print("FAIL: No conn specified")
        return False

    cmd = "nmcli conn show \"%s\"" % conn
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Unable to show conn")
        return False
    print(output)
    return True


def nm_conn_del(conn):
    """
    Deletes NetworkManager connection using nmcli
    \t conn: connection id(name) or uuid
    """
    cmd = "nmcli conn delete %s" % conn
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Unable to delete the conn %s" % conn)
        return False
    print(output)
    return True


def nm_add_conn(name=None, nic_or_mac=None, nic_type='ethernet'):
    """
    Use it to add new connection for devices without one
    \tcmd="nmcli con add type ethernet ifname enp5s0f1 con-name enp5s0f1 "
    """

    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
        if not nic:
            print("FAIL: Couldn't find NIC from MAC.")
            return False
    else:
        nic = nic_or_mac

    if not name:
        name = nic

    conn = None
    if nic:
        conn = nm_get_conn_from_dev(nic)
    # Exit if there is a connection already
    if conn:
        print("Connection already exists. Linked to: %s " % conn)
        return True

    cmd = "nmcli conn add type %s con-name %s" % (nic_type, name)
    if nic:
        cmd += " ifname %s" % nic
    if '_' in cmd:
        cmd = cmd.replace("_", "-")
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Unable to add con with cmd %s " % cmd)
        print(output)
        return False
    nm_conn_reload()
    return True


def nm_conn_mod(conn, key, value):
    """
    Modify one or more properties of the NetworkManager connection profile.
    \tnm_con_mod("enp17s0f1","connection.autoconnect", "yes")
    \tnmcli c modify ens2f1 connection.autoconnect yes
    \tExamples compared to network-scripts:
    \tipv4.method manual     >> BOOTPROTO=none
    \tipv4.method auto       >> BOOTPROTO=dhcp
    \tipv4.address "192.168.0.10/24"   >> IPADDR=192.168.0.10
    \tipv4.gateway 192.168.0.1  >> GATEWAY=192.168.0.1
    \tipv4.dns 8.8.8.8   >> DNS1=8.8.8.8
    \tconnection.autoconnect yes   >> ONBOOT=yes
    \tconnection.id eth0   >> NAME=eth0
    \tconnection.interface-name eth0   >> DEVICE=eth0
    \t802-3-ethernet.mac-address 08:00:27:4b:7a:80 >> HWADDR=08:00:27:4b:7a:80
    \tipv4.never-default no   >> DEFROUTE=yes
    """

    if not conn:
        print('FAIL: No connection specified')
        return False
    conn_uuid = nm_get_conn_uuid(conn)
    if not conn_uuid:
        return False
    cmd = "nmcli conn modify %s" % conn_uuid

    cmd += " %s %s" % (key, value)

    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Unable to modify conn %s with cmd %s " % (conn, cmd))
        print(output)
        return False
    return True


def nm_dev_mod(dev, key, value):
    """
    Modify one or more properties that are currently active on the device without modifying
    the connection profile. The changes have immediate effect.
    nmcli dev modify em1 ipv4.method shared
    nmcli dev modify em1 ipv4.address xx
    """

    cmd = "nmcli device modify %s" % dev
    cmd += " %s %s" % (key, value)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Unable to modify dev %s with cmd %s " % (dev, cmd))
        print(output)
        return False
    return True


def nm_set_ip(conn, ip, netmask='24', activate=True):
    """
    Uses nmcli to set static IP, netmask and activates connection.
    \t conn: networkmanager connection id(name) or uuid
    \t ip: IPv4 or IPv6
    """
    ip = str(ip)
    ipver = get_ip_version(ip)

    if ipver == 4:
        cmd_ip = 'ipv4'
    elif ipver == 6:
        cmd_ip = 'ipv6'
    else:
        print("FAIL: Invalid IP format")
        return False

    if "." in netmask:
        netmask = convert_netmask(netmask)

    cmd = "nmcli conn modify %s %s.method manual %s.addr %s/%s" % (conn, cmd_ip, cmd_ip, ip, netmask)
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        print("FAIL: Unable to set IP using nmcli: %s %s" % (conn, ip))
        print(output)
        return False

    if activate:
        if not nm_conn_up(conn):
            return False
    return True
