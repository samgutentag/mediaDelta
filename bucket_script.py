#! /usr/bin/env python3

"""Bucket Script is a harken back to my time at ILM as a Location Match Mover.

This module collects source image and video files generated by Canon and/or
Sony devices and imports them into specified file structures for import,
culling, tagging, sorting, and archiving media files.


This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

"""


__authors__ = ["Sam Gutentag"]
__email__ = "developer@samgutentag.com"
__date__ = "2019/09/13"
__deprecated__ = False
__license__ = "GPLv3"
__maintainer__ = "Sam Gutentag"
__status__ = "Production"
__version__ = "1.1.0"
# "Prototype", "Development", "Production", or "Legacy"


import argparse
import os
import shutil
from datetime import datetime, timezone
import getpass

import pyexifinfo
from tqdm import tqdm


def get_arguments():
    """Parse command line arguments with argparse."""
    parser = argparse.ArgumentParser(description="Import Media from Media Cards or File Directories")

    parser.add_argument("-s", "--source_dir",
                        dest="source_dir", required=True,
                        help=("Top level directory to search for media files, recursive"),
                        metavar="SOURCE_DIR")

    parser.add_argument("-t", "--target_dir",
                        dest="target_dir", required=True,
                        help=("Top level directory to organize collected files into"),
                        metavar="TARGET_DIR")

    parser.add_argument("-mode", "--bucket_mode",
                        dest="bucket_mode", required=False,
                        default="i",
                        help=("bucketing mode, supports (i)mport and (a)rchive, will use import by default"),
                        metavar="BUCKET_MODE")

    parser.add_argument("-mv", "--move_only",
                        action="store_true", required=False,
                        default=False,
                        help=("If passed, files are moved instead of copied."))

    parser.add_argument("-a", "--artist",
                        dest="artist", required=False,
                        default=getpass.getuser(),
                        help=("Name of Artist, lowercase no spaces, to tag in exif data, overwrites existing "))

    args = vars(parser.parse_args())

    return args


def get_media_files(search_dir=None, image_extensions=[], video_extensions=[], ignore_paths=[]):
    """Collect lists of media files found under a given source directory.

    Parameters:
    search_dir (string): root level directory to search for file
    image_extensions (list): list of accepted image file extensions
    video_extensions (list): list of accepted video file extensions
    ignore_paths (list): ignore files with absolute paths that include any of these sub directories

    Returns:
    [image_files, video_files, other_files]
    """
    image_files = []
    video_files = []
    other_files = []

    for root, dirs, files in os.walk(search_dir):

        for f in files:

            # get file absolute path
            file_abs_path = os.path.abspath(os.path.join(root, f))

            # check for ignore sub paths
            do_ignore = False
            if len(ignore_paths) > 0:
                # check each ignore path until any ignore is found
                for ignore_path in ignore_paths:
                    if ignore_path in file_abs_path:
                        do_ignore = True
                        break

            # extract file extension, format uppercase
            file_ext = os.path.splitext(f)[-1].upper()

            # append absolute filepath to lists depending on file time
            if file_ext in image_extensions and not do_ignore:
                image_files.append(file_abs_path)
            elif file_ext in video_extensions and not do_ignore:
                video_files.append(file_abs_path)
            else:
                other_files.append(file_abs_path)

    return [sorted(image_files), sorted(video_files), sorted(other_files)]


def parse_sony_exif(exif_data={}, artist=getpass.getuser()):
    """Specialized parsing for Sony Devices. Built with a6400 target in mind."""
    # print("file is from a sony device!")
    file_extension = exif_data["File:FileType"]

    file_type = exif_data["File:MIMEType"].split("/")[0]

    if file_type == "video":
        source_device = f"{exif_data['XML:DeviceModelName']}"
        capture_date = exif_data["XML:CreationDateValue"]
        quality = exif_data["QuickTime:VideoSize"]

    elif file_type == "image":
        artist = exif_data["EXIF:Artist"]
        source_device = f"{exif_data['MakerNotes:SonyModelID']}"
        capture_date = exif_data["Composite:SubSecCreateDate"]
        quality = exif_data["File:FileType"]

    # remove dashes from source_device
    source_device = source_device.replace("-", "")

    data = {"device_make": "Sony",
            "file_extension": file_extension,
            "file_type": file_type,
            "artist": artist,
            "source_device": source_device,
            "capture_date": capture_date,
            "quality": quality}

    return data


