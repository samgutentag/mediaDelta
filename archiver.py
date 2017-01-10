#!/usr/bin/end python


#------------------------------------------------------------------------------
#		Sample Usage
#------------------------------------------------------------------------------
#
#   > python archiver.py -a samgutentag -d /Volumes/GoProBackUps/DateCorrected/correctedFiles/02b_M-N/ -o /Volumes/MacPak500GB/photos > ~/Desktop/pyExifLog_corrected_02b_take2.txt
#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------

import pyexifinfo as p
import argparse
import json
import os
import shutil
import utils

# special stuff to handle known non ascii cahracters, blame sony! (not really)
import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')


#------------------------------------------------------------------------------
#		file relocation functions
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
#		file processing functions
#------------------------------------------------------------------------------


def getCorrectedArchiveFilePath(destinationDir, mediaFileObject):
    fileName = ''
    dirName = ''
    counter = '0001'

    # clean destinationDir to not include tail slashes, if they exist
    while destinationDir.endswith('/'):
        destinationDir = destinationDir[:-1]

    #  format:  'destination/mediaType(plural)/YYYY/YYYY.MM/MM.<eventName>/'
    #  example: 'photos/images/2016/2016.12/12.christmas/'
    #  example: 'photos/videos/2016/2016.11/11.thanksgiving'
    dirName = '%s/%ss/%s/%s.%s/' % (destinationDir,
                                            mediaFileObject.type,
                                            mediaFileObject.dateTime.year,
                                            mediaFileObject.dateTime.year,
                                            mediaFileObject.dateTime.month)
    # format:  'YYYYMMDD.HHMMSSsss.<creator>.<counter>.<extension>'
    fileName = '%s%s%s.%s%s%s%s.%s.%s.%s' % (mediaFileObject.dateTime.year,
                                                mediaFileObject.dateTime.month,
                                                mediaFileObject.dateTime.day,
                                                mediaFileObject.dateTime.hour,
                                                mediaFileObject.dateTime.minute,
                                                mediaFileObject.dateTime.second,
                                                mediaFileObject.dateTime.millisecond,
                                                mediaFileObject.creator,
                                                counter,
                                                mediaFileObject.extension)

    # return dirName + fileName
    return (dirName, fileName)



def archiveMediaFile(inputFile, destinationDir, creator):

    print ">>> processing '%s'" % inputFile
    archivedMediaFilePath = ''

    # mediaFileObject = utils.getMediaFileObject(inputFile, creator)
    # mediaFileObject.printInfo()


    mediaFileObject = utils.getMediaFileObject(inputFile, creator)
    utils.spacer()
    mediaFileObject.printInfo()
    utils.spacer()

    # make Corrected File Path
    correctedFilePath = getCorrectedArchiveFilePath(destinationDir, mediaFileObject)
    print correctedFilePath

    # copy file, returns destinationDirectory and destinationFile
    destinationFile = utils.makeCopy(inputFile, correctedFilePath[0], correctedFilePath[1])
    print destinationFile


    print '\tmoved\t%s' % inputFile
    print '\tto\t\t%s%s' % (destinationFile[0], destinationFile[1])

    return archivedMediaFilePath


#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():
    # setup parser
    parser = argparse.ArgumentParser(description='Read EXIF data of a given media file, update filename and sort into structured directory')

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

    # output directory destination
    parser.add_argument('-o', '--outputDirectory', dest='outputDirectory',
                        required = True,
                        help = 'this is the root destination directory that photos will be copied to',
                        metavar='OUTPUT_DIRECTORY')

    # creator name helps with identification when multiple photographers or artists are contributing to a single collection
    parser.add_argument('-c', '--creatorName', dest='creatorName',
                        required = True,
                        help = 'user provided creator name, used for tagging with multiple artists or photographers into a single collection',
                        metavar='CREATOR_NAME')

    # # creator name helps with identification when multiple photographers or artists are contributing to a single collection
    # parser.add_argument('-e', '--eventName', dest='eventName',
    #                 required = True,
    #                 help = 'event name used to aide identification of directories contents',
    #                 metavar='EVENT_NAME')

    args = vars(parser.parse_args())

    utils.bigSpacer()
    print 'Arguments...'
    utils.prettyPrintDict(args)
    utils.bigSpacer()

    # attempt to process a passed file
    if args['mediaFile']:
        # processMediaFile(args['mediaFile'], args['artistName'], args['outputDirectory'], args['cameraMake'], args['cameraModel'])
        archivedFilePath = archiveMediaFile(args['mediaFile'], args['outputDirectory'], args['creatorName'])
        print 'Archived %s\n\tto %s' % (args['mediaFile'], archivedFilePath)

        # try:
        #     archivedFilePath = archiveMediaFile(args['mediaFile'], args['outputDirectory'], args['creatorName'])
        #     print 'Archived %s\n\tto %s' % (args['mediaFile'], archivedFilePath)
        #
        # except:
        #     print '>>> Could not process file'

    # attempts to process a directory of files
    elif args['mediaDirectory']:

        # process a directory of files
        filesToProcess = getDirectoryContents(args['mediaDirectory'])

        fileProcessCounter = 1
        bigSpacer()
        for file in filesToProcess:

            print '\n%s of %s' % (fileProcessCounter, len(filesToProcess))
            processMediaFile(file, args['artistName'], args['outputDirectory'], args['cameraMake'], args['cameraModel'])

            fileProcessCounter += 1

        bigSpacer()

if __name__ == '__main__':
    main()
