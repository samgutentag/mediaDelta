## Requirements

- These tools all need the following utilities installed on the host machine
    ```
    > brew install ffmpeg
    https://www.sno.phy.queensu.ca/~phil/exiftool/
    ```

## Order of Operations
1. Create media with camera or drone or phone or potato

2. Import Data with bucket_script.py and arguments as needed

  > python bucket_script.py -m import -s /SOURCE_DRIVE/ -t /TARGET_DRIVE/ -a samgutentag

  -m mode, which mode bucket_script should be using to copy/relocate/transfer files

    import stages files by
      /TARGET_DIR/IMPORT/<MEDIA_TYPE>/<EXTENSION>/<YYYYMMDD.HH>/<artist>.<SOURCE_DEVICE>.<YYYYMMDD>.<HHmmss>.<ms>.<extension>

    archive locates files by
      /TARGET_DIR/IMPORT/<MEDIA_TYPE>/<YYYY>/<YYYY.MM>/<YYYYMMDD>.<HHmmss>.<artist>.<counter>.<extension>

  -a artist, assign exif creator and/or artist tags with passed variable

  -s source_drive, top level drive containing media files

  -t target_drive, top level destination directory


3. If desired or possible, do base level culling here, helps keep things cleaner later on

4. Optional - Use GeoTag.app and recorded GPX tracks to append GPS data to imported files.

5. Run script again in `archive` mode before importing to Lightroom