# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                               quality_check.py
#            Produces the quality check plot in the end of the pipeline
# ******************************************************************************

"""
Produces the quality check plot in the end of the pipeline

The S-PLUS field is given as the first command line argument. Configurations
are set in the config file, given as the second command line argument.

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------
Ideally this script should only be run through the pipeline.py script.

Assumes that all calibration steps have been run for this field

--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
$python3 quality_check.py *field_name* *config_file*

----------------
"""

################################################################################
# Import external packages

import os
import sys
import numpy as np
from matplotlib import pyplot as plt
from astropy.table import Table

pipeline_path = os.path.split(__file__)[0]
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

try:
    quality_path = sys.argv[3]
except IndexError:
    quality_path = conf['quality_path'] 


################################################################################
# Get directories
suffix = ut.calibration_suffix(conf)

field_path       = os.path.join(conf['run_path'], field)
photometry_path  = os.path.join(field_path, 'Photometry')
crossmatch_path  = os.path.join(field_path, 'Crossmatch')
calibration_path = os.path.join(field_path, f'Calibration_{suffix}')

################################################################################
# Check if plot already exists

save_file = os.path.join(calibration_path, f'{field}_plots.png')

if os.path.exists(save_file):
    # Copy to quality_path
    if quality_path:
        
        suffix = ut.calibration_suffix(conf)
        save_file_quality_path = os.path.join(quality_path,
                                              f'{field}_{suffix}.png')
        
        cmd = f"cp {save_file} {save_file_quality_path}"
        os.system(cmd)

    msg = "quality plot already exists and will not be made again"
    raise FileExistsError(msg)

################################################################################
# Initiallize plots

nrow = 3
ncol = 4

fig, axs = plt.subplots(nrow, ncol, figsize=[20,15.5])
for ax in fig.axes:
    ax.tick_params(labelrotation=90, axis = 'y')

fig.suptitle(field, fontsize=14)

plt.subplots_adjust(top=0.95)

filt_colors = {'U': "#d600a6",
               'F378': "#c300bc",
               'F395': "#a700ce",
               'F410': "#8300de",
               'F430': "#3e00f3",
               'G': "#00c1ff",
               'F515': "#17ff00",
               'R': "#ff5f00",
               'F660': "#f80000",
               'I': "#cb0000",
               'F861': "#a30000",
               'Z': "#9b0000"}

################################################################################
# Plot single mode detections

def plot_single_mode_detections():

    single_master = os.path.join(photometry_path, 'single', 'master',
                                 f"{field}_master_photometry_only_single.fits")

    # Load catalog
    single_master_data = ut.load_data(single_master)

    x = single_master_data.loc[:,'X'].values
    y = single_master_data.loc[:,'Y'].values

    axs[0,0].scatter(x,y, s = 0.5, alpha = 0.1)
    axs[0,0].set_xlabel("X")
    axs[0,0].set_ylabel("Y")
    axs[0,0].set_xlim([0, 11000])
    axs[0,0].set_ylim([0, 11000])

    axs[0,0].text(100, 10500, 'Photometry master [single]')
    axs[0,0].text(100, 100, f'N_sources: {len(single_master_data)}')

try:
    plot_single_mode_detections()
except:
    pass

################################################################################
# Plot dual mode detections

def plot_dual_mode_detections():

    dual_master = os.path.join(photometry_path, 'dual', 'master',
                                 f"{field}_master_photometry_only_dual.fits")

    # Load catalog
    dual_master_data = ut.load_data(dual_master)

    x = dual_master_data.loc[:,'X'].values
    y = dual_master_data.loc[:,'Y'].values

    axs[0,1].scatter(x,y, s = 0.5, alpha = 0.1)
    axs[0,1].set_xlabel("X")
    axs[0,1].set_ylabel("Y")
    axs[0,1].set_xlim([0, 11000])
    axs[0,1].set_ylim([0, 11000])

    axs[0,1].text(100, 10500, 'Photometry master [dual]')
    axs[0,1].text(100, 100, f'N_sources: {len(dual_master_data)}')
