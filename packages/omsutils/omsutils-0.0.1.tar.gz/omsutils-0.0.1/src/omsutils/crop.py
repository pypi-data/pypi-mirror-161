"""
crop.py

Crop data to a boundary box.

:authors: |  Glenn Grant <glenn.grant@orbitalmicro.com>
2021-11-30
"""

import logging
import numpy as np
import sys

def crop(data, lats, lons, lat_n, lat_s, lon_e, lon_w):
    """Crop data to a lat/lon boundary box.

    Data, lats, and lons can be 1D or 2D. Returns 1D. Data may also be "None"
    and it will still crop the lats and lons.

    Boundary box cannot cross the dateline or it will be clipped.

    Parameters
    ----------
    data : 1D or 2D float
        The data array to crop.
    lats : 1D or 2D float
        Latitudes corresponding to the data
    lons : 1D or 2D float
        Longitudes corresponding to the data
    lat_n : float
          Boundary box limit to the north
    lat_s : float
          Boundary box limit to the south
    lon_e : float
          Boundary box limit to the east
    lon_w : float
          Boundary box limit to the west

    Returns
    -------
    new_data : 1D float
        Cropped data array.
    new_lats : 1d float
        Latitudes for each row of the cropped data.
    new_lons : 1d float
        Lons for each column of the cropped data.
    """

    logger = logging.getLogger(__name__)

    if len(lats.shape) != len(lons.shape):
        logger.warning("lat/lon array dimensions are not equal")
        return None, None, None

    # Reduce lats/lons to one dimension
    lats = lats.flatten()
    lons = lons.flatten()

    if data is not None:
        data = data.flatten()

        if len(lats.shape) != len(data.shape):
            logger.warning("Data array dimensions not equal to locations")
            return None, None, None

    # Create a mask for the cropping
    mask = np.logical_and(lats >= lat_s, lats <= lat_n)
    mask = np.logical_and(mask, lons >= lon_w)
    mask = np.logical_and(mask, lons <= lon_e)

    # Crop to locations the mask
    new_lats = lats[mask]
    new_lons = lons[mask]

    # Crop data to the mask. Make allowances for an empty data array
    if data is not None:
        new_data = data[mask]
    else:
        new_data = None

    return new_data, new_lats, new_lons


def crop3d(data, lats, lons, lat_n, lat_s, lon_e, lon_w):
    """Crop a multi-layer (time series) data array to a lat/lon boundary box.

    Data must be 2D or 3D: [[time/layer], lats, lons]. Returns 2D or 3D cropped
    to new dimensions.

    Boundary box cannot cross the dateline or it will be clipped.

    Warning: Makes the assumption that the data is gridded rectangularly
    with cells parallel to meridians and latitudes. Application to swath
    data may be unpredictable.

    Parameters
    ----------
    data : 2d or 3d float
        The data array to crop. lats x lons, or time x lats x lons
    lats : 2d float
        Corresponding latitudes
    lons  : 2d float
        Corresponding longitudes
    lat_n : float
          Boundary box limit to the north
    lat_s : float
          Boundary box limit to the south
    lon_e : float
          Boundary box limit to the east
    lon_w : float
          Boundary box limit to the west

    Returns
    -------
    new_data : 2D or 3D float
        Cropped data array.
    new_lats : 2d float
        Latitudes for each point in the cropped data.
    new_lons : 2d float
        Longitudes for each point in the cropped data.
    """

    logger = logging.getLogger(__name__)
    logger.info("Cropping 3D")

    if len(data.shape) < 2:
        logger.error("Data must be a 2D or 3D array, lats x lons [x time]")
        sys.exit(0)

    # Sanity check for same dimensions
    dims = data.shape
    if len(data.shape) == 3:
        dims = data.shape[1:3]

    if dims is None:
        logger.warning("Data dimensions (dims) is none.")
        return None, None, None

    if dims != lats.shape or dims != lons.shape:
        logger.error("Data dimensions = " + str(dims) +
                     " does not match lats shape " + str(lats.shape) +
                     " and/or lons shape " + str(lons.shape))
        sys.exit(0)

    # Cropping warnings if something is amiss
    if lon_w > lon_e:
        logger.warning("boundary box west longitude is less than east.")
        return None, None, None

    if lon_e > 180:
        logger.warning("Boundary box East crosses the dateline, clipping.")
        lon_e = 179.99999999

    if lon_w < -180:
        logger.warning("Boundary box West crosses the dateline, clipping.")
        lon_w = -179.999999999

    if lat_s > lat_n:
        logger.warning("Boundary box north latitude is less than south.")
        return None, None, None

    lat_mask = np.logical_and(lats >= lat_s, lats <= lat_n)
    lon_mask = np.logical_and(lons >= lon_w, lons <= lon_e)

    # Combine the two masks
    mask = np.logical_and(lat_mask, lon_mask)

    # A place for the cropped data
    new_data = None
    new_lats = None
    new_lons = None

    rows = np.count_nonzero(lat_mask[:,0])
    cols = np.count_nonzero(lon_mask[0,:])

    if rows == 0 or cols == 0:
        logger.warning("Cropping resulted in zero rows or columns")
        logger.warning("Check array orientation and/or boundaries")

    else:
        new_lats = np.reshape(lats[mask], [rows, cols])
        new_lons = np.reshape(lons[mask], [rows, cols])

        # Crop data. Also handles case where there is no data (data is None) and
        # we're simply cropping the lats and lons.
        if data is not None:
            # Handle 3d data arrays
            if len(data.shape) == 3:
                new_data = np.reshape(data[:, mask], [data.shape[0], rows, cols])
            else:
                new_data = np.reshape(data[mask], [rows, cols])

    return new_data, new_lats, new_lons
