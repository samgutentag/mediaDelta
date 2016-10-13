#!/usr/bin/python

#import libraries to get exif data and for system level file manipulation

import exifread
import shutil
# import argparse

# print 'Lets rename some photos!'

knownFileTypes = ['JPG', 'CR2', 'PNG', 'JPEG', 'TIFF']


fTest = '/Users/samgutentag/Developer/python/imageTagging/SAMPLES/Cedar Point Amusement Park - Sandusky, OH, September 25, 2010/2010 Detroit - TF3 0064.JPG'
fTest = '/Users/samgutentag/Developer/python/mediaDelta/samplePhotos/Cedar Point Amusement Park - Sandusky, OH, September 25, 2010/2010 Detroit - TF3 0064.JPG'

def isFileOfType(file, knownFileTypes):
	# print 'Checking filetype of %s' % file
	

	# get file extension
	extension = file.split('.')[-1].upper()

	# check if file is in knownFileType list
	if extension in knownFileTypes:
		return True
	else:
		return False


def renameFile(sourceFile):
	print 'renaming %s' % sourceFile

	# check file type
	if isFileOfType(sourceFile, knownFileTypes):

		# open file
		f = open(sourceFile, 'rb')

		# get file extension
		extension = sourceFile.split('.')[-1].upper()
		destinationDirectory = '/Users/samgutentag/Desktop/'

		# get tags
		fTags = exifread.process_file(f)

		# get creation date
		creationDate = fTags['EXIF DateTimeOriginal']

		# print 'file created:\t %s' % creationDate
	
		# format string
		date = str(creationDate).split(' ')[0]
		time = str(creationDate).split(' ')[1]

		year = date.split(':')[0]
		month = date.split(':')[1]
		day = date.split(':')[2]

		hour = time.split(':')[0]
		minute = time.split(':')[1]
		second = time.split(':')[2]

		# print 'Year %s' % year
		# print 'Month %s' % month
		# print 'Day %s' % day

		# print 'Hour %s' % hour
		# print 'Minute %s' % minute
		# print 'Second %s' % second


		# rename file with string
		newFileName = '%s%s%s_%s%s%s.%s' % (year, month, day, hour, minute, second, extension)

		destinationFile = destinationDirectory + newFileName


		print '\ncopying %s to:\n\t%s' % (sourceFile, destinationFile)


		# copy file to main library
		shutil.copy2(sourceFile, destinationFile)

		print 'copied!'
	else:
		print '%s is not a supported file type, ignoring' % sourceFile


# print
# print '=' * 80
# print 'File name is: %s' % fTest
# print 'Is known file type: %r' % isFileOfType(fTest, knownFileTypes)
# renameFile(fTest)


print
