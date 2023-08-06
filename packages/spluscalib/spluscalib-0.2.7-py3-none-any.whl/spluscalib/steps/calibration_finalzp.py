# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                            calibration_finalzp.py
#      Combines the zero-points of all calibration steps into a final file
# ******************************************************************************

"""
Combines the zero-points of all calibration steps into a final zp file

The S-PLUS field is given as the first command line argument. Configurations
are set in the config file, given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------
copy_offset_zp_file()
calculate_final_zp()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

Assumes that at least calibration_external.py, and possibly calibration_stloc.py
and calibration_internal.py, have already been run for this field.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 calibration_finalzp.py *field_name* *config_file*

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

gaiascale_cal_path  = os.path.join(calibration_path, 'gaiascale')
gaiascale_plot_path = os.path.join(gaiascale_cal_path, 'plots')


log_path = os.path.join(calibration_path, 'logs')


################################################################################
# Initiate log file

ut.makedir(calibration_path)
ut.makedir(internal_cal_path)
ut.makedir(internal_plot_path)
ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'calibration_finalzp.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(calibration_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")


################################################################################
# Begin script

# ***************************************************
#    Combine all zps
# ***************************************************

def calculate_final_zp():
    """
    Combines all calibration .zp files to create a final zp file for the field
    """

    print("")
    ut.printlog(('********** '
                 'Combining all calibration .zp files '
                 '**********'),
                log_file)
    print("")

    zp_file_list = []

    save_name = f"{field}_final.zp"
    save_file = os.path.join(calibration_path, save_name)

    if not os.path.exists(save_file):
        # Add external .zp
        ext_zp_name = f"{field}_external.zp"
        ext_zp_file = os.path.join(external_cal_path, ext_zp_name)

        zp_file_list.append(ext_zp_file)

        # Add stellar locus .zp
        if 'calibration_stloc' in conf['run_steps']:
            stloc_zp_name = f"{field}_stlocus.zp"
            stloc_zp_file = os.path.join(stloc_cal_path, stloc_zp_name)

            zp_file_list.append(stloc_zp_file)

        # Add internal .zp
        if 'calibration_internal' in conf['run_steps']:
            int_zp_name = f"{field}_internal.zp"
            int_zp_file = os.path.join(internal_cal_path, int_zp_name)

            zp_file_list.append(int_zp_file)

        # Add gaia scale .zp
        if 'calibration_gaiascale' in conf['run_steps']:
            gaiascale_zp_name = f"{field}_gaiascale_splus.zp"
            gaiascale_zp_file = os.path.join(gaiascale_cal_path,
                                             gaiascale_zp_name)

            zp_file_list.append(gaiascale_zp_file)

        filters = []
        for filt in conf['filters']:
            filters.append(f"SPLUS_{filt}")

        # Combine zero-points
        ut.zp_add(zp_file_list = zp_file_list,
                  save_file    = save_file,
                  filters      = filters,
                  inst_zp      = conf['inst_zp'])

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"File {save_name} already exists", log_file)


calculate_final_zp()
