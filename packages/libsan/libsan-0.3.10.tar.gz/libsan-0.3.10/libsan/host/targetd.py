# -*- coding: utf-8 -*-

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

"""targetd.py: Module to manipulate functionality provided by targetd."""

from __future__ import absolute_import, division, print_function, unicode_literals

__author__ = "Filip Suba"
__copyright__ = "Copyright (c) 2018 Red Hat, Inc. All rights reserved."

import re  # regex
import os
import libsan.host.linux as linux
from libsan.host.cmdline import run

targetd_cfg = "/etc/target/targetd.yaml"
targetd_directory = "/etc/target/"


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


def ssl_change(enable=False):
    """
    Changes variable ssl in targetd config to "false".
    :return:
    True: Variable changed successfully.
    False: Targetd config does not exist.
    """
    change = False
    if not os.path.isfile(targetd_cfg):
        _print("FAIL: Targetd config does not exist.")
        return False
    with open(targetd_cfg, encoding='UTF-8') as config:
        lines = config.readlines()
    for line in lines:
        if line.startswith("ssl:") and str(enable).lower() not in line:
            change = True
            lines[lines.index(line)] = "ssl: %s\n" % str(enable).lower()
            break

    if change:
        with open(targetd_cfg, "w", encoding='UTF-8') as config:
            config.writelines(lines)
    return True


def set_password(password=None):
    """
    Function for setting password in targetd config.
    :return:
    True: Password changed successfully.
    False: Targetd config does not exist.
    """
    pass_line = "password:\n"

    if not os.path.isfile(targetd_cfg):
        _print("FAIL: Targetd config does not exist.")
        return False
    with open(targetd_cfg, encoding='UTF-8') as config:
        lines = config.readlines()
    if password:
        pass_line = "password: %s\n" % password
    for line in lines:
        if line.startswith("password:"):
            lines[lines.index(line)] = pass_line
            break

    with open(targetd_cfg, "w", encoding='UTF-8') as config:
        config.writelines(lines)
    return True


def remove_file(name):
    """
    Removes a file from targetd directory.
    :param name: Name of a file in targetd directory
    :return:
    True: File removed successfully.
    False: Could not find SSL key in targetd directory or Could not remove SSL key.
    """
    if not os.path.isfile(targetd_directory + name):
        _print("FAIL: Could not find SSL key in /etc/target")
        return False
    cmd = "rm -f %s%s" % (targetd_directory, name)
    ret = run(cmd)
    if ret != 0:
        _print("FAIL: Could not remove SSL key: %s" % name)
        return False
    return True


def gen_ssl_key(name):
    """
    Generates new private key and exports it as ".pem" file.
    :param name: Name for the export file.
    :return:
    True: Private key exported successfully.
    False: Could not generate SSL key or Could not change permissions.
    """

    print("Changing working directory to %s" % targetd_directory)
    pwd = os.path.abspath(os.curdir)
    os.chdir(targetd_directory)
    if os.path.abspath(os.curdir) != targetd_directory[:-1]:
        _print("FAIL: Could not change working directory to %s" % targetd_directory)
        return False

    cmd = "openssl genrsa -out %s.pem 2048" % (targetd_directory + name)
    ret = run(cmd)
    if ret != 0:
        _print("FAIL: Could not generate SSL key with name %s" % name)
        return False

    print("Changing working directory to %s" % pwd)
    os.chdir(pwd)
    if os.path.abspath(os.curdir) != pwd:
        _print("FAIL: Could not change working directory to %s" % pwd)
        return False

    cmd = "chmod 600 %s%s.pem" % (targetd_directory, name)
    ret = run(cmd)
    if ret != 0:
        _print("FAIL: Could not change permissions to 600")
        return False
    return True


def gen_ssl_cert(name, key_name):
    """
    Generates certificate and exports it as ".pem" file. Function for testing only!
    :param name: Name for the export file.
    :param key_name: Name of a private key to use.
    :return:
    True: Certificate exported successfully.
    False: Provided key does not exist.
           Could not change permissions.
           Could not change working directory.
    """

    key = targetd_directory + key_name
    cert = targetd_directory + name

    print("Changing working directory to %s" % targetd_directory)
    pwd = os.path.abspath(os.curdir)
    os.chdir(targetd_directory)
    if os.path.abspath(os.curdir) != targetd_directory[:-1]:  # removes slash at the end of targetd_directory path
        _print("FAIL: Could not change working directory to %s" % targetd_directory)
        return False

    cmd = "openssl req -new -x509 -subj /CN=CZ -key %s.pem -out %s.pem -days 9999" % (key, cert)
    ret = run(cmd)
    if ret != 0:
        _print("FAIL: Could not generate SSL cert with name %s and SSL key %s" % (cert, key))
        return False

    print("Changing working directory to %s" % pwd)
    os.chdir(pwd)
    if os.path.abspath(os.curdir) != pwd:
        _print("FAIL: Could not change working directory to %s" % pwd)
        return False

    cmd = "chmod 600 %s.pem" % cert
    ret = run(cmd)
    if ret != 0:
        _print("FAIL: Could not change permissions to 600")
        return False

    return True


def tls_status():
    """
    Checking if TLS is enabled.
    :return:
    True: TLS is enabled.
    False: TLS is disabled.
    """
    cmd = 'systemctl status targetd | grep "TLS yes"'
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: TLS is not enabled")
        return False
    return True


def targetd_status(retcode=0):
    """
    Checks targetd service status.
    :param retcode: Expected return code.
    :return:
    True: Expected return code is equal to actual return code.
    False: Return code is different than expected.
    """
    ret = linux.service_status("targetd")
    if retcode != ret:
        _print("FAIL: Return code is different than expected!")
        print("Expected ret: %s, got: %s" % (retcode, ret))
        return False
    return True
