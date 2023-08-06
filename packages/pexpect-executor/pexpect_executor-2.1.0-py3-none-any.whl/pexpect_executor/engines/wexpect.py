#!/usr/bin/env python3

# Standard libraries
# from os import environ

# Modules libraries
# environ['WEXPECT_SPAWN_CLASS'] = 'SpawnPipe'
from wexpect import EOF, spawn, TIMEOUT # pylint: disable=import-error

# Components
from .base import Base

# Wexpect class
class Wexpect(Base):

    # Constructor
    def __init__(self, command): # pylint: disable=super-init-not-called

        # Spawn command
        self._child = spawn(command)

        # Acquire initial output
        try:
            self._child.expect(EOF, timeout=0)
        except TIMEOUT: # pragma: no cover
            pass

        # Configure timeout
        self._child.timeout = 1

    # Read
    def _read(self):

        # Acquire output
        try:
            output = self._child.read_nonblocking(size=1024)
            if self._child.before: # pragma: no cover
                output = self._child.before + output
        except EOF:
            output = self._child.before
        except TIMEOUT: # pragma: no cover
            output = self._child.before

        # Handle output
        if output: # pragma: no cover

            # Stream line
            if '\n' in output:
                return output

            # Adapt lines
            length = 80
            return [output[i:i + length] for i in range(0, len(output), length)]

        # Empty output
        return None

    # Send
    def send(self, key):

        # Send key
        try:
            self._child.send(key)
        except EOF:
            pass

    # Status
    def status(self):

        # Process terminated
        if self._child.exitstatus is None:
            return 0 if self._child.flag_eof else 1

        # Process status
        return self._child.exitstatus # pragma: no cover

    # Terminate
    def terminate(self, force=False):

        # Terminate process
        if force:
            self._child.terminate()

        # Wait process
        else:
            self._child.wait()
