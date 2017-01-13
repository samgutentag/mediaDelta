#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Sample Usage
#------------------------------------------------------------------------------
#
#   > python printExifTags.py -d ~/Desktop/testPhotos
#   > python printExifTags.py -f ~/Desktop/testPhotos/samplePhoto.jpg
#
#------------------------------------------------------------------------------

import utils
import pyexifinfo
import argparse


#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():
    # setup parser
    parser = argparse.ArgumentParser(description='outputs non media type files, just to make sure we have everything')

    # passing a single file
    parser.add_argument('-f', '--mediaFile', dest='mediaFile',
                        required=False,
                        help='pass a single file to process',
                        metavar='MEDIA_FILE',
                        type=lambda x: utils.openMediaFile(parser, x))

    # passing a directory (with or without sub directories) of files
    parser.add_argument('-d', '--mediaDirectory', dest='mediaDirectory',
                        required=False,
                        help='pass a directory of files to process, WARNING: RECURSIVE',
                        metavar='MEDIA_DIRECTORY',
                        type=lambda x: utils.openMediaDirectory(parser, x))

    args = vars(parser.parse_args())

    utils.bigSpacer()
    print 'Arguments...'
    utils.prettyPrintDict(args)
    utils.bigSpacer()

    # attempt to process a passed file
    if args['mediaFile']:

        try:
            # # get absolute filepath in a string
            # exifTagsDict = utils.JSONToDict(pyexifinfo.get_json(args['mediaFile']))
            # # pretty print dictionary of exif tags
            # utils.prettyPrintDict(exifTagsDict)

            utils.isValidMediaFileType(args['mediaFile'])
        except:
            print '>>> unabel to process %s' % args['mediaFile']



    # attempts to process a directory of files
    elif args['mediaDirectory']:

        # process a directory of files
        filesToProcess = utils.getDirectoryContents(args['mediaDirectory'])

    utils.spacer()
    print 'ALL DONE!'
    utils.bigSpacer()

if __name__ == '__main__':
    main()
