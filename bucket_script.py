#! /usr/bin/env python3

"""Bucket Script is a harken back to my time at ILM as a Location Match Mover.

This module collects source image and video files generated by Canon and/or
Sony devices and imports them into specified file structures for import,
culling, tagging, sorting, and archiving media files.

"""

__authors__ = ["Sam Gutentag"]
__email__ = "developer@samgutentag.com"
__maintainer__ = "Sam Gutentag"
__version__ = "2020.06.30dev"
# "dev", "alpha", "beta", "rc1"


import argparse
import getpass
import os
import re
import shutil
from datetime import datetime, timezone

import pyexifinfo
import pytz
from timezonefinder import TimezoneFinder
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
        try:
            artist = exif_data["EXIF:Artist"]
        except:
            pass

        try:
            source_device = f"{exif_data['MakerNotes:SonyModelID']}"
        except KeyError:
            source_device = f"{exif_data['EXIF:Model']}"

        # capture_date = exif_data["Composite:SubSecCreateDate"]
        capture_date = exif_data["EXIF:DateTimeOriginal"]
        capture_date_tz = exif_data["EXIF:OffsetTimeOriginal"]
        capture_date = f"{capture_date}{capture_date_tz}"

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
        try:
            artist = exif_data["QuickTime:Author"]
        except:
            pass
        quality = exif_data["Composite:ImageSize"]

    elif file_type == "image":
        try:
            artist = exif_data["EXIF:Artist"]
        except:
            pass
        quality = exif_data["File:FileType"]

    # source device
    source_device = exif_data["EXIF:Model"]
    source_device = source_device.replace("Canon", "")

    # capture date
    try:
        capture_date = exif_data["Composite:SubSecDateTimeOriginal"]
    except KeyError:
        capture_date = exif_data["EXIF:DateTimeOriginal"]

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


def timezone_from_gps(gps_position="", capture_date="", tf=TimezoneFinder(in_memory=True)):
    """Bsic Lookup of timezone from gps coordinates

    Parameters:
    gps_coordinates (string): example 32 deg 12\' 7.60" N, 80 deg 41\' 8.19" W
    capture_date (string): example 2018:06:28 09:45:37
    tf (TimezoneFInder): a TimezoneFinder obejct

    Returns
    tz_offset (string): example "-07:00"
    """
    # extrac degrees, minutes, seconds
    dms_re = re.compile(r"\d+.?\d+")
    dms_matches = dms_re.findall(gps_position)

    # exrtact cardinal directions
    card_re = re.compile(r"[NWSE]")
    card_matches = card_re.findall(gps_position)

    # convert to coordinates
    latitude = float(dms_matches[0]) + float(dms_matches[1]) / 60 + float(dms_matches[2]) / (60 * 60)
    if card_matches[0] == 'S':
        latitude *= -1

    longitude = float(dms_matches[3]) + float(dms_matches[4]) / 60 + float(dms_matches[5]) / (60 * 60)
    if card_matches[1] == 'W':
        longitude *= -1

    try:
        # get timezone_name from lookup
        timezone_name = tf.timezone_at(lng=longitude, lat=latitude)

        # make timezone aware datetime
        capture_date = datetime.strptime(capture_date, "%Y:%m:%d %H:%M:%S")

        # get timezone from timesone name
        tz = pytz.timezone(timezone_name)

        # make aware string, parse out timezone offset, this is gross
        aware_datetime = str(capture_date.replace(tzinfo=tz))
        tz_string = f"{aware_datetime[-6:-3]}:{aware_datetime[-2:]}"

        return tz_string

    except:
        return "-00:00"


def parse_dji_exif(exif_data={}, artist=getpass.getuser()):
    """Specialized parsing for DJI Devices. Built with DJI Mavic Pro target in mind."""
    # print("file is from a DJI device!")
    file_extension = exif_data["File:FileType"]

    file_type = exif_data["File:MIMEType"].split("/")[0]

    if file_type == "video":
        quality = exif_data["Composite:ImageSize"]
        capture_date = exif_data["QuickTime:CreateDate"]
        source_device = exif_data["QuickTime:Model"].split("-")[0]

    elif file_type == "image":
        quality = exif_data["File:FileType"]
        capture_date = exif_data["EXIF:DateTimeOriginal"]
        try:
            source_device = exif_data["XMP:Model"]
        except:
            source_device = exif_data["EXIF:Model"]

    capture_date_tz = timezone_from_gps(gps_position=exif_data["Composite:GPSPosition"],
                                        capture_date=capture_date)

    capture_date = f"{capture_date}{capture_date_tz}"

    data = {"device_make": "DJI",
            "file_extension": file_extension,
            "file_type": file_type,
            "artist": artist,
            "source_device": source_device,
            "capture_date": capture_date,
            "quality": quality}

    return data


