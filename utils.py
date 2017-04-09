#!/usr/bin/end python


import pyexifinfo
import json
import os
import shutil
from datetime import datetime
import logging
import subprocess
import getpass
import progressBar



#   special stuff to handle known non ascii cahracters, blame Sony! (not really)
import sys  # import sys package, if not already imported
reload(sys)
sys.setdefaultencoding('utf-8')

#------------------------------------------------------------------------------
#		classes
#------------------------------------------------------------------------------

class CameraObject:

    def __init__(self, make, model, serial, software):
        self.make = str(make).replace(' ','.')
        self.model = str(model).replace(' ','.')
        self.serial = serial
        self.software = str(software).split('(')[0].replace(' ', '.')

    def printInfo(self):
        print 'Camera Make:\t\t%s' % self.make
        print 'Camera Model:\t\t%s' % self.model
        print 'Serial Number:\t\t%s' % self.serial
        print 'Software:\t\t\t%s' % self.software

class DateTimeObject:

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
        print 'Tag:\t\t\t%s' % self.tag
        print 'Year:\t\t\t%s' % self.year
        print 'Month:\t\t\t%s' % self.month
        print 'Day:\t\t\t%s' % self.day
        print 'Hour:\t\t\t%s' % self.hour
        print 'Minute:\t\t\t%s' % self.minute
        print 'Second:\t\t\t%s' % self.second
        print 'Millisecond:\t\t%s' % self.millisecond

class MediaFileObject:

    def __init__(self, type, extension, dateTimeObject, cameraObject, creator):
        self.type = type
        self.extension = extension
        self.dateTime = dateTimeObject
        self.camera = cameraObject
        self.creator = creator

    def printInfo(self):
        print 'Type:\t\t\t%s' % (self.type)
        print 'Extension:\t\t%s' % (self.extension)
        print 'Creator:\t\t%s' % (self.creator)
        self.camera.printInfo()
        self.dateTime.printInfo()


#------------------------------------------------------------------------------
#       pretty printer functions
#------------------------------------------------------------------------------

#   print exif tags, skips encoding tags
def prettyPrintTags(exifInfo):

    exifDict = JSONToDict(pyexifinfo.get_json(exifInfo))
    prettyPrintDict(exifDict)

    return True

#   print dateTime tags
def prettyPrintDateTimeTags(exifInfo):
    dateTimeTagsDict = {}
    exifDict = JSONToDict(pyexifinfo.get_json(exifInfo))

    # select only dateTime tags
    sortedDict = sorted(exifDict.iteritems())
    # for tag, entry in sortedDict:
    for tag, entry in sorted(exifDict.iteritems()):
        # print tag.lower()
        if 'date' in tag.lower():
            dateTimeTagsDict[tag] = entry

    prettyPrintDict(dateTimeTagsDict)

    return True

#   print camera tags
def prettyPrintCameraTags(exifInfo):
    cameraTagsDict = {}
    exifDict = JSONToDict(pyexifinfo.get_json(exifInfo))

    #   select only make, model, serial, and software tags
    sortedDict = sorted(exifDict.iteritems())

    #   for tag, entry in sortedDict
    for tag, entry in sortedDict:
        #   only write selected tags we want
        if 'make' in tag.lower():
            cameraTagsDict[tag] = entry

        elif 'model' in tag.lower():
            cameraTagsDict[tag] = entry

        elif 'serial' in tag.lower():
            cameraTagsDict[tag] = entry

        elif 'software' in tag.lower():
            cameraTagsDict[tag] = entry

    prettyPrintDict(cameraTagsDict)

    return True

#   pretty print a dictionary in key value pairs, well spaced
def prettyPrintDict(inpitDictionary):
    longestKey = 0

    for key in inpitDictionary:
        if len(key) > longestKey:
            longestKey = len(key)

    sortedDict = sorted(inpitDictionary.iteritems())
    for key, value in sortedDict:
        spacesNeeded = longestKey - len(key) + 4
        spaces = ' ' * spacesNeeded
        print '%s%s%s' % (key, spaces, value)
        logging.info('%s%s%s', key, spaces, value)

    return True

#   uniform spacers
def spacer():
    print '\n'
    print '#' + '-'*79
    print '\n'

    logging.info('\n')
    logging.info('#' + '-'*79)
    logging.info('\n')
