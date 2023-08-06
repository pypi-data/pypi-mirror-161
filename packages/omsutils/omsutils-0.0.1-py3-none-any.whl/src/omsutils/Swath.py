"""
Swath class

Create an object of swath data by reading a file.

:authors: | Richard Delf
            Modified by Glenn Grant for WXS NRT product use, 2021-12-06
"""

import os
import logging
import datetime
import unittest
import numpy as np
import h5py
import config


class Swath():

    def __init__(self, filepath, satellite=None,
                 aoi=[-180,180,-90,90], channel_list=None,
                 variable_list=None,
                 inc_angle_range=None, fill_value=np.nan):
        """
        Initialize swath data object from a file.

        Parameters
        -----------------
        filepath (str):
            Relative or fully qualified path of the input file

        Keyword Arguments
        -----------------
        satellite (str):
            Satellite type. Automated determination if left None.
        aoi (list):
            Boundary box for Area of Interest: [W, E, S, N]
        channel_list (list):
            List of channels to process
        variable_list (list):
            Specifies the variables to use to create an input array to a
            neural net. Use channel 'mwhs_ch1' etc. for Tb channels, and
            actual Class variable names for everything else, e.g. 'lat',
            'land_use', etc.
        inc_angle_range (list):
            Range of valid viewing angles relative to nadir: [min, max]
        fill_value (float):
            Fill value for data that is masked out.
        """


        logger = logging.getLogger(__name__)
        #logging.basicConfig(level = logging.INFO)

        self.fname = filepath
        logger.info('Swath init %s', self.fname)

        self.channels = channel_list
        self.aoi = aoi
        self.inc_angle_range = inc_angle_range
        self.fill_value = fill_value
        self.variable_list = variable_list
        self.nn_data = None
        self.satellite = satellite
        self.data = None
        self.lat = None
        self.lon = None

        # Attempt to determine satellite if not provided
        if self.satellite is None:
            if self.fname.find('FY3D_MWHSX_GBAL_L1') > -1:
                self.satellite = 'fy3d'
            if self.fname.find('TROPICS') > -1:
                self.satellite = 'tropics'
        else:
            self.satellite = self.satellite.lower()

        self.read_file()


    def read_file(self):
        """Read the data file.
        """

        logger = logging.getLogger(__name__)
        logger.info('Reading the data file')

        if self.satellite == 'fy3d':
            self.read_mwhs2()
        elif self.satellite == 'tropics':
            self.read_tropics()
        else:
            logger.error('Satellite type not recognized')


    def apply_mask(self):
        """
        Mask the data based on AOI, incidence view angle, and overlap.
        """

        logger = logging.getLogger(__name__)
        logger.info('Applying data mask')

        # The mask is generated to match latitudes array
        mask = np.full_like(self.lat,True)

        # Make incidence angle mask
        if self.inc_angle_range is not None:
            min_inc = self.inc_angle_range[0]
            max_inc = self.inc_angle_range[1]
            mask *= ((self.inc < max_inc) * (self.inc > min_inc))

        # Make an AOI bounding box mask
        mask *= (self.lat >= self.aoi[2]) * (self.lat <= self.aoi[3]) * \
                (self.lon >= self.aoi[0]) * (self.lon <= self.aoi[1])

        # The mwhs files have a slight crossover around (but not at) the
        # equator. The simplest way to crop for this to get all data with
        # no repeats when reading in multiple files is to crop at
        # around 5 degrees latitude:
        # FY3D: Look for pixels above 5 deg in the first part of the swath...
        if self.satellite == 'fy3d':

            start_xover_idx = np.argwhere(self.lat[:200,:]>5)

            # And pixels below 5 deg for the last part of the swath...
            end_xover_idx = np.argwhere(self.lat[2000:,:]<5)
            end_xover_idx[:,0] += 2000

            # ...and generate a mask from them.
            mask[start_xover_idx[:,0],start_xover_idx[:,1]] = False
            mask[end_xover_idx[:,0],end_xover_idx[:,1]] = False

        self.mask = mask.astype(bool)
        self.lat[~self.mask] = self.fill_value
        self.lon[~self.mask] = self.fill_value

        # Handle 3-D masks
        if len(self.mask.shape) == 3:
            self.data[~self.mask] = self.fill_value
            self.inc[~self.mask] = self.fill_value
            self.secant_inc[~self.mask] = self.fill_value
            self.aqtime[~self.mask[0]] = self.fill_value
        else:
            self.data[:, ~self.mask] = self.fill_value
            self.inc[~self.mask] = self.fill_value
            self.secant_inc[~self.mask] = self.fill_value
            self.aqtime[~self.mask] = self.fill_value


    def read_mwhs2(self):
        """
        Read an FY3 Microwave Humidity Sounder v2 (MWHS2) data file.
        """

        logger = logging.getLogger(__name__)
        #logging.basicConfig(level = logging.INFO)
        logger.info('Loading FY swath name: %s', self.fname)

        with h5py.File(self.fname,'r') as file:

            self.lat = file["Geolocation"]["Latitude"][:].astype(float)
            self.lon = file["Geolocation"]["Longitude"][:].astype(float)
            self.data  = file["Data"]["Earth_Obs_BT"][:]

            # Sensor viewing incidence angle
            zenith_slope = file['Geolocation/SolarZenith'].attrs.get('Slope')[0]
            self.inc = file["Geolocation"]["SensorZenith"][:]*zenith_slope

            # Secant of the viewing angle
            self.secant_inc = 1/np.cos(np.radians(self.inc))

            ob_start_datetime = file.attrs['Observing Beginning Date'].decode('utf-8') + \
                file.attrs['Observing Beginning Time'].decode('utf-8')
            ob_start_datetime = datetime.datetime.strptime(
                ob_start_datetime,'%Y-%m-%d%H:%M:%S.%f').replace(tzinfo=datetime.timezone.utc)

            ob_end_datetime = file.attrs['Observing Ending Date'].decode('utf-8') + \
                file.attrs['Observing Ending Time'].decode('utf-8')
            ob_end_datetime = datetime.datetime.strptime(
                ob_end_datetime,'%Y-%m-%d%H:%M:%S.%f').replace(tzinfo=datetime.timezone.utc)

            seconds = file['Geolocation/Scnlin_mscnt'][:]/1000
            seconds_unwrap = np.unwrap(seconds,12*60*60)

            self.start_time = ob_start_datetime
            self.start_time_timestamp = ob_start_datetime.timestamp()
            self.end_time = ob_end_datetime
            self.end_time_timestamp = ob_end_datetime.timestamp()

            # Seconds since start of epoch, 01 Jan 1970
            self.timearr = seconds_unwrap - seconds_unwrap[0] + self.start_time_timestamp
            self.aqtime = np.tile(self.timearr,(98,1)).T

            self.land_use = file["Geolocation"]["LandCover"][:]
            self.land_sea_mask = file["Geolocation"]["LandSeaMask"][:]
            self.DEM = file["Geolocation"]["DEM"][:]

        self.apply_mask()


    def read_tropics(self):
        """
        Read a TROPICS data file.
        """

        logger = logging.getLogger(__name__)
        #logging.basicConfig(level = logging.INFO)
        logger.info('Loading FY swath name: %s', self.fname)

        # For mapping the variable frequency bands to channels.
        # Band 1 = Ch.1; Band 2 = Ch. 2-4; Band 3 = Ch. 5-8;
        # Band 4 = Ch. 9-11; Band 5 = Ch. 12
        channels = 12

        with h5py.File(self.fname,'r') as file:

            # Lats/lons are by band, but data is by channel.
            # Duplicate the lats/lons to match the data's channel organization.
            # Brute force array duplication -- probably better ways of doing this.
            lats = file["losLat_deg"][:]
            self.lat = np.zeros([channels, lats.shape[1], lats.shape[2]])
            self.lat[0, :, :] = lats[0,:,:]
            self.lat[1, :, :] = lats[1,:,:]
            self.lat[2, :, :] = lats[1,:,:]
            self.lat[3, :, :] = lats[1,:,:]
            self.lat[4, :, :] = lats[2,:,:]
            self.lat[5, :, :] = lats[2,:,:]
            self.lat[6, :, :] = lats[2,:,:]
            self.lat[7, :, :] = lats[2,:,:]
            self.lat[8, :, :] = lats[3,:,:]
            self.lat[9, :, :] = lats[3,:,:]
            self.lat[10, :, :] = lats[3,:,:]
            self.lat[11, :, :] = lats[4,:,:]

            lons = file["losLon_deg"][:]
            self.lon = np.zeros([channels, lons.shape[1], lons.shape[2]])
            self.lon[0, :, :] = lons[0,:,:]
            self.lon[1, :, :] = lons[1,:,:]
            self.lon[2, :, :] = lons[1,:,:]
            self.lon[3, :, :] = lons[1,:,:]
            self.lon[4, :, :] = lons[2,:,:]
            self.lon[5, :, :] = lons[2,:,:]
            self.lon[6, :, :] = lons[2,:,:]
            self.lon[7, :, :] = lons[2,:,:]
            self.lon[8, :, :] = lons[3,:,:]
            self.lon[9, :, :] = lons[3,:,:]
            self.lon[10, :, :] = lons[3,:,:]
            self.lon[11, :, :] = lons[4,:,:]

            self.data  = file["tempBrightE_K"][:]

            year = file['Year'][:]
            month = file['Month'][:]
            day = file['Day'][:]
            hour = file['Hour'][:]
            minute = file['Minute'][:]

            # Scan line time in Seconds Since Epoch, 01 Jan 1970
            self.timearr = [datetime.datetime(
                year[x], month[x], day[x], hour[x], minute[x]).timestamp()
                for x in range(len(year))]

            # Each data point's time in SSE
            self.aqtime = np.tile(self.timearr,(81,1)).T

            # LOS incidence angle, by band (5)
            incidence = file["losScan_deg"][:]

            # Convert LOS incidence by band to angle by channel
            self.inc = np.zeros([channels, incidence.shape[1], incidence.shape[2]])
            self.inc[0, :, :] = incidence[0,:,:]
            self.inc[1, :, :] = incidence[1,:,:]
            self.inc[2, :, :] = incidence[1,:,:]
            self.inc[3, :, :] = incidence[1,:,:]
            self.inc[4, :, :] = incidence[2,:,:]
            self.inc[5, :, :] = incidence[2,:,:]
            self.inc[6, :, :] = incidence[2,:,:]
            self.inc[7, :, :] = incidence[2,:,:]
            self.inc[8, :, :] = incidence[3,:,:]
            self.inc[9, :, :] = incidence[3,:,:]
            self.inc[10, :, :] = incidence[3,:,:]
            self.inc[11, :, :] = incidence[4,:,:]

            self.secant_inc = 1/np.cos(np.radians(self.inc))

        self.apply_mask()


    def kl_transform(self):
        """
        Function to perform a karhunen-loeve transform on the data
        using the channels specified in the channel_list.
        """

        logger = logging.getLogger(__name__)
        logger.info('Performing KL transform on FY data')

        self.kl_data = np.full_like(self.data,np.nan)

        # Remove an average along the 0 axis
        zeromeandata = self.data - np.nanmean(self.data,axis=0)

        # Flatten the data
        zeromeandata = zeromeandata.flatten()

        # Remove nans from the lon and lat arrays
        val,vec = np.linalg.eig(np.cov(zeromeandata))
        klt = np.dot(vec,zeromeandata)

        # Reshape the kl transform array to original size
        # and put it in the kl_data array within the swath class
        self.kl_data[:,:] = klt.reshape(self.data.shape)
        self.kl_vals = val


    def compress(self):
        """
        Go through each variable, remove nans and compress arrays.
        """

        logger = logging.getLogger(__name__)
        logger.info('Compressing data')

        for var in self.__dict__:
            if not isinstance(self.__dict__[var],np.ndarray):
                continue
            if self.__dict__[var].ndim == 2:
                self.__dict__[var] = self.__dict__[var][self.mask]
            elif self.__dict__[var].ndim == 3:
                self.__dict__[var] = self.__dict__[var][:,self.mask]


    def select_data(self):
        """
        Create a 2D time-series of data for input into a neural net: [var, time].
        Uses the user-specified variables in variable_list to create the array.
        """

        logger = logging.getLogger(__name__)
        logger.info('Selecting timeseries data')

        if self.variable_list is None:
            logger.error('No variables selected')
            return

        # Channel indices in the FY3 brightness temperature data array.
        # Channel peak weighting altitude estimated from ECMWF, Lu et al. (2015)
        mwhs_channels = {
            'mwhs_ch1': 0,              # 89 GHz
            'mwhs_ch2': 1,              # 118.75±0.08 GHz
            'mwhs_ch3': 2,              # 118.75±0.2
            'mwhs_ch4': 3,              # 118.75±0.3  16 km
            'mwhs_ch5': 4,              # 118.75±0.8  10 km
            'mwhs_ch6': 5,              # 118.75±1.1  8 km
            'mwhs_ch7': 6,              # 118.75±2.5  2.5 km
            'mwhs_ch8': 7,              # 118.75±3.0  (surface)
            'mwhs_ch9': 8,              # 118.75±5.0  (surface)
            'mwhs_ch10': 9,             # 150 GHz  (surface)
            'mwhs_ch11': 10,            # 183±1 GHz 8 km
            'mwhs_ch12': 11,            # 183±1.8   7 km
            'mwhs_ch13': 12,            # 183±3     6 km
            'mwhs_ch14': 13,            # 183±4.5   5 km
            'mwhs_ch15': 14,            # 183±7     3.5 km
            }

        self.compress()

        # Define the neural net array
	# TBD this looks wrong. Recheck and created unit test.
        self.nn_data = np.zeros([self.data.shape[1], len(self.variable_list)])

        # For every variable requested, insert its data into the neural net array.
        for i in range(len(self.variable_list)):

            var = self.variable_list[i]

            # Find the requested variable in the class data dictionary
            if var in self.__dict__:
                self.nn_data[:,i] = self.__dict__[var]

            # Special case: extract a MWHS channel from the data array
            elif var.lower().find('mwhs_ch') > -1:
                self.nn_data[:,i] = self.data[mwhs_channels[var],:]

            # Variable not found.
            else:
                logger.error('Variable not found: %s', var)
                continue


# Unit testing
class TestMethods(unittest.TestCase):

    def test_swath(self):

        path = os.path.join(config.test_fy3d_dir, config.test_fy3d_file)
        swath = Swath(path, inc_angle_range=[0,60], aoi=[-180,180,-60,60],
                      variable_list=['mwhs_ch2', 'lat', 'land_use'])

        self.assertEqual(np.nanmax(swath.data), 289.0460205078125)

        swath.select_data()

        self.assertEqual(np.nanmax(swath.nn_data[:,0]), 235.46044921875)
        self.assertEqual(np.nanmax(swath.nn_data[:,1]), 59.99937438964844)
        self.assertEqual(np.nanmean(swath.nn_data[:,2]), 82.03946484985123)


if __name__ == '__main__':

    unittest.main()
