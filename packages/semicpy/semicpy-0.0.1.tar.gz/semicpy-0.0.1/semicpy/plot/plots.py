"""
module docstring for plottting E-k plots
"""

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import plotly.io as pio
import numpy as np
from semicpy.carriers.dist_functions import fermi_dirac,maxwell_boltzmann,bose_einstein

pio.renderers.default = 'browser'

def ekplot(energy=0,k=0):
    '''

    Parameters
    ----------
    energy : TYPE, optional
        DESCRIPTION. The default is 0.
    k : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    None.

    '''
    pass

def iv_curve(file=None,x=None,y=None,sheetname=None):
    '''
    Plots an IV curve from a file.

    Parameters
    ----------
    file : string, required
        file object, path object, or string. The default is None.
    x : string, required
        Name of your voltage column in your file. The default is None.
    y : string, required
        Name of your current column in your file. The default is None.
    sheetname : string, optional
        Sheetname of the chosen excel file. The default is None.

    Returns
    -------
    Displays a plot in your browser

    '''
    if (file.endswith('.csv')):
        d = pd.read_csv(file)
    elif(file.endswith(('.xls','.xlsx',))):
        d = pd.read_excel(file,sheet_name=sheetname)
    else:
        raise ValueError('Incorrect file type!')

    fig = go.Figure(data = go.Scatter(x=d[x], y=d[y]))
    fig.update_layout(title='I-V Curve')
    fig.update_xaxes(title_text = 'Voltage (V)')
    fig.update_yaxes(title_text = 'Current (mA)')
    fig.show()

    fig1 = px.line(d,x=x,y=y,title='I-V Curve',markers=True)
    fig1.show()


def distribution_function_plot(distribution_function=None,
                               energy=0,
                               fermi_energy=0,
                               omega=0,
                               velocity=0,
                               m_star=0,
                               temp=300):
    '''

    Parameters
    ----------
    distribution_function : str, required
        Distribution Functions (Fermi-Dirac,Maxwell-Boltzmann, Bose-Einstein).
        The default is None.
    energy : float, optional
        DESCRIPTION. The default is 0.
    fermi_energy : float, optional
        DESCRIPTION. The default is 0.
    omega : float, optional
        angular frequency in rad/s. The default is 0.
    velocity : float, optional
        velocity or group velocity of electrons. The default is 0.
    m_star : float, optional
        effective mass in carrier band. The default is 0.
    temp : float, optional
        Temperature in Kelvin. The default is 1.

    Returns
    -------
    None.

    '''
    if(distribution_function == 'Fermi-Dirac'):
        x = np.arange(start = (energy-fermi_energy) - 1,
                        stop = (energy-fermi_energy) + 1.1, step=0.1)

        fig = go.Figure(data = go.Scatter(x = x,y = fermi_dirac(x,0,temp)))
        fig.update_layout(title="Fermi-Dirac Distribution",
                          xaxis_title = '(E-Ef)/kbT',
                          yaxis_title = 'f_FD (E)')
        fig.show()
        '''
        sns.lineplot(x=x,y=fermi_dirac(x,0,temp))
        plt.xlabel("E-Ef (eV)")
        plt.ylabel("f_FD(E)")
        plt.title("Fermi-Dirac Distribution")'''
    elif(distribution_function == 'Maxwell-Boltzmann'):
        x = np.linspace(start = 0,stop = velocity + 1000)
        sns.lineplot(x=x,y=maxwell_boltzmann(x,m_star,temp))
        plt.xlabel("Velocity")
        plt.ylabel("f_MB")
        plt.title("Maxwell-Boltzmann Distribution")
    elif(distribution_function == 'Bose-Einstein'):
        x = np.linspace(start=1,stop=omega+10)
        sns.lineplot(x=x,y=bose_einstein(x,temp))
        plt.xlabel("\u03C9")
        plt.ylabel("f_BE")
        plt.title("Bose-Einstein Distribution")
    else:
        raise ValueError("ERROR! please specify a distribution function!")
