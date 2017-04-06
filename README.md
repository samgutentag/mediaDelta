**Assumptions**

	First ExifTool should be installed on the host machine, it can be downloaded here
	http://www.sno.phy.queensu.ca/~phil/exiftool/

	> pip install -U pyexifinfo
	> pip install -U moviepy
	> pip install -U PyExifTool
	> brew install ffmpeg



**Order of Operations**


- Take Images with camera or drone or phone or potato

- Import from card using
  - "importer.py" to '/STAGING_DRIVE/STAGING'
  - "deviceImporter.py" to '/STAGING_DRIVE/STAGING'

- Use Lightroom to go over images and import (via "Copy as DNG") to '/ORANGE_VAULT/MASTERS'

- Run "archiver.py"
  - '/STAGING_DRIVE/STAGING/IMAGE' to '/BACKUP_DRIVE/IMAGE_ARCHIVE'
  - '/STAGING_DRIVE/STAGING/VIDEO' to '/BACKUP_DRIVE/VIDEO_ARCHIVE'

- Process photos in Lightroom as desired, export selects to "Photos.app"



**HardDrive Setup**
