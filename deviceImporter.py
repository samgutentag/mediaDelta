#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Description
#       Script imports media files from a user passed directory to a user
#       specified destination.  This version of the importer script is designed
#       for media that comes from a single source device or camera.  Passing
#       tags for make and model.  In the future it will write the eif data to
#       the copied file. For example, a user imports from an SD card to a
#       portable hard drive.  Does very little to check if duplicates exists or
#       are being made.
#
#       Output destination is formatted by getting username from the user and
#       exif data from the media files being processed.
#
#       The output path is formatted as such:
#       <destinationDir>/<mediaType>/<camera>/<YYYY><MM><DD>/
#
#       The output filename is formatted as such:
#       <user>.<camera>.<YYYY><MM><DD>.<HH><mm><SS><sss>.<counter>.<extention>
#
#------------------------------------------------------------------------------
#		Sample Usage
#   >   python droneImporter.py -u $USER  -make DJI -model DJI.Mavic.Pro -s /Volumes/EOS_DIGITAL/ -d /Volumes/IMAGE_500/STAGING/
#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------

import argparse
import utils
import logging
import shutil
import os
import clipConverter
import getpass
import progressBar

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
def getImportMediaFileDestination(inputFile, destinationDir, user, counter, make, model):

    # print "\n>>> import processing '%s'" % inputFile
    logging.info(">>> import processing '%s'", inputFile)


    try:
        #   generate a mediaFileObject from the given input file
        mediaFileObject = utils.getMediaFileObject(inputFile, user)

        #   set mediaFileObject camera make and model for device
        mediaFileObject.camera.make = make
        mediaFileObject.camera.model = model

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
    importFilePath = '%s/%s/%s.%s/%s%s%s/' % (destinationDir,
                                        mediaFileObject.type,
                                        mediaFileObject.camera.make, mediaFileObject.camera.model,
                                        mediaFileObject.dateTime.year, mediaFileObject.dateTime.month, mediaFileObject.dateTime.day)

    return (importFilePath, importFileName)

#------------------------------------------------------------------------------
#   Main Function
#------------------------------------------------------------------------------
def main():

    #   Setup parser
    parser = argparse.ArgumentParser(description="Import Data from a memory card to a staging drive")

    parser.add_argument('-u', '--username', dest='username',
                        required = False,
                        default = getpass.getuser(),       # default to current user
                        help = 'tag files with the person who captured them',
                        metavar='USER_NAME')

    parser.add_argument('-make', '--deviceMake', dest='deviceMake',
                        required = True,
                        help = 'pass the device make for usage in organizing and writing exiftags',
                        metavar='DREVICEMAKE')

    parser.add_argument('-model', '--deviceModel', dest='deviceModel',
                        required = True,
                        help = 'pass the device model for usage in organizing and writing exiftags, use periods in place of spaces',
                        metavar='DEVICE_MODEL')

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
    logFileName = 'deviceImporter_%s.log' % logDateTime
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

    filesToAdjustExifData = []

    #   Process files and import if not already imported
    iterationCounter = 0
    print 'Device Import in progress...\n\t\t\tmake[%s]\n\t\t\t\tmodel[%s]' % (args['deviceMake'], args['deviceModel'])
    print 'Importing %s media files...' % str(fileCount)
    progressBar.print_progress(iterationCounter, fileCount, decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-')
    for file in filesToProcess:


        # progress_prefix = '\n%s of %s' % (fileProcessCounter, fileCount)
        logging.info('\n%s of %s', fileProcessCounter, fileCount)

        importFileDestination = getImportMediaFileDestination(file, destDir, args['username'], fileProcessCounter, args['deviceMake'], args['deviceModel'])

        if args['moveOnly']:
            utils.safeMove(file, importFileDestination[0], importFileDestination[1])
        else:
            utils.safeCopy(file, importFileDestination[0], importFileDestination[1])


        importPath = importFileDestination[0] + importFileDestination[1]

        #   set exif data on copied file to match device info
        filesToAdjustExifData.append(importPath)

        #   Update progressBar
        iterationCounter += 1
        progressBar.print_progress(iterationCounter, fileCount, decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-')

        fileProcessCounter += 1

    #   run command to update exif info on all the files we just imported
    exifArg_make = '-make=%s' % args['deviceMake']
    exifArg_model = '-model=%s' % args['deviceModel'].replace('.', ' ')

    exifArgs = [exifArg_make, exifArg_model]

    utils.setExifTags(exifArgs, filesToAdjustExifData)

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
