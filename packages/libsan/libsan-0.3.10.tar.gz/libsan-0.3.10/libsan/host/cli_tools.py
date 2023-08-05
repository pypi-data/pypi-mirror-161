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

"""cli_tools.py: Module to provide tools of wrapping command line tools for further usage."""

__author__ = "Jakub Krysl"
__copyright__ = "Copyright (c) 2018 Red Hat, Inc. All rights reserved."

import re


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


class WrongCommandException(Exception):
    def __init__(self, cmd):
        self.command = cmd
        super(WrongCommandException, self).__init__()

    def __str__(self):
        return repr(WrongCommandException.__name__ + ", caused by " + repr(self.command))


class WrongArgumentException(Exception):
    def __init__(self, arg, cmd=None, args=None):
        self.argument = arg
        self.command = cmd
        self.arguments = args
        super(WrongArgumentException, self).__init__()

    def __str__(self):
        return repr(WrongArgumentException.__name__ + ", caused by " + repr(self.argument))


class FailedCheckException(Exception):
    def __init__(self, arg=None):
        self.argument = arg
        super(FailedCheckException, self).__init__()

    def __str__(self):
        message = repr(FailedCheckException.__name__)
        if self.argument:
            message += ", caused by " + repr(self.argument)
        return message


class Wrapper(object):
    def __init__(self, commands, arguments, disable_check):
        self.commands = commands
        self.arguments = arguments
        self.disable_check = disable_check

    def _add_command(self, cmd):
        # Checks if given command is provided by CLI and returns its correct syntax
        if cmd in self.commands:
            return self.commands[cmd]
        raise WrongCommandException(cmd)

    def _get_arg(self, name):
        if not self.disable_check:
            if name in self.arguments:
                return self.arguments[name][1]
            raise WrongArgumentException(name)
        return self.arguments[name][1]

    def _get_cmd(self, name):
        if self.disable_check:
            return self.commands["all"]
        if name in self.arguments:
            return self.arguments[name][0]
        raise WrongCommandException(name)

    @staticmethod
    def _get_value(string, command, return_type=type("")):
        _value = string.split(command)[1].split()[0]
        try:
            value = return_type(_value)
        except ValueError as e:
            _print("WARN: Got ValueError: %s." % e)
            return None
        return value

    def _get_possible_arguments(self, command=None):
        # Returns possible arguments for said command if specified
        args = []
        if command:
            for key in list(self.arguments.keys()):
                if list(self.commands.keys())[list(self.commands.values()).index(command)] in self._get_cmd(key):
                    args.append(key)
        else:
            args = list(self.arguments.keys())
        return args

    @staticmethod
    def _add_value(value, command, argument):
        if argument[-1:] in ["=", "&"]:
            if argument[-1:] == "&":
                argument = argument[:-1] + " "
            if isinstance(value, list):
                # allows to use repeatable arguments as a list of values
                for val in value:
                    command += argument + "'" + str(val) + "'"
            else:
                command += argument + "'" + str(value) + "'"
        else:
            command += argument
        return command

    def _check_allowed_argument(self, arg, command):
        if arg not in self.arguments and not self.disable_check:
            raise WrongArgumentException(arg)
        cmd = command.split()[0]
        args = self._get_possible_arguments(cmd)
        if arg not in args:
            raise WrongArgumentException(arg, cmd, args)

    def _add_argument(self, arg, value, command):
        # Checks if given argument is allowed for given command and adds it to cmd string
        self._check_allowed_argument(arg, command)
        command = self._add_value(value, command, self._get_arg(arg))
        return command

    def _add_arguments(self, cmd, **kwargs):
        command = cmd
        for kwarg in kwargs:
            # skip adding this argument if the value is False
            if kwargs[kwarg] is False:
                continue
            command = self._add_argument(kwarg, kwargs[kwarg], command)
        return command
