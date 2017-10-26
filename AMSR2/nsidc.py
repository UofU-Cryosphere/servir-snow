from pyproj import Proj, transform

INPUT_PROJECTION = Proj(init='epsg:4326')

#  Northern Hemisphere  #
# ===================== #

# NSIDC North Pole Ease-Grid
NORTH_PROJECTION = '''PROJCS["NSIDC EASE-Grid North",
    GEOGCS["Unspecified datum based upon the International 1924 Authalic Sphere",
        DATUM["Not_specified_based_on_International_1924_Authalic_Sphere",
            SPHEROID["International 1924 Authalic Sphere",6371228,0,
                AUTHORITY["EPSG","7057"]],
            AUTHORITY["EPSG","6053"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4053"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Lambert_Azimuthal_Equal_Area"],
    PARAMETER["latitude_of_center",90],
    PARAMETER["longitude_of_center",0],
    PARAMETER["false_easting",0],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","3408"],
    AXIS["X",UNKNOWN],
    AXIS["Y",UNKNOWN]]'''
NORTH_PROJ = Proj(init='epsg:3408')
NORTH_UL_LON = -135  # This is an approximate value
NORTH_UL_LAT = -86.5  # This is an approximate value
# Converts coordinates from WGS 1984 to polar grid coordinates
NORTH_UL_X, NORTH_UL_Y = transform(
    INPUT_PROJECTION,
    NORTH_PROJ,
    NORTH_UL_LON,
    NORTH_UL_LAT
)

# NSIDC South Pole EASE-Grid
SOUTH_PROJECTION = '''PROJCS["NSIDC EASE-Grid South",
    GEOGCS["Unspecified datum based upon the International 1924 Authalic Sphere",
        DATUM["Not_specified_based_on_International_1924_Authalic_Sphere",
            SPHEROID["International 1924 Authalic Sphere",6371228,0,
                AUTHORITY["EPSG","7057"]],
            AUTHORITY["EPSG","6053"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4053"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Lambert_Azimuthal_Equal_Area"],
    PARAMETER["latitude_of_center",-90],
    PARAMETER["longitude_of_center",0],
    PARAMETER["false_easting",0],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","3409"],
    AXIS["X",UNKNOWN],
    AXIS["Y",UNKNOWN]]'''
SOUTH_PROJ = Proj(init='epsg:3409')
SOUTH_UL_LON = -45  # This is an approximate value
SOUTH_UL_LAT = 86.5  # This is an approximate value
