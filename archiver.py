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

import argparse
import utils
from datetime import datetime
import logging
import shutil
import os


# special stuff to handle known non ascii cahracters, blame sony! (not really)
import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')

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


    args = vars(parser.parse_args())


    #---------------------------------------------------------------------------
    #   Setup logging file
    #---------------------------------------------------------------------------
    logDateTime = datetime.now().strftime('%Y%m%d%H%M%S')
    logFileName = 'archiver_%s.log' % logDateTime
    logging.basicConfig(format='%(levelname)s:%(message)s', filename=logFileName, level=logging.DEBUG)

    utils.bigSpacer()
    print 'Arguments...'
    utils.prettyPrintDict(args)
    utils.spacer()

    startTime = datetime.now()
    fileCount = 0

    # attempt to process a passed file
    if args['mediaFile']:
        archivedFilePath = utils.archiveMediaFile(args['mediaFile'], args['outputDirectory'], args['creatorName'])
        fileCount = 1

    # attempts to process a directory of files
    elif args['mediaDirectory']:

        # process a directory of files
        filesToProcess = utils.getDirectoryContents(args['mediaDirectory'])
        fileProcessCounter = 1
        fileCount = len(filesToProcess)

        for file in filesToProcess:
            print '\n%s of %s ' % (fileProcessCounter, fileCount)
            archivedFilePath = utils.archiveMediaFile(file, args['outputDirectory'], args['creatorName'])
            fileProcessCounter += 1

    utils.spacer()
    utils.printTimeSheet(startTime, datetime.now(), fileCount)


    utils.spacer()
    print 'Done!'
    utils.bigSpacer()

    #---------------------------------------------------------------------------
    #   Move logging file
    #---------------------------------------------------------------------------

    # clean outputDirectory to not include tail slashes, if they exist
    outDir = args['outputDirectory']

    if outDir[-1:] != '/':
        outDir = outDir + '/'

    logFile_destinationDir = outDir[:outDir.rfind('/')+1] + 'logs/'

    # check if destination directory exists, if not create it
    if not os.path.exists(logFile_destinationDir):
        os.makedirs(logFile_destinationDir)

    logFileDestination = logFile_destinationDir + logFileName
    shutil.move(logFileName, logFileDestination)

    print 'Logfile located at \'%s\'' % logFileDestination

if __name__ == '__main__':
    main()
