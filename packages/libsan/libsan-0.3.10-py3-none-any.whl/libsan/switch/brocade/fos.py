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

"""fos.py: Module to handle commands on Brocade FOS Switch."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import time
import libsan.host.ssh
import libsan.host.linux
import libsan.host.fc


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ")", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ")", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ")", string)
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ")", string)
    print(string)
    return


def parse_ret(data):
    # remove command on 1st line and last line with '> '
    return data.split("\r\n")[1:-1]


class fos:
    """
    Class to manage Brocade FOS switches
    """
    host = None
    user = None
    passwd = None

    port_info_dict = None

    def __init__(self, hostname, username, password, timeout=None):
        self.host = hostname
        self.user = username
        self.passwd = password
        self.timeout = timeout
        if self.timeout:
            self.timeout = float(self.timeout)

    @staticmethod
    def _print(string):
        module_name = __name__
        string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
        string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
        string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
        print(string)
        return

    def _run(self, cmd, return_output=False, verbose=True):
        session = libsan.host.ssh.connect(self.host, user=self.user, passwd=self.passwd)
        if not session:
            _print("FAIL: Could not connect to switch (%s)" % self.host)
            if return_output:
                return 127, None
            return 127
        ret = libsan.host.ssh.run_cmd(session, cmd=cmd, return_output=return_output, verbose=verbose,
                                      timeout=self.timeout, invoke_shell=True, expect="> ")

        libsan.host.ssh.disconnect(session)

        if return_output:
            ret_code, output = ret
            output = "\n".join(parse_ret(output))
            # print output
            return ret_code, output

        return ret

    def get_version(self):
        """
        Return FW version of the switch
        """
        cmd = "version"
        _, output = self._run(cmd, return_output=True, verbose=False)
        version_regex = re.compile(r".*Fabric OS:\s+(\S+)", re.MULTILINE)
        v = version_regex.search(output)
        if v:
            return "%s" % (v.group(1))
        return None

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
        cap_dict["eth_switch"] = False
        cap_dict["rcsn_enable"] = True
        cap_dict["rcsn_disable"] = True
        return cap_dict

    def show_interfaces(self):
        cmd = "switchshow"  # % option
        return self._run(cmd)

    def link_trigger(self, action=None, port_id=None, check_state=True):
        if not action or not port_id:
            _print("FAIL: link_trigger needs 'action' and 'port_id' parameters")
            return False

        if action == "UP":
            cmds = "portenable %s" % port_id
        elif action == "DOWN":
            cmds = "portdisable %s" % port_id
        else:
            _print("FAIL: link_trigger unsupported action (%s)" % action)
            return False
        ret = self._run(cmds, verbose=True)
        if ret != 0:
            _print("FAIL: link_trigger command failed")
            return False

        # We do not want make sure the state is correct
        if not check_state:
            return True

        # wait up to 10s to detect link change
        cnt = 0
        max_attempts = 5
        while cnt < max_attempts:
            cnt += 1
            time.sleep(2)

            p_info_dict = self.query_port_info(recheck=True)
            if self.port_state(port_id) == action:
                _print("INFO: Successfully brought port %s %s" % (port_id, action))
                return True

            if cnt == max_attempts:
                _print("FAIL: Failed to bring port %s %s. Current state: %s" % (port_id, action, p_info_dict[port_id]))
                return False

        return False

    def port_state(self, port_id):
        if not port_id:
            _print("FAIL: port_state requires 'port_id' as parameter")
            return None

        p_info_dict = self.query_port_info()
        if not p_info_dict:
            _print("FAIL: Could not query port info")
            return None

        if port_id not in list(p_info_dict.keys()):
            _print("FAIL: port %s was not found on switch %s" % (port_id, self.host))
            print(p_info_dict)
            return None

        if "state" not in list(p_info_dict[port_id].keys()):
            _print("FAIL: Could not find port state for %s" % port_id)
            print(p_info_dict)
            return None

        return p_info_dict[port_id]["state"]

    def port_connect(self, port_id, check_state=True):
        return self.link_trigger(action="UP", port_id=port_id, check_state=check_state)

    def port_disconnect(self, port_id, check_state=True):
        return self.link_trigger(action="DOWN", port_id=port_id, check_state=check_state)

    def port_oscillate(self, port_id, min_uptime, max_uptime, min_downtime,
                       max_downtime, count):
        if (not port_id or min_uptime is None or max_uptime is None or
                min_downtime is None or max_downtime is None or count is None):
            _print("FAIL: port_oscillate() - needs 'port_id', " +
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

    def query_port_info(self, recheck=False):
        """
        Query all interfaces on switch and store its information on a dict
        If port is 'online' we set it as UP
        Otherwise we set it as DOWN
        """

        # If we do not need to recheck and port info exist we return it
        if self.port_info_dict and not recheck:
            return self.port_info_dict

        cmd = "switchshow"
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            _print("FAIL: switchshow command")
            print(output)
            return None
        # Index Port Address Media Speed State     Proto
        #    0   0   010000   id    N8   Online      FC  F-Port  50:0a:09:81:99:1b:8d:c5
        info_regex = re.compile(r"\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s?(.*)")
        # extra parameters, not always present
        # for example: Disabled or F-Port  50:0a:09:82:89:1b:8d:c5 or (No POD License) Disabled
        info_extra_regex = re.compile(r"(.*)\s(\S+)")
        lines = output.split("\n")

        self.port_info_dict = {}
        # Process port status
        for line in lines:
            m = info_regex.match(line)
            if m:
                # print line
                p_dict = {}
                port_id = m.group(1)
                p_dict["wwpn"] = None
                if m.group(8):
                    e = info_extra_regex.match(m.group(8))
                    if e and libsan.host.fc.is_wwn(e.group(2)):
                        p_dict["wwpn"] = e.group(2)

                state = m.group(6)
                if state == "No_Module":
                    # Skip
                    continue
                elif state == "Online":
                    state = "UP"
                else:
                    state = "DOWN"
                p_dict["state"] = state
                self.port_info_dict[port_id] = p_dict

        # Get the wwpns connected to each port
        # We might need to do this, because some ports have more than 1 WWPN connected to it (NPIV...)
        # process_wwpns = False
        # for port_id in self.port_info_dict.keys():
        #   cmd = "portshow %s" % port_id
        #   ret, output = self._run(cmd, return_output = True, verbose = False)
        #   if ret != 0:
        #       _print("FAIL: %s" % cmd)
        #       print output
        #       return None

        #   lines = output.split("\n")
        #   begin_regex = re.compile("portWwn of device\(s\) connected:")
        #   end_regex = re.compile("Distance:")
        #   wwpn_regex = re.compile("\s+((?:[0-9a-f]{2}:){7}[0-9a-f]{2})")
        #   for line in lines:
        #       if begin_regex.match(line):
        #           process_wwpns = True
        #           continue
        #       if end_regex.match(line):
        #           process_wwpns = False
        #           continue
        #       #There could have more then 1 wwpn, for example NPIVs
        #       #For now we just store the last entry...
        #       if process_wwpns:
        #           m = wwpn_regex.search(line)
        #           if m:
        #               self.port_info_dict[port_id]["wwpn"] = m.group(1)

        return self.port_info_dict

    def wwpn_2_port_id(self):
        """
        Query all interfaces that are connected
        And store as key the WWPN and the Port ID as its value
        """
        port_dict = self.query_port_info()

        if not port_dict:
            _print("FAIL: Could not query port info")
            return None

        wwn_dict = {}
        for port_id in list(port_dict.keys()):
            if "wwpn" in list(port_dict[port_id].keys()):
                wwn_dict[port_id] = port_dict[port_id]["wwpn"]
        return wwn_dict

    @staticmethod
    def mac_2_port_id():
        """
        Query all interfaces that are connected
        And store as key the WWPN and the Port ID as its value
        """
        # TODO
        return None

    def rcsn_trigger(self, action=None, port_id=None):
        if not action or not port_id:
            _print("FAIL: rcsn_trigger needs 'action' and 'port_id' parameters")
            return False

        cmds = None
        # To stop RCSN messages to being sent, we need to enable RCSN suppresion
        if action == "ENABLE":
            cmds = ["portcfg rscnsupr %s --disable" % port_id]
        elif action == "DISABLE":
            cmds = ["portcfg rscnsupr %s --enable" % port_id]
        else:
            _print("FAIL: rcsn_trigger unsupported action (%s)" % action)
        ret = self._run(cmds, verbose=True)
        if ret != 0:
            _print("FAIL: rcsn_trigger command failed")
            return False
        return True
