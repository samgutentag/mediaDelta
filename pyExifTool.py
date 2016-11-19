#!/usr/bin/end python

import pyexifinfo as p
import argparse
import json
import os
import shutil
import utils

#------------------------------------------------------------------------------
#		classes
#------------------------------------------------------------------------------

class cameraObject:

    def __init__(self, make, model, serial, software):
        self.make = make
        self.model = str(model).replace(' ','.')
        self.serial = serial
        self.software = str(software).split('(')[0].replace(' ', '.')

    def printInfo(self):
        print 'Camera Make:\t%s' % self.make
        print 'Camera Model:\t%s' % self.model
        print 'Serial Number:\t%s' % self.serial
        print 'Software:\t\t%s' % self.software

class mediaDateTimeObject:

    def __init__(self, tag, year, month, day, hour, minute, second, millisecond):
        self.tag = tag
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond

    def toString(self):
        dateTimeString = '%s%s%s%s%s%s%s' % (self.year, self.month, self.day,
                                            self.hour, self.minute, self.second,
                                            self.millisecond)
        return dateTimeString

    def printInfo(self):
        print 'tag:\t\t\t%s' % self.tag
        print 'year:\t\t\t%s' % self.year
        print 'month:\t\t\t%s' % self.month
        print 'day:\t\t\t%s' % self.day
        print 'hour:\t\t\t%s' % self.hour
        print 'minute:\t\t\t%s' % self.minute
        print 'second:\t\t\t%s' % self.second
        print 'millisecond:\t%s' % self.millisecond


#------------------------------------------------------------------------------
#		functions
#------------------------------------------------------------------------------

# uniform spacers
def spacer():
    print '\n'
    print '#' + '-'*79
    print '\n'
def bigSpacer():
    print '\n'
    print '#' + '!'*79
    print '#' + '!'*79
    print '\n'

# checks that a given file exists, and opens it
def openMediaFile(parser, arg):
    if not os.path.exists(arg):
        parser.error('The file %s does not exist' % arg)
    else:
        return open(arg, 'rb')

# checks that a given directory exists
def openMediaDirectory(parser, arg):
    if not os.path.exists(arg):
        parser.error('The directory %s does not exist' % arg)
    else:
        return arg

# convert json information gathered by exif tools into a dictionary
def JSONToDict(data):
    # print '>>> creating exifDict from json data...'

    if len(data) < 1:
        print '>>> this file has no exif data'
        return
    else:
        # dataDict = dict(sorted(data[0].iteritems()))
        dataDict = dict(sorted(data[0].iteritems()))
        # print '>>> done!'
        return dataDict


#------------------------------------------------------------------------------
#		file relocation functions
#------------------------------------------------------------------------------

# gets contents of a directory
def getDirectoryContents(dir):
    # print ">>> getting contents of directory '%s'" % dir

    directory_contents = []

    for root, directories, files in os.walk(dir):
        for filename in files:
            filePath = os.path.join(root, filename)
            directory_contents.append(filePath)
    return directory_contents

# construct file path and name of 'correctly' named file
def getFilePath(destinationDir, dateTimeStamp, cameraInfo, userName, extension):
    fileName = ''
    filePath = ''

    # clean destinationDir to not include tail slashes
    while destinationDir.endswith('/'):
        destinationDir = destinationDir[:-1]

    cleanCameraString = cameraLabelCleaner(cameraInfo, userName)
    filePath = '%s/%s/fullRes/%s.%s.%s/%s/' % (destinationDir,
                                                extension.upper(),
                                                dateTimeStamp.year,
                                                dateTimeStamp.month,
                                                dateTimeStamp.day,
                                                cleanCameraString)

    # camera model may not be known,
    if cameraInfo.model == 'NONE':
        # if it is not, try software,
        if cameraInfo.software == 'NONE':
            cameraName = ''
        # if that is not known, leave blank
        else:
            cameraName = '_' + cameraInfo.software
    else:
        cameraName = '_' + cameraInfo.model

    # formatting : YYYYMMDD_HHmmSS.sss.<ext>
    fileName = '%s%s%s_%s%s%s.%s.%s' % (dateTimeStamp.year,
                                        dateTimeStamp.month,
                                        dateTimeStamp.day,
                                        dateTimeStamp.hour,
                                        dateTimeStamp.minute,
                                        dateTimeStamp.second,
                                        dateTimeStamp.millisecond,
                                        extension)

    return filePath + fileName


