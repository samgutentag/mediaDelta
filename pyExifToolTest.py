#!/usr/bin/end python

import pyexifinfo as p
import argparse
import json
import os

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
    for key, value in dataDictionary.iteritems():
        print '%s\t:\t%s' % (key, value)
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


#------------------------------------------------------------------------------
#		main data points functions
#------------------------------------------------------------------------------

def getCameraModel(data):
    print '>>> getting camera info...'

    print '>>> done!'

    # get tags with the word 'date' in them



def getMediaDateTimeStamp(data):
    print '>>> getting earliest media time stamp...'

    # collect all date relted keys and values
    dateTimeTags = []

    for key, value in data.iteritems():
        if 'date' in key.lower():
            # print 'found \'%s\' tag...'
            dateTimeTags.append([key, value])
            # print dateTimeTags

    # find earliest 'dateTimeTag'

    earliestTag = ''

    # formatted earliestDateTimeStamp YYYYMMDDHHmmSSsss
    earliestDateTimeStamp = 999999999999999999999999999
    # earliestDateTimeStamp = 0

    for entry in dateTimeTags:
        dateTimeStamp = entry[1]

        # remove timezone adjustment if it exists
        try:
            dateTimeStamp = dateTimeStamp.split('-')[0]
        except:
            pass

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
            timeStamp = '23:59:99.999'

        # append fake milliseconds if they dont exists
        try:
            timeStampMilliseconds = timeStamp.split('.')[1]
            # strip milliseconds down to being 4 characters ie '.123'
            if len(timeStampMilliseconds) > 3:
                timeStampMilliseconds = timeStampMilliseconds[:4]
        # if milliseconds are not in the tag, max it out
        except:
            timeStamp = timeStamp + '.999'

        dateStamp = dateStamp.replace(':', '')
        timeStamp = timeStamp.replace(':', '').replace('.', '')

        # convert date and time stamps into a formatted string for comparison
        dateTimeINT = '%s%s' % (dateStamp,timeStamp)

        # check if dateTimeINT is earlier than previous earliestTag
        if int(dateTimeINT) < int(earliestDateTimeStamp):
            earliestTag = entry[0]
            earliestDateTimeStamp = int(dateTimeINT)



    return dateTimeINT



    print '>>> done!'




def getCameraOperator(data, name):
    print '>>> getting camera operator/photographer information...'

    print '>>> done!'








#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():

    # setup parser
    parser = argparse.ArgumentParser(description='Read EXIF data ofa  given media file, update filename and sort into structured directory')

    # script uses the artist name to help createu uinique file names
    parser.add_argument('-a', '--artistName',
                        required=True,
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

    spacer()
    print 'file: %s' % str(args['mediaFile']).split("'")[1]
    filename = str(args['mediaFile']).split("'")[1]

    spacer()
    exifTagsDict = JSONToDict(p.get_json(filename))

    spacer()
    prettyPrintTags(exifTagsDict)

    spacer()
    dateTimeStamp = getMediaDateTimeStamp(exifTagsDict)



    # all done!
    spacer()












if __name__ == '__main__':
    main()
