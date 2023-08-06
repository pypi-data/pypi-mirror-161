"""
Created on Sun Jun  5 23:11:01 2022

@author: Nithin Kumar Santha Kumar

Description:
"""
from semicpy.constants.constants import value
from semicpy.materials.semiconductor import Semiconductor
import numpy as np

BOLTZMANN = value("Boltzmann constant in eV/K")

class Si(Semiconductor):
    """
    """
    def bandgap_temp_dependence(self,
                                temperature: float=None)-> float:
        """_summary_

        Parameters
        ----------
        temperature : float
            _description_, by default None

        Returns
        -------
        float
            _description_
        """
        eg_0 = 1.17
        temp = self.abstemp if temperature is None else temperature
        return eg_0 - ((4.73e-4 * temp ** 2) / (temp + 636))

    def intrinsic_carrier_concentration(self,
                                        temperature: float=None)-> float:
        """_summary_

        Parameters
        ----------
        temperature : float, optional
            _description_, by default None

        Returns
        -------
        float
            _description_
        """
        temp = self.abstemp if temperature is None else temperature
        eg = self.bandgap_temp_dependence(temp)
        two_kb_t = 2 * BOLTZMANN * temp
        nc = self.cdos(temp)
        nv = self.vdos(temp)

        return np.sqrt(nc * nv) * np.exp(-eg / two_kb_t)

    def cdos(self,
             temperature: float=None)-> float:
        """_summary_

        Parameters
        ----------
        temperature : float, optional
            _description_, by default None

        Returns
        -------
        float
            _description_
        """
        temp = self.abstemp if temperature is None else temperature
        nc = 6.2e15 * temp ** (3/2) if self.conductionDensityOfStates is None else self.conductionDensityOfStates

        return nc
    
    def vdos(self,
             temperature: float=None)-> float:
        """_summary_

        Parameters
        ----------
        temperature : float, optional
            _description_, by default None

        Returns
        -------
        float
            _description_
        """
        temp = self.abstemp if temperature is None else temperature
        nv = 3.5e15 * temp ** (3/2) if self.valenceDensityOfStates is None else self.valenceDensityOfStates

        return nv

    def bandgap_pressure_dependence(self,
                                    pressure: float=0.0)-> float:
        """Dependence of the Energy Gap on Hydrostatic Pressure

        Parameters
        ----------
        pressure : float, optional
            Hydrostatic Pressure, by default 0.0 kbar

        Returns
        -------
        float
            _description_
        """
        eg_0 = 1.17

        return eg_0 - (1.4e-3 * pressure)
    
    def infrared_refractive_index(self,
                                  temp: float=None)-> float:
        """
        Calculates the refractive index based on temperature. This equation only works
        on temperature ranges between 77K and 400K.

        Parameters
        ----------
        temp : float, optional
            temperature in Kelvin, by default None

        Returns
        -------
        float
            The refractive index

        Raises
        ------
        ValueError
            Temperature is outside of range specified
        """
        temperature = self.abstemp if temp is None else temp

        if 77 < temperature < 400:
            return 3.38 * (1 + (3.9e-5 * temperature))
        else:
            raise ValueError("Temperature outside of specified range (77 < temperature < 400)!")
    
    def lattice_parameter(self,
                          temp: float=None)-> float:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            temperature in degrees C, by default None

        Returns
        -------
        float
            _description_
        """
        temperature = (self.abstemp - 273.15) if temp is None else temp
        a0 = 5.4304 #Angstroms
        
        return a0 + (1.8138e-5 * temperature) + (1.542e-9 * (temperature ** 2))