try:
    plot_dual_mode_detections()
except:
    pass

################################################################################
# Plot psf mode detections

def plot_psf_mode_detections():

    psf_master = os.path.join(photometry_path, 'psf', 'master',
                                 f"{field}_master_photometry_only_psf.fits")

    # Load catalog
    psf_master_data = ut.load_data(psf_master)

    x = psf_master_data.loc[:,'X'].values
    y = psf_master_data.loc[:,'Y'].values

    axs[0,2].scatter(x,y, s = 0.5, alpha = 0.1)
    axs[0,2].set_xlabel("X")
    axs[0,2].set_ylabel("Y")
    axs[0,2].set_xlim([0, 11000])
    axs[0,2].set_ylim([0, 11000])

    axs[0,2].text(100, 10500, 'Photometry master [psf]')
    axs[0,2].text(100, 100, f'N_sources: {len(psf_master_data)}')
try:
    plot_psf_mode_detections()
except:
    pass


################################################################################
# Plot psf mode detections

def plot_crossmatch():

    correction = conf['extinction_correction']

    suffix = ut.calibration_suffix(conf)

    crossmatch_name = ut.crossmatch_catalog_name(field, conf)
    crossmatch_name = crossmatch_name.replace(".fits",
                                              f"_ebvcorr_{correction}.fits")

    crossmatch = os.path.join(crossmatch_path, crossmatch_name)

    # Load catalog
    crossmatch_data = ut.load_data(crossmatch)

    x = crossmatch_data.loc[:,'X'].values
    y = crossmatch_data.loc[:,'Y'].values

    axs[0,3].scatter(x,y, s = 2, alpha = 1)
    axs[0,3].set_xlabel("X")
    axs[0,3].set_ylabel("Y")
    axs[0,3].set_xlim([0, 11000])
    axs[0,3].set_ylim([0, 11000])

    txt = (f"Crossmatch [ {conf['calibration_photometry']} | "
           f"{' '.join(conf['reference_catalog'])} | "
           f"{conf['extinction_correction']} ]")
    axs[0,3].text(100, 10500, txt)
    axs[0,3].text(100, 100, f'N_sources: {len(crossmatch_data)}')

try:
    plot_crossmatch()
except:
    pass


################################################################################
# Plot FWHM det

def plot_fwhm():

    mag_cut = [10,25]

    detection = os.path.join(photometry_path, 'dual', 'detection',
                             f'sex_{field}_detection_catalog.fits')

    # Load catalog
    detection_data = Table.read(detection)

    select, medianFWHM = ut.star_selector(catalog=detection_data,
                                          s2ncut=conf['apercorr_s2ncut'],
                                          starcut=conf['apercorr_starcut'],
                                          mag_partition=2,
                                          verbose=False)

    sexconf = os.path.join(photometry_path, 'dual', 'detection',
                             f'{field}_detection.sex')

    fwhm_config = ut.get_sexconf_fwhm(sexconf=sexconf)
    fwhm_estimated = medianFWHM * 3600

    ax = axs[1,0]
    ax.scatter(select['MAG_AUTO'], select['FWHM_WORLD'] * 3600,
               c="#2266FF", s=10, alpha=0.3, zorder=2)

    ax.scatter(detection_data['MAG_AUTO'],
                     detection_data['FWHM_WORLD'] * 3600,
                     c="#AAAAAA", s=10, alpha=0.1)

    ax.plot([mag_cut[0], mag_cut[1]], [fwhm_config, fwhm_config],
                color="#FF6622", zorder=1,
                label=r"FWHM$_{\mathrm{config}}$" + f": {fwhm_config:.3f}")

    ax.plot([mag_cut[0], mag_cut[1]], [fwhm_estimated, fwhm_estimated],
                color="#22AA66", zorder=1,
                label=r"FWHM$_{\mathrm{det_image}}$" + f": {fwhm_estimated:.3f}")

    ax.set_xlabel("MAG_DET_AUTO")
    ax.set_ylabel("FWHM [arcsec]")
    ax.set_xlim(mag_cut)
    ax.set_ylim([0, 10])

    ax.legend()

