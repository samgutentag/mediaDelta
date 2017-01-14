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
    parser = argparse.ArgumentParser(description='Output EXIF data of a given media file or files in a directory')

    # passing a single file

    parser.add_argument('-i', '--inputSource', dest='inputMedia',
                        required=False,
                        help='pass an inpute file or directory to be processed',
                        metavar='INPUT_SOURCE',
                        type=lambda x: utils.openInput(parser, x))

    # passing a directory (with or without sub directories) of files
    parser.add_argument('-x', '--force', dest='doForce',
                        required=False,
                        help='Force evaluation of files',
                        metavar='DO_FORCE')



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

        exifTagsDict = utils.JSONToDict(pyexifinfo.get_json(args['mediaFile']))
        # pretty print dictionary of exif tags
        utils.prettyPrintDict(exifTagsDict)

        try:
            # get absolute filepath in a string
            exifTagsDict = utils.JSONToDict(pyexifinfo.get_json(args['mediaFile']))
            # pretty print dictionary of exif tags
            utils.prettyPrintDict(exifTagsDict)
        except:
            print '>>> unabel to process %s' % args['mediaFile']



    # attempts to process a directory of files
    elif args['mediaDirectory']:

        # process a directory of files
        filesToProcess = utils.getDirectoryContents(args['mediaDirectory'])

        fileProcessCounter = 1
        for file in filesToProcess:
            utils.spacer()
            print '\n%s of %s' % (fileProcessCounter, len(filesToProcess)),
            try:
                # pretty print dictionary of exif tags
                exifTagsDict = utis.JSONToDict(pyexifinfo.get_json(file))
                utils.prettyPrintDict(exifTagsDict)
            except:
                print '\tskipping %s' % file

            fileProcessCounter += 1

    utils.spacer()
    print 'ALL DONE!'
    utils.bigSpacer()

if __name__ == '__main__':
    main()
