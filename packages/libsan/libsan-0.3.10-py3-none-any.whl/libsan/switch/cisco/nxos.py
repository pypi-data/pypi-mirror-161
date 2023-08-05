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

"""nxos.py: Module to handle commands on Cisco NXOS Switch."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import time
import libsan.host.ssh
import libsan.host.linux
from libsan.host.net import standardize_mac


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    return


def _standardize_port_id(port_id):
    """
    """
    if not port_id:
        return None
    m = re.match(r"e(\S+)$", port_id)
    if m:
        return "Ethernet%s" % m.group(1)

    m = re.match(r"Eth(\S+)$", port_id)
    if m:
        return "Ethernet%s" % m.group(1)

    m = re.match(r"p(\S+)$", port_id)
    if m:
        return "port-channel%s" % m.group(1)

    m = re.match(r"Po(\S+)$", port_id)
    if m:
        return "port-channel%s" % m.group(1)

    m = re.match(r"vlan(\S+)$", port_id)
    if m:
        return "Vlan%s" % m.group(1)

    return port_id


class nxos:
    """
    Class to manage Cisco NXOS switches
    """
    host = None
    user = None
    passwd = None

    def __init__(self, hostname, username, password):
        self.host = hostname
        self.user = username
        self.passwd = password

    @staticmethod
    def _print(string):
        module_name = __name__
        string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
        string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
        string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
        print(string)
        return

    def _run(self, cmd, return_output=False, verbose=False, invoke_shell=False, expect=None):
        session = libsan.host.ssh.connect(self.host, user=self.user, passwd=self.passwd)
        if not session:
            _print("FAIL: Could not connect to switch (%s)" % self.host)
            if return_output:
                return 127, None
            return 127

        _print("INFO: Connecting to %s for command:" % self.host)
        print(cmd)
        ret, output = libsan.host.ssh.run_cmd(session, cmd, return_output=True, verbose=verbose,
                                              invoke_shell=invoke_shell, expect=expect)
        libsan.host.ssh.disconnect(session)
        if return_output:
            return ret, output
        return ret

    @staticmethod
    def capability():
        """
        Indicates supported operation on switch
        """
        cap_dict = dict()
        cap_dict["link_down"] = True
        cap_dict["link_up"] = True
        cap_dict["link_oscillate"] = True
        cap_dict["switch_reboot"] = False
        cap_dict["fc_switch"] = True
        cap_dict["eth_switch"] = True
        return cap_dict

    def get_version(self):
        """
        Return FW version of the switch
        """
        cmd = "show version"
        _, output = self._run(cmd, return_output=True, verbose=False)
        nxos_regex = re.compile(r"Cisco Nexus Operating System", re.MULTILINE)
        version_regex = re.compile(r".*system:\s+version\s+(\d+)(\.\S+)", re.MULTILINE)
        n = nxos_regex.search(output)
        v = version_regex.search(output)
        if n and v:
            return "%s%s" % (v.group(1), v.group(2))
        return None

    def show_interfaces(self, option="brief"):
        cmd = "show interface %s" % option
        return self._run(cmd)

    def link_trigger(self, action=None, port_id=None, check_state=True):
        if not action or not port_id:
            _print("FAIL: link_trigger needs 'action' and 'port_id' parameters")
            return False

        port_id = _standardize_port_id(port_id)
        if not port_id:
            _print("FAIL: link_trigger() - Invalid port format")
            return False

        cmds = ["terminal length 0", "configure terminal", "interface %s" % port_id]

        if action == "UP":
            cmds.append("no shutdown")
        elif action == "DOWN":
            cmds.append("shutdown")
        else:
            _print("FAIL: link_trigger unsupported action (%s)" % action)
            return False
        # As the command to change interface is inside configure terminal, we need to run all commands in a single
        # shell, so we need to use invoke_shell
        ret = self._run(cmds, verbose=False, invoke_shell=True, expect="# ")
        if ret != 0:
            # It will never hit this point as _run with invoke_shell always return success
            _print("FAIL: link_trigger command failed")
            return False

        # We do not want make sure the state is correct
        if not check_state:
            return True

        attempts = 0
        max_attempts = 5
        verbose = False
        # Try few times to read port state
        while attempts < max_attempts:
            attempts += 1
            # wait 5s to detect link change
            time.sleep(5)
            p_state_dict = self.query_port_state(verbose=verbose)
            if not p_state_dict:
                _print("FATAL: Could not read switch port state")
                continue

            if port_id not in list(p_state_dict.keys()):
                _print("FAIL: Could not find state for port %s" % port_id)
                print(p_state_dict)
                # If could not get the state correct in the first time,
                # print query state output from the switch
                verbose = True
                continue

            if p_state_dict[port_id] == action:
                _print("INFO: Successfully brought port %s %s" % (port_id, action))
                return True

            if attempts == max_attempts:
                _print("FAIL: Failed to bring port %s %s. Current state: %s" %
                       (port_id, action, p_state_dict[port_id]))
                return False
        return False

    def port_state(self, port_id):

        port_id = _standardize_port_id(port_id)
        if not port_id:
            _print("FAIL: port_state requires 'port_id' as parameter")
            return None

        p_state_dict = self.query_port_state()
        if not p_state_dict:
            _print("FAIL: could not query port_state on switch")
            return None

        if port_id not in list(p_state_dict.keys()):
            _print("FAIL: port_state %s was not found on switch" % port_id)
            return None

        return p_state_dict[port_id]

    def port_connect(self, port_id, check_state=True):
        return self.link_trigger(action="UP", port_id=port_id, check_state=check_state)

    def port_disconnect(self, port_id, check_state=True):
        return self.link_trigger(action="DOWN", port_id=port_id, check_state=check_state)

    def port_oscillate(self, port_id, min_uptime, max_uptime, min_downtime,
                       max_downtime, count):
        if (not port_id or min_uptime is None or max_uptime is None or
                min_downtime is None or max_downtime is None or count is None):
            _print("FAIL: port_oscillate() - needs 'port_id' , " +
                   "'min_uptime', 'max_uptime', " +
                   "'min_downtime', 'max_downtime' and 'count' parameters")
            return False

        for cnt in range(1, count + 1):
            _print("INFO: Interaction %d/%d" % (cnt, count))
            self.port_disconnect(port_id, check_state=False)
            increment = (max_downtime - min_downtime) / count
            sleep_time = min_downtime + ((cnt - 1) * increment)
            _print("INFO: Going to sleep for %s with link down" % sleep_time)
            libsan.host.linux.sleep(sleep_time)
            self.port_connect(port_id, check_state=False)
            increment = (max_uptime - min_uptime) / count
            sleep_time = min_uptime + ((cnt - 1) * increment)
            _print("INFO: Going to sleep for %s with link up" % sleep_time)
            libsan.host.linux.sleep(sleep_time)

        return True

    def query_port_state(self, verbose=False):
        """
        Query all interfaces on switch and store there status on a dict
        If port is trunking or 'up' we set it as UP
        Otherwise we set it as DOWN
        """
        cmd = "show interface"
        ret, output = self._run(cmd, return_output=True, verbose=verbose)
        if ret != 0:
            return None

        state_regex = re.compile(r"^(\S+) is ([a-z]+)")
        lines = output.split("\n")
        port_state = {}
        for line in lines:
            m = state_regex.match(line)
            if m:
                state = m.group(2)
                if state == "trunking" or state == "up":
                    port_state[m.group(1)] = "UP"
                else:
                    port_state[m.group(1)] = "DOWN"
        return port_state

    def wwpn_2_port_id(self):
        """
        Query all interfaces that are connected
        And store as key the WWPN and the Port ID as its value
        """
        cmd = "show flogi database"
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            return None

        """# show flogi database
