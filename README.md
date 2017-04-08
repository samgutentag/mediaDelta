**Assumptions**

- These tools all need the following utilities installed on the host machine
    '''
	> pip install -U pyexifinfo
	> pip install -U moviepy
	> pip install -U PyExifTool
	> brew install ffmpeg
    '''

**Order of Operations**
- create media with camera or drone or phone or potato

- Import from media card using
  - "importer.py" to '/STAGING_DRIVE/STAGING'
  - "deviceImporter.py" to '/STAGING_DRIVE/STAGING'

- Use Lightroom to go over images and import (via "Copy as DNG") to '/MASTERS_DRIVE/MASTERS' AND TO 'MASTERS_BACKUP_DRIVE/MASTERS'

- Run "archiver.py"
  - '/STAGING_DRIVE/STAGING/IMAGE' to '/ARCHIVE_DRIVE/IMAGE_ARCHIVE'
  - '/STAGING_DRIVE/STAGING/VIDEO' to '/ARCHIVE_DRIVE/VIDEO_ARCHIVE'

- Process photos in Lightroom as desired, export selects to "Photos.app"

**Hard Drive Setup**
	-	500GB 	STAGING_DRIVE_1			Apple Sticker Drive
	-	500GB	MASTERS_BACKUP_DRIVE	GoPro Sticker Drive
	-	2TB		ARCHIVE_DRIVE			Desktop Drive
	-	1TB		MASTERS_DRIVE			Orange WD Passport
	-	???GB	SLAVE_DRIVE_01			Silver USBA Drive
	-	???GB	SLAVE_DRIVE_02			Black Automatic Sticker Drive
