# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                            calibration_internal.py
#               Runs the internal calibration step of the pipeline
# ******************************************************************************

"""
Obtains the external calibration zero-points by fitting models to a reference
catalog and comparing predicted S-PLUS magnitudes to instrumental magnitudes

The S-PLUS field is given as the first command line argument. Configurations
are set in the config file, given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

prepare_catalog_for_internal_calibration()
fit_sed_to_splus()
get_internal_calib_zero_points()
apply_external_zero_points()
plot_internal_zp()
combine_external_and_internal_zps()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

Assumes that crossmatch.py has already been run for this field.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 calibration_external.py *field_name* *config_file*

----------------
"""

################################################################################
# Import external packages

import os
import sys

steps_path = os.path.split(__file__)[0]
pipeline_path = os.path.split(steps_path)[0]
spluscalib_path = os.path.split(pipeline_path)[0]

sys.path.append(spluscalib_path)

################################################################################
# Import spluscalib packages

from spluscalib import utils as ut

################################################################################
# Read parameters

field     = sys.argv[1]
conf_file = sys.argv[2]

conf = ut.pipeline_conf(conf_file)

################################################################################
# Get directories

field_path       = os.path.join(conf['run_path'], field)
crossmatch_path  = os.path.join(field_path, 'Crossmatch')

suffix = ut.calibration_suffix(conf)
calibration_path  = os.path.join(field_path, f'Calibration_{suffix}')

external_cal_path = os.path.join(calibration_path, 'external')
external_plot_path = os.path.join(external_cal_path, 'plots')

stloc_cal_path = os.path.join(calibration_path, 'stlocus')
stloc_plot_path = os.path.join(stloc_cal_path, 'plots')

internal_cal_path = os.path.join(calibration_path, 'internal')
internal_plot_path = os.path.join(internal_cal_path, 'plots')

log_path = os.path.join(calibration_path, 'logs')


################################################################################
# Initiate log file

ut.makedir(calibration_path)
ut.makedir(internal_cal_path)
ut.makedir(internal_plot_path)
ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'calibration_internal.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(calibration_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Begin script

# ***************************************************
#    Copy instrumental magnitudes catalog
# ***************************************************


def prepare_catalog_for_internal_calibration():

    """
    Copy S-PLUS instrumental magnitudes to external calibration path
    """

    print("")
    ut.printlog(('********** '
                 'Preparing pre-internal calibration S-PLUS magnitudes catalog '
                 '**********'),
                 log_file)
    print("")

    if 'calibration_stloc' in conf['run_steps']:
        catalog_name = f"{field}_mag_stlocus.cat"
        catalog_file = os.path.join(stloc_cal_path, catalog_name)

    else:
        catalog_name = f"{field}_mag_ext.cat"
        catalog_file = os.path.join(external_cal_path, catalog_name)

    save_name = f"{field}_pre_internal.cat"
    save_file = os.path.join(internal_cal_path, save_name)

    if not os.path.exists(save_file):

        # Copy the last calibrated catalog
        cmd = f"cp {catalog_file} {save_file}"
        ut.printlog(cmd, log_file)
        os.system(cmd)

    else:
        ut.printlog(f"File {save_name} already created", log_file)


prepare_catalog_for_internal_calibration()

# ***************************************************
#    Fit SEDs to reference catalog
# ***************************************************


