#! /usr/bin/env python

"""Sort media files by capture date."""

from getpass import getuser
from datetime import datetime
from tqdm import tqdm
import pyexifinfo
import argparse
import os
import shutil

__author__ = "Sam Gutentag"
__copyright__ = "Copyright 2019, Sam Gutentag"
__credits__ = ["Sam Gutentag"]
__license__ = "GPL"
__version__ = "0.2.0"
__maintainer__ = "Sam Gutentag"
__email__ = "developer@samgutentag.com"
__status__ = "Development"
# "Prototype", "Development", or "Production"


class CaptureDevice:
    """Object to store capture device information."""

    def __init__(self, make, model, serial, software):
        """Initialize CaptureDevice object."""
        self.make = str(make).replace(" ", ".").upper()
        self.model = str(make).replace(" ", ".").upper()
        self.serial = str(serial).upper()

        software = str(software).split("(")[0].replace(" ", ".").upper()
        self.software = software

    def pretty_print(self, indent="\t"):
        """Output object attributes to console."""
        print(f"{indent}device_make       {self.make}")
        print(f"{indent}device_model      {self.model}")
        print(f"{indent}device_serial     {self.serial}")
        print(f"{indent}device_software   {self.software}")


class Bucket:
    """Main object of this tool.

    Holds all information needed to make a file archive or import

    Parameters:
    input_file (string): input media file to be processed
    destination_dir (string): destination root directory for import/archive
    username (string): user that created the file, defaults to current user

    """

    def __init__(self, input_file, destination_dir, username):
        """Initialize the Bucket Object."""
        self.input_file = input_file
        self.extension = input_file.split(".")[-1].lower()
        self.destination_dir = str(destination_dir)
        self.username = str(username).lower()

        self.process_file()

    def process_file(self):
        """Process file to get other attributes."""
        self.read_exif_tags()
        self.get_capture_device()
        self.get_capture_dt()
        self.get_media_type()
        self.get_media_resolution()

        # update media type and resolution for videos
        if self.media_type.lower() == "video":
            self.update_media_data()

        self.set_import_filepath()
        self.set_archive_filepath()

    def pretty_print(self, indent="\t"):
        """Output object attributes to console."""
        print(f"{indent}input_file        {self.input_file}")
        print(f"{indent}extension         {self.extension}")
        print(f"{indent}destination_dir   {self.destination_dir}")
        print(f"{indent}import_filepath   {self.import_filepath}")
        print(f"{indent}archive_filepath  {self.archive_filepath}")

        print(f"{indent}username          {self.username}")
        print(f"{indent}capture_dt        {self.capture_dt}")
        print(f"{indent}media_type        {self.media_type}")
        print(f"{indent}media_resolution  {self.media_resolution}")

        self.capture_device.pretty_print(indent=indent*2)

        print(f"{indent}exif_tags         {self.exif_tags}")

    def read_exif_tags(self):
        """Read exif tags from source file."""
        self.exif_tags = pyexifinfo.get_json(self.input_file)[0]

    def get_capture_device(self):
        """Find capture device/software."""
        make, model, serial, software = None, None, None, None

        # get camera_make
        for tag in ["XMP:Make", "EXIF:Make", "QuickTime:Make"]:
            try:
                make = self.exif_tags[tag]
                break
            except Exception:
                pass

        # get camera_model
        for tag in ["XMP:Model", "EXIF:Model", "QuickTime:Model"]:
            try:
                model = self.exif_tags[tag]
                break
            except Exception:
                pass

        # get camera_serial
        for tag in ["XMP:DeviceSerialNo", "EXIF:SerialNumber"]:
            try:
                serial = self.exif_tags[tag]
                break
            except Exception:
                pass

        # get software_name
        for tag in ["XMP:Software", "EXIF:Software", "QuickTime:Software"]:
            try:
                software = self.exif_tags[tag]
                break
            except Exception:
                pass

        self.capture_device = CaptureDevice(make, model, serial, software)

    def get_capture_dt(self):
        """Find capture/creation date of media file from exif tags."""
        datetime_tags = []

        for k, v in self.exif_tags.items():

            k = k.lower()
            if "date" in k and "composite:" not in k and "icc" not in k:

                dt = v.split("-")[0]
                dt = datetime.strptime(dt, "%Y:%m:%d %H:%M:%S")
                datetime_tags.append(dt)

        capture_datetime = min(datetime_tags)

        self.capture_dt = capture_datetime

    def get_media_type(self):
        """Attempt to find media type in exif tags."""
        try:
            media_type = self.exif_tags["File:MIMEType"].split("/")[0].upper()
            self.media_type = media_type
        except Exception:
            self.media_type = None

    def get_media_resolution(self):
        """Categorize resolution of media file."""
        resolution = "ORIGINAL"
        try:
            resolution = self.exif_tags["MakerNotes:Quality"].upper()
            resolution = resolution.replace("N/A", "ORIGINAL")
        except Exception:
            pass

        if self.media_type == "VIDEO":
            try:
                resolution = self.exif_data["Composite:ImageSize"]
            except Exception:
                pass

        self.media_resolution = resolution

    def update_media_data(self):
        """Update Media File resolution and media type."""
        pass

        self.resolution = self.exif_tags["Composite:ImageSize"]

        cond_a = " s" in self.exif_tags["QuickTime:TrackDuration"]
        cond_b = "apple" in self.capture_device.device_make
        if cond_a and cond_b:
            clip_duration = int(self.exif_tags["QuickTime:TrackDuration"].split(".")[0])

            if clip_duration < 10 and self.capture_dt.year > 2015:
                self.media_type = "1SE"

            software = int(str(self.exif_tags["QuickTime:Software"]).split(".")[0])
            frame_rate = float(self.exif_tags["QuickTime:VideoFrameRate"])
            if software >= 9 and frame_rate < 35.0 and clip_duration < 4:
                self.media_type = "LIVE"




    def set_import_filepath(self):
        """Format import filepath string."""
        # directory
        capture_dt_str = datetime.strftime(self.capture_dt, "%Y%m%d.%H%M%S")

        device_id = f"{self.capture_device.make}.{self.capture_device.model}"

        import_directory = "/".join([self.destination_dir, self.media_type,
                                     self.media_resolution,
                                     device_id, capture_dt_str])

        # filename
        capture_dt_str = datetime.strftime(self.capture_dt, "%Y%m%d.%H%M%S")
        file_counter = "0001"
        import_filename = ".".join([self.username, self.capture_device.serial,
                                    capture_dt_str, file_counter,
                                    self.extension])

        import_filepath = f"{import_directory}/{import_filename}"

        # increment counter if filename exists
        while os.path.exists(import_filepath):
            current_counter = int(import_filename.split(".")[-2])
            current_counter += 1
            file_counter = str(current_counter).zfill(4)

            import_filename = ".".join([self.username,
                                        self.capture_device.serial,
                                        capture_dt_str, file_counter,
                                        self.extension])

            import_filepath = f"{import_directory}/{import_filename}"

        self.import_filepath = import_filepath

    def set_archive_filepath(self):
        """Format archive filepath string."""
        # directory
        capture_year = datetime.strftime(self.capture_dt, "%Y")
        capture_year_month = datetime.strftime(self.capture_dt, "%Y.%m")

        archive_directory = "/".join([self.destination_dir, self.media_type,
                                      capture_year, capture_year_month])

        # filename
        capture_dt_str = datetime.strftime(self.capture_dt, "%Y%m%d.%H%M%S")
        file_counter = "0001"
        archive_filename = ".".join([capture_dt_str, self.username,
                                     file_counter, self.extension])

        archive_filepath = f"{archive_directory}/{archive_filename}"

        # increment counter if filename exists
        while os.path.exists(archive_filepath):
            current_counter = int(archive_filename.split(".")[-2])
            current_counter += 1
            file_counter = str(current_counter).zfill(4)

            archive_filename = ".".join([capture_dt_str, self.username,
                                         file_counter, self.extension])
            archive_filepath = f"{archive_directory}/{archive_filename}"

        self.archive_filepath = archive_filepath