def parse_canon_exif(exif_data={}, artist=getpass.getuser()):
    """Specialized parsing for Canon Devices. Built with a6400 target in mind."""
    # print("file is from a canon device!")
    file_extension = exif_data["File:FileType"]

    file_type = exif_data["File:MIMEType"].split("/")[0]

    if file_type == "video":
        artist = exif_data["QuickTime:Author"]
        quality = exif_data["Composite:ImageSize"]

    elif file_type == "image":
        artist = exif_data["EXIF:Artist"]
        quality = exif_data["File:FileType"]

    # source device
    source_device = exif_data["EXIF:Model"]
    source_device = source_device.replace("Canon", "")

    # capture date
    capture_date = exif_data["Composite:SubSecDateTimeOriginal"]
    capture_date_tz = exif_data["MakerNotes:TimeZone"]
    capture_date = f"{capture_date}{capture_date_tz}"

    data = {"device_make": "Canon",
            "file_extension": file_extension,
            "file_type": file_type,
            "artist": artist,
            "source_device": source_device,
            "capture_date": capture_date,
            "quality": quality}

    return data


def format_import_path(exif_data={}, target_dir=""):
    # format import filename
    """
    import stages files by
      /TARGET_DIR/IMPORT/<FILE_TYPE>/<QUALITY>/<YYYYMMDD.HH>/
      <artist>.<SOURCE_DEVICE>.<YYYYMMDD>.<HHmmss>.<ms>.<extension>
    """
    file_counter = 1
    import_filename = (f"{exif_data['artist']}."
                       f"{exif_data['device_make']}."
                       f"{exif_data['source_device']}."
                       f"{exif_data['capture_utc'].strftime('%Y%m%d.%H%M%S')}."
                       f"{file_counter:04}"
                       )

    import_filename = f"{import_filename.lower()}.{exif_data['file_extension']}"

    import_filepath = os.path.join(target_dir, "IMPORT",
                                   exif_data["file_type"].upper(),
                                   exif_data["quality"].upper(),
                                   exif_data['capture_utc'].strftime("%Y%m%d"),
                                   import_filename)
    # ensure we are not duplicating files, increment counter file with this name already exists
    while os.path.exists(import_filepath):
        # increment counter
        file_counter += 1

        # split filepath into tokens on dots
        tokens = import_filepath.split(".")
        # replace counter token with incremented counter
        tokens[-2] = f"{file_counter:04}"

        # reconstruct filepath from tokens
        import_filepath = ".".join(tokens)

    return import_filepath


def format_archive_path(exif_data={}, target_dir=""):
    """
    archive locates files by
      /TARGET_DIR/IMPORT/<FILE_TYPE>/<YYYY>/<YYYY.MM>/
      <YYYYMMDD>.<HHmmss>.<artist>.<counter>.<extension>
    """
    file_counter = 1
    archive_filename = (f"{exif_data['capture_utc'].strftime('%Y%m%d.%H%M%S')}."
                        f"{exif_data['artist']}."
                        f"{file_counter:04}"
                        )

    archive_filename = f"{archive_filename.lower()}.{exif_data['file_extension']}"

    archive_filepath = os.path.join(target_dir, "ARCHIVE",
                                    exif_data["file_type"].upper(),
                                    exif_data['capture_utc'].strftime("%Y/%Y%m"),
                                    archive_filename)
    # ensure we are not duplicating files, increment counter file with this name already exists
    while os.path.exists(archive_filepath):
        # increment counter
        file_counter += 1

        # split filepath into tokens on dots
        tokens = archive_filepath.split(".")
        # replace counter token with incremented counter
        tokens[-2] = f"{file_counter:04}"

        # reconstruct filepath from tokens
        archive_filepath = ".".join(tokens)

    return archive_filepath


