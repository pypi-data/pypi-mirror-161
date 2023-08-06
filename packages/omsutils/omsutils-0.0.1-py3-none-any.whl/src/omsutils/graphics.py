"""
graphics

Create images, shapefiles, animations, etc.

:authors: |  Glenn Grant <glenn.grant@orbitalmicro.com>
2021-11-29
2022-06-28 Module name changed from output_format.py to graphics.py
"""

import logging
import unittest
import os
import datetime as datetime
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import Affine
from matplotlib.colors import ListedColormap


def png(data,
        lats, lons,
        image_dir="",
        image_name="",
        lat_n=90., lat_s=-90.,
        lon_e=180., lon_w=-180.,
        title='', units='', colormap='rainbow',
        save=True, display=False,
        cb_min=0, cb_max=0, point_size=-1,
        cb_kwargs=None,
        figure_size_inches=(6.75,6),
        figure_dpi=100,
        coastlines=True,
        colorbar=True,
        gridlines=True,
        projection=ccrs.PlateCarree()):
    """
    Creates a PNG image from a Numpy data array.

    Color range is set to the data min/max if left to default.

    Projection defaults to PlateCarree, which is good for general look-see
    plotting of global data; refer to the CCRS projections page for other
    options: https://scitools.org.uk/cartopy/docs/v0.15/crs/projections.html

    Parameters
    -----------------
    data (1D or 2D float array):
        Data to be imaged.
    lats (1D or 2D float array):
        Latitudes matching the data array 1:1
    lons (1D or 2D float array):
        Longitudes matching the data array 1:1

    Keyword Arguments
    -----------------
    image_dir (str):
        Directory where the image will be stored
    image_name (str):
        Name of the image
    lat_n (float):
        Northern latitude limit to the plot
    lat_s (float):
        Southern latitude limit to the plot
    lon_e (float):
        Eastern longitude limit to the plot
    lon_w (float):
        Western longitude limit to the plot
    title (str):
        Title of the plot, if any
    Units (str):
        Units displayed on the colorbar, if any
    colormap (str):
        Name of the colormap used.
    coastlines (boolean):
        Plot coastlines?
    colorbar (boolean):
        Include a colorbar?
    save (boolean):
        Save the image?
    display (boolean):
        Display the image?
    cb_min (float):
        Minimum value on colorbar
    cb_max (float):
        Maximum value on colorbar
    point_size (int):
        Plotting point size
    cb_kwargs (str):
        Addtional plotting arguments; see matplotlib cb_kwargs
    figure_size_inches (float tuple):
        Size of the image in inches, width x height. TBD Use a zero for automatic.
    figure_dpi (int):
        Dots per inch
    gridlines (boolean)
        Draw gridlines?
    projection (ccrs projection object):
        Requested map projection

    Returns
    -------
    image_dir : str
        Directory where the png file is stored
    filename : str
        Name of the png file
    """

    # Reload plotting to make sure old settings are discarded

    #from imp import reload
    #import matplotlib.pyplot as plt
    #reload(plt)

    logger = logging.getLogger(__name__)

    logger.info('Creating PNG image')

    # If the data arrays are 2D, flatten them
    flat_data = np.copy(data).flatten()
    flat_lats = np.copy(lats).flatten()
    flat_lons = np.copy(lons).flatten()

    # Set the colorbar range, if left to default
    if cb_min == cb_max:
        cb_min = np.nanmin(flat_data)
        cb_max = np.nanmax(flat_data)

    # Set plot size
    plt.figure(num=None, figsize=figure_size_inches,
               dpi=figure_dpi, facecolor='w', edgecolor='k')

    # Make axes with the projection.
    axes = plt.axes(projection=projection)

    try:
        # Calculate a reasonable plotting point size, if the user hasn't
        # specified one.
        if point_size == -1:
            # The smaller the AOI, the larger the point size needed.
            scale = np.ptp(flat_lats)

            point_size = 2

            if scale < 10:
                point_size = 50 / scale
            if scale < 5:
                point_size = 400 / scale
            if scale < 1:
                point_size = 2000 / scale

        # imshow (plot a raster) with the extent, transform represents the
        # coordinate system of input data.
        contourf_ = plt.scatter( x=flat_lons, y=flat_lats, c=flat_data,
                s=point_size, marker=',', cmap=colormap,
                vmin=cb_min, vmax=cb_max)

        # Add coastlines, black lines by default
        if coastlines:
            axes.coastlines()

        # Define x and y gridline locations and add lines
        if gridlines:

            lon_spacing = 20
            if (lon_e - lon_w) < 41:
                lon_spacing = 5
            if (lon_e - lon_w) < 11:
                lon_spacing = 2

            lat_spacing = 10
            if (lat_n - lat_s) < 31:
                lat_spacing = 5
            if (lat_n - lat_s) < 11:
                lat_spacing = 2

            x_gl = np.arange(lon_w, lon_e, lon_spacing)
            y_gl = np.arange(lat_s, lat_n, lat_spacing)
            axes.gridlines(crs=ccrs.PlateCarree(),
                         xlocs = x_gl, ylocs = y_gl,
                         draw_labels=False, color='gray', alpha=1.0)

        axes.set_extent([lon_w, lon_e, lat_s, lat_n])

        # BUG IN MATPLOTLIB! Set_extent sometimes ignored, plot exceeds set
        # boundary. WHY??? Workaround...
        #if lat_n >= 40:
        #    axes.set_extent([lon_w, lon_e, lat_s, lat_n-5])

        if colorbar:
            if cb_kwargs == None:
                cb_kwargs = {'format': '%0.0f'}

                if cb_max - cb_min < 5:
                    cb_kwargs = {'format': '%0.1f'}

                elif cb_max - cb_min < 1:
                    cb_kwargs = {'format': '%0.2f'}

            colorbar = plt.colorbar(contourf_, ax=axes, fraction=0.03, **cb_kwargs)

            colorbar.set_label(units, fontsize=12)

        plt.title(title, fontsize=12)

        filepath = ''
        filename = ''

        if display:
            plt.show()

        if save:
            filename = image_name + '.png'
            filepath = os.path.join(image_dir, filename)
            logger.info("Saving PNG image %s", filepath)
            plt.savefig(filepath, bbox_inches='tight')

        return image_dir, filename

    except Exception as msg:
        logger.warning('Unable to create image: %s', str(msg))

    return '', ''


