## Requirements

- These tools all need the following utilities installed on the host machine
    ```
    > brew install ffmpeg
    https://www.sno.phy.queensu.ca/~phil/exiftool/
    ```

## Order of Operations
1. Create media with camera or drone or phone or potato

2. Import from media card using
  - "importer.py" to '/STAGING_DRIVE/staging'

3. Use Lightroom to go over images and import (via "Copy as DNG") to '/MASTERS_DRIVE/MASTERS' AND TO 'MASTERS_BACKUP_DRIVE/MASTERS'

4. Run "archiver.py"
  - '/STAGING_DRIVE/STAGING/IMAGE' to '/ARCHIVE_DRIVE/IMAGE_ARCHIVE'
  - '/STAGING_DRIVE/STAGING/VIDEO' to '/ARCHIVE_DRIVE/VIDEO_ARCHIVE'

5. Process photos in Lightroom as desired, export selects to "Photos.app"
