import pandas as pd

def smass_text_file_to_dataframe(filepath):
    d = pd.read_table(filepath, sep=r'\s+', header=None, names=['wavelength', 'reflectance', 'ignore1', 'ignore2'])
    return d.sort(['wavelength'])

    
