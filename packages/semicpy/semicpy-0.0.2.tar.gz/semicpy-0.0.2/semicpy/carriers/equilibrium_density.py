'''
module docstring for carrier equilibrium density
'''

from numpy import exp,sqrt,pi
from semicpy.constants.constants import value
from semicpy.math.functions import fdint_approx

def find_n0(n_c=0,conduction_band_energy=0,fermi_energy=0,temp=0):
    '''
    Function to find nondegenerate Equilibrium electron density
    in the conduction band.

    n_c: Thermal effective density of states in the
        conduction band.

    conduction_band_energy: Conduction band edge energy in a semiconductor.
        This is the potential energy of electrons, including
        electrostatic potential.

    fermi_energy: Fermi energy, or the chemical potential for electrons.

    k_b: Boltzmann's constant in eV/K

    temp: Temperature in Kelvin

    n0 = n_c*exp(-(conduction_band_energy-fermi_energy)/(k_b*temp))
    '''
    kb_t = value('Boltzmann constant in eV/K') * temp
    n_0 = n_c*exp(-(conduction_band_energy-fermi_energy)/kb_t)

    return n_0

def find_nc(mass_c=0,temp=0):
    '''
    Function to find thermal effective density of states in
    conduction band.

    mass_c: The effective mass of a carrier in the conduction band

    k_b: Boltzmann constant in eV/K

    temp: Temperature in Kelvin

    hbar: reduced Planck constant in eV s

    n_c = 2*[mass_c*k_b*temp/(2pi*hbar^2)]^(3/2)
    '''
    kb_t = value('Boltzmann constant in eV/K') * temp
    h_bar = value('reduced Planck constant in eV s')
    n_c = 2*((mass_c*kb_t/(2*pi*(h_bar**2)))**(3/2))

    return n_c

def find_p0(n_v=0,valence_band_energy=0,fermi_energy=0,temp=0):
    '''
    Function to find the nondegenerate Equilibrium hole density
    in the valence band.

    n_v: Thermal effective density of states in valence band

    valence_band_energy: Valence band edge energy in a semiconductor.
        This is the potential energy of electrons, including
        electrostatic potential.

    k_b: Boltzmann constant in eV/K

    temp: Temperature in Kelvin

    p0 = n_v*exp(valence_band_energy-fermi_energy/k_b*temp)
    '''

    kb_t = value('Boltzmann constant in eV/K') * temp
    p_0 = n_v*exp((valence_band_energy-fermi_energy)/kb_t)

    return p_0

def find_nv(mass_v=0,temp=0):
    '''
    Function to find the thermal effective density
    of states in valence band.

    mass_v: The effective mass of of carrier in valence band

    temp: Temperature in Kelvin

    k_b: Boltzmann constant in eV/K

    hbar: reduced Planck constant in eV s

    n_v = 2*[mass_v*k_b*temp/(2pi*hbar^2)]^(3/2)
    '''

    kb_t = value('Boltzmann constant in eV/K') * temp
    h_bar = value('reduced Planck constant in eV s')

    n_v = 2*(mass_v*kb_t/(2*pi*(h_bar**2)))**(3/2)

    return n_v


def find_ni(n_0 = 0, p_0 = 0):
    '''
    Function to find the intrinsic carrier density

    n_0 = Equilibrium carrier density of electrons in conduction band

    p_0 = Equilibrium carrier density of holes in valence band

    n_i = sqrt(n_0*p_0)
    '''

    n_i = sqrt(n_0 * p_0)

    return n_i

def n0_from_ni(n_i=0,fermi_energy=0,in_fermi_level=0,temp=1):
    '''
    Function to find the equilibrium electron density from the
    intrinsic carrier density of a semiconductor.

    n_i: Intrinsic carrier density of a semiconductor

    fermi_energy: Fermi energy, or the chemical potential of an electron

    in_fermi_level: Fermi level of an intrinsic semiconductor

    temp: Temperature in Kelvin

    n0 = ni*exp((Ef-Efi)/kbT)
    '''
    kb_t = value('Boltzmann constant in eV/K') * temp
    exponential = exp((fermi_energy-in_fermi_level)/kb_t)
    n_0 = n_i*exponential
    
    return n_0

def p0_from_ni(n_i=0,fermi_energy=0,in_fermi_level=0,temp=1):
    '''
    Function to find the equilibrium hole density from the
    intrinsic carrier density of a semiconductor.

    n_i: Intrinsic carrier density of a semiconductor

    fermi_energy: Fermi energy, or the chemical potential of an electron

    in_fermi_level: Fermi level of an intrinsic semiconductor

    temp: Temperature in Kelvin

    p0 = ni*exp((Efi-Ef)/kbT)
    '''
    kb_t = value('Boltzmann constant in eV/K') * temp
    exponential = exp((in_fermi_level-fermi_energy)/kb_t)
    p_0 = n_i*exponential

    return p_0

def p0_approx(n_v=0,eta=0):
    '''
    Function to find the equilibrium hole density
    using an approximation of the Fermi-Dirac integral
    of order 1/2.

    n_v: The thermal effective density of states in the valence band.

    eta: (Ev - Ef)/kT
    '''
    p_0 = n_v*fdint_approx(eta)

    return p_0

def n0_approx(n_c=0,eta=0):
    '''
    Function to find the equilibrium electron density
    using an approximation of the Fermi-Dirac integral
    of order 1/2.

    n_c: The thermal effective density of states in the conduction band.

    eta: (Ef - Ec)/kT
    '''
    n_0 = n_c*fdint_approx(eta)

    return n_0
