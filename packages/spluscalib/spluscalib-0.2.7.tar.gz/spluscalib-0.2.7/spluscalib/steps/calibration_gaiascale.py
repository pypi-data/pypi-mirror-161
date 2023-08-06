# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                           calibration_gaiascale.py
#               Runs the internal calibration step of the pipeline
# ******************************************************************************

"""
Obtains the gaia scale calibration zero-points by fitting models to s-plus
previously calibrated catalog and comparing predicted and observed Gaia
magnitudes

The S-PLUS field is given as the first command line argument. Configurations
are set in the config file, given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

crossmatch_splus_gaia()
fit_sed_to_splus()
get_gaia_gaiascale_zero_points()
get_splus_gaiascale_zero_points()
apply_gaiascale_zero_points()
plot_gaiascale_zp()

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
stloc_cal_path = os.path.join(calibration_path, 'stlocus')
internal_cal_path = os.path.join(calibration_path, 'internal')

gaiascale_cal_path = os.path.join(calibration_path, 'gaiascale')
gaiascale_plot_path = os.path.join(gaiascale_cal_path, 'plots')

log_path = os.path.join(calibration_path, 'logs')


################################################################################
# Initiate log file

ut.makedir(calibration_path)
ut.makedir(gaiascale_cal_path)
ut.makedir(gaiascale_plot_path)
ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'calibration_gaiascale.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(calibration_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Begin script


# ***************************************************
#    Crossmatch S-PLUS and Gaia Catalog
# ***************************************************

def crossmatch_splus_gaia():

    """
    Crossmatch S-PLUS and Gaia catalogues
    """

    print("")
    ut.printlog(('********** '
                 'Crossmatching S-PLUS (calibrated) and Gaia'
                 ' **********'),
                log_file)
    print("")

    # Get latest S-PLUS calibrated catalog for the field
    if 'calibration_internal' in conf['run_steps']:
        splus_name = f"{field}_mag_int.cat"
        splus_file = os.path.join(internal_cal_path, splus_name)

    else:
        if 'calibration_stloc' in conf['run_steps']:
            splus_name = f"{field}_mag_stlocus.cat"
            splus_file = os.path.join(stloc_cal_path, splus_name)

        else:
            splus_name = f"{field}_mag_ext.cat"
            splus_file = os.path.join(external_cal_path, splus_name)

    # Get gaia catalog file for the field
    gaia_file = os.path.join(crossmatch_path, f'{field}_GAIADR2.fits')

    save_file = os.path.join(gaiascale_cal_path, 'splus_gaia.fits')

    if not os.path.exists(save_file):
        cmd  = f"java -jar {conf['path_to_stilts']} tmatch2 "

        cmd += f"in1={splus_file} ifmt1=ascii "
        cmd += f"values1='RAJ2000 DEJ2000' "

        cmd += f"in2={gaia_file} ifmt2=fits "
        cmd += f"values2='GAIADR2_RAJ2000 GAIADR2_DEJ2000' "

        cmd += f"join=1and2 find=best matcher=sky params=3 "

        cmd += f"ofmt=fits out={save_file} "

        ut.printlog(cmd, log_file)
        os.system(cmd)

        ut.printlog(f"Created catalog {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_file} already exists", log_file)


crossmatch_splus_gaia()


# ***************************************************
#    Apply extinction correction to Gaia
# ***************************************************

def correct_extinction_gaia_magnitudes():
    """
    Applying extinction correction to Gaia magnitudes
    """

    print("")
    ut.printlog(('********** '
                 'Applying extinction correction to Gaia magnitudes '
                 '**********'),
                 log_file)
    print("")

    ###############################
    # Get crossmatched catalog file
    cmatch_file = os.path.join(gaiascale_cal_path, 'splus_gaia.fits')

    ##################
    # Apply correction
    correction = conf['extinction_correction']
    ebv_map_path = conf['extinction_maps_path']

    save_file = cmatch_file.replace(".fits", "_ebvcorr.fits")

    # S-PLUS magnitudes are already extinction corrected, so apply only to Gaia
    # reference http://svo2.cab.inta-csic.es/theory/fps/index.php?mode=browse&gname=GAIA&gname2=GAIA2r&asttype=
    filters_Alambda_Av = {'GAIA_BP': 1.13,
                          'GAIA_G': 0.939,
                          'GAIA_RP': 0.659}

    if not os.path.exists(save_file):
        ut.correct_extinction(catalog = cmatch_file,
                              save_file = save_file,
                              correction = correction,
                              ebv_maps_path = ebv_map_path,
                              filters_Alambda_Av = filters_Alambda_Av)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Extinction corrected catalog already exists", log_file)


if conf['extinction_correction'].lower() != 'none':
    correct_extinction_gaia_magnitudes()


# ***************************************************
#    Convert cmatch catalog to ascii
# ***************************************************

def convert_gaia_xmatch_2ascii():
    """
    Convert cmatch catalog to ascii
    """

    print("")
    ut.printlog(('********** '
                 'Converting Gaia crossmatch to ascii '
                 '**********'),
                 log_file)
    print("")

    if conf['extinction_correction'].lower() != 'none':
        splus_gaia_catalog = f"splus_gaia_ebvcorr.fits"
    else:
        splus_gaia_catalog = f"splus_gaia.fits"

    splus_gaia_file = os.path.join(gaiascale_cal_path, splus_gaia_catalog)

    save_file = splus_gaia_file.replace(".fits", ".cat")

    if not os.path.exists(save_file):

        cmd  = f"java -jar {conf['path_to_stilts']} tcopy "

        cmd += f"ifmt=fits in={splus_gaia_file} "
        cmd += f"ofmt=ascii out={save_file}"

        ut.printlog(cmd, log_file)
        os.system(cmd)

    else:
        ut.printlog(f"File {save_file} already exists", log_file)


convert_gaia_xmatch_2ascii()

# ***************************************************
#    Fit SEDs to splus magnitudes
# ***************************************************


def fit_sed_to_splus():

    """
    Fits SEDs to the splus catalog magnitudes to predict the gaia magnitudes
    """

    print("")
    ut.printlog(('********** '
                 'Fitting SEDs to splus '
                 '**********'),
                 log_file)
    print("")

    models_file = conf['path_to_models']

    if conf['extinction_correction'].lower() != 'none':
        splus_gaia_catalog = f"splus_gaia_ebvcorr.cat"
    else:
        splus_gaia_catalog = f"splus_gaia.cat"

    splus_gaia_file = os.path.join(gaiascale_cal_path, splus_gaia_catalog)

    bayesian_fitting = conf['model_fitting_bayesian']
    ebv_mode = conf['model_fitting_ebv_cut']

    ref_mag_cols  = conf['gaiascale_sed_fit']
    pred_mag_cols = conf['gaiascale_sed_pred'] + conf['external_sed_fit']

    save_name = f"{field}_gaiascale_sed_fit.cat"
    save_file = os.path.join(gaiascale_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.sed_fitting(models        = models_file,
                       catalog       = splus_gaia_file,
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

def get_gaia_gaiascale_zero_points():

    """
    Obtains the gaia scale calibration zero-points in gaia magnitudes
    """

    print("")
    ut.printlog(('********** '
                 'Getting gaia scale calibration for gaia magnitudes '
                 '**********'),
                 log_file)
    print("")

    catalog_name = f"{field}_gaiascale_sed_fit.cat"
    catalog_file = os.path.join(gaiascale_cal_path, catalog_name)

    save_name = f"{field}_gaiascale_gaia.zp"
    save_file = os.path.join(gaiascale_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.zp_estimate(catalog = catalog_file,
                       save_file = save_file,
                       filters_list = conf['gaiascale_sed_pred'],
                       mag_cut   = conf['gaia_zp_fitting_mag_cut'])

        ut.printlog(f"Created zp file {save_file}", log_file)

    else:
        ut.printlog(f"ZP file {save_name} already exists", log_file)


get_gaia_gaiascale_zero_points()


# ***************************************************
#    Get splus gaiascale zero points
# ***************************************************

def get_splus_gaiascale_zero_points():

    """
    Obtains the gaia scale calibration zero-points for the S-PLUS filters
    """

    print("")
    ut.printlog(('********** '
                 'Getting gaia scale calibration for S-PLUS magnitudes '
                 '**********'),
                 log_file)
    print("")

    gaia_zp_name = f"{field}_gaiascale_gaia.zp"
    gaia_zp_file = os.path.join(gaiascale_cal_path, gaia_zp_name)

    filters_list = []
    for filt in conf['filters']:
        filters_list.append(f'SPLUS_{filt}')

    save_name = f"{field}_gaiascale_splus_tmp.zp"
    save_file = os.path.join(gaiascale_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.zp_gaiascale(gaia_zp_file = gaia_zp_file,
                        save_file    = save_file,
                        filters_list = filters_list)

        ut.printlog(f"Created zp file {save_file}", log_file)

    else:
        ut.printlog(f"ZP file {save_name} already exists", log_file)


get_splus_gaiascale_zero_points()


# ***************************************************
#    Add offset to S-PLUS reference calibration
# ***************************************************

def add_offset_to_splus_reference_calibration():
    """
    Adds offset to S-PLUS reference calibration
    """

    if conf['offset_include_after'].lower() == "gaiascale":
        print("")
        ut.printlog(('********** '
                     'Adding offset to S-PLUS reference calibration '
                     '**********'),
                    log_file)
        print("")

    gaiascale_zp_name = f"{field}_gaiascale_splus_tmp.zp"
    gaiascale_zp_file = os.path.join(gaiascale_cal_path, gaiascale_zp_name)

    save_name = f"{field}_gaiascale_splus.zp"
    save_file = os.path.join(gaiascale_cal_path, save_name)

    if not os.path.exists(save_file):

        if conf['offset_include_after'].lower() == "gaiascale":
            offset_zp_name = f'offset_refcalib.zp'
            offset_zp_file = os.path.join(gaiascale_cal_path, offset_zp_name)

            cmd = f"cp {conf['offset_to_splus_refcalib']} {offset_zp_file}"
            ut.printlog(cmd, log_file)
            os.system(cmd)

            zp_file_list = [gaiascale_zp_file, offset_zp_file]

            filters = []
            for filt in conf['filters']:
                filters.append(f"SPLUS_{filt}")

            # Combine zero-points
            ut.zp_add(zp_file_list=zp_file_list,
                      save_file=save_file,
                      filters=filters,
                      inst_zp=0)

        else:
            cmd = f"cp {gaiascale_zp_file} {save_file}"
            os.system(cmd)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"File {save_name} already exists", log_file)


add_offset_to_splus_reference_calibration()

# ***************************************************
#    Apply Zero Points
# ***************************************************

def apply_gaiascale_zero_points():

    """
    Applies gaiascale zero-points to latest catalog
    """

    print("")
    ut.printlog(('********** '
                 'Applying gaia scale zero-points to latest catalog '
                 '**********'),
                 log_file)
    print("")

    catalog_name = f"{field}_gaiascale_sed_fit.cat"
    catalog_file = os.path.join(gaiascale_cal_path, catalog_name)

    zp_name = f"{field}_gaiascale_splus.zp"
    zp_file = os.path.join(gaiascale_cal_path, zp_name)

    save_name = f"{field}_mag_gaiascale.cat"
    save_file = os.path.join(gaiascale_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.zp_apply(catalog   = catalog_file,
                    save_file = save_file,
                    zp_file   = zp_file)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


apply_gaiascale_zero_points()

# ***************************************************
#          Plot internal ZPs fitting
# ***************************************************


def plot_gaiascale_zp():

    """
    Makes diagnostic plots of the gaia scale zp fitting process
    """

    print("")
    ut.printlog(('********** '
                 'Plotting gaia scale zp-fitting process '
                 '**********'),
                 log_file)
    print("")

    sed_fit_name = f"{field}_gaiascale_sed_fit.cat"
    sed_fit_file = os.path.join(gaiascale_cal_path, sed_fit_name)

    zp_name = f"{field}_gaiascale_gaia.zp"
    zp_file = os.path.join(gaiascale_cal_path, zp_name)

    for filt in conf['gaiascale_sed_pred']:
        save_name = f"{field}_{filt}_gaiascale.png"
        save_file = os.path.join(gaiascale_plot_path, save_name)

        if not os.path.exists(save_file):
            ut.plot_zp_fitting(sed_fit_file = sed_fit_file,
                               zp_file      = zp_file,
                               save_file    = save_file,
                               filt         = filt,
                               mag_cut      = conf['gaia_zp_fitting_mag_cut'])

            ut.printlog(f"Saved plot {save_file}", log_file)

        else:
            ut.printlog(f"Plot {save_name} already made", log_file)


plot_gaiascale_zp()