def fit_sed_to_splus():

    """
    Fits SEDs to the reference catalog magnitudes to predict the S-PLUS
    calibrated magnitudes
    """

    print("")
    ut.printlog(('********** '
                 'Fitting SEDs to reference '
                 '**********'),
                 log_file)
    print("")

    models_file = conf['path_to_models']

    splus_mag_catalog = f"{field}_pre_internal.cat"
    splus_mag_file    = os.path.join(internal_cal_path, splus_mag_catalog)

    bayesian_fitting = conf['model_fitting_bayesian']
    ebv_mode = conf['model_fitting_ebv_cut']

    ref_mag_cols  = conf['internal_sed_fit']

    #pred_mag_cols = None
    pred_mag_cols = conf['internal_sed_pred'] + conf['external_sed_fit']

    save_name = f"{field}_splus_sed_fit.cat"
    save_file = os.path.join(internal_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.sed_fitting(models        = models_file,
                       catalog       = splus_mag_file,
                       save_file     = save_file,
                       ref_mag_cols  = ref_mag_cols,
                       pred_mag_cols = pred_mag_cols,
                       bayesian      = bayesian_fitting,
                       ebv_mode      = ebv_mode)

        ut.printlog(f"Generated SED fit catalog {save_file}", log_file)
    else:
        ut.printlog(f"SED fit catalog {save_name} already exists", log_file)


fit_sed_to_splus()


# ***************************************************
#    Get external calibration zero points
# ***************************************************

def get_internal_calib_zero_points():

    """
    Obtains the S-PLUS internal calibration zero-points
    """

    print("")
    ut.printlog(('********** '
                 'Getting internal calibration ZPs '
                 '**********'),
                 log_file)
    print("")

    catalog_name = f"{field}_splus_sed_fit.cat"
    catalog_file = os.path.join(internal_cal_path, catalog_name)

    save_name = f"{field}_internal_tmp.zp"
    save_file = os.path.join(internal_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.zp_estimate(catalog = catalog_file,
                       save_file = save_file,
                       filters_list = conf['internal_sed_pred'],
                       mag_cut   = conf['zp_fitting_mag_cut'])

        ut.printlog(f"Created zp file {save_file}", log_file)

    else:
        ut.printlog(f"ZP file {save_name} already exists", log_file)


get_internal_calib_zero_points()


# ***************************************************
#    Add offset to S-PLUS reference calibration
# ***************************************************

def add_offset_to_splus_reference_calibration():
    """
    Adds offset to S-PLUS reference calibration
    """

    if conf['offset_include_after'].lower() == "internal":
        print("")
        ut.printlog(('********** '
                     'Adding offset to S-PLUS reference calibration '
                     '**********'),
                    log_file)
        print("")

    internal_zp_name = f"{field}_internal_tmp.zp"
    internal_zp_file = os.path.join(internal_cal_path, internal_zp_name)

    save_name = f"{field}_internal.zp"
    save_file = os.path.join(internal_cal_path, save_name)

    if not os.path.exists(save_file):

        if conf['offset_include_after'].lower() == "internal":
            offset_zp_name = f'offset_refcalib.zp'
            offset_zp_file = os.path.join(internal_cal_path, offset_zp_name)

            cmd = f"cp {conf['offset_to_splus_refcalib']} {offset_zp_file}"
            ut.printlog(cmd, log_file)
            os.system(cmd)

            zp_file_list = [internal_zp_file, offset_zp_file]

            filters = []
            for filt in conf['filters']:
                filters.append(f"SPLUS_{filt}")

            # Combine zero-points
            ut.zp_add(zp_file_list=zp_file_list,
                      save_file=save_file,
                      filters=filters,
                      inst_zp=0)

        else:
            cmd = f"cp {internal_zp_file} {save_file}"
            os.system(cmd)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"File {save_name} already exists", log_file)


add_offset_to_splus_reference_calibration()


# ***************************************************
#    Apply Zero Points
# ***************************************************


def apply_internal_zero_points():

    """
    Applies internal zero-points to mag_inst catalog
    """

    print("")
    ut.printlog(('********** '
                 'Applying internal zero-points to mag_inst catalog '
                 '**********'),
                 log_file)
    print("")

    catalog_name = f"{field}_splus_sed_fit.cat"
    catalog_file = os.path.join(internal_cal_path, catalog_name)

    zp_name = f"{field}_internal.zp"
    zp_file = os.path.join(internal_cal_path, zp_name)

    save_name = f"{field}_mag_int.cat"
    save_file = os.path.join(internal_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.zp_apply(catalog   = catalog_file,
                    save_file = save_file,
                    zp_file   = zp_file)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


apply_internal_zero_points()

# ***************************************************
#          Plot internal ZPs fitting
# ***************************************************


def plot_internal_zp():

    """
    Makes diagnostic plots of the external zp fitting process
    """

    print("")
    ut.printlog(('********** '
                 'Plotting internal zp-fitting process '
                 '**********'),
                 log_file)
    print("")

    sed_fit_name = f"{field}_splus_sed_fit.cat"
    sed_fit_file = os.path.join(internal_cal_path, sed_fit_name)

    zp_name = f"{field}_internal.zp"
    zp_file = os.path.join(internal_cal_path, zp_name)

    for filt in conf['internal_sed_pred']:
        save_name = f"{field}_{filt}_int.png"
        save_file = os.path.join(internal_plot_path, save_name)

        if not os.path.exists(save_file):
            ut.plot_zp_fitting(sed_fit_file = sed_fit_file,
                               zp_file      = zp_file,
                               save_file    = save_file,
                               filt         = filt,
                               mag_cut      = conf['zp_fitting_mag_cut'])

            ut.printlog(f"Saved plot {save_file}", log_file)

        else:
            ut.printlog(f"Plot {save_name} already made", log_file)


plot_internal_zp()


# ***************************************************
#    Combine external + stlocus + internal zps
# ***************************************************

def combine_external_and_internal_zps():
    """
    Combines the external and internal .zp files into a single .zp file
    """

    print("")
    ut.printlog(('********** '
                 'Combining external and internal .zp files '
                 '**********'),
                log_file)
    print("")

    if 'calibration_stloc' in conf['run_steps']:
        ext_zp_name = f"{field}_external_and_stlocus.zp"
        ext_zp_file = os.path.join(stloc_cal_path, ext_zp_name)
    else:
        ext_zp_name = f"{field}_external.zp"
        ext_zp_file = os.path.join(external_cal_path, ext_zp_name)

    int_zp_name = f"{field}_internal.zp"
    int_zp_file = os.path.join(internal_cal_path, int_zp_name)

    save_name = f"{field}_external_and_internal.zp"
    save_file = os.path.join(internal_cal_path, save_name)

    filters = []
    for filt in conf['filters']:
        filters.append(f"SPLUS_{filt}")

    if not os.path.exists(save_file) or True:

        ut.zp_add(zp_file_list=[ext_zp_file, int_zp_file],
                  save_file=save_file,
                  filters=filters)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


combine_external_and_internal_zps()
