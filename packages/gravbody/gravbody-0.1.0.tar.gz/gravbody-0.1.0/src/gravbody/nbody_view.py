#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 10:17:07 2022

@author: uzair
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib import ticker
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sys


class NBodyView:
    def __init__(self, path, size, three_dimensional=True, relativeToCenterOfMass=True,
                 timeScale=1, plot_energy=False, output_file=None):
        
        self.path = path
        self.size = size
        self.three_dimensional = three_dimensional
        self.relativeToCenterOfMass = relativeToCenterOfMass
        self.timeScale = timeScale
        self.plot_energy = plot_energy
        self.output_file = output_file
        self.energyX = np.array([])
        self.energyY = np.array([])
        self.energyAx = None
        
        self.anim = None
        self.end_anim = False
        self.old_com = np.zeros(3)
        self.scatter = None
        self.energy_scatter = None
        self.t = None
        self.masses = None
        
        self.load_anim()

    def update_plot(self, frame_number):
        try:
            data = np.load(self.path + '/' + str(frame_number * self.timeScale) + '.npy')
            pos = data[:, :3]
            vel = data[:, 3:6]
            com = np.sum(pos * self.masses.reshape(len(self.masses), 1), axis=0) / np.sum(self.masses)
            com_vel = (com - self.old_com) / (self.t * self.timeScale)
            self.old_com = com
            
            if self.plot_energy and frame_number != 0:
                energy = self.calc_energy(pos, vel)
                self.energyX = np.append(self.energyX, [frame_number * self.t * self.timeScale])
                self.energyY = np.append(self.energyY, [energy])
                plt.cla()
                self.energyAx.set_title("Energy Plot")
                self.energyAx.set_xlabel("Time")
                self.energyAx.set_ylabel("Energy")
                self.energyAx.scatter(self.energyX, self.energyY, 9, color='blue')
            
            if self.relativeToCenterOfMass:
                pos -= com
            
            if self.three_dimensional:
                self.scatter._offsets3d = pos.T
            else:
                self.scatter.set_offsets(pos[:, :2])
        except FileNotFoundError:
            self.end_anim = True
            # self.anim.event_source.stop()
    
    def frames_gen(self):
        i = 0
        while not self.end_anim:
            yield i
            i += 1
                
    def display(self):
        fig = plt.figure(figsize=(7,7))
        ax = None
        
        if self.plot_energy:
            grid = plt.GridSpec(3, 1, wspace=0.0, hspace=0.5)
            if self.three_dimensional:
                ax = plt.subplot(grid[0:2,0],
                                 xlim=(-self.size, self.size),
                                 ylim=(-self.size, self.size),
                                 zlim=(-self.size, self.size),
                                 projection='3d')
            else:
                ax = plt.subplot(grid[0:2,0],
                                 xlim=(-self.size, self.size),
                                 ylim=(-self.size, self.size))

            self.energyAx = plt.subplot(grid[2:,0])
            self.energyAx.set_title("Total Energy Over Time")
            self.energyAx.set_xlabel("Time")
            self.energyAx.set_ylabel("Energy")
            axis_format = ticker.FormatStrFormatter("%.6f")
            self.energyAx.yaxis.set_major_formatter(axis_format)
        else:
            if self.three_dimensional:
                ax = plt.axes(xlim=(-self.size, self.size),
                              ylim=(-self.size, self.size),
                              zlim=(-self.size, self.size),
                              projection='3d')
            else:
                ax = plt.axes(xlim=(-self.size, self.size),
                              ylim=(-self.size, self.size))
        
        self.scatter = ax.scatter(np.array([]), np.array([]))
        self.anim = FuncAnimation(fig, self.update_plot, frames=self.frames_gen, interval=0.0001, save_count=sys.maxsize)
        
        if self.output_file is None:
            plt.show()
        else:
            w = FFMpegWriter(fps=30)
            self.anim.save(self.output_file, writer=w)
        
    def calc_energy(self, pos, vel):
        KE = 0
        PE = 0
        for i in range(self.masses.shape[0]):
            KE += 0.5 * self.masses[i] * np.sum((vel[i]) ** 2)
            for j in range(self.masses.shape[0]):
                if i != j:
                    PE -= self.masses[i] * self.masses[j] / np.sqrt(np.sum((pos[i] - pos[j]) ** 2))
        # print(KE, PE, end="\t")
        PE /= 2
        
        return KE + PE
        
    def load_anim(self):
        arr = np.load(self.path + '/data.npy')
        self.t = arr[0]
        self.masses = arr[1:]
    
    def isEnergyConserved(self, acceptableError=0.01):
        minEnergy = None
        maxEnergy = None
        
        for i in range(0, 5000):
            data = np.load(self.path + '/' + str(i) + '.npy')
            pos = data[:, :3]
            
            e = self.calc_energy(pos, data[:, 3:6])
            if minEnergy == None or e < minEnergy:
                minEnergy = e
            if maxEnergy == None or e > maxEnergy:
                maxEnergy = e
        
        variability = (maxEnergy - minEnergy) / minEnergy
        
        return variability < acceptableError

if __name__ == '__main__':
    abc = NBodyView('../../animations/3_body_same_mass/0000', 200, plot_energy=True, timeScale=10)
    abc.display()
    
    # for i in range(1075, 1076):
    #     abc = NBodyView('../../animations/3_body_same_mass/%04d' % i, 40)
    #     if i % 50 == 0:
    #         print('-')
    #     if (not abc.isEnergyConserved()):
    #         print(i)
            