def parse_apple_exif(exif_data={}, artist=getpass.getuser()):
    """Specialized parsing for Apple Devices. Built with iPhone XS target in mind."""
    # print("file is from a apple device!")
    file_extension = exif_data["File:FileType"]

    file_type = exif_data["File:MIMEType"].split("/")[0]

    if file_type == "video":
        try:
            artist = exif_data["QuickTime:Author"]
        except:
            pass
        quality = exif_data["Composite:ImageSize"]

    elif file_type == "image":
        try:
            artist = exif_data["EXIF:Artist"]
        except:
            pass
        quality = exif_data["File:FileType"]

    # source device
    source_device = exif_data["EXIF:Model"]
    source_device = source_device.replace(" ", "")

    # capture date
    try:
        capture_date = exif_data["Composite:SubSecDateTimeOriginal"]
    except KeyError:
        capture_date = exif_data["EXIF:DateTimeOriginal"]

    try:
        capture_date_tz = timezone_from_gps(gps_position=exif_data["Composite:GPSPosition"],
                                        capture_date=capture_date)
    except:
        capture_date_tz = ""

    capture_date = f"{capture_date}{capture_date_tz}"

    # correct uploaded dates without timezones
    if capture_date.endswith("-08:00") or capture_date.endswith("-07:00"):
        pass
    # if not already set, defaults to california -07:00 timezone
    elif not capture_date.endswith("-00:00"):
        capture_date = f"{capture_date}-07:00"
    else:
        pass



    data = {"device_make": "Apple",
            "file_extension": file_extension,
            "file_type": file_type,
            "artist": artist,
            "source_device": source_device,
            "capture_date": capture_date,
            "quality": quality}

    return data


def check_image_match(imageA=None, imageB=None):

    # read imageA to rgb
    with open(imageA, "rb") as f1:
        imgA = f1.read()
    with open(imageB, "rb") as f2:
        imgB = f2.read()

    if imgA == imgB:
        return True
    else:
        return False


def format_import_path(source_file=None, exif_data={}, target_dir=""):
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

        if check_image_match(imageA=source_file, imageB=import_filepath):
            return None

        # increment counter
        file_counter += 1

        # split filepath into tokens on dots
        tokens = import_filepath.split(".")
        # replace counter token with incremented counter
        tokens[-2] = f"{file_counter:04}"

        # reconstruct filepath from tokens
        import_filepath = ".".join(tokens)

    return import_filepath