def bigSpacer():
    print '\n'
    print '#' + '!'*79
    print '#' + '!'*79
    print '\n'

    logging.info('\n')
    logging.info('#' + '!'*79)
    logging.info('#' + '!'*79)
    logging.info('\n')


#------------------------------------------------------------------------------
#		file relocation functions
#------------------------------------------------------------------------------

#   returns directory contents as a list
#   prunes only valid media file formats
def getDirectoryContents(dir):

    directory_contents = []

    for root, directories, files in os.walk(dir):
        for filename in files:
            # only add files that are a valid media file type
            if isValidMediaFileType(filename):
                filePath = os.path.join(root, filename)
                directory_contents.append(filePath)
            elif not isIgnorableSystemFile(filename):
                print '>>> POSSIBLE MEDIA FILE:\t%s/%s' % (root, filename)
                logging.info('>>> POSSIBLE MEDIA FILE:\t%s/%s', root, filename)

    return directory_contents

#   check if file is a known image or video format, returns boolean
def isValidMediaFileType(file):

    # get extension of file
    extensionToCheck = file.split('.')[-1].upper()

    # 'Valid' media file type extensions
    validVideoFileExtensions = ['MOV', 'MP4', 'MPG', 'M4V', '3G2', 'ASF', 'AVI']
    validImageFileExtensions = ['JPG', 'PNG', 'TIF', 'TIFF', 'CR2', 'BMP', 'GIF', 'DNG']

    if extensionToCheck in validVideoFileExtensions:
        return True
    elif extensionToCheck in validImageFileExtensions:
        return True
    else:
        return False

#   check if a file is a known ignorable file type, returns boolean
def isIgnorableSystemFile(file):
    # get extension of file
    extensionToCheck = file.split('.')[-1].upper()

    # 'Valid' media file type extensions
    ingnorableSystemFiles = ['INI', 'DS_STORE', 'DB', 'TEMP', 'INFO', 'PLIST', 'CTG', 'ATTR', 'TMP', 'WTC']

    if extensionToCheck in ingnorableSystemFiles:
        return True
    else:
        return False

#   convert json information gathered by exif tools into a dictionary
#   if file has no EXIF data, an empty dictionary is returned
def JSONToDict(data):
    if len(data) < 1:
        print '>>> this file has no exif data'
        logging.warning('>>> this file has no exif data')
        dataDict = {}
    else:
        # return a sorted dictionary of all exif tag, value pairs
        dataDict = dict(sorted(data[0].iteritems()))

    return dataDict

#   copy files and preserve metadata
#   handles copies by incrementing a copy counter
#   will overwrite when copies exceed 9999
#   returns absolute file path file was copied to
def safeCopy(sourceFile, destinationDirectoryName, destinationFileName):

    destinationAbsoluteFilePath = destinationDirectoryName + destinationFileName

    # increment counter when file already exists, helps elliminate file overwrite
    # fails out after 9999 copies are found, instead dumps all subsequent files to
    # counter '9999', WILL OVERWRITE
    def incrementCounter(sourceName):
        origCounter = sourceName.split('.')[-2]

        # get current counter value
        currentCounter = sourceName.split('.')[-2]

        # trim leading zeros
        while currentCounter[:1] == '0':
            currentCounter = currentCounter[1:]

        # format to integer and increment
        if int(currentCounter) < 9999:
            counter = int(currentCounter) + 1
        else:
            counter = 9999

        # format to string and left side zero pad counter
        newCounterString = str(counter)
        while len(newCounterString) < 4:
            newCounterString = '0' + newCounterString

        # add prefix and suffix '.', to help replace function better find only
        # counter portion of the file name string
        origCounterString = '.' + origCounter + '.'
        newCounterString = '.' + newCounterString + '.'

        incrementendFileName = sourceName.replace(origCounterString, newCounterString)

        return incrementendFileName

    # check if destination directory exists, if not create it
    if not os.path.exists(destinationDirectoryName):
        os.makedirs(destinationDirectoryName)

    # check if file exists
    while os.path.isfile(destinationAbsoluteFilePath):
        # print 'file exists, attempting to increment counter...'
        # this file exists! increment the counter
        destinationAbsoluteFilePath = incrementCounter(destinationAbsoluteFilePath)

        # when the counter reaches 9999, break out of while loop!
        if destinationAbsoluteFilePath.split('.')[-2] == '9999':
            break

    shutil.copy2(sourceFile, str(destinationAbsoluteFilePath))

    return str(destinationAbsoluteFilePath)


