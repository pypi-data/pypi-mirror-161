"""module docstring for schottky barrier
"""
from semicpy.math.coordinate import Rectangular2D
import matplotlib.pyplot as plt
import numpy as np

VACUUM = Rectangular2D(0,0)

class Semiconductor:
    def __init__(self,ec,ef,ev,eg,chi):
        self.conduction_band = ec
        self.valence_band = ev
        self.fermi_level_sc = ef
        self.bandgap = eg
        self.affinity = chi


class Metal:
    def __init__(self,workfunction,ef_m):
        self.phi_m = workfunction
        self.fermi_level_metal = ef_m
    

class SchottkyBarrier(Metal,Semiconductor):
    def __init__(self,affinity):
        self.affinity = affinity
    
    def barrier_height(self):
        return self.phi_m - self.affinity
    
    def model(self):
        """_summary_
        """
        x = np.arange(VACUUM.x,10,1)
        y = -x - 1
        mod = plt.Figure()
        return mod