# copy files and preserve metadata
def makeCopy(sourceFile, destinationFile):

    destinationFileName = destinationFile.split('/')[-1]

    destinationFileDirectory = destinationFile[:-len(destinationFileName)]

    # check that destination directory exists, else create it:
    if not os.path.exists(destinationFileDirectory):
        os.makedirs(destinationFileDirectory)

    # check if file exists, do not copy if it does
    if os.path.isfile(destinationFile):
        print 'file already exists... skipping' % destinationFile
    else:
        shutil.copy2(sourceFile, destinationFile)



#------------------------------------------------------------------------------
#		main exif tag formatting functions
#------------------------------------------------------------------------------

# compare two mediaDateTimeObjects and return earlier one
def getEarlierDateTime(tagA, tagB):

    # converts dateTime pieces into an integer for comparison
    tagAINT = int(tagA.year + tagA.month + tagA.day + tagA.hour + tagA.minute + tagA.second + tagA.millisecond)
    tagBINT = int(tagB.year + tagB.month + tagB.day + tagB.hour + tagB.minute + tagB.second + tagB.millisecond)

    # return the larger tag
    if tagAINT <= tagBINT:
        return tagA
    else:
        return tagB

# gets earlist date time tag, excludes dates in photoshop or camera profiles
# returns a list of (dateTimeTag, dateTimeValue)
def getMediaDateTimeStamp(data):

    # entryInfo = mediaDateTimeObject(tag, year, month, day, hour, minute, second, millisecond)
    earlyDateTimeInfo = mediaDateTimeObject('NONE', '9999', '99', '99', '99', '99', '99', '999')

    # collect all date related keys and values
    dateTimeTags = []

    # select dateTime key, value pairs as a subset
    for key, value in data.iteritems():
        if 'date' in key.lower():
            # exclude some odd tag keys
            if 'icc' not in key.lower():
                dateTimeTags.append([key, value])

    # go through dateTime tags to determine the earliest one
    for entry in dateTimeTags:

        # default values
        entryInfo = mediaDateTimeObject('NONE', '9999', '99', '99', '99', '99', '99', '999')

        # set entry tag
        entryInfo.tag = str(entry[0])
        dateTimeStamp = entry[1]

        # if year is '0000', we dont want it, break out!
        if dateTimeStamp.split(':')[0] == '0000':
            break

        # remove negative timezone adjustment if it exists
        try:
            dateTimeStamp = dateTimeStamp.split('-')[0]
        except:
            pass

        # remove positive timezone adjustment value if it exists
        try:
            dateTimeStamp = dateTimeStamp.split('+')[0]
        except:
            pass

        # try to split into dateStamp and timeStamp, get dateStamp
        try:
            dateStamp = dateTimeStamp.split(' ')[0]
        except:
            dateStamp = '9999:99:99'

        # try to split into dateStamp and timeStamp, get timeStamp
        try:
            timeStamp = dateTimeStamp.split(' ')[1]

            # sometimes time stamps have letters appened to the end of the second, lets remove those
            while timeStamp[len(timeStamp)-1].isalpha():
                timeStamp = timeStamp[:-1]
        except:
            timeStamp = '23:59:99.999'

        # set values for each
        entryInfo.year = dateStamp.split(':')[0]
        entryInfo.month = dateStamp.split(':')[1]
        entryInfo.day = dateStamp.split(':')[2]
        entryInfo.hour = timeStamp.split(':')[0]
        entryInfo.minute = timeStamp.split(':')[1]
        try:
            entryInfo.second = timeStamp.split(':')[2]
        except:
            entryInfo.second = '99.999'

        # try splitting secondStamp into secondStamp and millisecondStamp
        try:
            entryInfo.millisecond = entryInfo.second.split('.')[1]
            entryInfo.second = entryInfo.second.split('.')[0]

            # some time stamps come through with an alpha character(s) suffix
            # lets remove those if they exist
            while entryInfo.millisecond[len(entryInfo.millisecond)-1].isalpha():
                entryInfo.millisecond = entryInfo.millisecond[:-1]

        except:
            entryInfo.millisecond = '999'

        # format millisecondStamp to be a fixed length of 3 digits
        if len(entryInfo.millisecond) > 3:
            entryInfo.millisecond = entryInfo.millisecond[:4]

        while len(entryInfo.millisecond) < 3:
            entryInfo.millisecond = '0' + entryInfo.millisecond

        earlyDateTimeInfo = getEarlierDateTime(earlyDateTimeInfo, entryInfo)

    # print '>>> done!'
    return earlyDateTimeInfo

