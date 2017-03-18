#!/usr/bin/end python


import argparse
import utils
import logging
import shutil
import os

# special stuff to handle known non ascii cahracters, blame sony! (not really)
import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')


def main():

    #define parser
    parser = argparse.ArgumentParser(description="Import Data from a memory card to a staging drive")


    parser.add_argument('-u', '--username', dest='username',
                        required = True,
                        help = 'tag files with the person who captured them',
                        metavar='USER_NAME')

    parser.add_argument('-c', '--camera', dest='camera',
                        required = True,
                        help = 'tag files with the camera used to capture them',
                        metavar='CAMERA_NAME')

    parser.add_argument('-s', '--source', dest='sourceDirectory',
                        required = True,
                        help = 'the source directory of the files we want to import, typically a memory card',
                        metavar='SOURCE_DIRECTORY')

    parser.add_argument('-d', '--destination', dest='destinationDirectory',
                        required = True,
                        help='the destination directory of the files we want to import, typically on an external hard drive',
                        metavar='DESTINATION_DIRECTORY')

    args = vars(parser.parse_args())


    for arg in args:
        print arg

    print args


main()
