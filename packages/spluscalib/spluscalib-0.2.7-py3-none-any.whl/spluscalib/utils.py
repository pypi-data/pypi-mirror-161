# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                                     Utils
# ******************************************************************************


"""
This file includes all the functions used by the different scripts of the
calibration pipeline.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

general
    makedir()
    load_field_list()
    fz2fits()
    load_data()
    concat_data
    mean_robust()
    translate_filter_standard()

pipeline configuration file
    pipeline_conf()
    load_conf()
    convert_param_to_pipeline_types()
    convert_to_system_path()

pipeline log file
    printlog()
    gen_logfile_name()
    get_time_stamp()

aperture photometry
    get_sex_config()
    splus_image_satur_level()
    splus_image_gain()
    splus_image_seeing()
    get_swarp_config()
    update_detection_header()
    get_sexconf_fwhm()
    plot_sex_diagnostic()

psf photometry
    get_dophot_config()
    psf_flagstar()
    format_dophot_catalog()
    plot_dophot_diagnostic()

xy inhomogeneities correction
    intersection_2lines()
    align_splus_xy()
    apply_xy_correction()

aperture correction
    get_apertures_from_sexconf()
    obtain_aperture_correction()
    star_selector()
    growth_curve()
    growth_curve_plotter()

master photometry
    extract_sex_photometry()
    extract_psf_photometry()
    format_master_photometry()

crossmatch
    download_vizier_catalog_for_splus_field()
    download_galex()
    download_refcat2()
    download_ivezic()
    download_sdss()
    download_gaiadr2()
    download_gaia()
    download_reference()
    crossmatch_catalog_name()

extinction_correction
    correct_extinction_schlegel()
    correct_extinction_gorski()
    correct_extinction_gaiadr2()
    correct_extinction()

calibration
    zp_write()
    zp_read()
    zp_add()
    calibration_suffix()
    sed_fitting()
    get_filter_zeropoint()
    zp_estimate()
    zp_gaiascale()
    zp_apply()
    plot_zp_fitting()
    zp_estimate_stlocus()

catalog_preparation
    catalog_aperphot_filter()
    catalog_aperphot_det()
    catalog_psfphot_filter()

diagnostics

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
A casual user of the spluscalib package should never have to worry about the
content of this file.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
in python:
from spluscalib import utils

----------------
"""

################################################################################
# Import external packages

import os
import sys
import copy
import datetime
import warnings

import termcolor
from termcolor import cprint

from statistics import mode

# Astropy
from astropy import units as u
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import pixel_to_skycoord
from astropy.time import Time
from astropy.table import Table
from astropy.coordinates import SkyCoord, Distance

# Astroquery
from astroquery.vizier import Vizier

# sfdmap
import sfdmap

# Numpy
import numpy as np

# Pandas
import pandas as pd

# Scipy
from scipy.stats import linregress
from scipy.interpolate import interp2d
from scipy.ndimage import gaussian_filter

# Sklearn
from sklearn.neighbors import KernelDensity

# Matplotlib
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec

# Shapely
from shapely.geometry import Point, Polygon


################################################################################
# Setup pipeline directories

pipeline_path = os.path.split(__file__)[0]
spluscalib_path = os.path.split(pipeline_path)[0]

sys.path.append(spluscalib_path)

################################################################################
# Import splucalib packages

from spluscalib import dust_laws
from spluscalib import sed_fitting as sf

################################################################################
# General


def makedir(directory):
    """
    Checks if a directory exists and, if not, creates it.

    Parameters
    ----------
    directory : str
        Directory to be created
    """

    if not os.path.exists(directory):
        cprint(f"Creating {directory}", color="green")
        os.mkdir(directory)


def load_field_list(data_file):
    """
    Loads a list of fields in a file (one per line)

    Parameters
    ----------
    data_file : str
        Location with field list file

    Returns
    -------
    Sized
        list of fields
    """

    fields = []
    with open(data_file, 'r') as f:
        file_lines = f.readlines()

    for i in range(len(file_lines)):
        fields.append(file_lines[i].replace("\n", ""))

    return fields


def fz2fits(image):
    """
    Converts S-PLUS images from .fz to .fits

    Parameters
    ----------
    image : str
        Location of S-PLUS .fz image

    Returns
    -------
    Saves S-PLUS fits image in the same location
    """

    data = fits.open(image)[1].data
    header = fits.open(image)[1].header
    imageout = image[:-2] + 'fits'

    fits.writeto(imageout, data, header, overwrite=True)


def load_data(data_file):
    """
    Loads a catalog that is either in fits format, or can be read as a pandas
    dataframe, and returns a dataframe

    Parameters
    ----------
    data_file : str
        Location of the catalog

    Returns
    -------
    pd.DataFrame
        Catalog's dataframe
    """

    # If necessary, transform from fits table to data frame
    if os.path.splitext(data_file)[1] == '.fits':
        fits_data = Table.read(data_file, format='fits')
        ref_data  = fits_data.to_pandas()

    else:
        ref_data = pd.read_csv(data_file, delim_whitespace=True, escapechar='#',
                               skipinitialspace=True)

    ref_data.columns = ref_data.columns.str.replace(' ', '')

    return ref_data


def select_columns(catalog, save_file,
                   select_columns = None, rename_columns = None):
    """

    Creates a copy of 'catalog' keeping only the selected columns, can also
    be used to rename columns

    Parameters
    ----------
    catalog : str
        Location of input catalog
    save_file : str
        Location to save resulting catalog
    select_columns : list
        List of column names to keep in the save_file
    rename_columns

    Returns
    -------
    saves files with selected columns
    """

    cat_data = load_data(catalog)

    if select_columns is not None:
        selected_data = cat_data.loc[:,select_columns]
    else:
        selected_data = cat_data.loc[:,:]

    if rename_columns is not None:
        selected_data.rename(columns = rename_columns)

    with open(save_file, 'w') as f:
        f.write("# ")
        selected_data.to_csv(f, index = False, sep = " ")


def concat_data(files_list, save_file):
    """
    Concatenates a list of catalogs (can be both .fits or .cat [ascii])

    Parameters
    ----------
    files_list : list
        List of location of the catalogs to be concatenated
    save_file : str
        Location to save the result

    Returns
    -------
    Saves the concatenated catalog in .cat [ascii] format
    """

    df_list = []

    for cat_file in files_list:
        print(cat_file)
        df_list.append(load_data(cat_file))

    df_all = pd.concat(df_list)

    with open(save_file, 'w') as f:
        f.write("# ")
        df_all.to_csv(f, index = False, sep = " ")


def mean_robust(x, low=3, high=3):
    """
    Estimates the mean using a sigma clip between 'low'-sigma and 'high'-sigma

    Parameters
    ----------
    x : list
        Array-like unidimensional data
    low : float
        Lower cut [units of sdev]
    high : float
        Top cut [units of sdev]

    Returns
    -------
    float
        mean of the distribution after a sigma-clip
    """

    x = np.array(x)

    mean_x = np.nanmean(x)
    std_x = np.nanstd(x)

    x = x[(x > (mean_x - low * std_x)) & (x < (mean_x + high * std_x))]

    return np.mean(x)


def translate_filter_standard(filt):
    """
    Translates filter name from observation database to publication standards
    Parameters
    ----------
    filt: str
        Name of the filter in the observation database

    Returns
    -------
    str
        Filter name in the publication standard
    """

    filter_translation = {'U': 'u', 'SPLUS_U': 'u',
                          'G': 'g', 'SPLUS_G': 'g',
                          'R': 'r', 'SPLUS_R': 'r',
                          'I': 'i', 'SPLUS_I': 'i',
                          'Z': 'z', 'SPLUS_Z': 'z',
                          'F378': 'J0378', 'SPLUS_F378': 'J0378',
                          'F395': 'J0395', 'SPLUS_F395': 'J0395',
                          'F410': 'J0410', 'SPLUS_F410': 'J0410',
                          'F430': 'J0430', 'SPLUS_F430': 'J0430',
                          'F515': 'J0515', 'SPLUS_F515': 'J0515',
                          'F660': 'J0660', 'SPLUS_F660': 'J0660',
                          'F861': 'J0861', 'SPLUS_F861': 'J0861'}

    return filter_translation[filt]


################################################################################
# Configuration file


def pipeline_conf(conf_file):
    """
    Reads the configuration file including the default configuration

    Parameters
    ----------
    conf_file : str
        The location of the configuration file

    Returns
    -------
    dict
        a dictionary containing the parameters given in the configuration file.
        Parameter names are dict keys, and values are dict values.
    """

    # Load default configuration
    default_conf_file = os.path.join(pipeline_path,
                                     'steps',
                                     'resources',
                                     'default_config.conf')

    default_conf = load_conf(default_conf_file)

    # Load user configuration
    conf = load_conf(conf_file, default_conf)

    # Convert defaults to system path format
    conf = convert_to_system_path(conf)

    return conf


def load_conf(conf_file, default_conf=None):
    """
    Reads the configuration file and returns a dictionary with the parameters

    Parameters
    ----------
    conf_file : str
        The location of the configuration file

    default_conf : dict
        dictionary containing previously loaded parameters given in
        another (usually default) configuration file.

    Returns
    -------
    dict
        a dictionary containing the parameters given in the configuration file.
        Parameter names are dict keys, and values are dict values.
    """

    # Open the file
    with open(conf_file, 'r') as c:

        # Read the file
        raw_file = c.readlines()

    if default_conf is not None:
        conf = default_conf
    else:
        conf = {}

    for line in raw_file:

        # Ignore empty lines
        if line == '\n':
            continue

        # Ignore comment line
        if line[0] == '#':
            continue

        # Remove inline comment
        line = line.split("#")[0]

        # Remove extra spaces, tabs and linebreak
        line = " ".join(line.split())

        # Get parameter name
        param = line.split(" ")[0]

        # Get value
        value = "".join(line.split(" ")[1:])

        # Transform multiple values into list
        if ',' in value:
            value = value.split(',')

        # Assign param and value to dictionary
        conf[param] = value

    # Add run path if not given.
    if 'run_path' not in list(conf.keys()):
        try:
            conf['run_path'] = conf['save_path']
        except KeyError:
            pass

    # Convert parameters to expected types
    conf = convert_param_to_pipeline_types(conf)

    return conf


def convert_param_to_pipeline_types(conf):
    """
    Converts the parameters in the configuration file to the right python type

    Parameters
    ----------
    conf : dict
        pipeline config dictionary read in load_conf

    Returns
    -------
    dict
        dictionary with values converted to the expected type
    """

    ints = ['calibration_flag',
            'stellar_locus_N_bins']

    floats = ['inst_zp',
              'apercorr_max_aperture',
              'apercorr_diameter',
              'apercorr_starcut']

    bools = ['use_weight',
             'remove_fits',
             'sex_XY_correction',
             'reference_in_individual_files',
             'model_fitting_bayesian',
             'model_fitting_ebv_cut',
             'create_aper_catalog']

    list_of_floats = ['XY_correction_xbins',
                      'XY_correction_ybins',
                      'apercorr_s2ncut',
                      'zp_fitting_mag_cut',
                      'stellar_locus_color_range',
                      'gaia_zp_fitting_mag_cut']

    list_of_strings = ['run_steps',
                       'filters',
                       'detection_image',
                       'reference_catalog',
                       'external_sed_fit',
                       'external_sed_pred',
                       'stellar_locus_fit',
                       'stellar_locus_color_ref',
                       'internal_sed_fit',
                       'internal_sed_pred',
                       'gaiascale_sed_fit',
                       'gaiascale_sed_pred',
                       'diagnostic_sed_fit']

    for key in conf.keys():

        # Convert int type
        if key in ints:
            if not isinstance(conf[key], int):
                conf[key] = int(conf[key])

        # Convert float type
        elif key in floats:
            if not isinstance(conf[key], float):
                conf[key] = float(conf[key])

        # Convert boolean type
        elif key in bools:

            if not isinstance(conf[key], bool):
                if conf[key].lower() == 'true':
                    conf[key] = True

                elif conf[key].lower() == 'false':
                    conf[key] = False

                else:
                    raise ValueError("Invalid configuration for %s" % key)

        # Convert list of floats
        elif key in list_of_floats:
            if isinstance(conf[key], list):
                for i in range(len(conf[key])):
                    conf[key][i] = float(conf[key][i])

            else:
                raise ValueError("Invalid configuration for %s" % key)

        # Convert list of strings
        elif key in list_of_strings:
            if not isinstance(conf[key], list):
                conf[key] = [conf[key]]

    return conf


def convert_to_system_path(conf):
    """
    Convert paths to system path format and include path to the pipeline

    Parameters
    ----------
    conf : dict
        pipeline config dictionary read in load_conf

    Returns
    -------
    dict
        dictionary with formated paths
    """

    paths = ['save_path',
             'run_path',
             'path_to_sex',
             'path_to_swarp',
             'path_to_stilts',
             'path_to_dophot',
             'path_to_images',
             'sex_config',
             'sex_param',
             'swarp_config',
             'dophot_config',
             'XY_correction_maps_path',
             'extinction_maps_path',
             'path_to_reference',
             'path_to_models',
             'offset_to_splus_refcalib',
             'stellar_locus_reference',
             'path_to_gaia']

    for key in conf.keys():

        if key in paths:

            # Convert to system path format
            path_list = conf[key].split('/')

            if path_list[0] == '.':
                path_sys = os.path.join(pipeline_path, *path_list[1:])

            elif path_list[0] == '..':
                path_sys = os.path.join(spluscalib_path, *path_list[1:])

            else:
                path_sys = os.path.join(*path_list)

            # Replace default pipeline path to user pipeline path
            if "{pipeline_path}" in path_sys:
                path_sys = path_sys.format(pipeline_path=pipeline_path)

            # Replace default spluscalib path to user spluscalib path
            if "{spluscalib_path}" in path_sys:
                path_sys = path_sys.format(spluscalib_path=spluscalib_path)

            # Add initial /
            if path_sys[0] != '/':
                path_sys = '/' + path_sys

            # Remove double /
            path_sys = path_sys.replace("//", "/")

            # Update path to system path
            conf[key] = path_sys

    return conf


################################################################################
# Log

def printlog(message, log_file, **kwargs):
    """
    Prints message to console and save it to the log file

    Parameters
    ----------
    message : str
        message to print and save to log file

    log_file : str
        the location of the log file
    """
    
    termcolor.cprint(message, **kwargs)

    # Get time stamp
    stamp = get_time_stamp()

    try:
        with open(log_file, 'a') as log:
            log.write(stamp + message)
            log.write('\n')

    except FileNotFoundError:
        with open(log_file, 'w') as log:
            log.write(stamp + message)
            log.write('\n')


def gen_logfile_name(log_file, first_run = True):
    """
    Generates the name of the log file. If desired file already exists,
    adds _*number* in the end of the file name.
    Used to not overwrite existing log files.

    Parameters
    ----------
    log_file : str
        Desired log file location. Must end in .log

    first_run : bool
        Used internally to control recursivity

    Returns
    -------
    str
        Log file location.
    """

    if log_file[-4:] != '.log':
        raise NameError("log file must end in .log")

    if not os.path.exists(log_file):
        return log_file

    else:
        if first_run:
            new_file = log_file.replace(".log", "_1.log")
            return gen_logfile_name(new_file, first_run=False)

        else:
            log_number = int(log_file.split("_")[-1][:-4])
            new_file = log_file.replace(f"{log_number}.log",
                                        f"{log_number+1}.log")

            return gen_logfile_name(new_file, first_run = False)


def get_time_stamp():
    """
    Generates a time stamp

    Returns
    ----------
    str
        current time stamp
    """

    ct = datetime.datetime.now()

    stamp = "[{year}/{mon:02d}/{day:02d} {hh:02d}:{mm:02d}:{ss:02d}] ".format(
        year=ct.year,
        mon=ct.month,
        day=ct.day,
        hh=ct.hour,
        mm=ct.minute,
        ss=ct.second)

    return stamp


################################################################################
# Photometry

###############################
# Single / Dual mode photometry

# Generate Configuration file
def get_sex_config(save_file, default_sexconfig, default_sexparam,
                   catalog_file, image_file, inst_zp, path_to_sex,
                   use_weight=False, mode=None, check_aperima=None,
                   check_segima=None, detection_file=None):

    # Read general configuration file
    with open(default_sexconfig, 'r') as f:
        sex_config = f.readlines()
        sex_config = "".join(sex_config)

    # Read parameters from image header
    satur = splus_image_satur_level(image_file)
    seeing = splus_image_seeing(image_file)
    gain = splus_image_gain(image_file)

    # Update sexconfig
    sex_config = sex_config.format(catalog_file=catalog_file,
                                   param_file=default_sexparam,
                                   path_to_sex=path_to_sex,
                                   inst_zp=inst_zp,
                                   satur=satur,
                                   seeing=seeing,
                                   gain=gain)

    # Include weight image
    if use_weight:
        wimage_file = image_file.replace(".fits", "weight.fits")

        if mode == 'single':
            sex_config += ("WEIGHT_TYPE MAP_WEIGHT\n"
                           "WEIGHT_IMAGE {wimage}").format(wimage=wimage_file)

        elif mode == 'dual':

            wdetection_file = detection_file.replace(".fits", "weight.fits")

            sex_config += ("WEIGHT_TYPE MAP_WEIGHT, MAP_WEIGHT\n"
                           "WEIGHT_IMAGE {wdetection}, {wimage}"
                           "").format(wimage=wimage_file,
                                      wdetection=wdetection_file)

    # Add aper and segm image
    if check_aperima is not None:
        sex_config += ("\nCHECKIMAGE_TYPE APERTURES,SEGMENTATION\n"
                       "CHECKIMAGE_NAME {aperima}, {segima}"
                       "").format(aperima=check_aperima,
                                  segima=check_segima)

    # Save config file
    with open(save_file, 'w') as f:
        f.write(sex_config)



def splus_image_satur_level(image_file):
    """
    Reads the S-PLUS image header and returns the saturation level

    Parameters
    ----------
    image_file : str
        Location of S-PLUS image (fits or fz)

    Returns
    -------
    float
        Value of saturation level ('SATURATE')
    """

    # Get file extension
    extension = os.path.splitext(image_file)[1][1:]

    if extension == 'fz':
        head = fits.open(image_file)[1].header

    elif extension == 'fits':
        head = fits.open(image_file)[0].header

    else:
        raise ValueError("Image extension must be 'fits' or 'fz'")

    satur = float(head['SATURATE'])

    return satur


def splus_image_gain(image_file):
    """
    Reads the S-PLUS image header and returns the gain

    Parameters
    ----------
    image_file : str
        Location of S-PLUS image (fits or fz)

    Returns
    -------
    float
        Value of gain ('GAIN')
    """

    # Get file extension
    extension = os.path.splitext(image_file)[1][1:]

    if extension == 'fz':
        head = fits.open(image_file)[1].header

    elif extension == 'fits':
        head = fits.open(image_file)[0].header

    else:
        raise ValueError("Image extension must be 'fits' or 'fz'")

    gain = float(head['GAIN'])

    return gain


def splus_image_seeing(image_file):
    """
    Reads the S-PLUS image header and returns the observation seeing

    Parameters
    ----------
    image_file : str
        Location of S-PLUS image (fits or fz)

    Returns
    -------
    float
        Value of gain ('HIERARCH OAJ PRO FWHMSEXT')
    """

    # Get file extension
    extension = os.path.splitext(image_file)[1][1:]

    if extension == 'fz':
        head = fits.open(image_file)[1].header

    elif extension == 'fits':
        head = fits.open(image_file)[0].header

    else:
        raise ValueError("Image extension must be 'fits' or 'fz'")

    try:
        seeing = float(head['HIERARCH OAJ PRO FWHMSEXT'])
    except KeyError:
        seeing = float(head['HIERARCH MAR PRO FWHMSEXT'])

    return seeing


def get_swarp_config(save_file, default_swarpconfig, detection_image_out,
                     detection_weight_out, resample_dir, xml_output,
                     combine_type, weight_type, ref_image):

    """
    Generates the swarp configuration file, including field specific paths

    Parameters
    ----------
    save_file : str
        Location to save the swarp configuration file
    default_swarpconfig : str
        Location of the general swarp splus configuration file
    detection_image_out : str
        Location to save the generated detection image
    detection_weight_out : str
        Location to save the generated detection image weight
    resample_dir : str
        Directory to save the resampled fits images
    xml_output : str
        Location to save the swarp xml output
    combine_type : str
        swarp configuration parameter COMBINE_TYPE
    weight_type : str
        swarp configuration parameter WEIGHT_TYPE
    ref_image : str
        image to be used as reference to take center coordinates

    Returns
    -------

    """
    # Read general configuration file
    with open(default_swarpconfig, 'r') as f:
        swarp_config = f.readlines()
        swarp_config = "".join(swarp_config)

    # Get center
    extension = os.path.splitext(ref_image)[1][1:]

    if extension == 'fz':
        head = fits.open(ref_image)[1].header
    elif extension == 'fits':
        head = fits.open(ref_image)[0].header
    else:
        raise ValueError("Image extension must be 'fits' or 'fz'")

    center_ra = float(head['CRVAL1'])
    center_dec = float(head['CRVAL2'])

    center = f"{center_ra}, {center_dec}"

    # Update swarp_config
    swarp_config = swarp_config.format(image_out    = detection_image_out,
                                       weight_out   = detection_weight_out,
                                       resample_dir = resample_dir,
                                       xml_output   = xml_output,
                                       combine_type = combine_type,
                                       weight_type  = weight_type,
                                       center       = center)

    # Save config file
    with open(save_file, 'w') as f:
        f.write(swarp_config)


