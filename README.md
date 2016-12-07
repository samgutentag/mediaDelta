Assumptions

	First ExifTool should be installed on the host machine, it can be downloaded here
	http://www.sno.phy.queensu.ca/~phil/exiftool/

	pyexifinfo should be installed as an awesome python wrapper for it!

	https://github.com/guinslym/pyexifinfo

	> pip install -U pyexifinfo



Goal Sample Folder Structure

	photos
		extension
			YYYY.MM.DD
				cameraModel.artist.cameraSerial
					YYYYMMDD_HHmmSS.sss.extension


printExifTags.py
	prints all exif tags for a single file or a directory of files

cameraReporter.py
	generates a camera report of all files in a directory, or in a single file, and collects them in a dictionary that is easy to get counts for
