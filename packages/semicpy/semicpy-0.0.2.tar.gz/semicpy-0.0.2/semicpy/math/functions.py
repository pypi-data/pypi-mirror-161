'''
module docstring for special functions
'''
import numpy as np
from scipy.integrate import quad
from scipy.special import gamma

def fdint_approx(eta=0)-> float:
    """Function to find the approximate Fermi-Dirac Integral of
    order 1/2 with an error of +/- 0.5%

    Parameters
    ----------
    eta : int, optional
        _description_, by default 0

    Returns
    -------
    float
        approximate Fermi-Dirac Integral result
    """
    epsilon = 3 * np.sqrt(np.pi / 2) * ((eta + 2.13) + ((np.abs(eta - 2.13) ** 2.4) + 9.6) ** (5 / 12)) ** (-3 / 2)
    fd = 1 / (np.exp(-eta) + epsilon)
    return fd

def fermi_dirac_int(order=0.5,
                    eta=0.0)-> float:
    """
    Fermi-Dirac integral

    Parameters
    ----------
    order : float, required
        DESCRIPTION. The default is 0.5.
    eta : float, required
        DESCRIPTION. The default is 0.

    Returns
    -------
    Fermi-Dirac integral result

    """
    reciprocal_gamma = 1 / gamma(order + 1)
    intgrl = quad(lambda t: ((t ** order) / (1 + np.exp(t - eta))),a=0,b=np.inf,epsabs=1e-300,epsrel=1e-8,limit=100)
    return reciprocal_gamma * intgrl[0]

def ifdint_approx(eta=0)-> float:
    """The Inverse Fermi-Dirac Integral of Order 1/2 approximation.

    Parameters
    ----------
    eta : int, optional
        _description_, by default 0

    Returns
    -------
    float
        approximate Inverse Fermi-Dirac Integral value
    """
    ifd = np.log(eta) + ((3.53553e-1) * eta) - (4.95009e-3 * (eta ** 2)) + (1.48386e-4 * (eta ** 3)) - (4.42563e-6 * (eta ** 4))
    return ifd
