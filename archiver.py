#!/usr/bin/end python


#------------------------------------------------------------------------------
#		Sample Usage
#------------------------------------------------------------------------------
#
#   > python archiver.py -a samgutentag -d /Volumes/GoProBackUps/DateCorrected/correctedFiles/02b_M-N/ -o /Volumes/MacPak500GB/photos > ~/Desktop/pyExifLog_corrected_02b_take2.txt
#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------

import argparse
import utils
from datetime import datetime

# special stuff to handle known non ascii cahracters, blame sony! (not really)
import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')


#------------------------------------------------------------------------------
#		file relocation functions
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
#		file processing functions
#------------------------------------------------------------------------------


def getCorrectedArchiveFilePath(destinationDir, mediaFileObject):
    fileName = ''
    dirName = ''
    counter = '0001'

    # clean destinationDir to not include tail slashes, if they exist
    while destinationDir.endswith('/'):
        destinationDir = destinationDir[:-1]

    #  format:  'destination/mediaType(plural)/YYYY/YYYY.MM/MM.<eventName>/'
    #  example: 'photos/images/2016/2016.12/12.christmas/'
    #  example: 'photos/videos/2016/2016.11/11.thanksgiving'
    dirName = '%s/%ss/%s/%s.%s/' % (destinationDir,
                                            mediaFileObject.type,
                                            mediaFileObject.dateTime.year,
                                            mediaFileObject.dateTime.year,
                                            mediaFileObject.dateTime.month)
    # format:  'YYYYMMDD.HHMMSSsss.<creator>.<counter>.<extension>'
    fileName = '%s%s%s.%s%s%s%s.%s.%s.%s' % (mediaFileObject.dateTime.year,
                                                mediaFileObject.dateTime.month,
                                                mediaFileObject.dateTime.day,
                                                mediaFileObject.dateTime.hour,
                                                mediaFileObject.dateTime.minute,
                                                mediaFileObject.dateTime.second,
                                                mediaFileObject.dateTime.millisecond,
                                                mediaFileObject.creator,
                                                counter,
                                                mediaFileObject.extension)

    # return dirName + fileName
    return (dirName, fileName)



def archiveMediaFile(inputFile, destinationDir, creator):

    startTime = datetime.now()

    print ">>> processing '%s'" % inputFile
    archivedMediaFilePath = ''

    try:
        mediaFileObject = utils.getMediaFileObject(inputFile, creator)
    except:
        print 'ERROR:\tcould not create mediaFileObject from \'%s\', skipping...' % inputFile
        return inputFile


    # make Corrected File Path
    correctedFilePath = getCorrectedArchiveFilePath(destinationDir, mediaFileObject)

    # copy file, returns destinationDirectory and destinationFile
    archivedMediaFilePath = utils.makeCopy(inputFile, correctedFilePath[0], correctedFilePath[1])


    print 'Archived\t%s\nto\t\t\t%s' % (inputFile, archivedMediaFilePath)
    print '\t[%s]' % str(datetime.now() - startTime)

    return archivedMediaFilePath


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
                        type=lambda x: utils.openMediaFile(parser, x))

    # passing a directory (with or without sub directories) of files
    parser.add_argument('-d', '--mediaDirectory', dest='mediaDirectory',
                        required=False,
                        help='pass a directory of files to process, WARNING: RECURSIVE',
                        metavar='MEDIA_DIRECTORY',
                        type=lambda x: utils.openMediaDirectory(parser, x))

    # output directory destination
    parser.add_argument('-o', '--outputDirectory', dest='outputDirectory',
                        required = True,
                        help = 'this is the root destination directory that photos will be copied to',
                        metavar='OUTPUT_DIRECTORY')

    # creator name helps with identification when multiple photographers or artists are contributing to a single collection
    parser.add_argument('-c', '--creatorName', dest='creatorName',
                        required = True,
                        help = 'user provided creator name, used for tagging with multiple artists or photographers into a single collection',
                        metavar='CREATOR_NAME')


    args = vars(parser.parse_args())

    utils.bigSpacer()
    print 'Arguments...'
    utils.prettyPrintDict(args)
    utils.bigSpacer()

    startTime = datetime.now()
    fileCount = 0

    # attempt to process a passed file
    if args['mediaFile']:

        print '\tStarted: %s' % datetime.now().time()

        archivedFilePath = archiveMediaFile(args['mediaFile'], args['outputDirectory'], args['creatorName'])
        fileCount = 1

        print '\tFinished: %s' % datetime.now().time()

    # attempts to process a directory of files
    elif args['mediaDirectory']:

        # process a directory of files
        filesToProcess = utils.getDirectoryContents(args['mediaDirectory'])


        fileProcessCounter = 1
        fileCount = len(filesToProcess)
        for file in filesToProcess:

            print '\n%s of %s ' % (fileProcessCounter, fileCount)

            archivedFilePath = archiveMediaFile(file, args['outputDirectory'], args['creatorName'])


            fileProcessCounter += 1

    endTime = datetime.now()
    duration = endTime - startTime


    utils.spacer()

    print 'REPORT >>>'

    print 'Processed %s files in %s' % (fileCount, duration)

    print '\tStarted at:\t\t%s' % startTime.time()
    print '\tFinished at:\t%s' % endTime.time()

    print

    filesPerMinute = float(fileCount)/duration.seconds/60
    print 'Average Files Per Minute:\t%s' % str(filesPerMinute)

    secondsPerFile = duration.seconds/float(fileCount)
    print 'Average Seconds Per File:\t%s' % secondsPerFile






    utils.bigSpacer()
    print 'Done!'
    utils.bigSpacer()

if __name__ == '__main__':
    main()
