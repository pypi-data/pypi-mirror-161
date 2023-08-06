"""
CV Measurements
"""
import pandas as pd


'''
FUNCTION: This will parse Id-Vg data and provide corrected Measurements
'''
def corr_id(file=None,sheetname=None,i_d = None,i_g=None,i_sub=None):
    """
    DESCRIPTION

    Parameters
    ----------
    file : str, required
        file object, path object, or string. The default is None.
    sheetname : str, optional
        DESCRIPTION. The default is None.
    i_d : str, required
        DESCRIPTION. The default is None.
    i_g : str, required
        DESCRIPTION. The default is None.
    i_sub : str, required
        DESCRIPTION. The default is None.

    Returns
    -------
    corrected_drain_current : pandas.Series
        DESCRIPTION.

    """
    if(file.endswith('.csv')):
        data = pd.read_csv(file)
    elif(file.endswith(('.xls','.xlsx'))):
        data = pd.read_excel(file,
                             sheet_name=sheetname)
    else:
        raise ValueError("Incorrect File Type!")
    df = pd.DataFrame(data=data)
    drain_current = df[i_d]
    gate_current = df[i_g]
    substrate_current = df[i_sub]

    corrected_drain_current = drain_current + ((gate_current+
                                                substrate_current)/2)

    return corrected_drain_current

def norm_cgc(file=None,sheetname=None,cgc=None,c_min=None,area=None):
    """
    DESCRIPTION

    Parameters
    ----------
    file : TYPE, optional
        DESCRIPTION. The default is None.
    sheetname : TYPE, optional
        DESCRIPTION. The default is None.
    cgc : TYPE, optional
        DESCRIPTION. The default is None.
    c_min : TYPE, optional
        DESCRIPTION. The default is None.
    area : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """
    if(file.endswith('.csv')):
        data = pd.read_csv(file)
    elif(file.endswith(('.xls','.xlsx'))):
        data = pd.read_excel(file,
                             sheet_name=sheetname)
    else:
        raise ValueError("Incorrect File Type!")

    normalized = (data[cgc] - c_min)/area
    return normalized

def n_inv():
    pass

def eff_mob():
    pass

def dummy():
    pass
