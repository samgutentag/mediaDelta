Assumptions

	First ExifTool should be installed on the host machine, it can be downloaded here
	http://www.sno.phy.queensu.ca/~phil/exiftool/

	> pip install -U pyexifinfo
	> brew install moviepy



Order of Operations

00.	Smile

01.	Take Images with camera or drone or phone or potato

02.	Import from card using
	a.	"importer.py" to '/STAGING_DRIVE/STAGING'
	b.	"deviceImporter.py" to '/STAGING_DRIVE/STAGING'

03.	Use Lightroom to go over images and import (via "Copy as DNG") to '/ORANGE_VAULT/MASTERS'

04.	Run "archiver.py"
	a.	'/STAGING_DRIVE/STAGING/IMAGE' to '/BACKUP_DRIVE/IMAGE_ARCHIVE'
	b.	'/STAGING_DRIVE/STAGING/VIDEO' to '/BACKUP_DRIVE/VIDEO_ARCHIVE'

05.	Process photos in Lightroom as desired, export selects to "Photos.app"



HardDrive Setup
