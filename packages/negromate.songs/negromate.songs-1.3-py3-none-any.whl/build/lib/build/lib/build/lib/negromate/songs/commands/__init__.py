import argparse
import configparser
import logging
import traceback
import sys
from pathlib import Path
try:
    from importlib import metadata
except ImportError:  # Python <3.8
    import importlib_metadata as metadata


CONFIG_FILE = '~/.negromate/config.ini'


def main():
    """
        Build parser for all the commands and launch appropiate command.

        Each command must be a module with at least the following members:

            * name: String with the command name. Will be used for
              argparse subcommand.
            * help_text: String with the help text.
            * initial_config: Dict for initial configuration of commands.
            * options: Function to build the parser of the command. Takes
              two parametters, the argparser parser instance for this
              subcommand and the ConfigParser instance with all the
              configuration.
            * run: Function that runs the actual command. Takes two
              parametters, the argparse Namespace with the arguments and
              the ConfigParser with all the configuration.

        Minimal module example:

            # hello_world.py
            name = 'hello'
            help_text = 'Sample command'
            initial_config = {
                'who': 'World',
            }

            def options(parser, config, **kwargs):
                parser.add_argument(
                    '-w', '--who', default=config['hello']['who'],
                    help="Who to say hello, defaults to '{}'".format(config['hello']['who'])
                )

            def run(args, **kwargs):
                print("Hello {}".format(args.who))

        To add more commands to negromate register 'negromate.commands'
        entry point in setup.cfg. For example:

            [options.entry_points]
                negromate.commands =
                    hello = negromate.web.commands.hello_world

    """
    commands = []
    # clean sys.argv for any module imported here
    # Yes Kivy, I'm looking at you
    args = sys.argv.copy()
    sys.argv = args[:1]

    # Load commands from entry_point
    entry_points = metadata.entry_points().get('negromate.commands', [])
    for entry_point in entry_points:
        try:
            command = entry_point.load()
        except Exception as e:
            traceback.print_exc()
            print(e)
            continue
        commands.append(command)

    # Load initial configuration for commands
    initial_config = {
        'global': {
            'song_folder': '~/negro_mate/bideoak/',
            'lyrics_file': '~/negro_mate/libreto/libreto.pdf',
        }
    }
    for command in commands:
        if hasattr(command, 'initial_config'):
            initial_config[command.name] = command.initial_config

    # Load configuration
    config = configparser.ConfigParser()
    config.read_dict(initial_config)
    config.read(Path(CONFIG_FILE).expanduser())

    # Build parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help="Display informational messages.")
    parser.set_defaults(command=None)
    subparsers = parser.add_subparsers()
    for command in commands:
        command_parser = subparsers.add_parser(command.name, help=command.help_text)
        command_parser.set_defaults(command=command.name)
        command.options(parser=command_parser, config=config)

    # Run command
    args = parser.parse_args(args[1:])
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    if args.command is None:
        parser.print_usage()
    else:
        for command in commands:
            if args.command == command.name:
                command.run(args=args, config=config)
