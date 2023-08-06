# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                             photometry_master.py
#                      Generate photometry master catalogs
# ******************************************************************************

"""
Crossmatches S-PLUS with the reference catalog

The S-PLUS field is given as the first command line argument. Configurations
are set in the config file, given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

copy_splus_master_photometry()
dowload_references()
crossmatch_all_references()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

Assumes that photometry_master.py has already been run for this field.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 crossmatch.py *field_name* *config_file*

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
calibration_path = os.path.join(field_path, f'Calibration_{suffix}')
crossmatch_path  = os.path.join(field_path, 'Crossmatch')

photometry_path = os.path.join(field_path, 'Photometry')
images_path     = os.path.join(field_path, 'Images')

log_path = os.path.join(crossmatch_path, 'logs')


################################################################################
# Initiate log file

ut.makedir(crossmatch_path)
ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'crossmatch.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(crossmatch_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")


################################################################################
# Log configuration

ut.printlog("Reference crossmatch parameters:", log_file)

crossmatch_params = ['run_path', 'filters', 'calibration_photometry',
                     'reference_catalog']

for param in crossmatch_params:
    try:
        ut.printlog(f"{param}: {conf[param]}", log_file)
    except KeyError:
        ut.printlog(f"{param}: NONE", log_file)

################################################################################
# Begin script

# ***************************************************
#    Copy splus master photometry catalog
# ***************************************************


def copy_splus_master_photometry():

    """
    Copy S-PLUS photometry to the crossmatch path
    """

    print("")
    ut.printlog(('********** '
                 'Copying S-PLUS master photometry '
                 '**********'),
                 log_file)
    print("")

    calib_phot = conf['calibration_photometry']

    catalog_name = f"{field}_master_photometry_only_{calib_phot}.fits"
    catalog_file = os.path.join(photometry_path, calib_phot, 'master',
                                catalog_name)

    save_name = f'{field}_SPLUS_{calib_phot}_tmp.fits'
    save_file = os.path.join(crossmatch_path, save_name)

    if not os.path.exists(save_file):

        cmd = f"cp {catalog_file} {save_file}"
        ut.printlog(cmd, log_file)
        os.system(cmd)

    else:
        ut.printlog(f"Catalog {save_file} already exists", log_file)


copy_splus_master_photometry()


# ***************************************************
#    Add photometry offset
# ***************************************************

def adding_instrumental_offset():

    calib_phot = conf['calibration_photometry']

    catalog_name = f'{field}_SPLUS_{calib_phot}_tmp.fits'
    catalog_file = os.path.join(crossmatch_path, catalog_name)

    save_name = f'{field}_SPLUS_{calib_phot}.fits'
    save_file = os.path.join(crossmatch_path, save_name)

    if not os.path.exists(save_file):
        if conf["offset_inst_mag"].lower() != "none":

            print("")
            ut.printlog(('********** '
                         'Adding instrumental photometry offset '
                         '**********'),
                        log_file)
            print("")

            ut.add_inst_offset(catalog     = catalog_file,
                               offset_file = conf["offset_inst_mag"],
                               save_file   = save_file)

        else:
            cmd = f"cp {catalog_file} {save_file}"
            ut.printlog(cmd, log_file)
            os.system(cmd)

    else:
        ut.printlog(f"Catalog {save_file} already exists", log_file)


adding_instrumental_offset()

# ***************************************************
#    Download reference catalogs
# ***************************************************


def dowload_references():

    """
    Downloads reference catalogs covering the field's region
    """

    print("")
    ut.printlog(('********** '
                 'Downloading reference catalogs '
                 '**********'),
                 log_file)
    print("")

    for ref in conf['reference_catalog']:

        ut.printlog(f"Trying to download {ref}", log_file)

        ref_catalog = f'{field}_{ref}.fits'
        save_file = os.path.join(crossmatch_path, ref_catalog)

        # S-PLUS image to extract header info
        filt = conf['filters'][-1]
        image_name = f'{field}_{filt}_swp.fz'
        image_file = os.path.join(images_path, image_name)

        #fieldID_name =  f'{field}_FIELD_ID.fits'
        #fieldID_file = os.path.join(photometry_path, fieldID_name)

        if not os.path.exists(save_file):

            ut.download_reference(image = image_file,
                                  reference = ref,
                                  save_file = save_file)

            ut.printlog(f"Downloaded {ref} catalog for field {field}", log_file)

        else:
            ut.printlog(f"Reference {ref} already downloaded for field {field}",
                        log_file)

        print("")


dowload_references()


# ***************************************************
#    Download GAIA DR2 for the field
# ***************************************************

def dowload_gaiadr2():

    """
    Downloads GAIA DR2 catalogs covering the field's region
    """

    print("")
    ut.printlog(('********** '
                 'Downloading GAIA DR2 catalog '
                 '**********'),
                 log_file)
    print("")

    ref_catalog = f'{field}_GAIADR2_VEGA.fits'
    save_file = os.path.join(crossmatch_path, ref_catalog)

    # S-PLUS image to extract header info
    filt = conf['filters'][-1]
    image_name = f'{field}_{filt}_swp.fz'
    image_file = os.path.join(images_path, image_name)

    #fieldID_name = f'{field}_FIELD_ID.fits'
    #fieldID_file = os.path.join(photometry_path, fieldID_name)

    if not os.path.exists(save_file):

        ut.download_reference(image = image_file,
                              reference = 'GAIADR2',
                              save_file = save_file)

        ut.printlog(f"Downloaded Gaia DR2 catalog for field {field}", log_file)

    else:
        ut.printlog(f"Gaia DR2 already downloaded for field {field}",
                    log_file)

    print("")


dowload_gaiadr2()


# ***************************************************
#    Convert GAIA to AB magnitudes
# ***************************************************

def convert_gaia_VEGA_to_AB():

    """
    Converts Gaia magnitudes to AB system
    """

    print("")
    ut.printlog(('********** '
                 'Converting Gaia magnitudes to AB system '
                 '**********'),
                 log_file)
    print("")

    catalog_name = f'{field}_GAIADR2_VEGA.fits'
    catalog_file = os.path.join(crossmatch_path, catalog_name)

    save_name = f'{field}_GAIADR2.fits'
    save_file = os.path.join(crossmatch_path, save_name)

    if not os.path.exists(save_file):

        ut.convert_gaia_Vega2AB(gaia_catalog = catalog_file,
                                save_file    = save_file)

        ut.printlog(f"Converted Gaia DR2 magnitudes to AB for field {field}",
                    log_file)

    else:
        ut.printlog(f"Gaia DR2 already converted to AB for field {field}",
                    log_file)

    print("")


convert_gaia_VEGA_to_AB()

# ***************************************************
#    Crossmatch between references if more than one
# ***************************************************

def crossmatch_all_references():

    """
    Combines S-PLUS and reference catalogs
    """

    print("")
    ut.printlog(('********** '
                 'Crossmatching all reference catalogs '
                 '**********'),
                 log_file)
    print("")

    # Get photometry mode used for calibration
    calib_phot = conf['calibration_photometry']

    # Get number of reference catalogs
    nref = len(conf['reference_catalog'])

    # Include S-PLUS catalog in the tmatchn
    splus_cat = f'{field}_SPLUS_{calib_phot}.fits'
    splus_cat_file = os.path.join(crossmatch_path, splus_cat)

    # Include GAIA DR2
    gaia_cat = f'{field}_GAIADR2.fits'
    gaia_cat_file = os.path.join(crossmatch_path, gaia_cat)

    # Start save name
    save_name = ut.crossmatch_catalog_name(field, conf)
    save_file = os.path.join(crossmatch_path, save_name)

    if not os.path.exists(save_file):

        # Start tmatchn cmd
        cmd = f"java -jar {conf['path_to_stilts']} tmatchn "
        cmd += f"nin={nref + 2} "

        cmd += f"ifmt1=fits in1={splus_cat_file} "
        cmd += f"values1='RAJ2000 DEJ2000' join1=match "

        cmd += f"ifmt2=fits in2={gaia_cat_file} "
        cmd += f"values2='GAIADR2_RAJ2000 GAIADR2_DEJ2000' join2=match "

        for i in range(nref):
            ref = conf['reference_catalog'][i]

            ref_cat = f'{field}_{ref}.fits'
            ref_cat_file = os.path.join(crossmatch_path, ref_cat)

            values = f"{ref}_RAJ2000 {ref}_DEJ2000"
            cmd += f"ifmt{i + 3}=fits in{i + 3}={ref_cat_file} "
            cmd += f"values{i + 3}='{values}' join{i + 3}=match "

        cmd += f"out={save_file} ofmt=fits "
        cmd += f"matcher=sky params=3 multimode=group "

        ut.printlog(cmd, log_file)
        os.system(cmd)

        ut.printlog(f"Created catalog {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


crossmatch_all_references()


# ***************************************************
#    Correct extinction
# ***************************************************

def correct_extinction_crossmatched_catalog():
    """
    Generates crossmatched catalog with extinction correction
    """

    print("")
    ut.printlog(('********** '
                 'Applying exctinction correction '
                 '**********'),
                 log_file)
    print("")

    ###############################
    # Get crossmatched catalog file
    cmatch_name = ut.crossmatch_catalog_name(field, conf)
    cmatch_file = os.path.join(crossmatch_path, cmatch_name)

    ##################
    # Apply correction
    correction = conf['extinction_correction']
    ebv_map_path = conf['extinction_maps_path']

    save_file = cmatch_file.replace(".fits", f"_ebvcorr_{correction}.fits")

    if not os.path.exists(save_file):
        ut.correct_extinction(catalog = cmatch_file,
                              save_file = save_file,
                              correction = correction,
                              ebv_maps_path = ebv_map_path)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Extinction corrected catalog already exists", log_file)


if conf['extinction_correction'].lower() != 'none':
    correct_extinction_crossmatched_catalog()