#------------------------------------------------------------------------------
#		DateTimeObject functions
#------------------------------------------------------------------------------

#   compare two DateTimeObjects and return earlier one
def getEarlierDateTime(tagA, tagB):

    # converts DateTimeObject pieces into an integer for comparison
    tagA_INT = int(tagA.year + tagA.month + tagA.day + tagA.hour + tagA.minute + tagA.second + tagA.millisecond)
    tagB_INT = int(tagB.year + tagB.month + tagB.day + tagB.hour + tagB.minute + tagB.second + tagB.millisecond)

    # return the larger tag
    if tagA_INT <= tagB_INT:
        return tagA
    else:
        return tagB

#       gets earlist date time tag, excludes dates in photoshop or camera profiles
#   returns the earliest DateTimeObject, filters out dates prior to 1975
def getDateTimeObject(exifData):

    # default values
    earliestDateTimeObject = DateTimeObject('NONE', '9999', '99', '99', '99', '99', '99', '999')

    # collect all date related keys and values
    dateTimeTags = []

    # select dateTime (key, value) pairs as a subset
    for key, value in exifData.iteritems():
        if 'date' in key.lower():
            # exclude some odd tag keys
                # excludes ICC* keys
                # excludes FlashPix* keys
                # excludes values that dont have ':' character
            if 'icc' not in key.lower() and not 'flashpix' in key.lower() and ":" in value:
                dateTimeTags.append([key, value])

    # go through dateTime tags to determine the earliest one
    for entry in dateTimeTags:

        entry_tag = str(entry[0])
        entry_dateTimeStamp = entry[1]

        #-----------------------------------------------------------------------
        #   Clean up
        #-----------------------------------------------------------------------

        # some date tags are not formatted dates... super annoying
        try:
            entry_dateTimeStamp.split(':')[0]
        except:
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

        #-----------------------------------------------------------------------
        #   get dateStamp
        #   [dateStamp_year, dateStamp_month, dateStamp_day]
        #-----------------------------------------------------------------------

        # split apart dateStamp, defaults to '9999:99:99'
        try:
            entry_dateStamp = entry_dateTimeStamp.split(' ')[0]
        except:
            entry_dateStamp = entry_dateTimeStamp

        # note that dates are either formatted 'YYYY:MM:DD' or 'MM.DD.YYYY'
        entry_dateStamp = entry_dateStamp.replace('.', ':')

        # if formatted 'YYYY:MM:DD'
        if len(entry_dateStamp.split(':')[0]) == 2:
            dateStamp_year = entry_dateStamp.split(':')[2]
            dateStamp_month = entry_dateStamp.split(':')[0]
            dateStamp_day = entry_dateStamp.split(':')[1]
        # if formatted 'YYYY:MM:DD'
        else:
            dateStamp_year = entry_dateStamp.split(':')[0]
            dateStamp_month = entry_dateStamp.split(':')[1]
            dateStamp_day = entry_dateStamp.split(':')[2]

        # if year is before 1975, we dont want it, set year to 9999 to make sure
        # it is not the lowest year
        # this is to remove false low years that some software
        # defaults to writing out the date at the epoch
        if int(dateStamp_year) < 1975:
            dateStamp_year = '9999'

        #-----------------------------------------------------------------------
        #   get timeStamp
        #   [timeStamp_hour, timeStamp_minute, timeStamp_second, timeStamp_millisecond]
        #-----------------------------------------------------------------------

        # split apart timeStamp, defaults to '23:59:59.999'
        try:
            entry_timeStamp = entry_dateTimeStamp.split(' ')[1]

            # sometimes time stamps have letters appened to the end of the second, lets remove those
            while entry_timeStamp[len(entry_timeStamp)-1].isalpha():
                entry_timeStamp = entry_timeStamp[:-1]
        except:
            entry_timeStamp = '23:59:59.999'

        # break timeStamp into pieces
        timeStamp_hour = entry_timeStamp.split(':')[0]
        timeStamp_minute = entry_timeStamp.split(':')[1]

        try:
            timeStamp_second = entry_timeStamp.split(':')[2]
        except:
            timeStamp_second = '99'

        # try splitting second into seconds and milliseconds
        try:

            timeStamp_second = timeStamp_second.split('.')[0]
            timeStamp_millisecond = timeStamp_second.split('.')[1]

            # format millisecondStamp to be a fixed length of 3 digits
            if len(timeStamp_millisecond) > 3:
                timeStamp_millisecond = timeStamp_millisecond[:4]
            # zero padded from the left if needed
            while len(timeStamp_millisecond) < 3:
                timeStamp_millisecond = '0' + timeStamp_millisecond

        except:
            timeStamp_millisecond = '999'


        #-----------------------------------------------------------------------
        #   buildDateTimeObject
        #-----------------------------------------------------------------------

        # create DateTimeObject
        entry_DateTimeObject = DateTimeObject(entry_tag,
                                                dateStamp_year,
                                                dateStamp_month,
                                                dateStamp_day,
                                                timeStamp_hour,
                                                timeStamp_minute,
                                                timeStamp_second,
                                                timeStamp_millisecond)

        # entry_DateTimeObject.printInfo()

        # compare DateTimeObjects
        earliestDateTimeObject = getEarlierDateTime(earliestDateTimeObject, entry_DateTimeObject)
        # earliestDateTimeObject.printInfo()

    return earliestDateTimeObject


