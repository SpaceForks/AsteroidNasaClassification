import numpy as np
import pandas as pd
import scipy.interpolate
import os
import sys
from SMASS import *

# FIXME FIXME FIXME
mean_spectra_filepath = '/tmp/busdemeo-meanspectra.csv'
dmeanspec = pd.read_csv(mean_spectra_filepath, skiprows=1)

def clean_data(d):
    mn = d.flux.mean()
    sd = d.flux.std()
    d_no_outlier = d[np.abs(d.flux - mn)/sd < 3]
    return d_no_outlier.groupby('wavelength').apply(lambda x: x.mean())
    
def normalize(v, to=1.0):
    return (v-v.min())/ (v.max()-v.min()) * to
    
def get_interpolater(v_wavelength, v_flux):
    return scipy.interpolate.interp1d(v_wavelength, v_flux, 'cubic')

def classify(v_wavelength, v_flux, nbest=5):
    interpolater = get_interpolater(v_wavelength, v_flux)

    dresult = {}
    dmeanspec.Wavelength
    for col in dmeanspec.columns:
        if col == 'Wavelength':
            continue
        matched_flux = interpolater(dmeanspec.Wavelength)
        dresult[col] = ((normalize(matched_flux) - normalize(dmeanspec[col]))**2).mean()
    
    # pick the best
    res = [(diff, name) for name, diff in dresult.items()]
    res.sort()
    return [(v,k) for k,v in res][:nbest]



if __name__ == '__main__':

    import matplotlib.pyplot as plt

    input_filepath = os.path.expanduser('~/Dropbox/devsync/dataproc/data/smass_catalog/data/spex/sp41/a000001.sp41.txt')
    d = clean_data(smass_text_file_to_dataframe(input_filepath))
    res = classify(d.wavelength, d.flux)

    legend_text = []
    best = None
    for name,diff in res[:5]:
        print name,'\t',diff
        legend_text.append(name)
        if best is None:
            best = name

        plt.plot(dmeanspec.Wavelength, normalize(dmeanspec[name]))

    # FIXME rerun slow stuff :-(
    interpolater = get_interpolater(d.wavelength, d.flux)
    plt.scatter(dmeanspec.Wavelength, normalize(interpolater(dmeanspec.Wavelength)))
    legend_text.append('target')
    plt.legend(legend_text)
    plt.show()
