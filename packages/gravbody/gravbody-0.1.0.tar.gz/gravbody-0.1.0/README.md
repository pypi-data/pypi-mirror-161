# GravBody

## Abstract

One of the areas in which our mathematical analytical tools are lacking is in the prediction of gravitational interactions between three or more masses. Although a closed form solution for the motion caused by gravitational interactions exists for two-body systems and certain initial conditions of three body systems, there doesn't exist a general solution for any number of interacting bodies. N-body simulations are used to approximate the motion of multiple gravitating bodies, but maintaining accuracy over long intervals of time is difficult due to the high level of dependence of each particle's motion on every other particles' motions. GravBody is a python package that aims to efficiently and accurately simulate the motion of particles affected by gravitational forces while also being easy to use and accessible. 

## Background Information

The n-body problem is the issue of accurately predicting the motion of multiple objects which are all being affected by each object's gravitational forces. This has many applications in astronomical research, as predicting the motion of planets, stars, and even large asteroids can be integral for any space-related research. However, effeciently and accurately predicting the motion of these objects has proven to be a mathematical challenge. Closed-form solutions have been argued to be impossible, since for every n-body system, there exist more unknown variables than equations to describe them [[1]](#1). Because of this, we are forced to find methods to approximate the motion of these bodies.

One way to simulate gravitational interactions is to calculate the gravitational forces exerted by all bodies over very small time steps. Decreasing the amount of time in between simulation updates results in a higher accuracy, but takes longer to generate. For a large number of particles, measuring all the interacting forces between all of the particles is expensive. This is where further approximations, such as the Barnes-Hut method, come in. The Barnes-Hut method uses a quad tree that recursively divides particles up into their own cells, allowing nearby particles to be grouped together. Clusters of particles far away are approximated as a single mass at their center, allowing certain force calculations to be skipped entirely [[2]](#2).  This allows for more efficient simulations at the cost of accuracy. 

But how do we quantify this inaccuracy? Since there aren't always known solutions to the motion of interacting particles, the simplest way to verify results is to measure the total energy of the system over time. Realistically, the energy should remain constant as long as there are no external forces acting on any particle. Although a constant energy doesn't guarantee that the results are correct, it can still be used as a way to check that the results of a simulation are reasonable.

This python package was created with the purpose of being an easy-to-use tool to simulate gravitational interactions. It contains a variety of features, including the ability to use the Barnes-Hut approximation. It has a built-in CLI that also allows one to visualize the evolution of a gravitational system with an energy graph to verify the results, and can be easily imported and combined with another python project. 

## Algorithm Comparison

The figure below shows the time it takes to generate a single frame using both the barnes-hut tree and naive simulation methods. For a small number of particles, the barnes-hut method is slower due to the initial time it takes to create the quadtree. But, with a larger number of particles (more than ~4000 based on this graph), the barnes-hut tree generates frames much faster due to the fact that it is performing less calculations.

<p align="center">
    <img
    src="plots/bh_v_naive_frame_gen_time.png"
    alt="Barnes-Hut vs Naive Efficiency">
</p>

This improved efficiency comes with a cost to accuracy. The two plots below show the total energy of a simulation of 100 particles in an orbit over 20 time units, with a step size of 0.1 time units. In this case, the naive simulation's energy varies by about 0.03 energy units while the barnes-hut simulation varies by about 4 energy units. Both variations are relatively small, but it's clear that the naive simulation is more accurate.


<p align="center">
  <b>Naive Energy Conservation</b>
</p>
<p align="center">
  <img
  src="plots/naive_energy_100particles_0.01step.png"
  alt="Naive Energy Conservation Plot">
</p>

<br>
<br>


<p align="center">
  <b>Barnes-Hut Energy Conservation</b>
</p>
<p align="center">
  <img
  src="plots/bh_energy_100particles_0.01step.png"
  alt="Barnes-Hut Energy Conservation Plot">
</p>

## Features

- Naive but accurate O(n^2) approach to calculating forces on all particles and updating position
- Barnes-Hut approximation O(n log n) which handles larger scales more efficiently at the cost of accuracy
- Optional elastic collisions between particles
- 2D/3D visualization tool that also contains an energy plot to evaluate accuracy
- Command Line Interface


## Installation

### Pip

Installing this package through pip is fairly simple:

```bash
pip install gravbody
```

### From source

First clone this repo:

```bash
$ git clone https://codeberg.org/uzairn/gravbody.git
```

Then navigate to the top directory of the repo and build the package:

```bash
$ pip install build
$ python3 -m build
```

Now install the package using pip, replacing [version] with the current version of the package:

```bash 
$ pip install dist/gravbody-[version].tar.gz
```

## Usage

The usage for the command line tool can be accessed as shown: 
```bash
$ gravbody --help
```

There are two modes for this tool: simulation and visualization. 

#### Simulation

The simulation mode generates the files storing data on how the system evolves after a given set of initial conditions.
To see all of the available simulation options, run:
```bash
$ gravbody S --help
```
The initial conditions file should be formatted in the following form:
```text
[pos x] [pos y] [pos z] [velocity x] [velocity y] [velocity z] [mass]
[pos x] [pos y] [pos z] [velocity x] [velocity y] [velocity z] [mass]
...
[pos x] [pos y] [pos z] [velocity x] [velocity y] [velocity z] [mass]
```
Each row contains the initial conditions of a single particle, which are space separated. 
There are sample initial conditions given in the SAMPLES folder.

The output of a simulation will be placed in a specified directory in the format of one frame per file.

#### Visualization

The visualization mode allows you to view the results of a simulation.
To see all of the available visualization options, run:

```bash
$ gravbody V --help
```

## Sources
<a id="1">[1]</a>
M. Burdorf, “Analyzing Cosmological Evolution through n-body Simulation of Dark and Luminous Matter using ChaNGa,” thesis, 2021. 

<a id="2">[2]</a>
J. Barnes and P. Hut, “A hierarchical o(n log n) force-calculation algorithm,” Nature, vol. 324, no. 6096, pp. 446–449, Dec. 1986. 

<a id="3">[3]</a>
P. Mocz, “Create Your Own N-body Simulation (With Python),” Medium, Sep. 2022.



