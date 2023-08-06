# -*- coding: utf-8 -*-

# ******************************************************************************
#                          S-PLUS CALIBRATION PIPELINE
#                               sed_fitting.py
# ******************************************************************************

"""
Functions related to the SED fitting process used by the calibration pipeline
to predict S-PLUS magnitudes

--------------------------------------------------------------------------------
   FUNCTIONS:
--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
   COMMENTS:
--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
   USAGE:
--------------------------------------------------------------------------------
improt sed_fitting as sf
----------------
"""


################################################################################
# Import external packages
import os.path
import sys
import numpy as np
import pandas as pd
from time import time
from astropy.table import Table

################################################################################
# Define functions

def get_chi2(model_ref_mag_array, ref_mag_array, ref_magerr_array):

    # Shift the models
    shift_array = ref_mag_array - model_ref_mag_array
    shift_array = shift_array.mean(axis = 1).reshape(-1,1)

    shifted_model_ref_mag_array = model_ref_mag_array + shift_array

    chi2 = (shifted_model_ref_mag_array - ref_mag_array) ** 2 / ref_magerr_array

    # Sum over all colors
    chi2 = chi2.sum(axis=1)

    return chi2


# *************************************************************
#   Absolute shift for model mags
# *************************************************************
def get_mag_shift(model_ref_mag_array, best_model_id, ref_mag_array):
    bestmod_ref_mag_array = model_ref_mag_array[best_model_id, :]
    delta_mags = ref_mag_array - bestmod_ref_mag_array

    mag_shift = np.mean(delta_mags)

    return mag_shift


# *************************************************************
#   Evaluate best model
# *************************************************************
def get_best_model(models, data, ref_mag_cols, pred_mag_cols=None,
                   bayesian = False):

    # Slice models array to get only reference magnitudes
    model_ref_mag_array = models.loc[:, ref_mag_cols].values

    # Slice data array to get only reference magnitudes
    ref_mag_array = data.loc[ref_mag_cols].values

    # Slice data array to get only reference magnitudes errors
    ref_magerr_cols = get_ref_magerr_cols(ref_mag_cols)
    ref_magerr_array = data.loc[ref_magerr_cols].values

    # Only used for the output
    if pred_mag_cols is not None:
        # Slice data array to get only S-PLUS magnitudes
        pred_mag_array = data.loc[pred_mag_cols].values

        # Slice data array to get only S-PLUS magnitudes errors
        pred_magerr_cols = get_ref_magerr_cols(pred_mag_cols)
        pred_magerr_array = data.loc[pred_magerr_cols].values

    # Calculate chi2 for each model
    chi2 = get_chi2(model_ref_mag_array=model_ref_mag_array,
                    ref_mag_array=ref_mag_array,
                    ref_magerr_array=ref_magerr_array)

    # Get the best model id
    if bayesian:
        prior = models['prior'].values
        posterior = [prior[i] * np.exp(-chi2[i]/2) for i in range(len(chi2))]

        best_model_id = np.argmax(posterior)

    else:
        best_model_id = np.argmin(chi2)

    # Calculate chi2 for each model
    mag_shift = get_mag_shift(model_ref_mag_array=model_ref_mag_array,
                              best_model_id=best_model_id,
                              ref_mag_array=ref_mag_array)

    # Get best model
    best_model = models.iloc[best_model_id, :]

    # Generate the output list
    output_list = [best_model.loc['model_id']]
    output_list += [best_model.loc['Teff']]
    output_list += [best_model.loc['logg']]
    output_list += [best_model.loc['FeH']]
    output_list += [best_model.loc['aFe']]
    output_list += [best_model.loc['EB_V']]
    output_list += [chi2[best_model_id]]
    output_list += [mag_shift]

    # Add reference magnitudes to the output
    for mag_ref, magerr_ref in zip(ref_mag_array, ref_magerr_array):
        output_list += [mag_ref]
        output_list += [magerr_ref]

    #if pred_mag_cols is not None:
    #    # Add splus magnitudes to the output
    #    for mag_ref, magerr_ref in zip(pred_mag_array, pred_magerr_array):
    #        output_list += [mag_ref]
    #        output_list += [magerr_ref]

    # Add to-predict magnitudes to the output
    if pred_mag_cols is not None:
        for i in range(len(pred_mag_cols)):
            pred_mag_col = pred_mag_cols[i]
            if pred_mag_col not in ref_mag_cols:
                output_list += [pred_mag_array[i]]
                output_list += [pred_magerr_array[i]]

    # Add model predicted magnitudes to the output, applying the shift
    for model_mag_ref in ref_mag_cols:
        output_list += [best_model.loc[model_mag_ref] + mag_shift]

    if pred_mag_cols is not None:
        for i in range(len(pred_mag_cols)):
            model_mag_pred = pred_mag_cols[i]
            if model_mag_pred not in ref_mag_cols:
                output_list += [best_model.loc[model_mag_pred] + mag_shift]

    # turn output into array
    output = np.array(output_list)

    return output


