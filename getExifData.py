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
	# print 'Checking filetype of %s' % file

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

	# make sure there is exif data to read, else escape
	if len(exifTagsDict) < 1:
		print 'This file has no exif data to read'
		return

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
				print "Using '%s' tag:\t%s" % (tag, imageDateTime)

				# form correct string for output
				try:
					imageYear = imageDateTime.split(' ')[0].split(':')[0]
					imageMonth = imageDateTime.split(' ')[0].split(':')[1]
					imageDay = imageDateTime.split(' ')[0].split(':')[2]
					imageHour = imageDateTime.split(' ')[1].split(':')[0]
					imageMinute = imageDateTime.split(' ')[1].split(':')[1]
					imageSecond = imageDateTime.split(' ')[1].split(':')[2]

					imageDateTime = '%s%s%s%s%s%s' % (imageYear, imageMonth, imageDay, imageHour, imageMinute, imageSecond)

					return imageDateTime

				except:
					print 'Could not form imageDateTime from %s tag, skipping...' % tag

			except:
				print "Could not find '%s' tag, skipping..." % tag

	# if it gets this far, no DateTime tags could be found or fomred correctly
	# return default output
	print 'No image Date Time Tags found'
	imageDateTime = 'NO_DATE_TIME'

	return imageDateTime

# returns identifier for device that captured or created the image
def getImageSourceDevice(exifTagsDict):
	imageSourceDevice = ''

	knownImageSourceTags= ['MakerNote ImageType', 'Image Make', 'Image Software']

	for tag in knownImageSourceTags:
		if imageSourceDevice == '':
			try:
				imageSourceDevice = str(exifTagsDict[tag])

				# handling for images captured with a camera
				# combines make and model into a single string
				if tag == 'Image Make':
					try:
						imageSourceDevice = imageSourceDevice + '_' + str(exifTagsDict['Image Model'])
						print "Using '%s' and 'Image Model' tags: %s" % (tag, imageSourceDevice.replace(' ', '_'))
					except:
						print "Could not find 'Image Model' tag, skipping..."
				else:
					print "Using '%s' tag:\t%s" % (tag, imageSourceDevice.replace(' ', '_'))
			except:
				print "Could not find '%s' tag" % tag

	# default fall back
	if len(imageSourceDevice) < 1:
		print 'Could not generate SourceDevice from known image capture or creation tags'
		imageSourceDevice = 'NO_SOURCEDEVICE'

	imageSourceDevice = imageSourceDevice.replace(' ', '_')

	return imageSourceDevice

# returns name associated with the image, often the person who took the photo
# will fall back to required artistName argument required by script
def getImageArtistName(exifTagsDict, artistName):

	mediaArtistName = str(exifTagsDict['MakerNote OwnerName'])

	if len(mediaArtistName) > 0:
		print "Using 'MakerNote OwnerName' tag:\t%s" % mediaArtistName
		return mediaArtistName.replace(' ', '').lower()
	else:
		print 'No artist tag found, using default'
		return artistName.replace(' ', '').lower()


# returns source path of a file only
def getFileSourcePath(file):
	mediaFilePath = str(file).split(mediaFileName)[0].split("'")[-1]
	return mediaFilePath

# returns the file name from a full path file
def getFileName(file):
	mediaFileName = str(file).split('/')[-1].split("'")[0]
	return mediaFileName


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
			# print '%s is an image file!' % arg
			return open(arg, 'rb')
		elif isFileOfType(arg, knownVideoFileTypes):
			# print '%s is a video file!' % arg
			return open(arg, 'rb')
		else:
			parser.error('The file %s is not a known image type' % arg)

parser = argparse.ArgumentParser(description='Read EXIF data of a given image file')

# passing a single file
parser.add_argument('-f', dest='mediaFile', required=True, help='input image file to read EXIF data from', metavar='IMAGE_FILE', type=lambda x: isValidFile(parser, x))

# passing a directory with subdirectories and files
parser.add_argument('-d', dest='mediaDirectory', required=False, help='input directory', metavar='IMAGE_DIRECTORY', type=lambda x: spacer())

# pass name of person running the script, wil be used in file naming as a fallback if no artist information can be found in exif tags
parser.add_argument('-a', '--artistName', required=True, help='used as a fallback artist name for file naming', metavar='ARTIST_NAME')

args = vars(parser.parse_args())


exifTagsDict = exifread.process_file(args['mediaFile'])

# print args['artistName']



#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():
	# print 'Hello World!'
	return True

if __name__ == "__main__":
	main()

mediaFileName = getFileName(args['mediaFile'])
mediaFilePath = getFileSourcePath(args['mediaFile'])
mediaFileExtension = mediaFileName.split('.')[-1]

# spacer()
# printTags(exifTagsDict)
# spacer()

spacer()
imageDate = getDateTime(exifTagsDict)
imageSourceDevice = getImageSourceDevice(exifTagsDict)
imageArtist = getImageArtistName(exifTagsDict, args['artistName'])

oldFileName = mediaFileName
newFileName = '%s_%s_%s.%s' % (imageDate, imageArtist, imageSourceDevice, mediaFileExtension)


spacer()
print 'imageDate:\t\t%s' % imageDate
print 'imageSourceDevice:\t%s' % imageSourceDevice
print 'imageArtist:\t\t%s' % imageArtist
print
print 'oldFileName:\t\t%s' % oldFileName
print 'newFileName:\t\t%s' % newFileName
spacer()