def update_detection_header(detection_image, image_list_file):
    """
    Updates detection image header

    Parameters
    ----------
    detection_image : str
        Location of the detection image file
    image_list_file : str
        Location of the file listing the combined images
    """

    # Read list of images
    with open(image_list_file, 'r') as im_list:
        image_list = im_list.readlines()

    # Remove linebreaks
    for i in range(len(image_list)):
        image_list[i] = image_list[i].replace("\n", "")

    # Load images
    images = []

    for i in range(len(image_list)):
        images.append(fits.open(image_list[i]))

    # Load detection image
    det_image = fits.open(detection_image)

    # Update parameters
    det_image[0].header['AUTHOR'] = 'spluscalib'

    # Add new parameters
    FILTER   = ''
    NCOMBINE = 0
    TEXPOSED = 0.
    EFECTIME = 0.

    for i in range(len(image_list)):
        filter_i = images[i][0].header['FILTER'].split("_swp.fits")[0]
        filter_i = filter_i.split("_")[-1]

        FILTER += filter_i+','

        NCOMBINE += int(images[i][0].header['NCOMBINE'])
        TEXPOSED += float(images[i][0].header['TEXPOSED'])
        EFECTIME += float(images[i][0].header['EFECTIME'])

    # Remove last comma from FILTER
    FILTER = FILTER[:-1]

    # Add to the header
    det_image[0].header['FILTER'] = FILTER
    det_image[0].header['NCOMBINE'] = NCOMBINE
    det_image[0].header['TEXPOSED'] = TEXPOSED
    det_image[0].header['EFECTIME'] = EFECTIME

    det_image[0].header['FILENAME'] = os.path.split(detection_image)[1]

    # Add image list
    for i in range(len(image_list)):
        image_i = os.path.split(image_list[i])[1]
        param_name = f'IMAGE{i:.0f}'
        det_image[0].header[param_name] = image_i

    # List of params to take from image0
    inherit_params = ['HIERARCH OAJ QC NCMODE',
                      'HIERARCH OAJ QC NCMIDPT',
                      'HIERARCH OAJ QC NCMIDRMS',
                      'HIERARCH OAJ QC NCNOISE',
                      'HIERARCH OAJ QC NCNOIRMS',
                      'HIERARCH OAJ PRO FWHMSEXT',
                      'HIERARCH OAJ PRO FWHMSRMS',
                      'HIERARCH OAJ PRO FWHMMEAN',
                      'HIERARCH OAJ PRO FWHMBETA',
                      'HIERARCH OAJ PRO FWHMnstars',
                      'HIERARCH OAJ PRO Ellipmean',
                      'HIERARCH OAJ PRO PIPVERS',
                      'HIERARCH OAJ PRO REFIMAGE',
                      'HIERARCH OAJ PRO REFAIRMASS',
                      'HIERARCH OAJ PRO REFDATEOBS',
                      'HIERARCH OAJ PRO SWCMB1',
                      'HIERARCH OAJ PRO SWSCALE1',
                      'HIERARCH OAJ PRO SWCMB2',
                      'HIERARCH OAJ PRO SWSCALE2',
                      'HIERARCH OAJ PRO SWCMB3',
                      'HIERARCH OAJ PRO SWSCALE3']

    remove_params = []

    for param in inherit_params:
        try:
            det_image[0].header[param] = images[0][0].header[param]
        except KeyError:
            remove_params.append(param)

            msg = (f"Image {image_list[0]} does not contain header parameter "
                   f"{param}. This parameter will not be added to the "
                   f"detection image header.")
            warnings.warn(msg)

    for param in remove_params:
        inherit_params.remove(param)

    # Adding comments to the header
    det_image[0].header.add_comment(" Updated Header Keywords", after="PSCALET2")
    det_image[0].header.add_comment("", after="PSCALET2")

    det_image[0].header.add_comment(" List of combined images", after="EFECTIME")
    det_image[0].header.add_comment("", after="EFECTIME")

    det_image[0].header.add_comment(" Params from IMAGE0",
                                    after=inherit_params[-1])
    det_image[0].header.add_comment("", after=inherit_params[-1])

    # Save updated detection image
    det_image.writeto(detection_image, overwrite=True)


def get_sexconf_fwhm(sexconf):
    """
    Reads a SExtractor config file and extracts the FWHM value

    Parameters
    ----------
    sexconf : str
        Location of SExtractor config file

    Returns
    -------
    float
        FWHM used in SExtractor configuration
    """


    fwhm = None

    with open(sexconf, 'r') as f:
        lines = f.readlines()

        for line in lines:
            line = line.split()

            if line[0] == 'SEEING_FWHM':
                fwhm = float(line[1])
                break

    return fwhm


def plot_sex_diagnostic(catalog, save_file, s2ncut, starcut, sexconf, filt,
                        mag_cut = (10, 25)):
    """
    Makes diagnostic plots of the photometry in a given SExtractor output

    Parameters
    ----------
    catalog : str
        Location of SExtractor output catalog
    save_file : str
        Location to save plots
    s2ncut : list
        [min, max] values of the s2n calibration cut
    starcut : float
        min value of the class_star calibration cut
    sexconf : str
        Location of SExtractor configuration file
    filt : str
        Name of the photometric filter

    Returns
    -------
    Saves diagnostic plots
    """

    sexcat = Table.read(catalog)

    select, medianFWHM = star_selector(catalog       = sexcat,
                                       s2ncut        = s2ncut,
                                       starcut       = starcut,
                                       mag_partition = 2,
                                       verbose       = False)

    fig, axs = plt.subplots(3, figsize = [5,15])

    #################
    # Plot class star

    # Plot all points
    axs[0].scatter(sexcat['MAG_AUTO'], sexcat['CLASS_STAR'],
                   c="#AAAAAA", s=10, alpha=0.1)

    # Plot selection
    axs[0].scatter(select['MAG_AUTO'], select['CLASS_STAR'],
                   c="#2266FF", s=10, alpha=0.3,
                   label=f"s2ncut: {s2ncut}\n& starcut: {starcut}")

    # Plot cut line
    axs[0].hlines(starcut, mag_cut[0], mag_cut[1],
                  colors="#2266FF", zorder=1)

    # Plot grid lines
    axs[0].hlines(np.arange(-0.1, 1.1, 0.1), mag_cut[0], mag_cut[1],
                  colors="#EEEEEE", zorder=-1)

    axs[0].legend(loc=1)
    axs[0].set_xlim(mag_cut)
    axs[0].set_ylim([-0.1, 1.1])
    axs[0].set_ylabel('CLASS_STAR')
    axs[0].minorticks_on()

    ##########
    # Plot s2n

    # Plot all points
    s2n_cat = sexcat['FLUX_AUTO'] / sexcat['FLUXERR_AUTO']
    axs[1].scatter(sexcat['MAG_AUTO'], s2n_cat,
                   c="#AAAAAA", s=10, alpha=0.1)

    # Plot selection
    s2n_sel = select['FLUX_AUTO'] / select['FLUXERR_AUTO']
    axs[1].scatter(select['MAG_AUTO'], s2n_sel,
                   c="#2266FF", s=10, alpha=0.3)

    # Plot cut line
    axs[1].hlines(s2ncut, mag_cut[0], mag_cut[1],
                  colors="#2266FF", zorder=1)

    # Plot grid lines
    axs[1].hlines([0.1, 1, 10, 100, 1000, 10000], mag_cut[0], mag_cut[1],
                  colors="#EEEEEE", zorder=-1)

    axs[1].set_xlim(mag_cut)
    axs[1].set_yscale('log')
    axs[1].set_ylim([0.1, 2 * s2ncut[1]])
    axs[1].set_ylabel('S/N')
    axs[1].minorticks_on()

    ###########
    # Plot FWHM

    # Plot all points
    axs[2].scatter(sexcat['MAG_AUTO'], sexcat['FWHM_WORLD'] * 3600,
                   c="#AAAAAA", s=10, alpha=0.1)

    # Plot selection
    axs[2].scatter(select['MAG_AUTO'], select['FWHM_WORLD'] * 3600,
                   c="#2266FF", s=10, alpha=0.3, zorder=2)

    # Plot cut line
    fwhm_config = get_sexconf_fwhm(sexconf=sexconf)
    fwhm_estimated = medianFWHM * 3600

    axs[2].plot([mag_cut[0], mag_cut[1]], [fwhm_config, fwhm_config],
                color="#FF6622", zorder=1,
                label=r"FWHM$_{\mathrm{config}}$" + f": {fwhm_config:.3f}")

    axs[2].plot([mag_cut[0], mag_cut[1]], [fwhm_estimated, fwhm_estimated],
                color="#22AA66", zorder=1,
                label=r"FWHM$_{\mathrm{estimated}}$" + f": {fwhm_estimated:.3f}")

    # Plot grid lines
    axs[2].hlines(np.arange(0, 15, 2), mag_cut[0], mag_cut[1],
                  colors="#EEEEEE", zorder=-1)

    axs[2].legend(loc=2)
    axs[2].set_xlim(mag_cut)
    axs[2].set_ylim([0, 15])
    axs[2].set_ylabel('FWHM [arcsec]')
    axs[2].minorticks_on()

    axs[2].set_xlabel(f"{filt}_AUTO [inst]")

    plt.subplots_adjust(left=0.14, right=0.98, top=0.98, bottom=0.06, hspace=0.1)

    plt.savefig(save_file)
    plt.close(fig)


###############################
# PSF photometry


def get_dophot_config(image_in, objects_out, config_file,
                      apercorr_max_aperture):
    """
    Returns the dophot tuneup file for a given S-PLUS image

    Parameters
    ----------
    image_in : str
        Location of S-PLUS image to run dophot
    objects_out : str
        Location of desired dophot output file
    config_file : str
        Location to save dophot tuneup file for this image
    apercorr_max_aperture : float
        Diameter [pixels] considered for the aperture correction

    Returns
    -------
    saves dophot tuneup file in the param:config_file location

    """

    # Load S-PLUS image
    head = fits.open(image_in)[0].header

    # Get image and catalog names
    image_name   = os.path.split(image_in)[1]
    objects_name = os.path.split(objects_out)[1]

    # Calculating dophot parameters
    # Reference: Javier Alonso - Private Communication

    FWHM = float(head['HIERARCH OAJ PRO FWHMMEAN']) / float(head['PIXSCALE'])

    SKY = float(head['HIERARCH OAJ QC NCMIDPT'])

    TEXPOSED = float(head['TEXPOSED']) / float(head['NCOMBINE'])

    SIGSKY = float(head['HIERARCH OAJ QC NCNOISE']) * TEXPOSED

    EPERDN = float(head['GAIN']) / TEXPOSED

    RDNOISE = 3.43 * np.sqrt(float(head['NCOMBINE']))

    TOP = float(head['SATURATE']) * TEXPOSED

    SCALEAPRADIUS = np.around((apercorr_max_aperture/2) / FWHM,3)

    # Generating config file
    config = (f"FWHM =     {FWHM}\n"
              f"SKY =      {SKY}\n"
              f"SIGSKY =   {SIGSKY}\n"
              f"EPERDN =   {EPERDN}\n"
              f"RDNOISE =  {RDNOISE}\n"
              f"TOP =      {TOP}\n"
              f"TEXPOSED = {TEXPOSED}\n"
              f"IMAGE_IN = '{image_name}'\n"
              f"OBJECTS_OUT = '{objects_name}'\n"
              "PARAMS_DEFAULT = paramdefault")

    # Saving config file
    with open(config_file, "w") as f:
        f.write(config)

def psf_flagstar(fitmag, fitsky, err_fitmag, max_err = 0.02, upper_limit = 0.5):
    """
    Create a star flag (1 classified as star, 0 not classified) for the dophot
    output catalog using the columns fitmag, fitsky and err_fitmag.

    Parameters
    ----------
    fitmag : np.array
        dophot catalog fitmag column
    fitsky : np.array
        dophot catalog fitsky column
    err_fitmag : np.array
        dophot catalog err_fitmag column
    max_err : float
        max value of err_fitmag selected for linear regression
    upper_limit : float
        value above linear regression limiting the star classification

    Returns
    -------
    np.array
        starflag array (1 classified as star, 0 not classified)
    """

    nrows = len(fitmag)

    # Create flag_star array
    flagstar = np.zeros(nrows)

    # select points for fit
    f0 = fitsky > 0
    ferr = err_fitmag < max_err

    # Fix when no points are selected within this error
    Npoints = len(fitsky[f0 & ferr])
    if Npoints < 30:
        msg = (f"Selected only {Npoints} points with err_fitmag < {max_err}. "
              f"Using mag_err = {1.5*max_err} instead.")
        warnings.warn(msg)

        max_err = 1.5*max_err
        ferr = err_fitmag < max_err

    # Generate x and y
    y = np.log10(fitsky[f0 & ferr])
    x = fitmag[f0 & ferr]

    # Linear fit: log10(fitsky) = a * fitmag + b
    a, b = np.polyfit(x, y, 1)

    # Star classification
    selection = np.log10(fitsky[f0]) < (upper_limit + a*fitmag[f0] + b)

    flagstar[f0] = selection.astype(int)

    # Alse set points with fitsky < 0 as stars
    flagstar[~f0] = 1

    return flagstar.astype(int)


def format_dophot_catalog(catalog_in, catalog_out, image, filt = 'nan',
                          field = 'NoFieldName', drname = 'NoDRname'):
    """
    Formats dophot output catalog into an ascii table, adding RA, DEC columns
    and also classifing stars (column STAR_FLAG = 1)

    It's also necessary to input the location of the field's .fz
    image. The WCS data from the header is used to convert x, y coordinates to
    RA and DEC.

    Parameters
    ----------
    catalog_in : str
        Location of dophot .sum catalog
    catalog_out : str
        Desired location of the formated catalog
    image : str
        Location of S-PLUS field image
    filt : str
        Name of the filter
    field : str
        Name of the field to be added to the filter_ID
    drname : str
        Data release designation to be added to the filter_ID
    sexmode : str
        dual/single SExtractor mode to be added to the filter_ID

    Returns
    -------
    Saves formated catalog to the param:catalog_out location
    """

    dophot_column_names = ["Star_number", "xpos", "ypos", "fitmag",
                           "err_fitmag", "fitsky", "objtype", "chi", "apcorr"]

    dophot_data_types = {'Star_number': int, 'xpos': float, 'ypos': float,
                         'fitmag': float, 'err_fitmag': float, 'fitsky': float,
                         'objtype': int, 'chi': float, 'apcorr': float}

    cat_data = pd.read_csv(catalog_in,
                           skiprows = 3,
                           delim_whitespace = True,
                           names = dophot_column_names,
                           dtype = dophot_data_types)

    # Create filter ID
    # Assign filter IDs
    dophot_filter_number = cat_data.loc[:,'Star_number'].values

    filt_standard = translate_filter_standard(filt)
    filter_ID = [f'{drname}_{field}_psf_{filt_standard}_{i:07d}'
                 for i in dophot_filter_number]

    cat_data[f'{filt_standard}_ID_psf'] = filter_ID

    # Include RA and DEC
    x = cat_data.loc[:, 'xpos'].array
    y = cat_data.loc[:, 'ypos'].array

    # Extract field WCS from image header
    head = fits.open(image)[1].header
    coord_wcs = WCS(head)

    skycoords = pixel_to_skycoord(x, y, coord_wcs, origin=1)

    # Get ra and dec in degrees
    ra = np.array(skycoords.ra)
    dec = np.array(skycoords.dec)

    filt_standard = translate_filter_standard(filt)
    cat_data[f'RA_{filt_standard}'] = ra
    cat_data[f'DEC_{filt_standard}'] = dec

    flagstar = psf_flagstar(fitmag = cat_data.loc[:,'fitmag'].values,
                            fitsky = cat_data.loc[:,'fitsky'].values,
                            err_fitmag = cat_data.loc[:, 'err_fitmag'].values)

    cat_data['FLAG_STAR'] = flagstar

    with open(catalog_out, 'w') as f:
        f.write("# ")
        cat_data.to_csv(f, index = False, sep = " ")


def plot_dophot_diagnostic(catalog, save_file, filt, mag_cut = (8, 22)):
    """
    Makes diagnostic plots of the photometry in a given DOPHOT output

    Parameters
    ----------
    catalog : str
        Location of SExtractor output catalog
    save_file : str
        Location to save plots
    filt : str
        Name of the photometric filter
    mag_cut : list
        Limiting magnitudes (min, max)

    Returns
    -------
    Saves diagnostic plots
    """

    psfcat = load_data(catalog)

    fig, axs = plt.subplots(2, figsize = [5,10])

    #############
    # Plot fitsky

    # Plot all points
    axs[0].scatter(psfcat['fitmag'], psfcat['fitsky'],
                   c="#AAAAAA", s=10, alpha=0.1)

    # Plot selection
    f = psfcat['FLAG_STAR'] == 1
    axs[0].scatter(psfcat['fitmag'][f], psfcat['fitsky'][f],
                   c="#2266FF", s=10, alpha=0.3,
                   label=f"FLAG_STAR = 1")

    # Plot grid lines
    axs[0].hlines(np.arange(0, 10000, 100), mag_cut[0], mag_cut[1],
                  colors="#EEEEEE", zorder=-1)

    axs[0].legend(loc=1)
    axs[0].set_xlim(mag_cut)
    axs[0].set_ylim([-50, 500])
    axs[0].set_ylabel('fitsky')
    axs[0].minorticks_on()

    #############
    # Plot fitmag

    # Plot all points
    axs[1].scatter(psfcat['fitmag'], psfcat['err_fitmag'],
                   c="#AAAAAA", s=10, alpha=0.1)

    # Plot selection
    f = psfcat['FLAG_STAR'] == 1
    axs[1].scatter(psfcat['fitmag'][f], psfcat['err_fitmag'][f],
                   c="#2266FF", s=10, alpha=0.3,
                   label=f"err_fitmag < 0.02")

    # Plot cut line
    axs[1].hlines(0.02, mag_cut[0], mag_cut[1],
                  colors="#2266FF", zorder=1)

    # Plot grid lines
    axs[1].hlines(np.arange(0, 0.2, 0.02), mag_cut[0], mag_cut[1],
                  colors="#EEEEEE", zorder=-1)

    axs[1].set_xlim(mag_cut)
    axs[1].set_ylim([0, 0.2])
    axs[1].set_ylabel('err_fitmag')
    axs[1].minorticks_on()

    axs[1].set_xlabel(f"{filt}_fitmag [inst]")

    plt.subplots_adjust(left=0.14, right=0.98, top=0.98, bottom=0.06, hspace=0.1)

    plt.savefig(save_file)
    plt.close(fig)

###############################
# Correction xy


def intersection_2lines(x1, y1, x2, y2, x3, y3, x4, y4):

    """
    Returns the intersection of line L1 defined by points (x1,y1), (x2,y2), and
    line L2 defined by points (x3,y3), (x4,y4)

    see https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    """

    D = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)

    x = ( (x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4) ) / D

    y = ( (x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4) ) / D

    return np.array([x, y])


def align_splus_xy(x, y, center = None, margin = 10):
    """
    Aligns S-PLUS X,Y coordinates by moving origin to bottom left vertice and
    rotating to fit x and y directions

    Parameters
    ----------
    x : array
        array of X_IMAGE values
    y : array
        array of Y_IMAGE values
    center : list
        center value in the format [xcenter, ycenter]. If None, center is
        calculated from the average x and y values
    margin : int
        margin, in pixels, added to the origin

    Returns
    -------
    array
        array of square vertices in the format:
         [[x_bottomleft,  y_bottomleft],
          [x_bottomright, y_bottomright],
          [x_topright,    y_topright],
          [x_topleft,     y_topleft]]

    """
    # Center coordinates
    if center is None:
        x0 = np.nanmean(x)
        y0 = np.nanmean(y)
    else:
        x0 = center[0]
        y0 = center[1]

    # Defining quadrants:   Q4 | Q3
    #                       -------
    #                       Q1 | Q2

    Q1 = (x < x0) & (y < y0)
    Q2 = (x > x0) & (y < y0)
    Q3 = (x > x0) & (y > y0)
    Q4 = (x < x0) & (y > y0)

    # Finding points in left and right sides and bottom

    x1l = x[Q1][ x[Q1] == np.nanmin(x[Q1]) ][0]  # x of left most point in Q1
    y1l = y[Q1][ x[Q1] == np.nanmin(x[Q1]) ][0]  # y of left most point in Q1

    x1b = x[Q1][ y[Q1] == np.nanmin(y[Q1]) ][0]
    y1b = y[Q1][ y[Q1] == np.nanmin(y[Q1]) ][0]

    x2r = x[Q2][ x[Q2] == np.nanmax(x[Q2]) ][0]
    y2r = y[Q2][ x[Q2] == np.nanmax(x[Q2]) ][0]

    x2b = x[Q2][ y[Q2] == np.nanmin(y[Q2]) ][0]
    y2b = y[Q2][ y[Q2] == np.nanmin(y[Q2]) ][0]

    x3r = x[Q3][ x[Q3] == np.nanmax(x[Q3]) ][0]
    y3r = y[Q3][ x[Q3] == np.nanmax(x[Q3]) ][0]

    x4l = x[Q4][ x[Q4] == np.nanmin(x[Q4]) ][0]
    y4l = y[Q4][ x[Q4] == np.nanmin(x[Q4]) ][0]

    # bottom-left vertice
    vbl = intersection_2lines(x1=x1b, y1=y1b, x2=x2b, y2=y2b,
                              x3=x1l, y3=y1l, x4=x4l, y4=y4l)

    # bottom-right vertice
    vbr = intersection_2lines(x1=x1b, y1=y1b, x2=x2b, y2=y2b,
                              x3=x3r, y3=y3r, x4=x2r, y4=y2r)

    # Bottom vector
    vb = vbr - vbl

    # Unit vector
    unit_vb = vb / np.sqrt(np.sum((vb**2)))

    # Angle
    dot_product = np.dot(unit_vb, np.array([1, 0]))
    angle = np.arccos(dot_product)

    # Move origin to bottom left vertice
    x_temp = x - vbl[0] - margin
    y_temp = y - vbl[1] - margin

    # Rotate to align
    x_align = x_temp * np.cos(angle) - y_temp * np.sin(angle)
    y_align = x_temp * np.sin(angle) + y_temp * np.cos(angle)

    return x_align, y_align


def fix_xy_rotation(catalog, save_file, xcol = 'X_IMAGE', ycol = 'Y_IMAGE'):

    cat = fits.open(catalog)
    cat_data = cat[1].data

    x = cat_data.columns[xcol].array
    y = cat_data.columns[ycol].array

    # Normalize X and Y
    x_align, y_align = align_splus_xy(x, y)

    # Create new fits catalog with new columns
    corr_data = cat_data.columns

    corr_data += fits.Column(name='X_ALIGN',
                             format='1E',
                             array=x_align)

    corr_data += fits.Column(name='Y_ALIGN',
                             format='1E',
                             array=y_align)

    # Save corrected data to save_file fits catalog
    hdu = fits.BinTableHDU.from_columns(corr_data)
    hdu.writeto(save_file)


