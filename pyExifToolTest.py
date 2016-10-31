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
        self.model = str(model).replace(' ','')
        self.serial = serial
        self.software = str(software).split('(')[0]

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

# def openMediaFile
def openMediaFile(parser, arg):
    if not os.path.exists(arg):
        parser.error('The file %s does not exist' % arg)
    else:
        return open(arg, 'rb')

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

# gets contents of a directory
def getDirectoryContents(dir):
    print ">>> getting contents of directory '%s'" % dir

    for item in dir:
        # if item is a file
        if os.path.isfile(item):
            print '%s is a file!' % item

        # if item is a directory
        elif os.path.isdir(item):
            print '%s is a directory!' % item
            getDirectoryContents(item)

        else:
            print 'not sure what happened...'

def getEarlierDateTime(tagA, tagB):

    print 'TAG:\t\t\t%s\t%s' % (tagA.tag, tagB.tag)
    print 'YEAR:\t\t\t%s\t%s' % (tagA.year, tagB.year)
    print 'MONTH:\t\t\t%s\t\t%s' % (tagA.month, tagB.month)
    print 'DAY:\t\t\t%s\t\t%s' % (tagA.day, tagB.day)
    print 'HOUR:\t\t\t%s\t\t%s' % (tagA.hour, tagB.hour)
    print 'MINUTE:\t\t\t%s\t\t%s' % (tagA.minute, tagB.minute)
    print 'SECOND:\t\t\t%s\t\t%s' % (tagA.second, tagB.second)
    print 'MILLISECOND:\t%s\t\t%s' % (tagA.millisecond, tagB.millisecond)

    print '-' * 20



    return tagB





#------------------------------------------------------------------------------
#		main exif tag formatting functions
#------------------------------------------------------------------------------


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

    # cameraInfo.printInfo()

    print '>>> done!'

    return cameraInfo

# gets earlist date time tag, excludes dates in photoshop or camera profiles
# returns a list of (dateTimeTag, dateTimeValue)
def getMediaDateTimeStamp(data):
    print '>>> getting earliest media time stamp...'

    # # default date time information
    tag = 'NONE'
    year = '9999'
    month = '99'
    day = '99'
    hour = '99'
    minute = '99'
    second = '99'
    millisecond = '999'


    entryInfo = mediaDateTimeObject(tag, year, month, day, hour, minute, second, millisecond)
    earlyDateTimeInfo = mediaDateTimeObject(tag, year, month, day, hour, minute, second, millisecond)

    # collect all date related keys and values
    dateTimeTags = []

    for key, value in data.iteritems():
        if 'date' in key.lower():
            # print 'found \'%s\' tag...'
            if 'icc' not in key.lower():
                dateTimeTags.append([key, value])

    for entry in dateTimeTags:

        entryInfo.tag = str(entry[0])
        dateTimeStamp = entry[1]

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
            timeStamp = '23:59:99'

        # update values for each
        entryInfo.year = dateStamp.split(':')[0]
        entryInfo.month = dateStamp.split(':')[1]
        entryInfo.day = dateStamp.split(':')[2]
        entryInfo.hour = timeStamp.split(':')[0]
        entryInfo.minute = timeStamp.split(':')[1]
        entryInfo.second = timeStamp.split(':')[2]

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

        # earlyDateTimeInfo = getEarlierDateTime(earlyDateTimeInfo, entryInfo)
        early



    print'\n\n'
    print 'EARLIEST TAG IS: '
    earlyDateTimeInfo.printInfo()



    print '>>> done!!!'
    # # return earlyDateTimeInfo
    return True








def getCameraOperator(data, name):
    print '>>> getting camera operator/photographer information...'

    print '>>> done!'

#------------------------------------------------------------------------------
#		file processing functions
#------------------------------------------------------------------------------
def processMediaFile(mediaFile):
    fileName = str(mediaFile).split("'")[1]
    print ">>> processing '%s'" % fileName
    extension = str(fileName.split('.')[-1])

    newFileName = ''
    newFilePath = ''

    # spacer()
    exifTagsDict = JSONToDict(p.get_json(fileName))

    spacer()
    dateTimeStamp = getMediaDateTimeStamp(exifTagsDict)
    print dateTimeStamp

    spacer()
    cameraInfo = getCameraModel(exifTagsDict)


    # spacer()
    # prettyPrintTags(exifTagsDict)

    # all done!
    # spacer()

    year = dateTimeStamp[0]
    month = dateTimeStamp[1]
    day = dateTimeStamp[2]
    hour = dateTimeStamp[3]
    minute = dateTimeStamp[4]
    second = dateTimeStamp[5]
    millisecond = dateTimeStamp[6]

    newFilePath = '/dest/%s/%s/%s/' % (year, month, day)
    newFileName_Date = '%s%s%s%s%s%s%s' % (year, month, day, hour, minute, second, millisecond)
    newFileName_User = 'samgutentag'


    newFileName_Camera = '%s%s' % (cameraInfo.model, cameraInfo.serial)

    newFileName = '%s_%s_%s' % (newFileName_Date, newFileName_User, newFileName_Camera)

    destination = newFilePath + newFileName + '.' + extension

    print destination



    print '>>> done!'
    return newFileName


#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():

    # setup parser
    parser = argparse.ArgumentParser(description='Read EXIF data ofa  given media file, update filename and sort into structured directory')

    # script uses the artist name to help createu uinique file names
    parser.add_argument('-a', '--artistName',
                        required=False,
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
                        metavar='MEDIA_DIRECTORY', type=lambda x: spacer())

    args = vars(parser.parse_args())

    print args

    spacer()

    try:
        processMediaFile(args['mediaFile'])
    except:
        print '>>> no files to process... all done!'


if __name__ == '__main__':
    main()