def geotiff(data,
            lats, lons,
            image_dir,
            name,
            scale=1.0,
            date_time=None,
            as_integer=False,
            fillvalue=-9999):
    """
    Creates a GeoTIFF image from a Numpy data array.

    Assumes a full, filled affine array of data. Cannot be sparse.
    *TBD handle multiple layers.

    Parameters
    -----------------
    data (2D or 3D* float array):
        Data to be imaged.
    lats (2D float):
        Array of latitudes matching the data.
    lons (2D float):
        Array of longitudes matching the data.
    image_dir (str):
        Location where image will be stored.
    name (str):
        Name of the file.

    Keyword Arguments
    -----------------
    scale : float
        Scale the data by this factor.
    date_time : datetime object
        Add the data/time as a tag in the geotiff.
    as_integer : boolean, optional
        Round-down the data to the nearest integer and write the geotiff
        file data as Int32 instead of Float64. Integer data is more portable
        since some image viewers may not recognize float geotiff data, and
        Int32 is used because rasterio doesn't like the Int64 which is
        naturally produced by Python in the scaling process, fukin stupid.
    fillvalue : float or int
        No data fill value

    Returns
    -------
    filepath (str):
        Path/name of the geotiff file
    """

    logger = logging.getLogger(__name__)

    logger.info("Creating GeoTIFF image")

    # For setting the resolution - default to using the actual data.
    north = np.nanmax(lats)
    south = np.nanmin(lats)
    east = np.nanmax(lons)
    west = np.nanmin(lons)

    # Geotiffs depend on having a transform array. If there's no data,
    # no array generation is possible. Bail out.
    if not north or not south or not east or not west:
        logger.warning('Cannot create geotiff -- no data')
        return None

    # Resolution in x and y dimensions.
    x_res = np.abs(east - west) / lons.shape[1]
    y_res = np.abs(north - south) / lats.shape[0]

    # Create the affine transform which will be used by the GeoTIFF driver.
    # The transform requires the upper left point coordinate as a starting
    # point, and creates a scaling matrix based on the resolution and location.
    transform = Affine.translation(lons[0,0] - x_res / 2,
                                   lats[0,0] - y_res / 2) * \
                                   Affine.scale(x_res, -y_res)

    name = name + '.tif'
    path = os.path.join(image_dir, name)

    scaled_data = data*scale

    if as_integer:
        scaled_data = np.array(scaled_data).astype(np.int32)

    with rasterio.open(             # Open a raster file
        path,                       # path and file name
        'w',                        # Open the file for writing
        driver='GTiff',             # Format
        height=scaled_data.shape[0],
        width=scaled_data.shape[1],
        count=1,                    #TBD layers
        dtype=scaled_data.dtype,
        crs='+proj=latlong +datum=WGS84 +ellps=WGS84',
        transform=transform,
        nodata=fillvalue) as new_dataset:

        #???TBD Add tags. Starting point below, but only partially verified.
        # More work needed. Refer to:
        # https://www.loc.gov/preservation/digital/formats/content/tiff_tags.shtml
        new_dataset.update_tags(AREA_OR_POINT='Point')
        new_dataset.update_tags(TIFFTAG_IMAGEDESCRIPTION='ScaleFactor='+str(scale) + \
               ', FillValue=' + str(fillvalue))
        new_dataset.update_tags(TIFFTAG_RESOLUTIONUNIT=1)

        if date_time is not None:
            new_dataset.update_tags(
                TIFFTAG_DATETIME=date_time.strftime('%Y%m%d %H:%M UTC'))

        new_dataset.write(scaled_data, 1)

        #new_dataset.close()

    return name


