"""File input/output methods.

Created on July 6th 2022

: authors: | Johnny Hendricks <johnny.hendricks@orbitalmicro.com>
"""

def read_tropics():
    """
    Read the data in a Global Precipitation Measurement (GPM) file.

    Returns the data, lats, and lons as 2D arrays for the entire file.

    GPM data comes formatted at 0.1x0.1 degree data with the origin at the
    lower left. To make it consistent with other data sets we use, the arrays
    are transposed to put the origin (NW corner) in the upper left.

    Parameters
    ----------
    filepath : str
        Directory path and name of the file.

    Keyword Arguments
    -----------------
    var : str
        The GPM variable name to read. Must match with an available variable
        name in the Grid group within GPM files.

    Returns
    -------
    data : 2d float
        GPM precipitation rate
    lats : 2d numpy float
        Latitudes of the data points
    lons : 2d numpy float
        Longitudes of the data points
    times : 2d numpy float
        Timestamps of the data points
    """

    return None
