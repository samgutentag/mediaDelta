#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Description
#       Script imports media files from a user passed directory to a user
#       specified destination.  For example, a user imports from an SD card to
#       a portable hard drive.  Does very little to check if duplicates exists
#       or are being made.
#
#       Output destination is formatted by getting username from the user and
#       exif data from the media files being processed.
#
#       The output path is formatted as such:
#       <destinationDir>/<camera>/<mediaType>/<YYYY><MM><DD>/
#
#       The output filename is formatted as such:
#       <user>.<camera>.<YYYY><MM><DD>.<HH><mm><SS><sss>.<counter>.<extention>
#
#------------------------------------------------------------------------------
#		Sample Usage
#   >   python importer.py -u $USER -s /Volumes/EOS_DIGITAL/ -d /Volumes/IMAGE_500/STAGING/
#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------

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

#------------------------------------------------------------------------------
#   Formatting Functions
#------------------------------------------------------------------------------

#   formats file name and destination directory for easy sorting
def getImportMediaFileLocation(inputFile, destinationDir, user, counter):

    print ">>> import processing '%s'" % inputFile
    logging.info(">>> import processing '%s'", inputFile)


    try:
        #   generate a mediaFileObject from the given input file
        mediaFileObject = utils.getMediaFileObject(inputFile, user)

        #   set mediaFileObject camera make and model for drone
        mediaFileObject.camera.make = 'DJI'
        mediaFileObject.camera.model = 'DJI.Mavic.Pro'

    except:
        print 'ERROR:\tcould not create mediaFileObject from \'%s\', skipping...' % inputFile
        logging.warning('ERROR:\tcould not create mediaFileObject from \'%s\', skipping...', inputFile)
        return 'NULL'

    #   set file name and path
    #   format: <user>.<camera>.<YYYY><MM><DD>.<HH><mm><SS><sss>.<counter>.<extention>
    importFileName = '%s.%s.%s%s%s.%s%s%s%s.%s.%s' %   (user,
                                                    mediaFileObject.camera.model,
                                                    mediaFileObject.dateTime.year, mediaFileObject.dateTime.month, mediaFileObject.dateTime.day,
                                                    mediaFileObject.dateTime.hour, mediaFileObject.dateTime.minute, mediaFileObject.dateTime.second, mediaFileObject.dateTime.millisecond,
                                                    str(counter),
                                                    mediaFileObject.extension.lower())

    #   format: <destinationDir>/<camera>/<mediaType>/<YYYY><MM><DD>/
    importFilePath = '%s/%s/%s/%s%s%s/' % (destinationDir,
                                        mediaFileObject.camera.model,
                                        mediaFileObject.type,
                                        mediaFileObject.dateTime.year, mediaFileObject.dateTime.month, mediaFileObject.dateTime.day)

    return (importFilePath, importFileName)


#------------------------------------------------------------------------------
#   Main Function
#------------------------------------------------------------------------------
def main():

    #   Setup parser
    parser = argparse.ArgumentParser(description="Import Data from a memory card to a staging drive")

    parser.add_argument('-u', '--username', dest='username',
                        required = True,
                        help = 'tag files with the person who captured them',
                        metavar='USER_NAME')

    # parser.add_argument('-drone', dest='droneName',
    #                     required = True,
    #                     help = 'tag files with the drone model used to capture them',
    #                     metavar='DRONE_NAME')

    parser.add_argument('-r', '--resolution', dest='downsizeResolution',
                        required = False,
                        help = 'specify resolutions to downsize original clips to, ideal for social media sharing',
                        metavar='DOWNSIZE_RESOLUTION')

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
    logFileName = 'importer_%s.log' % logDateTime
    logging.basicConfig(format='%(message)s', filename=logFileName, level=logging.DEBUG)

    #   print arguments
    utils.bigSpacer()
    print 'Arguments...'
    utils.prettyPrintDict(args)
    utils.spacer()

    #   Get source directory contents
    filesToProcess = utils.getDirectoryContents(args['sourceDirectory'])
    fileProcessCounter = 1
    fileCount = len(filesToProcess)

    #   Clean up destination directory name
    destDir = args['destinationDirectory']
    while destDir[-1] == '/':
        destDir = destDir[:-1]

    #   Process files and import if not already imported
    for file in filesToProcess:

        print '\n%s of %s' % (fileProcessCounter, fileCount)
        logging.info('\n%s of %s', fileProcessCounter, fileCount)

        importFileLocation = getImportMediaFileLocation(file, destDir, args['username'], fileProcessCounter)

        utils.safeCopy(file, importFileLocation[0], importFileLocation[1])

        importPath = importFileLocation[0] + importFileLocation[1]

        #   set exif data on copied file to match drone info
        utils.setExifTag('-make', 'DJI', importPath)
        utils.setExifTag('-model', 'DJI.Mavic.Pro', importPath)


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
