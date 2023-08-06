##########################################
# Semiconductor Calculations Package
# Author: Nithin Kumar Santha Kumar
# Date: 9/9/2021
##########################################
# Changelog: 
# 4/25/2021 - Started Package
# 9/09/2021 - Started hole dynamics physics (dynamics.py)
# 
##########################################
from semicpy.constants.constants import value

HBAR = value('reduced Planck constant in eV s')

def group_velocity(gradient_k=None,E=None):
   '''
   Function to find the group velocity of an electron
   in a band structure or the velocity of an individual
   particle in a classical model.

   gradient_k : The gradient with respect to k, which is the wavector of a spatial wave.
                k's magnitude is equals the wavenumber and direction indicates
                the propagation direction.

   E : The energy of a particle or system, or of a
       particular quantum state.

   h : The Planck constant

   h_bar : The reduced Planck constant. 
   
   h_bar = h/(2*pi)

   group_velocity = (gradient_k * energy)/(h_bar)
   '''

   v = (gradient_k*E)/HBAR
   return v

def bloch_accel(force=None):
   '''
   Function to find the acceleration of a Bloch wave. The
   acceleration theorem states that a uniform force, F, will
   cause the wavector of a Bloch state to evolve as : 

               dk/dt = F/hbar,

   where k is the wavector of a spatial wave, F is the uniform
   force, and hbar is the reduced Planck constant. 
   '''

   dk_dt = force/HBAR
   return dk_dt

def momentum(k=None):
   '''
   Function to find the momentum, p, of
   a point particle as a function of k, the
   wavector.

   k : The wavector of a spatial wave. k's magnitude is
       equals the wavenumber and direction indicates
       the propagation direction.

   hbar : The reduced Planck constant. hbar = h/(2*pi)

   p : The momentum of a point particle

   p = hbar*k
   '''

   p = HBAR*k
   return p

def energy(Eb=None,k=None):
   '''
   Function to find the energy, E, of
   an electron. 

   Eb : the band energy.

   k : The wavector of a spatial wave. k's magnitude is
       equals the wavenumber and direction indicates
       the propagation direction.

   E : The energy of an electron

   E = Eb(k)
   '''

   E = Eb*k
   return E
   