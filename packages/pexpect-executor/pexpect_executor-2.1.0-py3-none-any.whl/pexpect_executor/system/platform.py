#!/usr/bin/env python3

# Standard libraries
from os import environ, sep
from sys import platform, stdin, stdout

# Platform, pylint: disable=too-few-public-methods
class Platform:

    # Constants
    IS_ANDROID = ('ANDROID_ROOT' in environ)
    IS_LINUX = (platform in ['linux', 'linux2'])
    IS_MAC_OS = (platform in ['darwin'])
    IS_WINDOWS = (platform in ['win32', 'win64'])

    # Separators
    PATH_SEPARATOR = sep

    # TTYs
    IS_TTY_STDIN = stdin.isatty() and stdin.encoding != 'cp1252'
    IS_TTY_STDOUT = stdout.isatty()

    # Flush
    @staticmethod
    def flush():
        print('', end='', flush=Platform.IS_TTY_STDOUT)
