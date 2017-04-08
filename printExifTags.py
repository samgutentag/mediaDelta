#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Description
#       Used to print out exif tags from a passed directory of images or a
#       single image file.
#
#       Writes a log file to a 'logs' directory under the current working
#       directory, will create one if it is not already present
#
#------------------------------------------------------------------------------
#		Sample Usage
#   >   python printExifTags.py -s /Volumes/EOS_DIGITAL/
#   >   python printExifTags.py -s ~/Desktop/sampleImages/image.0001.CR2
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


#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():
    # setup parser
    parser = argparse.ArgumentParser(description='Output EXIF data of a given media file or files in a directory')

    # passing a single file
    parser.add_argument('-s', '--mediaSource', dest='mediaSource',
                        required=True,
                        help='Pass a directory of files or a single file to print its EXIF tags',
                        metavar='MEDIA_SOURCE')

    parser.add_argument('-date', '--dateOnly',
                        action='store_true', default = False,
                        required=False,
                        help='if passed, script will only print out the dateTime tags')

    parser.add_argument('-camera', '--cameraOnly',
                        action='store_true', default = False,
                        required=False,
                        help='if passed, script will only print out the camera related tags')


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

    fileCount = 0

    # attempt to process a passed file
    # if args['mediaFile']:
    if os.path.isfile(args['mediaSource']):
        try:

            if args['dateOnly']:
                print "printing Date EXIF tags for '%s'\n" % args['mediaSource']
                logging.info("printing Date EXIF tags for '%s'\n", args['mediaSource'])

                utils.prettyPrintDateTimeTags(args['mediaSource'])

            elif args['cameraOnly']:
                print "printing Camera EXIF tags for '%s'\n" % args['mediaSource']
                logging.info("printing Camera EXIF tags for '%s'\n", args['mediaSource'])

                utils.prettyPrintCameraTags(args['mediaSource'])


            else:
                print "printing EXIF tags for '%s'\n" % args['mediaSource']
                logging.info("printing EXIF tags for '%s'\n", args['mediaSource'])

                utils.prettyPrintTags(args['mediaSource'])
        except:
            print '>>> unable to process %s' % args['mediaSource']
            logging.info('>>> unable to process %s', args['mediaSource'])

    # attempts to process a directory of files
    elif os.path.isdir(args['mediaSource']):

        # process a directory of files
        filesToProcess = utils.getDirectoryContents(args['mediaSource'])
        fileProcessCounter = 1
        fileCount = len(filesToProcess)

        for file in filesToProcess:
            print '\n%s of %s' % (fileProcessCounter, len(filesToProcess))
            logging.info('\n%s of %s', fileProcessCounter, len(filesToProcess))

            # try:
            if args['dateOnly']:
                print "printing Date EXIF tags for '%s'\n" % file
                logging.info("printing Date EXIF tags for '%s'\n", file)
                utils.prettyPrintDateTimeTags(file)
            elif args['cameraOnly']:
                print "printing Camera EXIF tags for '%s'\n" % file
                logging.info("printing Camera EXIF tags for '%s'\n", file)
                utils.prettyPrintCameraTags(file)
            else:
                print "printing EXIF tags for '%s'\n" % file
                logging.info("printing EXIF tags for '%s'\n", file)
                utils.prettyPrintTags(file)

            # except:
            #     print '\tskipping %s' % file
            #     logging.info('\tskipping %s', file)

            utils.spacer()
            fileProcessCounter += 1

    # utils.spacer()

    #   Say Goodbye!
    utils.spacer()
    print 'ALL DONE!'
    logging.info('ALL DONE!')
    utils.bigSpacer()

    #   Move log file to destination directory
    currentDirectory = os.getcwd() + '/'
    logFilePath = currentDirectory + logFileName
    logFileDestinationDir = os.getcwd() + '/logs/'

    #   Check if destination directory exists, if not create it
    if not os.path.exists(logFileDestinationDir):
        os.makedirs(logFileDestinationDir)

    logFileDestination = logFileDestinationDir  + logFileName
    shutil.move(logFilePath, logFileDestination)



if __name__ == '__main__':
    main()





#EOF
