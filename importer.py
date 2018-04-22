#!/usr/bin/end python


import argparse
from getpass import getuser
import sys, time
import os
import shutil

import utilities



def main():

    #--------------------------------------------------------------------------
    #       Setup Arguemnt Parser
    #--------------------------------------------------------------------------

    parser = argparse.ArgumentParser(description='Import Media Files from Media Card or External Hard Drive')

    '''
        file name prefix is a name, selected in the following order
            1   passed argument
            2   username of logged in account running this script
    '''
    parser.add_argument('-u', '--username',
                            dest='username',
                            required=False,
                            default=getuser(),
                            help='file prefix username',
                            metavar='USERNAME')

    parser.add_argument('-a', '--archive',
                        action='store_true', default = False,
                        required=False,
                        help='if passed, will archive files instead of importing')

    parser.add_argument('-s', '--source_dir',
                            dest='source_dir',
                            required=True,
                            help='source directory of media files, typically an external memory card',
                            metavar='SOURCE_DIR')

    parser.add_argument('-d', '--destination_dir',
                            dest='destination_dir',
                            required=True,
                            help='destination directory for imported media files',
                            metavar='DESTINATION_DIR')

    parser.add_argument('-thumb', '--make_thumbnail',
                            action='store_true', default = False,
                            required=False,
                            help='if passed, will generate a 720px thumbnail file')

    parser.add_argument('-move', '--move_only',
                            action='store_true', default = False,
                            required=False,
                            help='if passed, script will move files from source to destination, not make copies')

    args = vars(parser.parse_args())

    utilities.prettyPrintDict(args)

    # get files to process
    files_to_process = utilities.getDirectoryContents(args['source_dir'])

    # DONT ARCHIVE THUMBNAIL IMAGES
    if args['archive']:
        files_to_process = [file_name for file_name in files_to_process if '/THUMB/' not in file_name]

    num_files_to_process = len(files_to_process)
    max_len_filename = len(max(files_to_process, key=len))
    print('Found {:d} files to process...'.format(num_files_to_process))

    # loop over files
    for ii, file in enumerate(sorted(files_to_process)):

        # progress bar setup
        file_name = file
        if len(file_name) < max_len_filename:
            file_name = file_name + ' '* (max_len_filename-len(file_name))
        if args['archive']:
            prefix_string = 'Archiving {0:2}/{1:2} : {3:}'.format(ii+1, num_files_to_process,
                                                                    len(str(num_files_to_process)),
                                                                    file_name.replace(args['source_dir'], ''))
        else:
            prefix_string = 'Importing {0:2}/{1:2} : {3:}'.format(ii+1, num_files_to_process,
                                                                    len(str(num_files_to_process)),
                                                                    file_name.replace(args['source_dir'], ''))

        # make media file object
        if args['username'] == '':
            creatorName = getuser()
        else:
            creatorName = args['username']

        mediaFileObject = utilities.getMediaFileObject(file, creatorName = creatorName)


        # if import mode is 'ARCHIVE'
        if args['archive']:

            # archive file
            archive_file_path, archive_file_name = utilities.make_archive_file_name(mediaFileObject,
                                            # file_counter = ii,
                                            destination_directory = args['destination_dir'])

            if args['move_only']:
                # copy file
                shutil.move(file, '{}{}'.format(archive_file_path, archive_file_name))
            else:
                shutil.copy2(file, '{}{}'.format(archive_file_path, archive_file_name))

        else:

            # import file
            import_file_path, import_file_name = utilities.make_import_file_name(mediaFileObject,
                                            file_counter = ii,
                                            destination_directory = args['destination_dir'])

            # copy file
            if args['move_only']:
                # copy file
                shutil.move(file, '{}{}'.format(import_file_path, import_file_name))
            else:
                shutil.copy2(file, '{}{}'.format(import_file_path, import_file_name))

            # if making thumbnails...
            if args['make_thumbnail']:

                # only make thumbnails of IMAGE media files
                if mediaFileObject.type != 'IMAGE':
                    pass
                else:

                    # print('Making Thumbnail...')
                    # mediaFileObject.type = 'THUMB'
                    mediaFileObject.resolution = 'THUMB'
                    mediaFileObject.extension = 'JPEG'

                    import_thumbnail_path, import_thumbnail_name = utilities.make_import_file_name(mediaFileObject,
                                                    file_counter = ii,
                                                    destination_directory = args['destination_dir'])

                    # ensure file path exists
                    if not os.path.exists(import_thumbnail_path):
                        os.makedirs(import_thumbnail_path)

                    # make thumbnail from file
                    outfile = '{}{}'.format(import_thumbnail_path, import_thumbnail_name)
                    utilities.make_thumb(mediaFileObject, outfile, thumb_size=(1080,1080), thumb_file_type='JPEG')

        utilities.print_progress(ii+1, num_files_to_process, decimals=1, bar_length=50, prefix=prefix_string)

if __name__ == '__main__':
    main()
# EOF
