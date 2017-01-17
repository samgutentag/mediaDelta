#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Sample Usage
#------------------------------------------------------------------------------
#
#   > python printExifTags.py -d ~/Desktop/testPhotos
#   > python printExifTags.py -f ~/Desktop/testPhotos/samplePhoto.jpg
#
#------------------------------------------------------------------------------

import argparse
import utils
from datetime import datetime
from datetime import timedelta
import logging
import shutil
import os


#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():
    # setup parser
    parser = argparse.ArgumentParser(description='Output EXIF data of a given media file or files in a directory')

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


    #---------------------------------------------------------------------------
    #   Setup logging file
    #---------------------------------------------------------------------------
    logDateTime = datetime.now().strftime('%Y%m%d%H%M%S')
    logFileName = 'printExifTags_%s.log' % logDateTime
    logging.basicConfig(format='%(message)s', filename=logFileName, level=logging.DEBUG)


    utils.bigSpacer()
    print 'Arguments...'
    utils.prettyPrintDict(args)
    utils.spacer()

    startTime = datetime.now()
    fileCount = 0

    # attempt to process a passed file
    if args['mediaFile']:

        try:
            fileCount = 1
            utils.prettyPrintTags(args['mediaFile'])
        except:
            print '>>> unable to process %s' % args['mediaFile']
            logging.info('>>> unable to process %s', args['mediaFile'])


        logFile_destinationDir = args['mediaFile'][:args['mediaFile'].rfind('/')+1]


    # attempts to process a directory of files
    elif args['mediaDirectory']:

        # process a directory of files
        filesToProcess = utils.getDirectoryContents(args['mediaDirectory'])
        fileProcessCounter = 1
        fileCount = len(filesToProcess)

        elapsedTimeList = []

        for file in filesToProcess:
            print '\n%s of %s' % (fileProcessCounter, len(filesToProcess))
            logging.info('\n%s of %s', fileProcessCounter, len(filesToProcess))

            startTime = datetime.now()

            try:
                utils.prettyPrintTags(file)

            except:
                print '\tskipping %s' % file
                logging.info('\tskipping %s', file)

            endTime = datetime.now()

            elapsedTime = endTime - startTime

            elapsedTimeList.append(elapsedTime)

            # use time of first file for average of first
            if fileProcessCounter == 1:

                # calculate average file process time
                totalTime = 0
                for item in elapsedTimeList:
                    timeInSeconds = item.total_seconds()
                    totalTime = totalTime + timeInSeconds

                averageTime = totalTime / float(fileProcessCounter)

            # every 10 files, get the average elapsed time per file
            elif fileProcessCounter % 10 == 0:

                # calculate average file process time
                totalTime = 0
                for item in elapsedTimeList:
                    timeInSeconds = item.total_seconds()
                    totalTime = totalTime + timeInSeconds

                averageTime = totalTime / float(fileProcessCounter)

            logging.info('Averaging %s per file', str(timedelta(seconds=averageTime)))

            filesRemaining = fileCount - fileProcessCounter
            estimatedTimeRemaining = float(filesRemaining) * averageTime

            print 'Estimated Time Remaining:\t %s' % str(timedelta(seconds=estimatedTimeRemaining))
            logging.info('Estimated Time Remaining:\t %s', str(timedelta(seconds=estimatedTimeRemaining)))

            fileProcessCounter += 1

        logFile_destinationDir = args['mediaDirectory'][:args['mediaDirectory'].rfind('/')+1]

    utils.spacer()

    #---------------------------------------------------------------------------
    #   Move logging file
    #---------------------------------------------------------------------------

    # clean destinationDir to not include tail slashes, if they exist
    logFile_destinationDir = logFile_destinationDir + 'logs/'

    # check if destination directory exists, if not create it
    if not os.path.exists(logFile_destinationDir):
        os.makedirs(logFile_destinationDir)

    logFileDestination = logFile_destinationDir + logFileName
    print logFileDestination
    shutil.move(logFileName, logFileDestination)

    print 'Logfile located at \'%s\'' % logFileDestination

    utils.spacer()
    print 'ALL DONE!'
    utils.bigSpacer()



if __name__ == '__main__':
    main()
