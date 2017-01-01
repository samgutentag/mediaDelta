#!/usr/bin/end python


import pyexifinfo as p
import argparse
import json
import os
import shutil

# special stuff to handle known non ascii cahracters, blame sony! (not really)
import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')

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


class mediaFileObject:

    def __init__(self, type, extension, dateTime, camera, creator):
        self.type = type
        self.extension = extension
        self.dateTime = dateTime
        self.camera = camera
        self.creator = creator

    def printInfo(self):
        print 'type:\t\t%s' % (self.type)
        print 'extension:\t\t%s' % (self.extension)
        print 'dateTime:\t\t%s' % (self.dateTime)
        print 'camera:\t\t%s' % (self.camera)
        print 'creator:\t\t%s' % (self.creator)


class dateTimeObject:

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
def bigSpacer():
    print '\n'
    print '#' + '!'*79
    print '#' + '!'*79

# checks that a given file exists, and opens it
def openMediaFile(parser, arg):
    if not os.path.exists(arg):
        parser.error('The file %s does not exist' % arg)
    else:
        return open(arg, 'rb')

# closes passed file
def closeMediaFile(file):
    file.close()

# checks that a given directory exists
def openMediaDirectory(parser, arg):
    if not os.path.exists(arg):
        parser.error('The directory %s does not exist' % arg)
    else:
        return arg

# convert json information gathered by exif tools into a dictionary
def JSONToDict(data):
    if len(data) < 1:
        print '>>> this file has no exif data'
        return
    else:
        dataDict = dict(sorted(data[0].iteritems()))
        return dataDict


#------------------------------------------------------------------------------
#		file relocation functions
#------------------------------------------------------------------------------

# gets contents of a directory, returns directory contents as a list
# prunes only valid media file formats
def getDirectoryContents(dir):

    directory_contents = []

    for root, directories, files in os.walk(dir):
        for filename in files:
            # only add files htat are a valid media file type
            if isValidMediaFileType(filename)[0]:
                filePath = os.path.join(root, filename)
                directory_contents.append(filePath)
    return directory_contents

# check if file is a known image or video format, returns [bool, string] tuple
def isValidMediaFileType(file):

    extensionToCheck = file.split('.')[-1].upper()

    validImageFileExtensions = ['JPG', 'PNG', 'TIF', 'TIFF', 'CR2', 'BMP', 'GIF']
    validVideoFileExtensions = ['MOV', 'MP4', 'MPG', 'M4V', '3G2', 'ASF', 'AVI']

    if extensionToCheck in validVideoFileExtensions:
        return (True, 'image', extensionToCheck)
    elif extensionToCheck in validImageFileExtensions:
        return (True, 'video', extensionToCheck)
    else:
        return (False, 'ignore', extensionToCheck)

# construct file path and name of 'correctly' named file
def getFilePath(destinationDir, mediaFile, event):
    fileName = ''
    dirName = ''

    # clean destinationDir to not include tail slashes
    while destinationDir.endswith('/'):
        destinationDir = destinationDir[:-1]

    #  format:  'destination/type(plural)/YYYY/YYYY.MM/MM.<eventName>/'
    #  example: 'photos/images/2016/2016.12/12.christmas/'
    #  example: 'photos/videos/2016/2016.11/11.thanksgiving'
    dirName = '%s/%ss/%s/%s.%s/%s.%s/' % (destinationDir,
                                            mediaFile.type,
                                            mediaFile.dateTime.year,
                                            mediaFile.dateTime.year,
                                            mediaFile.dateTime.month,
                                            mediaFile.dateTime.month,
                                            event)

    fileName '%s%s%s.%s%s%s%s.%s.%s.%s.%s' = (mediaFile.dateTime.year,
                                                mediaFile.dateTime.month,
                                                mediaFile.dateTime.day,
                                                mediaFile.dateTime.hour,
                                                mediaFile.dateTime.minute,
                                                mediaFile.dateTime.second,
                                                mediaFile.dateTime.millisecond,
                                                event,
                                                mediaFile.creator,
                                                '0001',  # counter
                                                mediaFile.extension)

    # return dirName + fileName
    return (dirName, fileName)

# copy files and preserve metadata
# def makeCopy(sourceFile, destinationFile):
def makeCopy(sourceFile, destinationDirectoryName, destinationFileName):

    # increment counter when file already exists, helps elliminate file overwrite
    # fails out after 9999 copies are found, instead dumps all subsequent files to
    # counter '0000', WILL OVERWRITE
    def incrementCounter(sourceName):
        # get current counter value
        currentCounter = sourceName.split('.')[-2]

        # trim leading zeros
        while currentCounter[:1] == '0':
            currentCounter = currentCounter[1:]

        # format to integer and increment
        if int(currentCounter) < 9999:
            counter = int(currentCounter) + 1
        else:
            print '>>>>>>>\t9999 copies already exist!'
            return '0000'

        # format to string and left side zero pad counter
        newCounter = str(counter)
        while len(newCounter) < 5:
            newCounter = '0' + newCounter

        incrementendFileName = sourceName.replace(currentCounter, newCounter)

        return incrementendFileName

    # check if destination directory exists, if not create it
    if not os.path.exists(destinationDirectoryName):
        os.makedirs(destinationDirectoryName)

    # check if file exists
    while os.path.isfile(destinationFileName):
        # this file exists! increment the counter
        destinationFileName = incrementCounter(destinationFileName)

    # destination full file path
    destinationFullPath = '%s%s' % (destinationDirectoryName, destinationFileName)

    print 'copying %s to %s%s' % (sourceFile, destinationDirectoryName, destinationFileName)
    print 'copying %s to %s' % (sourceFile, destinationFullPath)

    # copy file
    # shutil.copy2(sourceFile, destinationFullPath)

    return (destinationDirectoryName, destinationFileName)


