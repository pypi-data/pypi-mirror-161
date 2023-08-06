"""JFET Class Module"""
import numpy as np
from semicpy.constants.constants import value

CHARGE = value('Elementary charge')
BOLTZMANN = value('Boltzmann constant in J/K')
TNOM = 300.15 #27 deg Celsius in Kelvin

class JFET:
    """JFET Class
    """
    def __init__(self,
                 temp: float=0.0,
                 af: float=1.0,
                 alpha: float=0.0,
                 beta: float=1.0e-4,
                 betatce: float=0.0,
                 cgd: float=0.0,
                 cgs: float=0.0,
                 fc: float=0.5,
                 i_s: float=1.0e-14,
                 isr: float=0.0,
                 kf: float=0.0,
                 lamda: float=0.0,
                 m: float=0.5,
                 n: float=1.0,
                 nr: float=2.0,
                 pb: float=1.0,
                 rd: float=0.0,
                 rs: float=0.0,
                 vk: float=0.0,
                 vto: float=-2.0,
                 vtotc: float=0.0,
                 xti: float=3.0)-> None:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default 0.0
        af : float, optional
            _description_, by default 1.0
        alpha : float, optional
            _description_, by default 0.0
        beta : float, optional
            _description_, by default 1.0e-4
        betatce : float, optional
            _description_, by default 0.0
        cgd : float, optional
            _description_, by default 0.0
        cgs : float, optional
            _description_, by default 0.0
        fc : float, optional
            _description_, by default 0.5
        i_s : float, optional
            _description_, by default 1.0e-14
        isr : float, optional
            _description_, by default 0.0
        kf : float, optional
            _description_, by default 0.0
        lamda : float, optional
            _description_, by default 0.0
        m : float, optional
            _description_, by default 0.5
        n : float, optional
            _description_, by default 1.0
        nr : float, optional
            _description_, by default 2.0
        pb : float, optional
            _description_, by default 1.0
        rd : float, optional
            _description_, by default 0.0
        rs : float, optional
            _description_, by default 0.0
        vk : float, optional
            _description_, by default 0.0
        vto : float, optional
            _description_, by default -2.0
        vtotc : float, optional
            _description_, by default 0.0
        xti : float, optional
            _description_, by default 3.0
        """
        self.temperature = temp
        self.flicker_noise_exp = af
        self.ionization_coeff = alpha
        self.transconductance_coeff = beta
        self.beta_exp_temp_coeff = betatce
        self.zero_bias_gate_drain_pn_cap = cgd
        self.zero_bias_gate_source_pn_cap = cgs
        self.fwd_bias_depl_cap_coeff = fc
        self.gate_pn_sat_current = i_s
        self.gate_pn_rec_current_param = isr
        self.flicker_noise_coeff = kf
        self.ch_len_modulation = lamda
        self.gate_pn_grading_coeff = m
        self.gate_pn_emission_coeff = n
        self.emission_coeff_isr = nr
        self.gate_pn_potential = pb
        self.drain_ohmic_resist = rd
        self.source_ohmic_resist = rs
        self.ionization_knee_voltage = vk
        self.threshold_voltage = vto
        self.vto_temp_coeff = vtotc
        self.sat_current_temp_coeff = xti
    
    def gate_current(self,
                     area: float=0.0,
                     vgs: float=0.0,
                     vgd: float=0.0,
                     vds: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        area : float, optional
            _description_, by default 0.0
        vgs : float, optional
            _description_, by default 0.0
        vgd : float, optional
            _description_, by default 0.0
        vds : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return area * (self.__gate_source_leakage_current(vgs) + self.__gate_drain_leakage_current(vgd,vgs,vds))

    def __gate_source_leakage_current(self,
                                      vgs: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vgs : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return self.__normal_current(vgs) + (self.__recombination_current(vgs) * self.__generation_factor(vgs))
    
    def __gate_drain_leakage_current(self,
                                     vgd: float=0.0,
                                     vgs: float=0.0,
                                     vds: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vgd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        ii = self.__impact_ionization_current(vgs,vds)
        return self.__normal_current(vgd) + (self.__recombination_current(vgd) * self.__generation_factor(vgd)) + ii

    def __normal_current(self,
                         voltage: float=0.0)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * self.temperature / CHARGE

        i_n = self.gate_pn_sat_current * (np.exp(voltage / (self.gate_pn_emission_coeff * vt) - 1))
        return i_n

    def __recombination_current(self,
                                voltage: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        voltage : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * self.temperature / CHARGE

        ir = self.gate_pn_rec_current_param * (np.exp(voltage / (self.emission_coeff_isr * vt)) - 1)
        return ir

    def __generation_factor(self,
                            voltage: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        voltage : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return (((1 - (voltage / self.gate_pn_potential)) ** 2) + 0.005) ** (self.gate_pn_grading_coeff / 2)
    
    def __impact_ionization_current(self,
                                    vgs: float=0.0,
                                    vds: float=0.0,
                                    vgd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vgs : float, optional
            _description_, by default 0.0
        vds : float, optional
            _description_, by default 0.0
        vgd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vdif = vds - (vgs-self.threshold_voltage)
        if 0 < (vgs-self.threshold_voltage) < vds:
            ii = self.i_drain(vgs,vds,vgd) * self.ionization_coeff * vdif * np.exp(-self.ionization_knee_voltage/vdif)
        else:
            ii = 0
        return ii

    def drain_current(self,
                      area: float=0.0,
                      vgd: float=0.0,
                      vgs: float=0.0,
                      vds: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        area : float, optional
            _description_, by default 0.0
        vgd : float, optional
            _description_, by default 0.0
        vgs : float, optional
            _description_, by default 0.0
        vds : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return area * (self.i_drain(vgs,vds,vgd) - self.__gate_drain_leakage_current(vgd,vgs,vds))
    
    def source_current(self,
                       area: float=0.0,
                       vgs: float=0.0,
                       vds: float=0.0,
                       vgd: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        area : float, optional
            _description_, by default 0.0
        vgs : float, optional
            _description_, by default 0.0
        vds : float, optional
            _description_, by default 0.0
        vgd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return area * (-self.i_drain(vgs,vds,vgd) - self.__gate_source_leakage_current(vgs))

    def i_drain(self,
                vgs: float=0.0,
                vds: float=0.0,
                vgd: float=0.0)-> float:
        """DC characteristic of JFET which is represented by nonlinear current source, i_drain().
        For p-channel JFET, the polarities of Vgs,Vds, and Vgd must be reversed. The direction of
        i_drain must also be reversed.

        Parameters
        ----------
        vgs : float, optional
            _description_, by default 0.0
        vds : float, optional
            _description_, by default 0.0
        vgd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        if vds >= 0.0:
            if (vgs-self.threshold_voltage) <= 0.0:
                return 0
            elif 0 < vds <= (vgs - self.threshold_voltage):
                return self.transconductance_coeff * vds * ((2 * (vgs - self.threshold_voltage)) - vds) * (1 + (self.ch_len_modulation * vds))
            elif 0 < (vgs - self.threshold_voltage) < vds:
                return self.transconductance_coeff * ((vgs - self.threshold_voltage) ** 2) * (1 + (self.ch_len_modulation * vds))
        else: 
            if (vgd-self.threshold_voltage) <= 0.0:
                return 0
            elif 0 < -vds <= (vgd - self.threshold_voltage):
                return self.transconductance_coeff * vds * ((2 * (vgd - self.threshold_voltage)) - vds) * (1 + (self.ch_len_modulation * vds))
            elif 0 < (vgd-self.threshold_voltage) < -vds:
                return -self.transconductance_coeff * ((vgd - self.threshold_voltage) ** 2) * (1 + (self.ch_len_modulation * vds))
    
    def gate_source_depletion_capacitance(self,
                                          area: float=0.0,
                                          vgs: float=0.0)-> float:
        """gate-source depletion capacitance

        Parameters
        ----------
        area : float, optional
            _description_, by default 0.0
        vgs : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        if vgs <= (self.fwd_bias_depl_cap_coeff * self.gate_pn_potential):
            cgs = area * self.zero_bias_gate_source_pn_cap * ((1 - (vgs/self.gate_pn_potential)) ** -self.gate_pn_grading_coeff)
        else:
            cgs = area * self.zero_bias_gate_source_pn_cap * ((1 - self.fwd_bias_depl_cap_coeff) ** -(1+self.gate_pn_grading_coeff)) * (1 - self.fwd_bias_depl_cap_coeff * (1 + self.gate_pn_grading_coeff) + self.gate_pn_grading_coeff * (vgs/self.gate_pn_potential))
        return cgs

    def gate_drain_depletion_capacitance(self,
                                         area: float=0.0,
                                         vgd: float=0.0)-> float:
        """gate-drain depletion capacitance

        Parameters
        ----------
        area : float, optional
            _description_, by default 0.0
        vgd : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        if vgd <= (self.fwd_bias_depl_cap_coeff * self.gate_pn_potential):
            cgd = area * self.zero_bias_gate_drain_pn_cap * ((1 - (vgd/self.gate_pn_potential)) ** -self.gate_pn_grading_coeff)
        else:
            cgd = area * self.zero_bias_gate_drain_pn_cap * ((1 - self.fwd_bias_depl_cap_coeff) ** -(1+self.gate_pn_grading_coeff)) * (1 - self.fwd_bias_depl_cap_coeff * (1 + self.gate_pn_grading_coeff) + self.gate_pn_grading_coeff * (vgd/self.gate_pn_potential))
        return cgd
    
    def vto(self,
            temp: float=298.15,
            tnom: float=TNOM)-> float:
        """threshold voltage with temperature dependence

        Parameters
        ----------
        temp : float, optional
            _description_, by default 300.15
        tnom : float, optional
            _description_, by default 300.15

        Returns
        -------
        float
            _description_
        """
        return self.threshold_voltage + self.vto_temp_coeff * (temp - tnom)
    
    def beta(self,
             temp: float=298.15,
             tnom: float=TNOM)-> float:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default 300.15
        tnom : float, optional
            _description_, by default TNOM

        Returns
        -------
        float
            _description_
        """
        return self.transconductance_coeff * (1.01**(self.beta_exp_temp_coeff*(temp-tnom)))
    
    def i_s(self,
            temp: float=298.15,
            tnom: float=TNOM,
            eg: float=1.11)-> float:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default 300.15
        tnom : float, optional
            _description_, by default TNOM
        eg : float, optional
            _description_, by default 1.11

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * temp / CHARGE
        return self.gate_pn_sat_current * np.exp((temp/tnom - 1) * eg / (self.gate_pn_emission_coeff * vt)) * ((temp/tnom)**(self.sat_current_temp_coeff/self.gate_pn_emission_coeff))

    def isr(self,
            temp: float=298.15,
            tnom: float=TNOM,
            eg: float=1.11)-> float:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default 300.15
        tnom : float, optional
            _description_, by default TNOM
        eg : float, optional
            _description_, by default 1.11

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * temp / CHARGE
        return self.gate_pn_rec_current_param * np.exp((temp/tnom - 1) * eg / (self.emission_coeff_isr * vt)) * ((temp/tnom)**(self.sat_current_temp_coeff/self.emission_coeff_isr))

    def __eg(self,
             temp: float=0.0)-> float:
        """Si bandgap energy 

        Parameters
        ----------
        temp : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        if 0 < temp <= 190:
            A = 1.17
            B = 1.059e-5
            C = 6.05e-7
        if 150 <= temp <= 301:
            A = 1.1785
            B = -9.025e-5
            C = 3.05e-7
        eg = A + (B * temp) - (C * (temp**2))
        return eg
    
    def pb(self,
           temp: float=298.15,
           tnom: float=TNOM)-> float:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default 300.15
        tnom : float, optional
            _description_, by default TNOM

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * temp / CHARGE
        pb = self.gate_pn_potential * (temp/tnom) - (3 * vt * np.log(temp/tnom)) - (self.__eg(tnom) * temp/tnom) + self.__eg(temp)
        return pb
    
    def cgs(self,
            temp: float=298.15,
            tnom: float=TNOM)-> float:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default 300.15
        tnom : float, optional
            _description_, by default TNOM

        Returns
        -------
        float
            _description_
        """
        cgs = self.zero_bias_gate_source_pn_cap
        m = self.gate_pn_grading_coeff
        pb = self.gate_pn_potential
        tdiff = temp - tnom

        return cgs * (1 + m * ((0.0004 * tdiff) + (1-self.pb(temp)/pb)))

    def cgd(self,
            temp: float=298.15,
            tnom: float=TNOM)-> float:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default 300.15
        tnom : float, optional
            _description_, by default TNOM

        Returns
        -------
        float
            _description_
        """
        cgd = self.zero_bias_gate_drain_pn_cap
        m = self.gate_pn_grading_coeff
        pb = self.gate_pn_potential
        tdiff = temp - tnom

        return cgd * (1 + m * ((0.0004 * tdiff) + (1-self.pb(temp)/pb)))

    def source_thermal_noise(self,
                             area: float=0.0,
                             temp: float=298.15)-> float:
        """Parasitic source resistance thermal noise

        Parameters
        ----------
        area : float, optional
            _description_, by default 0.0
        temp : float, optional
            _description_, by default 298.15

        Returns
        -------
        float
            _description_
        """
        noise = (4 * BOLTZMANN * temp) / (self.source_ohmic_resist / area)
        return noise
    
    def drain_thermal_noise(self,
                            area: float=0.0,
                            temp: float=298.15)-> float:
        """Parasitic drain resistance thermal noise

        Parameters
        ----------
        area : float, optional
            _description_, by default 0.0
        temp : float, optional
            _description_, by default 298.15

        Returns
        -------
        float
            _description_
        """
        noise = (4 * BOLTZMANN * temp) / (self.drain_ohmic_resist / area)
        return noise
    
    def intrinsic_noise(self,
                        temp: float=298.15,
                        gm: float=0.0,
                        vgs: float=0.0,
                        vds: float=0.0,
                        vgd: float=0.0,
                        freq: float=1.0)-> float:
        """Intrinsic JFET thermal and flicker noise

        Parameters
        ----------
        temp : float, optional
            _description_, by default 298.15
        gm : float, optional
            _description_, by default 0.0
        vgs : float, optional
            _description_, by default 0.0
        vds : float, optional
            _description_, by default 0.0
        vgd : float, optional
            _description_, by default 0.0
        freq : float, optional
            _description_, by default 1.0

        Returns
        -------
        float
            _description_
        """
        thermal = (8/3) * BOLTZMANN * temp * gm
        flicker = self.flicker_noise_coeff * (self.i_drain(vgs,vds,vgd) ** self.flicker_noise_exp) / freq
        noise = thermal + flicker

        return noise