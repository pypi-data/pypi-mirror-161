"""
Created on Sun Jun  5 23:11:01 2022

@author: Nithin Kumar Santha Kumar

Description:
"""

from semicpy.materials.semiconductor import Semiconductor

class AlN(Semiconductor):
    """
    """
    def lattice_parameter(self,
                          temp: float=None)-> tuple:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default None

        Returns
        -------
        tuple
            _description_
        """
        temperature = (self.abstemp - 273.15) if temp is None else temp
        a0 = 3.1113 #Angstroms
        c0 = 4.9793 #Angstroms
        a = a0 + (1.3130e-5 * temperature) + (4.147e-9 * (temperature ** 2))
        c = c0 + (1.4789e-5 * temperature) + (7.255e-9 * (temperature ** 2))

        return (a,c)