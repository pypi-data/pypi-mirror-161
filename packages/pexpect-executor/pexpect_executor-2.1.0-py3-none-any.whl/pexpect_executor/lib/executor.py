#!/usr/bin/env python3

# Standard libraries
from errno import ENOENT
from getpass import getuser
from os import chdir, environ
from time import sleep

# Components
from ..engines.engine import Engine
from ..package.bundle import Bundle
from ..prints.colors import Colors
from ..system.platform import Platform

# Executor
class Executor:

    # Constants
    KEY_UP = '\033[A'
    KEY_DOWN = '\033[B'
    KEY_LEFT = '\033[D'
    KEY_RIGHT = '\033[C'
    KEY_ENTER = '\r'
    KEY_SPACE = ' '

    # Delays
    DELAY_INIT = 1.0
    DELAY_PRESS = 0.5
    DELAY_PROMPT = 1.0

    # Labels
    LABEL_HOST = 'preview'
    LABEL_TOOL = 'executor'

    # Members
    __delay_init = None
    __delay_press = None
    __delay_prompt = None
    __engine = None
    __host = environ[Bundle.ENV_HOST] if Bundle.ENV_HOST in environ else LABEL_HOST
    __strips = None
    __tool = environ[Bundle.ENV_TOOL] if Bundle.ENV_TOOL in environ else LABEL_TOOL

    # Constructor, pylint: disable=too-many-arguments
    def __init__(self, command='', delay_init=DELAY_INIT, delay_press=DELAY_PRESS,
                 delay_prompt=DELAY_PROMPT, hold_prompt=False, workdir=None):

        # Prepare delays
        self.__delay_init = float(delay_init)
        self.__delay_press = float(delay_press)
        self.__delay_prompt = float(delay_prompt)

        # Prepare workdir
        if workdir:
            self.__prompt(f'cd {workdir}', hold_prompt=hold_prompt)
            chdir(workdir)

        # Prepare command
        self.__prompt(command, hold_prompt=hold_prompt)
        if command:

            # Spawn command
            self.__engine = Engine(command)

            # Delay executor initialization
            if self.__delay_init > 0.0:
                Executor.sleep(self.__delay_init)
                self.read()

    # Configure
    @staticmethod
    def configure(host=LABEL_HOST, tool=LABEL_TOOL, strips=None):

        # Prepare host
        Executor.__host = host

        # Prepare strips
        Executor.__strips = strips

        # Prepare tool
        Executor.__tool = tool

    # Control key, pylint: disable=no-self-use
    def __control_key(self, key):

        # Acquire key value
        key = key.lower()
        try:
            value = ord(key)
        except TypeError:
            value = 0

        # Handle alphabetical key
        if 97 <= value <= 122:
            value = value - ord('a') + 1
            return bytes([value])

        # List specific keys
        mappings = {
            '@': 0,
            '`': 0,
            '[': 27,
            '{': 27,
            '\\': 28,
            '|': 28,
            ']': 29,
            '}': 29,
            '^': 30,
            '~': 30,
            '_': 31,
            '?': 127
        }

        # Handle specific keys
        if key in mappings:
            return bytes([mappings[key]])

        # Unknown fallback
        return ''

    # Prompt
    def __prompt(self, command, hold_prompt=False):

        # Display prompt
        print(
            f'{Colors.GREEN_THIN}{getuser()}{Colors.RESET}'
            f'@{Colors.RED_THIN}{self.__host}{Colors.RESET}'
            f':{Colors.YELLOW_THIN}~/{self.__tool}{Colors.RESET}$ ', end='')
        Platform.flush()

        # Delay prompt
        Executor.sleep(self.__delay_prompt)

        # Display command
        if command:
            print(f'{command} ', end='')
            Platform.flush()
            Executor.sleep(self.__delay_prompt)
            print(' ')
            Platform.flush()

        # Return prompt
        elif not hold_prompt:
            print(' ')
            Platform.flush()

    # Press
    def press(self, key, control=False):

        # Execution check
        if not self.__engine:
            return self

        # Delay press
        Executor.sleep(self.__delay_press)

        # Press Ctrl+key
        if control:
            self.__engine.send(self.__control_key(key))

        # Press key
        else:
            self.__engine.send(key)

        # Result
        return self

    # Read
    def read(self):

        # Execution check
        if not self.__engine:
            return self

        # Read stream
        self.__engine.read(Executor.__strips)

        # Result
        return self

    # Wait
    def wait(self, delay):

        # Delay execution
        Executor.sleep(delay)

        # Result
        return self

    # Finish
    def finish(self, force=False):

        # Execution check
        if not self.__engine:
            return ENOENT

        # Read and wait execution
        if not force:
            try:
                while self.__engine.isalive():
                    self.read()
            except KeyboardInterrupt:
                pass

        # Terminate process
        self.__engine.terminate(force=force)

        # Result
        return self.__engine.status()

    # Sleep
    @staticmethod
    def sleep(delay):

        # Delay execution
        sleep(delay)
