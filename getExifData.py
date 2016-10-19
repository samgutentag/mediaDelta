#!/usr/bin/env python

import exifread
import argparse
import os

#------------------------------------------------------------------------------
#		functions
#------------------------------------------------------------------------------

# prints a default spacer to console
def spacer():

	print '\n'
	print '#' + '-' * 79
	print '\n'

def isFileOfType(file, knownFileTypes):
	# print 'Checking filetype of %s' % file


	# get file extension
	extension = file.split('.')[-1].upper()

	# check if file is in knownFileType list
	if extension in knownFileTypes:
		return True
	else:
		return False


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

# reads in exif tags, returns imageDate string
def getDate(exifTagsDict):
	imageDate = ''
	knownDateTimeTags = ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime'];
	for tag in knownDateTimeTags:
		if len(imageDate) < 1:
			try:
				imageDate = str(exifTagsDict[tag])
				print "Using '%s' tag: %s" % (tag, imageDate)
			except:
				print "Could not find '%s' tag" % tag

	# default fall back
	if len(imageDate) < 1:
		print 'No image Date Tags found'
		imageDate = 'NO_DATE'

	return imageDate

# returns the file name from a full path file
def getFileName(file):
	mediaFileName = str(file).split('/')[-1].split("'")[0]
	return mediaFileName

# returns sourth path of a file only
def getFileSourcePath(file):
	mediaFilePath = str(file).split(mediaFileName)[0].split("'")[-1]
	return mediaFilePath

# returns identifier for device that captured or created the image
def getImageSourceDevice(exifTagsDict):
	imageSourceDevice = ''

	knownImageSourceTags= ['MakerNote ImageType', 'Image Make', 'Image Software']

	for tag in knownImageSourceTags:
		if len(imageSourceDevice) < 1:
			try:
				imageSourceDevice = str(exifTagsDict[tag])

				if tag == 'Image Make':
					try:
						imageSourceDevice = imageSourceDevice + '_' + str(exifTagsDict['Image Model'])
						print "Using '%s' and 'Image Model' tags: %s" % (tag, imageSourceDevice.replace(' ', '_'))
					except:
						print "Could not find 'Image Model' tag, skipping..."

				print "Using '%s' tag: %s" % (tag, imageSourceDevice.replace(' ', '_'))
			except:
				print "Could not find '%s' tag" % tag

	# default fall back
	if len(imageSourceDevice) < 1:
		print 'Could not generate SourceDevice from known image capture or creation tags'
		imageSourceDevice = 'NO_SOURCEDEVICE'

	imageSourceDevice = imageSourceDevice.replace(' ', '_')

	return imageSourceDevice





def setFileDestinationPath(rootLocation, mediaFile):
	print 'setting file destination path'

	# set new path based on image date, also set case for image without date

	imageTags = exifread.process_file(args.mediaFile)

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
#		argparser setup
#------------------------------------------------------------------------------
knownImageFileTypes = ['JPG', 'CR2', 'PNG', 'JPEG', 'TIFF', 'TIF']
knownVideoFileTypes = ['MOV', 'MP4']

def isValidFile(parser, arg):
	if not os.path.exists(arg):
		parser.error('The file %s does not exists' % arg)
	else:
		if isFileOfType(arg, knownImageFileTypes):
			print '%s is an image file!' % arg
			return open(arg, 'rb')
		elif isFileOfType(arg, knownVideoFileTypes):
			print '%s is a video file!' % arg
			return open(arg, 'rb')
		else:
			parser.error('The file %s is not a known image type' % arg)


parser = argparse.ArgumentParser(description='Read EXIF data of a given image file')
parser.add_argument('-f', dest='mediaFile', required=True, help='input image file to read EXIF data from', metavar='FILE', type=lambda x: isValidFile(parser, x))
# parser.add_argument('-d', dest='imagesFolder', required=True, help='input image file to read EXIF data from', metavar='IMAGE', type=lambda x: isValidmediaFile(parser, x))

args = parser.parse_args()

exifTagsDict = exifread.process_file(args.mediaFile)




#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------


mediaFileName = getFileName(args.mediaFile)
mediaFilePath = getFileSourcePath(args.mediaFile)

printTags(exifTagsDict)
spacer()

imageDate = getDate(exifTagsDict)
# spacer()

imageSourceDevice = getImageSourceDevice(exifTagsDict)
# print '*' * 80
# print imageSourceDevice
# print '*' * 80

spacer()

print "File path:\t'%s'" % mediaFilePath
print "File:\t\t'%s'" % mediaFileName

spacer()

# setFileDestinationPath('/Users/samgutentag/Desktop/', args.mediaFile)

# spacer()
