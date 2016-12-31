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
        return (True, 'image')
    elif extensionToCheck in validImageFileExtensions:
        return (True, 'video')
    else:
        return (False, 'ignore')

# construct file path and name of 'correctly' named file
def getFilePath(destinationDir, mediaFile, event):
    fileName = ''
    dirName = ''

    # clean destinationDir to not include tail slashes
    while destinationDir.endswith('/'):
        destinationDir = destinationDir[:-1]

    # cleanCameraString = cameraLabelCleaner(cameraInfo, userName)
    # filePath = '%s/%s/%s.%s.%s/%s/' % (destinationDir,
    #                                     extension.upper(),
    #                                     dateTimeStamp.year,
    #                                     dateTimeStamp.month,
    #                                     dateTimeStamp.day,
    #                                     cleanCameraString)


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



    # # camera model may not be known,
    # if cameraInfo.model == 'NONE':
    #     # if it is not, try software,
    #     if cameraInfo.software == 'NONE':
    #         cameraName = ''
    #     # if that is not known, leave blank
    #     else:
    #         cameraName = '_' + cameraInfo.software
    # else:
    #     cameraName = '_' + cameraInfo.model

    # formatting : YYYYMMDD_HHmmSS.sss.<ext>
    # fileName = '%s%s%s_%s%s%s.%s.%s' % (dateTimeStamp.year,
    #                                     dateTimeStamp.month,
    #                                     dateTimeStamp.day,
    #                                     dateTimeStamp.hour,
    #                                     dateTimeStamp.minute,
    #                                     dateTimeStamp.second,
    #                                     dateTimeStamp.millisecond,
    #                                     extension)

    #  format:  'YYYYMMDD.HHMMSSsss.<eventName>.<creator>.<count(4 digits)>.<extension>'
    #  example: '20161225.1200000.christmas.samgutentag.0001.CR2'
    #  example: '20161127.1830500.thanksgiving.samgutentag.0003.CR2'
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


    # def make_str(counter):
    #     # trim leading zeros
    #
    #     try:
    #         counter_temp = counter.split('0')[-1]
    #         counterTemp = int(counter_temp) + 1
    #     except:
    #         counterTemp = int(counter) + 1
    #
    #     # format to 3 digits
    #     while len(str(counterTemp)) < 3:
    #         counterTemp = '0' + str(counterTemp)
    #
    #     return str(counterTemp)

    # destinationFileName = destinationFile.split('/')[-1]
    # destinationFileDirectory = destinationFile[:-len(destinationFileName)]
    #
    # # check that destination directory exists, else create it:
    # if not os.path.exists(destinationFileDirectory):
    #     os.makedirs(destinationFileDirectory)

    # # check if file exists, do not copy if it does
    # if os.path.isfile(destinationFile):
    #     print 'file already exists... trying to make another copy...'
    #
    #     destinationFile_adjusted = destinationFile
    #
    #     counter = 0
    #     destinationFile_adjusted = destinationFile_adjusted + '.copy' + make_str(counter)
    #
    #     while os.path.isfile(destinationFile_adjusted):
    #         destinationFile_adjusted = destinationFile_adjusted[:-3] + make_str(counter)
    #         # print destinationFile_adjusted
    #         counter += 1
    #
    #     # copy file
    #     shutil.copy2(sourceFile, destinationFile_adjusted)
    #
    #     return destinationFile_adjusted
    #
    #
    # else:
    #     # print 'would have been copied'
    #     shutil.copy2(sourceFile, destinationFile)
    #     return destinationFile


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
# returns a list of (dateTimeTag, dateTimeValue)
def getMediaDateTimeStamp(data):

    # entryInfo = dateTimeObject(tag, year, month, day, hour, minute, second, millisecond)
    earlyDateTimeInfo = dateTimeObject('NONE', '9999', '99', '99', '99', '99', '99', '999')

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
        entryInfo = dateTimeObject('NONE', '9999', '99', '99', '99', '99', '99', '999')

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

    return earlyDateTimeInfo

# gets camera and or software device information
# returns a list of (cameraMake, cameraModel, serialNumber, softwareName)
# defaults to 'NONE' if a piece of information can not be found
def getCameraInformation(data, cameraMake = 'NONE', cameraModel = 'NONE'):
    # we want make, model, serial number, software
    if not cameraMake:
        cameraMake = 'NONE'
    if not cameraModel:
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

    return cameraInfo




def getMediaFileObject(file):
    print 'builds mediaFileObject'
    print file

    # determine type, image or video
    mediaFileObject.type = isValidMediaFileType(file)[1]

    # get file extension
    mediaFileObject.extension = extension


    mediaFileObject.dateTime = dateTime


    mediaFileObject.camera = camera


    mediaFileObject.creator = creator



    return mediaFileObject






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

# clean up camera information for file naming
def cameraLabelCleaner(camera, userName):

    cleanCameraString = ''

    # special cases for known cameras
    # adjustments for Apple cameras, (iPhones, iPads, etc)
    if camera.make.upper() == 'APPLE':
        cleanCameraString = camera.make + '.' + camera.model + '.' + userName

    # adjustments for Canon cameras
    elif camera.make.upper() == 'CANON':
            # left pad all canon serial numbers with zeros to be 12 digits long
            if camera.serial == 'NONE':
                tempSerialNumber = ''
            else:
                tempSerialNumber = camera.serial

            while len(tempSerialNumber) < 13:
                tempSerialNumber = '0' + tempSerialNumber

            cleanCameraString = camera.model + '.' + userName + '.' + tempSerialNumber

        # adjustments for Kodak cameras
    elif camera.make.upper() == 'EASTMAN KODAK COMPANY':
            cleanCameraString = camera.model

        # adjustments for GoPro cameras
    elif camera.make.upper() == 'GOPRO':
            cleanCameraString = camera.make + '.' + camera.model + '.' + userName

        # adjustments for Sony cameras
    elif camera.make.upper() == 'SONY':
            # sony camera models tend to have '-' in them, replace with '.'
            tempModel = camera.model
            tempModel = tempModel.replace('-', '.')

            cleanCameraString = camera.make + '.' + tempModel + '.' + userName

        # adjustments for Nikon cameras
    elif camera.make.upper() == 'NIKON CORPORATION':
            cleanCameraString = camera.model + '.' + userName

    elif camera.make != 'NONE':
        cleanCameraString = cleanCameraString + '.' + camera.make

    elif camera.model != 'NONE':
        cleanCameraString = cleanCameraString + '.' + camera.model

    else:
        # print 'camera make not was not an option...'
        # camera.printInfo()
        cleanCameraString = 'UNKNOWNCAMERA'


    # remove anly leading '.'
    while cleanCameraString[0] == '.':
        cleanCameraString = cleanCameraString[1:]


    return cleanCameraString


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
