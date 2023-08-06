#!/usr/bin/env python3

# Standard libraries
from signal import SIGTERM

# Modules libraries
from pexpect import EOF, TIMEOUT # pylint: disable=import-error
from pexpect.popen_spawn import PopenSpawn # pylint: disable=import-error

# Components
from .base import Base

# PexpectPopen class
class PexpectPopen(Base):

    # Constructor
    def __init__(self, command): # pylint: disable=super-init-not-called

        # Spawn command
        self._child = PopenSpawn(command)

    # Read
    def _read(self): # pylint: disable=duplicate-code

        # Acquire output
        try:
            return self._child.read_nonblocking(size=1024, timeout=1)
        except (EOF, TIMEOUT):
            pass

        # Empty output
        return None

    # Is alive
    def isalive(self):

        # Result
        return not self._child.terminated

    # Terminate
    def terminate(self, force=False):

        # Terminate process
        if force:
            try:
                self._child.kill(sig=SIGTERM)
            except PermissionError: # pragma: no cover
                pass

        # Wait process
        self._child.wait()
