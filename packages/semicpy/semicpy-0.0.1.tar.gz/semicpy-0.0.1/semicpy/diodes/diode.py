"""
Module docstring
"""
import numpy as np
from scipy.misc import derivative
from semicpy.constants.constants import value

BOLTZMANN = value('Boltzmann constant in J/K')
CHARGE = value('Elementary charge')

class Diode:
    """Diode class description"""
    def __init__(self,
                 area: float=1.0,
                 temp: float=300.15,
                 tnom: float=300.15,
                 i_s: float=1.0e-14,
                 isr: float=0.0,
                 r_s: float=0.0,
                 trs1: float=0.0,
                 trs2: float=0.0,
                 n: float=1.0,
                 nbv: float=1.0,
                 nbvl: float=1.0,
                 nr: float=2.0,
                 tt: float=0.0,
                 cj0: float=0.0,
                 pb: float=1.0,
                 m: float=0.5,
                 e_g: float=1.11,
                 xti: float=3.0,
                 k_f: float=0.0,
                 a_f: float=1.0,
                 fc: float=0.5,
                 bv: float=np.inf,
                 tbv1: float=0.0,
                 tbv2: float=0.0,
                 ibv: float=1.0e-3,
                 ibvl: float=0.0,
                 ikf: float=np.inf,
                 tikf: float=0.0)-> None:
        """Diode Model Parameters. Based on SPICE model.

        Parameters
        ----------
        area : float, required
            Diode area. Must be greater than 0, by default 1.0 m^2
        temp : float, optional
            Analysis temperature, by default 300.15 K
        tnom : float, optional
            Model temperature at which all input data has been measured, by default 300.15 K
        i_s : float, optional
            Saturation current, by default 1.0e-14 A
        isr : float, optional
            Recombination current parameter, by default 0.0 A
        r_s : float, optional
            Parasitic resistance, by default 0.0 Ohms
        trs1 : float, optional
            Parasitic resistance linear temperature coefficient, by default 0.0 degC^-1
        trs2 : float, optional
            Parasitic resistance quadratic temperature coefficient, by default 0.0 degC^-2  
        n : float, optional
            Emission coefficient, by default 1.0
        nbv : float, optional
            Reverse breakdown ideality factor, by default 1.0
        nbvl : float, optional
            Low-level reverse breakdown ideality factor, by default 1.0
        nr : float, optional
            Emission coefficient for isr, by default 2.0
        tt : float, optional
            Transit Time, by default 0.0 s
        cj0 : float, optional
            Zero-bias junction capacitance, by default 0.0 F
        pb : float, optional
            Junction potential, by default 1.0 V
        m : float, optional
            Grading coefficient, by default 0.5
        e_g : float, optional
            Energy gap, by default 1.11 eV
                        1.11 for Si
                        0.69 for Schottky Barrier Diode (SBD)
                        0.67 for Ge 
        xti : float, optional
            Saturation current temperature exponent, by default 3.0
                                                     3.0 for pn-junction diode
                                                     2.0 for SBD
        k_f : float, optional
            Flicker-noise coefficient, by default 0.0
        a_f : float, optional
            Flicker-noise exponent, by default 1.0
        fc : float, optional
            Forward capacitance, by default 0.5 F
        bv : float, optional
            Reverse breakdown voltage (positive voltage), by default np.inf V
        tbv1 : float, optional
            Reverse breakdown voltage linear temperature coefficient, by default 0.0 degC^-1
        tbv2 : float, optional
            Reverse breakdown voltage quadratic temperature coefficient, by default 0.0 degC^-2
        ibv : float, optional
            Reverse breakdown current (positive voltage), by default 1.0e-3 A
        ibvl : float, optional
            Low-level reverse breakdown knee current, by default 0.0 A
        ikf : float, optional
            High-injection knee current, by default np.inf A
        tikf : float, optional
            High-injection knee current temperature coefficient, by default 0.0 degC^-1
        """
        self.area = area
        self.temperature = temp
        self.nominal_temperature = tnom
        self.sat_current = i_s
        self.recombination_current_param = isr
        self.ohmic_resistance = r_s
        self.rs_temp_coeff_lin = trs1
        self.rs_temp_coeff_quad = trs2
        self.emission_coeff = n
        self.rev_breakdown_IF = nbv
        self.low_level_rev_breakdown_IF = nbvl
        self.isr_emission_coeff = nr
        self.transit_time = tt
        self.zero_bias_junction_cap = cj0
        self.junction_pot = pb
        self.grading_coeff = m
        self.energy_gap = e_g
        self.sat_current_temp_exp = xti
        self.flicker_noise_coeff = k_f
        self.flicker_noise_exp = a_f
        self.forward_capacitance = fc
        self.rev_breakdown_voltage = bv
        self.bv_temp_coeff_lin = tbv1
        self.bv_temp_coeff_quad = tbv2
        self.rev_breakdown_current = ibv
        self.low_level_rev_breakdown_knee_current = ibvl
        self.knee_current = ikf
        self.ikf_temp_coeff = tikf
    
    def saturation_current(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * self.temperature / CHARGE
        t_tnom = self.temperature / self.nominal_temperature
        return self.sat_current * np.exp((t_tnom - 1) * self.energy_gap / (self.emission_coeff * vt)) * (t_tnom**(self.sat_current_temp_exp/self.emission_coeff))

    def recombination_current_parameter(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * self.temperature / CHARGE
        t_tnom = self.temperature / self.nominal_temperature
        return self.recombination_current_param * np.exp((t_tnom - 1) * self.energy_gap / (self.isr_emission_coeff * vt)) * (t_tnom**(self.sat_current_temp_exp/self.isr_emission_coeff))

    def high_injection_knee_current(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        return self.knee_current * (1 + (self.ikf_temp_coeff * (self.temperature - self.nominal_temperature)))

    def reverse_breakdown_voltage(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        return self.rev_breakdown_voltage * (1 + (self.bv_temp_coeff_lin * t_tnom) + (self.bv_temp_coeff_quad * (t_tnom ** 2)))
    
    def parasitic_resistance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        return self.ohmic_resistance * (1 + (self.rs_temp_coeff_lin * t_tnom) + (self.rs_temp_coeff_quad * (t_tnom ** 2)))
    
    def junction_potential(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature / self.nominal_temperature
        vt = BOLTZMANN * self.temperature / CHARGE
        return self.junction_pot * t_tnom - (3 * vt * np.log(t_tnom)) - (self.__eg(self.nominal_temperature)*t_tnom) + self.__eg(self.temperature)
    
    def zero_bias_junction_capacitance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        return self.zero_bias_junction_cap * (1 + (self.grading_coeff * ((0.0004 * t_tnom) + (1 - (self.junction_potential(self.nominal_temperature) / self.junction_pot)))))

    def __eg(self,
             temp: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default 0.0 K

        Eg_Si = 1.16 - (7.02e-4 * temp^2 / (1108 + temp)) (eV)
        Eg_Ge = 0.742 - (4.8e-4 * temp^2 /(235 + temp)) (eV)

        Returns
        -------
        float
            _description_
        """
        if self.energy_gap == 1.11:
            return 1.16 - ((7.02e-4 * (temp ** 2)) / (1108 + temp))
        elif self.energy_gap == 0.67:
            return 0.742 - (((4.8e-4) * (temp ** 2)) / (235 + temp))
        else:
            raise NotImplementedError("bandgap for SBD is not yet implemented!")

    def diode_current(self,
                      vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return self.area * (self.forward_current(vd) - self.reverse_current(vd))

    def forward_current(self,
                        vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return (self.normal_current(vd) * self.high_injection_factor()) + (self.recombination_current(vd) * self.generation_factor(vd))

    def reverse_current(self,
                        vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * self.temperature / CHARGE
        irev_h = self.rev_breakdown_current * np.exp(-(vd + self.reverse_breakdown_voltage()) / (self.rev_breakdown_IF * vt))
        irev_l = self.low_level_rev_breakdown_knee_current * np.exp(-(vd + self.reverse_breakdown_voltage()) / (self.low_level_rev_breakdown_IF * vt))
        return irev_h + irev_l

    def normal_current(self,
                       vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * self.temperature / CHARGE
        return self.saturation_current() * (np.exp(vd / (self.emission_coeff * vt)) - 1)

    def high_injection_factor(self,
                              vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        ikf = self.high_injection_knee_current()
        if ikf > 0:
            return np.sqrt(ikf / (ikf + self.normal_current(vd)))
        else:
            return 1.0

    def recombination_current(self,
                              vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * self.temperature / CHARGE
        return self.recombination_current_parameter() * (np.exp(vd / (self.isr_emission_coeff * vt)) - 1)

    def generation_factor(self,
                          vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vj = self.junction_potential()
        return (((1 - (vd / vj)) ** 2) + 0.005) ** (self.grading_coeff / 2)

    def diode_capacitance(self,
                          vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return self.transit_time_capacitance(vd) + (self.area * self.junction_capacitance(vd))

    def transit_time_capacitance(self,
                                 vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return self.transit_time * self.dc_conductance(vd)

    def dc_conductance(self,
                       vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        dqdv = derivative(self.forward_current, vd, dx=1.0e-6)
        return self.area * dqdv

    def junction_capacitance(self,
                             vd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vj = self.junction_potential()
        cjo = self.zero_bias_junction_capacitance()
        fc = self.forward_capacitance
        m = self.grading_coeff

        if vd <= (fc * vj):
            return cjo * ((1 - (vd / vj)) ** -m)
        else:
            f2 = (1 - fc) ** (1 + m)
            f3 = 1 - (fc * (1 + m))
            return (cjo / f2) * (f3 + (m * vd / vj))

    def parasitic_thermal_noise(self)-> float:
        """Parasitic resistance thermal noise per unit bandwidth. Bandwidth is assumed to be 1.0 Hz.

        Returns
        -------
        float
            Parasitic thermal noise mean-square value
        """
        return 4 * BOLTZMANN * self.temperature / (self.parasitic_resistance() / self.area)

    def intrinsic_diode_noise(self,
                              vd: float=0.0,
                              freq: float=1.0)-> float:
        """Intrinsic diode shot and flicker noise per unit bandwidth. Bandwidth is assumed to be 1.0 Hz.

        Parameters
        ----------
        vd : float, optional
            Diode voltage, by default 0.0 V
        freq : float, optional
            Frequency, by default 1.0 Hz

        Returns
        -------
        float
            intrinsic diode noise mean-square value
        """
        return (2 * CHARGE * self.diode_current(vd)) + (self.flicker_noise_coeff * self.diode_current(vd) / freq)