def apply_xy_correction(catalog, save_file, map_file, xbins, ybins):
    """
    Applies XY corrections to the S-PLUS photometry catalogs.

    Correction are applied to all fixed aperture, auto, petro and iso magnitudes
    and fluxes (if present in the catalogs).

    Two additional columns are created: X_ALIGN and Y_ALIGN, corresponding to
    normalized X_IMAGE and Y_IMAGE positions (origin moved to bottom left
    corner, and coordinates rotate to match X and Y axis).

    Parameters
    ----------
    catalog : str
        Location to the SExtractor photometry output catalog

    save_file : str
        Desired location to save the XY corrected catalog

    map_file : str
        Location of the xy correction map (must be numpy npy file)

    xbins : list
        xbins of the correction map (start, end, Nbins) [in pixels]

    ybins : list
        ybins of the correction map (start, end, Nbins) [in pixels]

    Returns
    -------
    Saves XY corrected catalog in the desired location (param:save_file)
    """

    cat = fits.open(catalog)
    cat_data = cat[1].data

    x = cat_data.columns['X_IMAGE'].array
    y = cat_data.columns['Y_IMAGE'].array

    # Normalize X and Y
    x_align, y_align = align_splus_xy(x, y)

    # Create new fits catalog with new columns
    corr_data = cat_data.columns

    corr_data += fits.Column(name='X_ALIGN',
                             format='1E',
                             array=x_align)

    corr_data += fits.Column(name='Y_ALIGN',
                             format='1E',
                             array=y_align)

    # Prepare bins
    xbins_grid = np.linspace(xbins[0], xbins[1], int(xbins[2]) + 1)
    ybins_grid = np.linspace(ybins[0], ybins[1], int(ybins[2]) + 1)

    xbins_id = np.array(range(int(xbins[2]) + 1))
    ybins_id = np.array(range(int(ybins[2]) + 1))

    # Load corrections
    corrections = np.load(map_file)

    # Apply corrections
    for k in range(len(cat_data)):
        x_source = x_align[k]
        y_source = y_align[k]

        # Get delta mag (if given on the correction map for this position)
        try:
            # Find ids of the bin that contains the source
            bin_source_i = xbins_id[xbins_grid <= x_source][-1]
            bin_source_j = ybins_id[ybins_grid <= y_source][-1]

            delta_mag = corrections[bin_source_i, bin_source_j]
            delta_flux_frac = 10.0 ** (-(delta_mag / 2.5))

        except IndexError:
            delta_mag = 0
            delta_flux_frac = 1

        try:
            if corr_data['MAG_AUTO'].array[k] != 99:
                corr_data['MAG_AUTO'].array[k] += delta_mag
            corr_data['FLUX_AUTO'].array[k] *= delta_flux_frac
        except KeyError:
            pass

        try:
            if corr_data['MAG_ISO'].array[k] != 99:
                corr_data['MAG_ISO'].array[k] += delta_mag
            corr_data['FLUX_ISO'].array[k] *= delta_flux_frac
        except KeyError:
            pass

        try:
            if corr_data['MAG_PETRO'].array[k] != 99:
                corr_data['MAG_PETRO'].array[k] += delta_mag
            corr_data['FLUX_PETRO'].array[k] *= delta_flux_frac
        except KeyError:
            pass

        try:
            f = corr_data['MAG_APER'].array[k] != 99
            corr_data['MAG_APER'].array[k][f] += delta_mag
            corr_data['FLUX_APER'].array[k] *= delta_flux_frac
        except KeyError:
            pass

        try:
            f = corr_data['MAG_APER'].array[k] != 99
            corr_data['MAG_APER'].array[k][f] += delta_mag
            corr_data['FLUX_APER'].array[k] *= delta_flux_frac
        except KeyError:
            pass

        try:
            if corr_data['MU_MAX'].array[k] != 99:
                corr_data['MU_MAX'].array[k] += delta_mag
        except KeyError:
            pass

        try:
            if corr_data['MU_THRESHOLD'].array[k] != 99:
                corr_data['MU_THRESHOLD'].array[k] += delta_mag
        except KeyError:
            pass

        try:
            corr_data['BACKGROUND'].array[k] *= delta_flux_frac
        except KeyError:
            pass

        try:
            corr_data['THRESHOLD'].array[k] *= delta_flux_frac
        except KeyError:
            pass

    # Save corrected data to save_file fits catalog
    hdu = fits.BinTableHDU.from_columns(corr_data)
    hdu.writeto(save_file)


def apply_xy_correction_psf(catalog, save_file, map_file, xbins, ybins):
    """
    Applies XY corrections to the S-PLUS psf photometry catalogs.

    Two additional columns are created: X_ALIGN and Y_ALIGN, corresponding to
    normalized X_IMAGE and Y_IMAGE positions (origin moved to bottom left
    corner, and coordinates rotate to match X and Y axis).

    Parameters
    ----------
    catalog : str
        Location to the SExtractor photometry output catalog

    save_file : str
        Desired location to save the XY corrected catalog

    map_file : str
        Location of the xy correction map (must be numpy npy file)

    xbins : list
        xbins of the correction map (start, end, Nbins) [in pixels]

    ybins : list
        ybins of the correction map (start, end, Nbins) [in pixels]

    Returns
    -------
    Saves XY corrected catalog in the desired location (param:save_file)
    """


    # Load filter catalogue
    cat_data = load_data(catalog)

    x = cat_data.loc[:,'xpos'].values
    y = cat_data.loc[:,'ypos'].values

    # Normalize X and Y
    x_align, y_align = align_splus_xy(x, y)

    # Create new fits catalog with new columns
    corr_data = cat_data

    corr_data['X_ALIGN'] = x_align
    corr_data['Y_ALIGN'] = y_align

    # Prepare bins
    xbins_grid = np.linspace(xbins[0], xbins[1], int(xbins[2]) + 1)
    ybins_grid = np.linspace(ybins[0], ybins[1], int(ybins[2]) + 1)

    xbins_id = np.array(range(int(xbins[2]) + 1))
    ybins_id = np.array(range(int(ybins[2]) + 1))

    # Load corrections
    corrections = np.load(map_file)

    # Apply corrections
    for k in range(len(cat_data)):
        x_source = x_align[k]
        y_source = y_align[k]

        # Get delta mag (if given on the correction map for this position)
        try:
            # Find ids of the bin that contains the source
            bin_source_i = xbins_id[xbins_grid <= x_source][-1]
            bin_source_j = ybins_id[ybins_grid <= y_source][-1]

            delta_mag = corrections[bin_source_i, bin_source_j]

        except IndexError:
            delta_mag = 0

        try:
            if corr_data.loc[:,'fitmag'].values[k] != 99:
                corr_data.loc[:,'fitmag'].values[k] += delta_mag
        except KeyError:
            pass

    # Save corrected data to save_file fits catalog
    with open(save_file, 'w') as f:
        f.write("# ")
        corr_data.to_csv(f, index = False, sep = " ")


def get_xy_correction_grid(data_file, save_file, mag, mag_ref, xbins, ybins):

    xNbins = xbins[2]
    yNbins = ybins[2]

    # Get values of bins limits and centers

    xbins = np.linspace(xbins[0], xbins[1], xbins[2]+1)
    ybins = np.linspace(ybins[0], ybins[1], ybins[2]+1)

    # generate the mesh

    xx, yy = np.meshgrid(xbins, ybins, sparse=True)

    corrections = 0*xx + 0*yy
    corrections_std = np.nan*xx + np.nan*yy

    # Load data
    data = load_data(data_file)

    X = data.loc[:,'X_ALIGN'].values
    Y = data.loc[:,'Y_ALIGN'].values

    DZP = data.loc[:,mag_ref].values - data.loc[:,mag].values

    mag_cut = (data.loc[:, mag].values > 14) & (data.loc[:, mag].values <= 17.5)
    remove_worst_cases = np.abs(DZP) < 0.2

    # Fill array of corrections
    N_data = len(DZP[mag_cut & remove_worst_cases])
    min_N_data = 0.05*N_data/(xNbins*yNbins)

    for i in range(xNbins):
        xselect = (X >= xbins[i]) & (X < xbins[i+1])

        for j in range(yNbins):
            yselect = (Y >= ybins[j]) & (Y < ybins[j+1])

            DZP_select = DZP[xselect & yselect & mag_cut & remove_worst_cases]

            if len(DZP_select) > min_N_data:
                corrections[i,j] = np.mean(DZP_select)

            corrections_std[i,j] = np.std(DZP_select)

    corrections = gaussian_filter(corrections, sigma=1)

    # Scale offset by mean value (offsets are dealt with in another step #########
    corrections = corrections - np.nanmean(DZP[mag_cut & remove_worst_cases])

    # Remove nan values
    corrections[np.isnan(corrections)] = 0

    np.save(save_file, corrections)


def plot_xy_correction_grid(grid_file, save_file, mag, xbins, ybins,
                            cmap = None, clim = [-0.05, 0.05]):

    # Get values of bins limits and centers

    xbins_grid = np.linspace(xbins[0], xbins[1], xbins[2] + 1)
    ybins_grid = np.linspace(ybins[0], ybins[1], ybins[2] + 1)

    # generate the mesh

    xx, yy = np.meshgrid(xbins_grid, ybins_grid, sparse=True)

    corrections = np.load(grid_file)

    plt.figure(figsize=(8, 6.4))

    vmin = clim[0]
    vmax = clim[1]

    if cmap is None:
        cmap = plt.get_cmap("seismic_r")

    cm = plt.pcolor(xx, yy, corrections.T, vmin=vmin, vmax=vmax, cmap=cmap)
    cbar = plt.colorbar(cm)
    cbar.set_label("offset")

    plt.vlines(xbins_grid, xbins[0], xbins[1], linewidth=0.5, alpha=0.4)
    plt.hlines(ybins_grid, ybins[0], ybins[1], linewidth=0.5, alpha=0.4)

    plt.gca().set_title("%s offsets" % mag)
    plt.gca().set_xlabel("X_ALIGN")
    plt.gca().set_ylabel("Y_ALIGN")
    plt.gca().set_xlim((xbins[0], xbins[1]))
    plt.gca().set_ylim((ybins[0], ybins[1]))
    plt.subplots_adjust(top=0.95, bottom=0.08, left=0.11, right=0.98)

    plt.savefig(save_file)
    plt.clf()
    plt.close()


################################################################################
# Assign detection IDs

def assign_single_mode_filter_id(catalog,
                                 filt,
                                 save_file,
                                 field = 'NoFieldName',
                                 drname = 'NoDRname'):

    """
    Assigns detection ID to SExtractor photometry (in single mode).

    Parameters
    ----------
    catalog : str
        Location of SExtractor photometry catalog
    filt : str
        Name of the filter
    save_file : str
        Desired location to save new catalog
    field : str
        Name of the field to be added to the filter_ID
    drname : str
        Data release designation to be added to the filter_ID

    Returns
    -------
    Saves new catalog with filter_ID

    """

    # Read catalog
    cat = fits.open(catalog)
    cat_data = cat[1].data

    # Create new fits catalog with new columns
    new_data = []

    filt_standard = translate_filter_standard(filt)

    for col in cat_data.columns:
        new_data.append(col)

    new_data.append(fits.Column(name=f"RA_{filt_standard}",
                                format='1E',
                                array=cat_data.columns["ALPHA_J2000"].array))

    new_data.append(fits.Column(name=f"DEC_{filt_standard}",
                                format='1E',
                                array=cat_data.columns["DELTA_J2000"].array))

    # Assign filter IDs
    sex_filter_number = cat_data.columns['NUMBER'].array

    filt_standard = translate_filter_standard(filt)
    filter_ID = [f'{drname}_{field}_single_{filt_standard}_{i:07d}'
                 for i in sex_filter_number]

    new_data.append(fits.Column(name=f'{filt_standard}_ID_single    ',
                                format='50A',
                                array=filter_ID))

    # Save corrected data to save_file fits catalog
    hdu = fits.BinTableHDU.from_columns(new_data)
    hdu.writeto(save_file)


def extract_filt_id_single(catalog,
                           filt,
                           save_file):

    """
    Extracts filter_ID, RA, DEC from filter ID catalog (in single mode).

    Parameters
    ----------
    catalog : str
        Location of SExtractor photometry catalog
    filt : str
        Name of the filter
    save_file : str
        Desired location to save new catalog

    Returns
    -------
    Saves new catalog with filter_ID

    """

    # Read catalog
    cat = fits.open(catalog)
    cat_data = cat[1].data

    # Create new fits catalog with new columns
    new_data = []

    filt_standard = translate_filter_standard(filt)

    for col in cat_data.columns:
        if col.name in [f"RA_{filt_standard}",
                        f"DEC_{filt_standard}",
                        f'{filt_standard}_ID_SINGLE']:

            new_data.append(col)

    # Save corrected data to save_file fits catalog
    hdu = fits.BinTableHDU.from_columns(new_data)
    hdu.writeto(save_file)


def extract_filt_id_psf(catalog,
                        filt,
                        save_file):

    """
    Extracts filter_ID, RA, DEC from filter ID catalog (in PSF mode).

    Parameters
    ----------
    catalog : str
        Location of SExtractor photometry catalog
    filt : str
        Name of the filter
    save_file : str
        Desired location to save new catalog

    Returns
    -------
    Saves new catalog with filter_ID

    """

    # Read catalog
    cat = load_data(catalog)

    # Create new fits catalog with new columns
    new_data = []

    filt_standard = translate_filter_standard(filt)

    filt_ID = cat.loc[:,f"{filt_standard}_ID_psf"].values
    new_data.append(fits.Column(name=f"{filt_standard}_ID_psf",
                                format='50A',
                                array=filt_ID))

    RA = cat.loc[:,f"RA_{filt_standard}"].values
    new_data.append(fits.Column(name=f"RA_{filt_standard}",
                                format='1E',
                                array=RA))

    DEC = cat.loc[:,f"DEC_{filt_standard}"].values
    new_data.append(fits.Column(name=f"DEC_{filt_standard}",
                                format='1E',
                                array=DEC))

    # Save corrected data to save_file fits catalog
    hdu = fits.BinTableHDU.from_columns(new_data)
    hdu.writeto(save_file)


def generate_phot_id(catalog,
                      save_file,
                      filters,
                      field = 'NoFieldName',
                      drname = 'NoDRname',
                      mode = 'noMode'):

    """
    Generate MODE ID SINGLE/PSF photometries

    Parameters
    ----------
    catalog : str
        Location of SExtractor photometry catalog
    save_file : str
        Desired location to save new catalog
    filters : str
        List of S-PLUS filters
    field : str
        Name of the field to be added to the filter_ID
    drname : str
        Data release designation to be added to the filter_ID

    Returns
    -------
    Saves new catalog with field_ID, RA_field_ID, DEC_field_ID

    """

    # Read catalog
    cat = fits.open(catalog)
    cat_data = cat[1].data

    # Create new fits catalog with new columns
    new_data = []

    nlines = len(cat_data)

    PHOT_ID = [f'{drname}_{field}_{mode}_{i:07d}'
                    for i in range(1,nlines+1)]

    PHOT_ID_RA = np.full(nlines, np.nan)
    PHOT_ID_DEC = np.full(nlines, np.nan)

    # fill RA, DEC from red to blue
    for filt in filters:
        filt_standard = translate_filter_standard(filt)
        f = np.isnan(PHOT_ID_RA)

        ra_filt = cat_data.columns[f'RA_{filt_standard}'].array
        dec_filt = cat_data.columns[f'DEC_{filt_standard}'].array

        PHOT_ID_RA[f] = ra_filt[f]
        PHOT_ID_DEC[f] = dec_filt[f]

    new_data.append(fits.Column(name=f'PHOT_ID_{mode}',
                                format='50A',
                                array=PHOT_ID))

    new_data.append(fits.Column(name=f'PHOT_ID_RA_{mode}',
                                format='1E',
                                array=PHOT_ID_RA))

    new_data.append(fits.Column(name=f'PHOT_ID_DEC_{mode}',
                                format='1E',
                                array=PHOT_ID_DEC))

    # Save corrected data to save_file fits catalog
    hdu = fits.BinTableHDU.from_columns(new_data)
    hdu.writeto(save_file)


def generate_field_id(catalog,
                      save_file,
                      field = 'NoFieldName',
                      drname = 'NoDRname',
                      modes = ["dual", "psf", "single"]):

    """
    Generate FIELD ID SINGLE/PSF photometries

    Parameters
    ----------
    catalog : str
        Location of SExtractor photometry catalog
    save_file : str
        Desired location to save new catalog
    field : str
        Name of the field to be added to the filter_ID
    drname : str
        Data release designation to be added to the filter_ID

    Returns
    -------
    Saves new catalog with field_ID, RA_field_ID, DEC_field_ID

    """

    # Read catalog
    cat = fits.open(catalog)
    cat_data = cat[1].data

    # Create new fits catalog with new columns
    new_data = []

    nlines = len(cat_data)

    FIELD_ID = [f'{drname}_{field}_{i:07d}'
                    for i in range(1,nlines+1)]

    FIELD_ID_RA = np.full(nlines, np.nan)
    FIELD_ID_DEC = np.full(nlines, np.nan)

    # fill RA, DEC following mode order priority
    for mode in modes:
        f = np.isnan(FIELD_ID_RA)

        ra_mode = cat_data.columns[f'PHOT_ID_RA_{mode}'].array
        dec_mode = cat_data.columns[f'PHOT_ID_DEC_{mode}'].array

        FIELD_ID_RA[f] = ra_mode[f]
        FIELD_ID_DEC[f] = dec_mode[f]

    new_data.append(fits.Column(name=f'FIELD_ID',
                                format='50A',
                                array=FIELD_ID))

    new_data.append(fits.Column(name=f'FIELD_ID_RA',
                                format='1E',
                                array=FIELD_ID_RA))

    new_data.append(fits.Column(name=f'FIELD_ID_DEC',
                                format='1E',
                                array=FIELD_ID_DEC))

    for mode in modes:
        new_data.append(cat_data.columns[f'PHOT_ID_{mode}'])
        new_data.append(cat_data.columns[f'PHOT_ID_RA_{mode}'])
        new_data.append(cat_data.columns[f'PHOT_ID_DEC_{mode}'])

    # Save corrected data to save_file fits catalog
    hdu = fits.BinTableHDU.from_columns(new_data)
    hdu.writeto(save_file)

def generate_dual_mode_phot_id(catalog,
                               save_file,
                               field = 'NoFieldName',
                               drname = 'NoDRname'):

    """
    Assigns detection ID to SExtractor photometry (in single mode).

    Parameters
    ----------
    catalog : str
        Location of SExtractor photometry catalog
    save_file : str
        Desired location to save new catalog
    field : str
        Name of the field to be added to the filter_ID
    drname : str
        Data release designation to be added to the filter_ID

    Returns
    -------
    Saves new catalog with filter_ID

    """

    # Read catalog
    cat = fits.open(catalog)
    cat_data = cat[1].data

    # Create new fits catalog with new columns
    new_data = []

    col_RA = cat_data.columns["ALPHA_J2000"]
    col_RA.name = "PHOT_ID_RA_dual"

    col_DEC = cat_data.columns["DELTA_J2000"]
    col_DEC.name = "PHOT_ID_DEC_dual"

    new_data.append(col_RA)
    new_data.append(col_DEC)

    # Assign filter IDs
    sex_filter_number = cat_data.columns['NUMBER'].array

    PHOT_ID = [f'{drname}_{field}_dual_{i:07d}'
                    for i in sex_filter_number]

    new_data.append(fits.Column(name=f'PHOT_ID_dual',
                                format='50A',
                                array=PHOT_ID))

    # Save corrected data to save_file fits catalog
    hdu = fits.BinTableHDU.from_columns(new_data)
    hdu.writeto(save_file)

################################################################################
# Aperture correction

# Aperture Photometry Functions for the S-PLUS Collaboration
# Author: André Zamorano Vitorelli - andrezvitorelli@gmail.com
# 2020-07-07
# """
#
# Editions: Felipe Almeida-Fernandes - felipefer42@gmail.com
# 2021-05-26
# __license__ = "GPL"
# __version__ = "0.1"

def get_apertures_from_sexconf(sexconf):
    """
    Reads the PHOT_APERTURES parameter in the sexconf file

    Parameters
    ----------
    sexconf : str
        Location of sexconf file

    Returns
    -------
    np.ndarray
        list of apertures
    """

    with open(sexconf) as f:
        lines = f.readlines()

    for line in lines:
        # remove comment from line
        line = line.split("#")[0]

        # Get param name
        param = line.split()[0]

        # If param is "PHOT_APERTURES", return list of values
        if param == "PHOT_APERTURES":
            value = "".join(line.split()[1:])
            value = np.array(value.split(","), dtype = float)

            return value

    # If param "PHOT_APERTURES" is not found
    return None


def obtain_aperture_correction(catalog, filt, sexconf, save_file, aperture,
                               s2ncut, starcut, max_aperture = 72.72727,
                               mag_partition = 2, convergence_slope = 1e-2,
                               check_convergence = True, verbose = False):
    """
    Calculates the aperture correction from a certain "aperture" to the another
    aperture "max_aperture" (which must be big enought to represent the
    total emission of the source)

    Parameters
    ----------
    catalog : str
        Location of SExtractor output catalog with the measured fixed apertures
    filt : str
        Name of the filter
    sexconf : str
        Location of sexconfig file for this filter's photometry
    save_file : str
        Desired location to save calculated aperture corrections
    aperture : float
        Base aperture which will have the correction estimated, in pixels
    s2ncut : list
        Min and max values of signal-to-noise to consider
    starcut : float
        Min value of SExtractor CLASS_STAR to consider
    max_aperture : str
        The maximum aperture in pixels
    mag_partition : float
        out of the stars selected with criteria above, get the 1/mag_partition
        sample with lower magnitudes
    convergence_slope : str
        the slope of the growth curve at the maximum aperture
    check_convergence : bool
        use slope to evaluate the confidence in the correction
    verbose : bool
        print details of the process

    Returns
    -------
    Saves estimated aperture correction and bounds in 3 columns to save_file,
    identified by filters by line
    """

    sextractor_table = Table.read(catalog)

    if verbose:
        catalog_name = os.path.split(catalog)[1]
        print(f"Filter {filt}")
        print(f"Calculating aperture correction from table {catalog_name}")
        print(f"Total objects: {len(sextractor_table)}\n")

    # Get aperture list
    apertures_list = get_apertures_from_sexconf(sexconf)  # type: np.ndarray

    if apertures_list is None:
        raise ValueError(f"Could not find param PHOT_APERTURES in {sexconf}.")

    # Get base aperture ID (allowing a rounding error up to the third decimal)
    round_list = np.around(apertures_list, 3)
    round_aper = np.around(aperture, 3)
    aperture_id = np.where(round_list == round_aper)[0][0]

    # Apply selection criteria
    select, medianFWHM = star_selector(catalog = sextractor_table,
                                       s2ncut        = s2ncut,
                                       starcut       = starcut,
                                       mag_partition = mag_partition,
                                       verbose       = verbose)

    magnitude_corr_list = []
    # individual aperture corrections
    for star in select:
        mags = star['MAG_APER'] - star['MAG_APER'][aperture_id]
        magnitude_corr_list.append(mags)

    mincorr, mediancorr, maxcorr = np.percentile(magnitude_corr_list,
                                                 [16, 50, 84], axis=0)

    correction = np.nan
    correction_low = np.nan
    correction_up = np.nan
    final_radius = np.nan
    slope = np.nan

    for i in range(len(apertures_list)):
        if verbose:
            SNR = np.sqrt(mediancorr[i] ** 2 / (maxcorr[i] - mincorr[i]) ** 2)

            msg  = "Radius: {:.2f} single aper. ".format(apertures_list[i])
            msg += "correction: {:.4f} ".format(mediancorr[i])
            msg += "[{:.4f} - {:.4f}](CL68) ".format(mincorr[i], maxcorr[i])
            msg += "SNR: {}".format(SNR)

            print(msg)

        if apertures_list[i] <= max_aperture:

            correction     = mediancorr[i]
            correction_low = mincorr[i]
            correction_up  = maxcorr[i]
            final_radius   = apertures_list[i]

            # Check convergence
            j = len(apertures_list) - i
            if check_convergence and i > 2:
                slope_radii = apertures_list[-(j + 3):-j]
                slope_corrs = mediancorr[-(j + 3):-j]
                slope = linregress(slope_radii, slope_corrs)[0]

    if verbose:
        print((f"low-median-high: [{correction_low:.4f} "
               f"{correction:.4f} {correction_up:.4f}]"))

        print(f'Nearest aperture: {final_radius}')

        if check_convergence:
            print(f'Slope of last 3 apertures: {slope:.2e}\n')

    convergence = None

    if check_convergence:
        if abs(slope) > convergence_slope:
            convergence = "Not_converged"
            print((f'Warning: aperture correction is not stable at the selected'
                   f' aperture for filter {filt}. Slope: {slope:.2e}'))
        else:
            convergence = "Converged"

    # Write to file
    with open(save_file, 'a') as f:
        f.write(f'SPLUS_{filt} {correction} {correction_low} {correction_up}')

        if check_convergence:
            f.write(f' {convergence}')

        f.write('\n')

    del select


