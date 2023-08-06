"""
BJT Class Module
Based on https://www.seas.upenn.edu/~jan/spice/PSpice_ReferenceguideOrCAD.pdf
"""
from semicpy.constants.constants import value
import numpy as np
from scipy.misc import derivative

CHARGE = value('Elementary charge')
BOLTZMANN = value('Boltzmann constant in J/K')

class BJT:
    """BJT Class
    """
    def __init__(self,
                 temp: float=300,
                 tnom: float=300,
                 area: float=1.0,
                 af: float=1.0,
                 bf: float=100.0,
                 br: float=1.0,
                 cjc: float=0.0,
                 cje: float=0.0,
                 cjs: float=0.0,
                 cn: float=2.42,
                 d: float=0.87,
                 eg: float=1.11,
                 fc: float=0.5,
                 gamma: float=1.0e-11,
                 ikf: float=np.inf,
                 ikr: float=np.inf,
                 irb: float=np.inf,
                 i_s: float=1.0e-16,
                 isc: float=0.0,
                 ise: float=0.0,
                 iss: float=0.0,
                 itf: float=0.0,
                 kf: float=0.0,
                 mjc: float=0.33,
                 mje: float=0.33,
                 mjs: float=0.0,
                 nc: float=2.0,
                 ne: float=1.5,
                 nf: float=1.0,
                 nk: float=0.5,
                 nr: float=1.0,
                 ns: float=1.0,
                 ptf: float=0.0,
                 qco: float=0.0,
                 quasimod: int=0,
                 rb: float=0.0,
                 rbm: float=0.0,
                 rc: float=0.0,
                 rco: float=0.0,
                 re: float=0.0,
                 tf: float=0.0,
                 tr: float=0.0,
                 trb1: float=0.0,
                 trb2: float=0.0,
                 trc1: float=0.0,
                 trc2: float=0.0,
                 tre1: float=0.0,
                 tre2: float=0.0,
                 trm1: float=0.0,
                 trm2: float=0.0,
                 vaf: float=np.inf,
                 var: float=np.inf,
                 vg: float=1.206,
                 vjc: float=0.75,
                 vje: float=0.75,
                 vjs: float=0.75,
                 vo: float=10.0,
                 vtf: float=np.inf,
                 xcjc: float=1.0,
                 xcjc2: float=1.0,
                 xcjs: float=1.0,
                 xtb: float=0.0,
                 xtf: float=0.0,
                 xti: float=3.0) -> None:
        """_summary_

        Parameters
        ----------
        temp : float, optional
            _description_, by default 298
        tnom : float, optional
            _description_, by default 300
        area : float, optional
            _description_, by default 1.0
        af : float, optional
            _description_, by default 1.0
        bf : float, optional
            _description_, by default 100.0
        br : float, optional
            _description_, by default 1.0
        cjc : float, optional
            _description_, by default 0.0
        cje : float, optional
            _description_, by default 0.0
        cjs : float, optional
            _description_, by default 0.0
        cn : float, optional
            _description_, by default 2.42
        d : float, optional
            _description_, by default 0.87
        eg : float, optional
            _description_, by default 1.11
        fc : float, optional
            _description_, by default 0.5
        gamma : float, optional
            _description_, by default 1.0e-11
        ikf : float, optional
            _description_, by default np.inf
        ikr : float, optional
            _description_, by default np.inf
        irb : float, optional
            _description_, by default np.inf
        i_s : float, optional
            _description_, by default 1.0e-16
        isc : float, optional
            _description_, by default 0.0
        ise : float, optional
            _description_, by default 0.0
        iss : float, optional
            _description_, by default 0.0
        itf : float, optional
            _description_, by default 0.0
        kf : float, optional
            _description_, by default 0.0
        mjc : float, optional
            _description_, by default 0.33
        mje : float, optional
            _description_, by default 0.33
        mjs : float, optional
            _description_, by default 0.0
        nc : float, optional
            _description_, by default 2.0
        ne : float, optional
            _description_, by default 1.5
        nf : float, optional
            _description_, by default 1.0
        nk : float, optional
            _description_, by default 0.5
        nr : float, optional
            _description_, by default 1.0
        ns : float, optional
            _description_, by default 1.0
        ptf : float, optional
            _description_, by default 0.0
        qco : float, optional
            _description_, by default 0.0
        quasimod : int, optional
            _description_, by default 0
        rb : float, optional
            _description_, by default 0.0
        rbm : float, optional
            _description_, by default 0.0
        rc : float, optional
            _description_, by default 0.0
        rco : float, optional
            _description_, by default 0.0
        re : float, optional
            _description_, by default 0.0
        tf : float, optional
            _description_, by default 0.0
        tr : float, optional
            _description_, by default 0.0
        trb1 : float, optional
            _description_, by default 0.0
        trb2 : float, optional
            _description_, by default 0.0
        trc1 : float, optional
            _description_, by default 0.0
        trc2 : float, optional
            _description_, by default 0.0
        tre1 : float, optional
            _description_, by default 0.0
        tre2 : float, optional
            _description_, by default 0.0
        trm1 : float, optional
            _description_, by default 0.0
        trm2 : float, optional
            _description_, by default 0.0
        vaf : float, optional
            _description_, by default np.inf
        var : float, optional
            _description_, by default np.inf
        vg : float, optional
            _description_, by default 1.206
        vjc : float, optional
            _description_, by default 0.75
        vje : float, optional
            _description_, by default 0.75
        vjs : float, optional
            _description_, by default 0.75
        vo : float, optional
            _description_, by default 10.0
        vtf : float, optional
            _description_, by default np.inf
        xcjc : float, optional
            _description_, by default 1.0
        xcjc2 : float, optional
            _description_, by default 1.0
        xcjs : float, optional
            _description_, by default 1.0
        xtb : float, optional
            _description_, by default 0.0
        xtf : float, optional
            _description_, by default 0.0
        xti : float, optional
            _description_, by default 3.0
        """
        self.temperature = temp
        self.nominal_temperature = tnom
        self.area = area
        self.flicker_noise_exp = af
        self.ideal_max_fwd_beta = bf
        self.ideal_max_rev_beta = br
        self.base_collector_pn_cap = cjc
        self.base_emitter_pn_cap = cje
        self.substrate_pn_cap = cjs
        self.qsat_temp_coeff_hm = cn
        self.qsat_temp_coeff_hcv = d
        self.bandgap = eg
        self.fwd_bias_dep_cap_coeff = fc
        self.epitaxial_reg_doping_factor = gamma
        self.fwd_beta_hi_current = ikf
        self.rev_beta_hi_current = ikr
        self.rb_half_current = irb
        self.sat_current = i_s

        if isc > 1:
            self.base_collector_leak_is = isc*i_s
        elif 0 <= isc <= 1:
            self.base_collector_leak_is = isc
        else:
            raise ValueError("ISC value must be greater than or equal to 0!")
        if ise > 1:
            self.base_emitter_leak_is = ise*i_s
        elif 0 <= ise <= 1:
            self.base_emitter_leak_is = ise
        else:
            raise ValueError("ISE value must be greater than or equal to 0!")

        self.substrate_pn_sat_current = iss
        self.transit_time_dependency_IC = itf
        self.flicker_noise_coeff = kf
        self.base_collector_grading_factor = mjc
        self.base_emitter_grading_factor = mje
        self.substrate_grading_factor = mjs
        self.base_collector_leak_emission_coeff = nc
        self.base_emitter_leak_emission_coeff = ne
        self.fwd_current_emission_coeff = nf
        self.hi_current_ro_coeff = nk
        self.rev_current_emission_coeff = nr
        self.substrate_emission_coeff = ns
        self.excess_phase = ptf
        self.epitaxial_reg_charge_factor = qco
        self.qsat_flag = quasimod if rco == 0 else 1
        self.zero_bias_max_base_resistance = rb
        self.min_base_resistance = rbm
        self.collector_ohmic_resistance = rc
        self.epitaxial_reg_resistance = rco
        self.emitter_ohmic_resistance = re
        self.ideal_fwd_transit_time = tf
        self.ideal_rev_transit_time = tr
        self.rb_temp_coeff_lin = trb1
        self.rb_temp_coeff_quad = trb2
        self.rc_temp_coeff_lin = trc1
        self.rc_temp_coeff_quad = trc2
        self.re_temp_coeff_lin = tre1
        self.re_temp_coeff_quad = tre2
        self.rbm_temp_coeff_lin = trm1
        self.rbm_temp_coeff_quad = trm2
        self.fwd_early_voltage = vaf
        self.rev_early_voltage = var
        self.qsat_bandgap_voltage_zero_k = vg
        self.base_collector_pot = vjc
        self.base_emitter_pot = vje
        self.substrate_pot = vjs
        self.carrier_mob_knee_voltage = vo
        self.transit_time_dependency_Vbc = vtf
        self.frac_cjc_internal_rb = xcjc
        self.frac_cjc_internal_rb2 = xcjc2
        self.frac_cjs_internal_rc = xcjs
        self.fwd_rev_beta_temp_coeff = xtb
        self.transit_time_bias_dependence_coeff = xtf
        self.is_temperature_exp = xti

    def thermal_voltage(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        return BOLTZMANN * self.temperature / CHARGE

    def base_current(self,
                     vbe: float=0.0,
                     vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbe : float, optional
            _description_, by default 0.0
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        ibe1 = self.forward_diffusion_current(vbe)
        bf = self.forward_beta()
        br = self.reverse_beta()
        ibe2 = self.non_ideal_base_emitter_current(vbe)
        ibc1 = self.reverse_diffusion_current(vbc)
        ibc2 = self.non_ideal_base_collector_current(vbc)
        
        return self.area * ((ibe1 / bf) + ibe2 + (ibc1 / br) + ibc2)

    def collector_current(self,
                          vbe: float=0.0,
                          vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbe : float, optional
            _description_, by default 0.0
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        ibe1 = self.forward_diffusion_current(vbe)
        ibc1 = self.reverse_diffusion_current(vbc)
        ibc2 = self.non_ideal_base_collector_current(vbc)
        kqb = self.base_charge_factor(vbe,vbc)
        br = self.reverse_beta()

        return self.area * ((ibe1 / kqb) - (ibc1 / kqb) - (ibc1 / br) - ibc2)

    def forward_beta(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature / self.nominal_temperature
        return self.fwd_beta_hi_current * (t_tnom ** self.fwd_rev_beta_temp_coeff)

    def reverse_beta(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature / self.nominal_temperature
        return self.rev_beta_hi_current * (t_tnom ** self.fwd_rev_beta_temp_coeff)

    def __eg(self,
             temp: float or int)-> float:
        """_summary_

        Parameters
        ----------
        temp : _type_
            _description_

        Returns
        -------
        float
            _description_
        """
        return 1.17 - ((7.02e-4 * temp ** 2) / (temp + 1108))    
    
    def forward_diffusion_current(self,
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
        vt = self.thermal_voltage()
        return self.saturation_current() * (np.exp(voltage/(vt * self.fwd_current_emission_coeff)) - 1)
        
    def saturation_current(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature / self.nominal_temperature
        vt = self.thermal_voltage()
        return self.sat_current * np.exp((t_tnom - 1) * self.__eg(self.temperature) / vt) * (t_tnom ** self.is_temperature_exp)

    def non_ideal_base_emitter_current(self,
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
        vt = self.thermal_voltage()
        ise = self.base_emitter_leakage_current()

        return ise * (np.exp(voltage / (vt * self.base_emitter_leak_emission_coeff)) - 1)
    
    def base_emitter_leakage_current(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature / self.nominal_temperature
        vt = self.thermal_voltage()

        return (self.base_emitter_leak_is / (t_tnom ** self.fwd_rev_beta_temp_coeff)) * np.exp((t_tnom - 1) * self.__eg(self.temperature) / (vt * self.base_emitter_leak_emission_coeff)) * (t_tnom ** (self.is_temperature_exp / self.base_emitter_leak_emission_coeff))
    
    def base_collector_leakage_current(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature / self.nominal_temperature
        vt = self.thermal_voltage()

        return (self.base_collector_leak_is / (t_tnom ** self.fwd_rev_beta_temp_coeff)) * np.exp((t_tnom - 1) * self.__eg(self.temperature) / (vt * self.base_collector_leak_emission_coeff)) * (t_tnom ** (self.is_temperature_exp / self.base_collector_leak_emission_coeff))

    def reverse_diffusion_current(self,
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
        vt = self.thermal_voltage()

        return self.saturation_current() * (np.exp(voltage / (self.rev_current_emission_coeff * vt)) - 1)

    def non_ideal_base_collector_current(self,
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
        vt = self.thermal_voltage()

        return self.base_collector_leakage_current() * (np.exp(voltage / (self.base_collector_leak_emission_coeff * vt)) - 1)

    def base_charge_factor(self,
                           vbe: float=0.0,
                           vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbe : float, optional
            _description_, by default 0.0
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        kq1 = 1 / (1 - (vbc / self.fwd_early_voltage) - (vbe / self.rev_early_voltage))
        kq2 = (self.forward_diffusion_current(vbe) / self.fwd_beta_hi_current) + (self.reverse_diffusion_current(vbc) / self.rev_beta_hi_current)

        return kq1 * (1 + ((1 + (4 * kq2)) ** self.hi_current_ro_coeff)) / 2
    
    def substrate_current(self,
                          vjs: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vjs : float, optional
            intrinsic collector-substrate voltage (NPN), by default 0.0 V
            intrinsic substrate-collector voltage (PNP)
            intrinsic base-substrate voltage (LPNP)

        Returns
        -------
        float
            _description_
        """
        vt = BOLTZMANN * self.temperature / CHARGE
        iss = self.substrate_saturation_current()

        return self.area * iss * (np.exp(vjs / (self.substrate_emission_coeff * vt)) - 1)

    def substrate_saturation_current(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature / self.nominal_temperature
        vt = self.thermal_voltage()

        return (self.substrate_pn_sat_current / (t_tnom ** self.fwd_rev_beta_temp_coeff)) * np.exp((t_tnom - 1) * self.__eg(self.temperature) / (vt * self.substrate_emission_coeff)) * (t_tnom ** (self.is_temperature_exp / self.substrate_emission_coeff))

    def actual_base_parasitic_resistance(self,
                                         vbe: float=0.0,
                                         vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbe : float, optional
            _description_, by default 0.0
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        if self.rb_half_current == np.inf:
            return (self.minimum_base_resistance() + ((self.maximum_base_resistance() - self.minimum_base_resistance()) / self.base_charge_factor(vbe,vbc))) / self.area
        elif self.rb_half_current > 0:
            x = (np.sqrt((1 + (144 / (np.pi ** 2))) * self.base_current(vbe,vbc) / (self.area * self.rb_half_current)) - 1) / ((24 / (np.pi ** 2)) * np.sqrt(self.base_current(vbe,vbc) / (self.area * self.rb_half_current)))
            return (self.minimum_base_resistance() + 3 * (self.maximum_base_resistance() - self.minimum_base_resistance()) * ((np.tan(x) - x) / (x * (np.tan(x)) ** 2))) / self.area
        else:
            raise Exception("IRB is less than 0!")

    def minimum_base_resistance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        return self.min_base_resistance * (1 + (self.rbm_temp_coeff_lin * t_tnom) + (self.rbm_temp_coeff_quad * (t_tnom ** 2)))
        
    def maximum_base_resistance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        return self.zero_bias_max_base_resistance * (1 + (self.rb_temp_coeff_lin* t_tnom) + (self.rb_temp_coeff_quad * (t_tnom ** 2)))

    def collector_resistance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        return self.collector_ohmic_resistance * (1 + (self.rc_temp_coeff_lin * t_tnom) + (self.rc_temp_coeff_quad * (t_tnom ** 2)))
    
    def emitter_resistance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        return self.emitter_ohmic_resistance * (1 + (self.re_temp_coeff_lin * t_tnom) + (self.re_temp_coeff_quad * (t_tnom ** 2)))

    def base_emitter_potential(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        vt = self.thermal_voltage()
        t_tnom = self.temperature / self.nominal_temperature
        
        return (self.base_emitter_pot * t_tnom) - (3 * vt * np.log(t_tnom)) - (self.__eg(self.nominal_temperature) * t_tnom) + self.__eg(self.temperature)

    def base_collector_potential(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        vt = self.thermal_voltage()
        t_tnom = self.temperature / self.nominal_temperature

        return (self.base_collector_pot * t_tnom) - (3 * vt * np.log(t_tnom)) - (self.__eg(self.nominal_temperature) * t_tnom) + self.__eg(self.temperature)

    def substrate_potential(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        vt = self.thermal_voltage()
        t_tnom = self.temperature / self.nominal_temperature

        return (self.substrate_pot * t_tnom) - (3 * vt * np.log(t_tnom)) - (self.__eg(self.nominal_temperature) * t_tnom) + self.__eg(self.temperature) 

    def temp_dep_base_emitter_capacitance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        mje = self.base_emitter_grading_factor

        return self.base_emitter_pn_cap * (1 + (mje * (4e-4 * t_tnom + (1 - (self.base_emitter_potential() / self.base_emitter_pot)))))
    
    def temp_dep_base_collector_capacitance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        mjc = self.base_collector_grading_factor

        return self.base_collector_pn_cap * (1 + (mjc * (4e-4 * t_tnom + (1 - (self.base_collector_potential() / self.base_collector_pot)))))

    def temp_dep_substrate_capacitance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        t_tnom = self.temperature - self.nominal_temperature
        mjs = self.substrate_grading_factor

        return self.substrate_pn_cap * (1 + (mjs * (4e-4 * t_tnom + (1 - (self.substrate_potential() / self.substrate_pot)))))

    def base_emitter_capacitance(self,
                                 vbe: float=0.0,
                                 vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbe : float, optional
            _description_, by default 0.0
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return self.transit_time_capacitance_be(vbc,vbe) + (self.area * self.base_emitter_junction_capacitance(vbe))

    def base_emitter_current(self,
                             vbe: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbe : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return self.forward_diffusion_current(vbe) + self.non_ideal_base_emitter_current(vbe)
    
    def base_collector_current(self,
                               vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return self.reverse_diffusion_current(vbc) + self.non_ideal_base_collector_current(vbc)

    def transit_time_capacitance_be(self,
                                 vbc: float=0.0,
                                 vbe: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbc : float, optional
            _description_, by default 0.0
        vbe : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vbc_comp = np.exp(vbc / (1.44 * self.transit_time_dependency_Vbc))
        sq_term = np.square(self.forward_diffusion_current(vbe) / (self.forward_diffusion_current(vbe) + (self.area * self.transit_time_dependency_IC)))
        tf = self.ideal_fwd_transit_time * (1 + (self.transit_time_bias_dependence_coeff * sq_term * vbc_comp))
        
        return tf * self.dc_conductance(self.base_emitter_current,vbe)

    def dc_conductance(self,
                       func,
                       voltage: float=0.0,
                       dV: float=1.0e-6)-> float:
        """_summary_

        Parameters
        ----------
        func : _type_
            _description_
        voltage : float, optional
            _description_, by default 0.0
        dV : float, optional
            _description_, by default 1.0e-6

        Returns
        -------
        float
            _description_
        """
        return derivative(func, voltage, dx=dV) 
    
    def base_emitter_junction_capacitance(self,
                                          vbe: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbe : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        fc = self.fwd_bias_dep_cap_coeff
        vje = self.base_emitter_potential()
        mje = self.base_emitter_grading_factor
        cje = self.temp_dep_base_emitter_capacitance()

        if (fc * vje) >= vbe:
            return cje * ((1 - (vbe / vje)) ** -mje)
        else:
            return cje * ((1 - fc) ** -(1 + mje)) * (1 - (fc * (1 + mje)) + (mje * vbe / vje))
    
    def base_collector_capacitance(self,
                                   vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        if (0.0 < self.frac_cjc_internal_rb2 < 1.0):
            return self.transit_time_capacitance_bc(vbc) + (self.area * self.frac_cjc_internal_rb2 * self.base_collector_junction_capacitance(vbc))
        else:
            return self.transit_time_capacitance_bc(vbc) + (self.area * self.frac_cjc_internal_rb * self.base_collector_junction_capacitance(vbc))

    def transit_time_capacitance_bc(self,
                                    vbc)-> float:
        """_summary_

        Parameters
        ----------
        vbc : _type_
            _description_

        Returns
        -------
        float
            _description_
        """
        return self.ideal_rev_transit_time * self.dc_conductance(self.base_collector_current,vbc)

    def base_collector_junction_capacitance(self,
                                            vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        fc = self.fwd_bias_dep_cap_coeff
        vjc = self.base_collector_potential()
        mjc = self.base_collector_grading_factor
        cjc = self.temp_dep_base_collector_capacitance()


        if vbc < (fc * vjc):
            return cjc * ((1 - (vbc / vjc)) ** -mjc)
        else:
            return cjc * ((1 - fc) ** -(1 + mjc)) * (1 - (fc * (1 + mjc)) + (mjc * vbc / vjc))

    def extrinsic_base_collector_capacitance(self,
                                             vbx: float=0.0,
                                             cnode: str="intrinsic")-> float:
        """_summary_

        Parameters
        ----------
        vbx : float, optional
            _description_, by default 0.0
        cnode : str, optional
            _description_, by default "intrinsic"

        Returns
        -------
        float
            _description_
        """
        if cnode == "intrinsic":
            return self.area * (1 - self.frac_cjc_internal_rb) * self.bx_junction_capacitance(vbx)
        elif cnode == "extrinsic":
            return self.area * (1 - self.frac_cjc_internal_rb2) * self.bx_junction_capacitance(vbx)
        else:
            raise Exception("cnode must be 'intrinsic' or 'extrinsic'!")

    def bx_junction_capacitance(self,
                                vbx: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbx : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        cjc = self.temp_dep_base_collector_capacitance()
        vjc = self.base_collector_potential()
        mjc = self.base_collector_grading_factor
        fc = self.fwd_bias_dep_cap_coeff

        if vbx <= (fc * vjc):
            return cjc * ((1 - (vbx / vjc)) ** -mjc)
        else:
            return cjc * ((1 - fc) ** -(1 + mjc)) * (1 - (fc * (1 + mjc)) + (mjc * vbx / vjc))
    
    def substrate_junction_capacitance(self,
                                       vjs: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vjs : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vj_s = self.substrate_potential()
        cjs = self.temp_dep_substrate_capacitance()
        mjs = self.substrate_grading_factor

        if vjs <= 0:
            return self.area * cjs * ((1 - (vjs / vj_s)) ** -mjs)
        else:
            return self.area * cjs * (1 + (mjs * vjs / vj_s))
    
    def epitaxial_region_doping_factor(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        gamma = self.epitaxial_reg_doping_factor
        tnom = self.nominal_temperature
        t = self.temperature
        t_tnom = self.temperature / self.nominal_temperature
        vg = self.qsat_bandgap_voltage_zero_k
        q = CHARGE
        k = BOLTZMANN

        return gamma * (t_tnom ** 3) * np.exp((-q * vg / k) * ((1 / t) - (1 / tnom)))
    
    def epitaxial_region_resistance(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        rco = self.epitaxial_reg_resistance
        t_tnom = self.temperature / self.nominal_temperature

        return rco * (t_tnom ** self.qsat_temp_coeff_hm)

    def carrier_mobility_knee_voltage(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        cn_d = self.qsat_temp_coeff_hm - self.qsat_temp_coeff_hcv
        t_tnom = self.temperature / self.nominal_temperature
        vo = self.carrier_mob_knee_voltage

        return vo * (t_tnom ** cn_d)

    def quasisaturation_effect(self,
                               vbc: float=0.0,
                               vbn: float=0.0)-> dict:
        """_summary_

        Parameters
        ----------
        vbc : float, optional
            _description_, by default 0.0
        vbn : float, optional
            _description_, by default 0.0

        Returns
        -------
        dict
            _description_
        """
        if self.qsat_flag == 0:
            vo = self.carrier_mob_knee_voltage
            rco = self.epitaxial_reg_resistance
            gamma = self.epitaxial_reg_doping_factor
        else:
            vo = self.carrier_mobility_knee_voltage()
            rco = self.epitaxial_region_resistance()
            gamma = self.epitaxial_region_doping_factor()
        
        if rco == 0:
            raise Exception("RCO must be greater than 0 for Epitaxial Region Current and Charge!")
        else:
            vt = self.thermal_voltage()
            qco = self.epitaxial_reg_charge_factor
            iepi = self.area * (vo * (vt * (self.k_v(gamma,vbc) - self.k_v(gamma,vbn) - np.log((1 + self.k_v(gamma,vbc)) / (1 + self.k_v(gamma,vbn)))) + vbc - vbn)) / (rco * (np.abs(vbc - vbn) + vo))
            qo = self.area * qco * (self.k_v(gamma,vbc) - 1 - (gamma / 2))
            qw = self.area * qco * (self.k_v(gamma,vbn) - 1 - (gamma / 2))
            qepi = qo + qw
            return {"Epitaxial Region Current" : iepi, "Epitaxial Region Charge" : qepi}
    
    def k_v(self,
            gamma: float,
            voltage: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        gamma : float
            _description_
        voltage : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        vt = self.thermal_voltage()
        return np.sqrt(1 + (gamma * np.exp(voltage / vt)))
    
    def parasitic_collector_resistance_thermal_noise(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        return 4 * BOLTZMANN * self.temperature / (self.collector_resistance() / self.area)
    
    def parasitic_base_resistance_thermal_noise(self,
                                                vbe: float=0.0,
                                                vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbe : float, optional
            _description_, by default 0.0
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return 4 * BOLTZMANN * self.temperature / self.actual_base_parasitic_resistance(vbe,vbc)
    
    def parasitic_emitter_resistance_thermal_noise(self)-> float:
        """_summary_

        Returns
        -------
        float
            _description_
        """
        return 4 * BOLTZMANN * self.temperature / (self.emitter_resistance() / self.area)
    
    def base_current_noise(self,
                           freq: float=1.0,
                           vbe: float=0.0,
                           vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        freq : float, optional
            _description_, by default 1.0
        vbe : float, optional
            _description_, by default 0.0
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return 2 * CHARGE * self.base_current(vbe,vbc) + (self.flicker_noise_coeff * (self.base_current(vbe,vbc) ** self.flicker_noise_exp) / freq)

    def collector_current_noise(self,
                                vbe: float=0.0,
                                vbc: float=0.0)-> float:
        """_summary_

        Parameters
        ----------
        vbe : float, optional
            _description_, by default 0.0
        vbc : float, optional
            _description_, by default 0.0

        Returns
        -------
        float
            _description_
        """
        return 2 * CHARGE * self.collector_current(vbe,vbc)

class NPN(BJT):
    """_summary_

    Parameters
    ----------
    BJT : _type_
        _description_
    """
    pass

class PNP(BJT):
    """_summary_

    Parameters
    ----------
    BJT : _type_
        _description_
    """
    pass

def vbe(vb: float=0.0,
        ve: float=0.0)-> float:
    """_summary_

    Parameters
    ----------
    vb : float, optional
        _description_, by default 0.0
    ve : float, optional
        _description_, by default 0.0

    Returns
    -------
    float
        _description_
    """
    voltage = vb-ve
    return voltage

def vbc(vb: float=0.0,
        vc: float=0.0)-> float:
    """_summary_

    Parameters
    ----------
    vb : float, optional
        _description_, by default 0.0
    vc : float, optional
        _description_, by default 0.0

    Returns
    -------
    float
        _description_
    """
    voltage = vb - vc
    return voltage

def vce(vc: float=0.0,
        ve: float=0.0)-> float:
    """_summary_

    Parameters
    ----------
    vc : float, optional
        _description_, by default 0.0
    ve : float, optional
        _description_, by default 0.0

    Returns
    -------
    float
        _description_
    """
    voltage = vc - ve
    return voltage

def i_e(i_en: float=0.0,
        i_ep: float=0.0)-> float:
    """
    Emitter current in a Bipolar Junction Transistor

    Parameters
    ----------
    i_en : TYPE, optional
        DESCRIPTION. The default is 0.
    i_ep : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    None.

    """
    ie = i_en + i_ep
    return ie

def i_b(i_ep: float=0.0,
        i_br: float=0.0,
        i_cp: float=0.0)-> float:
    """
    Base current in a Bipolar Junction Transistor

    Parameters
    ----------
    i_ep : TYPE, optional
        DESCRIPTION. The default is 0.
    i_br : TYPE, optional
        DESCRIPTION. The default is 0.
    i_cp : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    None.

    """
    ib = i_ep + i_br - i_cp
    return ib

def i_c(i_cn: float=0.0,
        i_cp: float=0.0)-> float:
    """
    Collector current in a Bipolar Junction Transistor

    Parameters
    ----------
    i_cn : TYPE, optional
        DESCRIPTION. The default is 0.
    i_cp : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    None.

    """
    ic = i_cn + i_cp
    return ic

def emitter_injection_efficiency(i_en: float=0.0,
                                 i_e: float=1.0)-> float:
    """
    The emitter injection efficiency measures the fraction
    of the emitter current carried by the desired electrons
    or holes in a NPN or PNP device. The default is for a
    NPN device.

    Parameters
    ----------
    i_en : float, required
        Electron emitter current. The default is 0.
    i_e : TYPE, optional
        Emitter current. The default is 1.

    Returns
    -------
    A float value corresponding to the emitter injection efficiency

    """
    gamma = i_en / i_e
    return gamma

def base_transport_factor(i_cn: float=0.0,
                          i_en: float=1.0)-> float:
    """
    The base transport factor measures the fraction of
    electrons that make it into the collector after injection
    from the emitter.

    Parameters
    ----------
    i_cn : TYPE, optional
        DESCRIPTION. The default is 0.
    i_en : TYPE, optional
        DESCRIPTION. The default is 1.

    Returns
    -------
    None.

    """
    alpha_t = i_cn / i_en
    return alpha_t

def common_base_current_gain(spec: str=None,
                             i_c: float=0.0,
                             i_e: float=1.0,
                             beta: float=0.0)-> float:
    """
    The low frequency common-base current gain of a bipolar
    junction transistor.

    Parameters
    ----------
    spec : string, required
        Specifies calculation type. Choose 'beta' for
        calculations based on common-emitter current gain.
        The default is None.
    i_c : float, optional
        Collector current. The default is 0.
    i_e : float, optional
        Emitter current. The default is 1.
    beta : float, optional
        Common-emitter current gain. The default is 0.

    Returns
    -------
    Float value corresponding to the low freq common-base current gain

    """
    if(spec == 'beta'):
        alpha_dc = beta / (beta + 1)
    else:
        alpha_dc = i_c / i_e
    return alpha_dc

def common_emitter_current_gain(spec: str=None,
                                i_c: float=0.0,
                                i_b: float=1.0,
                                alpha: float=0.0)-> float:
    """
    The common-emitter current gain of a bipolar
    junction transistor.

    Parameters
    ----------
    spec : string, required
        Specifies calculation type. Choose 'alpha' for
        calculations based on common-base current gain.
        The default is None.
    i_c : float, optional
        Collector current. The default is 0.
    i_b : float, optional
        Base current. The default is 1.
    alpha : float, optional
        Common-base current gain. The default is 0.

    Returns
    -------
    Float value corresponding to the common-emitter current gain

    """
    if(spec == 'alpha'):
        beta_dc = alpha / (1 - alpha)
    else:
        beta_dc = i_c / i_b
    return beta_dc