try:
    plot_fwhm()
except:
    pass

################################################################################
# Plot Growth curves (dual)

def plot_growth_curves():

    filters = conf['filters']
    ax = axs[1,1]

    aperture = conf['apercorr_diameter']
    max_aperture = conf['apercorr_max_aperture']
    maxy = 0.15
    miny = -0.5

    # max aperture
    ax.plot([max_aperture, max_aperture], [miny, maxy], '-', color='purple',
             linewidth = 0.5)

    ax.text(max_aperture, 0.05, f'{max_aperture:.3f}\ndiameter',
            color='purple', fontsize = 8)

    # base aperture
    ax.plot([aperture, aperture], [miny, maxy], '-', color='blue',
             linewidth = 0.5)

    ax.text(aperture, 0.05, f'{aperture:.3f}\ndiameter',
            color='blue', fontsize = 8)

    # region around zero
    ax.plot([0, 2*max_aperture], [0, 0], color='black', linewidth = 0.5)
    ax.fill_between([0, 2*max_aperture], [-1e-2, -1e-2], [1e-2, 1e-2],
                     color='black', alpha=0.1)

    for filt in filters:
        print(filt)
        color = filt_colors[filt]

        sexconf = os.path.join(photometry_path, 'dual', 'sexconf',
                             f'{field}_{filt}_dual.sex')

        apertures_list = ut.get_apertures_from_sexconf(sexconf)

        if 'correction_xy' in conf['run_steps']:
            catalog_dir = 'xy_correction'
            suffix = '_xycorr'
        else:
            catalog_dir = 'catalogs'
            suffix = ''

        catalog_file = os.path.join(photometry_path, 'dual', catalog_dir,
                                    f'sex_{field}_{filt}_dual{suffix}.fits')

        result, medianFWHM, starcount = ut.growth_curve(catalog=catalog_file,
                                               s2ncut=conf['apercorr_s2ncut'],
                                               starcut=conf['apercorr_starcut'],
                                               verbose=False)

        minmag2, minmag, medianmag, maxmag, maxmag2 = [x for x in result]

        diameter = [(a + b) / 2 for a, b in zip(apertures_list[:],
                                                apertures_list[1:])]

        # medians
        ax.plot(diameter, medianmag, color=color, linewidth = 0.5,
                label=f'{filt} ({starcount})')

        # CL68 & CL95
        ax.fill_between(diameter, minmag, maxmag, color=color, alpha=0.1)

    # Plot parameters
    ax.set_ylim([miny, maxy])
    ax.set_xlim([0, 1.2*max_aperture])

    # Labels
    ax.legend(loc=4, ncol = 2)
    ax.set_xlabel("Aperture Diameter (pix)")
    ax.set_ylabel("$m_{k+1} - m_{k}$")

try:
    plot_growth_curves()
except:
    pass


################################################################################
# Crossmatch dual and psf photometry

def crossmatch_dual_psf():

    dual_catalog = os.path.join(photometry_path, 'dual', 'master',
                                f'{field}_master_photometry_only_dual.fits')

    psf_catalog = os.path.join(photometry_path, 'psf', 'master',
                                f'{field}_master_photometry_only_psf.fits')

    save_file = os.path.join(crossmatch_path,
                             f'crossmatch_master_dual_psf.fits')

    if not os.path.exists(dual_catalog):
        raise ValueError(f"file {dual_catalog} does not exist.")

    if not os.path.exists(psf_catalog):
        raise ValueError(f"file {psf_catalog} does not exist.")

    if not os.path.exists(save_file):
        cmd  = f'java -jar {conf["path_to_stilts"]} tmatch2 '
        cmd += f'in1={dual_catalog} ifmt1=fits values1="RAJ2000 DEJ2000" '
        cmd += f'in2={psf_catalog} ifmt2=fits values2="RAJ2000 DEJ2000" '
        cmd += f'out={save_file} ofmt=fits '
        cmd += f'find=best join=1and2 matcher=sky params=1'

        print(cmd)
        os.system(cmd)


