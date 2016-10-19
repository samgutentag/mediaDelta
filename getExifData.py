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
		# excludes text encoded tags
		# these are just a ton of garbage data we dont need
		if tag not in ('JPEGThumbnail', 'TIFFThumbnail'):

			# calculate number of tab characters needed to pretty print
			tabsNeeded = ((longestTag - len(tag))/4) + 1

			# print all in line and numbered
			print '%s:\t%s:' % (counter, tag),
			print '\t' * tabsNeeded,
			print entry
			counter += 1

# reads in exif tags, returns mediaDateTime string
def getMediaDateTime(exifTagsDict):
	mediaDateTime = ''

	# search known, preset, media tags for date and time information of media.
	#
	#	TO DO
	#	Refactor to look for earliest tag available, not just the first one
	#	to be found from given list
	#

	# list of known DateTime tags, to be checked in order
	knownDateTimeTags = ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime'];

	for tag in knownDateTimeTags:
		# copy date time data form tag if mediaDateTime is currently empty
		if mediaDateTime == '':
			try:
				mediaDateTime = str(exifTagsDict[tag])
				print "Using '%s' tag:\t%s" % (tag, mediaDateTime)

				# form correct string for output
				try:
					mediaYear = mediaDateTime.split(' ')[0].split(':')[0]
					mediaMonth = mediaDateTime.split(' ')[0].split(':')[1]
					mediaDay = mediaDateTime.split(' ')[0].split(':')[2]
					mediaHour = mediaDateTime.split(' ')[1].split(':')[0]
					mediaMinute = mediaDateTime.split(' ')[1].split(':')[1]
					mediaSecond = mediaDateTime.split(' ')[1].split(':')[2]

					mediaDateTime = '%s%s%s%s%s%s' % (mediaYear, mediaMonth, mediaDay, mediaHour, mediaMinute, mediaSecond)

					return mediaDateTime

				except:
					print 'Could not form mediaDateTime from %s tag, skipping...' % tag

			except:
				print "Could not find '%s' tag, skipping..." % tag

	# if it gets this far, no DateTime tags could be found or fomred correctly
	# return default output
	print 'No media Date Time Tags found'
	mediaDateTime = 'NO_DATE_TIME'

	return mediaDateTime

# returns identifier for device that captured or created the media
def getMediaSourceDevice(exifTagsDict):
	mediaSourceDevice = ''

	knownmediaSourceTags= ['MakerNote ImageType', 'Image Make', 'Image Software']

	for tag in knownmediaSourceTags:
		if mediaSourceDevice == '':
			try:
				mediaSourceDevice = str(exifTagsDict[tag])

				# handling for media captured with a camera
				# combines make and model into a single string
				if tag == 'Image Make':
					try:
						mediaSourceDevice = mediaSourceDevice + '_' + str(exifTagsDict['Image Model'])
						print "Using '%s' and 'Image Model' tags: %s" % (tag, mediaSourceDevice.replace(' ', '_'))
					except:
						print "Could not find 'Image Model' tag, skipping..."
				else:
					print "Using '%s' tag:\t%s" % (tag, mediaSourceDevice.replace(' ', '_'))
			except:
				print "Could not find '%s' tag" % tag

	# default fall back
	if len(mediaSourceDevice) < 1:
		print 'Could not generate SourceDevice from known media capture or creation tags'
		mediaSourceDevice = 'NO_SOURCEDEVICE'

	mediaSourceDevice = mediaSourceDevice.replace(' ', '_')

	return mediaSourceDevice

# returns name associated with the media, often the person who took the photo
# will fall back to required artistName argument required by script
def getMediaArtistName(exifTagsDict, artistName):

	mediaArtistName = ''
	try:
		mediaArtistName = str(exifTagsDict['MakerNote OwnerName'])

	except:
		print 'No artist tag found, using default'
		# mediaArtistName = artistName
		return artistName.replace(' ', '').lower()

	if len(mediaArtistName) > 0:
		print "Using 'MakerNote OwnerName' tag:\t%s" % mediaArtistName
		return mediaArtistName.replace(' ', '').lower()
	else:
		print 'No artist tag found, using default'
		return artistName.replace(' ', '').lower()

# returns the file name from a full path file
def getFileName(file):
	mediaFileName = str(file).split('/')[-1].split("'")[0]
	return mediaFileName

# returns source path of a file only
def getFileSourcePath(file):
	mediaFileName = getFileName(file)
	mediaFilePath = str(file).split(mediaFileName)[0].split("'")[-1]
	return mediaFilePath



def isValidFile(parser, arg, knownImageFileTypes, knownVideoFileTypes):
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
			parser.error('The file %s is not a known media type' % arg)


#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():

	knownImageFileTypes = ['JPG', 'CR2', 'PNG', 'JPEG', 'TIFF', 'TIF']
	knownVideoFileTypes = ['MOV', 'MP4']

	parser = argparse.ArgumentParser(description='Read EXIF data of a given media file')

	# pass name of person running the script, wil be used in file naming as a fallback if no artist information can be found in exif tags
	parser.add_argument('-a', '--artistName', required=True, help='used as a fallback artist name for file naming', metavar='ARTIST_NAME')

	# passing a single file
	parser.add_argument('-f', dest='mediaFile', required=True, help='input media file to read EXIF data from', metavar='MEDIA_FILE', type=lambda x: isValidFile(parser, x, knownImageFileTypes, knownVideoFileTypes))

	# passing a directory with subdirectories and files
	parser.add_argument('-d', dest='mediaDirectory', required=False, help='input directory', metavar='MEDIA_DIRECTORY', type=lambda x: spacer())

	args = vars(parser.parse_args())

	exifTagsDict = exifread.process_file(args['mediaFile'])

	mediaFileName = getFileName(args['mediaFile'])
	mediaFilePath = getFileSourcePath(args['mediaFile'])
	mediaFileExtension = mediaFileName.split('.')[-1]

	spacer()
	mediaDate = getMediaDateTime(exifTagsDict)
	mediaSourceDevice = getMediaSourceDevice(exifTagsDict)
	mediaArtist = getMediaArtistName(exifTagsDict, args['artistName'])

	oldFileName = mediaFileName
	newFileName = '%s_%s_%s.%s' % (mediaDate, mediaArtist, mediaSourceDevice, mediaFileExtension)

	spacer()
	print 'mediaDate:\t\t%s' % mediaDate
	print 'mediaSourceDevice:\t%s' % mediaSourceDevice
	print 'mediaArtist:\t\t%s' % mediaArtist
	print
	print 'oldFileName:\t\t%s' % oldFileName
	print 'newFileName:\t\t%s' % newFileName
	spacer()

	return True

if __name__ == "__main__":
	main()
