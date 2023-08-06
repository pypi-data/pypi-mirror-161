# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                               photometry_psf.py
#                       psf photometry using dophot_splus
# ******************************************************************************

"""
Runs dophot_splus for one S-PLUS field and a list of filters.

The S-PLUS field is given as the first command line argument.

The set of filters, location of S-PLUS images, default dophot configuration,
and the output path must be set in the configuration file
given as the second command line argument

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

create_photometry_path()
copy_images_to_dophot_path()
generate_tuneup_files()
run_dophot()
delete_images_from_dophot_path()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 photometry_psf.py *field_name* *config_file*

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
psf_path        = os.path.join(photometry_path, 'psf')
dophot_path     = os.path.join(psf_path, 'dophot')
catalogs_path   = os.path.join(psf_path, 'catalogs')

images_path     = os.path.join(field_path, 'Images')

log_path        = os.path.join(photometry_path, 'logs')

################################################################################
# Create Photometry directory

ut.makedir(field_path)
ut.makedir(photometry_path)
ut.makedir(log_path)

################################################################################
# Initiate log file

log_file_name = os.path.join(log_path, 'photometry_psf.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(photometry_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Log configuration

ut.printlog("PSF photometry parameters:", log_file)

psf_params = ['run_path', 'filters', 'path_to_images',
              'path_to_dophot', 'dophot_config']

for param in psf_params:
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
                 'Generating PSF Photometry paths '
                 '**********'),
                 log_file)
    print("")

    # Create single mode photometry path
    ut.makedir(psf_path)

    ut.makedir(dophot_path)

    ut.makedir(catalogs_path)


create_photometry_path()

# ***************************************************
#    Copy images to dophot path
# ***************************************************


def copy_images_to_dophot_path():

    """
    Copying images to dophot path
    """

    print("")
    ut.printlog(('********** '
                 'Copying images to dophot path '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        # Get location of image file
        image_name      = f"{field}_{filt}_swp.fits"
        image_file_from = os.path.join(images_path, image_name)
        image_file_to   = os.path.join(dophot_path, image_name)

        if not os.path.exists(image_file_to):

            # Copy image file from source location
            cmd = f"cp {image_file_from} {image_file_to}"
            ut.printlog("$ "+cmd, log_file)
            os.system(cmd)

        else:
            ut.printlog(f"Image {image_name} already in dophot directory.",
                        log_file)


copy_images_to_dophot_path()

# ***************************************************
#    Generate dophot-splus tuneup files
# ***************************************************


def generate_tuneup_files():

    """
    Generate psf tuneup files for all filters
    """

    print("")
    ut.printlog(('********** '
                 'Generating PSF Photometry tuneup files '
                 '**********'),
                 log_file)
    print("")

    # Generate tuneup for each filter
    for filt in conf['filters']:

        # Generate location of config file
        conf_file_name = f"{field}_{filt}_swp.tuneup"
        save_file = os.path.join(dophot_path, conf_file_name)

        # Generate location of output catalog file
        catalog_name = f"{field}_{filt}_swp.sum"
        catalog_file = os.path.join(dophot_path, catalog_name)

        # Get location of image file
        image_name = f"{field}_{filt}_swp.fits"
        image_file = os.path.join(images_path, image_name)

        if not os.path.exists(save_file):

            ut.get_dophot_config(image_in    = image_file,
                                 objects_out = catalog_file,
                                 config_file = save_file,
                          apercorr_max_aperture = conf['apercorr_max_aperture'])

            ut.printlog(("Generated PSF tuneup file for field "
                         f"{field}, filter {filt}"), log_file)

        else:
            ut.printlog(("PSF tuneup file already obtained for field "
                         f"{field}, filter {filt}"), log_file)

    # Copy paramdefault file to dophot directory
    paramdefault_from = conf['dophot_config']
    paramdefault_to   = os.path.join(dophot_path, 'paramdefault')

    cmd = f'cp {paramdefault_from} {paramdefault_to}'
    ut.printlog("$ "+cmd, log_file)
    os.system(cmd)


generate_tuneup_files()

# ***************************************************
#    Run dophot-splus
# ***************************************************


def run_dophot():

    """
    Run dophot-splus to extract PSF photometry from all filters
    """

    print("")
    ut.printlog(('********** '
                 'Running dophot-splus '
                 '**********'),
                 log_file)
    print("")

    # Get current directory (to return after running dophot)
    cwd = os.getcwd()

    # Change working directory to dophot directory
    os.chdir(dophot_path)

    for filt in conf['filters']:

        catalog_name = f"{field}_{filt}_swp.sum"
        catalog_file = os.path.join(dophot_path, catalog_name)

        if not os.path.exists(catalog_file):

            # Get location of tuneup
            tuneup_file_name = f"{field}_{filt}_swp.tuneup"

            # Run dophot
            dophot_location = os.path.join(conf['path_to_dophot'],
                                           'dophot_splus')

            cmd = f"{dophot_location} {tuneup_file_name}"
            ut.printlog("$ "+cmd, log_file)
            os.system(cmd)

        else:
            ut.printlog(("PSF photometry already obtained for field "
                         f"{field}, filter {filt}"), log_file)

    # Go back to current working directory
    os.chdir(cwd)


run_dophot()


# ***************************************************
#    Format output catalogs
# ***************************************************


def format_dophot_catalogs():

    """
    Formats dophot-splus .sum files into ascii catalogs
    """

    print("")
    ut.printlog(('********** '
                 'Formating dophot catalogs '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        dophot_catalog_name = f"{field}_{filt}_swp.sum"
        dophot_catalog_file = os.path.join(dophot_path, dophot_catalog_name)

        formated_catalog_name = f"{field}_{filt}_psf.cat"
        formated_catalog_file = os.path.join(catalogs_path,
                                             formated_catalog_name)

        image_name = f"{field}_{filt}_swp.fz"
        image_file = os.path.join(images_path, image_name)

        if not os.path.exists(formated_catalog_file):

            ut.format_dophot_catalog(catalog_in  = dophot_catalog_file,
                                     catalog_out = formated_catalog_file,
                                     image       = image_file,
                                     filt        = filt,
                                     field       = field,
                                     drname      = conf['data_release_name'])

        else:
            ut.printlog(("Dophot catalog already formated for field "
                         f"{field}, filter {filt}"), log_file)


format_dophot_catalogs()

# ***************************************************
#    Delete images from dophot path
# ***************************************************


def delete_images_from_dophot_path():

    """
    Deletes images from dophot path
    """

    print("")
    ut.printlog(('********** '
                 'Deleting images from dophot path '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        # Get location of image file
        image_name = f"{field}_{filt}_swp.fits"
        image_file = os.path.join(dophot_path, image_name)

        if os.path.exists(image_file):

            # Copy image file from source location
            cmd = f"rm {image_file}"
            ut.printlog("$ "+cmd, log_file)
            os.system(cmd)

        else:
            ut.printlog((f"Image {image_name} already deleted from "
                          "dophot directory."), log_file)


delete_images_from_dophot_path()

ut.printlog("COMPLETED PSF PHOTOMETRY", log_file)


# ***************************************************
#    PSF diagnostic plots
# ***************************************************

def psf_diagnostic_plots():

    """
    Makes psf diagnostic plots of the resulting catalogs
    """

    print("")
    ut.printlog(('********** '
                 'Making diagnostic plots for PSF photometry'
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        # Generate location of output catalog file
        catalog_name = f"{field}_{filt}_psf.cat"
        catalog_file = os.path.join(catalogs_path, catalog_name)

        save_name = f"{field}_{filt}_psf.png"
        save_file = os.path.join(catalogs_path, save_name)

        if not os.path.exists(save_file):

            ut.plot_dophot_diagnostic(catalog   = catalog_file,
                                      save_file = save_file,
                                      filt      = filt)

            ut.printlog(f"Created file {save_file}", log_file)

        else:
            ut.printlog(("Diagnostic plots already made for field "
                         f"{field}, filter {filt}"), log_file)


psf_diagnostic_plots()

ut.printlog("COMPLETED PSF PHOTOMETRY", log_file)