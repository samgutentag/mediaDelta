**Assumptions**

- These tools all need the following utilities installed on the host machine
    ```
    > brew install ffmpeg
    https://www.sno.phy.queensu.ca/~phil/exiftool/
    ```

**Order of Operations**
- create media with camera or drone or phone or potato

- Import from media card using
  - "importer.py" to '/STAGING_DRIVE/staging'

- Use Lightroom to go over images and import (via "Copy as DNG") to '/MASTERS_DRIVE/MASTERS' AND TO 'MASTERS_BACKUP_DRIVE/MASTERS'

- Run "archiver.py"
  - '/STAGING_DRIVE/STAGING/IMAGE' to '/ARCHIVE_DRIVE/IMAGE_ARCHIVE'
  - '/STAGING_DRIVE/STAGING/VIDEO' to '/ARCHIVE_DRIVE/VIDEO_ARCHIVE'

- Process photos in Lightroom as desired, export selects to "Photos.app"