def get_arguments():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=("Import Media Files from "
                                                  "Media Card or External "
                                                  "Hard Drive."))

    parser.add_argument("-u", "--username", dest="username",
                        required=False, default=getuser(),
                        help="File prefix username", metavar="USERNAME")

    parser.add_argument("-a", "--archive", action="store_true",
                        default=False,
                        help=("If Passed, script put files in archive folder "
                              "structure."))

    parser.add_argument("-s", "--source", dest="source_dir",
                        required=True,
                        help="Source directory of media files.")

    parser.add_argument("-d", "--destination", dest="destination_dir",
                        required=True,
                        help="Destination root directory for media files.")

    # parser.add_argument("-thumb", "--make-thumbnails", action="store_true",
    #                     default=False, required=False,
    #                     help="Generate 720px thumbnail files.")

    parser.add_argument("-move", "--move-only", action="store_true",
                        default=False, required=False,
                        help="Move files to target folder instead of copying.")

    args = vars(parser.parse_args())

    return args


def get_media_files(search_dir=None, image_extensions=[], video_extensions=[]):
    """Get all files below a top level directory.

    Parameters:
    search_dir (string): top level directory to search from
    image_extensions (list of string): filter files with extension in this list
    video_extensions (list of string): filter files with extension in this list

    """
    # ensure uppercase extension lists
    image_extensions = [x.upper() for x in image_extensions]
    video_extensions = [x.upper() for x in video_extensions]

    image_file_list = []
    video_file_list = []
    non_media_files = []

    for root, dirs, files in os.walk(search_dir):
        for file in files:
            # check file extension
            ext = file.split(".")[-1]
            abs_filepath = f"{root}/{file}"

            if ext.upper() in image_extensions:
                image_file_list.append(abs_filepath)

            elif ext.upper() in video_extensions:
                video_file_list.append(abs_filepath)
            else:
                non_media_files.append(abs_filepath)

    return [image_file_list, video_file_list, non_media_files]


