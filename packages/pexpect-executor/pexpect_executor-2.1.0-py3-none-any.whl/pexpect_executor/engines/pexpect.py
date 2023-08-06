#!/usr/bin/env python3

# Modules libraries
from pexpect import EOF, spawn, TIMEOUT # pylint: disable=import-error

# Components
from .base import Base

# Pexpect class
class Pexpect(Base):

    # Constructor
    def __init__(self, command): # pylint: disable=super-init-not-called

        # Spawn command
        self._child = spawn('sh', ['-c', command])

    # Read
    def _read(self): # pylint: disable=duplicate-code

        # Acquire output
        try:
            return self._child.read_nonblocking(size=1024, timeout=1)
        except (AttributeError, EOF, TIMEOUT):
            pass

        # Empty output
        return None