def star_selector(catalog, s2ncut = (30, 1000), starcut = 0.9,
                  mag_partition = 2, verbose = False):
    """
    Selects the stars for the aperture correction

    Parameters
    ----------
    catalog : astropy Table
        Loaded fits catalog as an astropy table
    s2ncut : list
        Min and max values of signal-to-noise to consider
    starcut : float
        Min value of SExtractor CLASS_STAR to consider
    mag_partition : float
        out of the stars selected with criteria above, get the 1/mag_partition
        sample with lower magnitudes
    verbose : bool
        print details of the process

    Returns
    -------
    astropy Table
        Selected stars data
    """

    # Calculate the s2n
    s2n = catalog['FLUX_AUTO'] / catalog['FLUXERR_AUTO']

    # Apply selection conditions
    conditions = ((catalog['CLASS_STAR'] > starcut) &
                  (s2n > s2ncut[0]) &
                  (s2n < s2ncut[1]) &
                  (catalog['FLAGS'] == 0))

    select = catalog[conditions]

    if verbose:
        print(f"Selected stars: {len(select)}")

    # Select well behaved FWHM
    inferior, medianFWHM, superior = np.percentile(select['FWHM_WORLD'],
                                                   [16, 50, 84])

    conditions2 = ((select['FWHM_WORLD'] > inferior) &
                   (select['FWHM_WORLD'] < superior))

    select = select[conditions2]

    if verbose:
        print(f"Median FWHM for field: {medianFWHM:.4f}")
        print(f"After FWHM cut: {len(select)}")

    # Brightest of the best:
    select.sort('MAG_AUTO')
    select = select[0:int(len(select) / mag_partition)]

    if verbose:
        print(f"After brightest 1/{mag_partition} cut: {len(select)}\n")

    return select, medianFWHM


def growth_curve(catalog, s2ncut = (30, 1000), starcut = 0.9,
                 mag_partition=2, verbose = False):
    """
    Calculates the growth curve (magnitude in radius K+1 - magnitude in
    radius K) for a filter in a field from a sextractor catalogue

    Parameters
    ----------
    catalog : astropy Table
        Loaded fits catalog as an astropy table
    s2ncut : list
        Min and max values of signal-to-noise to consider
    starcut : float
        Min value of SExtractor CLASS_STAR to consider
    mag_partition : float
        out of the stars selected with criteria above, get the 1/mag_partition
        sample with lower magnitudes
    verbose : bool
        print details of the process

    Returns
    -------
    np.ndarray
        numpy array of shape (5, len(aperture_radii)-1) containing, in order:
            lower bound of the 95% confidence region of the growth curve
            lower bound of the 68% confidence region of the growth curve
            median of the growth curve
            higher bound of the 68% confidence region of the growth curve
            higher bound of the 95% confidence region of the growth curve
    float
        median FWHM of stars
    int
        number of selected stars
    """

    sextractor_table = Table.read(catalog)

    select, medianFWHM = star_selector(catalog = sextractor_table,
                                       s2ncut        = s2ncut,
                                       starcut       = starcut,
                                       mag_partition = mag_partition,
                                       verbose       = verbose)

    mlist = []
    for star in select:
        mags = np.diff(star['MAG_APER'])
        mlist.append(mags)

    percentile = np.percentile(mlist, [2.5, 16, 50, 84, 97.5], axis=0)
    minmag2, minmag, medianmag, maxmag, maxmag2 = percentile

    result = np.array([minmag2, minmag, medianmag, maxmag, maxmag2])

    return result, medianFWHM, len(select)


def growth_curve_plotter(catalog, filt, sexconf, save_file, aperture,
                         max_aperture = 72.72727, starcut=.9, s2ncut=(30, 1000),
                         mag_partition=2, verbose = False):
    """
    Generates and plots the field's growth curve for a given filter

    Parameters
    ----------
    catalog : str
        Location of SExtractor output catalog with the measured fixed apertures
    filt : str
        Name of the filter
    sexconf : str
        Location of sexconfig file for this filter's photometry
    save_file : str
        Desired location to save the plot of the growth curve
    aperture : float
        Base aperture diameter (pixels) which will have the correction estimated
    max_aperture : str
        The maximum aperture diameter in pixels
    s2ncut : list
        Min and max values of signal-to-noise to consider
    starcut : float
        Min value of SExtractor CLASS_STAR to consider
    mag_partition : float
        out of the stars selected with criteria above, get the 1/mag_partition
        sample with lower magnitudes
    verbose : bool
        print details of the process


    Returns
    -------
    Saves plot of the growth curve
    """

    # Get aperture list
    # Diameters (in pixels)
    apertures_list = get_apertures_from_sexconf(sexconf)  # type: np.ndarray

    if apertures_list is None:
        raise ValueError(f"Could not find param PHOT_APERTURES in {sexconf}.")

    result, medianFWHM, starcount = growth_curve(catalog = catalog,
                                                 s2ncut  = s2ncut,
                                                 starcut = starcut,
                                                 mag_partition = mag_partition,
                                                 verbose = verbose)

    minmag2, minmag, medianmag, maxmag, maxmag2 = [x for x in result]

    diameter = [(a + b) / 2 for a, b in zip(apertures_list[:],
                                            apertures_list[1:])]

    # Plot growth curve
    plt.figure(figsize=(5, 4))

    maxy = 0.1
    miny = -0.5

    # medians
    plt.plot(diameter, medianmag, color='red')

    # CL68 & CL95
    plt.fill_between(diameter, minmag, maxmag, color='orange', alpha=0.7)
    plt.fill_between(diameter, minmag2, maxmag2, color='orange', alpha=0.3)

    # plot median FWHM
    plt.plot([medianFWHM, medianFWHM], [miny, maxy], color='darkslategray',
             label='Median FWHM')

    # plot aperture
    plt.plot([max_aperture, max_aperture], [miny, maxy], '-', color='purple',
             label="{} pix".format(max_aperture))

    # base aperture
    plt.plot([aperture, aperture], [miny, maxy], '-', color='blue',
             label=f'{aperture:.3f}-diameter')

    # region around zero
    plt.plot([0, max(diameter)], [0, 0], color='blue')
    plt.fill_between([0, max(diameter)], [-1e-2, -1e-2], [1e-2, 1e-2],
                     color='blue', alpha=0.3)

    # Plot parameters
    plt.ylim(miny, maxy)
    plt.xlim(0, max(diameter))

    # Labels
    plt.legend()
    plt.xlabel("Aperture Diameter (pix)")
    plt.ylabel("$m_{k+1} - m_{k}$")
    plt.title(f"Magnitude growth curve in {filt}, {starcount} stars")
    plt.savefig(save_file, bbox_inches='tight')
    plt.close()


def apply_aperture_correction(catalog,
                              filt,
                              sexconf,
                              aperture,
                              apercorr_file,
                              save_file,
                              field = 'NoFieldName',
                              sexmode = 'NoSexMode',
                              drname = 'NoDRname'):

    """
    Applies aperture correction to SExtractor photometry.
    This function removes the APER column from SExtractor catalogs and adds the
    PStotal column and other desired apertures defined in aper_names and
    aper_ids

    Parameters
    ----------
    catalog : str
        Location of SExtractor photometry catalog
    filt : str
        Name of the filter
    sexconf : str
        SExtractor configuration file for this filter photometry
    aperture : float
        Base aperture to apply aperture correction
    apercorr_file : str
        Location of the aperture correction file
    save_file : str
        Desired location to save new catalog
    field : str
        Name of the field to be added to the filter_ID
    drname : str
        Data release designation to be added to the filter_ID
    sexmode : str
        dual/single SExtractor mode to be added to the filter_ID

    Returns
    -------
    Saves new catalog with aperture corrected apertures (PStotal)

    """

    # Read catalog
    cat = fits.open(catalog)
    cat_data = cat[1].data

    # Read aper correction
    aper_corr_dict = zp_read(apercorr_file)

    # Create new fits catalog with new columns
    new_data = []

    for col in cat_data.columns:
        new_data.append(col)

    # Get aperture list
    apertures_list = get_apertures_from_sexconf(sexconf)  # type: np.ndarray

    if apertures_list is None:
        raise ValueError(f"Could not find param PHOT_APERTURES in {sexconf}.")

    # Get base aperture ID (allowing a rounding error up to the third decimal)
    round_list = np.around(apertures_list, 3)
    round_aper = np.around(aperture, 3)
    aper_id    = np.where(round_list == round_aper)[0][0]

    # Apply aperture correction
    aper_corr = aper_corr_dict[f"SPLUS_{filt}"]
    flux_corr = 10**(-aper_corr/2.5)

    col = copy.deepcopy(cat_data.columns['MAG_APER'].array[:, aper_id])
    f = col != 99
    col[f] = col[f] + aper_corr
    new_data.append(fits.Column(name=f'MAG_PStotal',
                                format='1E',
                                array=col))

    col = copy.deepcopy(cat_data.columns['MAGERR_APER'].array[:, aper_id])
    new_data.append(fits.Column(name=f'MAGERR_PStotal',
                                format='1E',
                                array=col))

    col = copy.deepcopy(cat_data.columns['FLUX_APER'].array[:, aper_id] * flux_corr)
    new_data.append(fits.Column(name=f'FLUX_PStotal',
                                format='1E',
                                array=col))

    col = copy.deepcopy(cat_data.columns['FLUXERR_APER'].array[:, aper_id])
    new_data.append(fits.Column(name=f'FLUXERR_PStotal',
                                format='1E',
                                array=col))

    # Save corrected data to save_file fits catalog
    hdu = fits.BinTableHDU.from_columns(new_data)
    hdu.writeto(save_file)


################################################################################
# Master photometry

#############################################
# Extract photometry from SExtractor catalogs

def extract_sex_photometry(catalog, save_file, filt):
    """
    Loads a SExtractor catalog and extracts only the PStotal photometry,
    renaming the columns to the format used by the pipeline

    Parameters
    ----------
    catalog : str
        Location of SExtractor output fits catalog
    save_file : str
        Location to save catalog with photometry only
    filt : str
        Name of the catalog's filter

    Returns
    -------
    Saves file with only the photometry

    """

    filt_standard = translate_filter_standard(filt)

    photometry_data = []

    # Load data from filter catalog
    cat      = fits.open(catalog)
    cat_data = cat[1].data

    photometry_data.append(cat_data.columns['NUMBER'])
    photometry_data[-1].name = f'{filt}_SExNumber'

    photometry_data.append(cat_data.columns['ALPHA_J2000'])
    photometry_data[-1].name = 'RA'

    photometry_data.append(cat_data.columns['DELTA_J2000'])
    photometry_data[-1].name = 'DEC'

    photometry_data.append(cat_data.columns['X_IMAGE'])
    photometry_data[-1].name = 'X'

    photometry_data.append(cat_data.columns['Y_IMAGE'])
    photometry_data[-1].name = 'Y'

    photometry_data.append(cat_data.columns['MAG_PStotal'])
    photometry_data[-1].name = f'SPLUS_{filt}'

    photometry_data.append(cat_data.columns['MAGERR_PStotal'])
    photometry_data[-1].name = f'SPLUS_{filt}_err'

    photometry_data.append(cat_data.columns['CLASS_STAR'])
    photometry_data[-1].name = f'CLASS_STAR'

    # Generate HDU from columns
    hdu = fits.BinTableHDU.from_columns(photometry_data)

    # Save master HDU
    hdu.writeto(save_file)
    print('Created file %s' % save_file)


def extract_psf_photometry(catalog, save_file, filt):
    """
    Loads a DOPHOT catalog and extracts only the photometry, renaming the
    columns to the format used by the pipeline.

    Parameters
    ----------
    catalog : str
        Location of dophot output ascii catalog
    save_file : str
        Location to save catalog with photometry only
    filt : str
        Name of the catalog's filter

    Returns
    -------
    Saves file with only the photometry

    """

    photometry_data = []

    # Load data from filter catalog
    cat_data = pd.read_csv(catalog,
                           delim_whitespace=True,
                           escapechar = "#")

    # Get x,y coordinates
    x = cat_data.loc[:, 'xpos'].array
    y = cat_data.loc[:, 'ypos'].array

    # Get ra,dec coordinates
    filt_standard = translate_filter_standard(filt)
    ra = cat_data.loc[:, f'RA_{filt_standard}'].array
    dec = cat_data.loc[:, f'DEC_{filt_standard}'].array

    # Add number
    col_array = cat_data.loc[:, ' Star_number'].array
    photometry_data.append(fits.Column(name=f'{filt}_DoPHOTNumber',
                                       format='1J',
                                       array=col_array))

    # Add RA
    photometry_data.append(fits.Column(name=f'RA',
                                       format='1E',
                                       array=ra))

    # Add DEC
    photometry_data.append(fits.Column(name=f'DEC',
                                       format='1E',
                                       array=dec))

    # Add x
    photometry_data.append(fits.Column(name=f'X',
                                       format='1E',
                                       array=x))

    # Add y
    photometry_data.append(fits.Column(name=f'Y',
                                       format='1E',
                                       array=y))

    # Add mag
    col_array = cat_data.loc[:, 'fitmag'].array
    photometry_data.append(fits.Column(name=f'SPLUS_{filt}',
                                       format='1E',
                                       array=col_array))

    # Add mag error
    col_array = cat_data.loc[:, 'err_fitmag'].array
    photometry_data.append(fits.Column(name=f'SPLUS_{filt}_err',
                                       format='1E',
                                       array=col_array))

    # Add flag_star
    col_array = cat_data.loc[:, 'FLAG_STAR'].array
    photometry_data.append(fits.Column(name=f'CLASS_STAR',
                                       format='1E',
                                       array=col_array))

    # Generate HDU from columns
    hdu = fits.BinTableHDU.from_columns(photometry_data)

    # Save master HDU
    hdu.writeto(save_file)
    print('Created file %s' % save_file)


def format_master_photometry(catalog, save_file, filters, field = 'NoFieldName',
                             sexmode = 'NoSexMode', drname = 'NoDRname'):

    """
    Reads the previously created master catalog and formats it removing
    multiple columns and filling nan values with 99.

    RA, DEC, X, Y columns are selected from the reddest filter in which the
    source was detected

    Parameters
    ----------
    catalog : str
        Location of unformated master photometry file
    save_file : str
        Location to save formated master photometry file
    filters : sized
        List of filters, from bluest to reddest
    field : str
        Name of the field to be added to the filter_ID
    drname : str
        Data release designation to be added to the filter_ID
    sexmode : str
        dual/single SExtractor mode to be added to the filter_ID

    Returns
    -------
    Saves formated master photometry file
    """

    photometry_data = []

    # Load data from filter catalog
    cat      = fits.open(catalog)
    cat_data = cat[1].data

    N = cat_data.shape[0]

    calib_ID = [f'calib_{drname}_{field}_{sexmode}_{i:07d}'
                for i in range(1, N+1)]

    ra  = np.full(N, np.nan)
    dec = np.full(N, np.nan)

    x = np.full(N, np.nan)
    y = np.full(N, np.nan)

    class_star = np.full(N, np.nan)

    # Add new number column to new fits catalog
    photometry_data.append(fits.Column(name   = 'calib_ID',
                                       format = '50A',
                                       array  = calib_ID))

    # Iteratively fill coords and class_star
    for i in range(len(filters), 0, -1):
        ra_i = cat_data.columns[f'RA_{i}'].array
        ra[np.isnan(ra)] = ra_i[np.isnan(ra)]

        dec_i = cat_data.columns[f'DEC_{i}'].array
        dec[np.isnan(dec)] = dec_i[np.isnan(dec)]

        x_i = cat_data.columns[f'X_{i}'].array
        x[np.isnan(x)] = x_i[np.isnan(x)]

        y_i = cat_data.columns[f'Y_{i}'].array
        y[np.isnan(y)] = y_i[np.isnan(y)]

        class_star_i = cat_data.columns[f'CLASS_STAR_{i}'].array
        class_star[np.isnan(class_star)] = class_star_i[np.isnan(class_star)]

    # Add to new fits catalog
    photometry_data.append(fits.Column(name   = 'RAJ2000',
                                       format = '1E',
                                       array  = ra))

    photometry_data.append(fits.Column(name   = 'DEJ2000',
                                       format = '1E',
                                       array  = dec))

    photometry_data.append(fits.Column(name   = 'X',
                                       format = '1E',
                                       array  = x))

    photometry_data.append(fits.Column(name   = 'Y',
                                       format = '1E',
                                       array  = y))

    photometry_data.append(fits.Column(name   = 'CLASS_STAR',
                                       format = '1E',
                                       array  = class_star))

    # Ndetections
    ndet = np.zeros(N)

    # Add magnitudes
    for i in range(len(filters)):
        filt = filters[i]

        # Add to new fits catalog
        if sexmode in ["single", "dual"]:
            colname = f'{filt}_SExNumber'
            filter_ID = cat_data.columns[colname].array
            photometry_data.append(fits.Column(name=colname,
                                               format='50A',
                                               array=filter_ID))
        elif sexmode == "psf":
            colname = f'{filt}_DoPHOTNumber'
            filter_ID = cat_data.columns[colname].array
            photometry_data.append(fits.Column(name=colname,
                                               format='50A',
                                               array=filter_ID))

        mag     = cat_data.columns[f'SPLUS_{filt}'].array
        mag_err = cat_data.columns[f'SPLUS_{filt}_err'].array

        # Add detections
        ndet[~np.isnan(mag)] += 1

        # Fill nan values
        mag[np.isnan(mag)] = 99
        mag_err[np.isnan(mag_err)] = 99

        # Add to new fits catalog
        photometry_data.append(fits.Column(name=f'SPLUS_{filt}',
                                           format='1E',
                                           array=mag))

        photometry_data.append(fits.Column(name=f'SPLUS_{filt}_err',
                                           format='1E',
                                           array=mag_err))

    # Count detections
    photometry_data.append(fits.Column(name=f'NDET',
                                       format='1I',
                                       array=ndet))
    # Generate HDU from columns
    hdu = fits.BinTableHDU.from_columns(photometry_data)

    # Save master HDU
    hdu.writeto(save_file)
    print('Created file %s' % save_file)


################################################################################
# Crossmatch


def download_vizier_catalog_for_splus_field(vizier_catalog_id, columns,
                                            splus_image = None, fieldID_catalog = None,
                                            column_filters = None, pixscale = 0.55):
    """
    Downloads a catalog from vizier in the region covered by an splus_image

    Parameters
    ----------
    splus_image : str
        Location of the S-PLUS image .fz file
    vizier_catalog_id : str
        ID of the catalog in the vizier database
    columns: list
        List of columns to download
    column_filters: dictionary
        Column filters, see astroquery.Vizier documentation
    pixscale : float
        Pixel scale in arcsec/pixel. Only used if image has no PIXSCALE
        parameter in the header

    Returns
    -------
    astropy.table.table.Table
        Catalog obtained from the VIZIER database
    """

    v = Vizier()

    # Change row limit to get whole catalog
    v.ROW_LIMIT = -1

    # List of columns to download
    v.columns = columns

    if column_filters is not None:
        v.column_filters = column_filters

    if splus_image is not None:
        # Extract field ra and dec from image header
        head = fits.open(splus_image)[1].header
        try:
            ra = head['CRVAL1']   # degrees
            dec = head['CRVAL2']  # degrees
        except ValueError: # Works for Yazan images
            ra = head['RA']  # degrees
            dec = head['DEC']  # degrees

    else:
        cat = fits.open(fieldID_catalog)
        cat = cat[1].data

        ra_array  = cat.columns["FIELD_ID_RA"].array
        dec_array = cat.columns["FIELD_ID_DEC"].array

        # Estimate center of the field
        ra = np.median(ra_array)
        dec = np.median(dec_array)

    c = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg))

    try:
        width = head['NAXIS1'] * head['PIXSCALE'] / 3600.  # degrees
        height = head['NAXIS2'] * head['PIXSCALE'] / 3600.  # degrees

    except KeyError:
        warnings.warn(('No PIXSCALE value in image header. Using default value '
                      f'of {pixscale} for S-PLUS'))

        width = head['NAXIS1'] * pixscale / 3600.  # degrees
        height = head['NAXIS2'] * pixscale / 3600.  # degrees

    except UnboundLocalError:
        width = 11000 * pixscale / 3600 # degrees
        height = 11000 * pixscale / 3600 # degrees

    # Retrieve catalog data in the field
    query = v.query_region(c, width = width*u.deg, height = height*u.deg,
                           catalog = vizier_catalog_id)

    catalog = query[vizier_catalog_id]

    return catalog


def download_galex(save_file, image = None, fieldID_catalog = None):
    """
    Downloads the GALEX DR6/7 catalog from the vizier database in the region
    covered by an splus image. Changes column names for the format used by the
    pipeline, deletes unnecessary columns and saves results to a fits file

    Parameters
    ----------
    image : str
        Location of the splus image (must be .fz)
    save_file : str
        Location to save the retrieved catalog (must be .fits)

    Returns
    -------
    Saves catalog in the desired location
    """

    # Vizier Table
    cat_id = "II/335/galex_ais"

    columns = ['Name', 'RAJ2000', 'DEJ2000', 'FUVmag', 'e_FUVmag', 'NUVmag',
               'e_NUVmag']

    # Download catalog
    catalog = download_vizier_catalog_for_splus_field(splus_image = image,
                                               fieldID_catalog=fieldID_catalog,
                                               vizier_catalog_id = cat_id,
                                               columns = columns)

    # Rename columns
    catalog.columns['Name'].name = 'GALEX_ID'
    catalog.columns['RAJ2000'].name = 'GALEX_RAJ2000'
    catalog.columns['DEJ2000'].name = 'GALEX_DEJ2000'
    catalog.columns['FUVmag'].name = 'GALEX_FUV'
    catalog.columns['e_FUVmag'].name = 'GALEX_FUV_err'
    catalog.columns['NUVmag'].name = 'GALEX_NUV'
    catalog.columns['e_NUVmag'].name = 'GALEX_NUV_err'

    # Truncate description (usually to big to save as fits)
    catalog.meta['description'] = catalog.meta['description'][:55]

    # Save table as fits
    catalog.write(save_file, overwrite = True)


