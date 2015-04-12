import numpy as np
import pandas as pd
import scipy.interpolate
import os
from os.path import join as pjoin, split as psplit, abspath as pabspath
import sys
from SMASS import *

mean_spectra_filepath = pabspath(pjoin(psplit(pabspath(__file__))[0],
                                       '..', 'static', 'busdemeo-meanspectra.csv'))
dmeanspec = pd.read_csv(mean_spectra_filepath, skiprows=1)

def clean_data(d):
    mn = d.reflectance.mean()
    sd = d.reflectance.std()
    d_no_outlier = d[np.abs(d.reflectance - mn)/sd < 3]
    return d_no_outlier.groupby('wavelength').apply(lambda x: x.mean())
    
def normalize(v, to=1.0):
    return (v-v.min())/ (v.max()-v.min()) * to
    
def get_interpolater(v_wavelength, v_reflectance):
    return scipy.interpolate.interp1d(v_wavelength, v_reflectance, 'cubic', bounds_error=False)

def classify(v_wavelength, v_reflectance, nbest=5):
    interpolater = get_interpolater(v_wavelength, v_reflectance)

    dresult = {}
    dmeanspec.Wavelength
    for col in dmeanspec.columns:
        if col == 'Wavelength':
            continue
        matched_reflectance = interpolater(dmeanspec.Wavelength)
        dresult[col] = ((normalize(matched_reflectance) - normalize(dmeanspec[col]))**2).mean()
    
    # pick the best
    res = [(diff, name) for name, diff in dresult.items()]
    res.sort()
    return [(v,k) for k,v in res][:nbest]



if __name__ == '__main__':

    import matplotlib.pyplot as plt

    input_filepath = os.path.expanduser('~/Dropbox/devsync/dataproc/data/smass_catalog/data/spex/sp41/a000001.sp41.txt')
    d = clean_data(smass_text_file_to_dataframe(input_filepath))
    res = classify(d.wavelength, d.reflectance)
    
    legend_text = []
    best = None
    for name,diff in res[:5]:
        print name,'\t',diff
        legend_text.append(name)
        if best is None:
            best = name

        plt.plot(dmeanspec.Wavelength, normalize(dmeanspec[name]))

    # FIXME rerun slow stuff :-(
    interpolater = get_interpolater(d.wavelength, d.reflectance)
    plt.scatter(dmeanspec.Wavelength, normalize(interpolater(dmeanspec.Wavelength)))
    legend_text.append('target')
    plt.legend(legend_text)
    plt.show()