def format_archive_path(source_file=None, exif_data={}, target_dir=""):
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
                                    exif_data['capture_utc'].strftime("%Y/%Y.%m"),
                                    archive_filename)
    # ensure we are not duplicating files, increment counter file with this name already exists
    while os.path.exists(archive_filepath):

        if check_image_match(imageA=source_file, imageB=archive_filepath):
            return None

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

    # try:
    # get exif data from file
    exif_json = pyexifinfo.get_json(source_file)

    # convert to dictionary
    exif_dict = dict(sorted(exif_json[0].items()))

    # from pprint import pprint
    # pprint(exif_dict)

    try:
        # exif formatting is manufacturer specific and media type specific
        # get device make
        try:
            device_make = exif_dict["EXIF:Make"]
        except KeyError:
            try:
                device_make = exif_dict["XML:DeviceManufacturer"]
            except KeyError:
                try:
                    device_make = exif_dict["QuickTime:CompressorName"].split(" ")[0]
                except:
                    device_make = exif_dict["QuickTime:MajorBrand"].split(" ")[0]

        device_make = device_make.title()

        # sony handling, written for a6400
        if device_make == "Sony":
            exif_data = parse_sony_exif(exif_data=exif_dict, artist=artist)

        # canon handling, written for EOS 7D Mark II
        elif device_make == "Canon":
            exif_data = parse_canon_exif(exif_data=exif_dict, artist=artist)

        # dji handling, written for DJI Mavic Pro
        elif device_make == "Dji":
            exif_data = parse_dji_exif(exif_data=exif_dict, artist=artist)

        # apple handling, written for iPhone 11 Pro
        elif device_make == "Apple":
            exif_data = parse_apple_exif(exif_data=exif_dict, artist=artist)

        else:
            return source_file

        # format all text to uppercase and replace spaces with dots
        exif_data["artist"] = exif_data["artist"].replace(" ", "")
        exif_data["source_device"] = exif_data["source_device"].replace(" ", "")

        # formatting datetime into a datetime obect, remove colon in timezone offset
        exif_data["capture_date"] = f"{exif_data['capture_date'][:-3]}{exif_data['capture_date'][-2:]}"

        try:
            exif_data["capture_date"] = datetime.strptime(exif_data["capture_date"], "%Y:%m:%d %H:%M:%S%z")
        except ValueError:
            exif_data["capture_date"] = datetime.strptime(exif_data["capture_date"], "%Y:%m:%d %H:%M:%S.%f%z")

        # convert to UTC
        exif_data["capture_utc"] = exif_data["capture_date"].astimezone(timezone.utc)

        # format import filepath
        if bucket_mode == "i":
            target_filepath = format_import_path(source_file=source_file,
                                                 exif_data=exif_data,
                                                 target_dir=target_dir)
            if target_filepath is None:
                return "EXISTS"

        # format archive filepath
        elif bucket_mode == "a":
            target_filepath = format_archive_path(source_file=source_file,
                                                  exif_data=exif_data,
                                                  target_dir=target_dir)
            if target_filepath is None:
                return "EXISTS"

        # ensure target directory exists
        full_target_dir = os.path.dirname(target_filepath)
        if not os.path.isdir(full_target_dir):
            os.makedirs(full_target_dir)

        # print(f"source\t{source_file}")
        # print(f"target\t{target_filepath}\n")

        if move_only:
            shutil.move(source_file, target_filepath)
        else:
            shutil.copy2(source_file, target_filepath)

        return 1
    except Exception as e:
        print(f"\n\t{e}\t{source_file}")

        # from pprint import pprint
        # pprint(exif_dict)

        return "ERROR"


def collect_files():
    """Collect and Process images files.

    bucket[source_filepath]: {"import_filepath": import_filepath,
                          "archive_filepath": archive_filepath}

    """
    args = get_arguments()
    print(args)

    error_files = []
    existing_files = []

    # check bucketing mode
    args["bucket_mode"] = args["bucket_mode"][:1].lower()
    if args["bucket_mode"] not in ["a", "i"]:
        print(f"Invalide Bucketing mode {args['bucket_mode']} passed...")
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

    if len(images) > 0:
        for image_file in tqdm(images, desc="Image Files", total=len(images), ncols=100):
            bucket_status = bucket(source_file=image_file, target_dir=args["target_dir"],
                                   bucket_mode=args["bucket_mode"],
                                   move_only=args["move_only"],
                                   artist=args["artist"])

            if bucket_status == "ERROR":
                error_files.append(image_file)
            elif bucket_status == "EXISTS":
                existing_files.append(image_file)
            else:
                pass

    if len(videos) > 0:
        for video_file in tqdm(videos, desc="Video Files", total=len(videos), ncols=100):
            bucket_status = bucket(source_file=video_file, target_dir=args["target_dir"],
                                   bucket_mode=args["bucket_mode"],
                                   move_only=args["move_only"],
                                   artist=args["artist"])
            if bucket_status == "ERROR":
                error_files.append(video_file)
            elif bucket_status == "EXISTS":
                existing_files.append(video_file)
            else:
                pass

    if len(error_files) > 0:
        print(f"Could not process {len(error_files)} files...")
        error_files = sorted(error_files)
        for idx, err_file in enumerate(error_files):
            print(f"\t{idx + 1}\t{err_file}")

    if len(existing_files) > 0:
        print(f"Found {len(existing_files)} files that already existed at target...")
        existing_files = sorted(existing_files)
        for idx, exist_file in enumerate(existing_files):
            print(f"\t{idx + 1}\t{exist_file}")


if __name__ == "__main__":
    collect_files()
