

Assumptions

	exifread package is installed on host machine, can be installed with pip

	> pip install exifread





What I need To Do/Goal of Project

	Correctly format folder name as YYYYMMDD_EventName

	Correctly format image name as YYYYMMDD_HHMMSS_<imageTag>.<extension>

		<imageTag> 	will be the name of the parent folder, before the '-' character in camel case
			else will be 'IMG0000' numbered incrementing from 0001 within the folder









Sample Folder Structure


Current Sample

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



Goal Sample

	HardDrive
		Images
			2015
				03
					20150322_120000_anchorageSquare.JPG
					20150322_120100_anchorageSquare.JPG
					20150322_120200_anchorageSquare.JPG
			2013
				04
					20130413_120000_IMG0230.JPG
					20130420_120000_IMG0254.JPG
