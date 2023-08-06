'''Module docstring for Bandstructure'''

#raise NotImplementedError("Bandstructure has not been implemented yet!")

from semicpy.constants.constants import value
import numpy as np
import numpy.typing as npt

HBAR = value('Reduced Planck constant in eV s')

def conduction_band(k: npt.ArrayLike,
                    K_c: npt.ArrayLike,
                    M_e: npt.ArrayLike,
                    ec: float=0.0):
    """General equation for Conduction bands with minimum at Kc and assuming parabolic bands

    Parameters
    ----------
    k : npt.ArrayLike
        _description_
    K_c : npt.ArrayLike
        _description_
    M_e : npt.ArrayLike
        _description_
    ec : float, optional
        Lowest energy in the conduction bands, by default 0.0
    """
    return ec + ((np.square(HBAR) / 2) * (k - K_c) / M_e * (k - K_c))

def valence_band(k: npt.ArrayLike,
                 K_v: npt.ArrayLike,
                 M_h: npt.ArrayLike,
                 ev: float=0.0):
    """_summary_

    Parameters
    ----------
    k : npt.ArrayLike
        _description_
    K_v : npt.ArrayLike
        _description_
    M_h : npt.ArrayLike
        _description_
    ev : float, optional
        _description_, by default 0.0
    """
    return ev - ((np.square(HBAR) / 2) * (k - K_v) / M_h * (k - K_v)) 

def eff_mass_matrix(mxx: float=0.0,
                    mxy: float=0.0,
                    mxz: float=0.0,
                    myy: float=0.0,
                    myz: float=0.0,
                    mzz: float=0.0)-> npt.NDArray:
    """The effective mass matrix of electrons or holes.
    
    Effective Mass Matrix, M_e or M_h, must be symmetric due to physical considerations.
    Therefore mxy = myx, myz = mzy, mxz = mzx

    Parameters
    ----------
    mxx : float, optional
        _description_, by default 0.0
    mxy : float, optional
        _description_, by default 0.0
    mxz : float, optional
        _description_, by default 0.0
    myy : float, optional
        _description_, by default 0.0
    myz : float, optional
        _description_, by default 0.0
    mzz : float, optional
        _description_, by default 0.0

    Returns
    -------
    npt.NDArray
        Matrix corresponding to the Effective Mass Matrix. 
    """
    return np.array([[mxx,mxy,mxz],[mxy,myy,myz],[mxz,myz,mzz]])

def conduction_band_DOS(me,
                        mde,
                        E: float=0.0,
                        Ec: float=0.0,
                        iso: str="iso"):
    """_summary_

    Parameters
    ----------
    me : _type_
        _description_
    mde : _type_
        _description_
    E : float, optional
        _description_, by default 0.0
    Ec : float, optional
        _description_, by default 0.0
    iso : str, optional
        _description_, by default "iso"

    Returns
    -------
    _type_
        _description_
    """
    if iso == "iso":
        m = me
    elif iso == "aniso":
        m = mde
    else:
        raise ValueError("iso specifier must be 'iso' or 'aniso'!")

    if (E < Ec):
        return 0
    else:
        return (np.sqrt(2) / np.square(np.pi)) * ((m / np.square(HBAR)) ** (1.5)) * np.sqrt(E - Ec)


def valence_band_DOS(mh,
                     mdh,
                     E: float=0.0,
                     Ev: float=0.0,
                     iso: str="iso"):
    """_summary_

    Parameters
    ----------
    mde : _type_
        _description_
    E : _type_
        _description_
    Ev : _type_
        _description_
    """
    if iso == "iso":
        m = mh
    elif iso == "aniso":
        m = mdh
    else:
        raise ValueError("iso specifier must be 'iso' or 'aniso'!")

    if (E > Ev):
        return 0
    else:
        return (np.sqrt(2) / np.square(np.pi)) * ((m / np.square(HBAR)) ** (1.5)) * np.sqrt(Ev - E)

def effective_mass_DOS(mx,
                       my,
                       mz):
    """_summary_

    Parameters
    ----------
    mx : _type_
        _description_
    my : _type_
        _description_
    mz : _type_
        _description_
    """
    return (mx * my * mz) ** (1 / 3)