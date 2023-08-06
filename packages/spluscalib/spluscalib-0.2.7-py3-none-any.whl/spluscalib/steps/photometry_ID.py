# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                               photometry_id.py
#                  Assign detection IDs to instrumental catalogs
# ******************************************************************************

"""
Assign detection IDs to instrumental catalogs. In dual mode aperture photometry,
IDs in the filter catalogs matches the IDs of the detection image. In PSF and
single mode aperture photometry there is no correlation between IDs of different
filters

The S-PLUS field is given as the first command line argument.

Configuration parameters are set in the configuration file given as the second
command line argument

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------
create_id_path()
include_filter_id_in_single_mode_catalogs()
extract_filter_id_radec_from_single_catalogs()
crossmatch_filter_id_catalogs_single()
create_field_id_catalog_single()
include_field_id_in_single_mode_catalogs()
remove_temporary_single_mode_filter_id_files()
generate_dual_mode_field_ids()
include_field_id_in_dual_mode_catalogs()
include_field_id_in_detection_catalog()
extract_filter_id_radec_from_psf_catalogs()
crossmatch_filter_id_catalogs_psf()
create_field_id_catalog_psf()
include_field_id_in_psf_mode_catalogs()

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
$python3 photometry_id.py *field_name* *config_file*

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
single_catalog_path = os.path.join(single_path, 'catalogs')
single_xycorr_path = os.path.join(single_path, 'xy_correction')
single_apercorr_path = os.path.join(single_path, 'aper_correction')
single_id_path  = os.path.join(single_path, 'id')

dual_path         = os.path.join(photometry_path, 'dual')
dual_catalog_path = os.path.join(dual_path, 'catalogs')
dual_xycorr_path = os.path.join(dual_path, 'xy_correction')
dual_apercorr_path = os.path.join(dual_path, 'aper_correction')
dual_detection_path = os.path.join(dual_path, 'detection')
dual_id_path  = os.path.join(dual_path, 'id')

psf_path         = os.path.join(photometry_path, 'psf')
psf_catalog_path = os.path.join(psf_path, 'catalogs')
psf_xycorr_path = os.path.join(psf_path, 'xy_correction')
psf_id_path  = os.path.join(psf_path, 'id')

images_path     = os.path.join(field_path, 'Images')

log_path        = os.path.join(photometry_path, 'logs')


################################################################################
# Initiate log file

ut.makedir(log_path)

log_file_name = os.path.join(log_path, 'photometry_id.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(photometry_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Log configuration

ut.printlog("Single mode photometry parameters:", log_file)

master_phot_params = ['run_path', 'filters', 'data_release_name']

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


def create_id_path():

    print("")
    ut.printlog(('********** '
                 'Generating id paths '
                 '**********'),
                 log_file)
    print("")

    # Create single mode id path
    if 'photometry_single' in conf['run_steps']:
        ut.makedir(single_id_path)

    # Create dual mode id path
    if 'photometry_dual' in conf['run_steps']:
        ut.makedir(dual_id_path)

    # Create psf mode id path
    if 'photometry_psf' in conf['run_steps']:
        ut.makedir(psf_id_path)


create_id_path()


# ***************************************************
#    Assign single mode filter IDs
# ***************************************************

def include_filter_id_in_single_mode_catalogs():
    print("")
    ut.printlog(('********** '
                 'Including filter IDs in single mode catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        if "correction_aper" in conf["run_steps"]:
            catalog_name = f"sex_{field}_{filt}_single_apercorr.fits"
            catalog = os.path.join(single_apercorr_path, catalog_name)
        else:
            if "correction_xy" in conf["run_steps"]:
                catalog_name = f"sex_{field}_{filt}_single_xycorr.fits"
                catalog = os.path.join(single_xycorr_path, catalog_name)
            else:
                catalog_name = f"sex_{field}_{filt}_single.fits"
                catalog = os.path.join(single_catalog_path, catalog_name)

        save_name = f'sex_{field}_{filt}_single_tmp.fits'
        save_file = os.path.join(single_id_path, save_name)

        future_name = f'{field}_{filt}_id+radec_single.fits'
        future_file = os.path.join(single_id_path, future_name)

        if not os.path.exists(save_file) and not os.path.exists(future_file):
            ut.assign_single_mode_filter_id(catalog   = catalog,
                                            filt      = filt,
                                            save_file = save_file,
                                            field     = field,
                                     drname    = conf["data_release_name"])

            ut.printlog((f"Assigned Filter IDs for field {field}, "
                         f"filter {filt} (single mode)"), log_file)

        else:
            ut.printlog((f"Filter IDs already assigned for field {field}, "
                         f"filter {filt} (single mode)"), log_file)


if 'photometry_single' in conf['run_steps']:
    include_filter_id_in_single_mode_catalogs()

# ***************************************************
#    Extract filt_ID+RADEC catalogs
# ***************************************************

def extract_filter_id_radec_from_single_catalogs():
    print("")
    ut.printlog(('********** '
                 'Extracting filter IDs, RA, DEC from single mode catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f'sex_{field}_{filt}_single_tmp.fits'
        catalog = os.path.join(single_id_path, catalog_name)

        save_name = f'{field}_{filt}_id+radec_single.fits'
        save_file = os.path.join(single_id_path, save_name)

        if not os.path.exists(save_file):
            ut.extract_filt_id_single(catalog   = catalog,
                                      filt      = filt,
                                      save_file = save_file)

            ut.printlog((f"Extracted filter IDs for field {field}, "
                         f"filter {filt} (single mode)"), log_file)

        else:
            ut.printlog((f"Filter IDs already extracted for field {field}, "
                         f"filter {filt} (single mode)"), log_file)


if 'photometry_single' in conf['run_steps']:
    extract_filter_id_radec_from_single_catalogs()


# ***************************************************
#    Crossmatch filt catalogs single
# ***************************************************

def crossmatch_filter_id_catalogs_single():
    print("")
    ut.printlog(('********** '
                 'Crossmatching filter ID catalogs (single mode) '
                 '**********'),
                log_file)
    print("")

    save_name = f'{field}_all_id+radec_single.fits'
    save_file = os.path.join(single_id_path, save_name)

    if not os.path.exists(save_file):

        cmd  = f"java -Xss4m -jar {conf['path_to_stilts']} tmatchn "
        cmd += f"nin={len(conf['filters'])} matcher=sky params=3 "
        cmd += f"multimode=group "

        j = 1
        for filt in conf['filters']:
            catalog_name = f'{field}_{filt}_id+radec_single.fits'
            catalog = os.path.join(single_id_path, catalog_name)

            filt_standard = ut.translate_filter_standard(filt)
            valuesN = f"'RA_{filt_standard} DEC_{filt_standard}'"

            cmd += f"in{j}={catalog} ifmt{j}=fits values{j}={valuesN} "
            cmd += f"join{j}=always "
            j += 1

        cmd += f"out={save_file} ofmt=fits"

        ut.printlog(cmd, log_file)
        os.system(cmd)

        ut.printlog((f"Crossmatched Filter IDs for field {field}, "
                     f"(single mode)"), log_file)

    else:
        ut.printlog((f"Filter IDs already crossmatched for field {field}, "
                     f"(single mode)"), log_file)


if 'photometry_single' in conf['run_steps']:
    crossmatch_filter_id_catalogs_single()


# ***************************************************
#    Create field ID catalog for single mode
# ***************************************************

def create_phot_id_catalog_single():

    print("")
    ut.printlog(('********** '
                 'Creating PHOT ID catalog (single mode) '
                 '**********'),
                log_file)
    print("")

    catalog_name = f'{field}_all_id+radec_single.fits'
    catalog_file = os.path.join(single_id_path, catalog_name)

    save_name = f'{field}_PHOT_ID_single.fits'
    save_file = os.path.join(single_id_path, save_name)

    if not os.path.exists(save_file):
        ut.generate_phot_id(catalog=catalog_file,
                             filters=conf["filters"],
                             field=field,
                             drname=conf["data_release_name"],
                             mode="single",
                             save_file = save_file)

        ut.printlog((f"Generated PHOT IDs for field {field}, "
                     f"(single mode)"), log_file)

    else:
        ut.printlog((f"PHOT IDs already generated for field {field}, "
                     f"(single mode)"), log_file)


if 'photometry_single' in conf['run_steps']:
    create_phot_id_catalog_single()


# ***************************************************
#    Generate dual mode PHOT IDs catalog
# ***************************************************

def create_phot_id_catalog_dual():
    print("")
    ut.printlog(('********** '
                 'Creating PHOT ID catalog (dual mode) '
                 '**********'),
                log_file)
    print("")

    catalog_name = f"sex_{field}_detection_catalog.fits"
    catalog = os.path.join(dual_detection_path, catalog_name)

    save_name = f'{field}_PHOT_ID_dual.fits'
    save_file = os.path.join(dual_id_path, save_name)

    if not os.path.exists(save_file):
        ut.generate_dual_mode_phot_id(catalog=catalog,
                                  save_file=save_file,
                                  field=field,
                                  drname=conf["data_release_name"])

        ut.printlog(f"Generated dual PHOT IDs for field {field}", log_file)

    else:
        ut.printlog(f"Dual PHOT IDs already exist for field {field}", log_file)


if 'photometry_dual' in conf['run_steps']:
    create_phot_id_catalog_dual()


# ***************************************************
#    Extract filt_ID+RADEC catalogs (PSF)
# ***************************************************

def extract_filter_id_radec_from_psf_catalogs():
    print("")
    ut.printlog(('********** '
                 'Extracting filter IDs, RA, DEC from psf catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        if "correction_xy" in conf["run_steps"]:
            catalog_name = f'{field}_{filt}_psf_xycorr.cat'
            catalog_file = os.path.join(psf_xycorr_path, catalog_name)
        else:
            catalog_name = f'{field}_{filt}_psf.cat'
            catalog_file = os.path.join(psf_catalog_path, catalog_name)

        save_name = f'{field}_{filt}_id+radec_psf.fits'
        save_file = os.path.join(psf_id_path, save_name)

        if not os.path.exists(save_file):
            ut.extract_filt_id_psf(catalog   = catalog_file,
                                   filt      = filt,
                                   save_file = save_file)

            ut.printlog((f"Extracted filter IDs for field {field}, "
                         f"filter {filt} (psf mode)"), log_file)

        else:
            ut.printlog((f"Filter IDs already extracted for field {field}, "
                         f"filter {filt} (psf mode)"), log_file)


if 'photometry_psf' in conf['run_steps']:
    extract_filter_id_radec_from_psf_catalogs()


# ***************************************************
#    Crossmatch filt catalogs (psf)
# ***************************************************

def crossmatch_filter_id_catalogs_psf():
    print("")
    ut.printlog(('********** '
                 'Crossmatching filter ID catalogs (psf mode) '
                 '**********'),
                log_file)
    print("")

    save_name = f'{field}_all_id+radec_psf.fits'
    save_file = os.path.join(psf_id_path, save_name)

    if not os.path.exists(save_file):

        cmd  = f"java -Xss8m -jar {conf['path_to_stilts']} tmatchn "
        cmd += f"nin={len(conf['filters'])} matcher=sky params=3 "
        cmd += f"multimode=group "

        j = 1
        for filt in conf['filters']:
            catalog_name = f'{field}_{filt}_id+radec_psf.fits'
            catalog = os.path.join(psf_id_path, catalog_name)

            filt_standard = ut.translate_filter_standard(filt)
            valuesN = f"'RA_{filt_standard} DEC_{filt_standard}'"

            cmd += f"in{j}={catalog} ifmt{j}=fits values{j}={valuesN} "
            cmd += f"join{j}=always "
            j += 1

        cmd += f"out={save_file} ofmt=fits"

        ut.printlog(cmd, log_file)
        os.system(cmd)

        ut.printlog((f"Crossmatched Filter IDs for field {field}, "
                     f"(psf mode)"), log_file)

    else:
        ut.printlog((f"Filter IDs already crossmatched for field {field}, "
                     f"(psf mode)"), log_file)


if 'photometry_psf' in conf['run_steps']:
    crossmatch_filter_id_catalogs_psf()


# ***************************************************
#    Create PHOT ID catalog for psf mode
# ***************************************************

def create_phot_id_catalog_psf():

    print("")
    ut.printlog(('********** '
                 'Creating PHOT ID catalog (psf mode) '
                 '**********'),
                log_file)
    print("")

    catalog_name = f'{field}_all_id+radec_psf.fits'
    catalog_file = os.path.join(psf_id_path, catalog_name)

    save_name = f'{field}_PHOT_ID_psf.fits'
    save_file = os.path.join(psf_id_path, save_name)

    if not os.path.exists(save_file):
        ut.generate_phot_id(catalog=catalog_file,
                            filters=conf["filters"],
                            field=field,
                            drname=conf["data_release_name"],
                            mode="psf",
                            save_file = save_file)

        ut.printlog((f"Generated PHOT IDs for field {field}, "
                     f"(psf mode)"), log_file)

    else:
        ut.printlog((f"PHOT IDs already generated for field {field}, "
                     f"(psf mode)"), log_file)

if 'photometry_psf' in conf['run_steps']:
    create_phot_id_catalog_psf()


# ***************************************************
#    Combining PHOT ID catalogs all modes
# ***************************************************

def combining_phot_ID_catalogs():

    print("")
    ut.printlog(('********** '
                 'Combining PHOT ID catalogs '
                 '**********'),
                log_file)
    print("")

    single_name = f'{field}_PHOT_ID_single.fits'
    single_file = os.path.join(single_id_path, single_name)

    dual_name = f'{field}_PHOT_ID_dual.fits'
    dual_file = os.path.join(dual_id_path, dual_name)

    psf_name = f'{field}_PHOT_ID_psf.fits'
    psf_file = os.path.join(psf_id_path, psf_name)

    save_name = f'{field}_PHOT_ID_all.fits'
    save_file = os.path.join(photometry_path, save_name)

    if not os.path.exists(save_file):
        cmd  = f"java -Xss4m -jar {conf['path_to_stilts']} tmatchn "
        cmd += f"matcher=sky params=5 "
        cmd += f"multimode=group "

        j = 0
        last_mode = ""

        if "photometry_dual" in conf["run_steps"]:
            j += 1
            valuesN = "'PHOT_ID_RA_dual PHOT_ID_DEC_dual'"
            cmd += f"in{j}={dual_file} ifmt{j}=fits values{j}={valuesN} "
            cmd += f"join{j}=always "

            last_mode = "dual"

        if "photometry_single" in conf["run_steps"]:
            j += 1
            valuesN = "'PHOT_ID_RA_single PHOT_ID_DEC_single'"
            cmd += f"in{j}={single_file} ifmt{j}=fits values{j}={valuesN} "
            cmd += f"join{j}=always "

            last_mode = "single"

        if "photometry_psf" in conf["run_steps"]:
            j += 1
            valuesN = "'PHOT_ID_RA_psf PHOT_ID_DEC_psf'"
            cmd += f"in{j}={psf_file} ifmt{j}=fits values{j}={valuesN} "
            cmd += f"join{j}=always "

            last_mode = "psf"

        cmd += f"nin={j} out={save_file} ofmt=fits"

        if j > 1:
            ut.printlog(cmd, log_file)
            os.system(cmd)

        else:
            if last_mode == "dual":
                phot_id_catalog = dual_file
            elif last_mode == "single":
                phot_id_catalog = single_file
            elif last_mode == "psf":
                phot_id_catalog = psf_file
            else:
                raise ValueError(f"{last_mode} is not an acceptable value.")

            cmd = f"cp {phot_id_catalog} {save_file}"
            ut.printlog(cmd, log_file)
            os.system(cmd)

        ut.printlog(f"Combined PHOT IDs for field {field}, ", log_file)

    else:
        ut.printlog(f"PHOT IDs already combined for field {field}, ",
                    log_file)


combining_phot_ID_catalogs()

# ***************************************************
#    Generate FIELD_IDs for combined phot_ID catalogs
# ***************************************************

def creating_field_id_catalog():
    print("")
    ut.printlog(('********** '
                 'Creating Field ID catalog '
                 '**********'),
                log_file)
    print("")

    phot_id_catalog_name = f'{field}_PHOT_ID_all.fits'
    phot_id_catalog = os.path.join(photometry_path, phot_id_catalog_name)

    save_name = f'{field}_FIELD_ID.fits'
    save_file = os.path.join(photometry_path, save_name)

    if not os.path.exists(save_file):

        modes = []
        if "photometry_dual" in conf['run_steps']:
            modes.append("dual")
        if "photometry_single" in conf['run_steps']:
            modes.append("single")
        if "photometry_psf" in conf['run_steps']:
            modes.append("psf")

        ut.generate_field_id(catalog=phot_id_catalog,
                             field=field,
                             drname=conf["data_release_name"],
                             save_file=save_file,
                             modes = modes)

    else:
        ut.printlog(f"FIELD IDs already assigned for field {field}, ",
                    log_file)


creating_field_id_catalog()


# ***************************************************
#    Including MODE/FIELD IDs psf mode
# ***************************************************

def include_field_phot_ids_in_psf_catalogs():
    print("")
    ut.printlog(('********** '
                 'Including FIELD/PHOT ID in psf mode catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        if "correction_xy" in conf["run_steps"]:
            catalog_name = f'{field}_{filt}_psf_xycorr.cat'
            catalog_file = os.path.join(psf_xycorr_path, catalog_name)
        else:
            catalog_name = f'{field}_{filt}_psf.cat'
            catalog_file = os.path.join(psf_catalog_path, catalog_name)

        id_catalog_name = f'{field}_FIELD_ID.fits'
        id_catalog = os.path.join(photometry_path, id_catalog_name)

        save_name = f'{field}_{filt}_psf_withIDs.csv'
        save_file = os.path.join(psf_id_path, save_name)

        filt_standard = ut.translate_filter_standard(filt)
        values2 = f"'RA_{filt_standard} DEC_{filt_standard}'"

        if not os.path.exists(save_file):

            cmd = f"java -Xss4m -jar {conf['path_to_stilts']} tmatch2 "
            cmd += f"matcher=sky params=3 join=1and2 "
            cmd += f"in1={id_catalog} ifmt1=fits "
            cmd += f"values1='PHOT_ID_RA_psf PHOT_ID_DEC_psf' "
            cmd += f"in2={catalog_file} ifmt2=ascii "
            cmd += f"values2={values2} "
            cmd += f"out={save_file} ofmt=csv"

            print(cmd)
            os.system(cmd)

            ut.printlog((f"Assigned IDs for field {field}, "
                         f"filter {filt} (psf mode)"), log_file)

        else:
            ut.printlog((f"IDs already assigned for field {field}, "
                         f"filter {filt} (psf mode)"), log_file)


if 'photometry_psf' in conf['run_steps']:
    include_field_phot_ids_in_psf_catalogs()


# ***************************************************
#    Assign dual mode IDs
# ***************************************************

def include_field_phot_ids_in_dual_catalogs():
    print("")
    ut.printlog(('********** '
                 'Including FIELD/PHOT ID in dual mode catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        if "correction_aper" in conf["run_steps"]:
            catalog_name = f"sex_{field}_{filt}_dual_apercorr.fits"
            catalog = os.path.join(dual_apercorr_path, catalog_name)
        else:
            if "correction_xy" in conf["run_steps"]:
                catalog_name = f"sex_{field}_{filt}_dual_xycorr.fits"
                catalog = os.path.join(dual_xycorr_path, catalog_name)
            else:
                catalog_name = f"sex_{field}_{filt}_dual.fits"
                catalog = os.path.join(dual_catalog_path, catalog_name)

        id_catalog_name = f'{field}_FIELD_ID.fits'
        id_catalog = os.path.join(photometry_path, id_catalog_name)

        save_name = f'sex_{field}_{filt}_dual_withIDs.fits'
        save_file = os.path.join(dual_id_path, save_name)

        if not os.path.exists(save_file):
            cmd  = f"java -Xss4m -jar {conf['path_to_stilts']} tmatch2 "
            cmd += f"matcher=sky params=3 join=1and2 "
            cmd += f"in1={id_catalog} ifmt1=fits "
            cmd += f"values1='PHOT_ID_RA_dual PHOT_ID_DEC_dual' "
            cmd += f"in2={catalog} ifmt2=fits "
            cmd += f"values2='ALPHA_J2000 DELTA_J2000' "
            cmd += f"out={save_file} ofmt=fits"

            print(cmd)
            os.system(cmd)

            ut.printlog((f"Assigned IDs for field {field}, "
                         f"filter {filt} (dual mode)"), log_file)

        else:
            ut.printlog((f"IDs already assigned for field {field}, "
                         f"filter {filt} (dual mode)"), log_file)


if 'photometry_dual' in conf['run_steps']:
    include_field_phot_ids_in_dual_catalogs()


# ***************************************************
#    Include FIELD_ID in detection catalog
# ***************************************************

def include_field_phot_ids_in_detection_catalog():
    print("")
    ut.printlog(('********** '
                 'Including Field IDs in detection catalog '
                 '**********'),
                log_file)
    print("")

    catalog_name = f"sex_{field}_detection_catalog.fits"
    catalog = os.path.join(dual_detection_path, catalog_name)

    id_catalog_name = f'{field}_FIELD_ID.fits'
    id_catalog = os.path.join(photometry_path, id_catalog_name)

    save_name = f'sex_{field}_detection_withIDs.fits'
    save_file = os.path.join(dual_id_path, save_name)

    if not os.path.exists(save_file):
        cmd = f"java -Xss4m -jar {conf['path_to_stilts']} tmatch2 "
        cmd += f"matcher=sky params=3 join=1and2 "
        cmd += f"in1={id_catalog} ifmt1=fits "
        cmd += f"values1='PHOT_ID_RA_dual PHOT_ID_DEC_dual' "
        cmd += f"in2={catalog} ifmt2=fits "
        cmd += f"values2='ALPHA_J2000 DELTA_J2000' "
        cmd += f"out={save_file} ofmt=fits"

        os.system(cmd)

        ut.printlog(f"Assigned IDs for field {field}, detection catalog ", log_file)

    else:
        ut.printlog((f"IDs already assigned for field {field}, "
                     f"detection catalog"), log_file)


if 'photometry_dual' in conf['run_steps']:
    include_field_phot_ids_in_detection_catalog()


# ***************************************************
#    Assign single mode IDs
# ***************************************************

def include_field_phot_ids_in_single_catalogs():
    print("")
    ut.printlog(('********** '
                 'Including FIELD/PHOT IDs in single mode catalogs '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        catalog_name = f'sex_{field}_{filt}_single_tmp.fits'
        catalog = os.path.join(single_id_path, catalog_name)

        id_catalog_name = f'{field}_FIELD_ID.fits'
        id_catalog = os.path.join(photometry_path, id_catalog_name)

        save_name = f'sex_{field}_{filt}_single_withIDs.fits'
        save_file = os.path.join(single_id_path, save_name)

        if not os.path.exists(save_file):
            cmd  = f"java -Xss4m -jar {conf['path_to_stilts']} tmatch2 "
            cmd += f"matcher=sky params=3 join=1and2 "
            cmd += f"in1={id_catalog} ifmt1=fits "
            cmd += f"values1='PHOT_ID_RA_single PHOT_ID_DEC_single' "
            cmd += f"in2={catalog} ifmt2=fits "
            cmd += f"values2='ALPHA_J2000 DELTA_J2000' "
            cmd += f"out={save_file} ofmt=fits"

            print(cmd)
            os.system(cmd)

            ut.printlog((f"Assigned IDs for field {field}, "
                         f"filter {filt} (single mode)"), log_file)

        else:
            ut.printlog((f"IDs already assigned for field {field}, "
                         f"filter {filt} (single mode)"), log_file)


if 'photometry_dual' in conf['run_steps']:
    include_field_phot_ids_in_single_catalogs()


# ***************************************************
#    Removing temporary files
# ***************************************************

def remove_temporary_single_mode_filter_id_files():
    print("")
    ut.printlog(('********** '
                 'Removing temporary single mode Filter ID files '
                 '**********'),
                log_file)
    print("")

    for filt in conf['filters']:

        tmp_name = f'sex_{field}_{filt}_single_tmp.fits'
        tmp_file = os.path.join(single_id_path, tmp_name)

        catalog_name = f'sex_{field}_{filt}_single_withIDs.fits'
        catalog_file = os.path.join(single_id_path, catalog_name)

        if os.path.exists(catalog_file):
            if os.path.exists(tmp_file):
                cmd  = f"rm {tmp_file}"
                print(cmd)
                os.system(cmd)

                ut.printlog(f"Removed file {tmp_file}", log_file)


if 'photometry_single' in conf['run_steps']:
    remove_temporary_single_mode_filter_id_files()
