from __future__ import absolute_import, division, print_function, unicode_literals

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

"""qemu_img.py: Module to manipulate disk image using QEMU disk image utility."""

__author__ = "Filip Suba"
__copyright__ = "Copyright (c) 2018 Red Hat, Inc. All rights reserved."

import os
import re  # regex
import libsan.host.linux as linux
from libsan.host.cmdline import run

_QCOW_SUPPORTED_OPTIONS = ["compat", "backing_file", "encryption", "cluster_size",
                           "preallocation", "lazy_refcounts"]


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    return


def _get_package_name():
    return "qemu-img"


def _get_image_file(name, image_path):
    return "%s/%s.img" % (image_path, name)


def get_qcow_supported_options():
    """
    Return supported options for qcow image.
    :return: List of strings.
    """
    return _QCOW_SUPPORTED_OPTIONS


def install_qemu_img():
    """
    Install qemu-img tool
    :return:
    \tTrue: If qemu-img is installed correctly
    \tFalse: If some problem happened
    """
    if not linux.install_package(_get_package_name()):
        _print("FAIL: Could not install %s" % _get_package_name())
        return False
    return True


def qemu_create(filename, size="1024", fmt=None, img_path="/var/tmp", **options):
    """
    Create the new disk image
    :param filename: is a disk image filename
    :param size: is the disk image size in bytes
    :param fmt: is the disk image format
    :param img_path: is the full path to output directory
    :param options: see supported options for a qcow image
    :return:
    True: if success
    False: in case of failure
    """
    if not linux.is_installed(_get_package_name()):
        install_qemu_img()
    if not filename:
        _print("FAIL: qemu_create() requires parameter filename")
        return False
    if img_path:
        filename = _get_image_file(filename, img_path)
    cmd = _get_package_name() + " create "
    if fmt is not None:
        cmd += "-f %s" % fmt
    if fmt == "qcow2" and options:
        cmd += " -o "
        option = [str(i) + "=" + str(options[i]) for i in options if i in _QCOW_SUPPORTED_OPTIONS]
        cmd += ",".join(option)
    cmd += " %s %s" % (filename, size)
    ret = run(cmd)
    if ret != 0:
        _print("FAIL: Could not create disk image.")
        return False
    return True


def delete_image(name, image_path="/var/tmp"):
    """
    Delete the disk image
    :param name: is the image filename
    :param image_path: is the full path to the image directory
    :return:
    True: if success
    False: in case of failure
    """
    if not name:
        _print("FAIL: delete_image() - requires name parameter")
        return False

    print("INFO: Deleting image device %s" % name)
    fname = _get_image_file(name, image_path)
    if os.path.isfile(fname):
        cmd = "rm -f %s" % fname
        retcode = run(cmd)
        if retcode != 0:
            _print("FAIL: Could not delete image disk file %s" % fname)
            return False
    return True
