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

    # collect all date relted keys and values
    dateTimeTags = []

    for key, value in data.iteritems():
        if 'date' in key.lower():
            # print 'found \'%s\' tag...'
            if 'icc' not in key.lower():
                dateTimeTags.append([key, value])

    # find earliest 'dateTimeTag'
    earliestTag = ''

    # formatted earliestDateTimeStamp YYYYMMDDHHmmSSsss
    earliestDateTimeStamp = 999999999999999999999999999


    for entry in dateTimeTags:
        dateTimeStamp = entry[1]

        # remove timezone adjustment if it exists
        try:
            dateTimeStamp = dateTimeStamp.split('-')[0]
        except:
            pass

        # default values for each to fall back on
        yearStamp = ''
        monthStamp = ''
        dayStamp = ''
        hourStamp = ''
        minuteStamp = ''
        secondStamp = ''
        millisecondStamp = ''

        # try to split into dateStamp and timeStamp
        try:
            dateStamp = dateTimeStamp.split(' ')[0]
        except:
            dateStamp = '9999:99:99'

        try:
            timeStamp = dateTimeStamp.split(' ')[1]

            # sometimes time stamps have letters appened to the end of the second, lets remove those
            while timeStamp[len(timeStamp)-1].isalpha():
                timeStamp = timeStamp[:-1]
        except:
            timeStamp = '23:59:99'

        # update values for each
        yearStamp = dateStamp.split(':')[0]
        monthStamp = dateStamp.split(':')[1]
        dayStamp = dateStamp.split(':')[2]
        hourStamp = timeStamp.split(':')[0]
        minuteStamp = timeStamp.split(':')[1]
        secondStamp = timeStamp.split(':')[2]

        # try splitting secondStamp into secondStamp and millisecondStamp
        try:
            millisecondStamp = secondStamp.split('.')[1]
            secondStamp = secondStamp.split('.')[0]

            # some time stamps come through with an alpha character(s) suffix
            # lets remove those if they exist
            while millisecondStamp[len(millisecondStamp)-1].isalpha():
                millisecondStamp = millisecondStamp[:-1]

        except:
            millisecondStamp = '999'

        # format millisecondStamp to be a fixed length
        if len(millisecondStamp) > 3:
            millisecondStamp = millisecondStamp[:4]

        while len(millisecondStamp) < 3:
            millisecondStamp = millisecondStamp + '0'

        # format dateTimeStamp for integer comparison
        dateTimeFormattedStamp = '%s%s%s%s%s%s%s' % (yearStamp,monthStamp,dayStamp,hourStamp,minuteStamp,secondStamp,millisecondStamp)
        dateTimeFormattedStampINT = int(dateTimeFormattedStamp)

        # check if dateTimeINT is earlier than previous earliestTag
        if dateTimeFormattedStampINT < earliestDateTimeStamp:
            earliestTag = str(entry[0])
            earliestDateTimeStamp = dateTimeFormattedStampINT

        # break string back into components
        yearStamp = str(earliestDateTimeStamp)[0:4]
        monthStamp = str(earliestDateTimeStamp)[4:6]
        dayStamp = str(earliestDateTimeStamp)[6:8]
        hourStamp = str(earliestDateTimeStamp)[8:10]
        minuteStamp = str(earliestDateTimeStamp)[10:12]
        secondStamp = str(earliestDateTimeStamp)[12:14]
        millisecondStamp = str(earliestDateTimeStamp)[14:17]

    print '>>> done!'
    return (yearStamp, monthStamp, dayStamp, hourStamp, minuteStamp, secondStamp, millisecondStamp)

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

    spacer()
    exifTagsDict = JSONToDict(p.get_json(fileName))

    spacer()
    dateTimeStamp = getMediaDateTimeStamp(exifTagsDict)
    print dateTimeStamp

    spacer()
    cameraInfo = getCameraModel(exifTagsDict)


    # spacer()
    # prettyPrintTags(exifTagsDict)

    # all done!
    spacer()

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
