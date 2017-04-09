#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Sample Usage
#------------------------------------------------------------------------------
#
#   > python cameraReporter.py -s ~/Desktop/testPhotos
#
#------------------------------------------------------------------------------

import utils
import shutil
import argparse
import logging
import getpass
import os
from datetime import datetime
import progressBar

# special stuff to handle known non ascii cahracters, blame sony! (not really)
import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')

#------------------------------------------------------------------------------
#		file processing functions
#------------------------------------------------------------------------------

#   builds a dictionary of all unique camera objects found, and a file sample to match
def addToCameraDict(cameraDict, cameraObject, file):

    cameraObjectString = cameraObject.make + cameraObject.model + cameraObject.serial + cameraObject.software

    if cameraObjectString not in cameraDict:
        cameraDict[cameraObjectString] = [cameraObject, file]
    else:
        cameraDict[cameraObjectString].append(file)

    return cameraDict

#   pretty print the camera report
def printCameraReport(cameraDict):

    for key, value in sorted(cameraDict.iteritems()):
        cameraObj = value[0]
        numFiles = len(value) - 1
        fileList = value[1:]

        utils.spacer()
        print '%s.%s\t\t%s files' % (cameraObj.make, cameraObj.model, numFiles)
        logging.info('%s.%s\t\t%s files', cameraObj.make, cameraObj.model, numFiles)
        cameraObj.printInfo()
        print 'Files:'
        logging.info('Files:')

        #   print list of files
        for item in fileList:
            print '\t%s' % item
            logging.info('\t%s', item)

#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():
    # setup parser
    parser = argparse.ArgumentParser(description='Read EXIF data of a given media file, update filename and sort into structured directory')

    parser.add_argument('-s', '--source', dest='sourceDirectory',
                        required = True,
                        help = 'the source directory of the files we want to convert, typically a memory card',
                        metavar='SOURCE_DIRECTORY')


    args = vars(parser.parse_args())

    #   setup logging
    logDateTime = datetime.now().strftime('%Y%m%d%H%M%S')
    logFileName = 'cameraReporter_%s.log' % logDateTime
    logging.basicConfig(format='%(message)s', filename=logFileName, level=logging.DEBUG)

    #   print arguments
    utils.bigSpacer()
    print 'Arguments...'
    utils.prettyPrintDict(args)
    utils.spacer()

    #   Get source directory contents
    filesToProcess = utils.getDirectoryContents(args['sourceDirectory'])
    fileProcessCounter = 0
    fileCount = len(filesToProcess)

    #   this dictionary is as follows
        #   key:    cameraObject as a string
        #   value:  list [cameraObject, file1, file2, file3, ...]
    cameraDict = {}

    #   start progressBar
    progressBar.print_progress(fileProcessCounter, fileCount, decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-')

    #   build list of camera objects from the passed filesToProcess
    for file in filesToProcess:

        # logging.info('\n%s of %s', fileProcessCounter+1, fileCount)

        #   make mediaObject from file
        mediaFileObject = utils.getMediaFileObject(file)
        cameraObject = mediaFileObject.camera

        #   add (cameraObject, filePath) to cameraDict
        cameraDict = addToCameraDict(cameraDict, cameraObject, file)

        #   update progressBar
        fileProcessCounter += 1
        progressBar.print_progress(fileProcessCounter, fileCount, decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-')


    printCameraReport(cameraDict)

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
