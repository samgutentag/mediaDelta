#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Sample Usage
#------------------------------------------------------------------------------
#
#   > python cameraReport.py -d ~/Desktop/testPhotos
#
#------------------------------------------------------------------------------

import pyExifTools
import argparse

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

    # spacer()
    # cameraInfo = getCameraInformation(exifTagsDict, cameraMake, cameraModel)
    cameraInfo = pyExifTools.getCameraInformation(exifTagsDict)
    # cameraInfo.printInfo()

    camString = '%s_%s_%s_%s' % (cameraInfo.make, cameraInfo.model, cameraInfo.serial, cameraInfo.software)

    # if camera is not alrady in dictionary, add it
    if camString not in cameraDict:
        cameraDict[camString] = [[cameraInfo, mediaFile]]
    # else the camera already exists, so append file to its list
    else:
        cameraDict[camString].append([cameraInfo, mediaFile])

    return cameraDict

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
                        type=lambda x: pyExifTools.openMediaFile(parser, x))

    # passing a directory (with or without sub directories) of files
    parser.add_argument('-d', '--mediaDirectory', dest='mediaDirectory',
                        required=False,
                        help='pass a directory of files to process, WARNING: RECURSIVE',
                        metavar='MEDIA_DIRECTORY',
                        type=lambda x: pyExifTools.openMediaDirectory(parser, x))

    args = vars(parser.parse_args())

    pyExifTools.bigSpacer()

    print 'Arguments...'
    pyExifTools.prettyPrintDict(args)

    cameraDict = {}

    # attempt to process a passed file
    if args['mediaFile']:
        try:
            cameraDict = getUniqueCameras(args['mediaFile'], cameraDict)
            print cameraDict
        except:
            print '>>> Could not process file'

    # attempts to process a directory of files
    elif args['mediaDirectory']:

        # process a directory of files
        filesToProcess = pyExifTools.getDirectoryContents(args['mediaDirectory'])

        fileProcessCounter = 1
        pyExifTools.bigSpacer()
        for file in filesToProcess:

            print 'Processing %s of %s' % (fileProcessCounter, len(filesToProcess))
            try:
                cameraDict = getUniqueCameras(file, cameraDict)
            except:
                print '>>> Could not process file'

            fileProcessCounter += 1

        pyExifTools.bigSpacer()

    counter = 1
    for key,value in cameraDict.iteritems():
        pyExifTools.spacer()
        # print 'Entry:\t%i' % (counter)
        # print '%s\t(%i)' % (key, len(value))
        print '(%i)\t%s' % (len(value), key)
        for val in value:
            print '\t%s' % (val[-1])
        counter += 1

    pyExifTools.spacer()
    pyExifTools.bigSpacer()



if __name__ == '__main__':
    main()
