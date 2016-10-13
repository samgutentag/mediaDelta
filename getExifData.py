#!/usr/bin/env python

import exifread
import argparse
import os


#------------------------------------------------------------------------------
#		argparser setup
#------------------------------------------------------------------------------


def isValidImageFile(parser, arg):
	if not os.path.exists(arg):
		parser.error('The file %s does not exists' % arg)
	else:
		return open(arg, 'rb')


parser = argparse.ArgumentParser(description='Read EXIF data of a given image file')
parser.add_argument('-i', dest='imageFile', required=True, help='input image file to read EXIF data from', metavar='IMAGE', type=lambda x: isValidImageFile(parser, x))
# parser.add_argument('-f', dest='imagesFolder', required=True, help='input image file to read EXIF data from', metavar='IMAGE', type=lambda x: isValidImageFile(parser, x))

args = parser.parse_args()

testTagsDict = exifread.process_file(args.imageFile)


#------------------------------------------------------------------------------
#		functions
#------------------------------------------------------------------------------

# prints a default spacer to console
def spacer():

	print '\n'
	print '#' + '-' * 79
	print '\n'

# prints all EXIF tags that can be found on the file, with the exception of 
def printTags(exifTagsDict):
	spacer()
	counter = 0
	longestTag = 0

	for key in exifTagsDict.keys():
		if len(key) > longestTag:
			longestTag = len(key)

	for tag, entry in sorted(exifTagsDict.iteritems()):
		if tag not in ('JPEGThumbnail', 'TIFFThumbnail'):
			tabsNeeded = ((longestTag - len(tag))/4) + 1
			
			print '%s:\t%s:' % (counter, tag),
			print '\t' * tabsNeeded,
			print entry
			
			counter += 1

# reads in exif tags, returns imageDAte string
def getDate(exifTagsDict):
	imageDate = ''
	for tag in ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime']:
		if len(imageDate) < 1:
			try:
				imageDate = str(exifTagsDict[tag])
				print "Using '%s' tag" % tag
			except:
				print "Could not find '%s' tag" % tag

	if len(imageDate) < 1:
		print 'No image Date Tags found'
		imageDate = 'NO_DATE'

	print '$$ ' + imageDate + ' $$'

	return imageDate


def getFileName(file):
	imageFileName = str(file).split('/')[-1].split("'")[0]
	return imageFileName

def getFileSourcePath(file):
	imageFilePath = str(file).split(imageFileName)[0].split("'")[-1]
	return imageFilePath


def setFileDestinationPath(rootLocation, imageFile):
	print 'setting file destination path'

	# set new path based on image date, also set case for image without date

	imageTags = exifread.process_file(args.imageFile)

	printTags(imageTags)

	imageDate = getDate(imageTags)
	print imageDate


	try:
		imageDateYear = imageDate.split(':')[0]
		imageDateMonth = imageDate.split(':')[1]
	except:
		imageDateYear = 'XXXX'
		imageDateMonth = 'XX'

	print 'Year:\t%s' % imageDateYear
	print 'Month:\t%s' % imageDateMonth

	destinationPath = rootLocation






def setFileName(file):
	print 'setting file name'



#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------


imageFileName = getFileName(args.imageFile)
imageFilePath = getFileSourcePath(args.imageFile)



# printTags(testTagsDict)
# spacer()

# imageDate = getDate(testTagsDict)
# spacer()

# print 'File \'%s\' dated %s' % (imageFileName, imageDate)
# print 'File path:\t%s' % imageFilePath



spacer()



setFileDestinationPath('/Users/samgutentag/Desktop/', args.imageFile)



spacer()