def bucket():
    """Collect and Process images files."""
    args = get_arguments()

    video_extensions = ["3G2", "3GP", "ASF", "AVI",
                        "M4V", "MOV", "MP4", "MPG",
                        "WMV"]

    image_extensions = ["ARW", "BMP", "CR2", "DNG",
                        "GIF", "JPEG", "JPG", "PNG",
                        "TIF", "TIFF"]

    images, videos, others = get_media_files(search_dir=args["source_dir"],
                                             image_extensions=image_extensions,
                                             video_extensions=video_extensions)

    print(f"Script found {len(images)} image files.")
    print(f"Script found {len(videos)} video files.")
    print(f"Script found {len(others)} other files.")

    # archive will skip over THUMB directories
    if args["archive"]:
        images = [f for f in images if "/THUMB/" not in f]
        videos = [f for f in videos if "/THUMB/" not in f]
        others = [f for f in others if "/THUMB/" not in f]

    # process files
    for image_file in tqdm(sorted(images)[:100]):

        try:
            bucket_image = Bucket(image_file,
                                  destination_dir=args["destination_dir"],
                                  username=args["username"])

            # bucket_image.pretty_print()
        except ValueError as ve:
            print(ve)

        # set destination path
        if args["archive"]:
            destination_path = bucket_image.archive_filepath
        else:
            destination_path = bucket_image.import_filepath

        # ensure destination directory exists
        destination_dir = os.path.dirname(destination_path)
        if not os.path.isdir(destination_dir):
            os.makedirs(destination_dir)

        # copy or move file
        if args["move_only"]:
            shutil.move(bucket_image.input_file, destination_path)
        else:
            shutil.copy2(bucket_image.input_file, destination_path)


if __name__ == "__main__":
    bucket()
