#!/usr/bin/env python3
"""

Usage: > python3 md3.py



"""

import argparse
from getpass import getuser


def pretty_print_dict(d=None):
    ''' Pretty print dictionary well spaced '''

    if not d:
        return -1

    longest_key = max([len(x) for x in d.keys()])
    for k, v in d.items():
        print(f'{k.ljust(longest_key)}\t:\t{v}')


def get_arguments():
    parser = argparse.ArgumentParser(description='''Import Media Files from
                                        Media Card or External Hard Drive''')

    parser.add_argument('-u', '--username',
                        dest='username',
                        required=False,
                        default=getuser(),
                        help='Username or Creator Name for File Naming')

    parser.add_argument('-s', '--source_dir',
                        dest='source_dir',
                        required=True,
                        help='Source Directory containing media files')

    parser.add_argument('-d', '--dest_dir',
                        dest='destination_dir',
                        required=True,
                        help='Destination Directory for media import/archive')

    parser.add_argument('-thumbnail', '--make_thumbnails',
                        action='store_true',
                        default=False,
                        required=False,
                        help='''Make thumbnail images that are 2000 pixels on
                                the longest edge''')

    parser.add_argument('-move', '--move_only',
                        action='store_true',
                        default=False,
                        required=False,
                        help='''Move files instead of copying them,
                                typically in archiving''')

    args = vars(parser.parse_args())

    return args

def main():
    print('Gutentag World!')

    args = get_arguments()


    pretty_print_dict(d=args)



if __name__ == '__main__':
    main()
