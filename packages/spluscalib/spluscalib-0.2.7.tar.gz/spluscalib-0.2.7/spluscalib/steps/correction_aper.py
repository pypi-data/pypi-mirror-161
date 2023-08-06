# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                              correction_aper.py
#          Creates aperture corrected magnitudes in SExtractor catalogs
# ******************************************************************************


"""
Estimates and applies the aperture correction for the 3-arcsec diameter fixed
circular aperture.

Aperture corrections are obtained from the growth curve of each filter, derived
from the 32 fixed circular apertures given in the sextractor config file

The S-PLUS field is given as the first command line argument.

The set of filters, aperture to be corrected, cut in signal-to-noise and cut
in SExtractor CLASS_STAR parameter must be set in the configuration file
given as the second command line argument

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

create_apercorr_paths()
obtain_single_mode_aper_corr()
plot_single_mode_growth_curve()
apply_single_mode_aperture_correction()
obtain_dual_mode_aper_corr()
plot_dual_mode_growth_curve()
apply_dual_mode_aperture_correction()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

Assumes that photometry_single.py and/or photometry_dual.py (and optionally
correction_xy.py) has already been run for this field.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 correction_aper.py *field_name* *config_file*

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
dual_apercorr_path   = os.path.join(dual_path, 'aper_correction')
dual_sexconf_path    = os.path.join(dual_path, 'sexconf')

single_path          = os.path.join(photometry_path, 'single')
single_catalogs_path = os.path.join(single_path, 'catalogs')
single_xycorr_path   = os.path.join(single_path, 'xy_correction')
single_apercorr_path = os.path.join(single_path, 'aper_correction')
single_sexconf_path  = os.path.join(single_path, 'sexconf')

log_path             = os.path.join(photometry_path, 'logs')

################################################################################
# Initiate log file

ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'aper_correction.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(photometry_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")


################################################################################
# Log configuration

ut.printlog("PSF photometry parameters:", log_file)

single_mode_params = ['apercorr_diameter', 'apercorr_s2ncut',
                      'apercorr_starcut', 'apercorr_max_aperture']

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


def create_apercorr_paths():

    print("")
    ut.printlog(('********** '
                 'Generating aperture corrections paths '
                 '**********'),
                 log_file)
    print("")

    # Create single mode photometry path
    if 'photometry_dual' in conf['run_steps']:
        ut.makedir(dual_apercorr_path)
        ut.makedir(os.path.join(dual_apercorr_path, 'growth_curves'))

    if 'photometry_single' in conf['run_steps']:
        ut.makedir(single_apercorr_path)
        ut.makedir(os.path.join(single_apercorr_path, 'growth_curves'))


create_apercorr_paths()


# ***************************************************
#    Single Mode Aperture Correction
# ***************************************************

def obtain_single_mode_aper_corr():

    print("")
    ut.printlog(('********** '
                 'Estimating single mode aperture corrections '
                 '**********'),
                 log_file)
    print("")

    # Generate aperture correction file name
    aper_corr_name = f"{field}_apercorr_single.zp"
    save_file = os.path.join(single_apercorr_path, aper_corr_name)

    if not os.path.exists(save_file):

        # create file
        with open(save_file + 'temp', 'w') as f:
            f.write("")

        # Estimate aperture correction for each filter
        for filt in conf['filters']:

            # Get photometry catalog
            if conf['sex_XY_correction']:
                catalog_name = f"sex_{field}_{filt}_single_xycorr.fits"
                catalog = os.path.join(single_xycorr_path, catalog_name)
            else:
                catalog_name = f"sex_{field}_{filt}_single.fits"
                catalog = os.path.join(single_catalogs_path, catalog_name)

            # Get filt sexconfig file
            conf_file_name = f"{field}_{filt}_single.sex"
            sexconf_file = os.path.join(single_sexconf_path, conf_file_name)

            # Calculate filter aperture correction
            ut.obtain_aperture_correction(catalog=catalog,
                                          filt=filt,
                                          sexconf=sexconf_file,
                                          save_file=save_file + 'temp',
                                          aperture=conf['apercorr_diameter'],
                                          s2ncut=conf['apercorr_s2ncut'],
                                          starcut=conf['apercorr_starcut'],
                                          verbose=True,
                                    max_aperture=conf['apercorr_max_aperture'])

            ut.printlog((f"Estimated aperture correction for field {field}, "
                         f"filter {filt} (single mode)"), log_file)

    else:
        ut.printlog((f"Aperture correction already estimated for field "
                     f"{field} (single mode)"), log_file)

    # After finishing, remove temp file
    if not os.path.exists(save_file):
        cmd = f"mv {save_file+'temp'} {save_file}"
        ut.printlog(cmd, log_file)
        os.system(cmd)


if 'photometry_single' in conf['run_steps']:
    obtain_single_mode_aper_corr()


# ***************************************************
#    Plot growth curve - single mode
# ***************************************************


def plot_single_mode_growth_curve():

    print("")
    ut.printlog(('********** '
                 'Plotting single mode growth curves '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        plot_name = f'growth_curve_{field}_{filt}_single.png'
        save_file = os.path.join(single_apercorr_path, 'growth_curves',
                                 plot_name)

        if not os.path.exists(save_file):

            # Get photometry catalog
            if conf['sex_XY_correction']:
                catalog_name = f"sex_{field}_{filt}_single_xycorr.fits"
                catalog = os.path.join(single_xycorr_path, catalog_name)
            else:
                catalog_name = f"sex_{field}_{filt}_single.fits"
                catalog = os.path.join(single_catalogs_path, catalog_name)

            # Get filt sexconfig file
            conf_file_name = f"{field}_{filt}_single.sex"
            sexconf_file = os.path.join(single_sexconf_path, conf_file_name)

            # Calculate filter aperture correction
            ut.growth_curve_plotter(catalog=catalog,
                                    filt=filt,
                                    sexconf=sexconf_file,
                                    save_file=save_file,
                                    aperture=conf['apercorr_diameter'],
                                    s2ncut=conf['apercorr_s2ncut'],
                                    starcut=conf['apercorr_starcut'],
                                    verbose=True,
                                    max_aperture=conf['apercorr_max_aperture'])

            ut.printlog((f"Plotted growth curve for field {field}, "
                         f"filter {filt} (single mode)"), log_file)

        else:
            ut.printlog((f"Growth curve already plotted for field "
                         f"{field}, filter {filt}  (single mode)"), log_file)


if 'photometry_single' in conf['run_steps']:
    plot_single_mode_growth_curve()


# ***************************************************
#    Apply aperture correction - single mode
# ***************************************************


def apply_single_mode_aperture_correction():

    print("")
    ut.printlog(('********** '
                 'Applying single mode aperture correction '
                 '**********'),
                 log_file)
    print("")

    aper_corr_name = f"{field}_apercorr_single.zp"
    aper_corr_file = os.path.join(single_apercorr_path, aper_corr_name)

    for filt in conf['filters']:

        save_name = f'sex_{field}_{filt}_single_apercorr.fits'
        save_file = os.path.join(single_apercorr_path, save_name)

        if not os.path.exists(save_file):

            # Get photometry catalog
            if conf['sex_XY_correction']:
                catalog_name = f"sex_{field}_{filt}_single_xycorr.fits"
                catalog = os.path.join(single_xycorr_path, catalog_name)
            else:
                catalog_name = f"sex_{field}_{filt}_single.fits"
                catalog = os.path.join(single_catalogs_path, catalog_name)

            # Get filt sexconfig file
            conf_file_name = f"{field}_{filt}_single.sex"
            sexconf_file = os.path.join(single_sexconf_path, conf_file_name)

            # Calculate filter aperture correction
            ut.apply_aperture_correction(catalog       = catalog,
                                         filt          = filt,
                                         sexconf       = sexconf_file,
                                         aperture = conf['apercorr_diameter'],
                                         apercorr_file = aper_corr_file,
                                         save_file     = save_file,
                                         field         = field,
                                         drname   = conf['data_release_name'],
                                         sexmode       = 'single')

            ut.printlog((f"Applied aperture correction for field {field}, "
                         f"filter {filt} (single mode)"), log_file)

        else:
            ut.printlog((f"Aperture correction already applied for field "
                         f"{field}, filter {filt} (single mode)"), log_file)


if 'photometry_single' in conf['run_steps']:
    apply_single_mode_aperture_correction()


# ***************************************************
#    Dual Mode Aperture Correction
# ***************************************************

def obtain_dual_mode_aper_corr():

    print("")
    ut.printlog(('********** '
                 'Estimating dual mode aperture corrections '
                 '**********'),
                 log_file)
    print("")

    # Generate aperture correction file name
    aper_corr_name = f"{field}_apercorr_dual.zp"
    save_file = os.path.join(dual_apercorr_path, aper_corr_name)

    if not os.path.exists(save_file):

        # create file
        with open(save_file + 'temp', 'w') as f:
            f.write("")

        # Estimate aperture correction for each filter
        for filt in conf['filters']:

            # Get photometry catalog
            if conf['sex_XY_correction']:
                catalog_name = f"sex_{field}_{filt}_dual_xycorr.fits"
                catalog      = os.path.join(dual_xycorr_path, catalog_name)
            else:
                catalog_name = f"sex_{field}_{filt}_dual.fits"
                catalog      = os.path.join(dual_catalogs_path, catalog_name)

            # Get filt sexconfig file
            conf_file_name = f"{field}_{filt}_dual.sex"
            sexconf_file   = os.path.join(dual_sexconf_path, conf_file_name)

            # Calculate filter aperture correction
            ut.obtain_aperture_correction(catalog   = catalog,
                                          filt      = filt,
                                          sexconf   = sexconf_file,
                                          save_file = save_file+'temp',
                                          aperture  = conf['apercorr_diameter'],
                                          s2ncut    = conf['apercorr_s2ncut'],
                                          starcut   = conf['apercorr_starcut'],
                                          verbose=True,
                                     max_aperture=conf['apercorr_max_aperture'])

            ut.printlog((f"Estimated aperture correction for field {field}, "
                         f"filter {filt} (dual mode)"), log_file)

    else:
        ut.printlog((f"Aperture correction already estimated for field "
                     f"{field} (dual mode)"), log_file)

    # After finishing, remove temp file
    if not os.path.exists(save_file):
        cmd = f"mv {save_file+'temp'} {save_file}"
        ut.printlog(cmd, log_file)
        os.system(cmd)


if 'photometry_dual' in conf['run_steps']:
    obtain_dual_mode_aper_corr()


# ***************************************************
#    Plot growth curve - dual mode
# ***************************************************


def plot_dual_mode_growth_curve():

    print("")
    ut.printlog(('********** '
                 'Plotting dual mode growth curves '
                 '**********'),
                 log_file)
    print("")

    for filt in conf['filters']:

        plot_name = f'growth_curve_{field}_{filt}_dual.png'
        save_file = os.path.join(dual_apercorr_path, 'growth_curves',
                                 plot_name)

        if not os.path.exists(save_file):

            # Get photometry catalog
            if conf['sex_XY_correction']:
                catalog_name = f"sex_{field}_{filt}_dual_xycorr.fits"
                catalog = os.path.join(dual_xycorr_path, catalog_name)
            else:
                catalog_name = f"sex_{field}_{filt}_dual.fits"
                catalog = os.path.join(dual_catalogs_path, catalog_name)

            # Get filt sexconfig file
            conf_file_name = f"{field}_{filt}_dual.sex"
            sexconf_file = os.path.join(dual_sexconf_path, conf_file_name)

            # Calculate filter aperture correction
            ut.growth_curve_plotter(catalog=catalog,
                                    filt=filt,
                                    sexconf=sexconf_file,
                                    save_file=save_file,
                                    aperture=conf['apercorr_diameter'],
                                    s2ncut=conf['apercorr_s2ncut'],
                                    starcut=conf['apercorr_starcut'],
                                    verbose=True,
                                    max_aperture=conf['apercorr_max_aperture'])

            ut.printlog((f"Plotted growth curve for field {field}, "
                         f"filter {filt} (dual mode)"), log_file)

        else:
            ut.printlog((f"Growth curve already plotted for field "
                         f"{field}, filter {filt}  (dual mode)"), log_file)


if 'photometry_dual' in conf['run_steps']:
    plot_dual_mode_growth_curve()


# ***************************************************
#    Apply aperture correction - dual mode
# ***************************************************


def apply_dual_mode_aperture_correction():

    print("")
    ut.printlog(('********** '
                 'Applying dual mode aperture correction '
                 '**********'),
                 log_file)
    print("")

    aper_corr_name = f"{field}_apercorr_dual.zp"
    aper_corr_file = os.path.join(dual_apercorr_path, aper_corr_name)

    for filt in conf['filters']:

        save_name = f'sex_{field}_{filt}_dual_apercorr.fits'
        save_file = os.path.join(dual_apercorr_path, save_name)

        if not os.path.exists(save_file):

            # Get photometry catalog
            if conf['sex_XY_correction']:
                catalog_name = f"sex_{field}_{filt}_dual_xycorr.fits"
                catalog = os.path.join(dual_xycorr_path, catalog_name)
            else:
                catalog_name = f"sex_{field}_{filt}_dual.fits"
                catalog = os.path.join(dual_catalogs_path, catalog_name)

            # Get filt sexconfig file
            conf_file_name = f"{field}_{filt}_dual.sex"
            sexconf_file = os.path.join(dual_sexconf_path, conf_file_name)

            # Calculate filter aperture correction
            ut.apply_aperture_correction(catalog       = catalog,
                                         filt          = filt,
                                         sexconf       = sexconf_file,
                                         aperture = conf['apercorr_diameter'],
                                         apercorr_file = aper_corr_file,
                                         save_file     = save_file,
                                         field         = field,
                                         drname = conf['data_release_name'],
                                         sexmode       = 'dual')

            ut.printlog((f"Applied aperture correction for field {field}, "
                         f"filter {filt} (dual mode)"), log_file)

        else:
            ut.printlog((f"Aperture correction already applied for field "
                         f"{field}, filter {filt} (dual mode)"), log_file)


if 'photometry_dual' in conf['run_steps']:
    apply_dual_mode_aperture_correction()
