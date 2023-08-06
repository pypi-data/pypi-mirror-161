# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                           calibration_diagnostic.py
#               Runs the diagnostic calibration step of the pipeline
# ******************************************************************************

"""
Predicts the reference catalog magnitudes by fitting models to s-plus
previously calibrated catalog. This can be used to check the accuracy of
the S-PLUS calibration after comparing to the real values of the magnitudes
in the reference catalog.

The S-PLUS field is given as the first command line argument. Configurations
are set in the config file, given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

fit_sed_to_splus_diagnostic()

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

suffix = ut.calibration_suffix(conf)
calibration_path  = os.path.join(field_path, f'Calibration_{suffix}')
crossmatch_path   = os.path.join(field_path, f'Crossmatch')

external_cal_path  = os.path.join(calibration_path, 'external')
stloc_cal_path     = os.path.join(calibration_path, 'stlocus')
internal_cal_path  = os.path.join(calibration_path, 'internal')
gaiascale_cal_path = os.path.join(calibration_path, 'gaiascale')

diagnostic_cal_path = os.path.join(calibration_path, 'diagnostic')

log_path = os.path.join(calibration_path, 'logs')


################################################################################
# Initiate log file

ut.makedir(diagnostic_cal_path)
ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'calibration_diagnostic.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(calibration_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")


################################################################################
# Begin script

# ***************************************************
#    Prepare catalog with reference magnitudes
# ***************************************************

def prepare_diagnostic_input():
    """
    Prepares diagnostic input catalog
    """

    print("")
    ut.printlog(('********** '
                 'Preparing diagnostic input catalog '
                 '**********'),
                 log_file)
    print("")

    if 'calibration_gaiascale' in conf['run_steps']:
        cat_name = f"{field}_mag_gaiascale.cat"
        cat_file = os.path.join(gaiascale_cal_path, cat_name)
    else:
        if 'calibration_internal' in conf['run_steps']:
            cat_name = f"{field}_mag_int.cat"
            cat_file = os.path.join(internal_cal_path, cat_name)
        else:
            cat_name = f"{field}_mag_ext.cat"
            cat_file = os.path.join(internal_cal_path, cat_name)

    select_columns = ['RAJ2000', 'DEJ2000', 'X', 'Y']

    for filt in conf['diagnostic_sed_fit']:
        select_columns.append(f"{filt}")
        select_columns.append(f"{filt}_err")

    for filt in conf['external_sed_fit']:
        select_columns.append(f"{filt}")
        select_columns.append(f"{filt}_err")

    save_name = f'{field}_diagnostic_input.cat'
    save_file = os.path.join(diagnostic_cal_path, save_name)

    if not os.path.exists(save_file):

        ut.select_columns(catalog        = cat_file,
                          save_file      = save_file,
                          select_columns = select_columns)

        ut.printlog(f"Created catalog {save_file}", log_file)

    else:
        ut.printlog(f"File {save_file} already exists.", log_file)


prepare_diagnostic_input()


# ***************************************************
#    Predict reference magnitudes
# ***************************************************

def fit_sed_to_splus_diagnostic():

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

    cat_name = f'{field}_diagnostic_input.cat'
    cat_file = os.path.join(diagnostic_cal_path, cat_name)

    msg = f"Fitting models to file {cat_file}"
    ut.printlog(msg, log_file)

    bayesian_fitting = conf['model_fitting_bayesian']
    ebv_mode = conf['model_fitting_ebv_cut']

    ref_mag_cols  = conf['diagnostic_sed_fit']
    pred_mag_cols = conf['external_sed_fit']

    if conf['extinction_correction'].lower() != 'none':
        save_name = 'diagnostic_mag_ebvcorr.cat'
    else:
        save_name = 'diagnostic_mag.cat'
    save_file = os.path.join(diagnostic_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.sed_fitting(models        = models_file,
                       catalog       = cat_file,
                       save_file     = save_file,
                       ref_mag_cols  = ref_mag_cols,
                       pred_mag_cols = pred_mag_cols,
                       bayesian      = bayesian_fitting,
                       ebv_mode      = ebv_mode)

        ut.printlog(f"Generated SED fit catalog {save_file}", log_file)
    else:
        ut.printlog(f"SED fit catalog {save_name} already exists", log_file)


fit_sed_to_splus_diagnostic()


# ***************************************************
#    Convert to fits
# ***************************************************

def convert_diagnostic_2fits():
    """
    Converts diagnostic catalog to fits
    """

    print("")
    ut.printlog(('********** '
                 'Converting diagnostic catalog to fits '
                 '**********'),
                 log_file)
    print("")

    if conf['extinction_correction'].lower() != 'none':
        cat_name = 'diagnostic_mag_ebvcorr.cat'
    else:
        cat_name = 'diagnostic_mag.cat'

    cat_file = os.path.join(diagnostic_cal_path, cat_name)

    save_file = cat_file.replace(".cat", ".fits")

    if not os.path.exists(save_file):

        cmd  = f"java -jar {conf['path_to_stilts']} tcopy "

        cmd += f"ifmt=ascii in={cat_file} "
        cmd += f"ofmt=fits out={save_file}"

        ut.printlog(cmd, log_file)
        os.system(cmd)

    else:
        ut.printlog(f"File {save_file} already exists", log_file)


convert_diagnostic_2fits()


# ***************************************************
#    Remove extinction correction
# ***************************************************

def remove_extinction_correction():
    """
    Removes extinction correction from reference magnitudes (also from models)
    """

    print("")
    ut.printlog(('********** '
                 'Removing exctinction correction '
                 '**********'),
                 log_file)
    print("")

    ###############################
    # Get crossmatched catalog file
    cat_name = 'diagnostic_mag_ebvcorr.fits'
    cat_file = os.path.join(diagnostic_cal_path, cat_name)

    ##################
    # Apply correction
    correction = conf['extinction_correction']
    ebv_map_path = conf['extinction_maps_path']

    save_name = f'{field}_diagnostic_mag.fits'
    save_file = os.path.join(diagnostic_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.correct_extinction(catalog = cat_file,
                              save_file = save_file,
                              correction = correction,
                              ebv_maps_path = ebv_map_path,
                              reverse = True,
                              include_mod = True)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Removed extinction correction catalog already exists",
                    log_file)


if conf['extinction_correction'].lower() != 'none':
    remove_extinction_correction()


# ******************************************************************************
#    !!!!!!!!!!!!!!!!!!!!!!!!!!! OBSOLETE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ******************************************************************************

# ***************************************************
#    Crossmatch with external catalog
# ***************************************************

def crossmatch_with_reference():

    """
    Crossmatches diagnostic predictions with extinction corrected reference
    """

    print("")
    ut.printlog(('********** '
                 'Crossmatching diagnostic predictions with extinction '
                 'corrected reference'
                 '**********'),
                 log_file)
    print("")

    model_mag_name = f"{field}_diagnostic_sed_fit.cat"
    model_mag_file = os.path.join(diagnostic_cal_path, model_mag_name)

    # Here I'm taking the file used in the external calibration step, since
    # it has the EB-V corrected reference magnitudes
    ref_mag_name = f"{field}_mag_inst.cat"
    ref_mag_file = os.path.join(external_cal_path, ref_mag_name)

    save_name = 'diagnostic_mag_temp.cat'
    save_file = os.path.join(diagnostic_cal_path, save_name)

    if not os.path.exists(save_file):

        cmd  = f"java -jar {conf['path_to_stilts']} tmatch2 "

        cmd += f"in1={ref_mag_file} ifmt1=ascii values1='RAJ2000 DEJ2000' "
        cmd += f"in2={model_mag_file} ifmt2=ascii values2='RAJ2000 DEJ2000' "

        cmd += f"out={save_file} ofmt=ascii "

        cmd += f"join=1and2 matcher=sky params=1"

        ut.printlog(cmd, log_file)
        os.system(cmd)

        ut.printlog(f"Created catalog {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


#crossmatch_with_reference()


# ***************************************************
#    Remove unwanted columns
# ***************************************************

def remove_unwanted_cols():
    """
    Remove unwanted columns from diagnostic file
    """

    print("")
    ut.printlog(('********** '
                 'Removing unwanted columns from diagnostic file '
                 '**********'),
                log_file)
    print("")

    cat_name = 'diagnostic_mag_temp.cat'
    cat_file = os.path.join(diagnostic_cal_path, cat_name)

    if conf['extinction_correction'].lower() != 'none':
        save_name = 'diagnostic_mag_ebvcorr.cat'
    else:
        save_name = 'diagnostic_mag.cat'

    save_file = os.path.join(diagnostic_cal_path, save_name)

    select_columns = ['RAJ2000_1', 'DEJ2000_1', 'X', 'Y', 'model_id', 'Teff',
                      'logg', 'FeH', 'aFe', 'EB_V', 'chi2', 'model_mag_shift']

    for filt in conf['external_sed_fit']:
        select_columns.append(f'{filt}')
        select_columns.append(f'{filt}_err')
        select_columns.append(f'{filt}_mod')

    rename_columns = {'RAJ2000_1': 'RAJ2000', 'DEJ2000_1': 'DEJ2000',
                      'EB_V': 'EB_V_model'}

    if not os.path.exists(save_file):

        ut.select_columns(catalog        = cat_file,
                          save_file      = save_file,
                          select_columns = select_columns,
                          rename_columns = rename_columns)

        ut.printlog(f"Created catalog {save_file}", log_file)

        ut.printlog(f"Removing temporary catalog", log_file)

        cmd = f"rm {cat_file}"
        ut.printlog(cmd, log_file)
        os.system(cmd)

    else:
        ut.printlog(f"File {save_file} already exists.", log_file)


#remove_unwanted_cols()
