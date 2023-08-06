# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                        combine_calibration_catalogs.py
#         Combines intermediare calibration catalogs for a list of fields
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

################################################################################
# Initiate log file

log_file_name = os.path.join(save_path, 'combine_calibration_catalogs.log')
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

################################################################################
# Begin script

# ***************************************************
#    Combine instrumental catalogs
# ***************************************************


def concatenate_instrumental_catalogs():

    """
    Concatenates calibration catalogs with S-PLUS instrumental magnitudes
    """

    print("")
    ut.printlog(('********** '
                 'Concatenating instrumental magnitudes '
                 '**********'),
                 log_file)
    print("")

    cat_name = '{field}_mag_inst.cat'
    cat_file = os.path.join(conf['save_path'], '{field}',
                                 f'Calibration_{suffix}', 'external',
                                 cat_name)

    # Start save name
    save_name = 'concat_mag_inst.cat'
    save_file = os.path.join(save_path, save_name)

    if not os.path.exists(save_file):

        # Create list of field catalogs
        catalogs_list = []

        for field in fields:
            catalogs_list.append(cat_file.format(field=field))

        ut.concat_data(files_list = catalogs_list,
                       save_file  = save_file)

        ut.printlog(f"Created catalog {save_file}", log_file)

    else:
        ut.printlog(f"File {save_name} already exists", log_file)


concatenate_instrumental_catalogs()


# ***************************************************
#    Combine external calibration catalogs
# ***************************************************

def concatenate_external_calib_catalogs():

    """
    Concatenates calibration catalogs after the external calibration step
    has been run
    """

    print("")
    ut.printlog(('********** '
                 'Concatenating external calibrated magnitudes '
                 '**********'),
                 log_file)
    print("")

    cat_name = '{field}_mag_ext.cat'
    cat_file = os.path.join(conf['save_path'], '{field}',
                            f'Calibration_{suffix}', 'external',
                            cat_name)

    # Start save name
    save_name = 'concat_mag_ext.cat'
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


concatenate_external_calib_catalogs()


# ***************************************************
#    Combine stellar locus calibration catalogs
# ***************************************************

def concatenate_stlocus_calib_catalogs():

    """
    Concatenates calibration catalogs after the stellar locus calibration step
    has been run
    """

    print("")
    ut.printlog(('********** '
                 'Concatenating stellar locus calibrated magnitudes '
                 '**********'),
                 log_file)
    print("")

    cat_name = '{field}_mag_stlocus.cat'
    cat_file = os.path.join(conf['save_path'], '{field}',
                            f'Calibration_{suffix}', 'stlocus',
                            cat_name)

    # Start save name
    save_name = 'concat_mag_stlocus.cat'
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


if 'calibration_stloc' in conf['run_steps']:
    concatenate_stlocus_calib_catalogs()


# ***************************************************
#    Combine internal calibration catalogs
# ***************************************************

def concatenate_internal_calib_catalogs():

    """
    Concatenates calibration catalogs after the internal calibration step
    has been run
    """

    print("")
    ut.printlog(('********** '
                 'Concatenating internal calibrated magnitudes '
                 '**********'),
                 log_file)
    print("")

    cat_name = '{field}_mag_int.cat'
    cat_file = os.path.join(conf['save_path'], '{field}',
                            f'Calibration_{suffix}', 'internal',
                            cat_name)

    # Start save name
    save_name = 'concat_mag_int.cat'
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


if 'calibration_internal' in conf['run_steps']:
    concatenate_internal_calib_catalogs()


# ***************************************************
#    Combine gaiascale calibration catalogs
# ***************************************************

def concatenate_gaiascale_calib_catalogs():

    """
    Concatenates calibration catalogs after the gaia scale calibration step
    has been run
    """

    print("")
    ut.printlog(('********** '
                 'Concatenating gaia scale calibrated magnitudes '
                 '**********'),
                 log_file)
    print("")

    cat_name = "{field}_mag_gaiascale.cat"
    cat_file = os.path.join(conf['save_path'], '{field}',
                            f'Calibration_{suffix}', 'gaiascale',
                            cat_name)

    # Start save name
    save_name = 'concat_mag_gaiascale.cat'
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


if 'calibration_gaiascale' in conf['run_steps']:
    concatenate_gaiascale_calib_catalogs()


# ***************************************************
#    Combine diagnostic calibration catalogs
# ***************************************************

def concatenate_diagnostic_calib_catalogs():

    """
    Concatenates calibration catalogs after the diagnostic calibration step
    has been run
    """

    print("")
    ut.printlog(('********** '
                 'Concatenating diagnostic magnitudes '
                 '**********'),
                 log_file)
    print("")

    cat_name = '{field}_diagnostic_mag.fits'
    cat_file = os.path.join(conf['save_path'], '{field}',
                            f'Calibration_{suffix}', 'diagnostic',
                            cat_name)

    # Start save name
    save_name = 'concat_mag_diagnostic.cat'
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


if 'calibration_diagnostic' in conf['run_steps']:
    concatenate_diagnostic_calib_catalogs()
