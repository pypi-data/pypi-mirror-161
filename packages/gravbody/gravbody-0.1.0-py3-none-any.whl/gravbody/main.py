#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 11:45:59 2022

@author: uzair
"""

# Quick Testing Instructions
#
# Run: `python3 main.py S sample_data.txt [output_dir] 100 -t 0.005`
# This creates an orbital simulation
#
# Run: `python3 main.py V [simulation_dir] -e -t 50`
# This visualizes the simulation with an energy plot as well
# Watch the scale of the energy plot: it's zoomed in so it seems like it varies more than it does

import gravbody.nbody as nbody
import gravbody.nbody_view as nbody_view
import argparse

def main():
    parser = argparse.ArgumentParser(description='An N-Body Simulator')

    subparsers = parser.add_subparsers(dest="mode", help="Mode: [S]imulate or [V]iew saved simulation")

    sim = subparsers.add_parser("S")
    view = subparsers.add_parser("V")

    sim.add_argument("input_file", help="file containing initial conditions(pos, vel, mass) of all particles")
    sim.add_argument("output_dir", help="folder to store simulation output")
    sim.add_argument("time", help="the length of time that will be simulated", type=float)
    sim.add_argument("-t", "--time_step", help="the amount of time in between each simulation update", type=float)
    sim.add_argument("-b", "--barnes_hut", 
                    help="Use the barnes-hut algorithm to speed up execution for a large # of particles",
                    action="store_true")
    sim.add_argument("-c", "--collide_radius", help="Allow particles to collide elastically with a specified radius",
                    type=float)
    sim.add_argument("-s", "--save_every", help="Only save 1 frame per n frames generated",
                    type=int, default=1)
    sim.add_argument("-G", "--G_Constant", help="Set value of gravitational constant",
                    type=float, default=1)
    sim.add_argument("-f", "--force_softening", help="Aritifically increase distance to avoid unexpected behaviour near collisions",
                    type=float, default=0)

    view.add_argument("input_dir", help="directory containing simulation data")
    view.add_argument("-s", "--size", help="Set size of display", default=100, type=float)
    view.add_argument("-d", "--use_2d", help="display particles in a 2d projection instead of 3d",
                    action="store_true")
    view.add_argument("-r", "--relative", help="keep view relative to center of mass",
                    action="store_true")
    view.add_argument("-e", "--energy", help="plot the energy of the system",
                    action="store_true")
    view.add_argument("-t", "--time_scale", help="speed up visualization by a given factor",
                    default=1, type=int)
    view.add_argument("-o", "--output_file", help="store the output visualization in a video file")

    args = parser.parse_args()
    try:
        if args.mode == "S":
            t_step = args.time_step if args.time_step is not None else args.time / 1000
            numFrames = int(args.time / t_step / args.save_every)
            
            colliding = args.collide_radius is not None
            
            sim = nbody.NBody.FromFile(args.input_file, barnes_hut=args.barnes_hut,
                                    use_collisions=colliding, particle_radius=args.collide_radius,
                                    G=args.G_Constant, softening=args.force_softening)
            sim.save(t_step, args.output_dir, numFrames, saveEvery=args.save_every)

        elif args.mode == "V":
            view = nbody_view.NBodyView(args.input_dir, args.size, not args.use_2d,
                                        args.relative, args.time_scale, args.energy,
                                        args.output_file)
            view.display()

        else:
            parser.print_help()
    
    except AttributeError:
        parser.print_help()