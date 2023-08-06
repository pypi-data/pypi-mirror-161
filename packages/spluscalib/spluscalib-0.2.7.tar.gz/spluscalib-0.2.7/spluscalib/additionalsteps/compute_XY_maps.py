# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                         compute_XY_correction_maps.py
#      Computes XY zero-points offsets in relation to the reference catalog
# ******************************************************************************

"""
Combines intermediare calibration catalogs for a list of fields

Command line arguments for this script are, respectivelly:
1) Location of the S-PLUS fields list file
2) Location of the configuration file used in the calibration
3) Location to save the intermediary calibration catalogs

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

concatenate_instrumental_catalogs()
concatenate_external_calib_catalogs()
concatenate_stlocus_calib_catalogs()
concatenate_internal_calib_catalogs()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
This script should be run individually and not within the pipeline.py script

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 combine_calibration_catalogs.py *field_list_file* *config_file*

----------------
"""

################################################################################
# Import external packages

import os
import sys

addsteps_path = os.path.split(__file__)[0]
pipeline_path = os.path.split(addsteps_path)[0]
spluscalib_path = os.path.split(pipeline_path)[0]

sys.path.append(spluscalib_path)

################################################################################
# Import spluscalib packages

from spluscalib import utils as ut

################################################################################
# Read parameters

field_list_file = sys.argv[1]
conf_file = sys.argv[2]
save_path = sys.argv[3]

conf = ut.pipeline_conf(conf_file)

suffix = ut.calibration_suffix(conf)

if conf['reference_catalog'][0].lower() != 'ivezic':
    raise ValueError('Only Ivezic catalog is supported for XY computation')

################################################################################
# Initiate log file

ut.makedir(save_path)

log_file_name = os.path.join(save_path, 'compute_XY_maps.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(save_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Reading field list

ut.printlog("*********** Reading field list **********", log_file)

fields = ut.load_field_list(field_list_file)

ut.printlog(f"Running the pipeline for fields:", log_file)
ut.printlog(f"{fields}", log_file)

mag_pairs = {'SPLUS_U': 'SDSS_U',
             'SPLUS_G': 'SDSS_G',
             'SPLUS_R': 'SDSS_R',
             'SPLUS_I': 'SDSS_I',
             'SPLUS_Z': 'SDSS_Z'}

xbins = [0, 9200, 32]
ybins = [0, 9200, 32]

################################################################################
# Begin script

plots_path = os.path.join(save_path, 'plots')
ut.makedir(plots_path)

# ***************************************************
#    Convert catalogs to fits
# ***************************************************

def convert_2_fits():

    """
    Converts catalogs from ascii to fits
    """

    for field in fields:
        cat_name = f'{field}_mag_ext.cat'
        cat_step = 'external'

        cat_file = os.path.join(conf['save_path'], f'{field}',
                                f'Calibration_{suffix}', cat_step,
                                cat_name)

        save_name = f'{field}_mag_ext.fits'
        save_file = os.path.join(save_path, save_name)

        if not os.path.exists(save_file):

            cmd = f"java -jar {conf['path_to_stilts']} tcopy "
            cmd += f"in={cat_file} ifmt=ascii "
            cmd += f"out={save_file} ofmt=fits"

            ut.printlog(cmd, log_file)
            os.system(cmd)

        else:
            ut.printlog(f"File {save_file} already exists.", log_file)


convert_2_fits()

# ***************************************************
#    fix X,Y rotation
# ***************************************************

def fix_XY_rotation():

    """
    Fixes XY rotation of S-PLUS images
    """

    for field in fields:

        cat_name = f'{field}_mag_ext.fits'
        cat_file = os.path.join(save_path, cat_name)

        save_name = f'{field}_mag_ext_xycorr.fits'
        save_file = os.path.join(save_path, save_name)

        if not os.path.exists(save_file):

            ut.fix_xy_rotation(catalog = cat_file,
                               save_file = save_file,
                               xcol = 'X',
                               ycol = 'Y')

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"File {save_file} already exists.", log_file)


fix_XY_rotation()

# ***************************************************
#    Combine calibrated catalogs
# ***************************************************

def concatenate_calib_catalogs():

    """
    Concatenates calibration catalogs after the external calibration step
    """

    print("")
    ut.printlog(('********** '
                 'Concatenating external calibrated magnitudes '
                 '**********'),
                 log_file)
    print("")

    cat_name = '{field}_mag_ext_xycorr.fits'
    cat_file = os.path.join(save_path, cat_name)

    # Start save name
    save_name = 'concat_mag_ext_xycorr.cat'
    save_file = os.path.join(save_path, save_name)

    if not os.path.exists(save_file):

        # Create list of field catalogs
        catalogs_list = []

        for field in fields:
            catalogs_list.append(cat_file.format(field=field))

        ut.concat_data(files_list=catalogs_list,
                       save_file=save_file)

        ut.printlog(f"Created catalog {save_file}", log_file)

    else:
        ut.printlog(f"File {save_name} already exists", log_file)


concatenate_calib_catalogs()


# ***************************************************
#    Compute XY maps
# ***************************************************

def compute_xy_maps():

    """
    Computes XY correction maps
    """

    print("")
    ut.printlog(('********** '
                 'Computing XY correction maps '
                 '**********'),
                 log_file)
    print("")

    cat_name = 'concat_mag_ext_xycorr.cat'
    cat_file = os.path.join(save_path, cat_name)

    for filt in mag_pairs.keys():

        save_name = f"xy_corr_map_{filt}.npy"
        save_file = os.path.join(save_path, save_name)

        if not os.path.exists(save_file):

            ut.get_xy_correction_grid(data_file = cat_file,
                                      save_file = save_file,
                                      mag       = filt,
                                      mag_ref   = mag_pairs[filt],
                                      xbins     = xbins,
                                      ybins     = ybins)

            ut.printlog(f"Created file {save_file}.", log_file)

        else:
            ut.printlog(f"File {save_file} already exists.", log_file)


compute_xy_maps()


# ***************************************************
#    Plot XY maps
# ***************************************************

def plot_xy_maps():

    """
    Plots XY correction maps
    """

    print("")
    ut.printlog(('********** '
                 'Plotting XY correction maps '
                 '**********'),
                 log_file)
    print("")

    for filt in mag_pairs.keys():

        grid_name = f"xy_corr_map_{filt}.npy"
        grid_file = os.path.join(save_path, grid_name)

        save_name = f"xy_corr_map_{filt}.png"
        save_file = os.path.join(plots_path, save_name)

        if not os.path.exists(save_file):

            ut.plot_xy_correction_grid(grid_file = grid_file,
                                       save_file = save_file,
                                       mag       = filt,
                                       xbins     = xbins,
                                       ybins     = ybins)

            ut.printlog(f"Created file {save_file}.", log_file)

        else:
            ut.printlog(f"File {save_file} already exists.", log_file)


plot_xy_maps()