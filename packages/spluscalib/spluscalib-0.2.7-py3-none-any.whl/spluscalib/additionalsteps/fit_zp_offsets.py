# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                               fit_zp_offsets.py
#             Compares two calibrations to derive zero-point offsets
# ******************************************************************************

"""
--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------
create_compare_zp_file()


--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
This script should be run individually and not within the pipeline.py script

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 fit_zp_offsets.py *field_list_file*
                           *calib1_suffix* *calib2_suffix*
                           *calib1_step* *calib2_step*
                           *calib1_path* *calib2_path*[opt]

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

suffix1 = sys.argv[2]
suffix2 = sys.argv[3]

calib1_step = sys.argv[4]
calib2_step = sys.argv[5]

calib1_path = sys.argv[6]

try:
    calib2_path = sys.argv[7]
except IndexError:
    calib2_path = calib1_path


save_path = os.path.join(calib1_path, f'zp_offset_{suffix1}-{suffix2}')
ut.makedir(save_path)

################################################################################
# Initiate log file

log_file_name = os.path.join(save_path, 'fit_zp_offsets.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(save_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Reading field list

ut.printlog("*********** Reading field list **********", log_file)

fields = ut.load_field_list(field_list_file)

ut.printlog(f"Running the script for fields:", log_file)
ut.printlog(f"{fields}", log_file)

################################################################################
# Begin script

# ***************************************************
#    Create comparison file
# ***************************************************


def create_compare_zp_file():

    """
    Creates a file with zero points from calibrations 1 and 2
    """

    print("")
    ut.printlog(('********** '
                 'Creating zero-points comparation file '
                 '**********'),
                log_file)
    print("")

    save_name = f"zps_{calib1_step}1-{calib2_step}2.csv"
    save_file = os.path.join(save_path, save_name)

    if not os.path.exists(save_file):

        fields_zps = {}

        for field in fields:

            ####################################
            # Get calibration 1 zp file name base

            if calib1_step == 'external':
                zp_file1 = os.path.join(calib1_path, field,
                                        f"Calibration_{suffix1}",
                                        'external', f'{field}_external.zp')

            elif calib1_step == 'stlocus':
                zp_file1 = os.path.join(calib1_path, field,
                                  f"Calibration_{suffix1}",
                                  'stlocus', f'{field}_external_and_stlocus.zp')

            elif calib1_step == 'internal':
                zp_file1 = os.path.join(calib1_path, field,
                                  f"Calibration_{suffix1}",
                                'internal', f'{field}_external_and_internal.zp')

            elif calib1_step == 'final':
                zp_file1 = os.path.join(calib1_path, field,
                                  f"Calibration_{suffix1}",
                                       f'{field}_final.zp')

            else:
                zp_file1 = None

            ####################################
            # Get calibration 1 zp file name base

            if calib2_step == 'external':
                zp_file2 = os.path.join(calib2_path, field,
                                  f"Calibration_{suffix2}",
                                  'external', f'{field}_external.zp')

            elif calib2_step == 'stlocus':
                zp_file2 = os.path.join(calib2_path, field,
                                  f"Calibration_{suffix2}",
                                  'stlocus', f'{field}_external_and_stlocus.zp')

            elif calib2_step == 'internal':
                zp_file2 = os.path.join(calib2_path, field,
                                  f"Calibration_{suffix2}",
                                'internal', f'{field}_external_and_internal.zp')

            elif calib2_step == 'final':
                zp_file2 = os.path.join(calib2_path, field,
                                  f"Calibration_{suffix2}",
                                       f'{field}_final.zp')

            else:
                zp_file2 = None

            ############################
            # Fill dictionary fields_zps

            fields_zps[field] = [zp_file1, zp_file2]

        ########################
        # Get comparison catalog

        ut.zp_comparison(fields_zps  = fields_zps,
                         save_file   = save_file,
                         fields_list = fields)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


create_compare_zp_file()


# ***************************************************
#    Fit zp offsets
# ***************************************************

def fit_zp_offsets():

    """
    Fits the offsets between the zero-points of two different calibrations
    """

    print("")
    ut.printlog(('********** '
                 'Fitting zero-points offsets '
                 '**********'),
                log_file)
    print("")

    zpcomp_name = f"zps_{calib1_step}1-{calib2_step}2.csv"
    zpcomp_file = os.path.join(save_path, zpcomp_name)

    save_name = f"offsets.zp"
    save_file = os.path.join(save_path, save_name)

    filters = ['SPLUS_U', 'SPLUS_F378', 'SPLUS_F395', 'SPLUS_F410',
               'SPLUS_F430', 'SPLUS_G', 'SPLUS_F515', 'SPLUS_R',
               'SPLUS_F660', 'SPLUS_I', 'SPLUS_F861', 'SPLUS_Z']

    if not os.path.exists(save_file):
        ut.zp_fit_offsets(zp_comparison_file = zpcomp_file,
                                   save_file = save_file,
                                     filters = filters)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"ZP file {save_name} already exists", log_file)


fit_zp_offsets()
