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


"""dt.py: Module to run DT util."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import sys
import os
import subprocess
import libsan.host.linux
from libsan.host.cmdline import run


DT_DEFAULT_OPTION = {"flags": "direct",
                     "oncerr": "abort",
                     "iodir": "forward",
                     "align": "0",
                     "min": "b",
                     "max": "256k",
                     "pattern": "incr",
                     "dispose": "keep"}

DT_RW_OPTION = DT_DEFAULT_OPTION
DT_RW_OPTION.update({"disable": "eof,pstats"})

DT_INIT_OPTION = DT_DEFAULT_OPTION
DT_INIT_OPTION.update({"disable": "eof,pstats,compare,verify"})

DT_VERIFY_OPTION = DT_DEFAULT_OPTION
DT_VERIFY_OPTION.update({"disable": "eof,pstats"})

default_timeout = "4h"
default_verbose = 0


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    sys.stdout.flush()
    return


def _is_device(path):
    path_regex = re.compile("^/dev/")
    m = path_regex.match(path)
    if m:
        return True
    return False


def _has_dt():
    if run("which dt", verbose=False) != 0:
        return False
    return True


def install_dt():
    if _has_dt():
        return True

    if libsan.host.linux.install_package("dt"):
        return True

    _print("FAIL: Could not install dt")
    return False


def dt_stress(of, log=None, time=None, thread=None, limit=None,
              timeout=None, verbose=False, log_file=None, io_options=None):
    """
    Execute DT with IO paramters.
    The arguments are:
    \tof            = Output file or path
    \ttime          = how long dt should run
    \tthread        = The number of disk slices to test.
    \tlimit         = The number of bytes to transfer.
    \tverbose       = If should print command output or not. default: False
    \tio_options    = If want to change default io option parameters. Must be as dict format
    """
    if not io_options:
        io_options = DT_RW_OPTION
    if not _has_dt():
        _print("FATAL: dt is not installed")
        return False

    if log:
        pass
    if timeout:
        pass
    if log_file:
        pass

    io_options["slices"] = thread
    if not io_options["slices"]:
        if _is_device(of):
            # We run 16 threads by default if we are running to a device
            io_options["slices"] = "16"
        else:
            io_options["slices"] = "0"
            # if not limit:
            #    _print("FAIL:  dt_stress(): limit_size must be defined when using file")
            #    return False

    if time:
        io_options["runtime"] = time

    if limit:
        io_options["limit"] = limit

    dt_option = ""
    for key in list(io_options.keys()):
        dt_option += "%s=%s " % (key, io_options[key])
    dt_option += "of=%s" % of

    cmd = "dt %s" % dt_option
    # Append time information to command
    date = "date \"+%Y-%m-%d %H:%M:%S\""
    p = subprocess.Popen(date, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, _ = p.communicate()
    stdout = stdout.decode('ascii', 'ignore')
    stdout = stdout.rstrip("\n")
    _print("INFO: [%s] DT Running: '%s'..." % (stdout, cmd))

    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: running DT")
        print(output)
        return False
    _print("INFO: DT executed successfully")
    return True


def dt_stress_background(of, log=None, time=None, thread=None, limit=None,
                         timeout=None, verbose=False, log_file=None):
    """Run DT on background"""
    newpid = os.fork()
    if newpid == 0:
        # Trying to flush stdout to avoid duplicated lines when running hba_test
        sys.stdout.flush()
        rt = dt_stress(of, log=log, time=time, thread=thread, limit=limit,
                       timeout=timeout, verbose=verbose, log_file=log_file)
        if not rt:
            os._exit(1)  # pylint: disable=W0212
        # using os._exit() as sys.exit trigger exception
        os._exit(0)  # pylint: disable=W0212
    else:
        sys.stdout.flush()
        _print("INFO: dt_stress_background(): Child thread %d is running DT Stress" % newpid)
        return newpid


def dt_init_data(of, log=None, limit=None, timeout=None, verbose=False):
    """
    Usage

        dt_init_data(output_file)
        dt_init_data(of=output_file)
        dt_init_data(of=output_file,log=log)
        dt_init_data(of=output_file,limit=limit_size)
        dt_init_data(of=output_file,timeout=time_out)
        dt_init_data(of=output_file,verbose=flag_verbose)
    Purpose
        Using dt incr patter to write data into output_file. Normally pair with
        dt_verify_data().
        time_out default value is 4h which means I/O could only run 4 hours.
        Set it to 0 if you don't want timeout.
    Parameter
        output_file        # DT I/O output, like "/dev/sda" or "/var/tmp/dt_test.img"
        log                # the sting which hold all log of dt.
        time_in_sec        # time for seconds.
        thread_num         # count of dt thread for I/O stress.
        limit_size         # limit I/O size. Mush have for filesystem stress.
        time_out           # the maximum time dt command can run.
        flag_verbose       # whether dt command output to stdout. default is 0
    Returns
        1
            or
        undef
    Exceptions
        1. no dt installed.
    """
    if not _has_dt():
        _print("FATAL: dt_init_data() - dt is not installed")
        return False

    if not _is_device(of) and not limit:
        _print("FAIL:  dt_init_data(): limit_size must be defined when using file")
        return False

    if log:
        pass

    if timeout:
        pass

    dt_option = ""
    for key in list(DT_INIT_OPTION.keys()):
        dt_option += "%s=%s " % (key, DT_INIT_OPTION[key])

    dt_option += "of=%s" % of

    if limit:
        dt_option += " limit=%s" % limit

    cmd = "dt %s" % dt_option
    # Append time information to command
    date = "date \"+%Y-%m-%d %H:%M:%S\""
    p = subprocess.Popen(date, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, _ = p.communicate()
    stdout = stdout.decode('ascii', 'ignore')
    stdout = stdout.rstrip("\n")
    _print("INFO: [%s] DT Running: '%s'..." % (stdout, cmd))

    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: running DT")
        print(output)
        return False
    _print("INFO: DT initialized data successfully")
    return True


def dt_verify_data(in_file, log=None, limit=None, timeout=None, verbose=False):
    """
    Usage

        dt_verify_data(input_file)
        dt_verify_data(in_file=output_file)
        dt_verify_data(in_file=output_file,log=log)
        dt_verify_data(in_file=output_file,limit=limit_size)
        dt_verify_data(in_file=output_file,timeout=time_out)
        dt_verify_data(in_file=output_file,verbose=flag_verbose)
    Purpose
        Using dt incr patter to write data into input_file. Normally pair with
        dt_verify_data().
        $time_out default value is 4h which means I/O could only run 4 hours.
        Set it to 0 if you don't want timeout.
    Parameter
        input_file         # DT I/O input, like "/dev/sda" or "/var/tmp/dt_test.img"
        log                # the sting which hold all log of dt.
        time               # any format of time: '30m' or '60s'
        time_in_sec        # time for seconds.
        thread_num         # count of dt thread for I/O stress.
        limit_size         # limit I/O size. Mush have for filesystem stress.
        time_out           # the maxmum time dt command can run.
        flag_verbose       # whether dt command input to stdout. default is 0
    Returns
        1
            or
        undef
    Exceptions
        1. no dt installed.
    """
    if not _has_dt():
        _print("FATAL: dt_init_data() - dt is not installed")
        return False

    if not _is_device(in_file) and not limit:
        _print("FAIL:  dt_init_data(): limit_size must be defined when using file")
        return False

    if log:
        pass

    if timeout:
        pass

    dt_option = ""
    for key in list(DT_INIT_OPTION.keys()):
        dt_option += "%s=%s " % (key, DT_VERIFY_OPTION[key])
    dt_option += "if=%s" % in_file

    if limit:
        dt_option += " limit=%s" % limit

    cmd = "dt %s" % dt_option
    # Append time information to command
    date = "date \"+%Y-%m-%d %H:%M:%S\""
    p = subprocess.Popen(date, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, _ = p.communicate()
    stdout = stdout.decode('ascii', 'ignore')
    stdout = stdout.rstrip("\n")
    _print("INFO: [%s] DT Running: '%s'..." % (stdout, cmd))

    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("FAIL: running DT")
        print(output)
        return False
    _print("INFO: DT verified data successfully")
    return True
