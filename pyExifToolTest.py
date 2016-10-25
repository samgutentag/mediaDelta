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
def prettyPrintTags(data):
    print (json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

def prettyPrintTags2(data):
    counter = 0
    for item in sorted(data[0].iteritems()):

        tag = item[0]
        info = item[-1]

        print '%i:\t%s' % (counter, item)
        print '%i:\t%s\t%s' % (counter, tag, info)

        print
        counter += 1

#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():

    # setup parser
    parser = argparse.ArgumentParser(description='Read EXIF data ofa  given media file, update filename and sort into structured directory')

    # script uses the artist name to help createu uinique file names
    parser.add_argument('-a', '--artistName', required=True, help='default artist name', metavar='ARTIST_NAME')

    # passing a single file
    parser.add_argument('-f', '--mediaFile', dest='mediaFile', required=False, help='pass a single file to process', metavar='MEDIA_FILE', type=lambda x: openMediaFile(parser, x))

    # passing a directory (with or without sub directories) of files
    parser.add_argument('-d', '--mediaDirectory', dest='mediaDirectory', required=False, help='pass a directory of files to process, WARNING: RECURSIVE', metavar='MEDIA_DIRECTORY', type=lambda x: spacer())

    args = vars(parser.parse_args())

    print 'filename: %s' % str(args['mediaFile']).split("'")[1]
    filename = str(args['mediaFile']).split("'")[1]

    exifTagsDict = p.get_json(filename)

    spacer()

    print exifTagsDict

    spacer()

    prettyPrintTags(exifTagsDict)

    spacer()

    prettyPrintTags2(exifTagsDict)

    spacer()


main()
#
#
#
#
#
#
#
#
#
#
#
# fileName = '/Users/samgutentag/Downloads/IMG_1767.MOV'
# data = p.get_json(fileName)
# print (json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
#
#
# print '\n'
# print '#' + '-' * 79
# print '\n'
#
# fileName = '/Users/samgutentag/Developer/python/mediaDelta/samplePhotos/phoneImage.JPG'
# data = p.get_json(fileName)
# print (json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
