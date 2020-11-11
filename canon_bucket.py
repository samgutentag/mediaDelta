#! /usr/bin/env python3

"""bucket script customized for sony a6400

specific version of bucket_script.py rewritten for only sony a6400 files
Inspiration from https://gutentag.co/google_python_docstrings
and https://gutentag.co/google_python_styleguide

Use CalVer versioning as described at https://calver.org/

"""

__authors__ = ["Sam Gutentag"]
__email__ = "developer@samgutentag.com"
__maintainer__ = "Sam Gutentag"
__version__ = "2020.07.29dev"
# "dev", "alpha", "beta", "rc1"

import argparse
import hashlib
import os
import shutil
from datetime import datetime

import pyexifinfo


def get_files(source_dir=None):
    """Short description of this function.

    Longer description of this function.

    Args:
        argument_name (type): description

    Returns:
        return_value (type): description

    Raises:
        ErrorType: description and cause

    """
    image_files = []
    video_files = []
    other_files = []

    # walk directory tree
    for root, dirs, files in os.walk(source_dir):

        # check each file
        for f in files:
            # construct absolute path to file
            file_path = os.path.abspath(os.path.join(root, f))

            # check file extension for type
            file_extension = os.path.splitext(file_path)[1]

            if file_extension in [".ARW"]:
                image_files.append(file_path)
            elif file_extension in [".MP4"]:
                video_files.append(file_path)
            else:
                other_files.append(file_path)

    # sort file sets
    image_files = sorted(image_files)
    video_files = sorted(video_files)
    other_files = sorted(other_files)

    return [image_files, video_files, other_files]


