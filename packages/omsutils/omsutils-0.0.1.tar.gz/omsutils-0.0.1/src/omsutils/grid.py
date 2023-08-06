"""
grid

Gridding functions.

:authors: |  Glenn Grant <glenn.grant@orbitalmicro.com>
2021-12-09
"""

import numpy as np
import logging
import unittest
from scipy.interpolate import NearestNDInterpolator

# Dictionary of affine geographic grids with lat/lons spaced at regular intervals
grids = {"geographic_0.1deg":
         {"area_id": "geog_0.1",
             "description": "GPM Geographic 0.1 degree grid",
             "rows": 1800, "cols": 3600, 
             "max_lat": 89.95, "min_lat": -89.95,
             "max_lon": 179.95, "min_lon": -179.95,
          }
         }

    
def geographic_grid(grid=grids["geographic_0.1deg"], geotiff_orientation=False):
    
    """Returns lats and lons for a regularly-spaced geographic grid.
    By default, grids are oriented x,y (lon,lat), origin at the bottom left.
    
    Keyword Arguments
    -----------------
    grid : grids dictionary object
        The new grid.
    geotiff_orientation : boolean
        Rearrange the griding to match north-to-south geotiff orientation,
        with lats,lons dimensions.
        
    Returns
    -------
    lat_grid : 2d float array
        Latitudes for the specified grid
    lon_grid : 2d float array
        Longitudes for the specified grid
    """
    
    lat_line = np.linspace(grid['min_lat'], grid['max_lat'], grid['rows'])
    lon_line = np.linspace(grid['min_lon'], grid['max_lon'], grid['cols'])
    
    lon_grid, lat_grid = np.meshgrid(lon_line, lat_line, indexing='ij', sparse=False)

    # Flip lats for geotiff orientation (N-to-S, origin in upper left),
    # and transpose to put in [Y,X] indexing
    if geotiff_orientation:
        lat_grid = np.flip(lat_grid, axis=1)

        lat_grid = lat_grid.T
        lon_grid = lon_grid.T

    return lat_grid, lon_grid


def nearest_neighbor_regrid(lats, lons, grid=grids["geographic_0.1deg"]):
    """Regrids data using a nearest neighbor algorithm.
    
    Note: Since the underlying algorithm is an interplolation, not
    explicitly setting the new lats/lons to the grid centroid values,
    there may be minor precision errors. Rounding off at the 12th
    decimal place appears to address the problem, for now.

    Parameters
    ----------
    lats : 1d float array
        Array of latitudes to be regridded to their nearest neighbor
    lons : 1d float array
        Array of longitudes to be regridded to their nearest neighbor

    Keyword Arguments
    -----------------
    grid : grids dictionary object
        The new grid.

    Returns
    -------
    new_lats : 1d numpy float array
        Regridded lats
    new_lons : 1d numpy float array
        Regridded lons

    """
  
    logger = logging.getLogger(__name__)
    logger.info("Nearest-neighbor regridding")
    
    # Create an evenly-spaced lat/lon
    lat_grid, lon_grid = geographic_grid(grid)

    # Create an interpolation object to help with nearest-neighbor regridding
    # of latitudes
    lat_interp = NearestNDInterpolator(list(zip(lat_grid[0,:], lat_grid[0,:])),
                                       lat_grid[0,:])

    # Regrid the latitudes
    new_lats = lat_interp(list(zip(lats,lats)))
    new_lats = np.round(new_lats, decimals=12)  # Crop off loose bits
    
    # Do the same for longitudes
    lon_interp = NearestNDInterpolator(list(zip(lon_grid[:,0], lon_grid[:,0])),
                                       lon_grid[:,0])

    new_lons = lon_interp(list(zip(lons,lons)))
    
    # Round off negligible errors
    new_lons = np.round(new_lons, decimals=12)
    
    return new_lats, new_lons


# Unit testing
class TestMethods(unittest.TestCase):

    def test_geographic_grid(self):
                   
        # Create a default lat/lon grid
        lat_grid, lon_grid = geographic_grid()

        self.assertEqual(lon_grid.shape[0], 3600)   # Axis 0 (X) is longitude
        self.assertEqual(lat_grid.shape[1], 1800)   # Axis 1 (Y) is latitude
        
        # Check a sampling of latitudes
        self.assertEqual(lat_grid[0, 0], -89.95)    # Origin in lower left
        self.assertEqual(lat_grid[100, 200], -69.95)
        self.assertEqual(lat_grid[3599, 1799], 89.95) # Upper right corner

        # Check a sampling of longitudes
        self.assertEqual(lon_grid[0, 0], -179.95)    # Origin in lower left
        self.assertEqual(lon_grid[100, 200], -169.95)
        self.assertEqual(lon_grid[3599, 1799], 179.95) # Upper right corner

        # Check geotiff orientation
        lat_grid, lon_grid = geographic_grid(geotiff_orientation=True)

        # New dimensions should be [1800,3600] ([lats,lons]), with [0,0] in
        # the upper left corner (n-s orientation)
        self.assertEqual(lon_grid.shape[0], 1800)   # Axis 0 is latitude
        self.assertEqual(lat_grid.shape[1], 3600)   # Axis 1 is longitude
        self.assertEqual(lat_grid[0, 0], 89.95)     # Origin at upper left
        self.assertEqual(lat_grid[1799, 0], -89.95) # North to South
        self.assertEqual(lon_grid[1799, 3599], 179.95) # Lower right corner

        
    def test_nearest_neighbor_regrid(self):
        
        # Use some random lats/lons to see if the regridding interpolates
        # them to reasonable locations.
        lats = np.array([-89.99, 22.014, -36.228, 89.36])
        lons = np.array([-179.94, 0.014, -136.901, 179.98])
        
        new_lats, new_lons = nearest_neighbor_regrid(lats, lons)
        
        self.assertEqual(new_lats[0], -89.95)
        self.assertEqual(new_lats[1], 22.05)
        self.assertEqual(new_lats[2], -36.25)
        self.assertEqual(new_lats[3], 89.35)

        self.assertEqual(new_lons[0], -179.95)
        self.assertEqual(new_lons[1], 0.05)
        self.assertEqual(new_lons[2], -136.95)
        self.assertEqual(new_lons[3], 179.95)
   

if __name__ == '__main__':

    unittest.main()
