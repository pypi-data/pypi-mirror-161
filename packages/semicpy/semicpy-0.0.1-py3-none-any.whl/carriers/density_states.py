'''
module docstring for density of states
'''
from numpy import exp,sqrt,pi
from semicpy.constants.constants import value

def density_of_states(m_star=0,energy=0,conduction_band_energy=0):
    '''
    Function to find the density of quantum states as a function of
    energy

    m_star: the effective mass of a carrier in an energy band.

    energy: Energy of a particle or system, or of a particular quantum state

    conduction_band_energy: Conduction band edge energy in a semiconductor.
                            This is the potential energy for electrons, including
                            the electrostatic potential.
    D(E) = m_star*sqrt(2*m_star*(energy-conduction_band_energy))/(pi**2 * h_bar**3)
    '''
    h_bar = value('reduced Planck in eV s')
    d_e = m_star*sqrt(2*m_star*(energy-conduction_band_energy)) / ((pi**2) * (h_bar**3))

    return d_e

def density_of_states_abm(m1_star=0,m2_star=0,m3_star=0,energy=0,conduction_band_energy=0):
    '''
    Function to find the density of quantum states as a function of
    energy for an anisotropic band minimum.

    m_star: the effective mass of a carrier in an energy band.

    energy: Energy of a particle or system, or of a particular quantum state

    conduction_band_energy: Conduction band edge energy in a semiconductor.
                            This is the potential energy for electrons, including
                            the electrostatic potential.
    D(E) = sqrt(2*m1_star*m2_star*m3_star*(energy-conduction_band_energy))/(pi**2 * h_bar**3)
    '''

    h_bar = value('reduced Planck in eV s')

    d_e = sqrt(2*m1_star*m2_star*m3_star*(energy-conduction_band_energy)) / ((pi**2) * (h_bar**3))

    return d_e

def density_of_states_non_parabolic(m_star=0,energy=0,conduction_band_energy=0,alpha=0):
    '''
    Function to find the density of quantum states as a function of
    energy for a non-parabolic energy band.

    m_star: the effective mass of a carrier in an energy band.

    energy: Energy of a particle or system, or of a particular quantum state

    conduction_band_energy: Conduction band edge energy in a semiconductor.
                            This is the potential energy for electrons, including
                            the electrostatic potential.

    alpha: an arbitary constant

    D(E) = m_star*sqrt(2*m_star*(energy-conduction_band_energy)
           *[1+alpha*(energy-conduction_band_energy)])
           *[1+2*alpha*(energy-conduction_band_energy)/(pi**2 * h_bar**3)
    '''

    h_bar = value('reduced Planck constant in eV s')
    energy_sub = energy-conduction_band_energy
    pi_h_product = (pi**2) * (h_bar**3)
    sqrt_product = sqrt(2*m_star*(energy_sub)*(1+alpha*(energy_sub)))

    d_e = m_star*sqrt_product*(1+2*alpha*energy_sub) / pi_h_product

    return d_e

def density_of_states_two_d(m_star=0):
    '''
    Function to find the 2D density of quantum states.

    m_star: the effective mass of a carrier in an energy band.

    D_2d = m_star/(pi*h_bar**2)
    '''
    h_bar = value('reduced Planck constant in eV s')
    d_2d = m_star / (pi * (h_bar**2))

    return d_2d

def density_of_states_one_d(m_star=0,energy=0,conduction_band_energy=0):
    '''
    Function to find the 1D density of quantum states.

    m_star: the effective mass of a carrier in an energy band.

    energy: Energy of a particle or system, or of a particular quantum state

    conduction_band_energy: Conduction band edge energy in a semiconductor.
                            This is the potential energy for electrons, including
                            the electrostatic potential.

    D_1d = 1/(pi*h_bar) * sqrt(m_star/2(energy-conduction_band_energy))
    '''
    h_bar = value('reduced Planck constant in eV s')
    d_1d = (1 / (pi * h_bar)) * sqrt(m_star / (2*(energy-conduction_band_energy)))

    return d_1d

def density_of_states_photon(omega=0,speed_of_light=0,refractive_index=1):
    '''
    Function to find the 3D photon density of states.

    omega: angular frequency in rad/s.

    speed_of_light: speed of light in medium.

    refractive_index: refractive index of medium

    d_photon3d = omega**2 * refractive_index**3 / pi**2 * speed_of_light**3
    '''
    d_photon3d = ((omega**2)*(refractive_index**3)) / ((pi**2) * (speed_of_light**3))

    return d_photon3d

def density_of_states_photon1d(refractive_index=1,speed_of_light=1):
    '''
    Function to find the 1D photon density of states.

    speed_of_light: speed of light in medium.

    refractive_index: refractive index of medium.

    d_photon1d = refractive_index / (pi * speed_of_light)
    '''
    d_photon1d = refractive_index / (pi * speed_of_light)

    return d_photon1d

def equilibrium_energy_density(omega=0,speed_of_light=1,temp=1):
    '''
    Function to find the equilibrium energy density in an
    electromagnetic field.

    omega: angular frequency in rad/s.

    speed_of_light: speed of light in medium.

    temp: temperature in kelvin

    exponential = 1/(exp(h_bar*omega/(k_b * temps)) - 1)
    u_w = ((h_bar * omega**3) / ((pi**2)*(speed_of_light**3))) * exponential
    '''
    h_bar = value('reduced Planck constant in eV s')
    kb_t = value('Boltzmann constant in eV/K') * temp

    exponential = 1/(exp(h_bar*omega/kb_t) - 1)
    u_w = ((h_bar * omega**3) / ((pi**2)*(speed_of_light**3))) * exponential

    return u_w

def intensity_thermal_radiation(omega=0,speed_of_light=1,temp=1):
    '''
    Function to find the intensity (flux) of thermal radiation.

    omega: angular frequency in rad/s.

    speed_of_light: speed of light in medium.

    temp: temperature in kelvin

    exponential = 1/(exp(h_bar*omega/(k_b * temps)) - 1)
    I_w = ((h_bar * omega**3) / ((4*pi**3)*(speed_of_light**2))) * exponential
    '''
    h_bar = value('reduced Planck constant in eV s')
    kb_t = value('Boltzmann constant in eV/K') * temp

    exponential = 1/(exp(h_bar*omega/(kb_t)) - 1)
    i_w = ((h_bar * omega**3) / ((4*(pi**3))*(speed_of_light**2))) * exponential

    return i_w
