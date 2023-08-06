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

save_file = os.path.join(calibration_path, f'{field}_plots_PSF.png')

if os.path.exists(save_file):
    # Copy to quality_path
    if quality_path:
        
        suffix = ut.calibration_suffix(conf)
        extinction = conf['extinction_correction']
        save_file_quality_path = os.path.join(quality_path,
                                              f'{field}_{suffix}_{extinction}_PSF.png')
        
        cmd = f"cp {save_file} {save_file_quality_path}"
        os.system(cmd)

    msg = "quality plot already exists and will not be made again"
    raise FileExistsError(msg)

################################################################################
# Initiallize plots

nrow = 2
ncol = 3

fig, axs = plt.subplots(nrow, ncol, figsize=[15,10.5])
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
# Plot psf mode detections

def plot_psf_mode_detections():

    psf_master = os.path.join(photometry_path, 'psf', 'master',
                                 f"{field}_master_photometry_only_psf.fits")

    # Load catalog
    psf_master_data = ut.load_data(psf_master)

    x = psf_master_data.loc[:,'X'].values
    y = psf_master_data.loc[:,'Y'].values

    axs[0,0].scatter(x,y, s = 0.5, alpha = 0.1)
    axs[0,0].set_xlabel("X")
    axs[0,0].set_ylabel("Y")
    axs[0,0].set_xlim([0, 11000])
    axs[0,0].set_ylim([0, 11000])

    axs[0,0].text(100, 10500, 'Photometry master [psf]')
    axs[0,0].text(100, 100, f'N_sources: {len(psf_master_data)}')
try:
    plot_psf_mode_detections()
except:
    pass


################################################################################
# Plot crossmatch

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

    axs[0,1].scatter(x,y, s = 2, alpha = 1)
    axs[0,1].set_xlabel("X")
    axs[0,1].set_ylabel("Y")
    axs[0,1].set_xlim([0, 11000])
    axs[0,1].set_ylim([0, 11000])

    txt = (f"Crossmatch [ {conf['calibration_photometry']} | "
           f"{' '.join(conf['reference_catalog'])} | "
           f"{conf['extinction_correction']} ]")
    axs[0,1].text(100, 10500, txt)
    axs[0,1].text(100, 100, f'N_sources: {len(crossmatch_data)}')

try:
    plot_crossmatch()
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

    ax = axs[0,2]
    ax.set_xlim([11,21])
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
# Plot color-color 1

def plot_color_color_1():

    ax = axs[1,0]
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

    ax.scatter(x_cat, y_cat, color = "#FF5F00", s = 5, alpha = 0.2, zorder = 1)

try:
    plot_color_color_1()
except:
    pass

################################################################################
# Plot color-color 2

def plot_color_color_2():

    ax = axs[1,1]
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

    ax.scatter(x_cat, y_cat, color = "#FF5F00", s = 5, alpha = 0.2, zorder = 1)

try:
    plot_color_color_2()
except:
    pass


################################################################################
# Plot color-color 3

def plot_color_color_3():

    ax = axs[1,2]
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

    ax.scatter(x_cat, y_cat, color = "#FF5F00", s = 5, alpha = 0.2, zorder = 1)

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
                                         f'{field}_{suffix}_{extinction}.png')

    plt.savefig(save_file_quality_path)


plt.clf()
plt.close()
