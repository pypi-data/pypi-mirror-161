#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 10:19:30 2022

@author: uzair
"""

import numpy as np

def centerOfMass(masses, pos):
    '''Calculate the center of mass of a group of particles'''
    com = np.sum(pos * masses.reshape(len(masses), 1), axis=0) / np.sum(masses)
    return com

def elastic_collision(p1_pos, p1_vel, p1_mass, p2_pos, p2_vel, p2_mass):
    '''Calculate the new velocities of two colliding particles in an elastic collision
    Assumes that the two given particles are already colliding (doesn't check for collision)
                                                                
    Returns (p1_velocity, p2_velocity)'''
    
    # TODO
    # Figure out where this comes from:
    # https://physics.stackexchange.com/questions/681396/elastic-collision-3d-eqaution
    
    diff = p2_pos - p1_pos
    
    if (diff == 0).all():
        return p1_vel, p2_vel
    
    dist = np.sqrt(np.sum(diff ** 2))
    normal = (p1_pos - p2_pos) / dist
    
    eff_mass = 1 / (1/p1_mass + 1/p2_mass)
    impact_speed = np.dot(normal, (p1_vel - p2_vel))
    impulse_magnitude = 2 * eff_mass * impact_speed
    
    impulse = normal * impulse_magnitude
    return p1_vel - impulse / p1_mass, p2_vel + impulse / p2_mass


def dist(vector1, vector2):
    return np.sqrt(np.sum((vector1 - vector2) ** 2))