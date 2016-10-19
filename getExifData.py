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

# validation to check incoming file type
def isFileOfType(file, knownFileTypes):
	print 'Checking filetype of %s' % file

	# get file extension
	extension = file.split('.')[-1].upper()

	# check if file is in knownFileType list
	if extension in knownFileTypes:
		return True
	else:
		return False


# prints all EXIF tags that can be found on the file
def printTags(exifTagsDict):
	spacer()
	counter = 0
	longestTag = 0

	# get string length of longest key
	# assit in pretty printing
	for key in exifTagsDict.keys():
		if len(key) > longestTag:
			longestTag = len(key)

	# pretty print exif tags
	for tag, entry in sorted(exifTagsDict.iteritems()):
		# excludes text encoded image tags
		# these are just a ton of garbage data we dont need
		if tag not in ('JPEGThumbnail', 'TIFFThumbnail'):

			# calculate number of tab characters needed to pretty print
			tabsNeeded = ((longestTag - len(tag))/4) + 1

			# print all in line and numbered
			print '%s:\t%s:' % (counter, tag),
			print '\t' * tabsNeeded,
			print entry
			counter += 1

# reads in exif tags, returns imageDateTime string
def getDateTime(exifTagsDict):
	imageDateTime = ''

	# search known, preset, image tags for date and time information of image.
	#
	#	TO DO
	#	Refactor to look for earliest tag available, not just the first one
	#	to be found from given list
	#

	# list of known DateTime tags, to be checked in order
	knownDateTimeTags = ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime'];

	for tag in knownDateTimeTags:
		# copy date time data form tag if imageDateTime is currently empty
		if imageDateTime == '':
			try:
				imageDateTime = str(exifTagsDict[tag])
				print "Using '%s' tag: %s" % (tag, imageDateTime)

				# form correct string for output
				try:
					imageYear = imageDateTime.split(' ')[0].split(':')[0]
					imageMonth = imageDateTime.split(' ')[0].split(':')[1]
					imageDay = imageDateTime.split(' ')[0].split(':')[2]
					imageHour = imageDateTime.split(' ')[1].split(':')[0]
					imageMinute = imageDateTime.split(' ')[1].split(':')[1]
					imageSecond = imageDateTime.split(' ')[1].split(':')[2]

					imageDateTime = '%s%s%s%s%s%s' % (imageYear, imageMonth, imageDay, imageHour, imageMinute, imageSecond)

					print imageDateTime

					return imageDateTime
					
				except:
					print 'Could not form imageDateTime from %s tag, skipping...' % tag

			except:
				print "Could not find '%s' tag, skipping..." % tag

	# if it gets this far, no DateTime tags could be found or fomred correctly
	# return default output
	print 'No image Date Time Tags found'
	imageDateTime = 'NO_DATE_TIME'

	print imageDateTime

	return imageDateTime



	# for tag in knownDateTimeTags:
	# 	# copy date time data form tag if imageDateTime is currently empty
	# 	if len(imageDateTime) < 1:
	# 		try:
	# 			imageDateTime = str(exifTagsDict[tag])
	# 			print "Using '%s' tag: %s" % (tag, imageDateTime)
	# 		except:
	# 			print "Could not find '%s' tag, skipping..." % tag

	# # default fall back in the case that no DateTime tags can be found
	# if len(imageDateTime) < 1:
	# 	print 'No image Date Time Tags found'
	# 	imageDateTime = 'NO_DATE_TIME'
	#
	# # form correct string for output
	# else:
	# 	imageYear = imageDateTime.split(' ')[0].split(':')[0]
	# 	imageMonth = imageDateTime.split(' ')[0].split(':')[1]
	# 	imageDay = imageDateTime.split(' ')[0].split(':')[2]
	# 	imageHour = imageDateTime.split(' ')[1].split(':')[0]
	# 	imageMinute = imageDateTime.split(' ')[1].split(':')[1]
	# 	imageSecond = imageDateTime.split(' ')[1].split(':')[2]
	#
	# 	imageDateTime = '%s%s%s%s%s%s' % (imageYear, imageMonth, imageDay, imageHour, imageMinute, imageSecond)
	#


	# # form correct string for output
	# try:
	# 	imageYear = imageDateTime.split(' ')[0].split(':')[0]
	# 	imageMonth = imageDateTime.split(' ')[0].split(':')[1]
	# 	imageDay = imageDateTime.split(' ')[0].split(':')[2]
	# 	imageHour = imageDateTime.split(' ')[1].split(':')[0]
	# 	imageMinute = imageDateTime.split(' ')[1].split(':')[1]
	# 	imageSecond = imageDateTime.split(' ')[1].split(':')[2]
	#
	# 	imageDateTime = '%s%s%s%s%s%s' % (imageYear, imageMonth, imageDay, imageHour, imageMinute, imageSecond)

	# default fall back in the case that no DateTime tags can be found
	# except:
	# 	print 'No image Date Time Tags found'
	# 	imageDateTime = 'NO_DATE_TIME'
	#
	# print imageDateTime
	#
	# return imageDateTime

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

	imageDate = getDateTime(imageTags)
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

imageDate = getDateTime(exifTagsDict)
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