def download_refcat2(save_file, image = None, fieldID_catalog = None):

    """
    Downloads the ATLAS REFCAT2 catalog from the vizier database in the region
    covered by an splus image. Changes column names for the format used by the
    pipeline, deletes unnecessary columns and saves results to a fits file

    Parameters
    ----------
    image : str
        Location of the splus image (must be .fz)
    save_file : str
        Location to save the retrieved catalog (must be .fits)

    Returns
    -------
    Saves catalog in the desired location
    """

    # Vizier Table
    cat_id = "J/ApJ/867/105/refcat2"

    columns = ['RA_ICRS', 'DE_ICRS', 'pmRA', 'pmDE', 'Plx', 'gmag',
               'e_gmag', 'rmag', 'e_rmag', 'imag', 'e_imag', 'zmag', 'e_zmag',
               'gcontrib', 'rcontrib', 'icontrib', 'zcontrib', 'AG', 'Ag']

    column_filters = {'Plx': '>0'}

    # Download catalog
    catalog = download_vizier_catalog_for_splus_field(splus_image = image,
                                               fieldID_catalog=fieldID_catalog,
                                               vizier_catalog_id = cat_id,
                                               columns = columns,
                                               column_filters = column_filters)

    ###############################################
    # Covert coordinates from EPOCH 2015.5 to J2000
    ra_icrs = catalog.columns['RA_ICRS']
    de_icrs = catalog.columns['DE_ICRS']
    pmra    = catalog.columns['pmRA']
    pmde    = catalog.columns['pmDE']
    plx     = np.array(catalog.columns['Plx'])

    c = SkyCoord(ra=ra_icrs, dec=de_icrs, frame='icrs',
                 pm_ra_cosdec= pmra, pm_dec = pmde,
                 distance = Distance(parallax=plx*u.mas, allow_negative=True),
                 obstime = Time(2015.5, format='jyear'))

    # Convert epoch from 2015.5 to J2000
    c_j2000 = c.apply_space_motion(Time(2000.0, format='jyear'))

    # Get RA and DEC
    ra = np.array(c_j2000.ra)
    de = np.array(c_j2000.dec)

    ##############################
    # Add RA and DEC J2000 columns
    catalog['REFCAT2_RAJ2000'] = ra
    catalog['REFCAT2_DEJ2000'] = de

    ################
    # Rename columns
    catalog.columns['gmag'].name = 'PS_G'
    catalog.columns['e_gmag'].name = 'PS_G_err'
    catalog.columns['rmag'].name = 'PS_R'
    catalog.columns['e_rmag'].name = 'PS_R_err'
    catalog.columns['imag'].name = 'PS_I'
    catalog.columns['e_imag'].name = 'PS_I_err'
    catalog.columns['zmag'].name = 'PS_Z'
    catalog.columns['e_zmag'].name = 'PS_Z_err'
    catalog.columns['AG'].name = 'AG_Gaia' # G band extinction by Gaia
    catalog.columns['Ag'].name = 'AG_Schlegel' # G band extinction by Schelegel

    # Truncate description (usually to big to save as fits)
    catalog.meta['description'] = catalog.meta['description'][:55]

    ##############################
    # Remove unreliable magnitudes
    # (PS mag estimated from an insuficient number of references)
    f = np.full(len(ra), True)
    for mag in ['g', 'r', 'i', 'z']:
        contrib = np.array(catalog.columns[f'{mag}contrib'])
        f = f & (contrib != '00') & (contrib != '01')

    catalog = catalog[f]

    ####################
    # Save table as fits
    catalog.write(save_file, overwrite = True)


def download_ivezic(save_file, image = None, fieldID_catalog = None):
    """
    Downloads the Ivezic catalog from the vizier database in the region
    covered by an splus image. Changes column names for the format used by the
    pipeline, deletes unnecessary columns and saves results to a fits file

    Parameters
    ----------
    image : str
        Location of the splus image (must be .fz)
    save_file : str
        Location to save the retrieved catalog (must be .fits)

    Returns
    -------
    Saves catalog in the desired location
    """

    # Vizier Table
    cat_id = "J/AJ/134/973/stdcat"

    columns = ['RAJ2000', 'DEJ2000', 'umag', 'e_umag', 'gmag', 'e_gmag',
               'rmag', 'e_rmag', 'imag', 'e_imag', 'zmag', 'e_zmag']

    # Download catalog
    catalog = download_vizier_catalog_for_splus_field(splus_image = image,
                                               fieldID_catalog=fieldID_catalog,
                                               vizier_catalog_id = cat_id,
                                               columns = columns)

    # Rename columns
    catalog.columns['RAJ2000'].name = 'IVEZIC_RAJ2000'
    catalog.columns['DEJ2000'].name = 'IVEZIC_DEJ2000'

    catalog.columns['umag'].name = 'SDSS_U'
    catalog.columns['e_umag'].name = 'SDSS_U_err'
    catalog.columns['gmag'].name = 'SDSS_G'
    catalog.columns['e_gmag'].name = 'SDSS_G_err'
    catalog.columns['rmag'].name = 'SDSS_R'
    catalog.columns['e_rmag'].name = 'SDSS_R_err'
    catalog.columns['imag'].name = 'SDSS_I'
    catalog.columns['e_imag'].name = 'SDSS_I_err'
    catalog.columns['zmag'].name = 'SDSS_Z'
    catalog.columns['e_zmag'].name = 'SDSS_Z_err'

    ###################
    # Remove nan values
    Nrows = np.array(catalog.columns['IVEZIC_RAJ2000']).shape[0]
    f = np.full(Nrows, True)

    for mag in ['U', 'G', 'R', 'I', 'Z']:
        f = f & (np.array(catalog.columns[f'SDSS_{mag}']) < 90)

    catalog = catalog[f]

    # Truncate description (usually to big to save as fits)
    catalog.meta['description'] = catalog.meta['description'][:55]

    # Save table as fits
    catalog.write(save_file, overwrite = True)


def download_sdss(save_file, image = None, fieldID_catalog = None):
    """
    Downloads the SDSS DR12 catalog from the vizier database in the region
    covered by an splus image. Changes column names for the format used by the
    pipeline, deletes unnecessary columns and saves results to a fits file

    Parameters
    ----------
    image : str
        Location of the splus image (must be .fz)
    save_file : str
        Location to save the retrieved catalog (must be .fits)

    Returns
    -------
    Saves catalog in the desired location
    """

    # Vizier Table
    cat_id = "V/147/sdss12"

    columns = ['RA_ICRS', 'DE_ICRS', 'SDSS12', 'umag', 'e_umag', 'gmag',
               'e_gmag', 'rmag', 'e_rmag', 'imag', 'e_imag', 'zmag', 'e_zmag']

    column_filters = {'class': '=6', 'umag': '<100', 'gmag': '<100',
                      'rmag': '<100', 'imag': '<100', 'zmag': '<100'}

    # Download catalog
    catalog = download_vizier_catalog_for_splus_field(splus_image = image,
                                               fieldID_catalog=fieldID_catalog,
                                               vizier_catalog_id = cat_id,
                                               columns = columns,
                                               column_filters = column_filters)

    # Rename columns
    catalog.columns['RA_ICRS'].name = 'SDSS_RAJ2000'
    catalog.columns['DE_ICRS'].name = 'SDSS_DEJ2000'

    catalog.columns['umag'].name = 'SDSS_U'
    catalog.columns['e_umag'].name = 'SDSS_U_err'
    catalog.columns['gmag'].name = 'SDSS_G'
    catalog.columns['e_gmag'].name = 'SDSS_G_err'
    catalog.columns['rmag'].name = 'SDSS_R'
    catalog.columns['e_rmag'].name = 'SDSS_R_err'
    catalog.columns['imag'].name = 'SDSS_I'
    catalog.columns['e_imag'].name = 'SDSS_I_err'
    catalog.columns['zmag'].name = 'SDSS_Z'
    catalog.columns['e_zmag'].name = 'SDSS_Z_err'

    # Truncate description (usually to big to save as fits)
    catalog.meta['description'] = catalog.meta['description'][:55]

    # Save table as fits
    catalog.write(save_file, overwrite = True)


def download_gaiadr2(save_file, image = None, fieldID_catalog = None):
    """
    Downloads the Gaia EDR3 catalog from the vizier database in the region
    covered by an splus image. Changes column names for the format used by the
    pipeline, deletes unnecessary columns and saves results to a fits file

    Parameters
    ----------
    image : str
        Location of the splus image (must be .fz)
    save_file : str
        Location to save the retrieved catalog (must be .fits)

    Returns
    -------
    Saves catalog in the desired location
    """

    # Vizier Table
    cat_id = "I/345/gaia2"

    columns = ['RA_ICRS', 'DE_ICRS', 'Source', 'Plx', 'e_Plx', 'pmRA', 'pmDE',
               'Gmag', 'e_Gmag', 'BPmag', 'e_BPmag', 'RPmag', 'e_RPmag',
               'AG']

    column_filters = {'Plx': '>0', 'RPlx': '>5',
                      'Gmag': '<30', 'BPmag': '<30', 'RPmag': '<30'}

    # Download catalog
    catalog = download_vizier_catalog_for_splus_field(splus_image = image,
                                               fieldID_catalog=fieldID_catalog,
                                               vizier_catalog_id = cat_id,
                                               columns = columns,
                                               column_filters = column_filters)

    ###############################################
    # Covert coordinates from EPOCH 2016 to J2000
    ra_icrs = catalog.columns['RA_ICRS']
    de_icrs = catalog.columns['DE_ICRS']
    pmra    = catalog.columns['pmRA']
    pmde    = catalog.columns['pmDE']
    plx     = np.array(catalog.columns['Plx'])

    c = SkyCoord(ra=ra_icrs, dec=de_icrs, frame='icrs',
                 pm_ra_cosdec= pmra, pm_dec = pmde,
                 distance = Distance(parallax=plx*u.mas, allow_negative=True),
                 obstime = Time(2016, format='jyear'))

    # Convert epoch from 2015.5 to J2000
    c_j2000 = c.apply_space_motion(Time(2000.0, format='jyear'))

    # Get RA and DEC
    ra = np.array(c_j2000.ra)
    de = np.array(c_j2000.dec)

    ##############################
    # Add RA and DEC J2000 columns
    catalog['GAIADR2_RAJ2000'] = ra
    catalog['GAIADR2_DEJ2000'] = de

    # Rename columns
    catalog.columns['Source'].name = 'GAIA_ID'

    catalog.columns['Gmag'].name = 'GAIA_G'
    catalog.columns['e_Gmag'].name = 'GAIA_G_err'
    catalog.columns['BPmag'].name = 'GAIA_BP'
    catalog.columns['e_BPmag'].name = 'GAIA_BP_err'
    catalog.columns['RPmag'].name = 'GAIA_RP'
    catalog.columns['e_RPmag'].name = 'GAIA_RP_err'

    catalog.columns['AG'].name = 'GAIA_AG'

    # Truncate description (usually to big to save as fits)
    catalog.meta['description'] = catalog.meta['description'][:55]

    # Save table as fits
    catalog.write(save_file, overwrite = True)


def download_gaia(save_file, image = None, fieldID_catalog = None):
    """
    Downloads the Gaia EDR3 catalog from the vizier database in the region
    covered by an splus image. Changes column names for the format used by the
    pipeline, deletes unnecessary columns and saves results to a fits file

    Parameters
    ----------
    image : str
        Location of the splus image (must be .fz)
    save_file : str
        Location to save the retrieved catalog (must be .fits)

    Returns
    -------
    Saves catalog in the desired location
    """

    # Vizier Table
    cat_id = "I/350/gaiaedr3"

    columns = ['RA_ICRS', 'DE_ICRS', 'Source', 'Plx', 'pmRA', 'pmDE',
               'Gmag', 'e_Gmag', 'BPmag', 'e_BPmag', 'RPmag', 'e_RPmag']

    column_filters = {'Plx': '>0', 'Gmag': '<30', 'BPmag': '<30', 'RPmag': '<30'}

    # Download catalog
    catalog = download_vizier_catalog_for_splus_field(splus_image = image,
                                               fieldID_catalog=fieldID_catalog,
                                               vizier_catalog_id = cat_id,
                                               columns = columns,
                                               column_filters = column_filters)

    ###############################################
    # Covert coordinates from EPOCH 2016 to J2000
    ra_icrs = catalog.columns['RA_ICRS']
    de_icrs = catalog.columns['DE_ICRS']
    pmra    = catalog.columns['pmRA']
    pmde    = catalog.columns['pmDE']
    plx     = np.array(catalog.columns['Plx'])

    c = SkyCoord(ra=ra_icrs, dec=de_icrs, frame='icrs',
                 pm_ra_cosdec= pmra, pm_dec = pmde,
                 distance = Distance(parallax=plx*u.mas, allow_negative=True),
                 obstime = Time(2016, format='jyear'))

    # Convert epoch from 2015.5 to J2000
    c_j2000 = c.apply_space_motion(Time(2000.0, format='jyear'))

    # Get RA and DEC
    ra = np.array(c_j2000.ra)
    de = np.array(c_j2000.dec)

    ##############################
    # Add RA and DEC J2000 columns
    catalog['GAIA_RAJ2000'] = ra
    catalog['GAIA_DEJ2000'] = de

    # Rename columns
    catalog.columns['Source'].name = 'GAIA_ID'

    catalog.columns['Gmag'].name = 'GAIA_G'
    catalog.columns['e_Gmag'].name = 'GAIA_G_err'
    catalog.columns['BPmag'].name = 'GAIA_BP'
    catalog.columns['e_BPmag'].name = 'GAIA_BP_err'
    catalog.columns['RPmag'].name = 'GAIA_RP'
    catalog.columns['e_RPmag'].name = 'GAIA_RP_err'

    # Truncate description (usually to big to save as fits)
    catalog.meta['description'] = catalog.meta['description'][:55]

    # Save table as fits
    catalog.write(save_file, overwrite = True)

def download_skymapper(save_file, image = None, fieldID_catalog = None):
    """
    Downloads the Skymapper catalog from the vizier database in the region
    covered by an splus image. Changes column names for the format used by the
    pipeline, deletes unnecessary columns and saves results to a fits file

    Parameters
    ----------
    image : str
        Location of the splus image (must be .fz)
    save_file : str
        Location to save the retrieved catalog (must be .fits)

    Returns
    -------
    Saves catalog in the desired location
    """

    # Vizier Table
    cat_id = "II/358/smss"

    columns = ['RAICRS', 'DEICRS', 'uPSF', 'e_uPSF', 'vPSF', 'e_vPSF',
               'gPSF', 'e_gPSF', 'rPSF', 'e_rPSF', 'iPSF', 'e_iPSF',
               'zPSF', 'e_zPSF']

    column_filters = {'ClassStar': '>0.5', 'uPSF': '<50', 'vPSF': '<50',
                      'gPSF': '<50', 'rPSF': '<50', 'iPSF': '<50',
                      'zPSF': '<50'}

    # Download catalog
    catalog = download_vizier_catalog_for_splus_field(splus_image = image,
                                               fieldID_catalog=fieldID_catalog,
                                               vizier_catalog_id = cat_id,
                                               columns = columns,
                                               column_filters = column_filters)

    # Rename columns
    catalog.columns['RAICRS'].name = 'SKYMAPPER_RAJ2000'
    catalog.columns['DEICRS'].name = 'SKYMAPPER_DEJ2000'

    catalog.columns['uPSF'].name = 'SM_U'
    catalog.columns['e_uPSF'].name = 'SM_U_err'
    catalog.columns['vPSF'].name = 'SM_V'
    catalog.columns['e_vPSF'].name = 'SM_V_err'
    catalog.columns['gPSF'].name = 'SM_G'
    catalog.columns['e_gPSF'].name = 'SM_G_err'
    catalog.columns['rPSF'].name = 'SM_R'
    catalog.columns['e_rPSF'].name = 'SM_R_err'
    catalog.columns['iPSF'].name = 'SM_I'
    catalog.columns['e_iPSF'].name = 'SM_I_err'
    catalog.columns['zPSF'].name = 'SM_Z'
    catalog.columns['e_zPSF'].name = 'SM_Z_err'

    ###################
    # Remove nan values
    Nrows = np.array(catalog.columns['SKYMAPPER_RAJ2000']).shape[0]
    f = np.full(Nrows, True)

    for mag in ['U', 'G', 'R', 'I', 'Z']:
        f = f & ~np.isnan(catalog.columns[f'SM_{mag}'])

    catalog = catalog[f]

    # Truncate description (usually to big to save as fits)
    catalog.meta['description'] = catalog.meta['description'][:55]

    # Save table as fits
    catalog.write(save_file, overwrite = True)


def download_reference(reference, save_file, image = None,
                       fieldID_catalog = None):
    """
    General function to download a specific reference catalog

    Parameters
    ----------
    image : str
        Location of the splus image (must be .fz)
    reference : str
        Indiciates the reference catalog to download
    save_file : str
        Location to save the retrieved catalog (must be .fits)

    Returns
    -------
    Saves catalog in the desired location
    """

    if reference.lower() == 'galex':
        download_galex(save_file=save_file, image=image,
                       fieldID_catalog=fieldID_catalog)

    elif reference.lower() == 'refcat2':
        download_refcat2(save_file=save_file, image=image,
                         fieldID_catalog=fieldID_catalog)

    elif reference.lower() == 'ivezic':
        download_ivezic(save_file=save_file, image=image,
                        fieldID_catalog=fieldID_catalog)

    elif reference.lower() == 'sdss':
        download_sdss(save_file=save_file, image=image,
                      fieldID_catalog=fieldID_catalog)

    elif reference.lower() == 'gaia':
        download_gaia(save_file=save_file, image=image,
                      fieldID_catalog=fieldID_catalog)

    elif reference.lower() == 'gaiadr2':
        download_gaiadr2(save_file=save_file, image=image,
                         fieldID_catalog=fieldID_catalog)

    elif reference.lower() == 'skymapper':
        download_skymapper(save_file=save_file, image=image,
                         fieldID_catalog=fieldID_catalog)

    else:
        raise ValueError((f"Reference {reference} is not supported. Currently "
                          "supported values are 'GALEX', 'REFCAT2', 'IVEZIC', "
                          "'SDSS', and 'GAIA'"))


def crossmatch_catalog_name(field, conf):
    """
    Generates the name of the S-PLUS/references crossmatched catalog taking
    into account the photometry mode and the reference catalog(s) used for
    calibration

    Parameters
    ----------
    field : str
        Name of the S-PLUS field
    conf : dict
        Dictionary loaded from the configuration file

    Returns
    -------
    str
        Name of the crossmatched catalog
    """

    calib_phot = conf['calibration_photometry']
    cmatch_name = f"{field}_SPLUS_{calib_phot}"

    nref = len(conf['reference_catalog'])
    for i in range(nref):
        cmatch_name += f"_{conf['reference_catalog'][i]}"

    cmatch_name += ".fits"

    return cmatch_name


def convert_gaia_Vega2AB(gaia_catalog, save_file):
    """
    Converts gaia magnitudes from VEGA system to AB system

    gaia_catalog: str
        output of download_gaiadr2
    save_file: str
        path where the output AB magnitudes will be saved
    """

    # Conversion constants
    # reference https://gea.esac.esa.int/archive/documentation/GDR2/Data_processing/chap_cu5pho/sec_cu5pho_calibr/ssec_cu5pho_calibr_extern.html
    zp_G_Vega  = 25.6884
    zp_BP_Vega = 25.3514
    zp_RP_Vega = 24.7619

    zp_G_AB  = 25.7934
    zp_BP_AB = 25.3806
    zp_RP_AB = 25.1161

    # Load GAIA VEGA catalog
    # Load photometry catalog (with aperture correction)
    vega_cat = fits.open(gaia_catalog)
    vega_cat = vega_cat[1].data

    # Create new data Table
    cat = []

    for col in vega_cat.columns:
        if col.name == "GAIA_G":
            col.array += zp_G_AB - zp_G_Vega
        elif col.name == "GAIA_BP":
            col.array += zp_BP_AB - zp_BP_Vega
        elif col.name == "GAIA_RP":
            col.array += zp_RP_AB - zp_RP_Vega

        cat.append(col)

    hdul_vac = fits.BinTableHDU.from_columns(cat)
    hdul_vac.writeto(save_file)

################################################################################
# Extinction Correction

# Previously
# http://svo2.cab.inta-csic.es/svo/theory/fps3/index.php?mode=browse
_lambda_eff = {  'SPLUS_U': 3542.07, 'SPLUS_F378': 3783.69,
              'SPLUS_F395': 3940.17, 'SPLUS_F410': 4094.63,
              'SPLUS_F430': 4286.52,    'SPLUS_G': 4715.83,
              'SPLUS_F515': 5131.93,    'SPLUS_R': 6202.57,
              'SPLUS_F660': 6616.95,    'SPLUS_I': 7627.01,
              'SPLUS_F861': 8607.17,    'SPLUS_Z': 8913.47,
               'GALEX_FUV': 1549.02,  'GALEX_NUV': 2304.74,
                  'SDSS_U': 3608.04,     'SDSS_G': 4671.78,
                  'SDSS_R': 6141.12,     'SDSS_I': 7457.89,
                  'SDSS_Z': 8922.78,       'PS_G': 4810.88,
                    'PS_R': 6156.36,       'PS_I': 7503.68,
                    'PS_Z': 8668.56,    'GAIA_BP': 5020.92,
                  'GAIA_G': 5836.31,    'GAIA_RP': 7588.83,
                    'SM_U': 3500.22,       'SM_V': 3878.68,
                    'SM_G': 5016.05,       'SM_R': 6076.85,
                    'SM_I': 7732.83,       'SM_Z': 9120.25	}

# Previously
# source: http://stev.oapd.inaf.it/cgi-bin/cmd_3.5
#_Alambda_Av = {  'SPLUS_U': 1.60674, 'SPLUS_F378': 1.48704,
#              'SPLUS_F395': 1.43979, 'SPLUS_F410': 1.40023,
#              'SPLUS_F430': 1.34897,    'SPLUS_G': 1.21256,
#              'SPLUS_F515': 1.09187,    'SPLUS_R': 0.85465,
#              'SPLUS_F660': 0.80719,    'SPLUS_I': 0.65071,
#              'SPLUS_F861': 0.52064,    'SPLUS_Z': 0.42634,
#               'GALEX_FUV': 2.61686,  'GALEX_NUV': 2.80817,
#                  'SDSS_U': 1.57465,     'SDSS_G': 1.22651,
#                  'SDSS_R': 0.86639,     'SDSS_I': 0.68311,
#                  'SDSS_Z': 0.48245,       'PS_G': 1.17994,
#                    'PS_R': 0.86190,       'PS_I': 0.67648,
#                    'PS_Z': 0.51296,    'GAIA_BP': 1.09909,
#                  'GAIA_G': 0.83139,    'GAIA_RP': 0.63831,
#                    'SM_U': 1.60574,       'SM_V': 1.47086,
#                    'SM_G': 1.10789,       'SM_R': 0.87072,
#                    'SM_I': 0.64145,       'SM_Z': 0.46515}

# Current
# http://svo2.cab.inta-csic.es/svo/theory/fps3/index.php?mode=browse
_Alambda_Av = {  'SPLUS_U': 1.61, 'SPLUS_F378': 1.52,
              'SPLUS_F395': 1.46, 'SPLUS_F410': 1.40,
              'SPLUS_F430': 1.33,    'SPLUS_G': 1.20,
              'SPLUS_F515': 1.10,    'SPLUS_R': 0.864,
              'SPLUS_F660': 0.798,    'SPLUS_I': 0.648,
              'SPLUS_F861': 0.539,    'SPLUS_Z': 0.513,
               'GALEX_FUV': 2.61,  'GALEX_NUV': 2.85,
                  'SDSS_U': 1.58,     'SDSS_G': 1.22,
                  'SDSS_R': 0.884,     'SDSS_I': 0.673,
                  'SDSS_Z': 0.514,       'PS_G': 1.18,
                    'PS_R': 0.881,       'PS_I': 0.667,
                    'PS_Z': 0.534,    'GAIA_BP': 1.13,
                  'GAIA_G': 0.939,    'GAIA_RP': 0.658,
                    'SM_U': 1.63,       'SM_V': 1.50,
                    'SM_G': 1.11,       'SM_R': 0.885,
                    'SM_I': 0.636,       'SM_Z': 0.496}


def get_EBV_schlegel(RA, DEC, ebv_maps_path):

    """
    Returns Schlegel's E_B-V for positions RA and DEC

    Parameters
    ----------
    RA : np.array
        List of sources' right ascentions
    DEC : np.array
        List of sources' declinations
    ebv_maps_path : str
        Location of ISM extinction maps

    Returns
    -------
    np.array
        array of E_B-V in the position of the sources
    """

    m = sfdmap.SFDMap(ebv_maps_path)
    EBV = m.ebv(RA, DEC)

    return EBV



