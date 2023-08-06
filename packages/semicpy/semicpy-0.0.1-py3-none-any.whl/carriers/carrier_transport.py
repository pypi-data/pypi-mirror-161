"""
Created on Tue Jan 4 16:07:26 2022

@author: Nithin Kumar Santha Kumar

Description: Module docstring for carrier transport

TODO:
    ADD 3-D hole and electron current density.
    ADD 3-D net electrical current density.
    ADD Continuity equation.
    ADD Analytically Solvable Approximations
    ADD Displacement Current and Carrier Inertia
    ADD Induced Terminal Current
    ADD Noise Currents
    ADD Magnetic Fields: Hall Effect
"""

from semicpy.constants.constants import value
from semicpy.math.functions import ifdint_approx

def mobility(tau=0,
             effective_mass=1):
    '''

    Parameters
    ----------
    tau : float, required
        Relaxation time of a disspative process. The default is 0.
    effective_mass : float, required
        Effective mass of a carrier in an energy band. The default is 1.

    Returns
    -------
    mu_n or mu_p: the electron or hole mobility

    '''

    mu = value('Elementary charge') * tau / effective_mass
    return mu

def particle_current_density_drift(spec=None, 
                                   mu=0,
                                   density=0, 
                                   d_phi_d_z=0):
    """

    Parameters
    ----------
    spec : string, required
        specifies whether carriers are holes or electrons.
        The following arguments are accepted: "electrons","n","holes","p"
        The default is None.
    mu : float, required
        Electron or hole mobility. The default is 0.
    density : float, required
        Electron or hole density. The default is 0.
    d_phi_d_z : float, required
        Derivative of electrostatic potential with respect to z.
        The default is 0.

    Returns
    -------
    The drift particle current density

    """
    if(spec == "electrons" or "n"):
        j = mu*density*d_phi_d_z
        return j
    elif(spec == "holes" or "p"):
        j = -mu*density*d_phi_d_z
        return j
    else:
        raise ValueError("Error! Incorrect specifier given!")

def particle_current_density_diffusion(diffusivity=0,
                                       d_dz = 0):
    """
    Returns the diffusion particle current density.

    Parameters
    ----------
    diffusivity : float, required
        Electron or hole diffusivity. The default is 0.
    d_dz : float, required
        Derivative of the electron or hole density with respect to z.
        The default is 0.

    Returns
    -------
    The diffusion particle current density

    """
    j = -diffusivity*d_dz
    return j

def diffusivity(temp=300,
                mu=0):
    """
    Returns the electron or hole diffusivity

    Parameters
    ----------
    temp : float, required
        Temperature in Kelvin. The default is 300.
    mu : float, required
        Electron or hole mobility. The default is 0.

    Returns
    -------
    The electron or hole diffusivity.

    """
    kb_t = value("Boltzmann constant in eV/K") * temp
    d = kb_t * mu
    return d

def electron_current_density(mu=0,
                             density=0,
                             d_phi_d_z=0,
                             diffusivity=0,
                             dn_dz=0):
    """
    returns the electron current density

    Parameters
    ----------
    mu : TYPE, required
        DESCRIPTION. The default is 0.
    density : TYPE, required
        DESCRIPTION. The default is 0.
    d_phi_d_z : TYPE, required
        DESCRIPTION. The default is 0.
    diffusivity : TYPE, required
        DESCRIPTION. The default is 0.
    dn_dz : TYPE, required
        DESCRIPTION. The default is 0.

    Returns
    -------
    The electron current density

    """
    j = (mu*density*d_phi_d_z) - (diffusivity*dn_dz)
    return j

def hole_current_density(mu=0,
                         density=0,
                         d_phi_d_z=0,
                         diffusivity=0,
                         dp_dz=0):
    """
    returns the hole current density

    Parameters
    ----------
    mu : TYPE, required
        DESCRIPTION. The default is 0.
    density : TYPE, required
        DESCRIPTION. The default is 0.
    d_phi_d_z : TYPE, required
        DESCRIPTION. The default is 0.
    diffusivity : TYPE, required
        DESCRIPTION. The default is 0.
    dp_dz : TYPE, required
        DESCRIPTION. The default is 0.

    Returns
    -------
    The hole current density

    """
    j = -(mu*density*d_phi_d_z) - (diffusivity*dp_dz)
    return j

def electrical_current_density(j_n=0,
                               j_p=0):
    """
    returns the net electrical current density, J.

    Parameters
    ----------
    j_n : TYPE, optional
        DESCRIPTION. The default is 0.
    j_p : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    Electrical current density

    """
    q = value("Elementary charge")
    current_density = q*(j_p - j_n)
    return current_density

def electron_quasi_fermi_level(band_edge_energy=0,
                               phi=0, 
                               temp=0, 
                               density=0,
                               density_of_states=1):
    """
    Finds the Quasi Fermi Level for electrons

    Parameters
    ----------
    band_edge_energy : TYPE, optional
        DESCRIPTION. The default is 0.
    phi : TYPE, optional
        DESCRIPTION. The default is 0.
    temp : TYPE, optional
        DESCRIPTION. The default is 0.
    density : TYPE, optional
        DESCRIPTION. The default is 0.
    density_of_states : TYPE, optional
        DESCRIPTION. The default is 1.

    Returns
    -------
    None.

    """
    kb_t = value('Boltzmann constant in eV/K') * temp
    n_nc = density / density_of_states
    fn = band_edge_energy - phi + (kb_t * ifdint_approx(n_nc))

    return fn

def hole_quasi_fermi_level(band_edge_energy=0,
                           phi=0,
                           temp=0,
                           density=0,
                           density_of_states=1):
    """
    Finds the Quasi Fermi level for holes

    Parameters
    ----------
    band_edge_energy : TYPE, optional
        DESCRIPTION. The default is 0.
    phi : TYPE, optional
        DESCRIPTION. The default is 0.
    temp : TYPE, optional
        DESCRIPTION. The default is 0.
    density : TYPE, optional
        DESCRIPTION. The default is 0.
    density_of_states : TYPE, optional
        DESCRIPTION. The default is 1.

    Returns
    -------
    None.

    """
    kb_t = value('Boltzmann constant in eV/K') * temp
    p_nv = density / density_of_states
    fp = band_edge_energy - phi - (kb_t * ifdint_approx(p_nv))

    return fp
