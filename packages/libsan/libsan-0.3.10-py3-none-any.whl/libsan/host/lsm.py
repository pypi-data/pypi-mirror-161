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

"""lsm.py: Module to manipulate libstoragemgmt userspace package."""

__author__ = "Jakub Krysl"
__copyright__ = "Copyright (c) 2017 Red Hat, Inc. All rights reserved."

import re  # regex
import os
import libsan.host.linux
from libsan.host.cmdline import run
from libsan.host.cli_tools import Wrapper, FailedCheckException, WrongArgumentException, WrongCommandException
from time import sleep


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def _cli(func):
    # This is a decorator to mark functions callable by 'lsmcli'
    func.cli = True
    return func


class LibStorageMgmt(Wrapper):
    def __init__(self, username=None, password=None, target=None, protocol=None, disable_check=False):
        self.disable_check = disable_check
        if libsan.host.linux.dist_ver() < 7:
            _print("FATAL: libstoragemgmt is not supported on RHEL < 7.")

        self.username = None
        self.password = None
        self.target = None
        self.protocol = None
        self.port = None
        self.query_params = None
        self.timeout = None

        # persistent previous values
        self.previous_sys_read_pct = {}
        self.previous_phy_disk_cache_policy = {}
        self.previous_read_cache_policy = {}
        self.previous_write_cache_policy = {}
        self.previous_local_disk_ident_led = {}
        self.previous_local_disk_fault_led = {}

        # local target does not require anything of this and megaraid/sim needs only protocol
        if username and password and target and protocol:
            self.username = username
            self.password = password
            self.target = target
            self.protocol = protocol
        elif protocol and "megaraid" in protocol or "sim" in protocol:
            self.protocol = protocol

        if self.password:
            os.environ["LSMCLI_PASSWORD"] = self.password
            _print("INFO: Password set")
        else:
            if os.environ.get("LSMCLI_PASSWORD"):
                del os.environ["LSMCLI_PASSWORD"]
                _print("INFO: Password cleaned")

        requires_restart = False
        # stop if can't install lsm package
        if not libsan.host.linux.is_installed("libstoragemgmt"):
            if not libsan.host.linux.install_package("libstoragemgmt", check=False):
                _print("FATAL: Could not install libstoragemgmt package")
            else:
                requires_restart = True

        if self.protocol == "smispy":
            self.port = "5988"
            self.query_params = "?namespace=root/emc"
        if self.protocol == "smispy+ssl":
            # ssl uses different port
            self.port = "5989"
            # ignore missing ssl certificate
            self.query_params = "?namespace=root/emc&no_ssl_verify=yes"

        # install protocol specific packages
        if self.protocol:
            if "ontap" in self.protocol:
                if not libsan.host.linux.is_installed("libstoragemgmt-netapp-plugin"):
                    if not libsan.host.linux.install_package("libstoragemgmt-netapp-plugin", check=False):
                        _print("FATAL: Could not install LSM NetApp plugin")
                    else:
                        requires_restart = True
            elif "smispy" in self.protocol:
                if not libsan.host.linux.is_installed("libstoragemgmt-smis-plugin"):
                    if not libsan.host.linux.install_package("libstoragemgmt-smis-plugin", check=False):
                        _print("FATAL: Could not install LSM SMIS plugin")
                    else:
                        requires_restart = True
            elif "targetd" in self.protocol:
                if not libsan.host.linux.is_installed("libstoragemgmt-targetd-plugin"):
                    if not libsan.host.linux.install_package("libstoragemgmt-targetd-plugin", check=False):
                        _print("FATAL: Could not install LSM targetd plugin")
                    else:
                        requires_restart = True
            elif "megaraid" in self.protocol:
                if not libsan.host.linux.is_installed("libstoragemgmt-megaraid-plugin"):
                    if not libsan.host.linux.install_package("libstoragemgmt-megaraid-plugin", check=False):
                        _print("FATAL: Could not install LSM megaraid plugin")
                    else:
                        requires_restart = True
                # needs to install 3rd party tool
                if not libsan.host.linux.install_package("storcli"):
                    _print("FATAL: Could not install storcli")

        if requires_restart:
            if run("service libstoragemgmt restart", verbose=True) != 0:
                _print("FATAL: Could not restart libstoragemgmt service")
            else:
                _print("INFO: Waiting for service to restart.")
                sleep(5)
        else:
            # check if libstoragemgmt service is running
            if libsan.host.linux.service_status("libstoragemgmt") != 0:
                if libsan.host.linux.service_start("libstoragemgmt"):
                    _print("INFO: Waiting for service to start.")
                    sleep(5)

        self.commands = {
            "list": "list",
            "job_status": "job-status",
            "capabilities": "capabilities",
            "plugin_info": "plugin-info",
            "volume_create": "volume-create",
            "volume_raid_create": "volume-raid-create",
            "volume_raid_create_cap": "volume-raid-create-cap",
            "volume_delete": "volume-delete",
            "volume_resize": "volume-resize",
            "volume_replicate": "volume-replicate",
            "volume_replicate_range": "volume-replicate-range",
            "volume_replicate_range_block_size": "volume-replicate-range-block-size",
            "volume_dependants": "volume-dependants",
            "volume_dependants_rm": "volume-dependants-rm",
            "volume_access_group": "volume-access-group",
            "volume_mask": "volume-mask",
            "volume_unmask": "volume-unmask",
            "volume_enable": "volume-enable",
            "volume_disable": "volume-disable",
            "volume_raid_info": "volume-raid-info",
            "volume_ident_led_on": "volume-ident-led-on",
            "volume_ident_led_off": "volume-ident-led-off",
            "system_read_cache_pct_update": "system-read-cache-pct-update",
            "pool_member_info": "pool-member-info",
            "access_group_create": "access-group-create",
            "access_group_add": "access-group-add",
            "access_group_remove": "access-group-remove",
            "access_group_delete": "access-group-delete",
            "access_group_volumes": "access-group-volumes",
            "iscsi_chap": "iscsi-chap",
            "fs_create": "fs-create",
            "fs_delete": "fs-delete",
            "fs_resize": "fs-resize",
            "fs_export": "fs-export",
            "fs_unexport": "fs-unexport",
            "fs_clone": "fs-clone",
            "fs_snap_create": "fs-snap-create",
            "fs_snap_delete": "fs-snap-delete",
            "fs_snap_restore": "fs-snap-restore",
            "fs_dependants": "fs-dependants",
            "fs_dependants_rm": "fs-dependants-rm",
            "file_clone": "file-clone",
            "local_disk_list": "local-disk-list",
            "volume_cache_info": "volume-cache-info",
            "volume_phy_disk_cache_update": "volume-phy-disk-cache-update",
            "volume_read_cache_policy_update": "volume-read-cache-policy-update",
            "volume_write_cache_policy_update": "volume-write-cache-policy-update",
            "local_disk_ident_led_on": "local-disk-ident-led-on",
            "local_disk_ident_led_off": "local-disk-ident-led-off",
            "local_disk_fault_led_on": "local-disk-fault-led-on",
            "local_disk_fault_led_off": "local-disk-fault-led-off"
        }
        self.commands["all"] = list(self.commands.keys())

        self.arguments = {
            "human": [self.commands["all"], " --human"],
            "terse": [self.commands["all"], " --terse="],
            "enum": [self.commands["all"], " --enum"],
            "force": [self.commands["all"], " --force"],
            "wait": [self.commands["all"], " --wait="],
            "header": [self.commands["all"], " --header"],
            "async": [self.commands["all"], " --b"],
            "script": [self.commands["all"], " --script"],
            "lsm_type": [["list"], " --type="],
            "sys": [["list", "capabilities", "volume_raid_create_cap", "volume_replicate_range_block_size",
                     "system_read_cache_pct_update", "access_group_create"], " --sys="],
            "pool": [["list", "volume_create", "volume_replicate", "pool_member_info", "fs_create"], " --pool="],
            "vol": [["list", "volume_delete", "volume_resize", "volume_replicate", "volume_dependants",
                     "volume_dependants_rm", "volume_access_group", "volume_mask", "volume_unmask", "volume_enable",
                     "volume_disable", "volume_raid_info", "volume_ident_led_on", "volume_ident_led_off",
                     "volume_cache_info", "volume_phy_disk_cache_update", "volume_read_cache_policy_update",
                     "volume_read_cache_policy_update"], " --vol="],
            "disk": [["list", "volume_raid_create"], " --disk="],
            "ag": [["list", "volume_mask", "volume_unmask", "access_group_add", "access_group_remove",
                    "access_group_delete", "access_group_volumes"], " --ag="],
            "fs": [["list", "fs_delete", "fs_resize", "fs_export", "fs_snap_create", "fs_snap_delete",
                    "fs_snap_restore", "fs_dependants", "fs_dependants_rm", "file_clone"], " --fs="],
            "nfs_export": [["list"], " --nfs-export="],
            "tgt": [["list"], " --tgt="],
            "job": [["job_status"], " --job="],
            "name": [["volume_create", "volume_raid_create", "volume_replicate", "access_group_create", "fs_create",
                      "fs_snap_create"], " --name="],
            "size": [["volume_create", "volume_resize", "fs_create", "fs_resize"], " --size="],
            "provisioning": [["volume_create"], " --provisioning="],
            "raid_type": [["volume_raid_create"], " --raid-type="],
            "strip_size": [["volume_raid_create"], " --strip-size="],
            "rep_type": [["volume_replicate", "volume_replicate_range"], " --rep-type="],
            "src_vol": [["volume_replicate_range"], " --src-vol="],
            "dst_vol": [["volume_replicate_range"], " --dst-vol="],
            "src_start": [["volume_replicate_range"], " --src-start="],
            "dst_start": [["volume_replicate_range"], " --dst-start="],
            "count": [["volume_replicate_range"], " --count="],
            "read_pct": [["system_read_cache_pct_update"], " --read-pct="],
            "init": [["access_group_create", "access_group_add", "access_group_remove", "iscsi_chap"], " --init="],
            "in_user": [["iscsi_chap"], " --in-user="],
            "in_pass": [["iscsi_chap"], " --in-pass="],
            "out_user": [["iscsi_chap"], " --out-user="],
            "out_pass": [["iscsi_chap"], " --out-pass="],
            "export_path": [["iscsi_chap"], " --exportpath="],
            "anonuid": [["fs_export"], " --anonuid="],
            "anongid": [["fs_export"], " --anongid="],
            "auth_type": [["fs_export"], " --auth-type="],
            "root_host": [["fs_export"], " --root-host="],
            "ro_host": [["fs_export"], " --ro-host="],
            "rw_host": [["fs_export"], " --rw-host="],
            "export": [["fs_unexport"], " --export="],
            "src_fs": [["fs_clone"], " --src-fs="],
            "dst_name": [["fs_clone"], " --dst-name="],
            "backing_snapshot": [["fs_clone", "file_clone"], " --backing-snapshot="],
            "snap": [["fs_snap_delete", "fs_snap_restore"], " --snap="],
            "lsm_file": [["fs_snap_restore", "fs_dependants", "fs_dependants_rm"], " --file="],
            "fileas": [["fs_snap_restore"], " --fileas="],
            "src": [["file_clone"], " --src"],
            "dst": [["file_clone"], " --dst"],
            "policy": [["volume_phy_disk_cache_update", "volume_read_cache_policy_update",
                        "volume_read_cache_policy_update"], " --policy="],
            "path": [["local_disk_ident_led_on", "local_disk_ident_led_off", "local_disk_fault_led_on",
                      "local_disk_fault_led_on"], " --path="],
        }

        Wrapper.__init__(self, self.commands, self.arguments, self.disable_check)

        _print("INFO: LSM configured")

    def _check(self, cmd):
        if self.disable_check or cmd:
            # Do not check if checking is disabled
            return True

        return True

    def _run(self, cmd, verbosity=True, return_output=False, **kwargs):
        # Constructs the command to run and runs it

        ret_fail = False
        if return_output:
            ret_fail = (False, None)

        try:
            command = self._add_command(cmd)
            command = self._add_arguments(command, **kwargs)

        except WrongCommandException as e:
            _print("WARN: Given command '%s' is not allowed in this version." % e.command)
            return ret_fail
        except WrongArgumentException as e:
            message = "WARN: Given argument '%s' is not allowed for given command." % e.argument
            if e.command:
                message = message[:-1] + " '" + e.command + "'."
            if e.arguments:
                message += "\nPlease use only these: %s." % ", ".join(e.arguments)
            _print(message)
            return ret_fail

        cmd = "lsmcli "
        if self.timeout:
            cmd += "-w %s " % self.timeout
        if self.protocol:
            cmd += "-u \"%s://" % self.protocol
            if self.username and self.target:
                cmd += "%s@%s" % (self.username, self.target)
            if self.port:
                cmd += ":%s" % self.port
            if self.query_params:
                cmd += "%s" % self.query_params
            cmd += "\" "
        cmd += command

        try:
            self._check(cmd)
        except WrongArgumentException:
            pass
        except FailedCheckException as e:
            _print("WARN: Failed checking on argument %s" % e.argument)
            return ret_fail

        if return_output:
            ret, data = run(cmd, verbose=verbosity, return_output=True)
            if ret != 0:
                _print("WARN: Running command: '%s' failed. Return with output." % cmd)
            return ret, data

        ret = run(cmd, verbose=verbosity)
        if ret != 0:
            _print("WARN: Running command: '%s' failed." % cmd)
        return ret

    @staticmethod
    def _remove_nones(kwargs):
        return {k: v for k, v in kwargs.items() if v is not None}

    @_cli
    def list(self, lsm_type=None, fs=None, sys=None, pool=None, vol=None,
             disk=None, ag=None, nfs_export=None, tgt=None, **kwargs):
        kwargs.update({
            'lsm_type': lsm_type,
            'fs': fs,
            'sys': sys,
            'pool': pool,
            'vol': vol,
            'disk': disk,
            'ag': ag,
            'nfs_export': nfs_export,
            'tgt': tgt
        })
        return self._run("list", **self._remove_nones(kwargs))

    @_cli
    def job_status(self, job=None, **kwargs):
        kwargs.update({'job': job})
        return self._run("job_status", **self._remove_nones(kwargs))

    @_cli
    def capabilities(self, sys=None, **kwargs):
        kwargs.update({'sys': sys})
        return self._run("capabilities", **self._remove_nones(kwargs))

    @_cli
    def plugin_info(self, **kwargs):
        return self._run("plugin_info", **self._remove_nones(kwargs))

    @_cli
    def volume_create(self, name=None, size=None, pool=None, provisioning=None, **kwargs):
        kwargs.update({
            'name': name,
            'size': size,
            'pool': pool,
            'provisioning': provisioning
        })
        return self._run("volume_create", **self._remove_nones(kwargs))

    @_cli
    def volume_raid_create(self, name=None, raid_type=None, disk=None, strip_size=None, **kwargs):
        kwargs.update({
            'name': name,
            'raid_type': raid_type,
            'disk': disk,
            'strip_size': strip_size
        })
        return self._run("volume_raid_create", **self._remove_nones(kwargs))

    @_cli
    def volume_raid_create_cap(self, sys=None, **kwargs):
        kwargs.update({'sys': sys})
        return self._run("volume_raid_create_cap", **self._remove_nones(kwargs))

    @_cli
    def volume_ident_led_on(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_ident_led_on", **self._remove_nones(kwargs))

    @_cli
    def volume_ident_led_off(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_ident_led_off", **self._remove_nones(kwargs))

    @_cli
    def volume_delete(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_delete", **self._remove_nones(kwargs))

    @_cli
    def volume_resize(self, vol=None, size=None, **kwargs):
        kwargs.update({
            'vol': vol,
            'size': size
        })
        return self._run("volume_resize", **self._remove_nones(kwargs))

    @_cli
    def volume_replicate(self, vol=None, name=None, rep_type=None, pool=None, **kwargs):
        kwargs.update({
            'vol': vol,
            'name': name,
            'rep_type': rep_type,
            'pool': pool
        })
        return self._run("volume_replicate", **self._remove_nones(kwargs))

    @_cli
    def volume_replicate_range(self, src_vol=None, dst_vol=None, rep_type=None,
                               src_start=None, dst_start=None, count=None, **kwargs):
        kwargs.update({
            'src_vol': src_vol,
            'dst_vol': dst_vol,
            'rep_type': rep_type,
            'src_start': src_start,
            'dst_start': dst_start,
            'count': count
        })
        return self._run("volume_replicate_range", **self._remove_nones(kwargs))

    @_cli
    def volume_replicate_range_block_size(self, sys=None, **kwargs):
        kwargs.update({'sys': sys})
        return self._run("volume_replicate_range_block_size", **self._remove_nones(kwargs))

    @_cli
    def volume_dependants(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_dependants", **self._remove_nones(kwargs))

    @_cli
    def volume_dependants_rm(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_dependants_rm", **self._remove_nones(kwargs))

    @_cli
    def volume_access_group(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_access_group", **self._remove_nones(kwargs))

    @_cli
    def volume_mask(self, vol=None, ag=None, **kwargs):
        kwargs.update({
            'vol': vol,
            'ag': ag
        })
        return self._run("volume_mask", **self._remove_nones(kwargs))

    @_cli
    def volume_unmask(self, vol=None, ag=None, **kwargs):
        kwargs.update({
            'vol': vol,
            'ag': ag
        })
        return self._run("volume_unmask", **self._remove_nones(kwargs))

    @_cli
    def volume_enable(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_enable", **self._remove_nones(kwargs))

    @_cli
    def volume_disable(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_disable", **self._remove_nones(kwargs))

    @_cli
    def volume_raid_info(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_raid_info", **self._remove_nones(kwargs))

    @_cli
    def pool_member_info(self, pool=None, **kwargs):
        kwargs.update({'pool': pool})
        return self._run("pool_member_info", **self._remove_nones(kwargs))

    @_cli
    def access_group_create(self, name=None, init=None, sys=None, **kwargs):
        kwargs.update({
            'name': name,
            'init': init,
            'sys': sys
        })
        return self._run("access_group_create", **self._remove_nones(kwargs))

    @_cli
    def access_group_add(self, ag=None, init=None, **kwargs):
        kwargs.update({
            'ag': ag,
            'init': init
        })
        return self._run("access_group_add", **self._remove_nones(kwargs))

    @_cli
    def access_group_remove(self, ag=None, init=None, **kwargs):
        kwargs.update({
            'ag': ag,
            'init': init
        })
        return self._run("access_group_remove", **self._remove_nones(kwargs))

    @_cli
    def access_group_delete(self, ag=None, **kwargs):
        kwargs.update({'ag': ag})
        return self._run("access_group_delete", **self._remove_nones(kwargs))

    @_cli
    def access_group_volumes(self, ag=None, **kwargs):
        kwargs.update({'ag': ag})
        return self._run("access_group_volumes", **self._remove_nones(kwargs))

    @_cli
    def iscsi_chap(self, init=None, in_user=None, in_pass=None, out_user=None, out_pass=None, **kwargs):
        kwargs.update({
            'init': init,
            'in_user': in_user,
            'in_pass': in_pass,
            'out_user': out_user,
            'out_pass': out_pass
        })
        return self._run("iscsi_chap", **self._remove_nones(kwargs))

    @_cli
    def fs_create(self, fs=None, **kwargs):
        kwargs.update({'fs': fs})
        return self._run("fs_create", **self._remove_nones(kwargs))

    @_cli
    def fs_delete(self, fs=None, **kwargs):
        kwargs.update({'fs': fs})
        return self._run("fs_delete", **self._remove_nones(kwargs))

    @_cli
    def fs_resize(self, fs=None, size=None, **kwargs):
        kwargs.update({
            'fs': fs,
            'size': size
        })
        return self._run("fs_resize", **self._remove_nones(kwargs))

    @_cli
    def fs_export(self, fs=None, exportpath=None, anonguid=None, anongid=None,
                  auth_type=None, root_host=None, ro_host=None, rw_host=None, **kwargs):
        kwargs.update({
            'fs': fs,
            'exportpath': exportpath,
            'anonguid': anonguid,
            'anongid': anongid,
            'auth_type': auth_type,
            'root_host': root_host,
            'ro_host': ro_host,
            'rw_host': rw_host
        })
        return self._run("fs_export", **self._remove_nones(kwargs))

    @_cli
    def fs_unexport(self, export=None, **kwargs):
        kwargs.update({'export': export})
        return self._run("fs_unexport", **self._remove_nones(kwargs))

    @_cli
    def fs_clone(self, src_fs=None, dst_name=None, backing_snapshot=None, **kwargs):
        kwargs.update({
            'src_fs': src_fs,
            'dst_name': dst_name,
            'backing_snapshot': backing_snapshot
        })
        return self._run("fs_clone", **self._remove_nones(kwargs))

    @_cli
    def fs_snap_create(self, name=None, fs=None, **kwargs):
        kwargs.update({
            'name': name,
            'fs': fs
        })
        return self._run("fs_snap_create", **self._remove_nones(kwargs))

    @_cli
    def fs_snap_delete(self, snap=None, fs=None, **kwargs):
        kwargs.update({
            'snap': snap,
            'fs': fs
        })
        return self._run("fs_snap_delete", **self._remove_nones(kwargs))

    @_cli
    def fs_snap_restore(self, fs=None, snap=None, lsm_file=None, fileas=None, **kwargs):
        kwargs.update({
            'fs': fs,
            'snap': snap,
            'lsm_file': lsm_file,
            'fileas': fileas
        })
        return self._run("fs_snap_restore", **self._remove_nones(kwargs))

    @_cli
    def fs_dependants(self, fs=None, lsm_file=None, **kwargs):
        kwargs.update({
            'fs': fs,
            'lsm_file': lsm_file
        })
        return self._run("fs_dependants", **self._remove_nones(kwargs))

    @_cli
    def fs_dependants_rm(self, fs=None, lsm_file=None, **kwargs):
        kwargs.update({
            'fs': fs,
            'lsm_file': lsm_file
        })
        return self._run("fs_dependants_rm", **self._remove_nones(kwargs))

    @_cli
    def file_clone(self, fs=None, src=None, dst=None, backing_snapshot=None, **kwargs):
        kwargs.update({
            'fs': fs,
            'src': src,
            'dst': dst,
            'backing_snapshot': backing_snapshot
        })
        return self._run("file_clone", **self._remove_nones(kwargs))

    @_cli
    def system_read_cache_pct_update(self, sys=None, read_pct=None, **kwargs):
        kwargs.update({
            'sys': sys,
            'read_pct': read_pct
        })
        return self._run("system_read_cache_pct_update", **self._remove_nones(kwargs))

    @_cli
    def local_disk_list(self, **kwargs):
        return self._run("local_disk_list", **self._remove_nones(kwargs))

    @_cli
    def volume_cache_info(self, vol=None, **kwargs):
        kwargs.update({'vol': vol})
        return self._run("volume_cache_info", **self._remove_nones(kwargs))

    @_cli
    def volume_phy_disk_cache_update(self, vol=None, policy=None, **kwargs):
        kwargs.update({
            'vol': vol,
            'policy': policy
        })
        return self._run("volume_phy_disk_cache_update", **self._remove_nones(kwargs))

    @_cli
    def volume_read_cache_policy_update(self, vol=None, policy=None, **kwargs):
        kwargs.update({
            'vol': vol,
            'policy': policy
        })
        return self._run("volume_read_cache_policy_update", **self._remove_nones(kwargs))

    @_cli
    def volume_write_cache_policy_update(self, vol=None, policy=None, **kwargs):
        kwargs.update({
            'vol': vol,
            'policy': policy
        })
        return self._run("volume_write_cache_policy_update", **self._remove_nones(kwargs))

    @_cli
    def local_disk_ident_led_on(self, path=None, **kwargs):
        kwargs.update({'path': path})
        return self._run("local_disk_ident_led_on", **self._remove_nones(kwargs))

    @_cli
    def local_disk_ident_led_off(self, path=None, **kwargs):
        kwargs.update({'path': path})
        return self._run("local_disk_ident_led_off", **self._remove_nones(kwargs))

    @_cli
    def local_disk_fault_led_on(self, path=None, **kwargs):
        kwargs.update({'path': path})
        return self._run("local_disk_fault_led_on", **self._remove_nones(kwargs))

    @_cli
    def local_disk_fault_led_off(self, path=None, **kwargs):
        kwargs.update({'path': path})
        return self._run("local_disk_fault_led_off", **self._remove_nones(kwargs))

    def help(self, cmd=""):
        """Retrieve help.
        The arguments are:
        \tcmd - optional | get help on this command
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        if cmd and cmd not in list(self.commands.keys()):
            _print("FAIL: Unknown command %s." % cmd)
            return False

        command = "%s -h" % cmd.replace("_", "-")
        return run(command, verbose=True)

    def version(self, cmd=""):
        """Retrieve plugin version.
        The arguments are:
        \tcmd - optional | get version of this command
        Returns:
        \tBoolean:
        \t\tTrue if success
        \t\tFalse in case of failure
        """
        if cmd and cmd not in list(self.commands.keys()):
            _print("FAIL: Unknown command %s." % cmd)
            return False

        command = "%s -v" % cmd.replace("_", "-")
        return run(command, verbose=True)
