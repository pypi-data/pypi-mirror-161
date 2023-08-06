# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                            calibration_external.py
#               Runs the external calibration step of the pipeline
# ******************************************************************************

"""
Obtains the external calibration zero-points by fitting models to a reference
catalog and comparing predicted S-PLUS magnitudes to instrumental magnitudes

The S-PLUS field is given as the first command line argument. Configurations
are set in the config file, given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

copy_splus_instrumental_catalog()
fit_sed_to_reference()
get_external_calib_zero_points()
apply_external_zero_points()
plot_external_zp()
plot_model_x_reference()

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
import copy

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

log_path = os.path.join(calibration_path, 'logs')


################################################################################
# Initiate log file

ut.makedir(calibration_path)
ut.makedir(external_cal_path)
ut.makedir(external_plot_path)
ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'calibration_external.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(calibration_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Begin script

# ***************************************************
#    Copy instrumental magnitudes catalog
# ***************************************************


def copy_splus_instrumental_catalog():

    """
    Copy S-PLUS instrumental magnitudes to external calibration path
    """

    print("")
    ut.printlog(('********** '
                 'Copying S-PLUS instrumental magnitudes catalog '
                 '**********'),
                 log_file)
    print("")

    cmatch_name = ut.crossmatch_catalog_name(field, conf)
    cmatch_file = os.path.join(crossmatch_path, cmatch_name)

    if conf['extinction_correction'].lower() != 'none':
        correction  = conf['extinction_correction']
        cmatch_file = cmatch_file.replace(".fits",
                                          f"_ebvcorr_{correction}.fits")

    save_name = f'{field}_mag_inst.cat'
    save_file = os.path.join(external_cal_path, save_name)

    if not os.path.exists(save_file):

        cmd = f"java -jar {conf['path_to_stilts']} tcopy "
        cmd += f"in={cmatch_file} ifmt=fits "
        cmd += f"out={save_file} ofmt=ascii"
        ut.printlog(cmd, log_file)
        os.system(cmd)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


copy_splus_instrumental_catalog()

# ***************************************************
#    Fit SEDs to reference catalog
# ***************************************************


def fit_sed_to_reference():

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

    mag_inst_catalog = f'{field}_mag_inst.cat'
    mag_inst_file    = os.path.join(external_cal_path, mag_inst_catalog)

    ref_mag_cols  = conf['external_sed_fit']

    bayesian_fitting = conf['model_fitting_bayesian']

    pred_mag_cols = copy.deepcopy(conf['filters'])
    for i in range(len(pred_mag_cols)):
        pred_mag_cols[i] = 'SPLUS_' + pred_mag_cols[i]

    save_name = f"{field}_ref_sed_fit.cat"
    save_file = os.path.join(external_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.sed_fitting(models        = models_file,
                       catalog       = mag_inst_file,
                       save_file     = save_file,
                       ref_mag_cols  = ref_mag_cols,
                       pred_mag_cols = pred_mag_cols,
                       bayesian      = bayesian_fitting)

        ut.printlog(f"Generated SED fit catalog {save_file}", log_file)
    else:
        ut.printlog(f"SED fit catalog {save_name} already exists", log_file)


fit_sed_to_reference()


# ***************************************************
#    Get external calibration zero points
# ***************************************************

def get_external_calib_zero_points():

    """
    Obtains the S-PLUS external calibration zero-points
    """

    print("")
    ut.printlog(('********** '
                 'Getting external calibration ZPs '
                 '**********'),
                 log_file)
    print("")

    catalog_name = f"{field}_ref_sed_fit.cat"
    catalog_file = os.path.join(external_cal_path, catalog_name)

    save_name = f"{field}_external_tmp.zp"
    save_file = os.path.join(external_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.zp_estimate(catalog = catalog_file,
                       save_file = save_file,
                       filters_list = conf['external_sed_pred'],
                       mag_cut   = conf['zp_fitting_mag_cut'])

        ut.printlog(f"Created zp file {save_file}", log_file)

    else:
        ut.printlog(f"ZP file {save_name} already exists", log_file)


get_external_calib_zero_points()


# ***************************************************
#    Add offset to S-PLUS reference calibration
# ***************************************************

def add_offset_to_splus_reference_calibration():

    """
    Adds offset to S-PLUS reference calibration
    """

    if conf['offset_include_after'].lower() == "external":
        print("")
        ut.printlog(('********** '
                     'Adding offset to S-PLUS reference calibration '
                     '**********'),
                     log_file)
        print("")

    external_zp_name = f"{field}_external_tmp.zp"
    external_zp_file = os.path.join(external_cal_path, external_zp_name)

    save_name = f"{field}_external.zp"
    save_file = os.path.join(external_cal_path, save_name)

    if not os.path.exists(save_file):

        if conf['offset_include_after'].lower() == "external":
            offset_zp_name = f'offset_refcalib.zp'
            offset_zp_file = os.path.join(external_cal_path, offset_zp_name)

            cmd = f"cp {conf['offset_to_splus_refcalib']} {offset_zp_file}"
            ut.printlog(cmd, log_file)
            os.system(cmd)

            zp_file_list = [external_zp_file, offset_zp_file]

            filters = []
            for filt in conf['filters']:
                filters.append(f"SPLUS_{filt}")

            # Combine zero-points
            ut.zp_add(zp_file_list=zp_file_list,
                      save_file=save_file,
                      filters=filters,
                      inst_zp=0)

        else:
            cmd = f"cp {external_zp_file} {save_file}"
            os.system(cmd)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"File {save_name} already exists", log_file)


add_offset_to_splus_reference_calibration()

# ***************************************************
#    Apply Zero Points
# ***************************************************


def apply_external_zero_points():

    """
    Applies external zero-points to mag_inst catalog
    """

    print("")
    ut.printlog(('********** '
                 'Applying external zero-points to mag_inst catalog '
                 '**********'),
                 log_file)
    print("")

    catalog_name = f'{field}_ref_sed_fit.cat'
    catalog_file = os.path.join(external_cal_path, catalog_name)

    zp_name = f"{field}_external.zp"
    zp_file = os.path.join(external_cal_path, zp_name)

    save_name = f"{field}_mag_ext.cat"
    save_file = os.path.join(external_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.zp_apply(catalog   = catalog_file,
                    save_file = save_file,
                    zp_file   = zp_file)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


apply_external_zero_points()


# ***************************************************
#          Plot external ZPs fitting
# ***************************************************

def plot_external_zp():

    """
    Makes diagnostic plots of the external zp fitting process
    """

    print("")
    ut.printlog(('********** '
                 'Plotting external zp-fitting process '
                 '**********'),
                 log_file)
    print("")

    sed_fit_name = f"{field}_ref_sed_fit.cat"
    sed_fit_file = os.path.join(external_cal_path, sed_fit_name)

    zp_name = f"{field}_external.zp"
    zp_file = os.path.join(external_cal_path, zp_name)

    for filt in conf['external_sed_pred']:
        save_name = f"{field}_{filt}_ext.png"
        save_file = os.path.join(external_plot_path, save_name)

        if not os.path.exists(save_file):
            ut.plot_zp_fitting(sed_fit_file = sed_fit_file,
                               zp_file      = zp_file,
                               save_file    = save_file,
                               filt         = filt,
                               mag_cut      = conf['zp_fitting_mag_cut'])

            ut.printlog(f"Saved plot {save_file}", log_file)

        else:
            ut.printlog(f"Plot {save_name} already made", log_file)


plot_external_zp()


# ***************************************************
#       Plot comparison model and reference
# ***************************************************

def plot_model_x_reference():

    """
    Plots the comparison of reference magnitudes and model fitted magnitudes
    """

    print("")
    ut.printlog(('********** '
                 'Plotting comparison between model and reference '
                 '**********'),
                 log_file)
    print("")

    sed_fit_name = f"{field}_ref_sed_fit.cat"
    sed_fit_file = os.path.join(external_cal_path, sed_fit_name)

    for filt in conf['external_sed_fit']:
        save_name = f"{field}_{filt}_ref_x_mod.png"
        save_file = os.path.join(external_plot_path, save_name)

        if not os.path.exists(save_file):
            ut.plot_zp_fitting(sed_fit_file = sed_fit_file,
                               save_file    = save_file,
                               filt         = filt,
                               mag_cut      = conf['zp_fitting_mag_cut'],
                               label        = 'mag_ref',
                               color        = "#444444")

            ut.printlog(f"Saved plot {save_file}", log_file)

        else:
            ut.printlog(f"Plot {save_name} already made", log_file)


plot_model_x_reference()
