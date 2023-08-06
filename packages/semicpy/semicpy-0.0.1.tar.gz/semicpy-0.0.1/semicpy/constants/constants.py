##########################################
# Semiconductor Calculations Package
# Author: Nithin Kumar Santha Kumar
# Date: 10/30/2021
##########################################
# Changelog: 
# 4/25/2021 - Started Package
# 10/30/2021 - Started constants (constants.py)
# 10/30/2021 - Added more functionality
# 11/13/2021 - Constants.py is complete as of date listed
##########################################
"""
All constant values are from the 2018 CODATA publication.
More information on CODATA and their publication can be found at:
   https://physics.nist.gov/cuu/Constants/index.html and
   https://www.nist.gov/programs-projects/codata-values-fundamental-physical-constants

Any fundamental adjustments of constants will be made after the 2022 CODATA publication of 
fundamental constants.

Errors will be corrected on a more frequent basis.
"""

from pint import UnitRegistry

ureg = UnitRegistry(system = 'SI')


constants = {
            "Speed of light in vacuum" : [299792548, format(ureg.meter/ureg.second,'~')],
            "Planck constant in J s" : [6.62607015e-34, format(ureg.J * ureg.second, '~')],
            "Planck constant in eV s" : [4.135667696e-15, format(ureg.eV * ureg.second, '~')],
            "Reduced Planck constant in J s" : [1.054571817e-34, format(ureg.J * ureg.second, '~')],
            "Reduced Planck constant in eV s" : [6.582119569e-16, format(ureg.eV * ureg.second, '~')],
            "Elementary charge" : [1.602176634e-19, format(ureg.C,'~')],
            "Vacuum magnetic permeability" : [1.25663706212e-6, format(ureg.H / ureg.meter, '~')],
            "Vacuum electric permittivity" : [8.8541878128e-12, format(ureg.F / ureg.meter, '~')],
            "Boltzmann constant in eV/K" : [8.617333262e-5, format(ureg.eV / ureg.K, '~')],
            "Boltzmann constant in J/K" : [1.380649e-23, format(ureg.J / ureg.K, '~')],
            "Atomic mass constant" : [1.66053906660e-27, format(ureg.kg,'~')],
            "Fine structure constant" : [7.2973525693e-3, format(ureg.dimensionless,'~')],
            "Electron mass" : [9.1093837015e-31, format(ureg.kg,'~')],
            "Stefan-Boltzmann constant" : [5.670374419e-8, format(ureg.W/((ureg.meter**2) * (ureg.K**4)),'~')],
            "Rydberg constant" : [10973731.568160, format(ureg.meter**-1,'~')],
            "Rydberg constant times hc in eV" : [13.605693122994, format(ureg.eV,'~')],
            "Rydberg constant times hc in J" : [2.1798723611035e-18, format(ureg.J,'~')],
            "Rydberg constant times c in Hz" : [3.2898419602508e+15, format(ureg.Hz,'~')],
            "Compton wavelength" : [2.42631023867e-12, format(ureg.meter,'~')],
            "Classical electron wavelength" : [2.8179403262e-15, format(ureg.meter,'~')],
            "Characteristic impedance of vacuum" : [376.730313668, format(ureg.ohm,'~')],
            "Bohr radius" : [5.29177210903e-11, format(ureg.meter,'~')],
            "Electron volt in J" : [1.602176634e-19, format(ureg.J,'~')],
            "Proton mass" : [1.67262192369e-27, format(ureg.kg,'~')],
            "Neutron mass" : [1.67492749804e-27, format(ureg.kg,'~')], 
}

def value(key):
   """
   Value of constants given by key
   """
   return constants[key][0]

def units(key):
   """
   Unit of constants given by key
   """
   return constants[key][1]

def list_constants():
   """
   Lists all the constants in the constants dictionary
   """
   lst = list(constants.keys())
   print(lst)

def find_constants(search_term):
   """
   Finds constants based on search term
   """
   if search_term is None:
      print("Here is the list of constants available:\n")
      list_constants()
   else:
      for key in constants:
         if search_term.lower() in key.lower():
            print(key)
