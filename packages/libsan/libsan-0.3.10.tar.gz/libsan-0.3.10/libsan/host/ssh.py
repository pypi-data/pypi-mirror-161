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

"""ssh.py: Module to handle ssh session."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import socket
import time
from ssh2.exceptions import AuthenticationError, Timeout  # pylint: disable=E0611
from ssh2.exceptions import SocketRecvError, SocketDisconnectError  # pylint: disable=E0611
from ssh2.session import Session  # pylint: disable=E0611
from ssh2.utils import wait_socket  # pylint: disable=E0611

LIBSSH2_ERROR_EAGAIN = -37


def _print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def _check_timeout_value(timeout):
    # Do not overflow C long int
    return timeout if timeout <= 2**32 else 2**32


def _connect_socket(host, port, timeout=5, try_number=1):
    # This function is to handle SocketDisconnectError.
    # When we get it, we need to start the whole socket operation again.
    def _retry(_host, _port, _timeout, _try_number):
        time.sleep(5)
        return _connect_socket(_host, _port, _timeout, _try_number + 1)

    if try_number == 101:
        _print("FAIL: Could not establish socket connection after 100 tries.")
        return None
    try:
        # Create socket connection
        sock = socket.create_connection((host, port), timeout)
        # Create a session
        s = Session()
        s.handshake(sock)
    except SocketDisconnectError:
        _print("DEBUG: Got SocketDisconnectError, trying to connect to socket again after 5 seconds. %s/100"
               % try_number)
        return _retry(host, port, timeout, try_number)
    except socket.error as e:
        print("DEBUG: Got socket.error: '%s', retrying connection to socket after 5 seconds. %s/100" % (e, try_number))
        return _retry(host, port, timeout, try_number)
    return s


def connect(host, port=22, user=None, passwd=None, max_attempt=5):
    """
    Connect to a host using ssh
    The arguments are:
    \thost:                         Hostname
    \tport:                         Port number used to connect
    \tuser:                         username
    \tpasswd:                       Password
    \tmax_attempt                   Maximum attempt to connect (default:5)
    Returns:
    \tssh:                          ssh session
    \tNone:                         If there was some problem
    """

    # paramiko works this way
    if host == "":
        return None
    elif host is None:
        host = ""

    if not user:
        _print("FAIL: connect() needs \"user\" parameter")
        return None
    if not passwd:
        _print("FAIL: connect() needs \"passwd\" parameter")
        return None

    i = 0

    s = _connect_socket(host, port)

    while True:
        # Try to authenticate user
        try:
            s.userauth_password(user, passwd)
            break
        except AuthenticationError:
            print("Authentication failed when connecting to %s" % host)
            return None
        except (ValueError, OSError):
            print("Could not SSH to %s, waiting for it to start" % host)
            i += 1
        except (SocketDisconnectError, socket.error):
            print("Socket got disconnected in between, connecting again.")
            s = _connect_socket(host, port)
            i += 1
        except Exception as e:
            print("Could not SSH to %s" % host)
            print("Exception: %s" % e)
            return None
        # If we could not connect within set number of tries
        if i == max_attempt:
            print("Could not connect to %s. Giving up" % host)
            return None
        else:
            # Wait before next attempt
            time.sleep(2)
    return s


def disconnect(ssh_session):
    """
    Disconnect from a ssh session
    The arguments are:
    \tssh_session:                  ssh session, it is return by connect()
    Returns:
    \tTrue:                         Always
    """
    ssh_session.disconnect()
    return True


def read_chan(sock, ssh_session, chan, buff_size=1024, timeout=None, stderr=False):
    # Read channel output in non blocking way
    timeout = timeout or 2**32
    func = chan.read
    if stderr:
        func = chan.read_stderr
    size, tmp_buf = func(buff_size)
    time_end = time.time() + timeout
    while size == LIBSSH2_ERROR_EAGAIN:
        wait_socket(sock, ssh_session, timeout=timeout)
        size, tmp_buf = func(buff_size)
        if time.time() > time_end:
            raise Timeout
    return size, tmp_buf


def _execute_function(sock, ssh_session, func, **kwargs):
    # This executes function when the socket is not blocked (LIBSSH2_ERROR_EAGAIN)
    ret = func(**kwargs)
    while ret == LIBSSH2_ERROR_EAGAIN:
        wait_socket(sock, ssh_session)
        ret = func(**kwargs)
    return ret


def _execute(chan, command):
    # Wrapper for chan.execute to take keyword argument
    return chan.execute(command)


def run_cmd(ssh_session, cmd, verbose=True, return_output=False, invoke_shell=False, timeout=None, cr="\n",
            expect=None, command_expect=None):
    """
    Run a command to a specific ssh session
    The arguments are:
    \tssh_session:                  ssh session, it is returned by connect()
    \\tcmd:                         command to be executed
    \\tinvoke_shell:                run command in interactive shell
    \\texpect:                      if invoke_shell is true we try to read until find expect pattern
    \\tcommand_expect:              if multiple commands are sent with shell and expect, this is the patter to wait for
    Returns:
    \texit status:                  command status code, always 0 with interactive shell
    \tNone:                         If there was some problem
    """
    error = 0
    if timeout:
        # paramiko required timeout in secs, ssh2-python in milisecs
        timeout = _check_timeout_value(int(timeout * 1000))
    command_expect = command_expect or expect

    # This is for nonblocking mode, which allows to wait for socket to be ready
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssh_session.set_blocking(False)

    # by default we use exec_command to run a command as it has better control
    # when reading the buffers and supports exit code
    if not invoke_shell:
        for c in cmd if not isinstance(cmd, type("")) else [cmd]:
            chan = _execute_function(sock, ssh_session, ssh_session.open_session)
            if not chan:
                _print("FAIL: Could not create a chan")
                if return_output:
                    return 127, None
                return 127

            if timeout:
                ssh_session.set_timeout(timeout)

            if verbose:
                _print("INFO: Running ssh command '%s'" % c)
            try:
                _execute_function(sock, ssh_session, _execute, chan=chan, command=c)
            except Timeout:
                _print("FAIL: ssh - Got timeout (%ds) while executing command: '%s'" % (timeout, c))
                _execute_function(sock, ssh_session, chan.close)
                if return_output:
                    return 127, None
                return 127
            except Exception as e:
                _print("FAIL: ssh - Could not execute command: '%s'" % c)
                print("Failed due: %s" % repr(e))
                _execute_function(sock, ssh_session, chan.close)
                if return_output:
                    return 127, None
                return 127

            stdout = ""

            # keep reading stdout as long as there is anything to read
            try:
                size = 1
                while size > 0:
                    size, stdout_buf = read_chan(sock, ssh_session, chan, buff_size=1024, timeout=timeout)
                    stdout += stdout_buf.decode('ascii', 'ignore')

                # Read stderr and add it to stdout
                size = 1
                while size > 0:
                    size, stderr_buff = read_chan(sock, ssh_session, chan, buff_size=1024, timeout=timeout, stderr=True)
                    stdout += stderr_buff.decode('ascii', 'ignore')

                # The channel has to be closed to be able to get exit status
                _execute_function(sock, ssh_session, chan.close)

            except SocketRecvError:
                # Socket was closed, this happens when for example we reboot the server by this command
                pass

            exit_status = _execute_function(sock, ssh_session, chan.get_exit_status)

            if exit_status != 0:
                error += 1

            if verbose:
                print(stdout)

    else:
        # We use invoke_shell in situation where we need to run commands from a single shell
        # for example on cisco we need to run commands after configure terminal

        # Open channel
        chan = _execute_function(sock, ssh_session, ssh_session.open_session)

        # Set timeout
        if not timeout:
            timeout = 60 * 1000
        ssh_session.set_timeout(timeout)

        # Make this interactive shell
        _execute_function(sock, ssh_session, chan.pty)
        _execute_function(sock, ssh_session, chan.shell)

        tmp_buf = ""
        stdout = ""
        if expect:
            # wait for prompt
            while expect not in tmp_buf:
                try:
                    _, resp = read_chan(sock, ssh_session, chan, buff_size=9999, timeout=timeout)
                except Timeout:
                    _print("FAIL: Waiting for prompt '%s' timed out after %s seconds." % (expect, timeout))
                    resp = expect
                tmp_buf += resp.decode('ascii', 'ignore')

        else:
            # get rid of the whole header
            _execute_function(sock, ssh_session, chan.read, size=65535)

        # Handle cmd being a single string or a list of strings
        for c in cmd if not isinstance(cmd, type("")) else [cmd]:
            if verbose:
                print("INFO: ssh - sending command \"%s\"" % c)
            # Some targets need different ending symbols, for example ApCon switch needs \r, eqlogic \n\r...
            chan.write(c + cr)

            # Reading in between serves as waiting, as we are sending more commands when expecting prompt
            if expect:
                # On last command wait for normal prompt
                if c == cmd[-1]:
                    command_expect = expect
                # read until we get prompt again
                while not stdout.endswith(command_expect):
                    try:
                        size, tmp_buf = read_chan(sock, ssh_session, chan, buff_size=1024, timeout=timeout)
                    except Timeout:
                        _print("FAIL: Reading STDOUT timed out after %s seconds, did not get prompt '%s'."
                               % (timeout, command_expect))
                        tmp_buf = command_expect
                    stdout += tmp_buf.decode('ascii', 'ignore')
                # Add newline at the end to prevent the above while condition to be True before reading some data
                stdout += "\n"

        if not expect:
            # Read until we do not receive more bytes. First STDOUT, than STDERR
            size = 1
            while size > 0:
                try:
                    size, tmp_buf = read_chan(sock, ssh_session, chan, buff_size=1024, timeout=timeout)
                except Timeout:
                    _print("FAIL: Reading STDOUT ssh channel timed out after %s seconds." % timeout)
                    size, tmp_buf = (0, "")
                stdout += tmp_buf.decode('ascii', 'ignore')
            size = 1
            while size > 0:
                try:
                    size, tmp_buf = read_chan(sock, ssh_session, chan, buff_size=1024, timeout=timeout, stderr=True)
                except Timeout:
                    _print("WARN: Reading STDERR ssh channel timed out after %s seconds." % timeout)
                    size, tmp_buf = (0, "")
                stdout += tmp_buf.decode('ascii', 'ignore')

        # Close channel at the end
        chan.close()

        error = 0
        if verbose:
            print(stdout)

    if return_output:
        return error, stdout

    return error