def correct_extinction_schlegel(catalog, save_file, ebv_maps_path,
                                filters_Alambda_Av=None, reverse = False,
                                include_mod = False):
    """
    Corrects ISM extinction in the given catalog using Schelegel EB-V maps

    Parameters
    ----------
    catalog : str
        Location of the catalog which will have exctinction corrected
    save_file : str
        Location of file to save the results
    ebv_maps_path : str
        Path to directory containing extinction maps
    filters_Alambda_Av : dict
        Dictionary with values of Alambda/Av
    reverse : bool
        If true, extinction is applied instead of corrected
    include_mod : bool
        If true, also applies correction to columns {filt}_mod

    Returns
    -------
    Saves catalog with corrected extinctions
    """

    if filters_Alambda_Av is None:
        filters_Alambda_Av = _Alambda_Av

    # Also apply correction to model predicted magnitudes
    if include_mod is True:
        filters = list(filters_Alambda_Av.keys())
        for filt in filters:
            filters_Alambda_Av[f"{filt}_mod"] = filters_Alambda_Av[filt]

    m = sfdmap.SFDMap(ebv_maps_path)

    # Reading Catalog data
    cat = fits.open(catalog)
    cat_data = cat[1].data

    ##############
    # Obtaining AV
    RA = cat_data['RAJ2000']
    DEC = cat_data['DEJ2000']

    EBV = m.ebv(RA, DEC)
    Av = EBV * 3.1

    ####################################
    # Correct extinction for each filter

    for filt in list(filters_Alambda_Av.keys()):
        if filt in cat_data.columns.names:

            Alambda = Av * filters_Alambda_Av[filt]

            not_nan = cat_data.columns[filt].array != 99

            # If reverse, extinction is applied
            if reverse is True:
                cat_data.columns[filt].array[not_nan] += Alambda[not_nan]
            else:
                cat_data.columns[filt].array[not_nan] -= Alambda[not_nan]

    # Save output data
    cat.writeto(save_file)
    print('Created file %s' % save_file)


def correct_extinction_gorski(catalog, save_file, ebv_maps_path,
                              filters_Alambda_Av=None, reverse = False,
                              include_mod = False):
    """
    Corrects ISM extinction in the given catalog using Gorski et al. 2020
    EB-V maps for the small and large magellanic clouds

    Parameters
    ----------
    catalog : str
        Location of the catalog which will have exctinction corrected
    save_file : str
        Location of file to save the results
    ebv_maps_path : str
        Path to directory containing extinction maps
    filters_Alambda_Av : dict
        Dictionary with values of Alambda/Av
    reverse : bool
        If true, extinction is applied instead of corrected
    include_mod : bool
        If true, also applies correction to columns {filt}_mod

    Returns
    -------
    Saves catalog with corrected extinctions
    """

    # Add on a later date for proper calibration of the MCs
    # Extinction maps are already in the /stes/Resources/Extinction path
    if filters_Alambda_Av is None:
        filters_Alambda_Av = _Alambda_Av

    # Also apply correction to model predicted magnitudes
    if include_mod is True:
        filters = list(filters_Alambda_Av.keys())
        for filt in filters:
            filters_Alambda_Av[f"{filt}_mod"] = filters_Alambda_Av[filt]

    # SMC and LMC grid coverage
    # Made by hand using topcat
    smc_polygon = Polygon([[13.398,-71.201], [20.481,-71.201], [22.029,-74.197],
                           [13.770,-74.272], [13.559,-74.693], [12.321,-74.569],
                           [12.222,-74.730], [11.627,-74.643], [11.553,-74.854],
                           [4.891,-74.817],  [5.708,-72.315],  [11.392,-72.377],
                           [11.516,-71.609], [13.299,-71.585]])

    lmc_polygon = Polygon([[68.89, -66.51], [79.10, -66.51], [79.08, -67.67],
                           [86.66, -67.71], [86.75, -68.25], [91.55, -68.32],
                           [91.74, -68.87], [93.52, -68.90], [94.82, -71.31],
                           [93.48, -71.43], [93.99, -73.08], [89.85, -73.15],
                           [89.79, -72.57], [84.21, -72.53], [84.16, -71.98],
                           [78.71, -71.93], [78.75, -71.38], [73.45, -71.38],
                           [73.49, -70.85], [66.78, -70.67]])

    # Reading Catalog data
    cat = fits.open(catalog)
    cat_data = cat[1].data

    ##################################
    # Choose between LMC and SMC grids

    RA = cat_data['RAJ2000']
    DEC = cat_data['DEJ2000']

    within_smc = np.full(len(RA), False)
    within_lmc = np.full(len(RA), False)

    # Checking if points are within lmc or smc
    for i in range(len(RA)):
        p = Point(RA[i], DEC[i])
        within_smc[i] = p.within(smc_polygon)
        within_lmc[i] = p.within(lmc_polygon)

    if within_smc.sum() > 0:
        grid = os.path.join(ebv_maps_path, 'Gorski_EBV_res3_smc.txt')

    elif within_lmc.sum() > 0:
        grid = os.path.join(ebv_maps_path, 'Gorski_EBV_res3_lmc.txt')

    else:
        raise ValueError("Cannot calibrate field using Gorski EBV maps")

    #################
    # Interpolate EBV

    ebv_map = pd.read_csv(grid, delim_whitespace=True, comment = "#",
                    names = ['RA', 'DEC', 'EBV', 'e_EBV', 'sigma_RC', 'N_RC'])

    print("Interpolating extinction map")
    ebv_interp = interp2d(ebv_map['RA'], ebv_map['DEC'], ebv_map['EBV'])

    # Get EB-V
    EBV = np.full(len(RA), np.nan)

    for i in range(len(RA)):
        EBV[i] = ebv_interp(RA[i],DEC[i])

    Av = EBV * 3.1

    ####################################
    # Correct extinction for each filter
    for filt in list(filters_Alambda_Av.keys()):
        if filt in cat_data.columns.names:

            Alambda = Av * filters_Alambda_Av[filt]

            not_nan = cat_data.columns[filt].array != 99
            # If reverse, extinction is applied
            if reverse is True:
                cat_data.columns[filt].array[not_nan] += Alambda[not_nan]
            else:
                cat_data.columns[filt].array[not_nan] -= Alambda[not_nan]

    # Save output data
    cat.writeto(save_file)
    print('Created file %s' % save_file)


def correct_extinction_gaiadr2(catalog, save_file, ebv_maps_path=None,
                               filters_Alambda_Av=None, reverse=False,
                               include_mod=False):
    """
    Corrects ISM extinction in the given catalog using GAIA DR2 AG values

    Parameters
    ----------
    catalog : str
        Location of the catalog which will have exctinction corrected.
        The catalog must have been previously crossmatched with Gaia DR2 and
        need to have the GAIA_AG column.
    save_file : str
        Location of file to save the results
    filters_Alambda_Av : dict
        Dictionary with values of Alambda/Av
    ebv_maps_path : None
        Does nothing, only included to simplify backwards compatibility.
    reverse : bool
        If true, extinction is applied instead of corrected
    include_mod : bool
        If true, also applies correction to columns {filt}_mod

    Returns
    -------
    Saves catalog with corrected extinctions
    """

    if filters_Alambda_Av is None:
        filters_Alambda_Av = _Alambda_Av

    # Also apply correction to model predicted magnitudes
    if include_mod is True:
        filters = list(filters_Alambda_Av.keys())
        for filt in filters:
            filters_Alambda_Av[f"{filt}_mod"] = filters_Alambda_Av[filt]

    # Reading Catalog data
    cat = fits.open(catalog)
    cat_data = cat[1].data

    ##############
    # Obtaining AV
    AG = cat_data['GAIA_AG']

    Av = AG / filters_Alambda_Av['GAIA_G']

    ####################################
    # Correct extinction for each filter
    for filt in list(filters_Alambda_Av.keys()):
        if filt in cat_data.columns.names:

            Alambda = Av * filters_Alambda_Av[filt]

            nan_AG = AG > 100 # will removes nan values 1,000000E20

            not_nan = cat_data.columns[filt].array != 99
            not_nan = not_nan & ~nan_AG

            # If reverse, extinction is applied
            if reverse is True:
                cat_data.columns[filt].array[not_nan] += Alambda[not_nan]
            else:
                cat_data.columns[filt].array[not_nan] -= Alambda[not_nan]

            # Turn magnitudes that can't be corrected into 99
            cat_data.columns[filt].array[nan_AG] = 99

    # Save output data
    cat.writeto(save_file)
    print('Created file %s' % save_file)



def correct_extinction(catalog, save_file, correction,
                       filters_Alambda_Av=None, **kwargs):

    """
    General function to correct extinction using a specific map

    Parameters
    ----------
    catalog : str
        Location of the catalog which will have exctinction corrected
    save_file : str
        Location of file to save the results
    correction : str
        Which correction map should be applied: SCHLEIGEL, GORSKI
    filters_Alambda_Av : dict
        Dictionary with values of Alambda/Av

    Returns
    -------
    Saves catalog with corrected extinctions
    """

    if filters_Alambda_Av is None:
        filters_lambda = _Alambda_Av

    if correction.lower() == 'schlegel':
        correct_extinction_schlegel(catalog=catalog, save_file=save_file,
                                    filters_Alambda_Av=filters_Alambda_Av,
                                    **kwargs)

    elif correction.lower() == 'gorski':
        correct_extinction_gorski(catalog=catalog, save_file=save_file,
                                  filters_Alambda_Av=filters_Alambda_Av,
                                  **kwargs)

    elif correction.lower() == 'gaiadr2':
        correct_extinction_gaiadr2(catalog=catalog, save_file=save_file,
                                   filters_Alambda_Av=filters_Alambda_Av,
                                   **kwargs)

    else:
        raise ValueError(f"Extinction {correction} is not supported.")

################################################################################
# Calibration

# \todo ADD uncertainty estimation to the SED fitted zero-points


def zp_write(zp_dict, save_file, filters_list=None):
    """
    writes a .zp file

    Parameters
    ----------
    zp_dict : dict
        Dictionary of zero points (keys: filter name, value: filter zero-point)
    save_file : str
        Location to save the zp file
    filters_list : list
        List of filters to save zero-points. If None, all filters in zp_dict are
        saved

    Returns
    -------
    Saves a zp file
    """

    print('\nSaving results to file %s' % save_file)

    if filters_list is None:
        filters_list = zp_dict.keys()

    with open(save_file, 'w') as f:

        if type(filters_list) is str:
            f.write("{:s} {:.5f}\n".format(filters_list, zp_dict[filters_list]))

        else:
            for filt in filters_list:
                f.write("{:s} {:.5f}\n".format(filt, zp_dict[filt]))

    print('Results are saved in file %s' % save_file)


def zp_read(load_file, zp_col = 1):
    """
    Reads a .zp file
    Parameters
    ----------
    load_file : str
        Location of the .zp file
    zp_col : int
        Column where zero-point is saved

    Returns
    -------
    dict
        Dictionary of zero-points (keys: filter name, value: filter zero-point)
    """

    filters = np.genfromtxt(load_file, dtype=str, usecols=[0])
    ZPs = np.genfromtxt(load_file, dtype=float, usecols=[zp_col])

    zp_dict = {}

    try:
        for i in range(len(filters)):
            zp_dict[filters[i]] = ZPs[i]

    except TypeError:
        zp_dict[str(filters)] = float(ZPs)

    return zp_dict


def zp_add(zp_file_list, save_file, filters, inst_zp=None):
    """
    Adds the zero-points for the same filters in multiple .zp files

    Can also be used to combine multiple .zp files featuring different filters

    Parameters
    ----------
    zp_file_list : list
        List of .zp files to add
    save_file : str
        Location to save the resulting .zp file
    filters : list
        List of filters to add zps and save in the save_file
    inst_zp : float
        A zero-point value to be added for all filters. Default = None

    Returns
    -------
    Saves the resulting .zp file
    """

    zp_dict_sum = {}
    zp_dict_list = []

    for zp_file in zp_file_list:
        zp_dict_list.append(zp_read(zp_file))

    for filt in filters:
        zp_sum = 0
        for zp_dict in zp_dict_list:
            if filt in zp_dict.keys():
                zp_sum += zp_dict[filt]

        zp_dict_sum[filt] = zp_sum

        if inst_zp is not None:
            zp_dict_sum[filt] = zp_dict_sum[filt] + inst_zp

    zp_write(zp_dict=zp_dict_sum,
             save_file=save_file,
             filters_list=filters)


def calibration_suffix(conf):
    """
    Generates the suffix to apply to a given calibration configuration taking
    into account the photometry mode and the reference catalog(s) used for
    calibration

    Parameters
    ----------
    conf : dict
        Dictionary loaded from the configuration file

    Returns
    -------
    str
        Suffix to apply to calibration and catalogs for a given calibration
        configuration
    """

    if conf['data_release_name'] == 'iDR4_1':
        # Photometry mode
        suffix = f"{conf['calibration_photometry']}_"

        # Reference catalogs
        for i in range(len(conf['reference_catalog'])):
            if i != 0:
                suffix += '+'

            suffix += f"{conf['reference_catalog'][i]}"

        return suffix

    else:
        return conf['calibration_name']

def sed_fitting(models, catalog, save_file, ref_mag_cols,
                pred_mag_cols = None, bayesian = False, ebv_mode = False):
    """

    Parameters
    ----------
    models : str
        Location of the model's file with synthetic SEDs convolved to the
        pipeline supported filters
    catalog : str
        Location of the catalog with the filters data to fit the SEDs
    save_file : str
        Location of the desired save file where model predicted magnitudes will
        be saved
    ref_mag_cols : list
        List of magnitudes used to fit the SEDs
    pred_mag_cols : list
        List of magnitudes predicted by the fitted SEDs. If none, the code
        predicts magnitudes for ref_mag_cols only.
    bayesian : bool
        If True, model selection comes from maximization of posterior,
        otherwise, from minimization of chi2
    ebv_mode : bool
        If true, the mode data EB_V will be estimated and only models with this
        exctinction will be considered

    Returns
    -------
    Saves predicted magnitudes to the save_file location.
    """

    if ebv_mode:
        catalog_data = load_data(catalog)
        ebv_cut = mode(catalog_data['EB_V'])
    else:
        ebv_cut = None

    sf.get_model_mags(models_file   = models,
                      data_file     = catalog,
                      save_file     = save_file,
                      ref_mag_cols  = ref_mag_cols,
                      pred_mag_cols = pred_mag_cols,
                      bayesian      = bayesian,
                      ebv_cut       = ebv_cut)


def get_filter_zeropoint(obs_mag_array, model_mag_array, cut=(14,19)):
    """
    Estimate the zero point of a particular filter by comparing observed
    magnitudes and model predicted magnitudes.

    Parameters
    ----------
    obs_mag_array : np.array
        array of observed zero-points
    model_mag_array : np.array
        array of model predicted zero-points
    cut : list
        Interval [min,max] of magnitudes to be considered for the estimation
        of the zero-points

    Returns
    -------
    float
        The value of the zero-point
    """

    f = (model_mag_array >= cut[0]) & (model_mag_array <= cut[1])

    delta_array = model_mag_array[f] - obs_mag_array[f]

    delta_array = delta_array.values.reshape(-1, 1)

    kde_dens = KernelDensity(kernel='gaussian', bandwidth=0.05).fit(delta_array)

    # Transform to kde
    x = np.arange(-10, 10, 0.001)
    y = np.exp(kde_dens.score_samples(x.reshape(-1, 1)))

    # get mode
    mode = x[y == np.max(y)][0]

    return mode


def zp_estimate(catalog, save_file, filters_list, mag_cut=(14, 19)):
    """
    Obtain zero-points for a given catalog by comparing the observed and model
    predicted magnitudes in this catalog. Input catalog must be the output of
    sed_fitting.get_model_mags

    Parameters
    ----------
    catalog : str
        Location of the input catalog. Must be the output
        of sed_fitting.get_model_mags
    save_file : str
        Location to save the estimated zero-points
    filters_list : list
        List of filters to estimate the zero-points
    mag_cut : list
        Interval [min,max] of magnitudes to be considered for the estimation
        of the zero-points

    Returns
    -------
    Saves the zero-points in a .zp file
    """

    data = load_data(catalog)
    print("\n\nStarting to apply ZeroPoints\n\n")

    print("Obtaining zero point for magnitudes:")
    print(filters_list)

    print("Using {0} stars to estimate ZPs".format(data.shape[0]))

    # Estimating and applying ZP
    zp_dict = {}

    for filt in filters_list:
        print("\nEstimating ZP for mag {0}".format(filt))

        # Cut logg
        dwarfs = data.loc[:, 'logg'].values > 3

        obs_mag_array = data.loc[dwarfs, f"{filt}"]
        mod_mag_array = data.loc[dwarfs, f"{filt}_mod"]

        filt_zp = get_filter_zeropoint(obs_mag_array=obs_mag_array,
                                      model_mag_array=mod_mag_array,
                                      cut=mag_cut)

        zp_dict[filt] = filt_zp

        data.loc[:, f"{filt}"] = data.loc[:, f"{filt}"] + filt_zp

        print("{} ZP = {:.3f}".format(f"{filt}", filt_zp))

    # Saving data
    zp_write(zp_dict=zp_dict, save_file=save_file, filters_list=filters_list)


def zp_gaiascale(gaia_zp_file, save_file, filters_list):
    """
    Obtain gaiascale zero-points from the gaia zero points estimated comparing
    catalog and model predicted magnitudes.

    for each filter in filters_list:
    gaia_scale_zp = -mean(gaia_filter_zps)

    Parameters
    ----------
    gaia_zp_file : str
        zp file of gaia filters
    save_file : str
        Location to save the estimated gaia scale zero-points
    filters_list : list
        List of filters to estimate the zero-points

    Returns
    -------
    Saves the zero-points in a .zp file
    """

    gaia_zps = zp_read(gaia_zp_file)

    print("\n\nObtaining gaia scale ZPs\n\n")
    gaia_scale_zp = -np.mean(list(gaia_zps.values()))

    # Adding to the dictionary
    splus_zp_dict = {}

    for filt in filters_list:
        splus_zp_dict[filt] = gaia_scale_zp

        print("{} ZP = {:.3f}".format(f"{filt}", gaia_scale_zp))

    # Saving data
    zp_write(zp_dict=splus_zp_dict,
             save_file=save_file,
             filters_list=filters_list)

def zp_apply(catalog, save_file, zp_file, fmt = "ascii", zp_inst = None):
    """
    Applies the zero-points to the magnitudes catalog

    Parameters
    ----------
    catalog : str
        Location of the catalog
    save_file : str
        Location to save the catalog with zero-points applied
    zp_file : str
        Location to the .zp file with the zero-points
    fmt : str
        Output format
    zp_inst : float
        Constant zp to be added to all filters. Default = None

    Returns
    -------
    Saves new catalog with zero-points applied
    """

    ZPs = zp_read(zp_file)
    cat_data = load_data(catalog)

    # Apply Zero Points
    for filt in ZPs.keys():

        if zp_inst is None:
            zp_i = ZPs[filt]
        else:
            zp_i = ZPs[filt] + zp_inst

        no_nan = cat_data.loc[:, filt] != 99

        cat_data.loc[no_nan, filt] = cat_data.loc[no_nan, filt] + zp_i

    with open(catalog, 'r') as f:
        first_line = f.readline()

    if fmt == 'ascii':
        with open(save_file, 'w') as f:
            f.write(first_line)
            np.savetxt(f, cat_data, fmt='%.5f')

    elif fmt == 'fits':
        t = Table.from_pandas(cat_data)
        t.write(save_file)


def plot_zp_fitting(sed_fit_file, save_file, filt, mag_cut = (14, 19),
                    zp_file = None, label = 'mag_inst', color = "#2266ff"):

    """
    Makes a plot of the zero-point estimation process

    Parameters
    ----------
    sed_fit_file : str
        Location of the catalog with fitted and model-predicted magnitudes
    zp_file : str
        Location of the obtained zp file
    save_file : str
        Location to save the plot
    filt : str
        Name of the filter to plot
    mag_cut : list
        Limits of magnitudes [min,max] selected for zero-point estimation
    label : str
        Identify the step in the calibration process
    color : str
        Color of the points in the scatter plot and line of density plot

    Returns
    -------
    Saves the plot
    """

    ###########
    # Load data

    cat_data = load_data(sed_fit_file)

    # Remove 99
    data_selection = np.abs(cat_data.loc[:, filt] < 50)
    cat_data = cat_data[data_selection]

    ##############
    # Prepare data

    x = cat_data.loc[:, f'{filt}_mod']
    y = x - cat_data.loc[:, f'{filt}']

    dwarfs = cat_data.loc[:, 'logg'].values > 3
    selection = (x >= mag_cut[0]) & (x <= mag_cut[1]) & dwarfs

    ############################
    # Apply different estimators

    delta = y[selection]
    delta = delta.values.reshape(-1, 1)

    kde_dens = KernelDensity(kernel='gaussian', bandwidth=0.05).fit(delta)

    y_dens = np.arange(-10, 10, 0.001)
    x_dens = np.exp(kde_dens.score_samples(y_dens.reshape(-1, 1)))

    mode = y_dens[x_dens == np.max(x_dens)][0]

    mu = np.mean(y[selection])
    mu_robust = mean_robust(y[selection])

    ################
    # Make the plots

    fig = plt.figure(figsize=(8, 5))
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])

    ax1 = plt.subplot(gs[0])

    ax1.scatter(x[selection], y[selection],
                c=color, s=20, alpha=0.5, zorder=1)

    ax1.scatter(x[~selection], y[~selection],
                c=color, s=20, alpha=0.05, zorder=2)

    ax1.plot([mag_cut[0], mag_cut[1]], [mode, mode],
             color='#FF3219', linestyle='-', zorder=6)

    ####
    # Limits of the plot
    ####
    xlim = [mag_cut[0] - 2, mag_cut[1] + 4]
    ylim = [mode - 1.5, mode + 1.5]

    ax1.text(mag_cut[0] - 1.5, mode + 1.3, f"{filt}", fontsize=14)

    ax1.set_xlim(xlim)
    ax1.set_ylim(ylim)

    ax1.set_xlabel("mag_model")
    ax1.set_ylabel(f"mag_model - {label}")

    ###
    # Plot KDE distribution
    ###

    ax2 = plt.subplot(gs[1])

    ax2.plot(x_dens / np.max(x_dens), y_dens, zorder=3, color = color)

    if zp_file is not None:
        zp_data = zp_read(zp_file)
        zp = zp_data[filt]

        ax2.plot([0, 2], [zp, zp], color='#000000', linestyle='--',
                 zorder=3, label='zp: {:.4f}'.format(mode))

    ax2.plot([0, 2], [mode, mode], color='#FF3219', linestyle='-',
             zorder=2, label='mode: {:.4f}'.format(mode))

    ax2.plot([0, 2], [mu, mu], color='#1932FF', linestyle='--',
             zorder=1, label='mean: {:.4f}'.format(mu))

    ax2.plot([0, 2], [mu_robust, mu_robust], color='#19DD32', linestyle=':',
             zorder=1,
             label='mean_robust: {:.4f}'.format(mu_robust))

    ax2.set_xlim([0, 1.1])
    ax2.set_ylim(ylim)

    ax2.legend(fontsize=7)

    ax2.axes.get_xaxis().set_visible(False)
    ax2.axes.get_yaxis().set_visible(False)
    ax2.set_ylabel("Density")

    ############
    # Plot grids

    for i in np.arange(-10, 10, 0.5):

        ax1.plot([0, 30], [i, i],
                 color="#666666", alpha=0.3,
                 linewidth=0.5, zorder=-5)

        ax2.plot([0, 30], [i, i],
                 color="#666666", alpha=0.3,
                 linewidth=0.5, zorder=-5)

    for i in np.arange(-10, 10, 0.1):

        ax1.plot([0, 30], [i, i],
                 color="#666666", alpha=0.1,
                 linewidth=0.5, zorder=-5)

        ax2.plot([0, 30], [i, i],
                 color="#666666", alpha=0.1,
                 linewidth=0.5, zorder=-5)

    for i in np.arange(1, 30, 1):

        ax1.plot([i, i], [-10, 10],
                 color="#666666", linewidth=0.5,
                 alpha=0.1, zorder=-5)

    for i in np.arange(2, 30, 2):

        ax1.plot([i, i], [-10, 10],
                 color="#666666", linewidth=0.5,
                 alpha=0.3, zorder=-5)

    plt.subplots_adjust(top=0.98, left=0.1, right=0.98, wspace=0)

    plt.savefig(save_file)
    plt.clf()
    plt.close()


