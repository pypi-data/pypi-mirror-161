# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                                 pipeline.py
#             Runs all the steps of the S-PLUS calibration pipeline
# ******************************************************************************


"""
This scripts runs the steps of the calibration pipeline

--------------------------------------------------------------------------------
   INPUTS:
--------------------------------------------------------------------------------
All inputs are taken from the config_file

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
User must not change anything in this code. Changes to choose which steps to
run should be made in the config_file

config_file.py
    run_steps        = [*list of stepś*]

    possible steps are:
        The following steps are necessary to complete the calibration
        'photometry_single': obtain aperture photometry in single mode
        'photometry_dual'  : obtain aperture photometry in dual mode
        'photometry_psf'   : obtain psf photometry
        'correction_xy'    : corrects XY position zero-points inhomogeneities
        'aper_corretion'   : applies aperture correction to fixed aperture

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$ python pipeline_final *field_list_file* *config_file*

the field_list_file should be an ascii file where each line is the name of one
field to calibrate.
----------------
"""

################################################################################
# Import external packages

import os
import sys

from termcolor import cprint

usage_message = """
USAGE:

option1: list of fields
$spluscalib  *field_list_file* *config_file*

option2: single field
$spluscalib  *field_name* *config_file* --onefield

"""

pipeline_path = os.path.split(__file__)[0]

sys.path.append(pipeline_path)

################################################################################
# Import spluscalib packages

import utils as ut

################################################################################
# Read parameters

cprint("""
************************************************************************
*                                                                      *
*                   Starting the calibration pipeline                  *
*                                                                      *
************************************************************************
""", color = "cyan")

cwd = os.getcwd()

try:
    field_list_file = os.path.join(cwd, sys.argv[1])
    conf_file = os.path.join(cwd, sys.argv[2])

except IndexError:
    print(usage_message)
    sys.exit()

pipeline_path = os.path.split(__file__)[0]

cprint(conf_file, color = "white", attrs=["dark"])
cprint("******* reading the configuration file *******", color = "yellow")
conf = ut.pipeline_conf(conf_file)

################################################################################
# Create save path directory

ut.makedir(conf['save_path'])
ut.makedir(conf['run_path'])

logs_path = os.path.join(conf['run_path'], 'logs')
ut.makedir(logs_path)

################################################################################
# Initiate log file