#------------------------------------------------------------------------------
#		CameraObject Functions
#------------------------------------------------------------------------------

#   clean up camera information for file naming
def cameraObjectCleaner(cameraObject):

    # cameraObject.printInfo()

    # special cases for known cameras
    # adjustments for Apple cameras, (iPhones, iPads, etc)
    if cameraObject.make.upper() == 'APPLE':
        cameraObject.make = 'Apple'
        cameraObject.model = cameraObject.model
        cameraObject.serial = cameraObject.serial
        cameraObject.software = 'iOS.%s' % cameraObject.software
        # cameraObject.printInfo()

    #   adjustements for casio cameras
    if cameraObject.make.upper() == 'CASIO.COMPUTER.CO.,LTD.':
        cameraObject.make = 'Casio'
        cameraObject.model = 'Casio.%s' % cameraObject.model
        cameraObject.serial = cameraObject.serial
        cameraObject.software = cameraObject.software
        # cameraObject.printInfo()

    #   adjustements for Canon cameras
    if cameraObject.make.upper() == 'CANON':
        cameraObject.make = cameraObject.make
        cameraObject.model = cameraObject.model[6:]
        cameraObject.serial = cameraObject.serial
        cameraObject.software = cameraObject.software
        # cameraObject.printInfo()

    return cameraObject

    # # adjustments for Canon cameras
    # elif camera.make.upper() == 'CANON':
    #         # left pad all canon serial numbers with zeros to be 12 digits long
    #         if camera.serial == 'NONE':
    #             tempSerialNumber = ''
    #         else:
    #             tempSerialNumber = camera.serial
    #
    #         while len(tempSerialNumber) < 13:
    #             tempSerialNumber = '0' + tempSerialNumber
    #
    #         cleanCameraString = camera.model + '.' + userName + '.' + tempSerialNumber




    #
    # # adjustments for Kodak cameras
    # elif camera.make.upper() == 'EASTMAN KODAK COMPANY':
    #         cleanCameraString = camera.model
    #
    # # adjustments for GoPro cameras
    # elif camera.make.upper() == 'GOPRO':
    #         cleanCameraString = camera.make + '.' + camera.model + '.' + userName
    #
    # # adjustments for Sony cameras
    # elif camera.make.upper() == 'SONY':
    #         # sony camera models tend to have '-' in them, replace with '.'
    #         tempModel = camera.model
    #         tempModel = tempModel.replace('-', '.')
    #
    #         cleanCameraString = camera.make + '.' + tempModel + '.' + userName
    #
    # # adjustments for Nikon cameras
    # elif camera.make.upper() == 'NIKON CORPORATION':
    #         cleanCameraString = camera.model + '.' + userName
    #
    # elif camera.make != 'NONE':
    #     cleanCameraString = cleanCameraString + '.' + camera.make
    #
    # elif camera.model != 'NONE':
    #     cleanCameraString = cleanCameraString + '.' + camera.model
    #
    # else:
    #     # print 'camera make not was not an option...'
    #     # camera.printInfo()
    #     cleanCameraString = 'UNKNOWNCAMERA'
    #
    #
    # # remove anly leading '.'
    # while cleanCameraString[0] == '.':
    #     cleanCameraString = cleanCameraString[1:]


    # return cameraObject








