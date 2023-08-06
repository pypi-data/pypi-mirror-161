# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                             calibration_stloc.py
#            Runs the stellar locus calibration step of the pipeline
# ******************************************************************************

"""
Obtains the stellar locus calibration zero-points by comparing the stellar
locus (with a single not calibrated magnitude) to a reference stellar locus

The S-PLUS field is given as the first command line argument. Configurations
are set in the config file, given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

get_and_plot_stellar_locus_zps()
apply_stellar_locus_zero_points()
combine_external_and_stlocus_zps()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

Assumes that calibration_external.py has already been run for this field.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 calibration_stloc.py *field_name* *config_file*

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

field_path = os.path.join(conf['run_path'], field)

suffix = ut.calibration_suffix(conf)
calibration_path  = os.path.join(field_path, f'Calibration_{suffix}')

external_cal_path = os.path.join(calibration_path, 'external')
external_plot_path = os.path.join(external_cal_path, 'plots')

stloc_cal_path = os.path.join(calibration_path, 'stlocus')
stloc_plot_path = os.path.join(stloc_cal_path, 'plots')

log_path = os.path.join(calibration_path, 'logs')


################################################################################
# Initiate log file

ut.makedir(stloc_cal_path)
ut.makedir(stloc_plot_path)

log_file_name = os.path.join(log_path, 'calibration_stloc.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(calibration_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")


################################################################################
# Begin script

def get_and_plot_stellar_locus_zps():

    """
    Obtain zero-points using the stellar locus technique. Also saves the plots.
    """

    print("")
    ut.printlog(('********** '
                 'Getting stellar locus ZPs '
                 '**********'),
                 log_file)
    print("")

    catalog_name = f"{field}_mag_ext.cat"
    catalog_file = os.path.join(external_cal_path, catalog_name)

    save_name = f"{field}_stlocus_tmp.zp"
    save_file = os.path.join(stloc_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.zp_estimate_stlocus(catalog   = catalog_file,
                               save_file = save_file,
                               filts_to_get_zp = conf['stellar_locus_fit'],
                               stlocus_ref_cat = conf['stellar_locus_reference'],
                               filts_color_ref = conf['stellar_locus_color_ref'],
                               filt_ref = conf['stellar_locus_filt_ref'],
                               color_range = conf['stellar_locus_color_range'],
                               nbins = conf['stellar_locus_N_bins'],
                               plot_path = stloc_plot_path,
                               field = field)

        ut.printlog(f"Zero-points saved in {save_file}", log_file)

    else:
        ut.printlog((f"Stellar locus ZPs already obtained and saved in "
                     f"{save_name}"), log_file)


get_and_plot_stellar_locus_zps()


# ***************************************************
#    Add offset to S-PLUS reference calibration
# ***************************************************

def add_offset_to_splus_reference_calibration():
    """
    Adds offset to S-PLUS reference calibration
    """

    if conf['offset_include_after'].lower() == "stloc":
        print("")
        ut.printlog(('********** '
                     'Adding offset to S-PLUS reference calibration '
                     '**********'),
                    log_file)
        print("")

    stloc_zp_name = f"{field}_stlocus_tmp.zp"
    stloc_zp_file = os.path.join(stloc_cal_path, stloc_zp_name)

    save_name = f"{field}_stlocus.zp"
    save_file = os.path.join(stloc_cal_path, save_name)

    if not os.path.exists(save_file):

        if conf['offset_include_after'].lower() == "stloc":
            offset_zp_name = f'offset_refcalib.zp'
            offset_zp_file = os.path.join(stloc_cal_path, offset_zp_name)

            cmd = f"cp {conf['offset_to_splus_refcalib']} {offset_zp_file}"
            ut.printlog(cmd, log_file)
            os.system(cmd)

            zp_file_list = [stloc_zp_file, offset_zp_file]

            filters = []
            for filt in conf['filters']:
                filters.append(f"SPLUS_{filt}")

            # Combine zero-points
            ut.zp_add(zp_file_list=zp_file_list,
                      save_file=save_file,
                      filters=filters,
                      inst_zp=0)

        else:
            cmd = f"cp {stloc_zp_file} {save_file}"
            os.system(cmd)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"File {save_name} already exists", log_file)


add_offset_to_splus_reference_calibration()


# ***************************************************
#    Apply Zero Points
# ***************************************************

def apply_stellar_locus_zero_points():

    """
    Applies stellar locus zero-points to mag_ext catalog
    """

    print("")
    ut.printlog(('********** '
                 'Applying stellar locus zero-points to mag_ext catalog '
                 '**********'),
                 log_file)
    print("")

    catalog_name = f"{field}_mag_ext.cat"
    catalog_file = os.path.join(external_cal_path, catalog_name)

    zp_name = f"{field}_stlocus.zp"
    zp_file = os.path.join(stloc_cal_path, zp_name)

    save_name = f"{field}_mag_stlocus.cat"
    save_file = os.path.join(stloc_cal_path, save_name)

    if not os.path.exists(save_file):
        ut.zp_apply(catalog   = catalog_file,
                    save_file = save_file,
                    zp_file   = zp_file)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


apply_stellar_locus_zero_points()


# ***************************************************
#    Combine external and st_locus zps
# ***************************************************


def combine_external_and_stlocus_zps():

    """
    Combines the external and stlocus .zp files into a single .zp file
    """

    print("")
    ut.printlog(('********** '
                 'Combining external and stlocus .zp files '
                 '**********'),
                 log_file)
    print("")

    ext_zp_name = f"{field}_external.zp"
    ext_zp_file = os.path.join(external_cal_path, ext_zp_name)

    stlocus_zp_name = f"{field}_stlocus.zp"
    stlocus_zp_file = os.path.join(stloc_cal_path, stlocus_zp_name)

    save_name = f"{field}_external_and_stlocus.zp"
    save_file = os.path.join(stloc_cal_path, save_name)

    filters = []
    for filt in conf['filters']:
        filters.append(f"SPLUS_{filt}")

    if not os.path.exists(save_file):

        ut.zp_add(zp_file_list = [ext_zp_file, stlocus_zp_file],
                  save_file = save_file,
                  filters   = filters)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


combine_external_and_stlocus_zps()
