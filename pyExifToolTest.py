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
    for key, value in dataDictionary.iteritems():
        print '%s\t:\t%s' % (key, value)




def JSONToDict(data):
    print 'creating exifDict from json data...'

    if len(data) < 1:
        print 'this file has no exif data'
        return
    else:
        # dataDict = dict(sorted(data[0].iteritems()))
        dataDict = dict(sorted(data[0].iteritems()))
        print type(dataDict)
        print dataDict
        return dataDict


#------------------------------------------------------------------------------
#		main data points functions
#------------------------------------------------------------------------------

def getCameraModel(data):
    print 'getting camera info...'

    # get tags with the word 'date' in them



def getMediaDateTimeStamp(data):
    print 'getting earliest media time stamp...'

    # collect all date relted keys and values
    dateTimeTags = []

    for key, value in data.iteritems():
        if 'date' in key.lower():
            # print 'found \'%s\' tag...'
            dateTimeTags.append([key, value])
            # print dateTimeTags

    print 'All date and time related tags...'
    for entry in dateTimeTags:
        print '%s\t%s' % (entry[0], entry[1])


    # find earliest dateTimeTag, that is most likely the date media was captured or created

    earliestTag = ''
    earliestDateTimeStamp = ''

    for entry in dateTimeTags:
        # default case
        if len(earliestTag) < 1:
            earliestTag = entry[0]
            earliestDateTimeStamp = entry[1]

        else:


            dateTimeStamp = entry[1]
            # remove timezone adjsutment if it exists
            try:
                dateTimeStamp.split('-')[0]
            except:
                pass

            # break into components
            mediaYear = dateTimeStamp.split(' ')[0].split(':')[0]
            mediaMonth = dateTimeStamp.split(' ')[0].split(':')[1]
            mediaDay = dateTimeStamp.split(' ')[0].split(':')[2]
            mediaHour = edateTimeStamp.split(' ')[1].split(':')[0]
            mediaMinute = dateTimeStamp.split(' ')[1].split(':')[1]
            mediaSecond = dateTimeStamp.split(' ')[1].split(':')[2]

            # if tag is later than existing earliest tag, skip
            if True:
                # check mediaYear

                # check mediaMonth

                # check mediaDay

                # check mediaHour

                # check mediaMinute

                # check mediaSecond

            # else, set as new earliest tag
            else:
                earliestTag = entry[0]
                earliestDateTimeStamp = entry[1]



def getCameraOperator(data, name):
    print 'getting camera operator/photographer information...'









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

    print 'filename: %s' % str(args['mediaFile']).split("'")[1]
    filename = str(args['mediaFile']).split("'")[1]

    exifTagsDict = JSONToDict(p.get_json(filename))

    spacer()
    prettyPrintTags(exifTagsDict)
    spacer()

    getMediaDateTimeStamp(exifTagsDict)

    spacer()












if __name__ == '__main__':
    main()
