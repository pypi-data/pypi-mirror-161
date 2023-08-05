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


"""fio.py: Module to run FIO util."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import os
import re  # regex
import subprocess
import sys
import libsan.host.linux
from libsan.host.cmdline import run

fio_default_options = {
    "rw": "randrw",      # Type of I/O pattern. Supported(read, write, trim, randread, randwrite, rw, randrw, trimwrite)
    "name": "fio_test",  # signalling the start of a new job.
    "filename": None,    # device or filename
    "direct": 1,         # If true, use non-buffered I/O (usually O_DIRECT)
    "iodepth": 1,        # Number  of  I/O  units  to keep in flight against the file. Note that increasing
                         # iodepth beyond 1 will not affect synchronous ioengines
    "runtime": None,     # Terminate processing after the specified number of seconds.
    "size": None,        #
    "time_based": None,  # If given, run for the specified runtime duration even if the files are
                         # completely read or written.
    "numjobs": 1,        # Number of clones (processes/threads performing the same workload) of this job
    "bs": "4k",          # lock  size for I/O units.
    "verify": None       # Method  of verifying file contents after each iteration of the job
}                        # (supports: md5 crc16 crc32 crc32c crc32c-intel crc64 crc7 sha256 sha512 sha1 xxhash)

fio_default_verify_options = {
    "verify_backlog": 1024,  # fio will write only N blocks before verifying these blocks.
                             # Set to None to verify after all IO is written
    "verify_fatal": 1,       # If true, exit the job on the first observed verification failure
    "do_verify": 1
}


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    sys.stdout.flush()
    return


def _has_fio():
    if run("which fio", verbose=False) != 0:
        return False
    return True


def install_fio():
    pkg = "fio"
    if libsan.host.linux.install_package(pkg):
        return True
    if run("fio >/dev/null 2>&1") == 1:
        return True
    # Try to install FIO from source
    return install_fio_from_src()


def install_fio_from_src():
    git_url = "git://git.kernel.org/pub/scm/linux/kernel/git/axboe/fio.git"

    if not libsan.host.linux.install_package("libaio-devel"):
        _print("FAIL: Could not install libaio-devel")
        return False

    if not libsan.host.linux.install_package("zlib-devel"):
        _print("FAIL: Could not install zlib-devel")
        return False

    if run("git clone %s" % git_url) != 0:
        _print("FAIL: Could not clone fio repo")
        return False

    _print("INFO: Installing FIO")
    if run("cd fio && ./configure && make && make install") != 0:
        _print("FAIL: Could not build fio")
        return False

    if not _has_fio():
        _print("FAIL: FIO did not install properly")
        return False
    return True


def fio_stress(of, verbose=False, return_output=False, **fio_opts):
    # For compatibilty with tests using other named parameters
    convert_param = {'io_type': 'rw',
                     'time': 'runtime',
                     'thread': 'numjobs',
                     'log_file': 'output'}

    for key in convert_param:
        if key in list(fio_opts.keys()):
            fio_opts[convert_param[key]] = fio_opts.pop(key)

    fio_opts['filename'] = of

    for opt in fio_default_options:
        if opt not in list(fio_opts.keys()):
            fio_opts[opt] = fio_default_options[opt]

    if int(fio_opts["numjobs"]) > 1:
        fio_opts["group_reporting"] = 1

    if fio_opts['verify'] is not None:
        fio_opts.update(fio_default_verify_options)

    if not _has_fio():
        _print("FATAL: fio is not installed")
        return False

    fio_param = ""
    for key in list(fio_opts.keys()):
        if fio_opts[key]:
            fio_param += "--%s='%s' " % (key, fio_opts[key])

    if "fiojob" in list(fio_opts.keys()):
        fio_param = "%s --filename=%s" % (fio_opts["fiojob"], fio_opts["filename"])

    cmd = "fio %s" % fio_param
    # Append time information to command
    date = "date \"+%Y-%m-%d %H:%M:%S\""
    p = subprocess.Popen(date, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, _ = p.communicate()
    stdout = stdout.decode('ascii', 'ignore')
    stdout = stdout.rstrip("\n")
    if not verbose:  # If verbose option is selected, the run() will print the fio command.
        _print("INFO: [%s] FIO Running: '%s'..." % (stdout, cmd))

    # _print("INFO: Running %s" % cmd)
    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: running FIO")
        print(output)
        if return_output:
            return False, None
        return False

    _print("INFO: FIO executed successfully")
    if return_output:
        return True, output

    return True


def fio_stress_background(of, verbose=False, **fio_opts):
    """Run FIO on background"""
    newpid = os.fork()
    if newpid == 0:
        # Trying to flush stdout to avoid duplicated lines when running hba_test
        sys.stdout.flush()
        rt = fio_stress(of, verbose=verbose, **fio_opts)
        if not rt:
            os._exit(1)  # pylint: disable=W0212
        os._exit(0)  # pylint: disable=W0212
    else:
        sys.stdout.flush()
        _print("INFO: fio_stress_background(): Child thread %d is running FIO Stress" % newpid)
        return newpid
