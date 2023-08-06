"""
The module contains the subclass of the package that deals with all the magnetohydrodynamic visualisation.
It selects the variable to use for each visualisation method when they are called.
"""
from typing import Tuple
from .pluto import py3Pluto
from mpl_toolkits.axes_grid1 import make_axes_locatable as mal
from .calculator import RH_MHD

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import time
import os

class mhd_jet(py3Pluto):
    """
    This is a sub-class of py3Pluto, designed to visualise all MHD specific data sets calculated in the superclass.
    
        data_path: str - path to .h5 files output by PLUTO
        time_step: int - the number which is in the name of the file representing time-step
            Defaults to 0
        dpi: int - sets the matplotlib.pyplot artist's DPI parameter
            Defaults to 300,
        image_size: Tuple[int, int] - sets the matplotlib.pyplot artist's figsize argument
            Defaults to (10,5),
        ylim: float - sets the x-axis limit using matplotlib.pyplot xlim method
            Default to None,
        xlim: float - sets the y-axis limit using matplotlib.pyplot ylim method
            Default to None,
        cmap: str - colourmap used by matplotlib, takes a string and will give error if incorrect. 
            Default to 'bwr',
        global_limits: bool - if set True, all data file in directory will be looped through, and all
        the maximum and minimum values of all calculated variables are selected.
            Default to False,
        mirrored:bool = False,
        gamma: float = 5/3,
        title: str = ''

    """
    def __init__(self,
        data_path: str,
        time_step: int = 0,
        dpi: int = 300,
        image_size: Tuple[int, int] = (10,5),
        ylim: float = None,
        xlim: float = None,
        cmap: str = 'bwr',
        global_limits: bool = False,
        mirrored:bool = False,
        gamma: float = 5/3,
        title: str = ''
    ):

        super().__init__(
            data_path = data_path,
            time_step = time_step,
            dpi = dpi,
            image_size = image_size,
            ylim = ylim,
            xlim = xlim,
            cmap = cmap,
            global_limits = global_limits,
            mirrored = mirrored,
            gamma = gamma
        )
        self.data = None
        self.figure = None
        self.simulation_title = title

    def _data(self, data2plot=None, log=False, close=False, save=False):
        """
        Method plots individual data sets that are given as an argument.
        """
        if data2plot == None: # Size can be reduced by creating a dictionary with data2plot as key and name, data are values
            
            for sign, name in zip(self.varname_dict.keys(), self.varname_dict.values()):
                print(f'{sign:>15}:     {name}')
            data = None
            raise ValueError('Please give a variable to plot!')

        else:
            variable_name = self.varname_dict[data2plot]
            if log == True:
                data = np.log(self.data_dict[data2plot])
            else:
                data = self.data_dict[data2plot]
                        
        self.data = data
        self.variable_name = variable_name

        prefix = ''
        if log == True:
            prefix = 'Log of'
        self.title = f'{prefix} {variable_name}'

    def plot(self, data2plot=None, log=False, close=False, save=False, title=''):
        """
        This method plots the simulated data sets output by PLUTO, contained within the h5 file
        while additionally also plots the wave velocities, machnumbers and other calculated values.
        Focuses on spatial distributon of the data.
        """
        self._data(data2plot=data2plot, log=log, close=close, save=save)
        figure, axes = plt.subplots(figsize=self.image_size, dpi=self.dpi)
        plt.tight_layout()
        divider = mal(axes)
        cax = divider.append_axes('right',size='5%',pad=0.25)
        pl = axes.contourf(self.axial_grid, self.radial_grid, self.data, cmap=self.cmap, levels=128, alpha=0.95)
        plt.colorbar(pl,cax,ticks=np.linspace(np.min(self.data),np.max(self.data), 9))
        axes.set_xlim(self.xlim[0], self.xlim[1])
        axes.set_ylim(self.ylim[0], self.ylim[1])
        axes.set_ylabel(r'Radial distnace [$R_{jet}$]')
        axes.set_xlabel(r'Axial distance [$R_{jet}$]')
        

        if close==True:
            plt.close()

        if save==True:
            check_dir = f'{self.data_path}plot'
            chck_subdir = check_dir + f'/{data2plot}'
            if os.path.exists(check_dir) is False:
                os.mkdir(check_dir, 755)
            if os.path.exists(chck_subdir) is False:
                os.mkdir(chck_subdir, 755)
            bbox = matplotlib.transforms.Bbox([[0,0], [12,9]])
            plt.savefig(f'{self.data_path}plot/{data2plot}/{self.time_step}_{data2plot}_{title}.jpeg', bbox_inches='tight', pad_inches=0.5)
            plt.close()

    def hist(self,  data2plot=None, data2log=False, close=False, save=False, bins=None, log=False):
        """
        Method to plot histogram of the data which is passed in as the argument
        """
        self._data(data2plot=data2plot, log=log, close=close, save=save)
        title = self.title
        shape = self.data.shape
        x_shape = shape[0]*shape[1]
        new_shape = (x_shape, 1)
        data_plot = np.reshape(self.data, new_shape)
        plt.rc('font', size=8)
        fig, axes = plt.subplots(1,1,figsize=self.image_size, dpi=self.dpi)
        hist = axes.hist(data_plot, bins=bins, align='mid', edgecolor='white')
        axes.set_xlabel('Value')
        axes.set_ylabel('Frequency')
        cols = axes.patches
        labels = [f'{int(x)/x_shape*100:.2f}%' for x in hist[0]]
        
        for col, label in zip(cols, labels):
            height = col.get_height()
            axes.text(col.get_x() + col.get_width() / 2, height+0.01, label, ha='center', va='bottom')
    
        if data2log==True:
            plt.semilogy()
        
        if close==True:
            plt.close()

        if save==True:
            check_dir = f'{self.data_path}hist'
            chck_subdir = check_dir + f'/{data2plot}'
            if os.path.exists(check_dir) is False:
                os.mkdir(check_dir, 755)
            if os.path.exists(chck_subdir) is False:
                os.mkdir(chck_subdir, 755)
            bbox = matplotlib.transforms.Bbox([[0,0], [12,9]])
            plt.savefig(f'{self.data_path}hist/{data2plot}/{self.time_step}.jpeg', bbox_inches='tight', pad_inches=0.5)
            plt.close()
        
    def shocks(self, plot_shock='12, 13, 14, 23, 24, 34', save=False, close=False):
        """
        method to plot MHD shocks
        """
        self.plot_shock = plot_shock
        #### Super fast MS to Super Alfvénic ####
        zero_array = np.zeros_like(self.mach_fast)
        self.fast_shock_ax = []
        self.fast_shock_ra = []
        for j, row in enumerate(zero_array):
            for i, val in enumerate(row):
                if (i+1 == len(row)) or (j+1 == len(zero_array)):
                    pass
                else:
                    if (self.mach_fast[j,i] > 1) and (self.mach_fast[j,i+1] < 1) and (self.mach_alfvén[j,i+1] > 1):
                        self.fast_shock_ax.append(self.axial_grid[i])
                        self.fast_shock_ra.append(self.radial_grid[j])
                    if (self.mach_fast[j,i] > 1) and (self.mach_fast[j+1,i] < 1) and (self.mach_alfvén[j+1,i] > 1):
                        self.fast_shock_ax.append(self.axial_grid[i])
                        self.fast_shock_ra.append(self.radial_grid[j])
                    if (self.mach_fast[j,i] > 1) and (self.mach_fast[j+1,i+1] < 1) and (self.mach_alfvén[j+1,i+1] > 1):
                        self.fast_shock_ax.append(self.axial_grid[i])
                        self.fast_shock_ra.append(self.radial_grid[j])
                
        #### Intermed. Shocks #####
        self.inter_shock_ax1 = []
        self.inter_shock_ra1 = []
        self.inter_shock_ax2 = []
        self.inter_shock_ra2 = []
        self.inter_shock_ax3 = []
        self.inter_shock_ra3 = []
        self.inter_shock_ax4 = []
        self.inter_shock_ra4 = []
        
        for j, row in enumerate(zero_array):
            for i, val in enumerate(row):
                if (i+1 == len(row)) or (j+1 == len(zero_array)):
                    pass
                else:
                    ### Super Fast to Sub Alfvénic, Super Slow (1-3)
                    # perpendicular shocks
                    if (self.mach_fast[j,i] > 1) and (self.mach_alfvén[j,i+1] < 1) and (self.mach_slow[j,i+1] > 1):
                        self.inter_shock_ax1.append(self.axial_grid[i])
                        self.inter_shock_ra1.append(self.radial_grid[j])
                    # parallel shocks
                    if (self.mach_fast[j,i] > 1) and (self.mach_alfvén[j+1,i] < 1) and (self.mach_slow[j+1,i] > 1):
                        self.inter_shock_ax1.append(self.axial_grid[i])
                        self.inter_shock_ra1.append(self.radial_grid[j])
                    # oblique shocks
                    if (self.mach_fast[j,i] > 1) and (self.mach_alfvén[j+1,i+1] < 1) and (self.mach_slow[j+1,i+1] > 1):
                        self.inter_shock_ax1.append(self.axial_grid[i])
                        self.inter_shock_ra1.append(self.radial_grid[j])
                    
                    ## Sub Fast, Super Alfvénic to Sub Alfvénic, Super Slow (2-3)
                    # perpendicular shocks
                    if (self.mach_alfvén[j,i] > 1) and (self.mach_fast[j,i] < 1) and (self.mach_alfvén[j,i+1] < 1) and (self.mach_slow[j,i+1] > 1):
                        self.inter_shock_ax2.append(self.axial_grid[i])
                        self.inter_shock_ra2.append(self.radial_grid[j])
                    # parallel shocks
                    if (self.mach_alfvén[j,i] > 1) and (self.mach_fast[j,i] < 1) and (self.mach_alfvén[j+1,i] < 1) and (self.mach_slow[j+1,i] > 1):
                        self.inter_shock_ax2.append(self.axial_grid[i])
                        self.inter_shock_ra2.append(self.radial_grid[j])
                    # oblique shocks
                    if (self.mach_alfvén[j,i] > 1) and (self.mach_fast[j,i] < 1) and (self.mach_alfvén[j+1,i+1] < 1) and (self.mach_slow[j+1,i+1] > 1):
                        self.inter_shock_ax2.append(self.axial_grid[i])
                        self.inter_shock_ra2.append(self.radial_grid[j])
                   
                    ### Sub Fast, Super Alfvénic to Sub Slow (2-4)
                    # perpendicular shocks
                    if (self.mach_alfvén[j,i] > 1) and (self.mach_fast[j,i] < 1) and (self.mach_slow[j,i+1] < 1):
                        self.inter_shock_ax3.append(self.axial_grid[i])
                        self.inter_shock_ra3.append(self.radial_grid[j])
                    # parallel shocks
                    if (self.mach_alfvén[j,i] > 1) and (self.mach_fast[j,i] < 1) and (self.mach_slow[j+1,i] < 1):
                        self.inter_shock_ax3.append(self.axial_grid[i])
                        self.inter_shock_ra3.append(self.radial_grid[j])
                    # oblique shocks
                    if (self.mach_alfvén[j,i] > 1) and (self.mach_fast[j,i] < 1) and (self.mach_slow[j+1,i+1] < 1):
                        self.inter_shock_ax3.append(self.axial_grid[i])
                        self.inter_shock_ra3.append(self.radial_grid[j])

                    ### Hydrodynamic (1-4)
                    # perpendicular shocks
                    if (self.mach_fast[j,i] > 1) and (self.mach_slow[j,i+1] < 1):
                        self.inter_shock_ax4.append(self.axial_grid[i])
                        self.inter_shock_ra4.append(self.radial_grid[j])
                    # parallel shocks
                    if (self.mach_fast[j,i] > 1) and (self.mach_slow[j+1,i] < 1):
                        self.inter_shock_ax4.append(self.axial_grid[i])
                        self.inter_shock_ra4.append(self.radial_grid[j])
                    # oblique shocks
                    if (self.mach_fast[j,i] > 1) and (self.mach_slow[j+1,i+1] < 1):
                        self.inter_shock_ax4.append(self.axial_grid[i])
                        self.inter_shock_ra4.append(self.radial_grid[j])

        #### Slow shocks #####
        self.slow_shock_ax = []
        self.slow_shock_ra = []
        for j, row in enumerate(zero_array):
            for i, val in enumerate(row):
                if (i+1 == len(row)) or (j+1 == len(zero_array)):
                    pass
                else:
                    if (self.mach_slow[j,i] > 1) and (self.mach_alfvén[j,i+1] < 1) and (self.mach_slow[j,i+1] < 1):
                        self.slow_shock_ax.append(self.axial_grid[i])
                        self.slow_shock_ra.append(self.radial_grid[j])
                    if (self.mach_slow[j,i] > 1) and (self.mach_alfvén[j+1,i] < 1) and (self.mach_slow[j+1,i] < 1):
                        self.slow_shock_ax.append(self.axial_grid[i])
                        self.slow_shock_ra.append(self.radial_grid[j])
                    if (self.mach_slow[j,i] > 1) and (self.mach_alfvén[j+1,i+1] < 1) and (self.mach_slow[j+1,i+1] < 1):
                        self.slow_shock_ax.append(self.axial_grid[i])
                        self.slow_shock_ra.append(self.radial_grid[j])
        
        ### Check array for unit tests
        self.shocks_list = [
            [self.slow_shock_ax, self.slow_shock_ra],
            [self.fast_shock_ax, self.fast_shock_ra],
            [self.inter_shock_ax1,self.inter_shock_ra1],
            [self.inter_shock_ax2, self.inter_shock_ra2],
            [self.inter_shock_ax3, self.inter_shock_ra3],
            [self.inter_shock_ax4, self.inter_shock_ra4]
        ]

        ### Plots ###
        figureS, axesS = plt.subplots(figsize=(self.image_size[0]*1.25, self.image_size[1]*1.25), dpi=self.dpi*2)
        
        if 'slow' in self.plot_shock:
            axesS.plot(self.slow_shock_ax, self.slow_shock_ra, '+', lw=0.25, color='blue', markersize=3.5, label=f'Slow 3-4 Shocks ({len((self.slow_shock_ax))})', alpha=0.5)
        if 'inter' in self.plot_shock:
            axesS.plot(self.inter_shock_ax1, self.inter_shock_ra1, 's', lw=0.25, color='magenta', markersize=3.5, label=f'Inter 1-3 Shocks ({len((self.inter_shock_ax1))})', alpha=0.5)
            axesS.plot(self.inter_shock_ax2, self.inter_shock_ra2, 'v', lw=0.25, color='green', markersize=3.5, label=f'Inter 2-3 Shocks ({len((self.inter_shock_ax2))})', alpha=0.5)
            axesS.plot(self.inter_shock_ax3, self.inter_shock_ra3, 'H', lw=0.25, color='orange', markersize=3.5, label=f'Inter 2-4 Shocks ({len((self.inter_shock_ax3))})', alpha=0.5)
            axesS.plot(self.inter_shock_ax4, self.inter_shock_ra4, 'D', lw=0.25, color='cyan', markersize=3.5, label=f'Hydro 1-4 Shocks ({len((self.inter_shock_ax4))})', alpha=0.5)
        if 'fast' in self.plot_shock:
            axesS.plot(self.fast_shock_ax, self.fast_shock_ra, '^', lw=0.25, color='red', markersize=3.5, label=f'Fast 1-2 Shocks ({len((self.fast_shock_ax))})', alpha=0.5)

        if '12' in self.plot_shock:
            axesS.plot(self.fast_shock_ax, self.fast_shock_ra, '^', lw=0.25, color='red', markersize=3.5, label=f'Fast 1-2 Shocks ({len((self.fast_shock_ax))})', alpha=0.5)
        
        if '13' in self.plot_shock:
            axesS.plot(self.inter_shock_ax1, self.inter_shock_ra1, 's', lw=0.25, color='magenta', markersize=3.5, label=f'Inter 1-3 Shocks ({len((self.inter_shock_ax1))})', alpha=0.5)
        
        if '14' in self.plot_shock:
            axesS.plot(self.inter_shock_ax4, self.inter_shock_ra4, 'D', lw=0.25, color='cyan', markersize=3.5, label=f'Hydro 1-4 Shocks ({len((self.inter_shock_ax4))})', alpha=0.5)

        if '23' in self.plot_shock:
            axesS.plot(self.inter_shock_ax2, self.inter_shock_ra2, 'v', lw=0.25, color='green', markersize=3.5, label=f'Inter 2-3 Shocks ({len((self.inter_shock_ax2))})', alpha=0.5)

        if '24' in self.plot_shock:
            axesS.plot(self.inter_shock_ax3, self.inter_shock_ra3, 'H', lw=0.25, color='orange', markersize=3.5, label=f'Inter 2-4 Shocks ({len((self.inter_shock_ax3))})', alpha=0.5)

        if '34' in self.plot_shock:
            axesS.plot(self.slow_shock_ax, self.slow_shock_ra, '+', lw=0.25, color='blue', markersize=3.5, label=f'Slow 3-4 Shocks ({len((self.slow_shock_ax))})', alpha=0.5)
        

        axesS.legend()
        axesS.set_xlim(self.xlim[0], self.xlim[1])
        axesS.set_ylim(self.ylim[0], self.ylim[1])
        axesS.set_ylabel(r'Radial distance [$R_{jet}$]')
        axesS.set_xlabel(r'Axial distance [$R_{jet}$]')

        if close==True:
            plt.close()

        if save==True:
            check_dir = f'{self.data_path}shocks'
            chck_subdir = check_dir + f'/{self.plot_shock}'
            if os.path.exists(check_dir) is False:
                os.mkdir(check_dir, 755)
            if os.path.exists(chck_subdir) is False:
                os.mkdir(chck_subdir, 755)
            bbox = matplotlib.transforms.Bbox([[0,0], [12,9]])
            plt.savefig(f'{self.data_path}shocks/{self.plot_shock}/{self.time_step}.jpeg', bbox_inches='tight', pad_inches=0.5)
            plt.close()

    def plot_spacetime(self, data2plot=None, begin=0, end=-1, radial_step=0, log=False, close=False, save=False):
        """
        Space-time diagram plotting method
        """
        ### Deal with mirrored images ###
        check_mirr = self.mirrored
        self.mirrored = False
        
        ### Begin loop through dataset ###
        self.list2plot = []
        time_list = range(len(self.data_list))
        
        print(f'Begin space-time diagram - {time.ctime()}')
        if begin != 0:
            print(f'Started at time-step {begin}!')
        for index, val in enumerate(self.data_list[begin:end]):
            index += begin
            self.calculate_data(index)
            self._data(data2plot=data2plot, log=log, close=close, save=save)
            self.list2plot.append(self.data[radial_step])
            print(f'{index}/{len(self.data_list)-1} files loaded', end='\r')

        print(f'Done! {time.ctime()}')

        
        X, Y = np.meshgrid(self.axial_grid, range(begin, begin+len(self.list2plot)))
        figure, axes = plt.subplots(figsize=(self.image_size[1], self.image_size[1]), dpi=self.dpi)
        pl = axes.contourf(X, Y, self.list2plot, cmap='hot', levels=128)
        
        figure.colorbar(pl, 
            location='right', 
            shrink=0.95, 
            aspect=20,
            pad=0.02, 
            label=f'{self.variable_name}', 
            format='%.2f'
            )
        
        if end == -1:
            end_tick = len(self.data_list)
        else:
            end_tick = end

        ### Set tick spacing ###
        if end_tick - begin >= 500:
            spacing = 100
        elif end_tick - begin >= 100:
            spacing = 50
        elif end_tick - begin >= 50:
            spacing = 10

        if (begin == 0) == False and (end == -1) == False:
            axes.set_yticks(np.arange(begin,end_tick,spacing))
    
        axes.set_xlim(self.xlim[0], self.xlim[1])
        axes.set_ylabel(r'Time [$time-step$]')
        axes.set_xlabel(r'Axial distance [$R_{jet}$]')

        if close==True:
            plt.close()

        if save==True:
            check_dir = f'{self.data_path}space_time'
            chck_subdir = check_dir + f'/{data2plot}'
            if os.path.exists(check_dir) is False:
                os.mkdir(check_dir, 755)
            if os.path.exists(chck_subdir) is False:
                os.mkdir(chck_subdir, 755)
            bbox = matplotlib.transforms.Bbox([[0,0], [12,9]])
            plt.savefig(f'{self.data_path}space_time/{data2plot}/{self.time_step}.jpeg', bbox_inches='tight', pad_inches=0.5)
            plt.close()

        if check_mirr == True:
            self.mirrored = True

    def plot_power(self, save=False, close=False):
        """
        Plots the power curves for the jet
        """
        self.calculate_data(self.time_step)
        total_sys = [np.sum(x) for x in np.transpose(self.total_power_sys)]
        total_jet = [np.sum(x) for x in np.transpose(self.total_power_jet)]
        kinetic_jet = [np.sum(x) for x in np.transpose(self.kinetic_power_jet)]
        enthalpy_jet = [np.sum(x) for x in np.transpose(self.thermal_power_jet)]
        magnetic_jet = [np.sum(x) for x in np.transpose(self.magnetic_power_jet)]

        self.list_power = [
            total_sys,
            total_jet,
            kinetic_jet,
            enthalpy_jet,
            magnetic_jet
            ]

        figure, axes = plt.subplots(figsize=(self.image_size[0], self.image_size[1]), dpi=self.dpi)
        plt1 = axes.plot(self.axial_grid, total_jet, '-', color='blue', ms=2.5, label='Total Jet Power')
        plt2 = axes.plot(self.axial_grid, kinetic_jet, '-.', color='green', ms=2.5, label='Kinetic Jet Power')
        plt3 = axes.plot(self.axial_grid, enthalpy_jet, ':', color='orange', ms=1.5, label='Thermal Jet Power')
        plt4 = axes.plot(self.axial_grid, magnetic_jet, '--', color='red', ms=1.5, label='Magnetic Jet Power')
        axes.set_xlim(self.xlim[0], self.xlim[1])
        axes.set_ylabel(r'Power')
        axes.set_xlabel(r'Axial distance [$R_{jet}$]')
        axes.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize='small', markerscale=2)

        if close==True:
            plt.close()

        if save==True:
            check_dir = f'{self.data_path}power'
            if os.path.exists(check_dir) is False:
                os.mkdir(check_dir, 755)
                chck_subdir = check_dir
            bbox = matplotlib.transforms.Bbox([[0,0], [12,9]])
            plt.savefig(f'{self.data_path}power/{self.time_step}_pwr.jpeg', bbox_inches='tight', pad_inches=0.5)
            plt.close()
        
    def plot_energy(self, save=False, close=False):
        """
        Plots the energy curves for the jet
        """
        self.calculate_data(self.time_step)
        total_sys = np.asarray([np.sum(x) for x in np.transpose(self.total_energy_sys)])
        total_jet = np.asarray([np.sum(x) for x in np.transpose(self.total_energy_jet)])
        kinetic_jet = [np.sum(x) for x in np.transpose(self.kinetic_energy_jet)]
        enthalpy_jet = [np.sum(x) for x in np.transpose(self.thermal_energy_jet)]
        magnetic_jet = [np.sum(x) for x in np.transpose(self.magnetic_energy_jet)]

        self.list_energy = [
            total_sys,
            total_jet,
            kinetic_jet,
            enthalpy_jet,
            magnetic_jet,
        ]

        figure, axes = plt.subplots(figsize=(self.image_size[0], self.image_size[1]), dpi=self.dpi)
        plt1 = axes.plot(self.axial_grid, total_jet, '-', color='blue', ms=2.5, label='Total Jet Energy')
        plt2 = axes.plot(self.axial_grid, kinetic_jet, '-.', color='green', ms=2.5, label='Kinetic Jet Energy')
        plt3 = axes.plot(self.axial_grid, enthalpy_jet, ':', color='orange', ms=1.5, label='Thermal Jet Energy')
        plt4 = axes.plot(self.axial_grid, magnetic_jet, '--', color='red', ms=1.5, label='Magnetic Jet Energy')
        axes.set_xlim(self.xlim[0], self.xlim[1])
        axes.set_ylabel(r'Energy')
        axes.set_xlabel(r'Axial distance [$R_{jet}$]')
        axes.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize='small', markerscale=2)

        if close==True:
            plt.close()

        if save==True:
            check_dir = f'{self.data_path}energy'
            if os.path.exists(check_dir) is False:
                os.mkdir(check_dir, 755)
                chck_subdir = check_dir
            bbox = matplotlib.transforms.Bbox([[0,0], [12,9]])
            plt.savefig(f'{self.data_path}energy/{self.time_step}.jpeg', bbox_inches='tight', pad_inches=0.5)
            plt.close()

    def plot_energy_density(self, save=False, close=False):
        """
        Plots the energy density curves for the jet
        """
        ### Jet should say sys 
        self.calculate_data(self.time_step)
        total_jet = [np.sum(x) for x in np.transpose(self.total_energy_density)]
        kinetic_jet = [np.sum(x) for x in np.transpose(self.kinetic_energy_density)]
        enthalpy_jet = [np.sum(x) for x in np.transpose(self.thermal_energy_density)]
        magnetic_jet = [np.sum(x) for x in np.transpose(self.magnetic_energy_density)]
        
        self.list_E_dens = [
            total_jet,
            kinetic_jet,
            enthalpy_jet,
            magnetic_jet,
        ]

        figure, axes = plt.subplots(figsize=(self.image_size[0], self.image_size[1]), dpi=self.dpi)
        plt1 = axes.plot(self.axial_grid, total_jet, '-', color='blue', ms=2.5, label='Total System Energy Density')
        plt2 = axes.plot(self.axial_grid, kinetic_jet, '-.', color='green', ms=2.5, label='Kinetic System Energy Density')
        plt3 = axes.plot(self.axial_grid, enthalpy_jet, ':', color='orange', ms=1.5, label='Thermal System Energy Density')
        plt4 = axes.plot(self.axial_grid, magnetic_jet, '--', color='red', ms=1.5, label='Magnetic System Energy Density')
        axes.set_xlim(self.xlim[0], self.xlim[1])
        axes.set_ylabel(r'Energy density')
        axes.set_xlabel(r'Axial distance [$R_{jet}$]')
        axes.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize='small', markerscale=2)

        if close==True:
            plt.close()

        if save==True:
            check_dir = f'{self.data_path}energy_density'
            if os.path.exists(check_dir) is False:
                os.mkdir(check_dir, 755)
                chck_subdir = check_dir
            bbox = matplotlib.transforms.Bbox([[0,0], [12,9]])
            plt.savefig(f'{self.data_path}energy_density/{self.time_step}.jpeg', bbox_inches='tight', pad_inches=0.5)
            plt.close()

    def plot_fieldlines(self, save=False, close=False, levels=128, min_bxs=None, max_bxs=None, min_bx2=None, max_bx2=None):
        """
        Plots a vector plot of the magnetic field lines in the axial-radial plane,
        while plots the true magnitude of the magnetic field accounted in all 3 directions.
        """
        b_mag = self.magnetic_field_magnitude
        cmp='jet'
        scmap = 'seismic'
        density=4

        subgrid_x_low = float(self.ini_content['[Grid]']['X3-grid']['Subgrids Data'][0][0])
        subgrid_y_low = float(self.ini_content['[Grid]']['X1-grid']['Subgrids Data'][0][0])
        subgrid_x = float(self.ini_content['[Grid]']['X3-grid']['Subgrids Data'][1][0])
        subgrid_y = float(self.ini_content['[Grid]']['X1-grid']['Subgrids Data'][1][0])
        subgrid_x_res = int(self.ini_content['[Grid]']['X3-grid']['Subgrids Data'][0][1])
        subgrid_y_res = int(self.ini_content['[Grid]']['X1-grid']['Subgrids Data'][0][1])

        subgrid_y_start = 0
        subgrid_y_end = subgrid_y_res

        x1_comp = np.asarray(self.bx1)[subgrid_y_start:subgrid_y_end,:subgrid_x_res]
        x2_comp = np.asarray(self.bx2)[subgrid_y_start:subgrid_y_end,:subgrid_x_res]
        x3_comp = np.asarray(self.bx3)[subgrid_y_start:subgrid_y_end,:subgrid_x_res]
        magnitude = np.asarray(b_mag)[subgrid_y_start:subgrid_y_end,:subgrid_x_res]

        X, Y = np.meshgrid(self.axial_grid[:subgrid_x_res],
                            self.radial_grid[subgrid_y_start:subgrid_y_end])

        X2, Y2 = np.meshgrid(np.linspace(subgrid_x_low, subgrid_x, subgrid_x_res), 
                                 np.linspace(subgrid_y_low, subgrid_y, subgrid_y_res))

        ### Colourbar scaling

        if min_bxs == None:
            min_bxs = 0
        if max_bxs == None:
            max_bxs = np.max(magnitude)
        if min_bx2 == None:
            min_bx2 = np.min(x2_comp)
        if max_bxs == None:
            max_bx2 = np.max(x2_comp)

        figure, axes = plt.subplots(1,1,figsize=(self.image_size[0], self.image_size[0]),dpi=self.dpi)
        plt.tight_layout()
        norm = matplotlib.colors.Normalize(vmin=min_bxs, vmax=max_bxs)
        linenorm = matplotlib.colors.Normalize(vmin=min_bx2, vmax=max_bx2)
        
        axes.contourf(
                    X,
                    Y,
                    magnitude,
                    cmap=cmp,
                    alpha=0.95,
                    levels=levels)
        
        axes.streamplot(X2, 
                        Y2,
                        x3_comp,
                        x1_comp,
                        density=density,
                        color=x2_comp,
                        cmap=scmap,
                        integration_direction='both',
                        maxlength=20,
                        arrowsize=1.25,
                        arrowstyle='->',
                        linewidth=0.75,
                        norm=linenorm,
                        )
        
        plt.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmp), ax=axes, format='%.2f', label='Magnetic Field Strength',  location='bottom', pad=0.01), 
        plt.colorbar(matplotlib.cm.ScalarMappable(norm=linenorm, cmap=scmap), ax=axes, format='%.2f', label='Magnetic Field in direction x2',  location='bottom', pad=0.05)
        
        plt.xlim(self.xlim[0], self.xlim[1])
        
        if self.mirrored == False:
            plt.ylim(self.ylim[0], self.ylim[1])
        else:
            plt.ylim(-self.ylim[1], self.ylim[1])

        if close==True:
            plt.close()

        if save==True:
            check_dir = f'{self.data_path}field_line'
            if os.path.exists(check_dir) is False:
                os.mkdir(check_dir)
            bbox = matplotlib.transforms.Bbox([[0,0], [12,9]])
            plt.savefig(f'{self.data_path}field_line/{self.time_step}.jpeg', bbox_inches='tight', pad_inches=0.5)
            plt.close()

        self.streamline_check = magnitude

    def plot_azimuthal_energy(self):
        """
        Plots the Kinetic and Magnetic energies as a function of axial distance to compare for stability analysis
        """
        KE_int = [np.sum(b) for b in np.transpose(self.kinetic_energy_jet_x2)]
        BE_int = [np.sum(v) for v in np.transpose(self.magnetic_energy_jet_x2)]

        fig, ax = plt.subplots(figsize=(6,6), dpi=500)
        ax.plot(self.axial_grid, BE_int, 'b--', ms=3, lw=1.5, label='Magnetic')
        ax.plot(self.axial_grid, KE_int, 'g-.', ms=3, lw=1.5, label='Kinetic')
        ax.set_ylabel(r'Energy in x2 direction')
        ax.set_xlabel(r'Axial distance [$R_{jet}$]')
        ax.set_xlim(self.xlim)
        ### setup ylim within range ###
        filtr = [i for i, x in enumerate(self.axial_grid) if x <= self.xlim[1]]
        max_ke = KE_int[:int(max(filtr))]
        max_me = BE_int[:int(max(filtr))]
        max_e = np.max([max_ke, max_me])
        ax.set_ylim(0, max_e)
        ax.legend()

        self.azimuthal_energy_plot_check = type(fig)


        
    def oblique_shocks(self, min=0, max=10000):
        """
        Use the Ranking-Hugoniot relation for ideal MHD to find oblique shocks
        """
        shock_array = np.zeros_like(self.mach_slow)
        magneto_sonic_mach_mag = np.sqrt(self.mach_fast**2 + self.mach_alfvén**2 + self.mach_slow**2)
        
        RHx1 = np.zeros_like(magneto_sonic_mach_mag) 
        RHx2 = np.zeros_like(magneto_sonic_mach_mag) 
        RHy1 = np.zeros_like(magneto_sonic_mach_mag) 
        RHy2 = np.zeros_like(magneto_sonic_mach_mag) 
        RHxy1 = np.zeros_like(magneto_sonic_mach_mag) 
        RHxy2 = np.zeros_like(magneto_sonic_mach_mag) 

        RHx1[:, 0:-1], RHx2[:, 0:-1] = RH_MHD(
            self.gamma,
            self.beta[:, 0:-1],
            magneto_sonic_mach_mag[:, 0:-1],
            self.prs[:, 0:-1],
            self.prs[:, 1:],
            )
        
        RHy1[0:-1, :], RHy2[0:-1, :] = RH_MHD(
            self.gamma,
            self.beta[0:-1, :],
            magneto_sonic_mach_mag[0:-1, :],
            self.prs[0:-1, :],
            self.prs[1:, :],
            )
            
        RHxy1[0:-1, 0:-1], RHxy2[0:-1, 0:-1] = RH_MHD(
            self.gamma,
            self.beta[0:-1, 0:-1],
            magneto_sonic_mach_mag[0:-1, 0:-1],
            self.prs[0:-1, 0:-1],
            self.prs[1:, 1:],
            )
        
        ma1 = np.ma.masked_greater(np.ma.masked_less(RHx2, min), max)
        ma2 = np.ma.masked_greater(np.ma.masked_less(RHy2, min), max)
        ma3 = np.ma.masked_greater(np.ma.masked_less(RHxy2, min), max)

        ma4 = np.ma.masked_greater(np.ma.masked_less(RHx1, min), max)
        ma5 = np.ma.masked_greater(np.ma.masked_less(RHy1, min), max)
        ma6 = np.ma.masked_greater(np.ma.masked_less(RHxy1, min), max)

        figure, axes = plt.subplots(figsize=self.image_size, dpi=self.dpi)
        divider = mal(axes)
        cax = divider.append_axes('right',size='5%',pad=0.25)
        pl = axes.contourf(self.axial_grid, self.radial_grid, ma4, cmap=self.cmap, levels=16, alpha=0.35)
        pl = axes.contourf(self.axial_grid, self.radial_grid, ma1, cmap=self.cmap, levels=16, alpha=0.35)
        pl = axes.contourf(self.axial_grid, self.radial_grid, ma5, cmap=self.cmap, levels=16, alpha=0.35)
        pl = axes.contourf(self.axial_grid, self.radial_grid, ma2, cmap=self.cmap, levels=16, alpha=0.35)
        pl = axes.contourf(self.axial_grid, self.radial_grid, ma6, cmap=self.cmap, levels=16, alpha=0.35)
        pl = axes.contourf(self.axial_grid, self.radial_grid, ma3, cmap=self.cmap, levels=16, alpha=0.35)
        plt.colorbar(
            pl,
            cax,
            )
        axes.set_facecolor('0.85')
        axes.set_xlim(self.xlim[0], self.xlim[1])
        axes.set_ylim(self.ylim[0], self.ylim[1])
        axes.set_ylabel(r'Radial distance [$R_{jet}$]')
        axes.set_xlabel(r'Axial distance [$R_{jet}$]')

        self.oblique_shocks_check = type(figure)