# gets camera and or software device information
# returns a list of (cameraMake, cameraModel, serialNumber, softwareName)
# defaults to 'NONE' if a piece of information can not be found
def getCameraModel(data):
    # print '>>> getting camera info...'

    # we want make, model, serial number, software
    cameraMake = 'NONE'
    cameraModel  = 'NONE'
    serialNumber = 'NONE'
    softwareName = 'NONE'

    for key,value in data.iteritems():
        # get serial number string i.e. '192029004068'
        if 'exif:serialnumber' in key.lower():
            serialNumber = str(data[key])
        # get make string i.e. 'Canon'
        if 'exif:make' in key.lower():
            cameraMake = str(data[key])
        # get model string i.e. 'Canon EOS 5D Mark III'
        if 'exif:model' in key.lower():
            cameraModel = str(data[key])
        # get software string i.e. 'Adobe Photoshop Lightroom 6.3 (Macintosh)''
        if 'exif:software' in key.lower():
            softwareName = str(data[key])

    # special case for iOS devices reporting software version
    if cameraMake.lower() == 'apple':
        softwareName = 'iOS %s' % softwareName

    cameraInfo = cameraObject(cameraMake, cameraModel, serialNumber, softwareName)

    # print '>>> done!'

    return cameraInfo

# print tags
def prettyPrintTags(dataDictionary):
    # print dataDictionary
    # print '>>> pretty printing EXIF tags'
    # for key, value in dataDictionary.iteritems():
    #     print '%s\t:\t%s' % (key, value)


    counter = 0
    longestTag = 0

    # get string length of longest key
    # assit in pretty printing
    for key in dataDictionary.keys():
        if len(key) > longestTag:
            longestTag = len(key)

    # pretty print exif tags
    for tag, entry in sorted(dataDictionary.iteritems()):
        # excludes text encoded tags
        # these are just a ton of garbage data we dont need
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail'):

            # calculate number of tab characters needed to pretty print
            tabsNeeded = ((longestTag - len(tag))/4) + 1

            # print all in line and numbered
            if counter < 100:
                print '%s:\t\t%s:' % (counter, tag),
            else:
                print '%s:\t%s:' % (counter, tag),
            print '\t' * tabsNeeded,
            print entry
            counter += 1

    # print '>>> done!'

# print dateTime tags
def prettyPrintDateTimeTags(dataDictionary):
    # print dataDictionary
    # print '>>> pretty printing EXIF tags'
    # for key, value in dataDictionary.iteritems():
    #     print '%s\t:\t%s' % (key, value)


    counter = 0
    longestTag = 0

    # get string length of longest key
    # assit in pretty printing
    for key in dataDictionary.keys():
        if len(key) > longestTag:
            longestTag = len(key)

    # pretty print exif tags
    for tag, entry in sorted(dataDictionary.iteritems()):
        # excludes text encoded tags
        # these are just a ton of garbage data we dont need
        if 'date' in tag.lower():

            # calculate number of tab characters needed to pretty print
            tabsNeeded = ((longestTag - len(tag))/4) + 1

            # print all in line and numbered
            if counter < 100:
                print '%s:\t\t%s:' % (counter, tag),
            else:
                print '%s:\t%s:' % (counter, tag),
            print '\t' * tabsNeeded,
            print entry
            counter += 1

    # print '>>> done!'

# pretty print a dictionary in key value pairs, well spaced
def prettyPrintDict(dictionary):

    longestKey = 0

    for key in dictionary:
        if len(key) > longestKey:
            longestKey = len(key)

    for key, value in sorted(dictionary.iteritems()):
        spacesNeeded = longestKey - len(key) + 4
        spaces = ' ' * spacesNeeded
        print '%s%s%s' % (key, spaces, value)

    return True




# clean up camera information for file naming
def cameraLabelCleaner(camera, userName):

    # camera.printInfo()

    cleanCameraString = ''


    # special cases for known cameras
    # adjustments for Apple cameras, (iPhones, iPads, etc)
    if camera.make == 'Apple':
        cleanCameraString = camera.make + '.' + camera.model + '.' + userName

    # adjustments for Canon cameras
    elif camera.make == 'Canon':
        # left pad all canon serial numbers with zeros to be 12 digits long
        if camera.serial == 'NONE':
            tempSerialNumber = ''
        else:
            tempSerialNumber = camera.serial

        while len(tempSerialNumber) < 13:
            tempSerialNumber = '0' + tempSerialNumber

        cleanCameraString = camera.model + '.' + userName + '.' + tempSerialNumber

    # adjustments for Kodak cameras
    elif camera.make == 'EASTMAN KODAK COMPANY':
        cleanCameraString = camera.model

    # adjustments for GoPro cameras
    elif camera.make == 'GoPro':
        cleanCameraString = camera.make + '.' + camera.model + '.' + userName

    # adjustments for Sony cameras
    elif camera.make == 'Sony':
        # sony camera models tend to have '-' in them, replace with '.'
        tempModel = camera.model
        tempModel = tempModel.replace('-', '.')

        cleanCameraString = camera.make + '.' + tempModel + '.' + userName

    # adjustments for Nikon cameras
    elif camera.make == 'NIKON CORPORATION':
        cleanCameraString = camera.model + '.' + userName


    else:
        # print 'camera make not was not an option...'
        # camera.printInfo()
        cleanCameraString = 'UNKNOWNCAMERA'


    return cleanCameraString


