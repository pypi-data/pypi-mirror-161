#!/usr/bin/env python
"""Save the configuration of a DS1000 oscilloscope to a JSON file or
load the configration from a JSON file.
"""
from argparse import ArgumentParser, FileType
import json
import sys

import ds1052


description = __doc__


def get_args(argv):
    parser = ArgumentParser(description=description)
    subparsers = parser.add_subparsers(title='command')
    load_parser = subparsers.add_parser(
        'load',
        help=(
            'Configure a DS1000 oscilloscope from data saved in a JSON file'))
    load_parser.set_defaults(func=load_config)
    load_parser.add_argument(
        'config_file', type=FileType('r'),
        help='The name of a JSON file with DS1000 config data.')
    save_parser = subparsers.add_parser(
        'save',
        help=(
            'Save the configration of a DS1000 oscilloscope in a JSON file'))
    save_parser.set_defaults(func=save_config)
    save_parser.add_argument(
        'config_file', type=FileType('w'),
        help='The name of a file to save DS1000 config data in.')
    for p in load_parser, save_parser:
        p.add_argument(
            '--serial', default=None,
            help='The serial number of the oscilloscope (optional).',
            required=False)
    return parser.parse_args(argv)


def load_config(args):
    with ds1052.DS1052(serial=args.serial) as dso:
        config = json.load(args.config_file)
        if 'channel' in config:
            # JSON does not support integers as dictionary keys.
            # Instead, numbers are stored as strings...
            for ch in 1, 2:
                ch_as_str = str(ch)
                if (
                        ch_as_str in config['channel']
                        and ch not in config['channel']):
                    config['channel'][ch] = config['channel'][ch_as_str]
        dso.set_config(config)
        args.config_file.close()
        return 0


def save_config(args):
    with ds1052.DS1052(serial=args.serial) as dso:
        config = dso.get_config()
        json.dump(config, args.config_file, sort_keys=True, indent=4)
        args.config_file.close()
        return 0


if __name__ == '__main__':
    args = get_args(sys.argv[1:])
    sys.exit(args.func(args))
