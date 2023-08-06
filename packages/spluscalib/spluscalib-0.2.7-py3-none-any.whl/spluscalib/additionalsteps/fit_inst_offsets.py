# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                              fit_inst_offsets.py
#      Compares two instrumental photometries to derive zero-point offsets
# ******************************************************************************

"""
--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
This script should be run individually and not within the pipeline.py script

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 fit_zp_offsets.py *field_list_file* *calib1_path*

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
calib_path = sys.argv[2]

save_path = os.path.join(calib_path, f'zp_offset_inst')
ut.makedir(save_path)

path_to_stilts = os.path.join(spluscalib_path, "external_programs",
                              "stilts.jar")

filters = ["SPLUS_U", "SPLUS_F378", "SPLUS_F395", "SPLUS_F410",
           "SPLUS_F430", "SPLUS_G", "SPLUS_F515", "SPLUS_R",
           "SPLUS_F660", "SPLUS_I", "SPLUS_F861", "SPLUS_Z"]

################################################################################
# Initiate log file

log_file_name = os.path.join(save_path, 'fit_inst_offsets.log')
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
#    Crossmatching photometry files
# ***************************************************

def crossmatch_dual_psf_master_photometry():

    print("")
    ut.printlog(('********** '
                 'Crossmatching dual mode and psf master photometries '
                 '**********'),
                log_file)
    print("")

    for field in fields:

        save_name = f"{field}_master_photometry_dual_psf.fits"
        save_file = os.path.join(save_path, save_name)

        if not os.path.exists(save_file):
            dual_name = f"{field}_master_photometry_only_dual.fits"
            dual_file = os.path.join(calib_path, field, "Photometry", "dual",
                                     "master", dual_name)

            psf_name = f"{field}_master_photometry_only_psf.fits"
            psf_file = os.path.join(calib_path, field, "Photometry", "psf",
                                     "master", psf_name)

            values1 = "RAJ2000 DEJ2000"
            values2 = "RAJ2000 DEJ2000"

            cmd  = f"java -jar {path_to_stilts} tmatch2 "
            cmd += f"matcher=sky join=1and2 params=3 "
            cmd += f"in1={dual_file} ifmt1=fits values1='{values1}' "
            cmd += f"in2={psf_file} ifmt2=fits values2='{values2}' "
            cmd += f"out={save_file} ofmt=fits"

            ut.printlog(cmd, log_file)
            os.system(cmd)

        else:
            ut.printlog(f"File {save_file} already exists.", log_file)


crossmatch_dual_psf_master_photometry()


# ***************************************************
#    Estimating field dual_psf offsets
# ***************************************************

def estimating_dual_psf_offsets_by_field():

    print("")
    ut.printlog(('********** '
                 'Estimating dual/psf offsets for each field '
                 '**********'),
                log_file)
    print("")

    for field in fields:

        master_name = f"{field}_master_photometry_dual_psf.fits"
        master_file = os.path.join(save_path, master_name)

        save_name = f"{field}_offset_dual_psf.zp"
        save_file = os.path.join(save_path, save_name)

        if not os.path.exists(save_file):
            ut.estimate_field_dual_psf_offset(catalog   = master_file,
                                              save_file = save_file,
                                              filters   = filters)

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"File {save_file} already exists.", log_file)


estimating_dual_psf_offsets_by_field()


# ***************************************************
#    Estimating field dual_psf offsets
# ***************************************************

def estimating_overall_dual_psf_offsets():

    print("")
    ut.printlog(('********** '
                 'Overall dual/psf offsets'
                 '**********'),
                log_file)
    print("")

    save_name = f"all_offset_dual_psf.zp"
    save_file = os.path.join(save_path, save_name)

    if not os.path.exists(save_file):
        offset_files = []

        for field in fields:
            field_offset_name = f"{field}_offset_dual_psf.zp"
            field_offset_file = os.path.join(save_path,
                                             field_offset_name)

            offset_files.append(field_offset_file)

        ut.estimate_overall_dual_psf_offset(offset_files = offset_files,
                                            save_file = save_file,
                                            filters = filters)

    else:
        ut.printlog(f"File {save_file} already exists.", log_file)


estimating_overall_dual_psf_offsets()
