#!/usr/bin/env python3

# Components
from ..system.platform import Platform

# Base class
class Base:

    # Members
    _child = None

    # Constructor
    def __init__(self, command):

        # Virtual method
        raise NotImplementedError() # pragma: no cover

    # Read
    def _read(self):

        # Virtual method
        raise NotImplementedError() # pragma: no cover

    # Is alive
    def isalive(self):

        # Result
        return self._child.isalive()

    # Read
    def read(self, strips=None):

        # Read stream
        while True:

            # Acquire output
            output = self._read()

            # Interrupted stream
            if not output:
                break

            # Print stream
            if isinstance(output, (bytes, str)):
                if isinstance(output, bytes):
                    output = output.decode('utf-8', errors='ignore')
                output = output.replace('\x1b[6n', '')
                if strips: # pragma: no cover
                    for strip in strips:
                        output = output.replace(strip, '')
                print(output, end='')
                Platform.flush()

            # Lines lines
            elif isinstance(output, list): # pragma: no cover
                for line in output:
                    if isinstance(line, bytes):
                        line = line.decode('utf-8', errors='ignore')
                    line = line.replace('\x1b[6n', '')
                    if strips: # pragma: no cover
                        for strip in strips:
                            line = line.replace(strip, '')
                    print(line)
                Platform.flush()

    # Send
    def send(self, key):

        # Send key
        self._child.send(key)

    # Status
    def status(self):

        # Process status
        return self._child.exitstatus

    # Terminate
    def terminate(self, force=False):

        # Terminate process
        self._child.terminate(force=force)
