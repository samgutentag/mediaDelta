#!python3


'''
    Refactoring the mediaDelta scripts to leverage python3 goodness!

'''


from argparse import ArgumentParser
from getpass import getuser
import pyexifinfo

import os

VALID_VIDEO_EXTENSIONS = ['MOV', 'MP4', 'MPG', 'M4V', '3G2', '3GP', 'ASF', 'AVI', 'WMV']
VALID_IMAGE_EXTENSIONS = ['JPG', 'JPEG', 'PNG', 'TIF', 'TIFF', 'CR2', 'BMP', 'GIF', 'DNG', 'ARW']

APPROVED_MEDIA_FILE_EXTENTIONS =VALID_VIDEO_EXTENSIONS + VALID_IMAGE_EXTENSIONS


#   pretty print a dictionary in key value pairs, well spaced
def prettyPrintDict(inputDictionary):

    # get longest 'key' string length
    longest_key = max(map(len, inputDictionary.keys()))

    # sort and print formatting
    sortedDict = sorted(inputDictionary.items())
    for key, value in sortedDict:
        spacesNeeded = longest_key - len(key) + 4
        print(f'{key}{" " * spacesNeeded}{value}')

    return True


#-------------------------------------------------------------------------------
#   Argument Parsing
#-------------------------------------------------------------------------------
def parse_arguemnts():

    # define a parser
    parser = ArgumentParser(description="Import Media Files from Media Card or \
        External Hard Drive")

    # OPTIONAL -> 'username': defaults to logged in username
    parser.add_argument('-u', '--username',
                        dest='username',
                        required=False,
                        default=getuser(),
                        help='username, name of artist, defaults to username \
                        of  the currently logged in user',
                        metavar='USERNAME')

    # REQUIRED -> 'source_dir': the root direcctory to seach for media
    parser.add_argument('-s', '--source_dir',
                        dest='source_dir',
                        required=True,
                        help='the top level directory to collect media files, \
                        will include all sub directories',
                        metavar='SOURCE_DIR')

    # REQUIRED -> 'dest_dir': the destination root directory for media
    parser.add_argument('-d', '--dest_dir',
                        dest='dest_dir',
                        required=True,
                        help='the destination directory for import or archive \
                        of media files',
                        metavar='DEST_DIR')

    # OPTIONAL -> 'move_only':toggle copy or relocatoin of files, default copy
    parser.add_argument('-move', '--move_only',
                        action='store_true', default=False,
                        required=False,
                        help='if passed, script will move files from \
                        source_dir to dest_dir, overrides default action to \
                        copy files')

    # get arguments
    args = vars(parser.parse_args())

    return args

def isValidMediaFileType(file):

    # always sexclude dot files
    if file[0] == '.':
        return False

    file_extension = file.split('.')[-1]

    if file_extension.upper() not in APPROVED_MEDIA_FILE_EXTENTIONS:
        return False
    else:
        return True


def getMediaFileObject(file, artist=getuser()):

    print(file)
    print(artist)

    # get exif data
    exif_data = pyexifinfo.get_json(file)

    # attempt to extract media type
    mediaType = exif_data

    return True


def main():

    # parse user input arguments
    args = parse_arguemnts()
    # prettyPrintDict(args)

    # collect files to process from `source_dir`
    files_to_process = []
    skipped_files = []

    for root, dirs, files in os.walk(args['source_dir']):
        for file in files:

            # strip out non media type files
            if isValidMediaFileType(file):
                print(f'\t-> collecting {file}')
                files_to_process.append(f'{root}/{file}')

            else:
                print(f'\t!  skipping {file}')
                skipped_files.append(f'{root}/{file}')

    print(f'Found {len(files_to_process)} files to process...')
    print(f'\t {len(skipped_files)} non media-type files will be skipped...')



    # process each file
    for file in files_to_process:
        media_file_object = getMediaFileObject(file, artist=args['username'])




if __name__ == '__main__':
    main()


# EOF
