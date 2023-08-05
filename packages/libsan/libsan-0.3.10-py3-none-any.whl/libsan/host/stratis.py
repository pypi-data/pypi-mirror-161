# Copyright (C) 2018 Red Hat, Inc.
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

"""stratis.py: Module to manipulate stratis userspace package."""

__author__ = "Jakub Krysl"
__copyright__ = "Copyright (c) 2018 Red Hat, Inc. All rights reserved."

import re  # regex
import json
import libsan.host.linux
from libsan.host.cmdline import run
from libsan.host.cli_tools import Wrapper


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


def get_stratis_service() -> str:
    """
    Return name of the stratis service.
    :return: Name of the stratis service.
    :rtype: str
    """
    return "stratisd"


class Stratis(Wrapper):
    """
    Wrapper class for stratis command line interface.
    """
    def __init__(self, disable_check=True):
        self.disable_check = disable_check
        if libsan.host.linux.dist_ver() < 8:
            _print("FATAL: Stratis is not supported on RHEL < 8.")

        for pkg in ["stratisd", "stratis-cli"]:
            if not libsan.host.linux.is_installed(pkg):
                if not libsan.host.linux.install_package(pkg, check=False):
                    _print(f"FATAL: Could not install {pkg} package")

        self.commands = {}
        self.commands["all"] = list(self.commands.keys())
        self.arguments = {
            "force": [self.commands["all"], " --force"],
            "redundancy": [self.commands["all"], " --redundancy"],
            "propagate": [self.commands["all"], "--propagate "],
        }

        if libsan.host.linux.service_status(get_stratis_service(), verbose=False) != 0:
            if not libsan.host.linux.service_restart(get_stratis_service()):
                _print(f"FAIL: Could not start {get_stratis_service()} service")
            else:
                _print(f"INFO: Service {get_stratis_service()} restarted.")

        Wrapper.__init__(self, self.commands, self.arguments, self.disable_check)

    @staticmethod
    def _remove_nones(kwargs):
        return {k: v for k, v in kwargs.items() if v is not None}

    def _run(self, cmd, verbosity=True, return_output=False, **kwargs):
        # Constructs the command to run and runs it

        # add '--propagate' flag by default to show whole trace when getting errors
        # This is a suggestion from devs
        if not ("propagate" in kwargs and not kwargs["propagate"]):
            cmd = self.arguments["propagate"][1] + cmd

        cmd = "stratis " + cmd
        cmd = self._add_arguments(cmd, **kwargs)

        ret = run(cmd, verbose=verbosity, return_output=return_output)
        if isinstance(ret, tuple) and ret[0] != 0:
            _print(f"WARN: Running command: '{cmd}' failed. Return with output.")
        elif isinstance(ret, int) and ret != 0:
            _print(f"WARN: Running command: '{cmd}' failed.")
        return ret

    def get_pool_uuid(self, pool_name):
        ret, data = self._run(cmd="report", return_output=True)
        if ret == 0 and data:
            try:
                report = json.loads(data)
            except json.JSONDecodeError:
                print("FAIL: Could not deserialize data returned from 'stratis report' command!")
                return None
            for pool in report["pools"]:
                if pool_name == pool["name"]:
                    print(f"INFO: Found UUID: {pool['uuid']} for pool_name: {pool_name}.")
                    return pool["uuid"]
            print(f"FAIL: Could not find pool UUID for provided pool_name: {pool_name}!")
            return None

    def pool_create(self, pool_name=None, blockdevs=None, force=False, redundancy=None, key_desc=None,
                    tang_url=None, thumbprint=None, clevis=None, trust_url=None, no_overprovision=None, **kwargs):
        cmd = "pool create "
        if key_desc:
            cmd += f"--key-desc {key_desc} "
        if clevis:
            cmd += f"--clevis {clevis} "
        if tang_url:
            cmd += f"--tang-url {tang_url} "
        if thumbprint:
            cmd += f"--thumbprint {thumbprint} "
        if trust_url:
            cmd += "--trust-url "
        if no_overprovision:
            cmd += "--no-overprovision "
        if pool_name:
            cmd += f"{pool_name} "
        if blockdevs:
            if not isinstance(blockdevs, list):
                blockdevs = [blockdevs]
            cmd += " ".join(blockdevs)
        kwargs.update({
            'force': force,
            'redundancy': redundancy,
        })
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_list(self, pool_uuid=None, stopped_pools=None, **kwargs):
        cmd = "pool list "
        if pool_uuid:
            cmd += f"--uuid {pool_uuid} "
        if stopped_pools:
            cmd += "--stopped "
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_destroy(self, pool_name=None, **kwargs):
        cmd = "pool destroy "
        if pool_name:
            cmd += f"{pool_name} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_rename(self, current=None, new=None, **kwargs):
        cmd = "pool rename "
        if current:
            cmd += f"{current} "
        if new:
            cmd += f"{new} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_add_data(self, pool_name=None, blockdevs=None, **kwargs):
        cmd = "pool add-data "
        if pool_name:
            cmd += f"{pool_name} "
        if blockdevs:
            if not isinstance(blockdevs, list):
                blockdevs = [blockdevs]
            cmd += " ".join(blockdevs)
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_add_cache(self, pool_name=None, blockdevs=None, **kwargs):
        cmd = "pool add-cache "
        if pool_name:
            cmd += f"{pool_name} "
        if blockdevs:
            if not isinstance(blockdevs, list):
                blockdevs = [blockdevs]
            cmd += " ".join(blockdevs)
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_init_cache(self, pool_name=None, blockdevs=None, **kwargs):
        cmd = "pool init-cache "
        if pool_name:
            cmd += f"{pool_name} "
        if blockdevs:
            if not isinstance(blockdevs, list):
                blockdevs = [blockdevs]
            cmd += " ".join(blockdevs)
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_bind(self, binding_method=None, pool_name=None, key_desc=None,
                  trust_url=None, thumbprint=None, tang_url=None, force=None, redundancy=None, **kwargs):
        cmd = "pool bind "
        if binding_method:
            cmd += f"{binding_method} "
        if trust_url:
            cmd += "--trust-url "
        if thumbprint:
            cmd += f"--thumbprint {thumbprint} "
        if pool_name:
            cmd += f"{pool_name} "
        if key_desc:
            cmd += f"{key_desc} "
        if tang_url:
            cmd += f"{tang_url} "
        kwargs.update({
            'force': force,
            'redundancy': redundancy,
        })
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_rebind(self, binding_method=None, pool_name=None, key_desc=None,
                    force=None, redundancy=None, **kwargs):
        cmd = "pool rebind "
        if binding_method:
            cmd += f"{binding_method} "
        if pool_name:
            cmd += f"{pool_name} "
        if key_desc:
            cmd += f"{key_desc} "
        kwargs.update({
            'force': force,
            'redundancy': redundancy,
        })
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_unbind(self, binding_method=None, pool_name=None, force=None, redundancy=None, **kwargs):
        cmd = "pool unbind "
        if binding_method:
            cmd += f"{binding_method} "
        if pool_name:
            cmd += f"{pool_name} "
        kwargs.update({
            'force': force,
            'redundancy': redundancy,
        })
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_set_fs_limit(self, pool_name=None, fs_amount=None, force=None, redundancy=None, **kwargs):
        cmd = "pool set-fs-limit "
        if pool_name:
            cmd += f"{pool_name} "
        if fs_amount:
            cmd += f"{fs_amount} "
        kwargs.update({
            'force': force,
            'redundancy': redundancy,
        })
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_overprovision(self, pool_name=None, pool_overprovision=None, **kwargs):
        cmd = "pool overprovision "
        if pool_name:
            cmd += f"{pool_name} "
        if pool_overprovision:
            cmd += f"{pool_overprovision}"
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_explain(self, pool_error_code=None, **kwargs):
        cmd = "pool explain "
        if pool_error_code:
            cmd += f"{pool_error_code} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_debug(self, debug_subcommand=None, pool_name=None, pool_uuid=None, **kwargs):
        cmd = "pool debug "
        if debug_subcommand:
            cmd += f"{debug_subcommand} "
        if pool_name:
            cmd += f"--name {pool_name} "
        if pool_uuid:
            cmd += f"--uuid {pool_uuid} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_start(self, pool_uuid=None, unlock_method=None, **kwargs):
        cmd = "pool start "
        if unlock_method:
            cmd += f"--unlock-method {unlock_method} "
        if pool_uuid:
            cmd += f"{pool_uuid} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def pool_stop(self, pool_name=None, **kwargs):
        cmd = "pool stop "
        if pool_name:
            cmd += f"{pool_name} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def blockdev_list(self, pool_name=None, **kwargs):
        cmd = "blockdev list "
        if pool_name:
            cmd += f"{pool_name} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def blockdev_debug(self, debug_subcommand=None, dev_uuid=None, **kwargs):
        cmd = "blockdev debug "
        if debug_subcommand:
            cmd += f"{debug_subcommand} "
        if dev_uuid:
            cmd += f"--uuid {dev_uuid} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_create(self, pool_name=None, fs_name=None, fs_size=None, **kwargs):
        cmd = "fs create "
        if fs_size:
            cmd += f"--size {fs_size} "
        if pool_name:
            cmd += f"{pool_name} "
        if fs_name:
            cmd += f"{fs_name} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_debug(self, debug_subcommand=None, fs_name=None, fs_uuid=None, **kwargs):
        cmd = "fs debug "
        if debug_subcommand:
            cmd += f"{debug_subcommand} "
        if fs_name:
            cmd += f"--name {fs_name} "
        if fs_uuid:
            cmd += f"--uuid {fs_uuid} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_snapshot(self, pool_name=None, origin_name=None, snapshot_name=None, **kwargs):
        cmd = "fs snapshot "
        if pool_name:
            cmd += f"{pool_name} "
        if origin_name:
            cmd += f"{origin_name} "
        if snapshot_name:
            cmd += f"{snapshot_name} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_list(self, pool_name=None, **kwargs):
        cmd = "fs list "
        if pool_name:
            cmd += f"{pool_name} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_destroy(self, pool_name=None, fs_name=None, **kwargs):
        cmd = "fs destroy "
        if pool_name:
            cmd += f"{pool_name} "
        if fs_name:
            cmd += f"{fs_name} "
        return self._run(cmd, **self._remove_nones(kwargs))

    def fs_rename(self, pool_name=None, fs_name=None, new_name=None, **kwargs):
        cmd = "fs rename "
        if pool_name:
            cmd += f"{pool_name} "
        if fs_name:
            cmd += f"{fs_name} "
        if new_name:
            cmd += f"{new_name} "
        return self._run(cmd, **kwargs)

    def key_set(self, keyfile_path=None, key_desc=None, **kwargs):
        cmd = "key set "
        if keyfile_path:
            cmd += f"--keyfile-path {keyfile_path} "
        if key_desc:
            cmd += f"{key_desc} "
        ret = self._run("key list", return_output=True)
        # ret is a tuple in format -> (return_code, return_output)
        if key_desc in ret[1]:
            return self._run("key list")
        return self._run(cmd, **kwargs)

    def key_reset(self, keyfile_path=None, key_desc=None, **kwargs):
        cmd = "key reset "
        if keyfile_path:
            cmd += f"--keyfile-path {keyfile_path} "
        if key_desc:
            cmd += f"{key_desc} "
        return self._run(cmd, **kwargs)

    def key_list(self, **kwargs):
        return self._run("key list", **kwargs)

    def key_unset(self, key_desc=None, **kwargs):
        cmd = "key unset "
        if key_desc:
            cmd += f"{key_desc} "
        return self._run(cmd, **kwargs)

    # Pool unlock has been removed in favor of pool_start in Stratisd 3.2.0
    def pool_unlock(self, **kwargs):
        return self._run("pool unlock", **kwargs)

    def daemon_redundancy(self, **kwargs):
        return self._run("daemon redundancy", **kwargs)

    def daemon_version(self, **kwargs):
        return self._run("daemon version", **kwargs)

    def debug_refresh(self, **kwargs):
        return self._run("debug refresh", **kwargs)

    def version(self, **kwargs):
        return self._run("--version", **kwargs)