try:
    crossmatch_dual_psf()
except:
    pass


################################################################################
# Plot dual - psf photometry

def plot_dual_vs_psf():

    shift = [6,5,4,3,2,1,0,-1,-2,-3,-4,-5]

    catalog = os.path.join(crossmatch_path,
                           f'crossmatch_master_dual_psf.fits')

    catalog_data = ut.load_data(catalog)

    filters = conf['filters']
    ax = axs[1,2]
    ax.set_xlim([8,22])
    ax.set_ylim([-6,7])

    ax.set_xlabel("mag dual (PStotal)")
    ax.set_ylabel("mag dual - mag psf")

    ax.set_yticks([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6])
    ax.set_yticklabels(['', '', '', '', -1, 0, 1, '', '', '', '', ''],
                       minor=False)

    # Get zps
    zp_file = os.path.join(calibration_path, f'{field}_final.zp')
    zp_data = ut.zp_read(zp_file)

    for i in range(len(filters)):
        filt = filters[i]
        color = filt_colors[filt]

        zp_filt = zp_data[f'SPLUS_{filt}']-20

        ax.text(8.5, shift[i]+0.1, filt, color = color)

        mag_dual = catalog_data.loc[:,f'SPLUS_{filt}_1'].values + zp_filt
        mag_psf = catalog_data.loc[:,f'SPLUS_{filt}_2'].values + zp_filt

        delta = mag_dual - mag_psf
        f = np.abs(delta) < 1

        ax.scatter(mag_dual[f], delta[f]+shift[i], s = 2, alpha = 0.1,
                    color = color, zorder = 1)

        ax.plot([8,22],[shift[i],shift[i]], '--', color = 'black', alpha = 0.5,
                zorder = 0, linewidth = 0.5)

try:
    plot_dual_vs_psf()
except:
    pass

################################################################################
# Plot internal SED fitting


def plot_internal_sed_fitting():

    filters = conf['filters']
    shift = [6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5]
    mag_cut = conf['zp_fitting_mag_cut']

    sed_fit_file = os.path.join(calibration_path, 'internal',
                                f"{field}_mag_int.cat")

    cat_data = ut.load_data(sed_fit_file)

    ax = axs[1,3]
    ax.set_xlim([12,22])
    ax.set_ylim([-6,7])

    ax.set_xlabel("model mag")
    ax.set_ylabel("model mag - splus mag")

    ax.set_yticks([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6])
    ax.set_yticklabels(['', '', '', '', -0.5, 0, 0.5, '', '', '', '', ''],
                       minor=False)

    for i in range(len(filters)):
        filt = filters[i]
        color = filt_colors[filt]

        # Remove 99
        data_selection = np.abs(cat_data.loc[:, f'SPLUS_{filt}'] < 50)
        cat_data = cat_data[data_selection]

        ax.text(12.3, shift[i]+0.1, filt, color = color)

        ##############
        # Prepare data

        x = cat_data.loc[:, f'SPLUS_{filt}_mod']
        y = 2*(x - (cat_data.loc[:, f'SPLUS_{filt}']))

        dwarfs = cat_data.loc[:, 'logg'].values > 3
        selection = (x >= mag_cut[0]) & (x <= mag_cut[1]) & dwarfs

        ############################
        # Plot

        ax.scatter(x[selection], y[selection] + shift[i],
                   c=color, s=5, alpha=0.5, zorder=2)

        ax.scatter(x[~selection], y[~selection] + shift[i],
                   c="#666666", s=2, alpha=0.1, zorder=1)

        ax.plot([8,22],[shift[i],shift[i]], '--', color = 'black', alpha = 0.5,
                zorder = 0, linewidth = 0.5)

        ax.plot([mag_cut[0], mag_cut[0]], [-6,7],
                 color='#0066FF', linestyle='-', linewidth=0.5, zorder=6)

        ax.plot([mag_cut[1], mag_cut[1]], [-6,7],
                 color='#0066FF', linestyle='-', linewidth=0.5, zorder=6)


