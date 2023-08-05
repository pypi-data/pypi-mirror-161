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

"""apconcli.py: Module to handle commands on ApCon Switch."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import sys
import socket
import time
import libsan.host.ssh
import libsan.host.linux


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ")", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ")", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ")", string)
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ")", string)
    print(string)
    return


class apconcli:
    """
    Class to manage ApCon switches
    """
    host = None
    user = None
    passwd = None

    port_info_dict = None

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

    def _run(self, cmd, return_output=False, verbose=True, cr="\r", expect=">> ", command_expect=None):
        session = libsan.host.ssh.connect(self.host, user=self.user, passwd=self.passwd)
        if not session:
            _print("FAIL: Could not connect to switch (%s)" % self.host)
            if return_output:
                return 127, None
            return 127
        try:
            ret = libsan.host.ssh.run_cmd(session, cmd, return_output=return_output, verbose=verbose, invoke_shell=True,
                                          cr=cr, expect=expect, command_expect=command_expect)
        except socket.timeout:
            _print("FAIL: Timeout connecting to %s" % self.host)
            if return_output:
                return 127, None
            return 127
        except Exception as e:
            _print("FAIL: Exception when connecting to switch")
            print("Exception is ", sys.exc_info()[0] + " " + e)
            if return_output:
                return 127, None
            return 127
        libsan.host.ssh.disconnect(session)
        return ret

    def get_version(self):
        """
        Return FW version of the switch
        """
        cmd = "show version raw"
        _, output = self._run(cmd, return_output=True, verbose=False)
        if not output:
            _print("FAIL: get_version() - Could not get any output from switch")
            return None
        version_regex = re.compile(r".*Primary Cntrl F/W ver:[ \t]+([0-9]+)(.+)", re.MULTILINE)
        v = version_regex.search(output)
        if v:
            return "%s" % (v.group(1))
        _print("FAIL: get_version() - Could not parse output from switch")
        print(output)
        return None

    @staticmethod
    def capability():
        """
        Indicates supported operations on switch
        """
        cap_dict = dict()
        cap_dict["phy_port_connect"] = True
        cap_dict["phy_port_disconnect"] = True
        cap_dict["phy_port_flap"] = True
        cap_dict["phy_port_status"] = True
        cap_dict["phy_port_oscillate"] = True
        cap_dict["fc_physwitch"] = True
        return cap_dict

    def connect_state_dict(self):
        """
        Usage
            obj->connect_state_dict()
        Purpose
            Show the connection status and reture a dict like this:
                {A05: (06)}
            We depend on this command output:
                show connections raw
            Port 'A00' mean no connection defined, we omit them.
            We will use this info to reconnect ports if user not define all info.
        Parameter
            N/A
        Returns
            A dictionary of port ID to a list of Dest ports
        """
        cmd = "show connections raw"
        _, output = self._run(cmd, return_output=True, verbose=False)
        if not output:
            _print("FAIL: connect_state_dict() - Could not get any output from switch")
            return None

        state_dict = {}

        lines = output.split("\n")
        state_regex = re.compile(r"([A-Z]+[0-9]+):\s+([A-Z]+[0-9]+)")
        for line in lines:
            if re.search(cmd, line):
                # the output contains the command line, so we skip it
                continue
            m = state_regex.search(line)
            if m:
                src_port = m.group(1)
                dst_port = m.group(2)
                if dst_port == "A00":
                    # Skip A00 as it means no connection
                    continue
                if src_port not in list(state_dict.keys()):
                    state_dict[src_port] = []
                state_dict[src_port].append(dst_port)

        return state_dict

    def connect_mode_of(self, port_id):
        """
        Usage
            obj->connect_mode_of(port_id)
        Purpose
            Find out the connect stats for port_id.
            Return 'simplex' or 'duplex' or 'multicast' or None
        Parameter
            port_id        # like 'A01'
        Returns
            connect_state  # 'simplex' or 'duplex' or 'multicast'
                or
            None

        """
        if not port_id:
            _print("FAIL: connect_mode_of() - requires port_id as argument")
            return None

        port_state_dict = self.connect_state_dict()
        if port_id not in list(port_state_dict.keys()):
            return None

        n_conn = len(port_state_dict[port_id])
        for src_port in list(port_state_dict.keys()):
            for dst_port in port_state_dict[src_port]:
                if dst_port == port_id:
                    n_conn += 1

        if n_conn == 1:
            return "simplex"

        if n_conn == 2:
            return "duplex"

        if n_conn > 2:
            return "multicast"

        _print("FATAL: Unsupported mode on port %s" % port_id)
        return None

    def port_status(self, port_id):
        if not port_id:
            _print("FAIL: port_status() - needs 'port_id' parameter")
            return False

        cmd = "show port info %s" % port_id
        ret, output = self._run(cmd, return_output=True, verbose=False)
        if ret != 0:
            # It will never hit this point as _run with invoke_shell always return success
            _print("FAIL: port_status() - command failed")
            return None

        status_regex = re.compile(r"%s:\s+Status:\s+(\S+)" % port_id)
        lines = output.split("\n")
        for line in lines:
            m = status_regex.match(line)
            if m:
                return m.group(1)
        _print("FAIL: port_status() - Could not find status for port %s" % port_id)
        print(output)
        return None

    def port_disconnect(self, port_id, check_state=True):
        if not port_id:
            _print("FAIL: port_disconnect() - needs 'port_id' parameter")
            return False

        cmd = "disconnect %s" % port_id
        ret = self._run(cmd, verbose=False)
        if ret != 0:
            # It will never hit this point as _run with invoke_shell always return success
            _print("FAIL: port_disconnect() - command failed")
            return False

        if not check_state:
            _print("INFO: Successfully disconnected port %s" % port_id)
            return True

        state_dict = self.connect_state_dict()
        if port_id not in list(state_dict.keys()):
            _print("INFO: Successfully disconnected port %s" % port_id)
            return True

        _print("FAIL: port_disconnect() - Failed to disconnect port %s." % port_id)
        return False

    def port_connect(self, src_port_id, dst_port_id, mode, check_state=True):
        if not src_port_id or not dst_port_id or not mode:
            _print("FAIL: port_connect() - needs 'src_port_id' , 'dst_port_id' and 'mode' parameters")
            return False

        if mode != "simplex" and mode != "duplex":
            _print("FAIL: mode %s is not supported" % mode)
            return False

        cmd = "connect %s %s %s" % (mode, src_port_id, dst_port_id)
        ret = self._run(cmd, verbose=False)
        if ret != 0:
            # It will never hit this point as _run with invoke_shell always return success
            _print("FAIL: port_connect() - command failed")
            return False

        if not check_state:
            _print("INFO: Successfully connected port %s to %s (%s)" % (src_port_id, dst_port_id, mode))
            return True

        connected_mode = self.connect_mode_of(src_port_id)
        if connected_mode and connected_mode == mode:
            _print("INFO: Successfully connected port %s to %s (%s)" % (src_port_id, dst_port_id, mode))
            return True

        _print("FAIL: port_connect() - Failed to connect port %s to %s (%s)." % (src_port_id, dst_port_id, mode))
        return False

    def port_oscillate(self, src_port_id, dst_port_id, mode, min_uptime,
                       max_uptime, min_downtime, max_downtime, count):
        if (not src_port_id or not dst_port_id or not mode or min_uptime is None or
                max_uptime is None or min_downtime is None or max_downtime is None or count is None):
            _print("FAIL: port_oscillate() - needs 'src_port_id' , 'dst_port_id', " +
                   "'mode', 'min_uptime', 'max_uptime', " +
                   "'min_downtime', 'max_downtime' and 'count' parameters")
            return False

        for cnt in range(1, count + 1):
            _print("INFO: Interaction %d/%d" % (cnt, count))
            self.port_disconnect(src_port_id, check_state=False)
            increment = (max_downtime - min_downtime) / count
            sleep_time = min_downtime + ((cnt - 1) * increment)
            _print("INFO: Going to sleep for %s with link down" % sleep_time)
            libsan.host.linux.sleep(sleep_time)
            self.port_connect(src_port_id, dst_port_id, mode, check_state=False)
            increment = (max_uptime - min_uptime) / count
            sleep_time = min_uptime + ((cnt - 1) * increment)
            _print("INFO: Going to sleep for %s with link up" % sleep_time)
            libsan.host.linux.sleep(sleep_time)

        return True

    def port_flap(self, port_id, uptime, downtime, count):
        """
        Purpose
            Flap a port via command 'flap'.
            We will sleep utils flap done. 'flap' command in ApConCLI is still
            interactive command.
            The maximum duration of a flap is 10 seconds.
            So if that exceed, we will reduce count first.
            If uptime + downtime exceeded 10 seconds, we will change each of them to 5s.
        Parameter
            port_id        # like 'A05'
            uptime         # time to keep link up during flap in micro seconds
            downtime       # time to keep link down during flap in micro seconds
            count          # how many times should we flap the port. like '10'
        """
        if not port_id or not uptime or not downtime or not count:
            _print("FAIL: port_flap() - requires 'port_id', 'uptime', 'downtime' and count as parameters")
            return False

        # make sure uptime, downtime, count are int
        try:
            uptime = int(uptime)
            downtime = int(downtime)
            count = int(count)
        except Exception as e:
            _print("FAIL: uptime, downtime and count must be integers")
            print(e)
            return False

        if uptime + downtime > 10000:
            _print("WARN: port_flap() - The sum of uptime and downtime exceed 10s, chaging each of them to 5s")
            uptime = 5000
            downtime = 5000

        # Might be better to use expect
        cmds = ["flap", "%s" % port_id, "%s" % downtime, "%s" % uptime, "%s" % count]
        ret, output = self._run(cmds, return_output=True, verbose=False, command_expect=": ")
        if ret != 0:
            # It will never hit this point as _run with invoke_shell always return success
            _print("FAIL: port_flap() - command failed")
            return False

        flap_start_regex = re.compile("Port flapping started", re.MULTILINE)
        if output and flap_start_regex.search(output):
            sleep_time = int((uptime + downtime) * count / 1000) + 1
            _print("INFO: port_flap() - Flapping port %s uptime %s ms, downtime %s ms, count %s" %
                   (port_id, uptime, downtime, count))
            _print("INFO: port_flap() - Waiting %s seconds while flapping port %s" %
                   (sleep_time, port_id))
            time.sleep(sleep_time)
            _print("INFO: port_flap() - Port %s finished flapping" % port_id)
            return True

        _print("FAIL: Could not start flap on port %s" % port_id)
        print(output)
        return False