--------------------------------------------------------------------------------
INTERFACE        VSAN    FCID           PORT NAME               NODE NAME
--------------------------------------------------------------------------------
vfc1             702   0xb30000  20:00:90:e2:ba:a3:97:cb 10:00:90:e2:ba:a3:97:cb
        """
        parse_regex = re.compile(r"^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)")
        lines = output.split("\n")
        wwn_dict = {}
        for line in lines:
            m = parse_regex.match(line)
            if m:
                if m.group(1) == "Total" or m.group(1) == "INTERFACE":
                    continue
                wwpn = m.group(4)
                wwn_dict[m.group(1)] = wwpn
        return wwn_dict

    def mac_2_port_id(self):
        """
        Query all interfaces that are connected
        And store as key the WWPN and the Port ID as its value
        """
        cmd = "show mac address-table"
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: mac_2_port_id")
            print(output)
            return None

        """# show mac address-table
        Legend:
                * - primary entry, G - Gateway MAC, (R) - Routed MAC, O - Overlay MAC
                age - seconds since last seen,+ - primary entry using vPC Peer-Link
        VLAN     MAC Address      Type      age     Secure NTFY   Ports/SWID.SSID.LID
        ---------+-----------------+--------+---------+------+----+------------------
        * 1        90e2.baa3.9528    dynamic   20         F    F  Eth1/10
        """
        parse_regex = re.compile(r"^\*\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)")
        lines = output.split("\n")
        mac_dict = {}
        for line in lines:
            m = parse_regex.match(line)
            if m:
                mac = standardize_mac(m.group(2))
                port_id = _standardize_port_id(m.group(7))
                if not port_id:
                    _print("FAIL: mac_2_port_id() - Could not understand port_id %s format" % m.group(7))
                    return None
                mac_dict[port_id] = mac
        return mac_dict
