## Requirements

- These tools all need the following utilities installed on the host machine
    ```
    > pip install -r requirements.txt
    ```

- Reading and writing exif data is implemented with Phil Harvey's ExifTool which can be found and downloaded here:
    ```
    https://www.sno.phy.queensu.ca/~phil/exiftool/
    ```

- Future experimentation and video testing will require ffmpeg, install on OSX with Homebrew
    ```
    https://brew.sh
    > brew install ffmpeg
    ```

## Order of Operations
1. Create media with camera or drone or phone or potato

2. Import Data with bucket_script.py and arguments as needed

  > python bucket_script.py -s /SOURCE_DRIVE/ -t /TARGET_DRIVE/ -a samgutentag -mode import

3. If desired or possible, do base level culling here, helps keep things cleaner later on

4. Optional - Use GeoTag.app and recorded GPX tracks to append GPS data to imported files.

5. Run script again in `archive` mode before importing to Lightroom