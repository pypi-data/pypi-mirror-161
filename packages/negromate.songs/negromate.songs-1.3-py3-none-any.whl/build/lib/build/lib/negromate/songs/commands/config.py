import sys
from pathlib import Path

name = 'config'
help_text = 'Write the configuration'
initial_config = {
    'file': '~/.negromate/config.ini',
}


def options(parser, config, **kwargs):
    parser.add_argument(
        '-f', '--file', type=Path,
        default=config['config']['file'],
        help="Configuration file, defaults to {}".format(
            config['config']['file']))


def run(args, config, **kwargs):
    with args.file.expanduser().open('w') as f:
        config.write(f)