#   sorts out camera information and returns a camera object
def getCameraObject(exifData):
    # we want make, model, serial number, software
    cameraMake = 'NONE'
    cameraModel  = 'NONE'
    cameraSerial = 'NONE'
    softwareName = 'NONE'

    # # update CameraObject pieces if they can be found
    # for key,value in exifData.iteritems():
    #
    #     # print '%s\t\t%s' % (key, value)
    #
    #     # get serial number string i.e. '192029004068'
    #     if 'exif:serialnumber' in key.lower():
    #         cameraSerial = str(exifData[key])
    #
    #     # # get make string i.e. 'Canon'
    #     # # looks for user generate xmp exif tag if an originl from camera can not be found
    #     # elif 'exif:make' in key.lower():
    #     #     cameraMake = str(exifData[key])
    #     # elif 'quicktime:make' in key.lower():
    #     #     cameraMake = str(exifData[key])
    #
    #
    #     # # get model string i.e. 'Canon EOS 5D Mark III'
    #     # # looks for user generate xmp exif tag if an originl from camera can not be found
    #     # elif 'exif:model' in key.lower():
    #     #     cameraModel = str(exifData[key])
    #     # elif 'quicktime:model' in key.lower():
    #     #     cameraModel = str(exifData[key])
    #
    #     # # get software string i.e. 'Adobe Photoshop Lightroom 6.3 (Macintosh)''
    #     # elif 'exif:software' in key.lower():
    #     #     softwareName = str(exifData[key])
    #     # elif 'quicktime:software' in key.lower():
    #     #     softwareName = str(exifData[key])
    #
    #     #
    #     # #   Manually writted tags get the 'xmp' prefix, these should override any other tags we find in the file
    #     # elif 'xmp:make' in key.lower():
    #     #     print 'found xmp:make! %s' % str(exifData[key])
    #     #     cameraMake = str(exifData[key])
    #     # elif 'xmp:model' in key.lower():
    #     #     print 'found xmp:model! %s' % str(exifData[key])
    #     #     cameraModel = str(exifData[key])
    #

    #   get cameraMake metadata
    try:
        cameraMake = exifData['XMP:Make']
    except:
        try:
            cameraMake = exifData['EXIF:Make']
        except:
            try:
                cameraMake = exifData['QuickTime:Make']
            except:
                pass

    #   get cameraModel metadata
    try:
        cameraModel = exifData['XMP:Model']
    except:
        try:
            cameraModel = exifData['EXIF:Model']
        except:
            try:
                cameraModel = exifData['QuickTime:Model']
            except:
                pass

    #   get software metadata
    try:
        softwareName = exifData['EXIF:Software']
    except:
        pass

    #   get camera serial Number
    try:
        cameraSerial = exifData['EXIF:SerialNumber']
    except:
        pass


    # build CameraObject
    cameraObject = CameraObject(cameraMake, cameraModel, cameraSerial, softwareName)
    cameraObject = cameraObjectCleaner(cameraObject)

    return cameraObject


#------------------------------------------------------------------------------
#		MediaFileObject Functions
#------------------------------------------------------------------------------

#   uses information from exifData to create a MediaFileObject if possible
def getMediaFileObject(file, creatorName=getpass.getuser()):
    # print 'building MediaFileObject from %s' % file

    # if the file is a valid media file type, else skip all this
    if isValidMediaFileType(file):

        # get exifTags into a dictionary
        exifTagsDict = JSONToDict(pyexifinfo.get_json(file))
        # prettyPrintDict(exifTagsDict)

        # Get file type information
        fileTypeInfo = getMediaFileType(exifTagsDict)
        mediaType = fileTypeInfo[0]
        extension = fileTypeInfo[1]

        # get DateTimeObject for file
        dateTimeObject = getDateTimeObject(exifTagsDict)

        # get CameraObject for file
        cameraObject = getCameraObject(exifTagsDict)

        # get creatorName for file
        creator = creatorName.lower()

        # init MediaFileObject
        mediaFileObject = MediaFileObject(mediaType,
                                            extension,
                                            dateTimeObject,
                                            cameraObject,
                                            creator)

        return mediaFileObject

    else:
        print '>>> could not create MediaFileObject from %s, not a valid media file type' % file
        logging.warning('>>> could not create MediaFileObject from %s, not a valid media file type', file)
        return False


