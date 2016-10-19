

Assumptions

	exifread package is installed on host machine, can be installed with pip

	> pip install exifread

Usage

	An example command would be

	> python getExifData.py -f /sampleDirectory/sampleImage.jpg -a $USER

	to get help on required and optional arguments use

	> python getExifData.py -h

Current Sample Folder Structure
	HardDrive
		DateCorrected
			Anchorage Square - San Francisco, CA, March 22, 2015
				20151029_IMG_0168.JPG
				20151029_IMG_0169.JPG
				20151029_IMG_0167.JPG
			April 13, 2013
				20151030_IMG_0230.JPG
			April 20, 2013
				20151030_IMG_0254.JPG



Goal Sample Folder Structure
	HardDrive
		Images
			2015
				03
					20150322120000_username_cameramodel.JPG
					20150322120100_username_cameramodel.JPG
					20150322120200_username_cameramodel.JPG
			2013
				04
					20130413120000_username_cameramodel.JPG
					20130420120000_username_cameramodel.JPG
