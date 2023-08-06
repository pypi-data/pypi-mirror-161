# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                             photometry_single.py
#                      aperture photometry in single mode
# ******************************************************************************

"""
Runs SExtractor in single mode for one S-PLUS field and a list of filters.

The S-PLUS field is given as the first command line argument.

The set of filters, location of S-PLUS images, default SExtractor configuration
and param files, and the output path must be set in the configuration file
given as the second command line argument

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

create_photometry_path()
generate_sexconfig_files()
run_sex_single()
single_diagnostic_plots()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 photometry_single.py *field_name* *config_file*

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
single_path     = os.path.join(photometry_path, 'single')
sexconf_path    = os.path.join(single_path, 'sexconf')
catalogs_path   = os.path.join(single_path, 'catalogs')

images_path     = os.path.join(field_path, 'Images')

log_path        = os.path.join(photometry_path, 'logs')

################################################################################
# Create Photometry directory

ut.makedir(field_path)
ut.makedir(photometry_path)
ut.makedir(log_path)

################################################################################
# Initiate log file

log_file_name = os.path.join(log_path, 'photometry_single.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(photometry_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Log configuration

ut.printlog("Single mode photometry parameters:", log_file)

single_mode_params = ['run_path', 'filters', 'path_to_images', 'inst_zp',
                      'use_weight', 'path_to_sex', 'sex_config', 'sex_param',
                      'sex_XY_correction', 'XY_correction_maps_path',
                      'XY_correction_xbins', 'XY_correction_ybins',
                      ]

for param in single_mode_params:
    try:
        ut.printlog(f"{param}: {conf[param]}", log_file)
    except KeyError:
        ut.printlog(f"{param}: NONE", log_file)

################################################################################
# Begin script

# ***************************************************
#    If photometry path does not exist -> create
# ***************************************************


def create_photometry_path():

    print("")
    ut.printlog(('********** '
                 'Generating Single Photometry paths '
                 '**********'),
                 log_file)
    print("")

    # Create single mode photometry path
    ut.makedir(single_path)

    # Create single mode sexconf path
    ut.makedir(sexconf_path)

    # Create single mode catalogs path
    ut.makedir(catalogs_path)


create_photometry_path()


# ***************************************************
#    Generate SExconfig files
# ***************************************************

def generate_sexconfig_files():

    """
    Generate single mode sexconfig file for all filters
    """

    print("")
    ut.printlog(('********** '
                 'Generating Single Photometry config files '
                 '**********'),
                 log_file)
    print("")

    # Default SExconfig and SExparam files
    default_sexconfig = conf['sex_config']
    default_sexparam  = conf['sex_param']

    # Generate configuration for each filter
    for filt in conf['filters']:

        # Generate location of config file
        conf_file_name = f"{field}_{filt}_single.sex"
        save_file = os.path.join(sexconf_path, conf_file_name)

        # Generate location of output catalog file
        catalog_name = f"sex_{field}_{filt}_single.fits"
        catalog_file = os.path.join(catalogs_path, catalog_name)

        # Get location of image file
        image_name = f"{field}_{filt}_swp.fits"
        image_file = os.path.join(images_path, image_name)

        if not os.path.exists(save_file):

            ut.get_sex_config(save_file = save_file,
                              default_sexconfig = default_sexconfig,
                              default_sexparam  = default_sexparam,
                              catalog_file      = catalog_file,
                              image_file        = image_file,
                              inst_zp           = conf['inst_zp'],
                              path_to_sex       = conf['path_to_sex'],
                              use_weight        = conf['use_weight'],
                              mode              = 'single')

            ut.printlog(("Generated single mode sexconfig for field "
                         f"{field}, filter {filt}"), log_file)

        else:
            ut.printlog(("Single mode sexconfig already obtained for field "
                         f"{field}, filter {filt}"), log_file)

    # Copy sexparam file to field config directory (for proper documentation)
    cmd = f'cp {default_sexparam} {sexconf_path}'
    ut.printlog("$ "+cmd, log_file)
    os.system(cmd)


generate_sexconfig_files()

# ***************************************************
#    Run SExtractor in Single Mode
# ***************************************************


def run_sex_single():

    """
    Run SExtractor in Single mode for all filters
    """

    print("")
    ut.printlog(('********** '
                 'Running SeX on single mode '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f"sex_{field}_{filt}_single.fits"
        catalog_file = os.path.join(catalogs_path, catalog_name)

        if not os.path.exists(catalog_file):

            # Get location of image file
            image_name = f"{field}_{filt}_swp.fits"
            image_file = os.path.join(images_path, image_name)

            # Get location of sexconfig file
            conf_file_name = f"{field}_{filt}_single.sex"
            sexconf_file = os.path.join(sexconf_path, conf_file_name)

            # Run SExtractor
            sex_location = os.path.join(conf['path_to_sex'], 'src', 'sex')

            cmd = f"{sex_location} {image_file} -c {sexconf_file}"
            ut.printlog("$ "+cmd, log_file)
            os.system(cmd)

        else:
            ut.printlog(("Single mode photometry already obtained for field "
                         f"{field}, filter {filt}"), log_file)


run_sex_single()


# ***************************************************
#    Single diagnostic plots
# ***************************************************

def single_diagnostic_plots():

    """
    Makes diagnostic plots of the resulting catalogs
    """

    print("")
    ut.printlog(('********** '
                 'Making diagnostic plots for single mode photometry'
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        # Generate location of output catalog file
        catalog_name = f"sex_{field}_{filt}_single.fits"
        catalog_file = os.path.join(catalogs_path, catalog_name)

        save_name = f"{field}_{filt}_single.png"
        save_file = os.path.join(catalogs_path, save_name)

        conf_file_name = f"{field}_{filt}_single.sex"
        sexconf_file = os.path.join(sexconf_path, conf_file_name)

        if not os.path.exists(save_file):

            ut.plot_sex_diagnostic(catalog   = catalog_file,
                                   save_file = save_file,
                                   s2ncut    = conf['apercorr_s2ncut'],
                                   starcut   = conf['apercorr_starcut'],
                                   sexconf   = sexconf_file,
                                   filt      = filt)

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(("Diagnostic plots already made for field "
                         f"{field}, filter {filt}"), log_file)


single_diagnostic_plots()

ut.printlog("COMPLETED SINGLE MODE PHOTOMETRY", log_file)
