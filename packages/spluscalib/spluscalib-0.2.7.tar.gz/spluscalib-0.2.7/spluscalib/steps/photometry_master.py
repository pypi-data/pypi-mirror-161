# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                             photometry_master.py
#                      Generate photometry master catalogs
# ******************************************************************************

"""
Generates a master catalog combining the photometry of each individual field,
for each photometry mode (SExtractor single and dual modes, and dophot PSF)

The S-PLUS field is given as the first command line argument.

The set of filters, location of S-PLUS images, default SExtractor configuration
and param files, and the output path must be set in the configuration file
given as the second command line argument

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

create_master_path()
extract_photometry_only_dual_catalog()
create_master_photometry_dual()
format_photometry_master_dual()
extract_photometry_only_single_catalog()
create_master_photometry_single()
format_photometry_master_single()
extract_photometry_only_psf_catalog()
create_master_photometry_psf()
format_photometry_master_psf()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

Assumes that photometry_psf.py and/or photometry_single.py and/or
photometry_dual.py (and optionally correction_xy.py) and correction_aper has
already been run for this field.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 photometry_master.py *field_name* *config_file*

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

field_path      = os.path.join(conf['run_path'], field)
photometry_path = os.path.join(field_path, 'Photometry')

single_path         = os.path.join(photometry_path, 'single')
single_catalog_path = os.path.join(single_path, 'aper_correction')
single_master_path  = os.path.join(single_path, 'master')

dual_path         = os.path.join(photometry_path, 'dual')
dual_catalog_path = os.path.join(dual_path, 'aper_correction')
dual_master_path  = os.path.join(dual_path, 'master')

psf_path         = os.path.join(photometry_path, 'psf')
psf_catalog_path = os.path.join(psf_path, 'catalogs')
psf_xycorrection_path = os.path.join(psf_path, 'xy_correction')
psf_master_path  = os.path.join(psf_path, 'master')

images_path     = os.path.join(field_path, 'Images')

log_path        = os.path.join(photometry_path, 'logs')


################################################################################
# Initiate log file

ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'photometry_master.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(photometry_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Log configuration

ut.printlog("Single mode photometry parameters:", log_file)

master_phot_params = ['run_path', 'filters', 'path_to_images', 'inst_zp',
                      'use_weight', 'path_to_sex', 'sex_config', 'sex_param',
                      'apercorr_diameter', 'apercorr_s2ncut',
                      'apercorr_starcut', 'apercorr_max_aperture',
                      'path_to_dophot', 'dophot_config']

for param in master_phot_params:
    try:
        ut.printlog(f"{param}: {conf[param]}", log_file)
    except KeyError:
        ut.printlog(f"{param}: NONE", log_file)

################################################################################
# Begin script

# ***************************************************
#    If photometry path does not exist -> create
# ***************************************************


def create_master_path():

    print("")
    ut.printlog(('********** '
                 'Generating Master Photometry paths '
                 '**********'),
                 log_file)
    print("")

    # Create single mode master photometry path
    if 'photometry_single' in conf['run_steps']:
        ut.makedir(single_master_path)

    # Create dual mode master photometry path
    if 'photometry_dual' in conf['run_steps']:
        ut.makedir(dual_master_path)

    # Create psf mode master photometry path
    if 'photometry_psf' in conf['run_steps']:
        ut.makedir(psf_master_path)


create_master_path()

# ***************************************************
#    Prepare photometry-only dual catalog
# ***************************************************


def extract_photometry_only_dual_catalog():
    """
    Extracts only ID, RA, DEC and PStotal photometry from the dual mode
    catalogs
    """

    print("")
    ut.printlog(('********** '
                 'Creating photometry only dual mode catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:
        # Generate location of output catalog file
        catalog_name = f"sex_{field}_{filt}_dual_apercorr.fits"
        catalog_file = os.path.join(dual_catalog_path, catalog_name)

        save_file_name = f"{field}_{filt}_photometry_only_dual.fits"
        save_file = os.path.join(dual_master_path, save_file_name)

        if not os.path.exists(save_file):

            ut.extract_sex_photometry(catalog   = catalog_file,
                                      save_file = save_file,
                                      filt      = filt)

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"Catalog {save_file_name} already exists.", log_file)


if 'photometry_dual' in conf['run_steps']:
    extract_photometry_only_dual_catalog()


# ***************************************************
#    Prepare master catalog dual mode
# ***************************************************

def create_master_photometry_dual():
    """
    Combines the individual photometry-only dual mode catalogs into a
    single file
    """

    print("")
    ut.printlog(('********** '
                 'Creating photometry-only dual mode master catalog '
                 '**********'),
                log_file)
    print("")

    save_file_name = f"{field}_master_photometry_only_dual_raw.fits"
    save_file = os.path.join(dual_master_path, save_file_name)

    if not os.path.exists(save_file):

        cmd = f"java -jar {conf['path_to_stilts']} tmatchn "
        cmd += f"nin={len(conf['filters'])} "

        for i in range(len(conf['filters'])):
            filt = conf['filters'][i]

            catalog_name = f"{field}_{filt}_photometry_only_dual.fits"
            catalog_file = os.path.join(dual_master_path, catalog_name)

            cmd += f"ifmt{i+1}=fits in{i+1}={catalog_file} "
            cmd += f"values{i+1}='RA DEC' join{i+1}=always "

        cmd += f"out={save_file} ofmt=fits "
        cmd += f"matcher=sky params=1 multimode=group "

        ut.printlog(cmd, log_file)
        os.system(cmd)

    else:
        ut.printlog(f"Master catalog {save_file_name} already exists.",
                    log_file)


if 'photometry_dual' in conf['run_steps']:
    create_master_photometry_dual()


# ***************************************************
#    Format master dual
# ***************************************************

def format_photometry_master_dual():
    print("")
    ut.printlog(('********** '
                 'Formating photometry-only dual master catalog '
                 '**********'),
                log_file)
    print("")

    catalog_name = f"{field}_master_photometry_only_dual_raw.fits"
    catalog_file = os.path.join(dual_master_path, catalog_name)

    save_file_name = f"{field}_master_photometry_only_dual.fits"
    save_file = os.path.join(dual_master_path, save_file_name)

    if not os.path.exists(save_file):

        ut.format_master_photometry(catalog   = catalog_file,
                                    save_file = save_file,
                                    filters   = conf['filters'],
                                    sexmode   = 'dual',
                                    field     = field,
                                    drname    = conf['data_release_name'])

        ut.printlog(f"Created catalog {save_file}", log_file)

    else:
        ut.printlog(f"Master catalog {save_file_name} already exists.",
                    log_file)


if 'photometry_dual' in conf['run_steps']:
    format_photometry_master_dual()


# ***************************************************
#    Prepare photometry-only single catalog
# ***************************************************

def extract_photometry_only_single_catalog():
    """
    Extracts only ID, RA, DEC and PStotal photometry from the single mode
    catalogs
    """

    print("")
    ut.printlog(('********** '
                 'Creating photometry only single mode catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:
        # Generate location of output catalog file
        catalog_name = f"sex_{field}_{filt}_single_apercorr.fits"
        catalog_file = os.path.join(single_catalog_path, catalog_name)

        save_file_name = f"{field}_{filt}_photometry_only_single.fits"
        save_file = os.path.join(single_master_path, save_file_name)

        if not os.path.exists(save_file):

            ut.extract_sex_photometry(catalog   = catalog_file,
                                      save_file = save_file,
                                      filt      = filt)

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"Catalog {save_file_name} already exists.", log_file)


if 'photometry_single' in conf['run_steps']:
    extract_photometry_only_single_catalog()


# ***************************************************
#    Prepare master catalog single mode
# ***************************************************

def create_master_photometry_single():
    """
    Combines the individual photometry-only single mode catalogs into a
    single file
    """

    print("")
    ut.printlog(('********** '
                 'Creating photometry-only single mode master catalog '
                 '**********'),
                log_file)
    print("")

    save_file_name = f"{field}_master_photometry_only_single_raw.fits"
    save_file = os.path.join(single_master_path, save_file_name)

    if not os.path.exists(save_file):

        cmd = f"java -jar {conf['path_to_stilts']} tmatchn "
        cmd += f"nin={len(conf['filters'])} "

        for i in range(len(conf['filters'])):
            filt = conf['filters'][i]

            catalog_name = f"{field}_{filt}_photometry_only_single.fits"
            catalog_file = os.path.join(single_master_path, catalog_name)

            cmd += f"ifmt{i+1}=fits in{i+1}={catalog_file} "
            cmd += f"values{i+1}='RA DEC' join{i+1}=always "

        cmd += f"out={save_file} ofmt=fits "
        cmd += f"matcher=sky params=1 multimode=group "

        ut.printlog(cmd, log_file)
        os.system(cmd)

    else:
        ut.printlog(f"Master catalog {save_file_name} already exists.",
                    log_file)


if 'photometry_single' in conf['run_steps']:
    create_master_photometry_single()


# ***************************************************
#    Format master single
# ***************************************************

def format_photometry_master_single():
    print("")
    ut.printlog(('********** '
                 'Formating photometry-only single master catalog '
                 '**********'),
                log_file)
    print("")

    catalog_name = f"{field}_master_photometry_only_single_raw.fits"
    catalog_file = os.path.join(single_master_path, catalog_name)

    save_file_name = f"{field}_master_photometry_only_single.fits"
    save_file = os.path.join(single_master_path, save_file_name)

    if not os.path.exists(save_file):

        ut.format_master_photometry(catalog=catalog_file,
                                    save_file=save_file,
                                    filters=conf['filters'],
                                    sexmode   = 'single',
                                    field     = field,
                                    drname    = conf['data_release_name'])

        ut.printlog(f"Created catalog {save_file}", log_file)

    else:
        ut.printlog(f"Master catalog {save_file_name} already exists.",
                    log_file)


if 'photometry_single' in conf['run_steps']:
    format_photometry_master_single()


# ***************************************************
#    Prepare photometry-only psf catalog
# ***************************************************

def extract_photometry_only_psf_catalog():
    """
    Extracts only ID, RA, DEC and PStotal photometry from the single mode
    catalogs
    """

    print("")
    ut.printlog(('********** '
                 'Creating photometry only psf catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:
        # Generate location of output catalog file
        catalog_name = f"{field}_{filt}_psf.cat"
        catalog_file = os.path.join(psf_catalog_path, catalog_name)

        save_file_name = f"{field}_{filt}_photometry_only_psf.fits"
        save_file = os.path.join(psf_master_path, save_file_name)

        if not os.path.exists(save_file):

            ut.extract_psf_photometry(catalog   = catalog_file,
                                      save_file = save_file,
                                      filt      = filt)

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(f"Catalog {save_file_name} already exists.", log_file)


if 'photometry_psf' in conf['run_steps']:
    extract_photometry_only_psf_catalog()


# ***************************************************
#    Prepare master catalog psf
# ***************************************************

def create_master_photometry_psf():
    """
    Combines the individual photometry-only psf catalogs into a single file
    """

    print("")
    ut.printlog(('********** '
                 'Creating photometry-only psf master catalog '
                 '**********'),
                log_file)
    print("")

    save_file_name = f"{field}_master_photometry_only_psf_raw.fits"
    save_file = os.path.join(psf_master_path, save_file_name)

    if not os.path.exists(save_file):

        cmd = f"java -jar {conf['path_to_stilts']} tmatchn "
        cmd += f"nin={len(conf['filters'])} "

        for i in range(len(conf['filters'])):
            filt = conf['filters'][i]

            catalog_name = f"{field}_{filt}_photometry_only_psf.fits"
            catalog_file = os.path.join(psf_master_path, catalog_name)

            cmd += f"ifmt{i+1}=fits in{i+1}={catalog_file} "
            cmd += f"values{i+1}='RA DEC' join{i+1}=always "

        cmd += f"out={save_file} ofmt=fits "
        cmd += f"matcher=sky params=1 multimode=group "

        ut.printlog(cmd, log_file)
        os.system(cmd)

    else:
        ut.printlog(f"Master catalog {save_file_name} already exists.",
                    log_file)


if 'photometry_psf' in conf['run_steps']:
    create_master_photometry_psf()


# ***************************************************
#    Format master psf
# ***************************************************

def format_photometry_master_psf():
    print("")
    ut.printlog(('********** '
                 'Formating photometry-only psf master catalog '
                 '**********'),
                log_file)
    print("")

    catalog_name = f"{field}_master_photometry_only_psf_raw.fits"
    catalog_file = os.path.join(psf_master_path, catalog_name)

    save_file_name = f"{field}_master_photometry_only_psf.fits"
    save_file = os.path.join(psf_master_path, save_file_name)

    if not os.path.exists(save_file):

        ut.format_master_photometry(catalog=catalog_file,
                                    save_file=save_file,
                                    filters=conf['filters'],
                                    sexmode   = 'psf',
                                    field     = field,
                                    drname    = conf['data_release_name'])

        ut.printlog(f"Created catalog {save_file}", log_file)

    else:
        ut.printlog(f"Master catalog {save_file_name} already exists.",
                    log_file)


if 'photometry_psf' in conf['run_steps']:
    format_photometry_master_psf()
