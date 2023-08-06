#%%
"""
Space-time module is to store the space-time class, as it is fairly lengthy in 
it self and requires all the data files to be read in, it lives seperately.
"""
from .pluto import py3Pluto
import os
import numpy as np
import matplotlib.pyplot as plt
import h5py

class SpaceTime(py3Pluto):

    def __init__(self, 
        data_path,
        data2plot,
        dpi=300,
        image_size=(10, 5),
        xlim=None,
        cmap='bwr',
        
    ):

        super().__init__(
            data_path = data_path,
            time_step = 0,
            dpi = dpi,
            image_size = image_size,
            xlim = xlim,
            cmap = cmap,
        )

        self.data_path = data_path
        self._read_folder()

    def _read_folder(self):
        self._files = os.listdir(self.data_path)
        self._ext = '.h5'
        self.data_list = [file for file in self._files if self._ext in file and 'out' not in file]
            
    def plot_spacetime(self, data2plot, log=False, save=False, close=False):
        """
        Method plots a space time diagram of the variables along the jet axis
        """
        return None