try:
    plot_internal_sed_fitting()
except:
    pass


################################################################################
# Plot internal SED fitting

def plot_class_star():

    detection = os.path.join(photometry_path, 'dual', 'detection',
                             f'sex_{field}_detection_catalog.fits')

    sexcat = Table.read(detection)
    starcut = conf['apercorr_starcut']
    s2ncut = conf['apercorr_s2ncut']
    mag_cut = [10,25]

    select, medianFWHM = ut.star_selector(catalog=sexcat,
                                          s2ncut=s2ncut,
                                          starcut=starcut,
                                          mag_partition=2,
                                          verbose=False)

    ax = axs[2,0]

    ax.scatter(sexcat['MAG_AUTO'], sexcat['CLASS_STAR'],
                   c="#AAAAAA", s=10, alpha=0.1)

    # Plot selection
    ax.scatter(select['MAG_AUTO'], select['CLASS_STAR'],
                   c="#2266FF", s=10, alpha=0.3,
                   label=f"s2ncut: {s2ncut}\n& starcut: {starcut}")

    # Plot cut line
    ax.hlines(starcut, mag_cut[0], mag_cut[1],
                  colors="#2266FF", zorder=1)

    # Plot grid lines
    ax.hlines(np.arange(-0.1, 1.1, 0.1), mag_cut[0], mag_cut[1],
                  colors="#EEEEEE", zorder=-1)

    ax.legend(loc=1)
    ax.set_xlim(mag_cut)
    ax.set_ylim([-0.1, 1.1])
    ax.set_ylabel('CLASS_STAR')
    ax.set_xlabel('MAG_AUTO (detection)')
    ax.minorticks_on()

try:
    plot_class_star()
except:
    pass

################################################################################
# Plot color-color 1

def plot_color_color_1():

    ax = axs[2,1]
    ax.set_xlim([0.75,3])
    ax.set_ylim([0.5,4])

    ax.set_xlabel("U - G")
    ax.set_ylabel("F378 - F660")

    stellar_locus_reference_file = conf['stellar_locus_reference']
    sl_ref = ut.load_data(stellar_locus_reference_file)

    # Plot reference stellar locus
    x_ref = sl_ref.loc[:,'SPLUS_U'].values - sl_ref.loc[:,'SPLUS_G'].values
    y_ref = sl_ref.loc[:,'SPLUS_F378'].values - sl_ref.loc[:,'SPLUS_F660'].values

    ax.scatter(x_ref, y_ref, color = "#AAAAAA", s = 2, alpha = 0.05, zorder = -1)

    # Load field data (calibrated and EB-V corrected)
    catalog_file = os.path.join(calibration_path, 'internal',
                                f'{field}_mag_int.cat')

    cat_data = ut.load_data(catalog_file)

    x1 = cat_data.loc[:,'SPLUS_U'].values
    x2 = cat_data.loc[:,'SPLUS_G'].values
    y1 = cat_data.loc[:,'SPLUS_F378'].values
    y2 = cat_data.loc[:,'SPLUS_F660'].values

    f = (x1 < 19) & (x2 < 19) & (y1 < 19) & (y2 < 19)

    x_cat = x1[f] - x2[f]
    y_cat = y1[f] - y2[f]

    ax.scatter(x_cat, y_cat, color = "#FF5F00", s = 5, alpha = 0.5, zorder = 1)

