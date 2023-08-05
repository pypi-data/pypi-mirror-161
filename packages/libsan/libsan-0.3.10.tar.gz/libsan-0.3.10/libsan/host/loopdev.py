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

"""loopdev.py: Module to manipulate loop devices using losetup."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import libsan.host.linux
import libsan.misc.size
from libsan.host.cmdline import run
import os
import re  # regex
import sys


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    return


def _get_loop_path(name):
    loop_path = name
    if "/dev/" not in name:
        loop_path = "/dev/" + name

    return loop_path


def _get_image_file(name, image_path):
    image_file = "%s/%s.img" % (image_path, name)
    return image_file


def _standardize_name(name):
    """
    Make sure use same standard for name, for example remove /dev/ from it if exists
    """
    if not name:
        _print("FAIL: _standardize_name() - requires name as parameter")
        return None
    return name.replace("/dev/", "")


def create_loopdev(name=None, size=1024, image_path="/var/tmp", reuse_file=False):
    """
    Create a loop device
    Parameters:
    \tname:         eg. loop0 (optional)
    \tsize:         Size in MB (default: 1024MB)
    \timage_path:   Path to store the image (default: /var/tmp)
    \treuse_file:   Reuse a previous image file (default: False)
    """
    #    name = args['name']
    #    if name is None:
    #        name = "loop0"

    #    size = args['size']
    #    if size is None:
    #        size = 1024

    if not name:
        cmd = "losetup -f"
        retcode, output = run(cmd, return_output=True, verbose=False)
        if retcode != 0:
            _print("FAIL: Could not find free loop device")
            print(output)
            return None
        name = output
    name = _standardize_name(name)

    fname = _get_image_file(name, image_path)
    print("INFO: Creating loop device %s with size %d" % (fname, size))

    if not reuse_file and os.path.isfile(fname):
        print("INFO: Deleting file %s" % fname)
        # If for some reason the file exist and we don't want reuse, delete it.
        run("rm -f %s" % fname)

    # make sure we have enough space to create the file
    free_space_bytes = libsan.host.linux.get_free_space(image_path)
    # Convert the size given in megabytes to bytes
    size_bytes = int(libsan.misc.size.size_human_2_size_bytes("%sMiB" % size))
    if free_space_bytes <= size_bytes:
        _print("FAIL: Not enough space to create loop device with size %s"
               % libsan.misc.size.size_bytes_2_size_human(size_bytes))
        _print("available space: %s" % libsan.misc.size.size_bytes_2_size_human(free_space_bytes))
        return None
    print("INFO: Creating file %s" % fname)
    # cmd = "dd if=/dev/zero of=%s seek=%d bs=1M count=0" % (fname, size)
    cmd = "fallocate -l %sM %s" % (size, fname)
    try:
        # We are just creating the file, not writting zeros to it
        retcode = run(cmd)
        if retcode != 0:
            _print("command failed with code %s" % retcode)
            _print("FAIL: Could not create loop device image file")
            return None
    except OSError as e:
        print("command failed: ", e, file=sys.stderr)
        return None

    loop_path = _get_loop_path(name)
    # detach loop device if it exists
    detach_loopdev(loop_path)

    # Going to associate the file to the loopdevice
    cmd = "losetup %s %s" % (loop_path, fname)
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: Could not create loop device")
        return None

    return loop_path


def delete_loopdev(name):
    """
    Delete a loop device
    Parameters:
    \tname:     eg. loop0 or /dev/loop0
    """
    if not name:
        _print("FAIL: delete_loopdev() - requires name parameter")
        return False

    print("INFO: Deleting loop device %s" % name)
    name = _standardize_name(name)

    loop_path = _get_loop_path(name)

    # find image file
    fname = get_loopdev_file(loop_path)
    if fname is None:
        _print("WARN: could not find loopdev named %s" % name)
        # loopdev does not exist, nothing to do
        return True

    # detach loop device if it exists
    if not detach_loopdev(name):
        _print("FAIL: could not detach %s" % loop_path)
        return False

    if os.path.isfile(fname):
        cmd = "rm -f %s" % fname
        retcode = run(cmd)
        if retcode != 0:
            _print("FAIL: Could not delete loop device file %s" % fname)
            return False

    # check if loopdev file is deleted as it sometimes remains
    if os.path.isfile(fname):
        _print("FAIL: Deleted loop device file %s but it is still there" % fname)
        return False

    return True


# show loop devices
def list_loopdev():
    retcode, output = run("losetup -a", return_output=True)
    return retcode, output


# Return all loop devices
def get_loopdev():
    # example of output on rhel-6.7
    # /dev/loop0: [fd00]:396428 (/var/tmp/loop0.img)
    retcode, output = run("losetup -a | awk '{print$1}'", return_output=True, verbose=False)
    # retcode, output = run("losetup -l | tail -n +2", return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: get_loopdev failed to execute")
        print(output)
        return None

    devs = None
    if output:
        devs = output.split("\n")
        # remove the ":" character from all devices
        devs = [d.replace(':', "") for d in devs]

    return devs


# Return loop device file for given path
def get_loopdev_file(loop_path):
    # example of output on rhel-6.7
    # /dev/loop0: [fd00]:396428 (/var/tmp/loop0.img)
    retcode, output = run("losetup -a | grep '%s:' | awk '{print$3}'" % loop_path, return_output=True, verbose=False)
    if retcode != 0:
        _print("FAIL: get_loopdev_file failed to execute")
        print(output)
        return None

    if output:
        # remove the "(" and ")" character from device
        dev = output[1:-1]
    else:
        _print("WARN: get_loopdev_file failed to requested loopdev")
        return None

    return dev


def detach_loopdev(name=None):
    cmd = "losetup -D"
    if name:
        devs = get_loopdev()
        if not devs:
            # No device was found
            return False

        name = _standardize_name(name)

        # Just try to detach if device is connected, otherwise ignore
        # print "INFO: Checking if ", loop_path, " exists, to be detached"
        dev_path = _get_loop_path(name)
        if dev_path in devs:
            cmd = "losetup -d %s" % dev_path
        else:
            # if loop device does not exist just ignore it
            return True

    # run losetup -D or -d <device>
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: Could not detach loop device")
        return False

    return True
