#!/usr/bin/end python

import pyExifTool
import pyexifinfo as p
import argparse

import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')

# main processing of media file, gets exif data, setups up destination directory and filename, copies file
# def processMediaFile(mediaFile, userName, destinationDir):
def processMediaFile(mediaFile):
    # when a single file is passed, the file name needs to be trimmed
    try:
        originalFilePath = str(mediaFile).split("'")[1]
    # when a file is passed as part of a directory, it does not need to be trimmed
    except:
        originalFilePath = mediaFile

    # spacer()
    print ">>> processing '%s'" % originalFilePath
    extension = str(originalFilePath.split('.')[-1])

    # ignore dot files i.e. '.DS_Store'
    if originalFilePath.split('.')[0].endswith('/'):
        print 'ignoring %s' % originalFilePath
        return False

    # get information from exif tags, format dateTime, and Camera class objects
    exifTagsDict = pyExifTool.JSONToDict(p.get_json(originalFilePath))
    dateTimeStamp = pyExifTool.getMediaDateTimeStamp(exifTagsDict)
    cameraInfo = pyExifTool.getCameraInformation(exifTagsDict)

    # print information
    # pyExifTool.bigSpacer()
    pyExifTool.prettyPrintTags(exifTagsDict)
    pyExifTool.spacer()
    cameraInfo.printInfo()
    pyExifTool.spacer()
    dateTimeStamp.printInfo()
    pyExifTool.bigSpacer()



    return True


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
                        type=lambda x: pyExifTool.openMediaFile(parser, x))

    # passing a directory (with or without sub directories) of files
    parser.add_argument('-d', '--mediaDirectory', dest='mediaDirectory',
                        required=False,
                        help='pass a directory of files to process, WARNING: RECURSIVE',
                        metavar='MEDIA_DIRECTORY',
                        type=lambda x: pyExifTool.openMediaDirectory(parser, x))

    args = vars(parser.parse_args())

    print 'Arguments...'
    pyExifTool.prettyPrintDict(args)
    pyExifTool.bigSpacer()

    # attempt to process a passed file
    if args['mediaFile']:
        try:
            processMediaFile(args['mediaFile'])
        except:
            print '>>> Could not process file'

    # attempts to process a directory of files
    elif args['mediaDirectory']:

        # process a directory of files
        filesToProcess = pyExifTool.getDirectoryContents(args['mediaDirectory'])

        fileProcessCounter = 1
        for file in filesToProcess:
            try:
                print '\n%s of %s' % (fileProcessCounter, len(filesToProcess))
                processMediaFile(file)

            except:
                print 'skipping %s' % file

            fileProcessCounter += 1

    pyExifTool.spacer()

    print 'ALL DONE!'

    pyExifTool.bigSpacer()



if __name__ == '__main__':
    main()
