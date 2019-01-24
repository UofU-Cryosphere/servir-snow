from osgeo import gdal


class ReferenceInfo(object):
    # Bounding box for watershed basins in the Himalayas
    GCP_X_MAX = 127.00310516357422
    GCP_X_MIN = 45.992488861083984
    GCP_Y_MAX = 47.39791488647461
    GCP_Y_MIN = 24.56041717529297

    GCP_PROJECTION = '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 ' \
                     '+a=6371007.181 +b=6371007.181 +units=m ' \
                     '+no_defs +nadgrids=@null +wktext'

    def __init__(self, filename):
        self._file_name = filename
        self.file = filename
        self._geo_transform = self.file.GetGeoTransform()
        self._projection = self.file.GetProjection()
        self.gcps = self.file.GetGCPs()
        self.gcp_projection = self.file.GetGCPProjection()

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

    @gcps.setter
    def gcps(self, gcps):
        self._gcps = [gcp for gcp in gcps if self.within_basin(gcp)]

    @property
    def gcp_projection(self):
        return self._gcp_projection

    @gcp_projection.setter
    def gcp_projection(self, projection):
        if len(projection) is 0:
            self._gcp_projection = self.GCP_PROJECTION
        else:
            self._gcp_projection = self.projection

    def within_basin(self, gcp):
        if self.GCP_X_MIN <= gcp.GCPX <= self.GCP_X_MAX and \
                self.GCP_Y_MIN <= gcp.GCPY <= self.GCP_Y_MAX:
            return True
        return False

    def copy_to_file(self, file):
        if self.file.GetGCPCount() == 0:
            file.SetGeoTransform(self.geo_transform)
        else:
            file.SetGCPs(self.gcps, self.gcp_projection)

        file.SetProjection(self.projection)