#------------------------------------------------------------------------------
#		main exif tag formatting functions
#------------------------------------------------------------------------------

# compare two dateTimeObjects and return earlier one
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
# returns a list of dateTImeObject
def getDateTimeObject(exifData):

    # entryInfo = dateTimeObject(tag, year, month, day, hour, minute, second, millisecond)
    earlistDateTimeObject = dateTimeObject('NONE', '9999', '99', '99', '99', '99', '99', '999')

    # collect all date related keys and values
    dateTimeTags = []

    # select dateTime (key, value) pairs as a subset
    for key, value in exifData.iteritems():
        if 'date' in key.lower():
            # exclude some odd tag keys
            if 'icc' not in key.lower():
                dateTimeTags.append([key, value])

    # go through dateTime tags to determine the earliest one
    for entry in dateTimeTags:

        entry_tag = str(entry[0])
        entry_dateTimeStamp = entry[1]

        # if year is before 1975, we dont want it, break out!
            # this is to remove false low years that some software
            # defaults to writing out the date at the epoch
        if int(entry_dateTimeStamp.split(':')[0]) < 1975:
            break

        # remove negative timezone adjustment if it exists
        try:
            entry_dateTimeStamp = entry_dateTimeStamp.split('-')[0]
        except:
            pass

        # remove positive timezone adjustment value if it exists
        try:
            entry_dateTimeStamp = entry_dateTimeStamp.split('+')[0]
        except:
            pass

        # try to split into dateStamp and timeStamp, get dateStamp
        try:
            entry_dateStamp = entry_dateTimeStamp.split(' ')[0]
        except:
            entry_dateStamp = '9999:99:99'

        # try to split into dateStamp and timeStamp, get timeStamp
        try:
            entry_timeStamp = entry_dateTimeStamp.split(' ')[1]

            # sometimes time stamps have letters appened to the end of the second, lets remove those
            while entry_timeStamp[len(timeStamp)-1].isalpha():
                entry_timeStamp = entry_timeStamp[:-1]
        except:
            entry_timeStamp = '23:59:99.999'

        # set values for each
        yearTag = entry_dateStamp.split(':')[0]
        monthTag = entry_dateStamp.split(':')[1]
        dayTag = entry_dateStamp.split(':')[2]
        hourTag = entry_timeStamp.split(':')[0]
        minuteTag = entry_timeStamp.split(':')[1]

        # split out secondTag, else default to '99'
        try:
            secondTag = entry_timeStamp.split(':')[2]
        except:
            secondTag = '99.999'

        # try splitting second into secondStamp and millisecondStamp
        try:
            millisecondTag = secondTag.split('.')[1]
            secondTag = secondTag.split('.')[0]

            # some time stamps come through with an alpha character(s) suffix
            # lets remove those if they exist
            while millisecondTag[len(millisecondTag)-1].isalpha():
                millisecondTag = millisecondTag[:-1]

            # format millisecondStamp to be a fixed length of 3 digits
            if len(millisecondTag) > 3:
                millisecondTag = millisecondTag[:4]

            while len(millisecondTag) < 3:
                millisecondTag = '0' + millisecondTag

        except:
            millisecondTag = '999'


        entry_dateTimeObject = dateTimeObject(entry_tag,
                                                yearTag,
                                                monthTag,
                                                dayTag,
                                                hourTag,
                                                minuteTag,
                                                secondTag,
                                                millisecondTag)


        dateTime = getEarlierDateTime(earlistDateTimeObject, entry_dateTimeObject)

    return dateTime

# sorts out camera information and returns a camera object
def getCameraObject(exifData):
    # we want make, model, serial number, software
    cameraMake = 'NONE'
    cameraModel  = 'NONE'
    serialNumber = 'NONE'
    softwareName = 'NONE'

    for key,value in exifData.iteritems():
        # get serial number string i.e. '192029004068'
        if 'exif:serialnumber' in key.lower():
            serialNumber = str(exifData[key])
        # get make string i.e. 'Canon'
        if 'exif:make' in key.lower():
            cameraMake = str(exifData[key])
        # get model string i.e. 'Canon EOS 5D Mark III'
        if 'exif:model' in key.lower():
            cameraModel = str(exifData[key])
        # get software string i.e. 'Adobe Photoshop Lightroom 6.3 (Macintosh)''
        if 'exif:software' in key.lower():
            softwareName = str(exifData[key])

    # special case for iOS devices reporting software version
    if cameraMake.lower() == 'apple':
        softwareName = 'iOS %s' % softwareName

    camera = cameraObject(cameraMake, cameraModel, serialNumber, softwareName)

    return camera