log_file_name = os.path.join(logs_path, 'pipeline.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(conf['run_path'], log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Reading parameters

print("\n\n")

ut.printlog("*********** Reading configuratrion file **********", log_file, 
            color = "yellow")

for param in list(conf.keys()):
    ut.printlog(f"{param}: {conf[param]}", log_file, 
                color = "blue")

print("\n\n")

################################################################################
# Reading field list

ut.printlog("*********** Reading field list **********", log_file,
           color = "yellow")

if '--onefield' in sys.argv:
    fields = [sys.argv[1]]
else:
    fields = ut.load_field_list(field_list_file)

ut.printlog(f"Running the pipeline for fields:", log_file, color = "yellow")
ut.printlog(f"{fields}", log_file, 
            color = "yellow", attrs = ["bold"])

################################################################################
# Running pipeline for each field

for field in fields:

    ut.printlog(f"""
    ************************************************************************
    *                                                                      *
    *                Working on field {field:37}*
    *                                                                      *
    ************************************************************************
    """, log_file, color = "cyan", attrs = ["bold"])

    #################
    # Make field path
    field_path = os.path.join(conf['run_path'], field)
    logs_path = os.path.join(field_path, 'logs')

    field_images_path = os.path.join(field_path, 'Images')
    
    if "--skip_missing_images" in sys.argv:
        source_images_path = os.path.join(conf["path_to_images"], field)
        if not os.path.exists(source_images_path):
            ut.printlog(f"{field} images not found. Skipping to next field\n\n",
                        log_file, color = "white", attrs = ["dark"])
            continue

    if not os.path.exists(field_path):
        ut.makedir(field_path)
        ut.printlog(f"Created directory {field_path}.", log_file,
                    color = "green", attrs=["bold"])

        ut.makedir(logs_path)
        ut.printlog(f"Created directory {logs_path}.", log_file,
                    color = "green", attrs=["bold"])

        ut.makedir(field_images_path)
        ut.printlog(f"Created directory {field_images_path}.", log_file,
                    color = "green", attrs=["bold"])

    else:
        ut.printlog(f"Directory {field_path} already exists.", log_file,
                    color = "white", attrs=["bold", "dark"])

    print("")

    ###################
    # Copy files already present in save_path
    
    if conf['run_path'] != conf['save_path']:
        field_save_path = os.path.join(conf['save_path'], field)
        cmd = f"rsync --update -haz --progress {field_save_path} {conf['run_path']}"
        ut.printlog(cmd, log_file, color = "blue")
        os.system(cmd)
        print("")

    ###################
    # Prepare field log

    log_field_name = os.path.join(logs_path, f'{field}.log')
    log_field_name = ut.gen_logfile_name(log_field_name)
    log_field_file = os.path.join(conf['run_path'], log_field_name)

    with open(log_file, "w") as log:
        log.write("")

    # Make backup of config file
    cmd = f"cp {conf_file} {logs_path}"
    ut.printlog(cmd, log_field_file, color = "green")
    os.system(cmd)

    # Run steps

    ############################################################################
    # Copy fz images and unpack, if necessary

    # Check if configuration asks photometry to be run
    run_photometry = 'photometry_single' in conf['run_steps']
    run_photometry = run_photometry or ('photometry_dual' in conf['run_steps'])
    run_photometry = run_photometry or ('photometry_psf' in conf['run_steps'])

    already_run = False
    already_run_single = False
    already_run_dual = False
    already_run_psf = False

    # Check if photometry was already run
    if run_photometry:

        already_run = True
        if 'photometry_single' in conf['run_steps']:
            already_run_single = ut.check_photometry(field = field,
                                               save_path   = conf['save_path'],
                                               photometry  = 'single',
                                               filter_list = conf['filters'])

            already_run = already_run & already_run_single

        if 'photometry_dual' in conf['run_steps']:
            already_run_dual = ut.check_photometry(field=field,
                                                   save_path=conf['save_path'],
                                                   photometry='dual',
                                                   filter_list=conf['filters'])

            already_run = already_run & already_run_dual

        if 'photometry_psf' in conf['run_steps']:
            already_run_psf = ut.check_photometry(field=field,
                                                  save_path=conf['save_path'],
                                                  photometry='psf',
                                                  filter_list=conf['filters'])

            already_run = already_run & already_run_psf

    if run_photometry and not ('--nofits' in sys.argv) and not already_run:

        for filt in conf['filters']:
            image_name  = f'{field}_{filt}_swp.fz'
            image_db_fz = os.path.join(conf['path_to_images'], field,
                                       image_name)
            image_fz    = os.path.join(field_images_path, image_name)

            ##############################################
            # Copying fz from path_to_images to field path

            if not os.path.exists(image_fz):

                ut.printlog(f"Copying image {image_name}", log_field_file,
                            color = "yellow")

                cmd = f"cp {image_db_fz} {field_images_path}"
                ut.printlog(cmd, log_field_file, color = "green")
                os.system(cmd)

            else:
                ut.printlog(f"Image {image_fz} already exists",
                            log_field_file, color = "white", attrs = ["dark"])
            

            if conf['use_weight']:

                weight_fz = image_fz.replace(".fz", "weight.fz")
                weight_db_fz = image_db_fz.replace(".fz", "weight.fz")

                if not os.path.exists(weight_fz):
                    cmd = f"cp {weight_db_fz} {field_images_path}"
                    ut.printlog(cmd, log_field_file, color = "green")
                    os.system(cmd)

                else:
                    ut.printlog(f"Image {weight_fz} already exists",
                                log_field_file, 
                                color = "white", attrs = ["dark"])

            #######################
            # Unpacking fits images

            image_fits = image_fz.replace(".fz", ".fits")

            if not os.path.exists(image_fits):

                ut.printlog(f"Unpacking image {image_fz}", log_field_file,
                            color = "yellow")
                ut.fz2fits(image_fz)

            else:
                ut.printlog(f"Image {image_fits} already exists",
                            log_field_file, color = "white", attrs = ["dark"])
                
                
            if conf['use_weight']:
                weight_fz = image_fz.replace(".fz", "weight.fz")
                weight_fits = weight_fz.replace(".fz", ".fits")

                if not os.path.exists(weight_fits):             
                    ut.printlog(f"Unpacking weight {weight_fz}",
                                log_field_file, color = "yellow")
                    ut.fz2fits(weight_fz)

                else:
                    ut.printlog(f"Image {weight_fits} already exists",
                                log_field_file, 
                                color = "white", attrs = ["dark"])

            print("")

    ############################################################################

    ############################################################################
    # Run the photometry
    if 'photometry_single' in conf['run_steps'] and not already_run_single:

        final_file = os.path.join(field_path, 'Photometry', 'single', 'master',
                                  f"{field}_master_photometry_only_single.fits")

        if not os.path.exists(final_file):
            script = os.path.join(pipeline_path,'steps','photometry_single.py')
            cmd = f'python3 {script} {field} {conf_file}'
            ut.printlog(cmd, log_field_file, 
                        color = "blue", on_color = "on_white")
            os.system(cmd)

            print("\n\n")

    if 'photometry_dual' in conf['run_steps'] and not already_run_dual:

        final_file = os.path.join(field_path, 'Photometry', 'dual', 'master',
                                  f"{field}_master_photometry_only_dual.fits")

        if not os.path.exists(final_file):
            script = os.path.join(pipeline_path, 'steps', 'photometry_dual.py')
            cmd = f'python3 {script} {field} {conf_file}'
            ut.printlog(cmd, log_field_file,
                        color = "blue", on_color = "on_white")
            os.system(cmd)

            print("\n\n")

    if 'photometry_psf' in conf['run_steps'] and not already_run_psf:

        final_file = os.path.join(field_path, 'Photometry', 'psf', 'master',
                                  f"{field}_master_photometry_only_psf.fits")

        if not os.path.exists(final_file):
            script = os.path.join(pipeline_path, 'steps', 'photometry_psf.py')
            cmd = f'python3 {script} {field} {conf_file}'
            ut.printlog(cmd, log_field_file,
                        color = "blue", on_color = "on_white")
            os.system(cmd)

            print("\n\n")

    if 'correction_xy' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'correction_xy.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'correction_aper' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'correction_aper.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'photometry_id' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'photometry_ID.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'photometry_master' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'photometry_master.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'crossmatch' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'crossmatch.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'calibration_external' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'calibration_external.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'calibration_stloc' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'calibration_stloc.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'calibration_internal' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'calibration_internal.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'calibration_gaiascale' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'calibration_gaiascale.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'calibration_diagnostic' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'calibration_diagnostic.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    # It only needs to check for calibration_external to know if any calibration
    # is being run.
    if 'calibration_external' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'calibration_finalzp.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    if 'calibration_catalog' in conf['run_steps']:

        script = os.path.join(pipeline_path, 'steps', 'calibration_catalog.py')
        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")
    
    if 'quality_check' in conf['run_steps']:

        if "--dual_quality_check" in sys.argv:
            script = os.path.join(pipeline_path, 'quality_check.py')
        else:
            if conf['calibration_photometry'].lower() in ['single', 'dual']:
                script = os.path.join(pipeline_path, 'quality_check.py')
            elif conf['calibration_photometry'].lower() in ['psf']:
                script = os.path.join(pipeline_path, 'quality_check_PSF.py')

        cmd = f'python3 {script} {field} {conf_file}'
        ut.printlog(cmd, log_field_file,
                    color = "blue", on_color = "on_white")
        os.system(cmd)

        print("\n\n")

    ############################################################################

    ###################
    # Remove fits files

    if run_photometry and conf['remove_fits'] and not ('--nofits' in sys.argv) \
                      and not ('--keepfits' in sys.argv):

        for filt in conf['filters']:
            image_name = f'{field}_{filt}_swp.fz'
            image_fz = os.path.join(field_images_path, image_name)
            image_fits = image_fz.replace(".fz", ".fits")

            # Only remove .fits if .fz exists:
            if os.path.exists(image_fz) and os.path.exists(image_fits):

                ut.printlog(f"Removing image {image_fits}", log_field_file,
                             color = "red")

                cmd = f"rm {image_fits}"
                ut.printlog(cmd, log_field_file, color = "yellow")
                os.system(cmd)

            if conf['use_weight']:

                weight_fz = image_fz.replace(".fz", "weight.fz")
                weight_fits = weight_fz.replace(".fz", ".fits")

                if os.path.exists(weight_fz) and os.path.exists(weight_fits):
                    ut.printlog(f"Removing weight {weight_fits}",
                                log_field_file, color = "yellow")

                    cmd = f"rm {weight_fits}"
                    ut.printlog(cmd, log_field_file, color = "red")
                    os.system(cmd)

    #################################
    # Remove all images, including fz

    if os.path.exists(field_images_path) and conf["remove_images"]:
        ut.printlog(f"Removing images, including .fz",
                    log_field_file, color = "yellow")

        cmd = f"rm -r {field_images_path}"
        ut.printlog(cmd, log_field_file, color = "red", attrs = ["bold"])
        os.system(cmd)

    #########################
    # Sync run_path and save_path field to save_path
    if conf['save_path'] != conf['run_path']:
        
        cmd = f"rsync --update -haz --progress {field_path} {conf['save_path']}"
        ut.printlog(cmd, log_field_file, color = "blue")
        os.system(cmd)
        
        cmd = f"rm -r {field_path}"
        ut.printlog(cmd, log_field_file, color = "red", attrs=["bold"])
        os.system(cmd)
    