def bucket(source_file=None, target_dir="", bucket_mode="i", move_only=False, artist=getpass.getuser()):
    """Use image exif data to copy/move source file to target directory

    Parameters:
    source_file (string): absolute path of source file to be bucketed
    target_dir (string): top level directory to bucket files into
    bucket_mode (string): (i)mport and (a)rchive, strucutes filepaths and filenames
    move_only (bool): default is to copy source file, if True, this will move the source file
    artist (string): the username of the artist, used when exif data can not be found or does not exist
    """

    # get exif data from file
    exif_json = pyexifinfo.get_json(source_file)

    # convert to dictionary
    exif_dict = dict(sorted(exif_json[0].items()))

    # exif formatting is manufacturer specific and media type specific
    # get device make
    try:
        device_make = exif_dict["EXIF:Make"]
    except KeyError:
        device_make = exif_dict["XML:DeviceManufacturer"]
    device_make = device_make.title()

    # sony handling, written for a6400
    if device_make == "Sony":
        exif_data = parse_sony_exif(exif_data=exif_dict, artist=artist)

    # canon handling, written for EOS 7D Mark II
    elif device_make == "Canon":
        exif_data = parse_canon_exif(exif_data=exif_dict, artist=artist)

    # format all text to uppercase and replace spaces with dots
    exif_data["artist"] = exif_data["artist"].replace(" ", "")
    exif_data["source_device"] = exif_data["source_device"].replace(" ", "")

    # formatting datetime into a datetime obect
    exif_data["capture_date"] = f"{exif_data['capture_date'][:-3]}00"
    try:
        exif_data["capture_date"] = datetime.strptime(exif_data["capture_date"], "%Y:%m:%d %H:%M:%S%z")
    except ValueError:
        exif_data["capture_date"] = datetime.strptime(exif_data["capture_date"], "%Y:%m:%d %H:%M:%S.%f%z")

    # convert to UTC
    exif_data["capture_utc"] = exif_data["capture_date"].astimezone(timezone.utc)

    # format import filepath
    if bucket_mode == "i":
        target_filepath = format_import_path(exif_data=exif_data,
                                             target_dir=target_dir)

    # format archive filepath
    elif bucket_mode == "a":
        target_filepath = format_archive_path(exif_data=exif_data,
                                              target_dir=target_dir)

    # ensure target directory exists
    full_target_dir = os.path.dirname(target_filepath)
    if not os.path.isdir(full_target_dir):
        os.makedirs(full_target_dir)

    if move_only:
        shutil.move(source_file, target_filepath)
    else:
        shutil.copy2(source_file, target_filepath)


def collect_files():
    """Collect and Process images files.

    bucket[source_filepath]: {"import_filepath": import_filepath,
                          "archive_filepath": archive_filepath}

    """
    args = get_arguments()
    print(args)

    # check bucketing mode
    args["bucket_mode"] = args["bucket_mode"][:1].lower()
    if args["bucket_mode"] not in ["a", "i"]:
        print(f"Invalide Bucketting mode {args['bucket_mode']} passed...")
        print(f"\tvalid options are (i)mport or (a)rchive.")

    video_extensions = [".3G2", ".3GP", ".ASF", ".AVI",
                        ".M4V", ".MOV", ".MP4", ".MPG",
                        ".WMV"]

    image_extensions = [".ARW", ".BMP", ".CR2", ".DNG",
                        ".GIF", ".JPEG", ".JPG", ".PNG",
                        ".TIF", ".TIFF"]

    images, videos, others = get_media_files(search_dir=args["source_dir"],
                                             image_extensions=image_extensions,
                                             video_extensions=video_extensions,
                                             ignore_paths=["THMBNL"])

    print(f">>>> Found {len(images)} image files")
    print(f">>>> Found {len(videos)} video files")

    # log other files to console for inspection
    print(f">>>> Found {len(others)} other files")
    for other_file in others:
        print(f"\t>>{other_file}")

    for image_file in tqdm(images, desc="Image Files", total=len(images), ncols=100):
        bucket(source_file=image_file, target_dir=args["target_dir"],
               bucket_mode=args["bucket_mode"],
               move_only=args["move_only"],
               artist=args["artist"])

    for video_file in tqdm(videos, desc="Video Files", total=len(videos), ncols=100):
        bucket(source_file=video_file, target_dir=args["target_dir"],
               bucket_mode=args["bucket_mode"],
               move_only=args["move_only"],
               artist=args["artist"])


if __name__ == "__main__":
    collect_files()
