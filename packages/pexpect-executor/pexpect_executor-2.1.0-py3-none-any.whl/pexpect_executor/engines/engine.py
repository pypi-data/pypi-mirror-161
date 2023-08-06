#!/usr/bin/env python3

# Standard libraries
from os import environ

# Components
from ..package.bundle import Bundle
from ..system.platform import Platform

# Optional modules libraries (Windows)
if Platform.IS_WINDOWS:

    # Default engine
    if Bundle.ENV_ENGINE not in environ:
        environ[Bundle.ENV_ENGINE] = 'wexpect'

    # Optional Pexpect engine
    if environ[Bundle.ENV_ENGINE] == 'pexpect_popen':
        from .pexpect_popen import PexpectPopen as Engine # pylint: disable=unused-import

    # Optional Wexpect engine
    elif environ[Bundle.ENV_ENGINE] == 'wexpect':
        from .wexpect import Wexpect as Engine # pylint: disable=unused-import

    # Unknown engine
    else:
        raise NotImplementedError(f'Unknown engine "{environ[Bundle.ENV_ENGINE]}"')

# Optional modules libraries (Linux)
else:

    # Optional Pexpect engine
    from .pexpect import Pexpect as Engine # pylint: disable=unused-import
