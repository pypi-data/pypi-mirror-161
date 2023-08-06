# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                               correction_xy.py
#                  ad-hoc zero-point inhomogeneity correction
# ******************************************************************************


"""
Applies ad-hoc zero-point inhomogeneity corrections to the aperture photometry
catalogues.

The correction maps are saved as numpy .npy arrays, with bins defined in the
configuration file

The S-PLUS field is given as the first command line argument.

The set of filters, location of correction maps and definition of the bins,
must be set in the configuration file given as the second command line argument

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

create_xycorr_paths()
apply_xycorr_single_catalogs()
apply_xycorr_dual_catalogs()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

Assumes that photometry_single.py and/or photometry_dual.py has already been
run for this field.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 correction_xy.py *field_name* *config_file*

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

field_path           = os.path.join(conf['run_path'], field)
photometry_path      = os.path.join(field_path, 'Photometry')

dual_path            = os.path.join(photometry_path, 'dual')
dual_catalogs_path   = os.path.join(dual_path, 'catalogs')
dual_xycorr_path     = os.path.join(dual_path, 'xy_correction')

single_path          = os.path.join(photometry_path, 'single')
single_catalogs_path = os.path.join(single_path, 'catalogs')
single_xycorr_path   = os.path.join(single_path, 'xy_correction')

psf_path          = os.path.join(photometry_path, 'psf')
psf_catalogs_path = os.path.join(psf_path, 'catalogs')
psf_xycorr_path   = os.path.join(psf_path, 'xy_correction')

log_path             = os.path.join(photometry_path, 'logs')

################################################################################
# Initiate log file

ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'xy_correction.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(photometry_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Log configuration

ut.printlog("PSF photometry parameters:", log_file)

single_mode_params = ['sex_XY_correction', 'XY_correction_maps_path',
                      'XY_correction_xbins', 'XY_correction_ybins']

for param in single_mode_params:
    try:
        ut.printlog(f"{param}: {conf[param]}", log_file)
    except KeyError:
        ut.printlog(f"{param}: NONE", log_file)


################################################################################
# Begin script

# ***************************************************
#    Create paths
# ***************************************************

def create_xycorr_paths():

    print("")
    ut.printlog(('********** '
                 'Generating XY corrections paths '
                 '**********'),
                 log_file)
    print("")

    # Create single mode photometry path
    if 'photometry_dual' in conf['run_steps']:
        ut.makedir(dual_xycorr_path)

    if 'photometry_single' in conf['run_steps']:
        ut.makedir(single_xycorr_path)

    if 'photometry_psf' in conf['run_steps']:
        ut.makedir(psf_xycorr_path)

create_xycorr_paths()


# ***************************************************
#    Apply XY correction to single mode catalogs
# ***************************************************


def apply_xycorr_single_catalogs():

    print("")
    ut.printlog(('********** '
                 'Applying XY corrections to single mode catalogs '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f"sex_{field}_{filt}_single.fits"
        catalog      = os.path.join(single_catalogs_path, catalog_name)

        xycorr_catalog_name = f"sex_{field}_{filt}_single_xycorr.fits"
        save_file           = os.path.join(single_xycorr_path,
                                           xycorr_catalog_name)

        xycorr_map_name = f"SPLUS_{filt}_offsets_grid.npy"
        xycorr_map_file = os.path.join(conf['XY_correction_maps_path'],
                                       xycorr_map_name)

        if not os.path.exists(save_file):

            ut.apply_xy_correction(catalog   = catalog,
                                   save_file = save_file,
                                   map_file  = xycorr_map_file,
                                   xbins     = conf['XY_correction_xbins'],
                                   ybins     = conf['XY_correction_ybins'])

            ut.printlog(("Generated single mode XY corrected catalog for field "
                         f"{field}, filter {filt}"), log_file)

        else:
            ut.printlog(("Single mode XY corrected catalog already created for "
                         f"field {field}, filter {filt}"), log_file)


if 'photometry_single' in conf['run_steps']:
    apply_xycorr_single_catalogs()


# ***************************************************
#    Apply XY correction to dual mode catalogs
# ***************************************************


def apply_xycorr_dual_catalogs():
    print("")
    ut.printlog(('********** '
                 'Applying XY corrections to dual mode catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f"sex_{field}_{filt}_dual.fits"
        catalog = os.path.join(dual_catalogs_path, catalog_name)

        xycorr_catalog_name = f"sex_{field}_{filt}_dual_xycorr.fits"
        save_file = os.path.join(dual_xycorr_path,
                                 xycorr_catalog_name)

        xycorr_map_name = f"SPLUS_{filt}_offsets_grid.npy"
        xycorr_map_file = os.path.join(conf['XY_correction_maps_path'],
                                       xycorr_map_name)

        if not os.path.exists(save_file):

            ut.apply_xy_correction(catalog=catalog,
                                   save_file=save_file,
                                   map_file=xycorr_map_file,
                                   xbins=conf['XY_correction_xbins'],
                                   ybins=conf['XY_correction_ybins'])

            ut.printlog(("Generated dual mode XY corrected catalog for field "
                         f"{field}, filter {filt}"), log_file)

        else:
            ut.printlog(("Dual mode XY corrected catalog already created for "
                         f"field {field}, filter {filt}"), log_file)


if 'photometry_dual' in conf['run_steps']:
    apply_xycorr_dual_catalogs()


# ***************************************************
#    Apply XY correction to psf mode catalogs
# ***************************************************


def apply_xycorr_psf_catalogs():
    print("")
    ut.printlog(('********** '
                 'Applying XY corrections to psf catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f"{field}_{filt}_psf.cat"
        catalog = os.path.join(psf_catalogs_path, catalog_name)

        xycorr_catalog_name = f"{field}_{filt}_psf_xycorr.cat"
        save_file = os.path.join(psf_xycorr_path,
                                 xycorr_catalog_name)

        xycorr_map_name = f"SPLUS_{filt}_offsets_grid.npy"
        xycorr_map_file = os.path.join(conf['XY_correction_maps_path'],
                                       xycorr_map_name)

        if not os.path.exists(save_file):

            ut.apply_xy_correction_psf(catalog=catalog,
                                       save_file=save_file,
                                       map_file=xycorr_map_file,
                                       xbins=conf['XY_correction_xbins'],
                                       ybins=conf['XY_correction_ybins'])

            ut.printlog(("Generated psf XY corrected catalog for field "
                         f"{field}, filter {filt}"), log_file)

        else:
            ut.printlog(("PSF XY corrected catalog already created for "
                         f"field {field}, filter {filt}"), log_file)


if 'photometry_psf' in conf['run_steps']:
    apply_xycorr_psf_catalogs()