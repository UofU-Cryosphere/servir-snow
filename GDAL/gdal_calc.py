# Trimmed down version of gdal's distributed gdal_gdal.py helper script

import os

from osgeo import gdal, gdalnumeric


def gdal_calc(input_file, output_file_name, no_data_value, input_threshold):
    print('Generating filtered output file: ' + output_file_name)

    ################################################################
    # fetch details of input layer
    ################################################################

    band = 1
    source_file = gdal.Open(input_file, gdal.GA_ReadOnly)
    data_type = source_file.GetRasterBand(band).DataType

    file_no_data_value = source_file.GetRasterBand(band).GetNoDataValue()
    output_dimensions = {
        'x': source_file.RasterXSize,
        'y': source_file.RasterYSize
    }

    ################################################################
    # set up output file
    ################################################################

    # remove existing file and regenerate
    if os.path.isfile(output_file_name):
        os.remove(output_file_name)

    # create file
    gdal_driver = gdal.GetDriverByName('GTiff')
    output_file = gdal_driver.Create(
        output_file_name,
        output_dimensions['x'],
        output_dimensions['y'],
        band,
        data_type
    )

    # set output geo info based on input layer
    output_file.SetGeoTransform(source_file.GetGeoTransform())
    output_file.SetProjection(source_file.GetProjection())

    no_data_value = float(no_data_value)

    band_output = output_file.GetRasterBand(band)
    band_output.SetNoDataValue(no_data_value)
    # write to band
    band_output = None

    ################################################################
    # find block size to chop grids into bite-sized chunks
    ################################################################

    # use the block size of the first layer to read efficiently
    s_block_size = source_file.GetRasterBand(band).GetBlockSize()
    # store these numbers in variables that may change later
    s_x_block_size = s_block_size[0]
    s_y_block_size = s_block_size[1]
    # find total x and y blocks to be read
    total_x_blocks = int(
        (output_dimensions['x'] + s_x_block_size - 1) / s_x_block_size
    )
    total_y_blocks = int(
        (output_dimensions['y'] + s_y_block_size - 1) / s_y_block_size
    )

    ################################################################
    # loop through blocks of data
    ################################################################

    # loop through X lines
    for x_block in range(0, total_x_blocks):

        # in the rare (impossible?) case that the blocks don't fit perfectly
        # change the block size of the final piece
        if x_block == total_x_blocks - 1:
            s_x_block_size = output_dimensions['x'] - x_block * s_block_size[0]

        x_offset = x_block * s_block_size[0]

        # reset buffer size for start of Y loop
        s_y_block_size = s_block_size[1]

        # loop through Y lines
        for y_block in range(0, total_y_blocks):
            # change the block size of the final piece
            if y_block == total_y_blocks - 1:
                s_y_block_size = output_dimensions['y'] -\
                                 y_block * s_block_size[1]

            y_offset = y_block * s_block_size[1]

            # fetch data from input layer
            source_values = gdalnumeric.BandReadAsArray(
                source_file.GetRasterBand(band),
                xoff=x_offset, yoff=y_offset,
                win_xsize=s_x_block_size, win_ysize=s_y_block_size)

            # Filter result according to given input value
            filter_result = source_values * (source_values < input_threshold)
            del source_values

            # write data block to the output file
            output_band = output_file.GetRasterBand(band)
            gdalnumeric.BandWriteArray(
                output_band, filter_result, xoff=x_offset, yoff=y_offset
            )
