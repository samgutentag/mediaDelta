#!/usr/bin/end python

import pyexifinfo as p
import argparse
import json
import os

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

# printing a spacer to console
def spacer():
    print '\n'
    print '#' + '-'*79
    print '\n'
def  bigSpacer():
    print '\n'
    print '#' + '!'*124
    print '#' + '!'*124
    print '\n'

# checks that a given file exists, and opens it
def openMediaFile(parser, arg):
    if not os.path.exists(arg):
        parser.error('The file %s does not exist' % arg)
    else:
        return open(arg, 'rb')

# def checks that a given directory exists
def openMediaDirectory(parser, arg):
    if not os.path.exists(arg):
        parser.error('The directory %s does not exist' % arg)
    else:
        return arg



def JSONToDict(data):
    print '>>> creating exifDict from json data...'

    if len(data) < 1:
        print '>>> this file has no exif data'
        return
    else:
        # dataDict = dict(sorted(data[0].iteritems()))
        dataDict = dict(sorted(data[0].iteritems()))
        print '>>> done!'
        return dataDict

# construct file path and name of 'correctly' named file
def getFilePath(destinationDir, dateTimeStamp, cameraInfo, userName, extension):
    fileName = ''
    filePath = ''

    # formatting : photos/<ext>/fullRes/YYYY.MM.DD/<cameraModel>.<artist>.<cameraSerial>/
    # filePath = '%s/%s/%s/%s/' % (destinationDir, dateTimeStamp.year,
    #                                              dateTimeStamp.month,
    #                                              dateTimeStamp.day)

    filePath = '/photos/%s/fullRes/%s.%s.%s/%s.%s.%s/' % (extension,
                                                        dateTimeStamp.year,
                                                        dateTimeStamp.month,
                                                        dateTimeStamp.day,
                                                        cameraInfo.model,
                                                        userName,
                                                        cameraInfo.serial)

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
    # fileName = '%s_%s%s' % (dateTimeStamp.toString(), userName, cameraName)
    fileName = '%s%s%s_%s%s%s.%s.%s' % (dateTimeStamp.year,
                                        dateTimeStamp.month,
                                        dateTimeStamp.day,
                                        dateTimeStamp.hour,
                                        dateTimeStamp.minute,
                                        dateTimeStamp.second,
                                        dateTimeStamp.millisecond,
                                        extension)


    return filePath + fileName


#------------------------------------------------------------------------------
#		file relocation functions
#------------------------------------------------------------------------------

# gets contents of a directory
def getDirectoryContents(dir):
    print ">>> getting contents of directory '%s'" % dir

    directory_contents = []

    for root, directories, files in os.walk(dir):
        for filename in files:
            filePath = os.path.join(root, filename)
            directory_contents.append(filePath)
    #
    #
    # for item in directory_contents:
    #     print item

    return directory_contents



#------------------------------------------------------------------------------
#		main exif tag formatting functions
#------------------------------------------------------------------------------

# compare two mediaDateTimeObjects and return earlier one
def getEarlierDateTime(tagA, tagB):

    # convert tag parts to an int from a concatenated string of the parts
    tagAINT = int(tagA.year + tagA.month + tagA.day + tagA.hour + tagA.minute + tagA.second + tagA.millisecond)
    tagBINT = int(tagB.year + tagB.month + tagB.day + tagB.hour + tagB.minute + tagB.second + tagB.millisecond)

    if tagAINT <= tagBINT:
        return tagA
    else:
        return tagB