#   read exifTags for media file type info
#   returns a list of mediaType, fileType, fileExtensions
#   example (video, MOV, MOV) -> movie file
#   example (image, JPEG, JPG) -> image file
def getMediaFileType(exifData):

    # get media type from 'File:MIMEType' value, (video or image)
    mediaType = exifData['File:MIMEType'].split('/')[0].upper()

    # get file extension from 'File:FileTypeExtension' value
    fileExtension = exifData['File:FileTypeExtension'].upper()

    return (mediaType, fileExtension)


#------------------------------------------------------------------------------
#		file backup functions
#------------------------------------------------------------------------------

#   creates a backup of files if and only if they do not already exist in the destinationDir structure
def backupMediaFile(sourceDir, inputFile, destinationDir):
    startTime = datetime.now()

    print ">>> processing '%s'" % inputFile
    logging.info(">>> processing '%s'",inputFile)


    #   sourceDir           /Volumes/GreenTree2000/photoArchive/
    #   inputFile          /Volumes/GreenTree2000/photoArchive/images/2017/2017.02/20170210.034208999.samgutentag.0001.CR2
    #   destinationDir      /Volumes/destinationDir/photoArchive/

    # destinationFileFullPath
    #   /Volumes/destinationDir/photoArchive/images/2017/2017.02/20170210.034208999.samgutentag.0001.CR2

    backupFileAbsolutePath = inputFile.replace(sourceDir, destinationDir, 1)

    fullDestinationDir = backupFileAbsolutePath[0:backupFileAbsolutePath.rfind('/')]

    print backupFileAbsolutePath

    # check if destination directory exists, if not create it
    if not os.path.exists(fullDestinationDir):
        os.makedirs(fullDestinationDir)

    # check if file exists
    if os.path.isfile(backupFileAbsolutePath):
        logging.info('file has already been backed up, skipping')
        print 'file has already been backed up, skipping'

    else:
        logging.info('backing up %s to %s', inputFile, backupFileAbsolutePath)
        print 'backing up %s to %s' % (inputFile, backupFileAbsolutePath)
        shutil.copy2(inputFile, backupFileAbsolutePath)


    endTime = datetime.now()
    elapsedTime = endTime - startTime

    logging.info('Backed Up\t%s\nto\t\t\t%s', inputFile, backupFileAbsolutePath)
    logging.info('\t[%s]', elapsedTime)

    return (backupFileAbsolutePath, elapsedTime)


#------------------------------------------------------------------------------
#		Command Line Tool Wrappers
#------------------------------------------------------------------------------

#   takes a list of arguments and a list of files to pass the against exiftools
def setExifTags(argsList, fileList):

    fileCount = len(fileList)

    iterationCounter = 1
    # progress_prefix = '\n%s of %s' % (iterationCounter, fileCount)
    logging.info('\n%s of %s', iterationCounter, fileCount)

    # progressBar.print_progress(iterationCounter, fileCount, prefix=progress_prefix, decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-')
    progressBar.print_progress(iterationCounter, fileCount, decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-')

    #   append all arguments to 'exiftools' command line tool
    executeArgs = ['exiftool'] + argsList

    #   append all files to run arguments against
    for item in fileList:

        #   print and log action
        print "updating exif tags for '%s'" % item
        logging.info("updating exif tags for '%s'", item)


        executeArgs.append(str(item))
        # progressBar.print_progress(iterationCounter, fileCount, prefix=progress_prefix, decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-')
        progressBar.print_progress(iterationCounter, fileCount, decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-')
        iterationCounter +=1

    spacer()
    print 'Running exiftools...'
    logging.info('Running exiftools...')
    subprocess.call(executeArgs)


#   writes all exiftags from a srouce media file to the target media file
def matchExifTags(sourceFile, targetFile):

    #   append all arguments to 'exiftools' command line tool
    executeArgs = ['exiftool -tagsFromFile'] + [sourceFile] + [targetFile]

    print 'Running exiftools...'
    logging.info('Running exiftools...')
    subprocess.call(executeArgs)
