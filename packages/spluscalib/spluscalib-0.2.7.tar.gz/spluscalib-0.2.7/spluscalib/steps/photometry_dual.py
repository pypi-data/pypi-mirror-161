# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                              photometry_dual.py
#                       aperture photometry in dual mode
# ******************************************************************************

"""
Generates a detection image and runs SExtractor in dual mode for one S-PLUS
field and a list of filters.

The S-PLUS field is given as the first command line argument.

The set of filters, location of S-PLUS images, default SExtractor configuration
and param files, filters used to build the detection image, and the output path
must be set in the configuration file given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------

create_photometry_path()
generate_swarp_config()
generate_combine_images_list()
generate_detection_image()
update_detection_header()
generate_detection_sexconfig_file()
generate_dual_sexconfig_files()
run_sex_detection()
run_sex_dual()
convert_detection_fits_to_fz()
dual_diagnostic_plots()

--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 photometry_dual.py *field_name* *config_file*

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
dual_path       = os.path.join(photometry_path, 'dual')
sexconf_path    = os.path.join(dual_path, 'sexconf')
catalogs_path   = os.path.join(dual_path, 'catalogs')
detection_path  = os.path.join(dual_path, 'detection')

images_path     = os.path.join(field_path, 'Images')

log_path        = os.path.join(photometry_path, 'logs')

################################################################################
# Create Photometry directory

ut.makedir(field_path)
ut.makedir(photometry_path)
ut.makedir(log_path)

################################################################################
# Initiate log file

log_file_name = os.path.join(log_path, 'photometry_dual.log')
log_file_name = ut.gen_logfile_name(log_file_name)
log_file = os.path.join(photometry_path, log_file_name)

with open(log_file, "w") as log:
    log.write("")

################################################################################
# Log configuration

ut.printlog("Dual mode photometry parameters:", log_file,
            color = "blue", attrs=["bold"])

dual_mode_params = ['run_path', 'filters', 'path_to_images', 'inst_zp',
                    'use_weight', 'path_to_sex', 'sex_config', 'sex_param',
                    'detection_image']

for param in dual_mode_params:
    try:
        ut.printlog(f"{param}: {conf[param]}", log_file,
                    color = "blue")
    except KeyError:
        ut.printlog(f"{param}: NONE", log_file,
                     color = "red")

################################################################################
# Begin script

# ***************************************************
#    If photometry path does not exist -> create
# ***************************************************


def create_photometry_path():

    print("")
    ut.printlog(('********** '
                 'Generating Dual Photometry paths '
                 '**********'),
                 log_file, color = "yellow")
    print("")

    # Create dual mode photometry path
    ut.makedir(dual_path)

    # Create dual mode sexconf path
    ut.makedir(sexconf_path)

    # Create dual mode catalogs path
    ut.makedir(catalogs_path)

    # Create detection image path
    ut.makedir(detection_path)


create_photometry_path()


# ***************************************************
#  Generate SWARP configuration for detection image
# ***************************************************

def generate_swarp_config():
    """
    Generate swarp configuration file for detection image
    """

    print("")
    ut.printlog(('********** '
                 'Generating swarp configuration '
                 '**********'), log_file, color = "yellow")
    print("")

    save_file = os.path.join(detection_path, f'{field}_config.swarp')

    if not os.path.exists(save_file):

        detection_image_name = f'{field}_detection.fits'
        detection_weight_name = f'{field}_detectionweight.fits'

        detection_image_file = os.path.join(detection_path,
                                            detection_image_name)
        detection_weight_file = os.path.join(detection_path,
                                             detection_weight_name)
        xml_output_file = os.path.join(detection_path, 'swarp_output.xml')

        if conf['use_weight']:
            combine_type = "WEIGHTED"
            weight_type  = "MAP_WEIGHT"
        else:
            combine_type = "AVERAGE"
            weight_type  = "NONE"

        # Get first image for center reference
        ref_filt = conf['detection_image'][0]
        image_name = f"{field}_{ref_filt}_swp.fits"
        image_file = os.path.join(images_path, image_name)

        # Generating config file
        ut.get_swarp_config(save_file            = save_file,
                            default_swarpconfig  = conf['swarp_config'],
                            detection_image_out  = detection_image_file,
                            detection_weight_out = detection_weight_file,
                            resample_dir         = detection_path,
                            xml_output           = xml_output_file,
                            combine_type         = combine_type,
                            weight_type          = weight_type,
                            ref_image            = image_file)

        ut.printlog(f"Created file {save_file}", log_file,
                    color = "green")

    else:
        ut.printlog(f"File {save_file} already created.", log_file,
                    color = "white", attrs=["dark"])


generate_swarp_config()


# ***************************************************
#  Generate combine images list
# ***************************************************

def generate_combine_images_list():

    """
    Generate list of images to combine for the detection image
    """

    print("")
    ut.printlog(('********** '
                 'Generating list of images to combine '
                 '**********'), log_file, color = "yellow")
    print("")

    save_file = os.path.join(detection_path, f'combine_images.txt')

    if not os.path.exists(save_file):
        # Generating filter image list
        with open(save_file, 'w') as imlist:
            for filt in conf['detection_image']:
                # Get image file
                image_name = f"{field}_{filt}_swp.fits"
                image_file = os.path.join(images_path, image_name)

                imlist.write(image_file)
                imlist.write("\n")

        ut.printlog(f"Created file combine_images.txt", log_file,
                    color = "green")

    else:
        ut.printlog(f"{save_file} already created.", log_file,
                    color = "white", attrs = ["dark"])


generate_combine_images_list()

# ***************************************************
#    Generate Detection image
# ***************************************************


def generate_detection_image():

    """
    Generate detection image
    """

    print("")
    ut.printlog(('********** '
                 'Generating Detection Image '
                 '**********'), log_file, color = "yellow")
    print("")

    det_image_name = f"{field}_detection.fits"
    det_image_file = os.path.join(detection_path, det_image_name)
    det_image_fz   = det_image_file + ".fz"

    if not os.path.exists(det_image_fz):
        if not os.path.exists(det_image_file):

            # Get swarp config file name
            swarp_conf = os.path.join(detection_path, f'{field}_config.swarp')

            # Get combine images list
            image_list = os.path.join(detection_path, 'combine_images.txt')

            # Prepare swarp cmd
            cmd = f"{conf['path_to_swarp']} @{image_list} -c {swarp_conf}"

            ut.printlog("$ "+cmd, log_file, color = "cyan")

            # Run swarp
            os.system(cmd)

        else:
            ut.printlog(f"File {det_image_file} already exists.", log_file,
                        color = white, attrs=["dark"])
    else:
        ut.printlog(f"File {det_image_fz} already exists.", log_file,
                    color = "white", attrs=["dark"])


generate_detection_image()


# ***************************************************
#    Update Detection Image Header
# ***************************************************

def update_detection_header():

    """
    Update detection image header
    """

    print("")
    ut.printlog(('********** '
                 'Updating detection image header '
                 '**********'),
                log_file, color = "yellow")
    print("")

    # Get detection image file
    det_image_name = f"{field}_detection.fits"
    det_image_file = os.path.join(detection_path, det_image_name)

    # Get list of comined images
    image_list = os.path.join(detection_path, f'combine_images.txt')

    # Create header update control file
    header_log = os.path.join(detection_path, 'updated_header.txt')

    if not os.path.exists(header_log):

        ut.update_detection_header(detection_image = det_image_file,
                                   image_list_file = image_list)

        ut.printlog("Detection header was updated.", log_file)

        with open(header_log, 'w') as f:
            f.write("Detection header was updated.")

    else:
        ut.printlog("Detection header already updated.", log_file,
                    color = "white", attrs=["dark"])


update_detection_header()

# ***************************************************
#    Generate Detection SExconfig file
# ***************************************************


def generate_detection_sexconfig_file():

    """
    Generate detection image sexconfig file
    """

    print("")
    ut.printlog(('********** '
                 'Generating detection image photometry config files '
                 '**********'),
                log_file, color = "yellow")
    print("")

    # Default SExconfig and SExparam files
    default_sexconfig = conf['sex_config']
    default_sexparam = conf['sex_param']

    conf_file_name = f"{field}_detection.sex"
    save_file = os.path.join(detection_path, conf_file_name)

    # Generate location of output catalog file
    catalog_name = f"sex_{field}_detection_catalog.fits"
    catalog_file = os.path.join(detection_path, catalog_name)

    # Get location of image file
    image_name = f"{field}_detection.fits"
    image_file = os.path.join(detection_path, image_name)

    segm_image = image_file.replace(".fits", ".segm.fits")
    aper_image = image_file.replace(".fits", ".aper.fits")

    if not os.path.exists(save_file):

        ut.get_sex_config(save_file=save_file,
                          default_sexconfig=default_sexconfig,
                          default_sexparam=default_sexparam,
                          catalog_file=catalog_file,
                          image_file=image_file,
                          inst_zp=conf['inst_zp'],
                          path_to_sex=conf['path_to_sex'],
                          use_weight=conf['use_weight'],
                          mode='single',
                          check_segima=segm_image,
                          check_aperima=aper_image)

        ut.printlog(f"Generated detection image sexconfig for field {field}",
                    log_file, color = "green")

    else:
        ut.printlog(("Detection image sexconfig already obtained for field "
                     f"{field}"), log_file, color = "white", attrs=["dark"])


generate_detection_sexconfig_file()

# ***************************************************
#    Generate SExconfig files
# ***************************************************


def generate_dual_sexconfig_files():

    """
    Generate dual mode sexconfig file for all filters
    """

    print("")
    ut.printlog(('********** '
                 'Generating Dual Photometry config files '
                 '**********'),
                 log_file, color = "yellow")
    print("")

    # Default SExconfig and SExparam files
    default_sexconfig = conf['sex_config']
    default_sexparam  = conf['sex_param']

    # Generate configuration for each filter
    for filt in conf['filters']:

        # Generate location of config file
        conf_file_name = f"{field}_{filt}_dual.sex"
        save_file = os.path.join(sexconf_path, conf_file_name)

        # Generate location of output catalog file
        catalog_name = f"sex_{field}_{filt}_dual.fits"
        catalog_file = os.path.join(catalogs_path, catalog_name)

        # Get location of image file
        image_name = f"{field}_{filt}_swp.fits"
        image_file = os.path.join(images_path, image_name)

        # Get location of detection image file
        detection_name = f"{field}_detection.fits"
        detection_file = os.path.join(detection_path, detection_name)

        if not os.path.exists(save_file):

            ut.get_sex_config(save_file = save_file,
                              default_sexconfig = default_sexconfig,
                              default_sexparam  = default_sexparam,
                              catalog_file      = catalog_file,
                              image_file        = image_file,
                              inst_zp           = conf['inst_zp'],
                              path_to_sex       = conf['path_to_sex'],
                              use_weight        = conf['use_weight'],
                              mode              = 'dual',
                              detection_file    = detection_file)

            ut.printlog(("Generated dual mode sexconfig for field "
                         f"{field}, filter {filt}"), log_file,
                         color = "green")

        else:
            ut.printlog(("Dual mode sexconfig already obtained for field "
                         f"{field}, filter {filt}"), log_file,
                         color = "white", attrs=["dark"])

    # Copy sexparam file to field config directory (for proper documentation)
    cmd = f'cp {default_sexparam} {sexconf_path}'
    ut.printlog("$ "+cmd, log_file, color = "green")
    os.system(cmd)


generate_dual_sexconfig_files()

# ***************************************************
#    Run SExtractor in Detection image
# ***************************************************


def run_sex_detection():

    """
    Run SExtractor in Detection image
    """

    print("")
    ut.printlog(('********** '
                 'Running SeX on detection image '
                 '**********'),
                 log_file, color = "yellow")
    print("")

    # Generate location of output catalog file
    catalog_name = f"sex_{field}_detection_catalog.fits"
    catalog_file = os.path.join(detection_path, catalog_name)

    if not os.path.exists(catalog_file):

        # Get location of image file
        image_name = f"{field}_detection.fits"
        image_file = os.path.join(detection_path, image_name)

        # Get location of sexconfig file
        conf_file_name = f"{field}_detection.sex"
        sexconf_file   = os.path.join(detection_path, conf_file_name)

        # Run SExtractor
        sex_location = os.path.join(conf['path_to_sex'], 'src', 'sex')

        cmd = f"{sex_location} {image_file} -c {sexconf_file}"
        cmd += " -PHOT_APERTURES '5.45455, 36.363636'"
        ut.printlog("$ "+cmd, log_file, color = "cyan")
        os.system(cmd)

    else:
        ut.printlog(("Detection image photometry already obtained for field "
                     f"{field}"), log_file, color = "white", attrs = ["dark"])


run_sex_detection()


# ***************************************************
#    Run SExtractor in Dual Mode
# ***************************************************

def run_sex_dual():

    """
    Run SExtractor in Dual mode for all filters
    """

    print("")
    ut.printlog(('********** '
                 'Running SeX in dual mode '
                 '**********'),
                 log_file, color = "yellow")
    print("")

    for filt in conf['filters']:

        # Generate location of output catalog file
        catalog_name = f"sex_{field}_{filt}_dual.fits"
        catalog_file = os.path.join(catalogs_path, catalog_name)

        if not os.path.exists(catalog_file):

            # Get location of image file
            image_name = f"{field}_{filt}_swp.fits"
            image_file = os.path.join(images_path, image_name)

            # Get location of detection image file
            detection_name = f"{field}_detection.fits"
            detection_file = os.path.join(detection_path, detection_name)

            # Generate location of config file
            conf_file_name = f"{field}_{filt}_dual.sex"
            sexconf_file   = os.path.join(sexconf_path, conf_file_name)

            # Run SExtractor
            sex_location = os.path.join(conf['path_to_sex'], 'src', 'sex')

            cmd = (f"{sex_location} {detection_file}, {image_file} "
                   f"-c {sexconf_file}")

            ut.printlog("$ "+cmd, log_file, color = "cyan")
            os.system(cmd)

        else:
            ut.printlog(("Dual mode photometry already obtained for field "
                         f"{field}, filter {filt}"), log_file,
                         color = "white", attrs = ["dark"])


run_sex_dual()

# ***************************************************
#    Convert detection .fits to .fz
# ***************************************************


def convert_detection_fits_to_fz():

    """
    Converts detection image, detection weight, detection .aper and
    detection .segm from .fits to .fz

    Then, remove the .fits files.
    """

    print("")
    ut.printlog(('********** '
                 'Converting detection .fits to .fz '
                 '**********'),
                 log_file, color = "yellow")
    print("")

    det_image_name = f"{field}_detection.fits"
    det_image_file = os.path.join(detection_path, det_image_name)

    det_weight_file = det_image_file.replace(".fits", "weight.fits")
    det_aper_file   = det_image_file.replace(".fits", ".aper.fits")
    det_segm_file   = det_image_file.replace(".fits", ".segm.fits")

    images = [det_image_file, det_weight_file, det_aper_file, det_segm_file]
    names  = ['Detection', 'Detection weight', 'Detection aper',
              'Detection segm']

    for image, name in zip(images, names):
        if not os.path.exists(image+'.fz'):

            # Compress fits
            cmd = f"fpack {image}"
            ut.printlog("$ " + cmd, log_file, color = "cyan")
            os.system(cmd)

        else:
            ut.printlog(f"{name} image already compressed.", log_file,
                        color = "white", attrs = ["dark"])

        if os.path.exists(image + '.fz'):
            # Remove fits
            cmd = f"rm {image}"
            ut.printlog("$ " + cmd, log_file, color = "red")
            os.system(cmd)

        else:
            ut.printlog(f"{name} fits image already deleted.", log_file,
                        color = "white", attrs = ["dark"])


convert_detection_fits_to_fz()

# ***************************************************
#    Make diagnostic plots
# ***************************************************

def dual_diagnostic_plots():

    """
    Makes diagnostic plots of the resulting catalogs
    """

    print("")
    ut.printlog(('********** '
                 'Making diagnostic plots for dual mode photometry'
                 '**********'),
                log_file, color = "yellow")
    print("")

    for filt in conf['filters']:

        # Generate location of output catalog file
        catalog_name = f"sex_{field}_{filt}_dual.fits"
        catalog_file = os.path.join(catalogs_path, catalog_name)

        save_name = f"{field}_{filt}_dual.png"
        save_file = os.path.join(catalogs_path, save_name)

        conf_file_name = f"{field}_{filt}_dual.sex"
        sexconf_file = os.path.join(sexconf_path, conf_file_name)

        if not os.path.exists(save_file):

            ut.plot_sex_diagnostic(catalog   = catalog_file,
                                   save_file = save_file,
                                   s2ncut    = conf['apercorr_s2ncut'],
                                   starcut   = conf['apercorr_starcut'],
                                   sexconf   = sexconf_file,
                                   filt      = filt)

            ut.printlog(f"Created file {save_file}", log_file,
                        color = "green")

        else:
            ut.printlog(("Diagnostic plots already made for field "
                         f"{field}, filter {filt}"), log_file,
                         color = "white", attrs = ["dark"])


dual_diagnostic_plots()


ut.printlog("COMPLETED DUAL MODE PHOTOMETRY", log_file, 
        color = "yellow", attrs=["bold", "reverse"])
