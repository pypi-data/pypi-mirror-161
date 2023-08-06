"""File input/output methods.

Created on July 6th 2022

: authors: | Johnny Hendricks <johnny.hendricks@orbitalmicro.com>
"""

def read_gpm(filepath, var='precipitationCal'):
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

    logger = logging.getLogger(__name__)

    logger.info("read_gpm: reading file %s", filepath)

    try:
        # Read the H5 file.
        file = h5py.File(filepath, 'r')

        # Retrieve the location and time points. Produces 1-D arrays.
        #
        # Warning: default type from h5 read is a float32, which shouldn't
        # be a problem but will cause GeoJSON creation to fail because
        # it wants a float64.
        lats = file['Grid/lat'][:]
        lons = file['Grid/lon'][:]
        time = file['Grid/time'][:]     # Integer seconds since epoch 1970

        # Read the precip data
        data = file["Grid/"+var][:]

        # Data has a useless first dimension. Get rid of it.
        data = data[0, :, :]

        # Data is in col,row order. Transpose for consistency with
        # other data sets. Will now be in row,col order
        data = data.T

        # Data is south to north. Flip for consistency (flip lats to match)
        data = np.flip(data, axis=0)
        lats = np.flip(lats)    # 1-D

        rows = len(lats)        # Number of latitudes
        cols = len(lons)        # Number of longitudes

        # Create 2-D arrays of the lats and lons, to match the data array
        lats = np.repeat(lats, cols)
        lats = lats.reshape(rows, cols)

        lons = np.repeat(lons, rows)
        lons = lons.reshape(cols, rows).T

        # Assume we're using precipitationCal, which only has one time
        # assoicitated with it. Repeat that time for all data points.
        times = np.repeat(time, rows)
        times = np.repeat(times, cols)
        times = times.reshape(rows, cols)

        file.close()

        return data, lats, lons, times

    except Exception as msg:
        logger.warning("Exception while trying to read GPM file: %s", filepath)
        logger.warning(msg)
        return None, None, None, None