# *************************************************************
#   Load models
# *************************************************************
def load_models(models_file):
    # must load the file with the models and put it in a pd dataframe
    models = pd.read_csv(models_file, delim_whitespace=True, escapechar='#')
    models.columns = models.columns.str.replace(' ', '')

    return models

# *************************************************************
#   Load data
# *************************************************************


def load_data(data_file):

    # If necessary, transform from fits table to data frame
    if os.path.splitext(data_file)[1] == '.fits':
        fits_data = Table.read(data_file, format='fits')
        ref_data  = fits_data.to_pandas()

    else:
        ref_data = pd.read_csv(data_file, delim_whitespace=True, escapechar='#',
                               skipinitialspace=True)

    ref_data.columns = ref_data.columns.str.replace(' ', '')

    return ref_data


# *************************************************************
#   Get colnames for the errors
# *************************************************************
def get_ref_magerr_cols(ref_mag_cols):
    ref_magerr_cols = []

    for col in ref_mag_cols:
        ref_magerr_cols.append(col + '_err')

    return ref_magerr_cols


# *************************************************************
#   Fit model mags and save to a file
# *************************************************************
def get_model_mags(models_file, data_file, save_file,
                   ref_mag_cols, pred_mag_cols=None,
                   bayesian=False, ebv_cut=None):
    """
    Fit model mags to a reference catalog and predict the values of magnitudes
    for another filter system


    Parameters
    ----------
    models_file: str
        path to file with model magnitudes

    data_file: str
        path to file with reference magnitudes

    save_file: str
        path to the output file

    ref_mag_cols: tuple
        list of magnitudes names to be used to fit the models

    pred_mag_cols: tuple
        list of magnitudes names to be predicted by the models.

    bayesian: bool
        If true, best model is selected from the maximization of the posterior,
        otherwise, minimization of chi2.

    ebv_cut: float
        if not None, only models with EB_V = EBV_cut will be considered

    Returns
    -------
    Generates output file with predicted magnitudes

    """

    t0 = time()

    # load models
    print('Loading models from file %s' % models_file)
    models = load_models(models_file)

    if ebv_cut is not None:
        filt = models['EB_V'] == ebv_cut
        models = models[filt]

    # load data
    print('Loading data from file %s' % data_file)
    data = load_data(data_file)

    print('\nReference magnitudes being used are:')
    print(ref_mag_cols)

    ref_magerr_cols = get_ref_magerr_cols(ref_mag_cols)

    if pred_mag_cols is not None:
        pred_magerr_cols = get_ref_magerr_cols(pred_mag_cols)
        print('\nMagnitudes being predicted are:')
        print(pred_mag_cols)

    # Create output array

    Nlines = data.shape[0]
    Ncols = 4  # RA, DEC, X, Y
    Ncols += 8  # model_id, Teff, logg, FeH, aFe, EB_V, chi2, mag_shift
    Ncols += 3 * len(ref_mag_cols)  # mag_ref, mag_ref_err, mag_ref_model

    if pred_mag_cols is not None:
        for i in range(len(pred_mag_cols)):
            mag_name = pred_mag_cols[i]
            if mag_name not in ref_mag_cols:
                Ncols += 3

    output = np.full((Nlines, Ncols), np.nan)

    print('\n\nStarting to fit best model for each star ')

    # Obtain model mags for each star in data
    for i in range(Nlines):
        sys.stdout.write('\rFinding best model for star {0} of {1}'.format(i + 1,
                                                                           Nlines))
        sys.stdout.flush()

        # Put Model data in the output array
        output[i, 4:] = get_best_model(models=models,
                                       data=data.iloc[i, :],
                                       ref_mag_cols=ref_mag_cols,
                                       pred_mag_cols=pred_mag_cols,
                                       bayesian=bayesian)

    print('\n\nFinished estimating best model for {0} stars'.format(Nlines))

    output[:, 0] = data.loc[:, 'RAJ2000'].values
    output[:, 1] = data.loc[:, 'DEJ2000'].values
    output[:, 2] = data.loc[:, 'X'].values
    output[:, 3] = data.loc[:, 'Y'].values

    with open(save_file, 'w') as f:
        f.write('# RAJ2000 DEJ2000 X Y model_id Teff logg FeH aFe EB_V chi2 model_mag_shift')
        fmt = ['%.6f', '%.6f', '%.6f', '%.6f', '%d', '%d', '%.1f', '%.2f', "%.2f", '%.3f', '%.3f', '%.3f']

        for mag_name, mag_err_name in zip(ref_mag_cols, ref_magerr_cols):
            fmt += ['%.3f', '%.3f']
            f.write(' {0} {1}'.format(mag_name, mag_err_name))

        if pred_mag_cols is not None:
            #for mag_name, mag_err_name in zip(pred_mag_cols, pred_magerr_cols):
            #    fmt += ['%.3f', '%.3f']
            #    f.write(' {0} {1}'.format(mag_name, mag_err_name))
            for i in range(len(pred_mag_cols)):
                mag_name = pred_mag_cols[i]
                mag_err_name = pred_magerr_cols[i]
                if mag_name not in ref_mag_cols:
                    fmt += ['%.3f', '%.3f']
                    f.write(' {0} {1}'.format(mag_name, mag_err_name))

        for mag_name in ref_mag_cols:
            fmt += ['%.3f']
            f.write(' %s_mod' % mag_name)

        if pred_mag_cols is not None:
            for i in range(len(pred_mag_cols)):
                mag_name = pred_mag_cols[i]
                if mag_name not in ref_mag_cols:
                    fmt += ['%.3f']
                    f.write(' %s_mod' % mag_name)

        f.write('\n')
        np.savetxt(f, output, fmt=fmt)

    print('Results saved in file %s' % save_file)

    dt = time() - t0
    print ("\nThe minchi2 model magnitudes script took "
           "{0} seconds to find the best model for {1} stars".format(dt,
                                                                     Nlines))

    return output


# *************************************************************
#   save model fitting data
# *************************************************************
def save_data(output, save_file, ref_mag_cols, ref_magerr_cols,
              splus_mag_cols, splus_magerr_cols):

    with open(save_file, 'w') as f:
        f.write('# RA DEC model_id EB_V chi2')
        fmt = ['%.6f', '%.6f', '%d', '%.3f', '%.3f']

        for mag_name, mag_err_name in zip(ref_mag_cols, ref_magerr_cols):
            fmt += ['%.3f', '%.3f']
            f.write(' {0} {1}'.format(mag_name, mag_err_name))

        if splus_mag_cols is not None:
            for mag_name, mag_err_name in zip(splus_mag_cols, splus_magerr_cols):
                fmt += ['%.3f', '%.3f']
                f.write(' {0} {1}'.format(mag_name, mag_err_name))

        for mag_name in ref_mag_cols:
            fmt += ['%.3f']
            f.write(' %s_mod' % mag_name)

        if splus_mag_cols is not None:
            for mag_name in splus_mag_cols:
                fmt += ['%.3f']
                f.write(' %s_mod' % mag_name)

        f.write('\n')

        np.savetxt(f, output, fmt=fmt)