# creates a mediaFileObject
def getMediaFileObject(file, creatorName):
    print 'builds mediaFileObject'
    print file

    if isValidMediaFileType(file)[0]:

        # process file
        exifTagsDict = JSONToDict(p.get_json(originalFilePath))

        # determine type, image or video
        fileType = isValidMediaFileType(file)[1]

        # get file extension
        extension = isValidMediaFileType(file)[2]

        # get dateTimeObject for file
        dateTime = getDateTimeObject(exifTagsDict)

        # get cameraObject for file
        camera = getCameraObject(exifTagsDact)

        # get creatorName for file
        creator = creatorName.lower()

        # init mediaFileObject
        mediaFile = mediaFileObject(fileType, extension, dateTime, camera, creator)
        return mediaFile

    else:
        print 'not a valid media type'


#------------------------------------------------------------------------------
#		pretty print tags and dictionary sources
#------------------------------------------------------------------------------

# print "most" exif tags, skips encoding tags
def prettyPrintTags(dataDictionary):

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

# print dateTime tags
def prettyPrintDateTimeTags(dataDictionary):

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

# # clean up camera information for file naming
# def cameraLabelCleaner(camera, userName):
#
#     cleanCameraString = ''
#
#     # special cases for known cameras
#     # adjustments for Apple cameras, (iPhones, iPads, etc)
#     if camera.make.upper() == 'APPLE':
#         cleanCameraString = camera.make + '.' + camera.model + '.' + userName
#
#     # adjustments for Canon cameras
#     elif camera.make.upper() == 'CANON':
#             # left pad all canon serial numbers with zeros to be 12 digits long
#             if camera.serial == 'NONE':
#                 tempSerialNumber = ''
#             else:
#                 tempSerialNumber = camera.serial
#
#             while len(tempSerialNumber) < 13:
#                 tempSerialNumber = '0' + tempSerialNumber
#
#             cleanCameraString = camera.model + '.' + userName + '.' + tempSerialNumber
#
#         # adjustments for Kodak cameras
#     elif camera.make.upper() == 'EASTMAN KODAK COMPANY':
#             cleanCameraString = camera.model
#
#         # adjustments for GoPro cameras
#     elif camera.make.upper() == 'GOPRO':
#             cleanCameraString = camera.make + '.' + camera.model + '.' + userName
#
#         # adjustments for Sony cameras
#     elif camera.make.upper() == 'SONY':
#             # sony camera models tend to have '-' in them, replace with '.'
#             tempModel = camera.model
#             tempModel = tempModel.replace('-', '.')
#
#             cleanCameraString = camera.make + '.' + tempModel + '.' + userName
#
#         # adjustments for Nikon cameras
#     elif camera.make.upper() == 'NIKON CORPORATION':
#             cleanCameraString = camera.model + '.' + userName
#
#     elif camera.make != 'NONE':
#         cleanCameraString = cleanCameraString + '.' + camera.make
#
#     elif camera.model != 'NONE':
#         cleanCameraString = cleanCameraString + '.' + camera.model
#
#     else:
#         # print 'camera make not was not an option...'
#         # camera.printInfo()
#         cleanCameraString = 'UNKNOWNCAMERA'
#
#
#     # remove anly leading '.'
#     while cleanCameraString[0] == '.':
#         cleanCameraString = cleanCameraString[1:]
#
#
#     return cleanCameraString


#------------------------------------------------------------------------------
#		file processing functions
#------------------------------------------------------------------------------

# main processing of media file, gets exif data, setups up destination directory and filename, copies file
def processMediaFile(mediaFile, userName, destinationDir, cameraMake, cameraModel):
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

    # get information from exif tags, format dateTime, and Camera class objects
    exifTagsDict = JSONToDict(p.get_json(originalFilePath))
    dateTimeStamp = getMediaDateTimeStamp(exifTagsDict)
    cameraInfo = getCameraInformation(exifTagsDict, cameraMake, cameraModel)

    # build file path for media file to be copied to
    correctedFilePath = getFilePath(destinationDir, dateTimeStamp, cameraInfo, userName.lower(), extension)

    # build file name for meida file to be copied as, appends '.copy' and a counter if it already exists
    destFile = makeCopy(originalFilePath, correctedFilePath)

    print '\tmoved\t%s' % originalFilePath
    print '\tto\t\t%s' % destFile

    return True

# builds a dictionary of all unique camera objects found, and a file sample to match
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
    # cameraInfo = getCameraInformation(exifTagsDict)
    cameraInfo = getCameraInformation(exifTagsDict, cameraMake, cameraModel)
    # cameraInfo.printInfo()

    return cameraInfo