###########################
# Stellar Locus calibration

def zp_estimate_stlocus(catalog, save_file, stlocus_ref_cat,
                        filts_color_ref, filt_ref, filts_to_get_zp,
                        color_range, nbins, plot_path = None, field = None):

    """
    Applies the stellar locus technique to derive the zero-points of a list
    of filters yet to be calibrated.

    Parameters
    ----------
    catalog : str
        Location of the catalog with filter columns to be calibrated
    save_file : str
        Location of the .zp output file
    stlocus_ref_cat : str
        Location of the catalog used as the reference for the calibration
    filts_color_ref : list
        color filt1 - filt2 is calculated from the columns [filt1, filt2]
    filt_ref : str
        filter that completes the color in the y axis
    filts_to_get_zp : list
        List of filters to obtain zp using the stellar locus technique
    color_range : list
        x-axis color range considered in the zp fitting [min, max]
    nbins : int
        Number of bins to divide the color_range interval
    plot_path : str
        Location of the directory to save plots (can be None)
    field : str
        Name of the field (used only for the plots file names)

    Returns
    -------
    Saves a .zp file with the zero points and, optionally, saves plots of the
    process
    """

    # Load Reference and data
    reference = load_data(stlocus_ref_cat)
    cat_data = load_data(catalog)

    # define x axis => color = filt_x0 - filt_x1
    filt_x0 = filts_color_ref[0]
    filt_x1 = filts_color_ref[1]

    # Calculate colors from reference and from catalog to calibrate
    reference_x = reference.loc[:, filt_x0] - reference.loc[:, filt_x1]
    cat_data_x  = cat_data.loc[:, filt_x0] - cat_data.loc[:, filt_x1]

    zp_dict = {}

    bins = np.linspace(color_range[0], color_range[1], nbins)
    delta_bin = bins[1] - bins[0]

    # Obtain zero points
    for filt in filts_to_get_zp:
        print(f"Estimating ZP for filter {filt} using the stellar locus")

        delta_mag = []

        ####
        reference_bin_y_list = []
        data_bin_y_list = []
        ####

        # Remove mag = 99 or -99
        remove_bad_data = (cat_data.loc[:, filt].values != -99) & \
                          (cat_data.loc[:, filt].values != 99) & \
                          (cat_data.loc[:, filt_ref].values != -99) & \
                          (cat_data.loc[:, filt_ref].values != 99) & \
                          (cat_data.loc[:, filt_x0].values != -99) & \
                          (cat_data.loc[:, filt_x0].values != 99) & \
                          (cat_data.loc[:, filt_x1].values != -99) & \
                          (cat_data.loc[:, filt_x1].values != 99)

        for bin_i in bins[:-1]:

            reference_bin_cut = (reference_x >= bin_i) & \
                                (reference_x < bin_i + delta_bin)

            data_bin_cut = (cat_data_x >= bin_i) & \
                           (cat_data_x < bin_i + delta_bin) & \
                           remove_bad_data

            reference_bin_y = reference.loc[reference_bin_cut, filt] - \
                              reference.loc[reference_bin_cut, filt_ref]

            data_bin_y = cat_data.loc[data_bin_cut, filt] - \
                         cat_data.loc[data_bin_cut, filt_ref]

            mean_reference_bin_y = mean_robust(reference_bin_y)

            cut_outliers = (data_bin_y > -5) & (data_bin_y < 5)
            mean_data_bin_y = mean_robust(data_bin_y[cut_outliers], 0.5, 0.5)

            delta_mag.append(mean_reference_bin_y - mean_data_bin_y)

            ####
            reference_bin_y_list.append(mean_reference_bin_y)
            data_bin_y_list.append(mean_data_bin_y)
            ####

        # Calculate ZP
        delta_mag = np.array(delta_mag)

        reference_bin_y_list = np.array(reference_bin_y_list)
        data_bin_y_list = np.array(data_bin_y_list)

        # Get order to remove max and min values
        o = np.argsort(delta_mag)

        zp_dict[filt] = mean_robust(delta_mag[o][1:-1])
        print(f"{filt} ZP = {zp_dict[filt]:.3f}")

        #######
        save_fig_name = f"{field}_{filt}_stlocus.png"
        save_fig_file = os.path.join(plot_path, save_fig_name)

        if (plot_path is not None) and (not os.path.exists(save_fig_file)):

            x = np.array(bins[:-1]) + delta_bin/2

            plt.scatter(reference_x,
                        reference.loc[:, filt] - reference.loc[:, filt_ref],
                        zorder = 1, alpha = 0.02, color = "#444444")

            plt.scatter(x[o][1:-1], reference_bin_y_list[o][1:-1],
                        s = 100, c = "#000000", zorder = 3)

            plt.scatter(x[o][0], reference_bin_y_list[o][0],
                        s = 100, c = "#000000", marker = 'x', zorder = 3)

            plt.scatter(x[o][-1], reference_bin_y_list[o][-1],
                        s = 100, c = "#000000", marker = 'x', zorder = 3)

            plt.plot(x, reference_bin_y_list, color = "#000000", zorder = 4)

            x_data = cat_data_x[remove_bad_data]
            y_data = cat_data.loc[remove_bad_data, filt] - \
                     cat_data.loc[remove_bad_data, filt_ref]

            plt.scatter(x_data, y_data, c = "#AA8800", zorder=2, alpha=0.2)

            plt.scatter(x[o][1:-1], data_bin_y_list[o][1:-1],
                        s = 100, c = "#664400", zorder = 5)

            plt.scatter(x[o][0], data_bin_y_list[o][0],
                        s = 100, c = "#000000", marker = 'x', zorder = 5)

            plt.scatter(x[o][-1], data_bin_y_list[o][-1],
                        s = 100, c = "#000000", marker = 'x', zorder = 5)

            plt.plot(x, data_bin_y_list, color = "#664400", zorder = 6)

            ymax = np.nanmax((np.max(reference_bin_y_list),
                          np.max(data_bin_y_list))) + 1
            ymin = np.nanmin((np.min(reference_bin_y_list),
                          np.min(data_bin_y_list))) - 1

            plt.gca().set_xlabel(f"{filt_x0} - {filt_x1}")
            plt.gca().set_ylabel(f"{filt} - {filt_ref}")
            plt.gca().set_ylim((ymin, ymax))
            plt.gca().set_xlim(color_range)
            plt.savefig(save_fig_file)
            plt.clf()
            plt.close()
            #######

    # Write zero-points to .zp file
    zp_write(zp_dict=zp_dict,
             save_file=save_file,
             filters_list=filts_to_get_zp)


def zp_comparison(fields_zps, save_file, fields_list):
    """
    Creates a comparison file between two zero points calibrations for a list
    of fields

    Parameters
    ----------
    fields_zps : dict
        Dictionary formated as fields_zps[*field*] = [zp_file1, zp_file2],
        where zp_file corresponds to the .zp file of each calibration to
        compare
    fields_list : list
        List of filters. If None the list is taking from fields_zps.keys(),
        although in this case the order of the fields will be randomized
    save_file : str
        Location to save the resulting comparison file

    Returns
    -------
    Saves a .cat table with zero points from both calibrations and their
    differences
    """

    #########################################
    # Get list of filters from first .zp file
    field0   = list(fields_zps.keys())[0]
    zp_file0 = fields_zps[field0][0]

    filters = np.genfromtxt(zp_file0, dtype=str, usecols=[0])

    ##############################
    # Create comparison data frame
    if fields_list is None:
        fields = fields_zps.keys()
    else:
        fields = fields_list

    zp_data = pd.DataFrame()

    zp_data['field'] = fields
    for filt in filters:
        zp_data[f'zp_{filt}_1'] = np.full(len(fields), np.nan)
        zp_data[f'zp_{filt}_2'] = np.full(len(fields), np.nan)
        zp_data[f'zp_{filt}_diff'] = np.full(len(fields), np.nan)

    ############################
    # Fill comparison data frame
    for i in range(len(fields)):

        field = fields[i]
        try:
            zp1 = zp_read(fields_zps[field][0])
        except OSError:
            zp1 = None

        try:
            zp2 = zp_read(fields_zps[field][1])
        except OSError:
            zp2 = None

        for filt in filters:

            try:
                zp_data.loc[i, f'zp_{filt}_1'] = zp1[filt]
            except KeyError:
                pass
            except TypeError:
                pass

            try:
                zp_data.loc[i, f'zp_{filt}_2'] = zp2[filt]
            except KeyError:
                pass
            except TypeError:
                pass

            try:
                diff = zp1[filt] - zp2[filt]
                zp_data.loc[i, f'zp_{filt}_diff'] = np.around(diff, 5)
            except KeyError:
                pass
            except TypeError:
                pass

    #################
    # Save data frame
    with open(save_file, 'w') as f:
        f.write("# ")
        zp_data.to_csv(f, index = False, sep = ",")


def zp_fit_offsets(zp_comparison_file, save_file, filters):
    """
    fit offsets between the zero-points obtained from two different calibrations

    Parameters
    ----------
    zp_comparison_file : str
        Location of the .cat zero-point comparison catalog
        (output of func:zp_comparison)

    save_file : str
        Location to save offset zp file

    filters : list
        List of filters to estimate offsets

    Returns
    -------
    Saves .zp file with the offsets to be applied
    """

    offsets = {}
    zp_diff = pd.read_csv(zp_comparison_file, escapechar='#',
                               skipinitialspace=True)

    for filt in filters:
        diff_array = np.array(zp_diff[f'zp_{filt}_diff'])
        diff_array = diff_array[~np.isnan(diff_array)]
        diff_array = diff_array.reshape(-1, 1)

        kde_dens = KernelDensity(kernel='gaussian', bandwidth=0.05)
        kde_dens = kde_dens.fit(diff_array)

        # Transform to kde
        x = np.arange(-1, 1, 0.001)
        y = np.exp(kde_dens.score_samples(x.reshape(-1, 1)))

        # get mode
        mode = x[y == np.max(y)][0]

        offsets[filt] = mode

    zp_write(zp_dict=offsets,
             save_file=save_file,
             filters_list=filters)


################################################################################
# Catalog preparation

def sexcatalog_apply_calibration(catalog_file, zp_file, save_file,
                                 filter_name, field, sex_mag_zp,
                                 calibration_flag, mode = 'dual',
                                 calibration_name=None,
                                 drname='NoDRname',
                                 extinction_maps_path=None,
                                 extinction_correction=None):
    """

    Parameters
    ----------
    catalog_file
    zp_file
    save_file
    filter_name
    apertures
    other_columns

    Returns
    -------

    """

    # Load photometry catalog (with aperture correction)
    phot_cat = fits.open(catalog_file)
    phot_cat = phot_cat[1].data

    N_sources = len(phot_cat)

    # Load ZP
    ZPs = zp_read(zp_file)
    ZP = ZPs[f'SPLUS_{filter_name}']

    # Standard filter name
    filt_standard = translate_filter_standard(filter_name)

    # Create new data Table
    cat = []

    # Fill new data Table ######################################################

    # Field column
    cat.append(fits.Column(name='Field',
                           format='%dA' % len(field),
                           array=N_sources*[field]))

    # FIELD ID
    phot_cat.columns[f'FIELD_ID'].name = f'ID'
    cat.append(phot_cat.columns[f'ID'])
    phot_cat.columns[f'FIELD_ID_RA'].name = f'ID_RA'
    cat.append(phot_cat.columns[f'ID_RA'])
    phot_cat.columns[f'FIELD_ID_DEC'].name = f'ID_DEC'
    cat.append(phot_cat.columns[f'ID_DEC'])

    # Filter ID
    if mode == "single":
        cat.append(phot_cat.columns[f'PHOT_ID_single'])
        cat.append(phot_cat.columns[f'PHOT_ID_RA_single'])
        cat.append(phot_cat.columns[f'PHOT_ID_DEC_single'])
        cat.append(phot_cat.columns[f'{filt_standard}_ID_single'])

        # RA, DEC
        phot_cat.columns[f'RA_{filt_standard}'].name = f'RA_{filt_standard}'
        cat.append(phot_cat.columns[f'RA_{filt_standard}'])
        phot_cat.columns[f'DEC_{filt_standard}'].name = f'DEC_{filt_standard}'
        cat.append(phot_cat.columns[f'DEC_{filt_standard}'])


    # Filter ID dual (have to generate)
    elif mode == "dual":
        cat.append(phot_cat.columns[f'PHOT_ID_dual'])
        cat.append(phot_cat.columns[f'PHOT_ID_RA_dual'])
        cat.append(phot_cat.columns[f'PHOT_ID_DEC_dual'])

        cat.append(fits.Column(name=f'{filt_standard}_ID_dual',
                               format='50A',
                               array=phot_cat.columns[f'PHOT_ID_dual'].array))

        # RA,DEC
        phot_cat.columns['ALPHA_J2000'].name = 'RA'
        cat.append(phot_cat.columns['RA'])
        phot_cat.columns['DELTA_J2000'].name = 'DEC'
        cat.append(phot_cat.columns['DEC'])

    # SEX_NUMBER
    phot_cat.columns['NUMBER'].name = f'SEX_NUMBER_{filt_standard}'
    cat.append(phot_cat.columns[f'SEX_NUMBER_{filt_standard}'])

    # SEX_FLAG
    phot_cat.columns['FLAGS'].name = f'SEX_FLAGS_{filt_standard}'
    cat.append(phot_cat.columns[f'SEX_FLAGS_{filt_standard}'])

    # CALIB_FLAG
    #cat.append(fits.Column(name='calib_flag',
    #                       format='1J',
    #                       array=N_sources*[calibration_flag]))

    # CALIB STRATEGY
    if calibration_name is not None:
        N_str = len(calibration_name)
        cat.append(fits.Column(name=f"calib_strat",
                               format=f'{N_str}A',
                               array=[calibration_name] * N_sources))

    if mode == 'single':

        # X, Y
        phot_cat.columns['X_IMAGE'].name = f'X_{filt_standard}'
        cat.append(phot_cat.columns[f'X_{filt_standard}'])

        phot_cat.columns['Y_IMAGE'].name = f'Y_{filt_standard}'
        cat.append(phot_cat.columns[f'Y_{filt_standard}'])

        # A, B, THETA
        phot_cat.columns['A_WORLD'].name = f'A_{filt_standard}'
        cat.append(phot_cat.columns[f'A_{filt_standard}'])

        phot_cat.columns['B_WORLD'].name = f'B_{filt_standard}'
        cat.append(phot_cat.columns[f'B_{filt_standard}'])

        phot_cat.columns['THETA_WORLD'].name = f'THETA_{filt_standard}'
        cat.append(phot_cat.columns[f'THETA_{filt_standard}'])

        # Elongation, Ellipticity
        phot_cat.columns['ELONGATION'].name = f'ELONGATION_{filt_standard}'
        cat.append(phot_cat.columns[f'ELONGATION_{filt_standard}'])
        phot_cat.columns['ELLIPTICITY'].name = f'ELLIPTICITY_{filt_standard}'
        cat.append(phot_cat.columns[f'ELLIPTICITY_{filt_standard}'])

        # ISOarea
        phot_cat.columns['ISOAREA_WORLD'].name = f'ISOarea_{filt_standard}'
        cat.append(phot_cat.columns[f'ISOarea_{filt_standard}'])

        # KRON/PETROSIAN/FLUX Radius
        phot_cat.columns['KRON_RADIUS'].name = f'KRON_RADIUS_{filt_standard}'
        cat.append(phot_cat.columns[f'KRON_RADIUS_{filt_standard}'])

        phot_cat.columns['PETRO_RADIUS'].name = f'PETRO_RADIUS_{filt_standard}'
        cat.append(phot_cat.columns[f'PETRO_RADIUS_{filt_standard}'])

        # Add FLUX_RADIUS
        for j, r in zip(range(4), [20, 50, 70, 90]):
            cat.append(fits.Column(name=f'FLUX_RADIUS_{r}_{filt_standard}',
                                   format='1E',
                        array=phot_cat.columns['FLUX_RADIUS'].array[:, j]))

        # CLASS_STAR
        phot_cat.columns['CLASS_STAR'].name = f'CLASS_STAR_{filt_standard}'
        cat.append(phot_cat.columns[f'CLASS_STAR_{filt_standard}'])

    # FWHM
    phot_cat.columns['FWHM_WORLD'].name = f'FWHM_{filt_standard}'
    cat.append(phot_cat.columns[f'FWHM_{filt_standard}'])

    ### Normalized FWHM
    col_s2n_auto = phot_cat['FLUX_AUTO'] / phot_cat['FLUXERR_AUTO']
    col_s2n_auto = np.where(col_s2n_auto > 0., col_s2n_auto, -1.00)

    if mode == "single":
        col_class_star = phot_cat[f'CLASS_STAR_{filt_standard}']
    elif mode == "dual":
        col_class_star = phot_cat[f'CLASS_STAR']

    selection = (col_s2n_auto >= 100) & (col_s2n_auto <= 1000) & (col_class_star > 0.9)
    mean_FWHM = mean_robust(phot_cat[f'FWHM_{filt_standard}'][selection])

    col_FWHM_n = phot_cat[f'FWHM_{filt_standard}'] / mean_FWHM

    cat.append(fits.Column(name=f'FWHM_n_{filt_standard}',
                           format='1E',
                           array=col_FWHM_n))

    # MU_MAX, MU_THRESHOLD, BACKGROUND, THRESHOLD
    MU_MAX = phot_cat.columns['MU_MAX'].array - sex_mag_zp + ZP
    cat.append(fits.Column(name=f'MU_MAX_{filt_standard}',
                           format='1E',
                           array=MU_MAX))

    MU_THRESHOLD = phot_cat.columns['MU_THRESHOLD'].array - sex_mag_zp + ZP
    cat.append(fits.Column(name=f'MU_THRESHOLD_{filt_standard}',
                           format='1E',
                           array=MU_THRESHOLD))

    BACKGROUND = phot_cat.columns['BACKGROUND'].array
    cat.append(fits.Column(name=f'BACKGROUND_{filt_standard}',
                           format='1E',
                           array=BACKGROUND))

    THRESHOLD = phot_cat.columns['THRESHOLD'].array
    cat.append(fits.Column(name=f'THRESHOLD_{filt_standard}',
                           format='1E',
                           array=THRESHOLD))

    # FLUXES and MAGNITUDES for different apertures

    apertures = ['AUTO', 'PETRO', 'ISO']
    for aper in apertures:

        fmt = '1E'

        f = phot_cat.columns[f'MAG_{aper}'].array != 99

        # FLUX
        FLUX     = phot_cat.columns[f'FLUX_{aper}'].array
        e_FLUX     = phot_cat.columns[f'FLUXERR_{aper}'].array

        # Signal to noise
        s2n = FLUX/e_FLUX

        # AB magnitude
        mag     = phot_cat.columns[f'MAG_{aper}'].array
        mag[f] += ZP - sex_mag_zp

        e_mag = phot_cat.columns[f'MAGERR_{aper}'].array

        cat.append(fits.Column(name=f'{filt_standard}_{aper.lower()}',
                               format=fmt,
                               array=mag))

        cat.append(fits.Column(name=f'e_{filt_standard}_{aper.lower()}',
                               format=fmt,
                               array=e_mag))

        cat.append(fits.Column(name=f's2n_{filt_standard}_{aper.lower()}',
                               format=fmt,
                               array=s2n))

    # Including APER_3
    f = phot_cat.columns[f'MAG_APER'].array[:,2] != 99

    FLUX = phot_cat.columns[f'FLUX_APER'].array[:,2]
    e_FLUX = phot_cat.columns[f'FLUXERR_APER'].array[:, 2]

    s2n_aper_3 = FLUX / e_FLUX

    mag = phot_cat.columns[f'MAG_APER'].array[:, 2]
    mag[f] += ZP - sex_mag_zp

    e_mag = phot_cat.columns[f'MAGERR_APER'].array[:, 2]

    cat.append(fits.Column(name=f'{filt_standard}_aper_3',
                           format=fmt,
                           array=mag))

    cat.append(fits.Column(name=f'e_{filt_standard}_aper_3',
                           format=fmt,
                           array=e_mag))

    cat.append(fits.Column(name=f's2n_{filt_standard}_aper_3',
                           format=fmt,
                           array=s2n_aper_3))

    # Including APER_6
    f = phot_cat.columns[f'MAG_APER'].array[:, 4] != 99

    FLUX = phot_cat.columns[f'FLUX_APER'].array[:, 4]
    e_FLUX = phot_cat.columns[f'FLUXERR_APER'].array[:, 4]

    s2n_aper_6 = FLUX / e_FLUX

    mag = phot_cat.columns[f'MAG_APER'].array[:, 4]
    mag[f] += ZP - sex_mag_zp

    e_mag = phot_cat.columns[f'MAGERR_APER'].array[:, 4]

    cat.append(fits.Column(name=f'{filt_standard}_aper_6',
                           format=fmt,
                           array=mag))

    cat.append(fits.Column(name=f'e_{filt_standard}_aper_6',
                           format=fmt,
                           array=e_mag))

    cat.append(fits.Column(name=f's2n_{filt_standard}_aper_6',
                           format=fmt,
                           array=s2n_aper_6))

    # PStotal fluxes and magnitudes
    # mag
    mag = phot_cat.columns[f'MAG_PStotal'].array
    f = mag != 99

    mag[f] += ZP - sex_mag_zp

    e_mag = phot_cat.columns[f'MAGERR_APER'].array[:,2]

    cat.append(fits.Column(name=f'{filt_standard}_PStotal',
                           format='1E',
                           array=mag))

    cat.append(fits.Column(name=f'e_{filt_standard}_PStotal',
                           format='1E',
                           array=e_mag))

    # S2N
    s2n = np.full(len(mag), -1.)
    s2n[f] = s2n_aper_3[f]

    cat.append(fits.Column(name=f's2n_{filt_standard}_PStotal',
                           format='1E',
                           array=s2n))

    if extinction_maps_path is not None:
        if extinction_correction.lower() == 'schlegel':

            RA = phot_cat.columns[f'RA_{filt_standard}'].array
            DEC = phot_cat.columns[f'DEC_{filt_standard}'].array

            EBV = get_EBV_schlegel(RA  = RA,
                                   DEC = DEC,
                                   ebv_maps_path = extinction_maps_path)

            cat.append(fits.Column(name=f'EBV_SCH',
                                   format='1E',
                                   array=EBV))

    # Generate HDU from columns
    hdu = fits.BinTableHDU.from_columns(cat)

    # Save HDU
    hdu.writeto(save_file)


