#!/usr/bin/end python


import argparse
import utils
import logging
import shutil
import os

from datetime import datetime
from datetime import timedelta


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

    parser.add_argument('-s', '--source', dest='sourceDirectory',
                        required = True,
                        help = 'the source directory of the files we want to import, typically a memory card',
                        metavar='SOURCE_DIRECTORY')

    parser.add_argument('-d', '--destination', dest='destinationDirectory',
                        required = True,
                        help='the destination directory of the files we want to import, typically on an external hard drive',
                        metavar='DESTINATION_DIRECTORY')

    args = vars(parser.parse_args())

    #   setup logging
    logDateTime = datetime.now().strftime('%Y%m%d%H%M%S')
    logFileName = 'import_%s.log' % logDateTime
    logging.basicConfig(format='%(message)s', filename=logFileName, level=logging.DEBUG)

    #   print arguments
    utils.bigSpacer()
    print 'Arguments...'
    utils.prettyPrintDict(args)
    utils.spacer()

    fileCount = 0

    #   Get source directory contents
    filesToProcess = utils.getDirectoryContents(args['sourceDirectory'])
    fileProcessCounter = 1
    fileCount = len(filesToProcess)

    #   Clean up destination directory name
    destDir = args['destinationDirectory']
    while destDir[-1] == '/':
        destDir = destDir[:-1]

    #   process files and import if not already imported
    for file in filesToProcess:
        startTime = datetime.now()

        print '\n%s of %s' % (fileProcessCounter, fileCount)
        logging.info('\n%s of %s', fileProcessCounter, fileCount)

        importFileLocation = utils.getImportMediaFileLocation(file, destDir, args['username'], fileProcessCounter)

        importPath = importFileLocation[0] + importFileLocation[1]
        # print importPath

        # check if destination directory exists, if not create it
        if not os.path.exists(importFileLocation[0]):
            os.makedirs(importFileLocation[0])

        # check if file exists
        if os.path.isfile(importPath):
            logging.info('\tfile has already been imported, skipping')
            print '\tfile has already been imported, skipping'

        else:
            logging.info("\timporting\t'%s'\n\tto\t\t'%s'", file, importPath)
            print "\timporting\t'%s'\n\tto\t\t'%s'" % (file, importPath)
            shutil.copy2(file, importPath)

        fileProcessCounter += 1




    #   move log file to destination directory

    currentDirectory = os.getcwd() + '/'
    logFilePath = currentDirectory + logFileName
    logFileDestinationDir = destDir + '/logs/'


    # check if destination directory exists, if not create it
    if not os.path.exists(logFileDestinationDir):
        os.makedirs(logFileDestinationDir)

    logFileDestination = logFileDestinationDir  + logFileName

    shutil.move(logFilePath, logFileDestination)




    #   print arguments
    utils.spacer()
    print 'ALL DONE!'
    logging.info('ALL DONE!')
    utils.bigSpacer()



if __name__ == '__main__':
    main()






























#EOF