try:
    plot_color_color_1()
except:
    pass

################################################################################
# Plot color-color 2

def plot_color_color_2():

    ax = axs[2,2]
    ax.set_xlim([0.5,3.5])
    ax.set_ylim([0,3.5])

    ax.set_xlabel("F395 - R")
    ax.set_ylabel("F410 - F861")

    stellar_locus_reference_file = conf['stellar_locus_reference']
    sl_ref = ut.load_data(stellar_locus_reference_file)

    # Plot reference stellar locus
    x_ref = sl_ref.loc[:,'SPLUS_F395'].values - sl_ref.loc[:,'SPLUS_R'].values
    y_ref = sl_ref.loc[:,'SPLUS_F410'].values - sl_ref.loc[:,'SPLUS_F861'].values

    ax.scatter(x_ref, y_ref, color = "#AAAAAA", s = 2, alpha = 0.05, zorder = -1)

    # Load field data (calibrated and EB-V corrected)
    catalog_file = os.path.join(calibration_path, 'internal',
                                f'{field}_mag_int.cat')

    cat_data = ut.load_data(catalog_file)

    x1 = cat_data.loc[:,'SPLUS_F395'].values
    x2 = cat_data.loc[:,'SPLUS_R'].values
    y1 = cat_data.loc[:,'SPLUS_F410'].values
    y2 = cat_data.loc[:,'SPLUS_F861'].values

    f = (x1 < 19) & (x2 < 19) & (y1 < 19) & (y2 < 19)

    x_cat = x1[f] - x2[f]
    y_cat = y1[f] - y2[f]

    ax.scatter(x_cat, y_cat, color = "#FF5F00", s = 5, alpha = 0.5, zorder = 1)

try:
    plot_color_color_2()
except:
    pass


################################################################################
# Plot color-color 3

def plot_color_color_3():

    ax = axs[2,3]
    ax.set_xlim([0.3,2.5])
    ax.set_ylim([0,2])

    ax.set_xlabel("F430 - I")
    ax.set_ylabel("F515 - Z")

    stellar_locus_reference_file = conf['stellar_locus_reference']
    sl_ref = ut.load_data(stellar_locus_reference_file)

    # Plot reference stellar locus
    x_ref = sl_ref.loc[:,'SPLUS_F430'].values - sl_ref.loc[:,'SPLUS_I'].values
    y_ref = sl_ref.loc[:,'SPLUS_F515'].values - sl_ref.loc[:,'SPLUS_Z'].values

    ax.scatter(x_ref, y_ref, color = "#AAAAAA", s = 2, alpha = 0.05, zorder = -1)

    # Load field data (calibrated and EB-V corrected)
    catalog_file = os.path.join(calibration_path, 'internal',
                                f'{field}_mag_int.cat')

    cat_data = ut.load_data(catalog_file)

    x1 = cat_data.loc[:,'SPLUS_F430'].values
    x2 = cat_data.loc[:,'SPLUS_I'].values
    y1 = cat_data.loc[:,'SPLUS_F515'].values
    y2 = cat_data.loc[:,'SPLUS_Z'].values

    f = (x1 < 19) & (x2 < 19) & (y1 < 19) & (y2 < 19)

    x_cat = x1[f] - x2[f]
    y_cat = y1[f] - y2[f]

    ax.scatter(x_cat, y_cat, color = "#FF5F00", s = 5, alpha = 0.5, zorder = 1)

try:
    plot_color_color_3()
except:
    pass

plt.tight_layout()

plt.savefig(save_file)

if quality_path:
    suffix = ut.calibration_suffix(conf)
    extinction = conf['extinction_correction']
    save_file_quality_path = os.path.join(quality_path,
                                         f'{field}_{suffix}.png')

    plt.savefig(save_file_quality_path)


plt.clf()
plt.close()