# gets earlist date time tag, excludes dates in photoshop or camera profiles
# returns a list of (dateTimeTag, dateTimeValue)
def getMediaDateTimeStamp(data):
    print '>>> getting earliest media time stamp...'

    # entryInfo = mediaDateTimeObject(tag, year, month, day, hour, minute, second, millisecond)
    earlyDateTimeInfo = mediaDateTimeObject('NONE', '9999', '99', '99', '99', '99', '99', '999')

    # collect all date related keys and values
    dateTimeTags = []

    # select dateTime key  value pairs as a subset
    for key, value in data.iteritems():
        if 'date' in key.lower():
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

        # remove timezone adjustment if it exists
        try:
            dateTimeStamp = dateTimeStamp.split('-')[0]
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

        # format millisecondStamp to be a fixed length
        if len(entryInfo.millisecond) > 3:
            entryInfo.millisecond = entryInfo.millisecond[:4]

        while len(entryInfo.millisecond) < 3:
            entryInfo.millisecond = '0' + entryInfo.millisecond

        # entryInfo.printInfo()

        earlyDateTimeInfo = getEarlierDateTime(earlyDateTimeInfo, entryInfo)

    print '>>> done!'
    return earlyDateTimeInfo

# gets camera and or software device information
# returns a list of (cameraMake, cameraModel, serialNumber, softwareName)
# defaults to 'NONE' if a piece of information can not be found
def getCameraModel(data):
    print '>>> getting camera info...'

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

    print '>>> done!'

    return cameraInfo

# print tags
def prettyPrintTags(dataDictionary):
    # print dataDictionary
    print '>>> pretty printing EXIF tags'
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

    print '>>> done!'

# print dateTime tags
def prettyPrintDateTimeTags(dataDictionary):
    # print dataDictionary
    print '>>> pretty printing EXIF tags'
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

    print '>>> done!'


#------------------------------------------------------------------------------
#		file processing functions
#------------------------------------------------------------------------------

def processMediaFile(mediaFile, userName):
    # originalFilePath = str(mediaFile).split("'")[1]
    # when a single file is passed, the file name needs to be trimmed
    try:
        originalFilePath = str(mediaFile).split("'")[1]
    # when a file is passed as part of a ridrectory, it does not need to be trimmed
    except:
        originalFilePath = mediaFile

    print ">>> processing '%s'" % originalFilePath
    extension = str(originalFilePath.split('.')[-1])

    # ignore dot files i.e. '.DS_Store'
    if originalFilePath.split('.')[0].endswith('/'):
        print 'ignoring %s' % originalFilePath
        return 'IGNORE'



    newFileName = ''
    newFilePath = ''

    # spacer()
    exifTagsDict = JSONToDict(p.get_json(originalFilePath))

    # spacer()
    dateTimeStamp = getMediaDateTimeStamp(exifTagsDict)
    # dateTimeStamp.printInfo()

    # spacer()
    cameraInfo = getCameraModel(exifTagsDict)
    # cameraInfo.printInfo()

    # spacer()
    # prettyPrintTags(exifTagsDict)

    # spacer()
    # prettyPrintDateTimeTags(exifTagsDict)

    # spacer()
    destinationDir = '/DESTINATION_DIRECTORY'
    correctedFilePath = getFilePath(destinationDir, dateTimeStamp, cameraInfo, userName.lower(), extension)

    print '\t\tmoving\t%s' % originalFilePath
    print '\t\tto\t\t%s' % correctedFilePath


    print '>>> done!'
    return newFileName


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

    args = vars(parser.parse_args())

    print args
    spacer()

    # attempt to process a file if only one is given
    # keep this next line for testing, forces the loop, instead of just trying it...
    # processMediaFile(args['mediaFile'], args['artistName'])

    if args['mediaFile']:
        try:
            processMediaFile(args['mediaFile'], args['artistName'])
        except:
            print '>>> no files to process... all done!'
    elif args['mediaDirectory']:


        # process a directory of files
        filesToProcess = getDirectoryContents(args['mediaDirectory'])

        for file in filesToProcess:
            bigSpacer()
            # processMediaFile(file, args['artistName'])
            try:
                processMediaFile(file, args['artistName'])
            except:
                print 'unable to process %s' % file

    spacer()

    print 'ALL DONE!'

    spacer()


if __name__ == '__main__':
    main()
