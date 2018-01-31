## GDAL scripts to merge MODIS images

### Features
The script processes all images found inside each day folder of a year for given
type. It first creates a mosaic from the individual images and filters all values 
above a threshold which is determined by the type of images. For radiative forcing 
the upper limit is 400 and for snow fraction 100.
Last step is a projection of the mosaic output to WGS 84.

### Source folder structure

The required `source-folder` parameter passed into the execution of a script run 
assumes the following structure to process images:<br/>
```/Path/To/SourceFolder/YYYY/[forcing|snow_fraction]/YYYYMM```
* `YYYY`: four digit year of the downloaded images.
* `[forcing|snow_fraction]`: One of the two image types
* `YYYYMMM`: Four digit year plus three digit day of year

<br/>Downloaded images can be placed directly inside source folder without the
day of year folder. The script can create the day folder automatically when given 
the optional parameter `scan-folder`.

#### Sample source folder
```
/MODIS_ARCHIVE/Region1/
                       2000/
                            forcing/
                                    2000001/  <- will be created based on found images
                            snow_fraction/
                                    2000001/
                       2001/
                            forcing/
                                    2001001/
                            snow_fraction/
                                    2001001/
```

### Output
The final output file for each day has the following naming convention:
```
YYYYMM_[rf|SCA].tiff
```
* `rf`: Radiative forcing
* `SCA`: Snow covered area

### Usage
In a terminal:

```sh 
python gdal_merge.py 
--source-type [fraction|forcing]
--source-folder /Path/To/SourceFolder/
--scan-folder 0
--year YYYY
```

Parameters:
* `source_type`: _(Required)_ Can be either:
  * `forcing` - to press radiative `forcing` folders
  * `fraction` - to process `snow_fraction` folders
* `source-folder`: _(Required)_ Source folder path with images to process.
* `year`: _(Optional)_ Only process given year. Otherwise the source folder will
be scanned for years from 2000 to present.
* `scan-folder`: _(Optional)_ Scan for newly downloaded images inside the year 
foldaer and create a day folder where images from the same day are moved to.

These parameters, plus a short description can also be obtained in the terminal
by passing the `--help` to the script.