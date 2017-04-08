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

# special stuff to handle known non ascii cahracters, blame sony! (not really)
import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')

#------------------------------------------------------------------------------
#		file processing functions
#------------------------------------------------------------------------------

# builds a dictionary of all unique camera objects found, and a file sample to match
def getUniqueCameras(mediaFile, cameraDict):
    # originalFilePath = str(mediaFile).split("'")[1]
    # when a single file is passed, the file name needs to be trimmed
    try:
        originalFilePath = str(mediaFile).split("'")[1]
    # when a file is passed as part of a directory, it does not need to be trimmed
    except:
        originalFilePath = mediaFile

    # print ">>> getting camera info for '%s'" % originalFilePath
    extension = str(originalFilePath.split('.')[-1])

    # ignore dot files i.e. '.DS_Store'
    if originalFilePath.split('.')[0].endswith('/'):
        # print 'ignoring %s' % originalFilePath
        return 'IGNORE'

    exifTagsDict = pyExifTools.JSONToDict(pyExifTools.p.get_json(originalFilePath))

    cameraInfo = pyExifTools.getCameraInformation(exifTagsDict)

    # cameraInfo.printInfo()

    # camString = '%s_%s_%s_%s' % (cameraInfo.make, cameraInfo.model, cameraInfo.serial, cameraInfo.software)
    camString = '%s_%s' % (cameraInfo.make, cameraInfo.model)

    if camString == 'NONE_NONE':
        camString = '%s' % (cameraInfo.software)

    # if camera is not alrady in dictionary, add it
    if camString not in cameraDict:
        cameraDict[camString] = [[cameraInfo, mediaFile]]
    # else the camera already exists, so append file to its list
    else:
        cameraDict[camString].append([cameraInfo, mediaFile])

    return cameraDict


def addToCameraDict(cameraDict, cameraObject, file):


    cameraObjectString = cameraObject.make + cameraObject.model + cameraObject.serial + cameraObject.software

    if cameraObjectString not in cameraDict:
        cameraDict[cameraObjectString] = [cameraObject, file]
    else:
        cameraDict[cameraObjectString].append(file)

    return cameraDict

def printCameraReport(cameraDict):

    # print list of all unique cameras, and their count
    for key,value in sorted(cameraDict.iteritems()):
        pyExifTools.spacer()
        print '(%i)\t%s' % (len(value), key)

    pyExifTools.bigSpacer()

    # print list of all unique cameras, their count, and all files that have the camera
    for key,value in sorted(cameraDict.iteritems()):
        pyExifTools.spacer()
        print '(%i)\t%s' % (len(value), key)
        for val in value:
            print '\t%s' % (val[-1])

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
    fileProcessCounter = 1
    fileCount = len(filesToProcess)

    #   this dictionary is as follows
        #   key:    cameraObject
        #   value:  list of filtes whose camera Object match
    cameraDict = {}

    #   build list of camera objects from the passed filesToProcess
    for file in filesToProcess:

        #   make mediaObject from file

        mediaFileObject = utils.getMediaFileObject(file)
        cameraObject = mediaFileObject.camera

        #   add (cameraObject, filePath) to cameraDict
        cameraDict = addToCameraDict(cameraDict, cameraObject, file)


    # print type(cameraDict)

    print cameraDict
    utils.spacer()

    for key, value in sorted(cameraDict.iteritems()):
        camObject = cameraDict[key][0]
        camObject.printInfo()

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
