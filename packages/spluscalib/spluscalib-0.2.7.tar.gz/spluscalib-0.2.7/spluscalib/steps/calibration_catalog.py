# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                             calibration_catalog.py
#            Applies the final zero-point to the photometry catalogs
# ******************************************************************************

"""
Generates photometric calibrated catalogs from the final zero-points and the
photometry output tables

The S-PLUS field is given as the first command line argument. Configurations
are set in the config file, given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------
copy_splus_psf_inst_catalog()
apply_final_zero_points_to_psf()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

Assumes that at least calibration_finalzp.py has already been run for this field

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 calibration_catalog.py *field_name* *config_file*

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

catalogs_path = os.path.join(calibration_path, field)
catalogs_path_psf    = os.path.join(catalogs_path, 'psf')
catalogs_path_single = os.path.join(catalogs_path, 'single')
catalogs_path_dual   = os.path.join(catalogs_path, 'dual')

photometry_path = os.path.join(field_path, 'Photometry')

psf_path              = os.path.join(photometry_path, 'psf')
psf_catalog_path      = os.path.join(psf_path, 'catalogs')
psf_xycorrection_path = os.path.join(psf_path, 'xy_correction')
psf_master_path       = os.path.join(psf_path, 'master')
psf_id_path  = os.path.join(psf_path, 'id')

single_path         = os.path.join(photometry_path, 'single')
single_catalog_path = os.path.join(single_path, 'aper_correction')
single_master_path  = os.path.join(single_path, 'master')
single_id_path  = os.path.join(single_path, 'id')

dual_path         = os.path.join(photometry_path, 'dual')
dual_catalog_path = os.path.join(dual_path, 'aper_correction')
dual_master_path  = os.path.join(dual_path, 'master')
dual_detection_path = os.path.join(dual_path, 'detection')
dual_id_path  = os.path.join(dual_path, 'id')

log_path = os.path.join(calibration_path, 'logs')

################################################################################
# Initiate log file


ut.makedir(catalogs_path)
ut.makedir(log_path)

# Check for photometry folders
has_photometry_single = "photometry_single" in conf["run_steps"]
has_photometry_dual   = "photometry_dual" in conf["run_steps"]
has_photometry_psf    = "photometry_psf" in conf["run_steps"]

has_photometry_single &= os.path.exists(single_catalog_path)
has_photometry_dual   &= os.path.exists(dual_catalog_path)
has_photometry_psf    &= os.path.exists(psf_catalog_path)

if has_photometry_single:
    ut.makedir(catalogs_path_single)

if has_photometry_dual:
    ut.makedir(catalogs_path_dual)

if has_photometry_psf:
    ut.makedir(catalogs_path_psf)

log_file_name = os.path.join(log_path, 'catalog.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(calibration_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Begin script

# ***************************************************
#    Make single mode filter catalogs
# ***************************************************


def generate_singlemode_filter_catalogues():

    """
    Generates single mode calibrated filter catalogues
    """

    print("")
    ut.printlog(('********** '
                 'Generating single mode calibrated filter catalogues '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f'sex_{field}_{filt}_single_withIDs.fits'
        catalog_file = os.path.join(single_id_path, catalog_name)

        zp_name = f'{field}_final.zp'
        zp_file = os.path.join(calibration_path, zp_name)

        save_name = f'{field}_{filt}_single.fits'
        save_file = os.path.join(catalogs_path_single, save_name)

        if not os.path.exists(save_file):

            ut.sexcatalog_apply_calibration(catalog_file = catalog_file,
                                            zp_file      = zp_file,
                                            save_file    = save_file,
                                            filter_name  = filt,
                                            field        = field,
                                            sex_mag_zp   = conf['inst_zp'],
                                            mode         = 'single',
                                      calibration_flag=conf['calibration_flag'],
                                      calibration_name=conf['calibration_name'],
                              extinction_maps_path=conf['extinction_maps_path'],
                            extinction_correction=conf['extinction_correction'])

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"Catalog {save_name} already exists", log_file)


if has_photometry_single:
    generate_singlemode_filter_catalogues()


# ***************************************************
#    Make dual mode filter catalogs
# ***************************************************

def generate_dualmode_filter_catalogues():

    """
    Generates dual mode calibrated filter catalogues
    """

    print("")
    ut.printlog(('********** '
                 'Generating dual mode calibrated filter catalogues '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f'sex_{field}_{filt}_dual_withIDs.fits'
        catalog_file = os.path.join(dual_id_path, catalog_name)

        zp_name = f'{field}_final.zp'
        zp_file = os.path.join(calibration_path, zp_name)

        save_name = f'{field}_{filt}_dual.fits'
        save_file = os.path.join(catalogs_path_dual, save_name)

        if not os.path.exists(save_file):

            ut.sexcatalog_apply_calibration(catalog_file = catalog_file,
                                            zp_file      = zp_file,
                                            save_file    = save_file,
                                            filter_name  = filt,
                                            field        = field,
                                            sex_mag_zp   = conf['inst_zp'],
                                            mode         = 'dual',
                                            drname=conf["data_release_name"],
                                      calibration_flag=conf['calibration_flag'],
                                      calibration_name=conf['calibration_name'])

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"Catalog {save_name} already exists", log_file)


if has_photometry_dual:
    generate_dualmode_filter_catalogues()


# ***************************************************
#    Make dual mode filter catalogs
# ***************************************************

def generate_detection_catalogue():

    """
    Generates dual mode calibrated filter catalogues
    """

    print("")
    ut.printlog(('********** '
                 'Generating dual mode detection catalogue '
                 '**********'),
                 log_file)
    print("")

    detection_name = f'sex_{field}_detection_withIDs.fits'
    detection_file = os.path.join(dual_id_path, detection_name)

    save_name = f'{field}_detection_dual.fits'
    save_file = os.path.join(catalogs_path_dual, save_name)

    if not os.path.exists(save_file):

        ut.sexcatalog_detection(detection_file   = detection_file,
                                save_file        = save_file,
                                calibration_flag = conf['calibration_flag'],
                                field            = field,
                              extinction_maps_path=conf['extinction_maps_path'],
                          extinction_correction = conf['extinction_correction'],
                                calibration_name=conf['calibration_name'])

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


if has_photometry_dual:
    generate_detection_catalogue()


# ***************************************************
#    Make PSF filter catalogs
# ***************************************************


def generate_psf_filter_catalogues():

    """
    Generates PSF calibrated filter catalogues
    """

    print("")
    ut.printlog(('********** '
                 'Generating PSF calibrated filter catalogues '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f'{field}_{filt}_psf_withIDs.csv'
        catalog_file = os.path.join(psf_id_path, catalog_name)

        zp_name = f'{field}_final.zp'
        zp_file = os.path.join(calibration_path, zp_name)

        save_name = f'{field}_{filt}_psf.fits'
        save_file = os.path.join(catalogs_path_psf, save_name)

        if not os.path.exists(save_file):

            ut.psfcatalog_apply_calibration(catalog_file = catalog_file,
                                            zp_file      = zp_file,
                                            save_file    = save_file,
                                            filter_name  = filt,
                                            field        = field,
                                            inst_mag_zp  = conf['inst_zp'],
                                      calibration_flag=conf['calibration_flag'],
                                      calibration_name=conf['calibration_name'],
                              extinction_maps_path=conf['extinction_maps_path'],
                            extinction_correction=conf['extinction_correction'])

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"Catalog {save_name} already exists", log_file)


if has_photometry_psf:
    generate_psf_filter_catalogues()


# ***************************************************
#    Make single mode 32-aper filter catalogs
# ***************************************************

def generate_singlemode_32aper_filter_catalogues():

    """
    Generates single mode 32-aper calibrated filter catalogues
    """

    print("")
    ut.printlog(('********** '
                 'Generating single mode 32-aper calibrated filter catalogues '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f'sex_{field}_{filt}_single_withIDs.fits'
        catalog_file = os.path.join(single_id_path, catalog_name)

        zp_name = f'{field}_final.zp'
        zp_file = os.path.join(calibration_path, zp_name)

        save_name = f'{field}_{filt}_single_aper.fits'
        save_file = os.path.join(catalogs_path_single, save_name)

        if not os.path.exists(save_file):

            ut.sexcatalog_apply_calibration_aper(catalog_file = catalog_file,
                                            zp_file      = zp_file,
                                            save_file    = save_file,
                                            filter_name  = filt,
                                            sex_mag_zp   = conf['inst_zp'],
                                            mode         = 'single',
                                            field        = field,
                                        drname=conf["data_release_name"])

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"Catalog {save_name} already exists", log_file)


if has_photometry_single:
    if conf["create_aper_catalog"]:
        generate_singlemode_32aper_filter_catalogues()


# ***************************************************
#    Make dual mode 32-aper filter catalogs
# ***************************************************

def generate_dualmode_32aper_filter_catalogues():

    """
    Generates dual mode 32-aper calibrated filter catalogues
    """

    print("")
    ut.printlog(('********** '
                 'Generating dual mode 32-aper calibrated filter catalogues '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f'sex_{field}_{filt}_dual_withIDs.fits'
        catalog_file = os.path.join(dual_id_path, catalog_name)

        zp_name = f'{field}_final.zp'
        zp_file = os.path.join(calibration_path, zp_name)

        save_name = f'{field}_{filt}_dual_aper.fits'
        save_file = os.path.join(catalogs_path_dual, save_name)

        if not os.path.exists(save_file):

            ut.sexcatalog_apply_calibration_aper(catalog_file = catalog_file,
                                            zp_file      = zp_file,
                                            save_file    = save_file,
                                            filter_name  = filt,
                                            sex_mag_zp   = conf['inst_zp'],
                                            mode         = 'dual',
                                            field=field,
                                            drname=conf["data_release_name"])

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"Catalog {save_name} already exists", log_file)


if has_photometry_dual:
    if conf["create_aper_catalog"]:
        generate_dualmode_32aper_filter_catalogues()


# ***************************************************
#    Extract VAC features from detection
# ***************************************************

def extract_vac_features_from_dual_mode():

    """
    Extracts VACs features from detection catalog
    """

    print("")
    ut.printlog(('********** '
                 'Extracting VAC features from detection catalog '
                 '**********'),
                 log_file)
    print("")

    for filt in ["detection"] + conf['filters']:

        if filt == "detection":
            catalog_name = f'{field}_detection_dual.fits'
            catalog_file = os.path.join(catalogs_path_dual, catalog_name)

            save_name = f'{field}_detection_dual_VAC_features.fits'
            save_file = os.path.join(catalogs_path_dual, save_name)
        else:
            catalog_name = f'{field}_{filt}_dual.fits'
            catalog_file = os.path.join(catalogs_path_dual, catalog_name)

            save_name = f'{field}_{filt}_dual_VAC_features.fits'
            save_file = os.path.join(catalogs_path_dual, save_name)

        future_name = f'{field}_dual_VAC_features.fits'
        future_file = os.path.join(catalogs_path_dual, future_name)

        if not os.path.exists(save_file) and not os.path.exists(future_file):
            ut.extract_vac_features(catalog = catalog_file,
                                    save_file = save_file,
                                    filt = filt)

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"Catalog {save_name} already exists", log_file)


if has_photometry_dual:
    extract_vac_features_from_dual_mode()


# ***************************************************
#    Combine VAC features
# ***************************************************

def combine_vac_features():
    print("")
    ut.printlog(('********** '
                 'Combining VAC features '
                 '**********'),
                log_file)
    print("")

    save_name = f'{field}_dual_VAC_features.fits'
    save_file = os.path.join(catalogs_path_dual, save_name)

    if not os.path.exists(save_file):

        cmd  = f"java -jar {conf['path_to_stilts']} tmatchn "
        cmd += f"nin={1+len(conf['filters'])} matcher=exact "
        cmd += f"multimode=group "

        catalog_name = f'{field}_detection_dual_VAC_features.fits'
        catalog = os.path.join(catalogs_path_dual, catalog_name)

        valuesj = f"PHOT_ID_dual"

        cmd += f"in1={catalog} ifmt1=fits values1={valuesj} "
        cmd += f"join1=always "

        j = 2
        for filt in conf['filters']:
            catalog_name = f'{field}_{filt}_dual_VAC_features.fits'
            catalog = os.path.join(catalogs_path_dual, catalog_name)

            valuesj = f"PHOT_ID_dual"

            cmd += f"in{j}={catalog} ifmt{j}=fits values{j}={valuesj} "
            cmd += f"join{j}=always "
            j += 1

        cmd += f"out={save_file} ofmt=fits"

        ut.printlog(cmd, log_file)
        os.system(cmd)

        ut.printlog(f"Created file {save_file}", log_file)

    else:
        ut.printlog(f"Catalog {save_name} already exists", log_file)


if 'photometry_dual' in conf['run_steps']:
    combine_vac_features()


# ***************************************************
#    Remove temporary VAC files
# ***************************************************

def remove_temporary_vac_features():
    print("")
    ut.printlog(('********** '
                 'Removing temporary VAC features '
                 '**********'),
                log_file)
    print("")

    vac_name = f'{field}_dual_VAC_features.fits'
    vac_file = os.path.join(catalogs_path_dual, vac_name)

    if os.path.exists(vac_file):

        catalog_name = f'{field}_detection_dual_VAC_features.fits'
        catalog = os.path.join(catalogs_path_dual, catalog_name)

        cmd = f"rm {catalog} "
        ut.printlog(cmd, log_file)
        os.system(cmd)

        for filt in conf['filters']:
            catalog_name = f'{field}_{filt}_dual_VAC_features.fits'
            catalog = os.path.join(catalogs_path_dual, catalog_name)

            cmd = f"rm {catalog} "
            ut.printlog(cmd, log_file)
            os.system(cmd)


if 'photometry_dual' in conf['run_steps']:
    remove_temporary_vac_features()
