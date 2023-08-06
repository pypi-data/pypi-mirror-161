#!/usr/bin/env python3

# Standard libraries
from argparse import ArgumentParser, RawTextHelpFormatter
from sys import exit as sys_exit

# Components
from ..features.actions import ActionsFeature
from ..lib.executor import Executor
from ..package.bundle import Bundle
from ..package.version import Version
from ..system.platform import Platform
from ..types.commands import Commands

# Main
def main():

    # Variables
    result = False

    # Arguments creation
    parser = ArgumentParser(
        prog=Bundle.NAME,
        description=f'{Bundle.NAME}: Automate interactive CLI tools actions',
        add_help=False, formatter_class=RawTextHelpFormatter)

    # Arguments internal definitions
    group = parser.add_argument_group('internal arguments')
    group.add_argument('-h', '--help', dest='help', action='store_true',
                       help='Show this help message')
    group.add_argument('--version', dest='version', action='store_true',
                       help='Show the current version')

    # Arguments configuration definitions
    group = parser.add_argument_group('configuration arguments')
    group.add_argument(
        '--delay-init', dest='delay_init', type=float, default=Executor.DELAY_INIT,
        help='Delay the initial action execution (in s, default: %(default)s)',
        metavar='SECS')
    group.add_argument(
        '--delay-press', dest='delay_press', type=float, default=Executor.DELAY_PRESS,
        help='Delay the press actions execution (in s, default: %(default)s)',
        metavar='SECS')
    group.add_argument(
        '--delay-prompt', dest='delay_prompt', type=float, default=Executor.DELAY_PROMPT,
        help='Delay the prompt actions execution (in s, default: %(default)s)',
        metavar='SECS')
    group.add_argument('--hold-prompt', dest='hold_prompt', action='store_true',
                       help='Hold the prompt execution without a new line')
    group.add_argument(
        '--host', dest='host', action='store', default=Executor.LABEL_HOST,
        help='Configure the host name (default: %(default)s' + ', env: ' +
        Bundle.ENV_HOST + ')')
    group.add_argument(
        '--tool', dest='tool', action='store', default=Executor.LABEL_TOOL,
        help='Configure the tool name (default: %(default)s' + ', env: ' +
        Bundle.ENV_TOOL + ')')
    group.add_argument('--workdir', dest='workdir', action='store',
                       help='Use a specific working directory path')

    # Arguments actions definitions
    group = parser.add_argument_group('actions arguments')
    group.add_argument('--up', dest='actions', action='append_const',
                       const=ActionsFeature.ActionKey(Executor.KEY_UP),
                       help='Press the <UP> key')
    group.add_argument('--down', dest='actions', action='append_const',
                       const=ActionsFeature.ActionKey(Executor.KEY_DOWN),
                       help='Press the <DOWN> key')
    group.add_argument('--left', dest='actions', action='append_const',
                       const=ActionsFeature.ActionKey(Executor.KEY_LEFT),
                       help='Press the <LEFT> key')
    group.add_argument('--right', dest='actions', action='append_const',
                       const=ActionsFeature.ActionKey(Executor.KEY_RIGHT),
                       help='Press the <RIGHT> key')
    group.add_argument('--enter', dest='actions', action='append_const',
                       const=ActionsFeature.ActionKey(Executor.KEY_ENTER),
                       help='Press the <ENTER> key')
    group.add_argument('--space', dest='actions', action='append_const',
                       const=ActionsFeature.ActionKey(Executor.KEY_SPACE),
                       help='Press the <SPACE> key')
    group.add_argument('--press', dest='actions', action='append',
                       type=ActionsFeature.ActionKey, help='Press the specified <KEY>',
                       metavar='KEY')
    group.add_argument('--ctrl', dest='actions', action='append',
                       type=ActionsFeature.ActionKeyControl,
                       help='Press the specified Ctrl+<KEY>', metavar='KEY')
    group.add_argument('--read', dest='actions', action='append_const',
                       const=ActionsFeature.ActionRead(),
                       help='Read the buffered data output (forced)')
    group.add_argument(
        '--wait', dest='actions', action='append', type=ActionsFeature.ActionWait,
        help='Wait the specified time (in s, example: 1.0)', metavar='SECS')
    group.add_argument('--finish', dest='actions', action='append_const',
                       const=ActionsFeature.ActionFinish(),
                       help='Finish the execution (forced)')

    # Arguments positional definitions
    group = parser.add_argument_group('positional arguments')
    group.add_argument('command', nargs='*',
                       help='Command arguments to execute (use -- to separate)')

    # Arguments parser
    options = parser.parse_args()

    # Help informations
    if options.help:
        print(' ')
        parser.print_help()
        print(' ')
        Platform.flush()
        sys_exit(0)

    # Version informations
    if options.version:
        print(
            f'{Bundle.NAME} {Version.get()} from {Version.path()} (python {Version.python()})'
        )
        Platform.flush()
        sys_exit(0)

    # Prepare command
    command = Commands(options.command).get()

    # Action executor
    result = ActionsFeature(command, options).run()

    # Result
    if result:
        sys_exit(0)
    else:
        sys_exit(1)

# Entrypoint
if __name__ == '__main__': # pragma: no cover
    main()
