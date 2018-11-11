from osgeo import gdal


class ReferenceInfo(object):
    def __init__(self, filename):
        self._file_name = filename
        self.file = filename
        self._geo_transform = self.file.GetGeoTransform()
        self._projection = self.file.GetProjection()
        self._gcps = self.file.GetGCPs()
        self._gcp_projection = self.file.GetGCPProjection()

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, filename):
        file = gdal.Open(filename)
        self._file = gdal.Open(file.GetSubDatasets()[0][0], gdal.GA_ReadOnly)
        del file

    @property
    def geo_transform(self):
        return self._geo_transform

    @property
    def projection(self):
        return self._projection

    @property
    def gcps(self):
        return self._gcps

    @property
    def gcp_projection(self):
        return self._gcp_projection

    def copy_to_file(self, file):
        if self.file.GetGCPCount() == 0:
            file.SetGeoTransform(self.geo_transform)
        else:
            file.SetGCPs(self.gcps, self.gcp_projection)

        file.SetProjection(self.projection)
