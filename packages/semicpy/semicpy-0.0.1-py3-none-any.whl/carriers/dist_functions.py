'''
This module contains the distribution functions
'''

from numpy import exp,sqrt,pi
from semicpy.constants.constants import value


def maxwell_boltzmann(velocity=0,m_star=0,temp=1):
    '''
    Function to find the the average number of electrons in
    state f using the Maxwell-Boltzmann distribution function.

    v: group velocity of an electron in a band structure, or
       the velocity of an individual particle in a classical
       model.

    m_star: The effective mass of a carrier in an energy band.

    temp: Temperature in Kelvin.

    k_b: Boltzmann's constant in eV/K

    f_mb(v) = sqrt(m_star/(2pi*kb*T))*exp(-m_star*v^2/2kb*T)
    '''

    kb_t = value('Boltzmann constant in eV/K') * temp
    f_mb = sqrt(m_star / (2*pi*kb_t)) * exp(-m_star*(velocity**2) / (2*kb_t))

    return f_mb

def fermi_dirac(energy=0,fermi_energy=0,temp=1):
    '''
    Function to find the average number of electrons in state f
    using the Fermi-Dirac distribution function.

    energy: Energy in eV

    fermi_energy: Fermi energy, or chemical potential of electrons, in eV

    temp: temperature in Kelvin

    k_b: Boltzmann's constant in eV/K

    f_df(E) = 1/(1+exp((E-fermi_energy)/k*temp))
    '''
    kb_t = value('Boltzmann constant in eV/K') * temp
    f_fd = 1/(1+exp((energy-fermi_energy)/(kb_t)))

    return f_fd

def bose_einstein(omega=0, temp=1):
    '''
    Function to find the average number of bosons in state f
    using the Bose-Einstein Distribution function.

    hbar: Reduced Planck Constant in eV s

    omega (w) : angular frequency in radians per second

    k_b: Boltzmann Constant in eV/K

    temp: Temperature in Kelvin

    f_be(hbar*w) = 1/(exp((h_bar*omeg_a)/(k_b*temp)) - 1)
    '''
    kb_t = value('Boltzmann constant in eV/K') * temp
    h_bar = value('Reduced Planck constant in eV s')

    f_be = 1/(exp((h_bar*omega)/kb_t) - 1)

    return f_be

def donor_distribution(g_d=0,fermi_energy=0,donor_energy=0,temp=1):
    '''
    Function to find the distribution of donor states in a
    semiconductor

    g_d: The degeneracy factor of a donor.

    fermi_energy: Fermi energy, or chemical potential of electrons, in eV

    donor_energy: Energy level of a donor impurity in a semiconductor, including
        the shift due to the electrostatic potential.

    k_b: Boltzmann's constant in eV/K

    temp: Temperature in Kelvin

    f(D+) = 1/(1+g_d*exp((fermi_energy-donor_energy)/(k_b*temp)))
    '''

    kb_t = value('Boltzmann constant in eV/K') * temp
    f_D = 1 / (1 + g_d*exp((fermi_energy-donor_energy)/kb_t))

    return f_D

def acceptor_distribution(g_a=0,fermi_energy=0,acceptor_energy=0,temp=1):
    '''
    Function to find the distribution of acceptor states in a
    semiconductor

    g_a: The degeneracy factor of an acceptor.

    fermi_energy: Fermi energy, or chemical potential of electrons, in eV

    acceptor_energy: Energy level of an acceptor impurity in a semiconductor, including
        the shift due to the electrostatic potential.

    k_b: Boltzmann's constant in eV/K

    temp: Temperature in Kelvin

    f(A-) = 1/(1+g_a*exp((acceptor_energy-fermi_energy)/(k_b*temp)))
    '''

    kb_t = value('Boltzmann constant in eV/K') * temp
    f_A = 1 / (1 + g_a*exp((acceptor_energy-fermi_energy)/kb_t))

    return f_A