#------------------------------------------------------------------------------
#		file processing functions
#------------------------------------------------------------------------------

def processMediaFile(mediaFile, userName, destinationDir):
    # originalFilePath = str(mediaFile).split("'")[1]
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

    # spacer()
    exifTagsDict = JSONToDict(p.get_json(originalFilePath))

    # spacer()

    dateTimeStamp = getMediaDateTimeStamp(exifTagsDict)
    cameraInfo = getCameraModel(exifTagsDict)

    correctedFilePath = getFilePath(destinationDir, dateTimeStamp, cameraInfo, userName.lower(), extension)

    # print '\tmoving\t%s' % originalFilePath
    # print '\tto\t\t%s' % correctedFilePath
    # spacer()

    try:
        makeCopy(originalFilePath, correctedFilePath)
        print '\tmoved\t%s' % originalFilePath
        print '\tto\t\t%s' % correctedFilePath
    except:
        print 'skipping... already exsits...'

    # print '>>> done!'
    return True

def getUniqueCameras(mediaFile):
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

    # spacer()
    exifTagsDict = JSONToDict(p.get_json(originalFilePath))

    # spacer()
    cameraInfo = getCameraModel(exifTagsDict)
    # cameraInfo.printInfo()

    return cameraInfo


#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():
    # setup parser
    parser = argparse.ArgumentParser(description='Read EXIF data of a given media file, update filename and sort into structured directory')

    # script uses the artist name to help createu uinique file names
    parser.add_argument('-a', '--artistName', dest='artistName',
                        required=False,
                        default=os.getlogin(),
                        help='default artist name',
                        metavar='ARTIST_NAME')

    # passing a single file
    parser.add_argument('-f', '--mediaFile', dest='mediaFile',
                        required=False,
                        help='pass a single file to process',
                        metavar='MEDIA_FILE',
                        type=lambda x: openMediaFile(parser, x))

    # passing a directory (with or without sub directories) of files
    parser.add_argument('-d', '--mediaDirectory', dest='mediaDirectory',
                        required=False,
                        help='pass a directory of files to process, WARNING: RECURSIVE',
                        metavar='MEDIA_DIRECTORY',
                        type=lambda x: openMediaDirectory(parser, x))

    # output directory destination
    parser.add_argument('-o', '--outputDirectory', dest='outputDirectory',
                        required = True,
                        help = 'this is root directory that photos will be copied to',
                        metavar='OUTPUT_DIRECTORY')

    args = vars(parser.parse_args())

    bigSpacer()

    print 'Arguments...'
    # for key,value in sorted(args.iteritems()):
    #     print '%s\t%s' % (key, value)

    prettyPrintDict(args)

    cameraDict = {}

    # attempt to process a file if only one is given
    if args['mediaFile']:
        try:
            processMediaFile(args['mediaFile'], args['artistName'], args['outputDirectory'])

        except:
            print '>>> Could not process file'

    # process a directory
    elif args['mediaDirectory']:

        # process a directory of files
        filesToProcess = getDirectoryContents(args['mediaDirectory'])

        fileProcessCounter = 1
        bigSpacer()
        for file in filesToProcess:

            try:
                print '\n%s of %s' % (fileProcessCounter, len(filesToProcess))
                processMediaFile(file, args['artistName'], args['outputDirectory'])

                # build list of unique cameraInfo with counters
                cameraInfo = getUniqueCameras(file)
                # cameraInfo.printInfo()

                cameraString = '%s_%s_%s_%s' % (cameraInfo.make, cameraInfo.model, cameraInfo.serial, cameraInfo.software)

                if cameraString in cameraDict:
                    pass
                else:
                    cameraDict[cameraString] = file

            except:
                print 'skipping %s' % file

            fileProcessCounter += 1

        bigSpacer()
        # for key, value in sorted(cameraDict.iteritems()):
        #     print '%s\t%s' % (key, value)
        prettyPrintDict(cameraDict)

    bigSpacer()

    print 'ALL DONE!'

    bigSpacer()



if __name__ == '__main__':
    main()