def sexcatalog_detection(detection_file, save_file, field,
                         calibration_flag, extinction_maps_path=None,
                         extinction_correction=None,
                         calibration_name=None):
    """

    Parameters
    ----------
    catalog_file
    zp_file
    save_file
    filter_name
    apertures
    other_columns

    Returns
    -------

    """

    # Load photometry catalog (with aperture correction)
    det_cat = fits.open(detection_file)
    det_cat = det_cat[1].data

    N_sources = len(det_cat)

    # Create new data Table
    cat = []

    # Fill new data Table ######################################################

    # Field column
    cat.append(fits.Column(name='Field',
                           format='%dA' % len(field),
                           array=N_sources * [field]))

    # FIELD ID
    det_cat.columns[f'FIELD_ID'].name = f'ID'
    cat.append(det_cat.columns[f'ID'])
    det_cat.columns[f'FIELD_ID_RA'].name = f'ID_RA'
    cat.append(det_cat.columns[f'ID_RA'])
    det_cat.columns[f'FIELD_ID_DEC'].name = f'ID_DEC'
    cat.append(det_cat.columns[f'ID_DEC'])

    # Add PHOT IDs
    cat.append(det_cat.columns[f'PHOT_ID_dual'])
    cat.append(det_cat.columns[f'PHOT_ID_RA_dual'])
    cat.append(det_cat.columns[f'PHOT_ID_DEC_dual'])

    cat.append(fits.Column(name=f'DET_ID_dual',
                           format='50A',
                           array=det_cat.columns[f'PHOT_ID_dual'].array))

    # RA,DEC
    det_cat.columns['ALPHA_J2000'].name = 'RA'
    cat.append(det_cat.columns['RA'])
    det_cat.columns['DELTA_J2000'].name = 'DEC'
    cat.append(det_cat.columns['DEC'])

    # SEX_NUMBER
    det_cat.columns['NUMBER'].name = f'SEX_NUMBER_DET'
    cat.append(det_cat.columns[f'SEX_NUMBER_DET'])

    # SEX_FLAG
    det_cat.columns['FLAGS'].name = f'SEX_FLAGS_DET'
    cat.append(det_cat.columns[f'SEX_FLAGS_DET'])

    # CALIB_FLAG
    #cat.append(fits.Column(name='calib_flag',
    #                       format='1J',
    #                       array=N_sources * [calibration_flag]))

    # CALIB STRATEGY
    if calibration_name is not None:
        N_str = len(calibration_name)
        cat.append(fits.Column(name=f"calib_strat",
                               format=f'{N_str}A',
                               array=[calibration_name] * N_sources))

    # X, Y
    det_cat.columns['X_IMAGE'].name = 'X'
    cat.append(det_cat.columns['X'])

    det_cat.columns['Y_IMAGE'].name = 'Y'
    cat.append(det_cat.columns['Y'])

    # A, B, THETA
    det_cat.columns['A_WORLD'].name = 'A'
    cat.append(det_cat.columns['A'])

    det_cat.columns['B_WORLD'].name = 'B'
    cat.append(det_cat.columns['B'])

    det_cat.columns['THETA_WORLD'].name = 'THETA'
    cat.append(det_cat.columns['THETA'])

    # Elongation, Ellipticity
    cat.append(det_cat.columns['ELONGATION'])
    cat.append(det_cat.columns['ELLIPTICITY'])

    # ISOarea
    det_cat.columns['ISOAREA_WORLD'].name = 'ISOarea'
    cat.append(det_cat.columns['ISOarea'])

    # KRON/PETROSIAN/FLUX Radius
    det_cat.columns['KRON_RADIUS'].name = 'KRON_RADIUS'
    cat.append(det_cat.columns['KRON_RADIUS'])

    det_cat.columns['PETRO_RADIUS'].name = 'PETRO_RADIUS'
    cat.append(det_cat.columns['PETRO_RADIUS'])

    # Add FLUX_RADIUS
    for j, r in zip(range(4), [20, 50, 70, 90]):
        cat.append(fits.Column(name=f'FLUX_RADIUS_{r}',
                               format='1E',
                               array=det_cat.columns['FLUX_RADIUS'].array[:, j]))

    # CLASS_STAR
    det_cat.columns['CLASS_STAR'].name = 'CLASS_STAR'
    cat.append(det_cat.columns['CLASS_STAR'])

    # FWHM
    det_cat.columns['FWHM_WORLD'].name = 'FWHM'
    cat.append(det_cat.columns['FWHM'])

    ### Normalized FWHM
    col_s2n_Det_auto = det_cat['FLUX_AUTO'] / det_cat['FLUXERR_AUTO']
    col_s2n_Det_auto = np.where(col_s2n_Det_auto > 0., col_s2n_Det_auto, -1.00)

    selection = (col_s2n_Det_auto >= 100) & (col_s2n_Det_auto <= 1000) & (det_cat['CLASS_STAR'] > 0.9)
    mean_FWHM = mean_robust(det_cat['FWHM'][selection])

    col_FWHM_n = det_cat['FWHM'] / mean_FWHM

    cat.append(fits.Column(name='FWHM_n',
                           format='1E',
                           array=col_FWHM_n))

    # MU_MAX, MU_THRESHOLD, BACKGROUND, THRESHOLD
    MU_MAX = det_cat.columns['MU_MAX'].array
    cat.append(fits.Column(name=f'MU_MAX_INST',
                           format='1E',
                           array=MU_MAX))

    MU_MAX = det_cat.columns['MU_THRESHOLD'].array
    cat.append(fits.Column(name=f'MU_THRESHOLD_INST',
                           format='1E',
                           array=MU_MAX))

    cat.append(det_cat.columns['BACKGROUND'])
    cat.append(det_cat.columns['THRESHOLD'])

    ### S2N_AUTO
    col_s2n_Det_auto = det_cat['FLUX_AUTO'] / det_cat['FLUXERR_AUTO']
    col_s2n_Det_auto = np.where(col_s2n_Det_auto > 0., col_s2n_Det_auto, -1.00)

    cat.append(fits.Column(name='s2n_DET_auto',
                           format='1E',
                           array=col_s2n_Det_auto))

    ### S2N_PETRO
    col_s2n_Det_petro = det_cat['FLUX_PETRO'] / det_cat['FLUXERR_PETRO']
    col_s2n_Det_petro = np.where(col_s2n_Det_petro > 0., col_s2n_Det_petro, -1.00)

    cat.append(fits.Column(name='s2n_DET_petro',
                           format='1E',
                           array=col_s2n_Det_petro))

    ### S2N_ISO
    col_s2n_Det_iso = det_cat['FLUX_ISO'] / det_cat['FLUXERR_ISO']
    col_s2n_Det_iso = np.where(col_s2n_Det_iso > 0., col_s2n_Det_iso, -1.00)

    cat.append(fits.Column(name='s2n_DET_iso',
                           format='1E',
                           array=col_s2n_Det_iso))

    ### FIXED APERTURES
    col_s2n_aper_3 = det_cat.columns['FLUX_APER'].array[:, 2] / det_cat.columns['FLUXERR_APER'].array[:, 2]
    col_s2n_aper_3 = np.where(col_s2n_aper_3 > 0., col_s2n_aper_3, -1.00)

    cat.append(fits.Column(name='s2n_DET_aper_3',
                           format='1E',
                           array=col_s2n_aper_3))

    col_s2n_aper_6 = det_cat.columns['FLUX_APER'].array[:, 4] / det_cat.columns['FLUXERR_APER'].array[:, 4]
    col_s2n_aper_6 = np.where(col_s2n_aper_6 > 0., col_s2n_aper_6, -1.00)

    cat.append(fits.Column(name='s2n_DET_aper_6',
                           format='1E',
                           array=col_s2n_aper_6))

    cat.append(fits.Column(name='s2n_DET_PStotal',
                           format='1E',
                           array=col_s2n_aper_3))

    if extinction_maps_path is not None:
        if extinction_correction.lower() == 'schlegel':

            RA = det_cat.columns[f'RA'].array
            DEC = det_cat.columns[f'DEC'].array

            EBV = get_EBV_schlegel(RA  = RA,
                                   DEC = DEC,
                                   ebv_maps_path = extinction_maps_path)

            cat.append(fits.Column(name=f'EBV_SCH',
                                   format='1E',
                                   array=EBV))

    # Generate HDU from columns
    hdu = fits.BinTableHDU.from_columns(cat)

    # Save HDU
    hdu.writeto(save_file)



def psfcatalog_apply_calibration(catalog_file, zp_file,
                                 save_file, filter_name, field, inst_mag_zp,
                                 calibration_flag, extinction_maps_path=None,
                                 extinction_correction=None,
                                 calibration_name=None):
    """

    Parameters
    ----------
    catalog_file
    zp_file
    save_file
    filter_name
    apertures
    other_columns

    Returns
    -------

    """

    # Load filter catalogue
    cat_data = pd.read_csv(catalog_file)

    N_sources = len(cat_data)

    # Load ZP
    ZPs = zp_read(zp_file)
    ZP = ZPs[f'SPLUS_{filter_name}']

    # Standard filter name
    filt_standard = translate_filter_standard(filter_name)

    # Create new data Table
    cat = []

    # Fill new data Table ######################################################

    # Field column
    cat.append(fits.Column(name='Field',
                           format='%dA' % len(field),
                           array=N_sources * [field]))

    # Field ID
    try:
        N_str = len(cat_data.loc[:, f'FIELD_ID'].values[0])
    except TypeError:
        N_str = 50

    cat.append(fits.Column(name=f'ID',
                           format=f'{N_str:d}A',
                           array=cat_data.loc[:, f'FIELD_ID'].values))

    cat.append(fits.Column(name=f'ID_RA',
                           format=f'1E',
                           array=cat_data.loc[:, f'FIELD_ID_RA'].values))

    cat.append(fits.Column(name=f'ID_DEC',
                           format=f'1E',
                           array=cat_data.loc[:, f'FIELD_ID_DEC'].values))

    # Add PHOT IDs
    N_str = len(cat_data.loc[:, f'PHOT_ID_psf'].values[0])

    cat.append(fits.Column(name=f'PHOT_ID_psf',
                           format=f'{N_str:d}A',
                           array=cat_data.loc[:, f'PHOT_ID_psf'].values))

    cat.append(fits.Column(name=f'PHOT_ID_RA_psf',
                           format=f'1E',
                           array=cat_data.loc[:, f'PHOT_ID_RA_psf'].values))

    cat.append(fits.Column(name=f'PHOT_ID_DEC_psf',
                           format=f'1E',
                           array=cat_data.loc[:, f'PHOT_ID_DEC_psf'].values))

    # Filter ID
    N_str = len(cat_data.loc[:, f'{filt_standard}_ID_psf'].values[0])
    array = cat_data.loc[:, f'{filt_standard}_ID_psf'].values
    cat.append(fits.Column(name=f'{filt_standard}_ID_psf',
                           format=f'{N_str:d}A',
                           array=array))

    cat.append(fits.Column(name=f'RA_{filt_standard}',
                           format='1E',
                           array=cat_data.loc[:, f'RA_{filt_standard}'].values))

    cat.append(fits.Column(name=f'DEC_{filt_standard}',
                           format='1E',
                           array=cat_data.loc[:, f'DEC_{filt_standard}'].values))

    # Star_number
    dophot_filter_number = cat_data.loc[:, 'Star_number'].values
    cat.append(fits.Column(name=f'DoPHOT_Star_number_{filt_standard}',
                           format='1J',
                           array=dophot_filter_number))


    # CALIB_FLAG
    #cat.append(fits.Column(name='calib_flag',
    #                       format='1J',
    #                       array=N_sources * [calibration_flag]))

    # CALIB STRATEGY
    if calibration_name is not None:
        N_str = len(calibration_name)
        cat.append(fits.Column(name=f"calib_strat",
                               format=f'{N_str}A',
                               array=[calibration_name] * N_sources))

    # RA, DEC, X, Y
    cat.append(fits.Column(name=f'X_{filt_standard}',
                           format='1E',
                           array=cat_data.loc[:, 'xpos'].values))

    cat.append(fits.Column(name=f'Y_{filt_standard}',
                           format='1E',
                           array=cat_data.loc[:, 'ypos'].values))

    # DoPHOT parameters
    #cat.append(fits.Column(name=f'DoPHOT_fitsky_{filt_standard}',
    #                       format='1E',
    #                       array=cat_data.loc[:, 'fitsky'].values))

    #cat.append(fits.Column(name=f'DoPHOT_objtype_{filt_standard}',
    #                       format='1J',
    #                       array=cat_data.loc[:, 'objtype'].values))

    #cat.append(fits.Column(name=f'DoPHOT_chi_{filt_standard}',
    #                       format='1E',
    #                       array=cat_data.loc[:, 'chi'].values))

    #cat.append(fits.Column(name=f'DoPHOT_apcorr_{filt_standard}',
    #                       format='1E',
    #                       array=cat_data.loc[:, 'apcorr'].values))

    # CLASS_STAR
    cat.append(fits.Column(name=f'CLASS_STAR_{filt_standard}',
                           format='1J',
                           array=cat_data.loc[:, 'FLAG_STAR'].values))

    # Magnitudes and fluxes
    fitmag = cat_data.loc[:, 'fitmag'].values
    err_fitmag = cat_data.loc[:, 'err_fitmag'].values

    mag   = fitmag + ZP - inst_mag_zp
    e_mag = err_fitmag

    flux = 10**((-mag-48.6)/2.5)
    e_flux = (flux*e_mag)/1.083

    s2n = flux/e_flux

    cat.append(fits.Column(name=f'{filt_standard}_psf',
                           format='1E',
                           array=mag))

    cat.append(fits.Column(name=f'e_{filt_standard}_psf',
                           format='1E',
                           array=e_mag))

    cat.append(fits.Column(name=f's2n_{filt_standard}_psf',
                           format='1E',
                           array=s2n))

    if extinction_maps_path is not None:
        if extinction_correction.lower() == 'schlegel':

            RA = cat_data.loc[:, f'RA_{filt_standard}'].values
            DEC = cat_data.loc[:, f'DEC_{filt_standard}'].values

            EBV = get_EBV_schlegel(RA  = RA,
                                   DEC = DEC,
                                   ebv_maps_path = extinction_maps_path)

            cat.append(fits.Column(name=f'EBV_SCH',
                                   format='1E',
                                   array=EBV))

    # Generate HDU from columns
    hdu = fits.BinTableHDU.from_columns(cat)

    # Save HDU
    hdu.writeto(save_file)

def check_photometry(field, save_path, photometry, filter_list):
    """
    Checks if photometry has been already done for a given field

    Parameters
    ----------
    field: str
        Name of the S-PLUS field
    save_path: str
        Configuration file 'save_path' parameter
    photometry: str
        Photometry mode (single, dual, psf)
    filter_list: list
        List of S-PLUS filters

    Returns
    -------
    bool
        True if photometry is complet and False if not
    """

    if photometry.lower() == 'single':
        check_file = os.path.join(save_path, '{field}', 'Photometry',
                                  'single', 'catalogs',
                                  'sex_{field}_{filt}_single.fits')

    elif photometry.lower() == 'dual':
        check_file = os.path.join(save_path, '{field}', 'Photometry',
                                  'dual', 'catalogs',
                                  'sex_{field}_{filt}_dual.fits')

    elif photometry.lower() == 'psf':
        check_file = os.path.join(save_path, '{field}', 'Photometry',
                                  'psf', 'catalogs',
                                  '{field}_{filt}_psf.cat')

    else:
        raise ValueError(f"Unsupported photometry mode: {photometry}")

    has_all_photometry = True

    for filt in filter_list:
        filt_file = check_file.format(field = field, filt = filt)

        if not os.path.exists(filt_file):
            has_all_photometry = False

    return has_all_photometry


# Create 32 aper catalogs
def sexcatalog_apply_calibration_aper(catalog_file, zp_file, save_file,
                                 filter_name, sex_mag_zp,
                                 mode = 'dual', field = 'NoFieldName',
                                 drname = 'NoDRname'):

    # Load photometry catalog (with aperture correction)
    phot_cat = fits.open(catalog_file)
    phot_cat = phot_cat[1].data

    N_sources = len(phot_cat)

    # Load ZP
    ZPs = zp_read(zp_file)
    ZP = ZPs[f'SPLUS_{filter_name}']

    # Standard filter name
    filt_standard = translate_filter_standard(filter_name)

    # Create new data Table
    cat = []

    # FIELD ID
    phot_cat.columns[f'FIELD_ID'].name = f'ID'
    cat.append(phot_cat.columns[f'ID'])
    phot_cat.columns[f'FIELD_ID_RA'].name = f'ID_RA'
    cat.append(phot_cat.columns[f'ID_RA'])
    phot_cat.columns[f'FIELD_ID_DEC'].name = f'ID_DEC'
    cat.append(phot_cat.columns[f'ID_DEC'])


    # Add PHOT IDs
    if mode == "dual":
        cat.append(phot_cat.columns[f'PHOT_ID_dual'])
        cat.append(phot_cat.columns[f'PHOT_ID_RA_dual'])
        cat.append(phot_cat.columns[f'PHOT_ID_DEC_dual'])

        cat.append(fits.Column(name=f'{filt_standard}_ID_dual',
                               format='50A',
                               array=phot_cat.columns[f'PHOT_ID_dual'].array))

    elif mode == "single":
        cat.append(phot_cat.columns[f'PHOT_ID_single'])
        cat.append(phot_cat.columns[f'PHOT_ID_RA_single'])
        cat.append(phot_cat.columns[f'PHOT_ID_DEC_single'])

        cat.append(phot_cat.columns[f'{filt_standard}_ID_single'])


    if mode == "single":
        cat.append(phot_cat.columns[f"RA_{filt_standard}"])
        cat.append(phot_cat.columns[f"DEC_{filt_standard}"])
    elif mode == "dual":
        phot_cat.columns['ALPHA_J2000'].name = 'RA'
        cat.append(phot_cat.columns['RA'])
        phot_cat.columns['DELTA_J2000'].name = 'DEC'
        cat.append(phot_cat.columns['DEC'])

    ncols = phot_cat.columns[f"MAG_APER"].array.shape[1]

    for i in range(ncols):

        fmt = '1E'
        f = phot_cat.columns[f'MAG_APER'].array[:,i] != 99

        # FLUX
        FLUX = phot_cat.columns[f'FLUX_APER'].array[:,i]
        e_FLUX = phot_cat.columns[f'FLUXERR_APER'].array[:,i]

        # Signal to noise
        s2n = FLUX / e_FLUX

        # AB magnitude
        mag = phot_cat.columns[f'MAG_APER'].array[:,i]
        mag[f] += ZP - sex_mag_zp

        e_mag = phot_cat.columns[f'MAGERR_APER'].array[:,i]

        cat.append(fits.Column(name=f'{filt_standard}_aper_id{i}',
                               format=fmt,
                               array=mag))

        cat.append(fits.Column(name=f'e_{filt_standard}_aper_id{i}',
                               format=fmt,
                               array=e_mag))

        cat.append(fits.Column(name=f's2n_{filt_standard}_aper_id{i}',
                               format=fmt,
                               array=s2n))

    hdul_vac = fits.BinTableHDU.from_columns(cat)
    hdul_vac.writeto(save_file)


def extract_vac_features(catalog, save_file, filt):

    # Load photometry catalog
    phot_cat = fits.open(catalog)
    phot_cat = phot_cat[1].data

    cat = []

    if filt == "detection":
        cat.append(phot_cat.columns['ID'])
        cat.append(phot_cat.columns['PHOT_ID_dual'])
        cat.append(phot_cat.columns['RA'])
        cat.append(phot_cat.columns['DEC'])
        cat.append(phot_cat.columns['A'])
        cat.append(phot_cat.columns['B'])
        cat.append(phot_cat.columns['KRON_RADIUS'])
        cat.append(phot_cat.columns['FWHM_n'])
        cat.append(phot_cat.columns['MU_MAX_INST'])
        cat.append(phot_cat.columns['ISOarea'])
        cat.append(phot_cat.columns['SEX_FLAGS_DET'])
        cat.append(phot_cat.columns['s2n_DET_aper_6'])

    else:
        filt = translate_filter_standard(filt)
        cat.append(phot_cat.columns['PHOT_ID_dual'])
        cat.append(phot_cat.columns[f'SEX_FLAGS_{filt}'])
        cat.append(phot_cat.columns[f'{filt}_iso'])
        cat.append(phot_cat.columns[f'e_{filt}_iso'])
        cat.append(phot_cat.columns[f'{filt}_aper_3'])
        cat.append(phot_cat.columns[f'e_{filt}_aper_3'])
        cat.append(phot_cat.columns[f'{filt}_aper_6'])
        cat.append(phot_cat.columns[f'e_{filt}_aper_6'])
        cat.append(phot_cat.columns[f'{filt}_auto'])
        cat.append(phot_cat.columns[f'e_{filt}_auto'])
        cat.append(phot_cat.columns[f'{filt}_petro'])
        cat.append(phot_cat.columns[f'e_{filt}_petro'])
        cat.append(phot_cat.columns[f'{filt}_PStotal'])
        cat.append(phot_cat.columns[f'e_{filt}_PStotal'])
        cat.append(phot_cat.columns[f'FWHM_n_{filt}'])
        cat.append(phot_cat.columns[f'MU_MAX_{filt}'])

    hdul_vac = fits.BinTableHDU.from_columns(cat)
    hdul_vac.writeto(save_file)


################################################################################
# Fit psf photometry offsets

def estimate_field_dual_psf_offset(catalog, save_file, filters):

    # Load photometry catalog
    cat = fits.open(catalog)
    cat = cat[1].data

    offset = {}

    for filt in filters:
        mag_dual = cat.columns[f"{filt}_1"].array
        e_mag_dual = cat.columns[f"{filt}_err_1"].array
        dual_class_star = cat.columns[f"CLASS_STAR_1"].array
        mag_psf = cat.columns[f"{filt}_2"].array

        f = (dual_class_star > 0.9) & (e_mag_dual < 0.02)

        offset[filt] = mean_robust(mag_dual[f] - mag_psf[f])

    print(offset)

    zp_write(zp_dict = offset, save_file = save_file, filters_list = filters)


def estimate_overall_dual_psf_offset(offset_files, save_file, filters):

    overall_offsets = {}

    for filt in filters:

        filter_offsets = np.full(len(offset_files), np.nan)

        for i in range(len(offset_files)):
            field_offsets = zp_read(offset_files[i])
            filter_offsets[i] = field_offsets[filt]

        filter_offsets = filter_offsets.reshape(-1, 1)

        kde_dens = KernelDensity(kernel='gaussian', bandwidth=0.05).fit(filter_offsets)

        # Transform to kde
        x = np.arange(-10, 10, 0.001)
        y = np.exp(kde_dens.score_samples(x.reshape(-1, 1)))

        # get mode
        mode = x[y == np.max(y)][0]

        overall_offsets[filt] = mode

    zp_write(zp_dict=overall_offsets, save_file=save_file,
             filters_list=filters)


def add_inst_offset(catalog, offset_file, save_file):

    # Load photometry catalog
    cat = fits.open(catalog)

    # Load offsets
    offsets = zp_read(offset_file)

    for filt in offsets.keys():
        f = cat[1].data.columns[filt].array != 99
        cat[1].data.columns[filt].array[f] += offsets[filt]

    cat.writeto(save_file)
