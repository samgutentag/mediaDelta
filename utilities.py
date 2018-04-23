

import sys
import logging
import os
import pyexifinfo
# import getpass
from getpass import getuser
import shutil

from datetime import datetime
from dateutil.parser import parse as date_parser

# thumbnail imports
from PIL import Image
import rawpy

#----------------------------------------------------------------------------
#       Custom Classes
#----------------------------------------------------------------------------

class CameraObject:

    def __init__(self, make, model, serial, software):
        self.make = str(make).replace(' ','.').upper()
        self.model = str(model).replace(' ','.').upper()
        self.serial = str(serial).upper()
        self.software = str(software).split('(')[0].replace(' ', '.').upper()

    def printInfo(self):
        print('Camera Make:     {}'.format(self.make))
        print('Camera Model:    {}'.format(self.model))
        print('Serial Number:   {}'.format(self.serial))
        print('Software:        {}'.format(self.software))

class MediaFileObject:

    def __init__(self, file, type, resolution, extension, captureDTS, cameraObject, creator):
        self.file = file
        self.type = type
        self.resolution = resolution
        self.extension = extension
        self.captureDTS = captureDTS
        self.device = cameraObject
        self.creator = creator

    def printInfo(self):
        print('Type:            {}'.format(self.type))
        print('Resolution:      {}'.format(self.resolution))
        print('Extension:       {}'.format(self.extension))
        print('Creator:         {}'.format(self.creator))
        print('Capture Date:    {}'.format(self.captureDTS))

        self.device.printInfo()


#----------------------------------------------------------------------------
#       Progress Bar
#----------------------------------------------------------------------------

# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-'):

    """
    Call in a loop to create terminal progress bar
    @params:
        iteration           - Required  :   current iteration (Int)
        total               - Required  :   total iterations (Int)
        prefix              - Optional  :   prefix string (Str)
        suffix              - Optional  :   suffix string (Str)
        decimals            - Optional  :   positive number of decimals in percent complete (Int)
        bar_length          - Optional  :   character length of bar (Int)
        complete_symbol     - Optional  :   character used to display completion progress
        incomplete_symbol   - Optional  :   character used to display remaining progress
    """

    str_format = "{0:." + str(decimals) + "f}"
    if total > 0:
        percents = str_format.format(100 * (iteration / float(total)))
        filled_length = int(round(bar_length * iteration / float(total)))
    else:
        percents = str_format.format(100)
        filled_length = 100


    bar = complete_symbol * filled_length + incomplete_symbol * (bar_length - filled_length)

    if prefix == '':
        prefix_a = ' ' * (len(str(total)) - len(str(iteration))) + str(iteration)
        prefix_b = str(total)
        prefix = '{} of {}'.format(prefix_a, prefix_b)


    sys.stdout.write('\r{}\t|{}| {}{} {}'.format(prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

#----------------------------------------------------------------------------
#       Get Directory Contents
#----------------------------------------------------------------------------

def getDirectoryContents(directory):
    """
    Get files from passed directory and all sub directories
    @params:
        directory           - Required  :   top directory to search for media files (Str)

    @returns
        directory_contents  :   list of file paths to media files
    """

    directory_contents = []

    # prune extra slashes from file path name
    while directory[-1] == '/':
        directory = directory[:-1]

    for root, directories, files in os.walk(directory):
        for filename in files:
            # only add files that are a valid media file type
            if isValidMediaFileType(filename):
                filePath = os.path.join(root, filename)
                directory_contents.append(filePath)
            elif not isIgnorableSystemFile(filename):
                print('>>> POSSIBLE MEDIA FILE:\t{}/{}'.format(root, filename))
                # logging.info('>>> POSSIBLE MEDIA FILE:\t%s/%s', root, filename)

    return directory_contents

def isValidMediaFileType(file):

    """
    Check if file is a media file, currently uses a hard coded list of image and video extensions
    @params:
        file    - Required  :   file to check extension (Str)
    """

    # get extension of file
    extensionToCheck = file.split('.')[-1].upper()

    # Weed out some sneaky dot files with valid file extensions
    if file[0] == '.':
        return False

    # 'Valid' media file type extensions
    validVideoFileExtensions = ['MOV', 'MP4', 'MPG', 'M4V', '3G2', '3GP', 'ASF', 'AVI', 'WMV']
    validImageFileExtensions = ['JPG', 'JPEG', 'PNG', 'TIF', 'TIFF', 'CR2', 'BMP', 'GIF', 'DNG', 'ARW']

    if extensionToCheck in validVideoFileExtensions:
        return True

    elif extensionToCheck in validImageFileExtensions:
        return True

    else:
        return False

def isIgnorableSystemFile(file):
    """
    Check if a file is a known ignorable file type
    @params:
        file    - Required  :   file to check extension (Str)
    """

    # get extension of file
    extensionToCheck = file.split('.')[-1].upper()

    # 'Valid' media file type extensions
    ignorableSystemFiles = ['INI', 'DS_STORE', 'DB', 'TEMP', 'INFO', 'PLIST', 'CTG', 'ATTR', 'TMP', 'WTC']

    if extensionToCheck in ignorableSystemFiles:
        return True
    else:
        return False


#----------------------------------------------------------------------------
#       Get EXIF tags
#----------------------------------------------------------------------------

#   pretty print a dictionary in key value pairs, well spaced
def prettyPrintDict(inputDictionary):
    longestKey = 0

    for key in inputDictionary:
        if len(key) > longestKey:
            longestKey = len(key)

    sortedDict = sorted(inputDictionary.items())
    for key, value in sortedDict:
        spacesNeeded = longestKey - len(key) + 4
        spaces = ' ' * spacesNeeded
        print('{}{}{}'.format(key, spaces, value))
        # logging.info('%s%s%s', key, spaces, value)

    return True

def get_exifs(file):

    exif_data = pyexifinfo.get_json(file)

    if len(exif_data) < 1:
        print('>>> this file has no exif data')
        # logging.warning('>>> this file has no exif data')
        dataDict = {}
    else:
        # return a sorted dictionary of all exif tag, value pairs
        dataDict = dict(sorted(exif_data[0].items()))
    return dataDict


#----------------------------------------------------------------------------
#       Get Camera Object
#----------------------------------------------------------------------------

#   clean up camera information for file naming
def cameraObjectCleaner(cameraObject):

    # cameraObject.printInfo()

    # special cases for known cameras
    # adjustments for Apple cameras, (iPhones, iPads, etc)
    if cameraObject.make.upper() == 'APPLE':
        cameraObject.make = 'Apple'
        cameraObject.model = cameraObject.model
        cameraObject.serial = cameraObject.serial
        cameraObject.software = 'iOS'
        # cameraObject.printInfo()

    #   adjustements for Canon cameras
    if cameraObject.make.upper() == 'CANON':
        cameraObject.make = cameraObject.make
        cameraObject.model = cameraObject.model[6:]
        cameraObject.serial = cameraObject.serial
        cameraObject.software = 'NONE'
        # cameraObject.printInfo()

    return cameraObject

#   sorts out camera information and returns a camera object
def getCameraObject(exifData):
    #   we want make, model, serial number, software
    cameraMake = 'NONE'
    cameraModel  = 'NONE'
    cameraSerial = 'NONE'
    softwareName = 'NONE'

    #   get cameraMake metadata
    try:
        cameraMake = exifData['XMP:Make']
    except:
        try:
            cameraMake = exifData['EXIF:Make']
        except:
            try:
                cameraMake = exifData['QuickTime:Make']
            except:
                pass

    #   get cameraModel metadata
    try:
        cameraModel = exifData['XMP:Model']
    except:
        try:
            cameraModel = exifData['EXIF:Model']
        except:
            try:
                cameraModel = exifData['QuickTime:Model']
            except:
                pass

    #   get software metadata
    try:
        softwareName = exifData['EXIF:Software']
    except:
        pass

    #   get camera serial Number
    try:
        cameraSerial = exifData['EXIF:SerialNumber']
    except:
        # sony camera exception
        try:
            cameraSerial = exifData['XML:DeviceSerialNo']
        except:

            pass


    #   build CameraObject
    cameraObject = CameraObject(cameraMake, cameraModel, cameraSerial, softwareName)

    #   clean camera object with known metadata tag 'fixes'
    cameraObject = cameraObjectCleaner(cameraObject)

    return cameraObject


#----------------------------------------------------------------------------
#       Get Capture Date and Time Stamp
#----------------------------------------------------------------------------

def getCaptureDTS(exifData, mediaType):

    # prettyPrintDict(exifData)
    dateTimeTags = {}

    for k, v in exifData.items():
        if 'date' in k.lower() and 'composite:' not in k.lower() and 'icc' not in k.lower():
            # dateTimeTags[k] = v.split('.')[0].split('-')[0]

            dt = v.split('.')[0].split('-')[0]

            try:
                dt = datetime.strptime(dt, '%Y:%m:%d %H:%M:%S')

                dateTimeTags[k] = dt
            except:
                pass

    captureDTS = min(dateTimeTags.values())

    return captureDTS


#----------------------------------------------------------------------------
#       Get Media File Object
#----------------------------------------------------------------------------

#   uses information from exifData to create a MediaFileObject if possible
def getMediaFileObject(file, creatorName=getuser()):

    # if the file is a valid media file type, else skip all this
    if isValidMediaFileType(file):

        # get exifTags into a dictionary
        exif_data = get_exifs(file)

        # pretty print exif tags
        # prettyPrintDict(exif_data)

        # get media type from 'File:MIMEType' value, (video or image)
        mediaType = exif_data['File:MIMEType'].split('/')[0].upper()

        # get file extension from 'File:FileTypeExtension' value
        fileExtension = exif_data['File:FileTypeExtension'].upper()

        # # get DateTimeObject for file
        captureDTS = getCaptureDTS(exif_data, mediaType)

        # get CameraObject for file
        cameraObject = getCameraObject(exif_data)

        # get creatorName for file
        creator = creatorName.lower()

        # get resolution
        resolution =  'ORIGINAL'
        try:
            resolution = exif_data['MakerNotes:Quality'].upper()
            resolution = resolution.replace("N/A","ORIGINAL")
        except:
            pass


        # video resolution set to widthxheight in pixels
        if mediaType == 'VIDEO':

            try:
                resolution = exif_data['Composite:ImageSize']
            except:
                pass

            try:
                # QuickTime:TrackDuration
                if ' s' in exif_data['QuickTime:TrackDuration'] and 'apple' in cameraObject.make.lower():

                    clip_duration = int(exif_data['QuickTime:TrackDuration'].split('.')[0])

                    if clip_duration < 10 and captureDTS.year > 2015:
                        mediaType = '1SE'

                    software = int(str(exif_data['QuickTime:Software']).split('.')[0])
                    frame_rate = float(exif_data['QuickTime:VideoFrameRate'])
                    if software >= 9 and frame_rate < 35.0 and clip_duration < 4:
                        mediaType = 'LIVE'

                else:
                    clip_duration = int(exif_data['QuickTime:TrackDuration'].split('.')[0])
                    if clip_duration < 10 and captureDTS.year > 2015:
                        mediaType = '1SE'
                try:
                    if exif_data['QuickTime:ComApplePhotosCaptureMode'].lower() == 'time-lapse':
                        mediaType = '1SE'
                except:
                    pass
            except:
                pass



        # init MediaFileObject
        mediaFileObject = MediaFileObject(file,
                                            mediaType,
                                            resolution,
                                            fileExtension,
                                            captureDTS,
                                            cameraObject,
                                            creator)

        # update resolution, from file name
        if mediaFileObject.extension.upper() in ['DNG', 'CR2', 'ARW']:
            mediaFileObject.resolution = 'RAW'

        # correct model for drone
        if mediaFileObject.device.model.upper() in ['FC220', 'FC220-SE']:
            mediaFileObject.device.model = 'MAVIC.PRO'

        return mediaFileObject

    else:
        print('>>> could not create MediaFileObject from {}, not a valid media file type'.format(file))
        # logging.warning('>>> could not create MediaFileObject from %s, not a valid media file type', file)
        return False


#----------------------------------------------------------------------------
#       File Name Formatting
#----------------------------------------------------------------------------

def make_import_file_name(mediaFileObject, file_counter, destination_directory):

    # assemble file name
    MEDIA_FILE_TYPE     = mediaFileObject.type
    RESOLUTION          = mediaFileObject.resolution
    MAKE                = mediaFileObject.device.make
    MODEL               = mediaFileObject.device.model
    SERIAL              = mediaFileObject.device.serial
    CAPTURE_DATE        = mediaFileObject.captureDTS.strftime('%Y%m%d')
    CAPTURE_TIME        = mediaFileObject.captureDTS.strftime('%H%M%S')
    USERNAME            = mediaFileObject.creator
    EXT                 = mediaFileObject.extension

    if RESOLUTION == 'THUMB':
        destination_file_path = '{}/{}/{}.{}/{}/'.format(destination_directory,
                                                            RESOLUTION,
                                                            MAKE, MODEL,
                                                            CAPTURE_DATE)
    else:
        destination_file_path = '{}/{}/{}/{}.{}/{}/'.format(destination_directory,
                                                            MEDIA_FILE_TYPE,
                                                            RESOLUTION,
                                                            MAKE, MODEL,
                                                            CAPTURE_DATE)

    destination_file_name = '{}.{}.{}.{}.{}.{}'.format(USERNAME,
                                                        SERIAL,
                                                        CAPTURE_DATE,
                                                        CAPTURE_TIME,
                                                        file_counter,
                                                        EXT)

    # ensure file path exists
    if not os.path.exists(destination_file_path):
        os.makedirs(destination_file_path)

    return destination_file_path, destination_file_name

def make_archive_file_name(mediaFileObject, destination_directory):

    # assemble file name
    MEDIA_FILE_TYPE = mediaFileObject.type
    CAPTURE_YEAR    = mediaFileObject.captureDTS.strftime('%Y')
    CAPTURE_MONTH   = mediaFileObject.captureDTS.strftime('%m')
    CAPTURE_DATE    = mediaFileObject.captureDTS.strftime('%Y%m%d')
    CAPTURE_TIME    = mediaFileObject.captureDTS.strftime('%H%M%S')
    USERNAME        = mediaFileObject.creator
    EXT             = mediaFileObject.extension

    destination_file_path = '{}/{}/{}/{}.{}/'.format(destination_directory,
                                                    MEDIA_FILE_TYPE,
                                                    CAPTURE_YEAR,
                                                    CAPTURE_YEAR, CAPTURE_MONTH)

    file_counter = '0001'
    destination_file_name = '{}.{}.{}.{}.{}'.format(CAPTURE_DATE,
                                                    CAPTURE_TIME,
                                                    USERNAME,
                                                    file_counter,
                                                    EXT)

    # if file extists, increment counter and try again


    while os.path.isfile('{}{}'.format(destination_file_path, destination_file_name)):

        # get current file_counter
        currentCounter = int(destination_file_name.split('.')[-2])

        # if file exists, increment counter and zero pad
        currentCounter += 1
        currentCounter = str(currentCounter).zfill(4)

        destination_file_name = '{}.{}.{}.{}.{}'.format(CAPTURE_DATE,
                                                        CAPTURE_TIME,
                                                        USERNAME,
                                                        currentCounter,
                                                        EXT)

    # ensure file path exists
    if not os.path.exists(destination_file_path):
        os.makedirs(destination_file_path)

    return destination_file_path, destination_file_name


#----------------------------------------------------------------------------
#       Making Thumbnails
#----------------------------------------------------------------------------

def make_thumb(mediaFileObject, outfile, thumb_size=(1080,1080), thumb_file_type='JPEG'):

    infile = mediaFileObject.file

    # try to read raw file
    try:
        with rawpy.imread(infile) as raw:
            rgb = raw.postprocess()
            im = Image.fromarray(rgb)
    # non raw file
    except:
        im = Image.open(infile)

    # make thumbnail
    im.thumbnail(thumb_size)

    try:

        im.save(outfile, thumb_file_type)
    except:
        # print('Could not write thumbnail, copying original image...')
        shutil.copy2(mediaFileObject.file, outfile)

    # print('Thumbnail written to {}'.format(outfile))


# EOF
