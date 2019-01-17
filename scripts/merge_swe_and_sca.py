import os
import sys

import click
import numpy as np
from osgeo import gdal, gdalnumeric, gdalconst

from snowrs.amsr2.swe import SWE


def merge_swe_with_sca(swe_file, sca_file):
    output_file_name = os.path.join(
        os.path.dirname(sca_file.GetDescription()),
        'SWE_by_SCA.tif'
    )

    swe_by_sca = gdal.GetDriverByName('MEM').CreateCopy(
        output_file_name, sca_file, 0
    )
    swe_by_sca_band = swe_by_sca.GetRasterBand(1)

    modis_band = sca_file.GetRasterBand(1)
    sca_data = np.ma.masked_values(
        modis_band.ReadAsArray(), modis_band.GetNoDataValue(), copy=False
    )
    sca_data = sca_data / 100

    swe_band = swe_file.GetRasterBand(1)
    swe_data = np.ma.masked_values(
        swe_band.ReadAsArray(), swe_band.GetNoDataValue(), copy=False
    )

    gdalnumeric.BandWriteArray(
        swe_by_sca_band,
        (sca_data * swe_data).astype(np.int16)
    )

    swe_by_sca_band.SetMetadata({
        'Description': 'Snow Water Equivalent',
        'Unit': 'mm'
    })
    swe_by_sca_band.ComputeStatistics(0)
    swe_by_sca_band.FlushCache()

    del modis_band, sca_data
    del swe_band, swe_data
    del swe_by_sca_band

    # GDAL Translate is more efficient with compression for some unknown reason
    gdal.Translate(
        output_file_name,
        swe_by_sca,
        format='GTiff',
        creationOptions=["COMPRESS=LZW", "TILED=YES",
                         "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"]
    )

    del swe_by_sca


@click.command()
@click.option('--swe-file',
              prompt=True,
              type=click.Path(exists=True),
              help='Location of LANCE 2 SWE file')
@click.option('--modis-file',
              prompt=True,
              type=click.Path(exists=True),
              help='Location of MODIS SCA file')
def process_swe(**kwargs):
    sca = gdal.Open(kwargs['modis_file'], gdalconst.GA_ReadOnly)

    swe = SWE(kwargs['swe_file'])
    swe.clip_to_tif(sca)

    merge_swe_with_sca(swe.tif_file, sca)

    del swe
    del sca


if __name__ == '__main__':
    sys.exit(process_swe())
