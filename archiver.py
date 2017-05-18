#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Description
#       Script is ideal for archiving large photo or video libraries, uses exif
#       tags to sort media files into a structured folder system.  If duplicates
#       are found, they are given an incremented counter in the file name, up to
#       9999, after that, the counter loops back over itself, overwriting 0001, etc.
#
#       Output destination is formatted by getting username from the user and
#       exif data from the media files being processed.
#
#       The output path is formatted as such:
#       <destinationDir>/<mediaType>/<YYYY>/<YYYY><MM>/
#
#       The output filename is formatted as such:
#       <YYYY><MM><DD>.<HH><MM><SS><sss.<creator>.<counter>.<extension>
#
#------------------------------------------------------------------------------
#		Sample Usage
#   >   python archiver.py -u $USER -s /Volumes/EOS_DIGITAL/ -d /Volumes/IMAGE_500/STAGING/
#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------

import argparse
import utils
from datetime import datetime
from datetime import timedelta
import logging
import shutil
import os
import getpass
import progressBar


# special stuff to handle known non ascii cahracters, blame sony! (not really)
import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')

#------------------------------------------------------------------------------
#   Formatting Functions
#------------------------------------------------------------------------------

#   formats file name and destination directory for easy sorting
def getArchiveMediaFileDestination(inputFile, destinationDir, user):

    startTime = datetime.now()

    # print "\n>>> archive processing '%s'" % inputFile
    logging.info(">>> archive processing '%s'",inputFile)

    try:
        #   generate a mediaFileObject from the given input file
        mediaFileObject = utils.getMediaFileObject(inputFile, user)
    except:
        print 'ERROR:\tcould not create mediaFileObject from \'%s\', skipping...' % inputFile
        logging.warning('ERROR:\tcould not create mediaFileObject from \'%s\', skipping...', inputFile)
        return 'NULL'


    #   Set file name and path
    archiveFileName = ''
    archiveFilePath = ''
    counter = '0001'

    #   format:  <YYYY><MM><DD>.<HH><MM><SS><sss.<creator>.<counter>.<extension>
    archiveFileName = '%s%s%s.%s%s%s%s.%s.%s.%s' % (mediaFileObject.dateTime.year, mediaFileObject.dateTime.month, mediaFileObject.dateTime.day,
                                                    mediaFileObject.dateTime.hour, mediaFileObject.dateTime.minute, mediaFileObject.dateTime.second, mediaFileObject.dateTime.millisecond,
                                                    mediaFileObject.creator,
                                                    counter,
                                                    mediaFileObject.extension)

    #   format: <destinationDir>/<mediaType>/<YYYY>/<YYYY><MM>/
    archiveFilePath = '%s/%s/%s/%s.%s/' % (destinationDir,
                                            mediaFileObject.type,
                                            mediaFileObject.dateTime.year,
                                            mediaFileObject.dateTime.year, mediaFileObject.dateTime.month)

    return (archiveFilePath, archiveFileName)


#------------------------------------------------------------------------------
#	Main Function
#------------------------------------------------------------------------------

def main():

    #   Setup parser
    parser = argparse.ArgumentParser(description='Read EXIF data of a given media file, update filename and sort into structured directory')

    parser.add_argument('-u', '--username', dest='username',
                        required = False,
                        default = getpass.getuser(),       # default to current user
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

    parser.add_argument('-move', '--moveOnly',
                        action='store_true', default = False,
                        required=False,
                        help='if passed, script will move teh files from source to destination, not make copies')


    args = vars(parser.parse_args())

    #   setup logging
    logDateTime = datetime.now().strftime('%Y%m%d%H%M%S')
    logFileName = 'archiver_%s.log' % logDateTime
    logging.basicConfig(format='%(message)s', filename=logFileName, level=logging.DEBUG)

    #   print arguments
    utils.bigSpacer()
    print 'Arguments...'
    utils.prettyPrintDict(args)
    utils.spacer()

    # Get source directory countents
    filesToProcess = utils.getDirectoryContents(args['sourceDirectory'])
    fileProcessCounter = 1
    fileCount = len(filesToProcess)

    #   Clean destination directory name
    destDir = args['destinationDirectory']
    while destDir[-1] == '/':
        destDir = destDir[:-1]

    #   Process files and archive them to their final destination, handles duplicates
    iterationCounter = 0
    print 'Archiving %s media files...' % str(fileCount)
    progressBar.print_progress(iterationCounter, fileCount, decimals=1, bar_length=40, complete_symbol='#', incomplete_symbol='-')
    for file in filesToProcess:

        # print '\n%s of %s ' % (fileProcessCounter, fileCount)
        logging.info('\n%s of %s ', fileProcessCounter, fileCount)

        # archivedFilePath = utils.archiveMediaFile(file, args['outputDirectory'], args['creatorName'])
        archiveFileDestination = getArchiveMediaFileDestination(file, destDir, args['username'])

        archivePath = archiveFileDestination[0] + archiveFileDestination[1]

        if args['moveOnly']:
            utils.safeMove(file, archiveFileDestination[0], archiveFileDestination[1])
        else:
            utils.safeCopy(file, archiveFileDestination[0], archiveFileDestination[1])

        #   Update progressBar
        iterationCounter += 1
        progressBar.print_progress(iterationCounter, fileCount, decimals=1, bar_length=40, complete_symbol='#', incomplete_symbol='-')

        fileProcessCounter += 1

    #   Say Goodbye!
    utils.spacer()
    print 'ALL DONE!'
    logging.info('ALL DONE!')
    utils.bigSpacer()

    #   Move log file to destination directory
    currentDirectory = os.getcwd() + '/'
    logFilePath = currentDirectory + logFileName
    logFileDestinationDir = destDir + '/logs/'

    #   Check if destination directory exists, if not create it
    if not os.path.exists(logFileDestinationDir):
        os.makedirs(logFileDestinationDir)

    logFileDestination = logFileDestinationDir  + logFileName
    shutil.move(logFilePath, logFileDestination)


if __name__ == '__main__':
    main()




























#EOF