def precip_cmap():
    """
    Creates a standardized colormap for depicting rain rates.

    Uses white as precip = 0.0 mm/hr.

    Returns
    -------
    precip_cm : colormap object
        Color map for rain rates. Can be used in lieu of a named colormap,
        e.g., instead of 'rainbow'
    """

    base_cm = plt.get_cmap('gist_ncar_r', 256)
    precip = base_cm(np.linspace(0, 1, 256))
    white = np.array([256/256, 256/256, 256/256, 1])
    precip[0, :] = white
    precip_cm = ListedColormap(precip)

    return precip_cm


def cloud_cmap():
    """
    Creates a standardized colormap for depicting clouds.

    Returns
    -------
    cloud_colormap : colormap object
        Color map for rain rates. Can be used in lieu of a named colormap,
        e.g., instead of 'rainbow'
    """

    base_cm = plt.get_cmap('rainbow_r', 256)
    clouds = base_cm(np.linspace(1, 0, 256))
    white = np.array([256/256, 256/256, 256/256, 1])
    clouds[255, :] = white
    cloud_colormap = ListedColormap(clouds)

    return cloud_colormap


# Unit testing
class TestMethods(unittest.TestCase):
    """
    Unit testing.
    """

    def test_png(self):
        """
        Test PNG generation.

        Returns
        -------
        None.

        """

        name = 'png_test'
        '''
        # Remove any old test images
        filepath = os.path.join(config.test_output_dir, name+'.png')

        if os.path.exists(filepath):
            os.remove(filepath)

        path = os.path.join(config.test_dir,
                            config.test_gpm_file)

        data, lats, lons, _ = Product.read_gpm(path)

        mask = data >= 0
        data = data[mask]
        lats = lats[mask]
        lons = lons[mask]

        _, filename = png(data, lats, lons, config.test_output_dir, name,
                          cb_max=10, colormap=precip_cmap(),
                          title='Test Image', units='mm/hr',
                          save=True, display=False)

        print("Created PNG:", filename)

        self.assertEqual(name+'.png', filename)
        self.assertTrue(os.path.exists(filepath))
        '''


    def test_geotiff(self):
        """
        Test geotiff generation.
        """

        '''
        # Get some test data
        path = os.path.join(config.test_dir,
                            config.test_gpm_file)

        data, lats, lons, _ = Product.read_gpm(path)

        date_time = datetime.date.today()

        # Remove any old test images
        filepath = os.path.join(config.test_output_dir,
                                "test_geotiff.tif")

        if os.path.exists(filepath):
            os.remove(filepath)

        # Create the new image
        name = geotiff(data, lats, lons, config.test_output_dir,
                       "test_geotiff", date_time=date_time)

        print("Created geotiff:", name)

        # Test for success
        self.assertEqual(name, "test_geotiff.tif")
        self.assertTrue(os.path.exists(filepath))


        # Repeat same test but using different options
        filepath = os.path.join(config.test_output_dir,
                                "test_geotiff_x100.tif")
        if os.path.exists(filepath):
            os.remove(filepath)

        # Save the geotiff as integer data, with a scaling factor
        name = geotiff(data, lats, lons, config.test_output_dir,
                       "test_geotiff_x100", scale=100, as_integer=True,
                       date_time=date_time)

        print("Created second geotiff:", name)

        self.assertEqual(name, "test_geotiff_x100.tif")
        self.assertTrue(os.path.exists(filepath))
        '''


if __name__ == '__main__':

    unittest.main()