def compare_files(file_a, file_b):
    """compare two images for similarit

    Longer description of this function.

    Args:
        argument_name (type): description

    Returns:
        return_value (type): description

    Raises:
        ErrorType: description and cause

    """
    digests = []
    for filename in [file_a, file_b]:
        hasher = hashlib.md5()
        with open(filename, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
            a = hasher.hexdigest()
            digests.append(a)

    result = digests[0] == digests[1]

    return result


def format_filepath(input_file=None, media_type=None, destination_dir=None):
    """parse input image file for capture/creation date

    Read exif tags to find creation date of input media file. Will
    prioritze datetimes that include a timezone offset.

    Args:
        argument_name (type): description

    Returns:
        return_value (type): description

    Raises:
        ErrorType: description and cause

    """
    # parse file exif data to json object
    exif_json = pyexifinfo.get_json(input_file)[0]

    # convert to dictionary
    exif_dict = dict(exif_json)

    # get capture date - example `2020:07:29 16:44:57-07:00`
    if media_type == "IMAGE":
        capture_date = exif_dict["Composite:SubSecDateTimeOriginal"]
    elif media_type == "VIDEO":
        capture_date = exif_dict["XML:CreationDateValue"]
    else:
        return None

    # remove colon from timezone offset
    last_colon = capture_date.rfind(":")
    capture_date = capture_date[:last_colon] + capture_date[-2:]

    capture_datetime = datetime.strptime(capture_date, "%Y:%m:%d %H:%M:%S%z")

    # format filepath
    # dir -> /TARGET_DIR/IMPORT/<FILE_TYPE>/<YYYY>/<YYYY.MM>/
    # file -> <YYYYMMDD>.<HHmmss>.<artist>.<counter>.<extension>

    counter = 1
    archive_filepath = ""

    while os.path.exists(archive_filepath) or counter == 1:
        file_extension = os.path.splitext(input_file)[1]
        archive_timestamp = capture_datetime.strftime("%Y%m%d.%H%M%S")

        archive_filename = ".".join([archive_timestamp, "samgutentag", f"{counter:04d}"])
        archive_filename = f"{archive_filename}{file_extension}"

        archive_filepath = os.path.join(destination_dir,
                                        "ARCHIVE",
                                        media_type,
                                        capture_datetime.strftime("%Y"),
                                        capture_datetime.strftime("%Y.%m"),
                                        archive_filename)

        # if this file path already exists, compare images
        if os.path.exists(archive_filepath):
            comparison = compare_files(input_file, archive_filepath)
            if comparison:
                return None
        counter += 1

    return archive_filepath


# def parse_video_file(input_file=None, destination_dir=None):
#     """parse input image file for capture/creation date

#     Read exif tags to find creation date of input media file. Will
#     prioritze datetimes that include a timezone offset.

#     Args:
#         argument_name (type): description

#     Returns:
#         return_value (type): description

#     Raises:
#         ErrorType: description and cause

#     """
#     # parse file exif data to json object
#     exif_json = pyexifinfo.get_json(input_file)[0]

#     # convert to dictionary
#     exif_dict = dict(exif_json)

#     # get capture date - example `2020:07:29 16:44:57-07:00`
#     capture_date = exif_dict["XML:CreationDateValue"]

#     # remove colon from timezone offset
#     last_colon = capture_date.rfind(":")
#     capture_date = capture_date[:last_colon] + capture_date[-2:]

#     capture_datetime = datetime.strptime(capture_date, "%Y:%m:%d %H:%M:%S%z")

#     # format filepath
#     # dir -> /TARGET_DIR/IMPORT/<FILE_TYPE>/<YYYY>/<YYYY.MM>/
#     # file -> <YYYYMMDD>.<HHmmss>.<artist>.<counter>.<extension>

#     counter = 1
#     archive_filepath = ""

#     while os.path.exists(archive_filepath) or counter == 1:
#         file_extension = os.path.splitext(input_file)[1]
#         archive_timestamp = capture_datetime.strftime("%Y%m%d.%H%M%S")

#         archive_filename = ".".join([archive_timestamp, "samgutentag", f"{counter:04d}"])
#         archive_filename = f"{archive_filename}{file_extension}"

#         archive_filepath = os.path.join(destination_dir,
#                                         "ARCHIVE",
#                                         "VIDEO",
#                                         capture_datetime.strftime("%Y"),
#                                         capture_datetime.strftime("%Y.%m"),
#                                         archive_filename)
#         counter += 1

#     return archive_filepath


def sony_bucket(*args):
    """run sony bucket script

    Longer description of this function.

    Args:
        argument_name (type): description

    Returns:
        return_value (type): description

    Raises:
        ErrorType: description and cause

    """

    parser = argparse.ArgumentParser(description="Import Media from Sony Camera SD Card")

    parser.add_argument("-s", "--source_dir",
                        dest="source_dir", required=True,
                        help=("Top level directory to search for media files, recursive"),
                        metavar="SOURCE_DIR")

    parser.add_argument("-d", "--destination_dir",
                        dest="destination_dir", required=True,
                        help=("Top level directory to organize collected files into"),
                        metavar="DESTINATION_DIR")

    args = vars(parser.parse_args())

    image_files, video_files, other_files = get_files(source_dir=args["source_dir"])

    for image_file in image_files:
        # print(image_file)
        dest_path = format_filepath(input_file=image_file,
                                    media_type="IMAGE",
                                    destination_dir=args["destination_dir"])

        if dest_path is None:
            break

        dest_dir = os.path.dirname(os.path.abspath(dest_path))

        # ensure dest path exists
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        # copy file
        shutil.copy2(image_file, dest_path)

    for video_file in video_files:
        # print(image_file)
        dest_path = format_filepath(input_file=video_file,
                                    media_type="VIDEO",
                                    destination_dir=args["destination_dir"])

        if dest_path is None:
            break

        dest_dir = os.path.dirname(os.path.abspath(dest_path))

        # ensure dest path exists
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        # copy file
        shutil.copy2(video_file, dest_path)

    if len(other_files) > 0:
        print("Other Files found:")
        for i in other_files:
            print(f"\t{i}")

if __name__ == "__main__":
    sony_bucket()
