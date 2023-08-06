'''Heterostructure modeling'''

import numpy as np
import matplotlib.pyplot as plt
from semicpy.math.coordinate import Rectangular2D

VACUUM = Rectangular2D(0,0)

class A:
    def __init__(self,ec,ef,ev,eg,chi):
        self.conduction_band_1 = ec
        self.fermi_level_1 = ef
        self.valence_band_1 = ev
        self.bandgap_1 = eg
        self.affinity_1 = chi

class B:
    def __init__(self,ec,ef,ev,eg,chi):
        self.conduction_band_2 = ec
        self.fermi_level_2 = ef
        self.valence_band_2 = ev
        self.bandgap_2 = eg
        self.affinity_2 = chi

class Heterostructure(A,B):
    def delta_ec(self)-> float:
        if((self.conduction_band_1 is None) or (self.conduction_band_2 is None)):
            return np.abs(self.affinity_1 - self.affinity_2)
        else:
            return np.abs(self.conduction_band_1 - self.conduction_band_2) 
    
    def delta_ev(self)-> float:
        if((self.valence_band_1 is None) or (self.valence_band_2 is None)):
            return np.abs(self.delta_eg() - self.delta_ec())
        else:
            return np.abs(self.valence_band_1 - self.valence_band_2)
    
    def delta_eg(self)-> float:
        if(self.bandgap_1 is None) or (self.bandgap_2 is None):
            return np.abs(self.delta_ec() + self.delta_ev())
        else:
            return np.abs(self.bandgap_1 - self.bandgap_2)

    def model(self):
        '''
        x1 = np.arange(VACUUM.x,5,1)
        x2 = np.arange(VACUUM.x+5,10,1)
        ec1 = VACUUM.y - self.affinity_1 # Conduction band semiconductor 1
        ec2 = VACUUM.y - self.chi2 # Conduction band semiconductor 2
        ev1 = VACUUM.y - self.ev1
        ev2 = VACUUM.y - self.ev2
        ef1 = VACUUM.y - self.ef1
        ef2 = VACUUM.y - self.ef2

        plt.plot(ec1)
        plt.show()'''
        pass