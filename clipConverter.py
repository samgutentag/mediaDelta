#!/usr/bin/end python


from moviepy.editor import *
import utils
import shutil
import argparse
import logging
import getpass
import os
from datetime import datetime

def resizeClip(inputFilePath, outputFilePath, width, height):

    print 'starting %sx%s resize of %s' % (width, height, inputFilePath)
    logging.info('starting %sx%s resize of %s', width, height, inputFilePath)

    #   get the input file clip
    inputClip = VideoFileClip(inputFilePath)

    #   resize this clip
    clip_resized = inputClip.resize( (width, height) )

    #   write resized clip to a new file
    clip_resized.write_videofile(outputFilePath,
                        # fps = 23.975,
                        # fps = 60,
                        codec='libx264')

    #    write exif tags from original file to the new converted file
    print 'finished'
    logging.info('finished')

def resizeClipList(clipList, width, height):


    for clip in clipList:

        #   file path for clip
        clipPath = clip[0] + clip[1]

        #   create downrezed video file
        downRez_fileName = clip[0] + '%sx%s/' % (width, height) + clip[1]

        # create downRez Directory if it does not already exist
        if not os.path.exists(clip[0] + '%sx%s/' % (width, height)):
            os.makedirs(clip[0] + '%sx%s/' % (width, height))

        #   convert Clip and write it to disk
        resizeClip(clipPath, downRez_fileName, width, height)

def main():

    #   Setup parser
    parser = argparse.ArgumentParser(description="Batch convert clips to specific resolutions")

    parser.add_argument('-s', '--source', dest='sourceDirectory',
                        required = True,
                        help = 'the source directory of the files we want to convert, typically a memory card',
                        metavar='SOURCE_DIRECTORY')

    parser.add_argument('-d', '--destination', dest='destinationDirectory',
                        required = False,
                        help='the destination root directory of the files we want to import, typically on an external hard drive',
                        metavar='DESTINATION_DIRECTORY')

    parser.add_argument('-width', '--resizeWidth', dest='resizeWidth',
                        required = True,
                        help='when resizing clips, set the width in pixels',
                        metavar='RESIZE_WIDTH')

    parser.add_argument('-height', '--resizeHeight', dest='resizeHeight',
                        required = True,
                        help='when resizing clips, set the height in pixels',
                        metavar='RESIZE_HEIGHT')


    args = vars(parser.parse_args())

    #   setup logging
    logDateTime = datetime.now().strftime('%Y%m%d%H%M%S')
    logFileName = 'clipConverter_%s.log' % logDateTime
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


    #   Sanitize input width and height values to be even numbers
    resizeWidth = args['resizeWidth']
    if int(resizeWidth) % 2 == 1:
        resizeWidth = resizeWidth - 1

    resizeHeight = args['resizeHeight']
    if int(resizeHeight) % 2 == 1:
        resizeHeight = resizeHeight - 1


    #   if a destinationDir was passed use it, else set one as sibling of sourceDirectory
    if args['destinationDirectory']:
        destDir = args['destinationDirectory']
        #   Clean up destination directory name
        while destDir[-1] == '/':
            destDir = destDir[:-1]

        if destDir[-1] != '/':
            destDir = destDir + '/'

    else:
        #   set destination dir to be sibling of source directory
        destDir = args['sourceDirectory']
        #   Clean up destination directory name
        while destDir[-1] == '/':
            destDir = destDir[:-1]

        #   replace directory with 'CONVERTED'
        destDir = destDir[:destDir.rfind('/')] + '/CONVERTED/'

    filesToAdjustExifData = []
    # clipList = []

    #   Process files and import if not already imported
    for file in filesToProcess:

        print '\n%s of %s' % (fileProcessCounter, fileCount)
        logging.info('\n%s of %s', fileProcessCounter, fileCount)

        #   get MediaFileObject
        mediaFileObject = utils.getMediaFileObject(file)

        # only convert Video type media
        if mediaFileObject.type == 'VIDEO':

            #   set converted clip file path
            convertedClipPath = file.replace(args['sourceDirectory'], destDir)


            #   if destination directory does not exists, create it
            convertedClipDir = convertedClipPath[:convertedClipPath.rfind('/')]
            if not os.path.exists(convertedClipDir):
                print '%s did not exist, creating it' % convertedClipDir
                logging.info('%s did not exist, creating it', convertedClipDir)
                os.makedirs(convertedClipDir)

            #   get file extension
            fileExtension = convertedClipPath[convertedClipPath.rfind('.'):]

            #   create suffix string for file name
            suffix = '_%sx%s%s' % (resizeWidth, resizeHeight, fileExtension)

            #   set final convertedClipPath with new suffix
            convertedClipPath = convertedClipPath[:convertedClipPath.rfind('.')] + suffix

            #   Convert clip
            resizeClip(file, convertedClipPath, resizeWidth, resizeHeight)

        else:
            print 'this tool only converts video clips, skipping...'




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



#   EOF
