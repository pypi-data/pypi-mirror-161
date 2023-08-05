##################################################################
#                                                                #
#.#####...#####...##..##..##..##...####...##......######...####..#
#.##..##..##..##...####...###.##..##......##......##......##.....#
#.#####...#####.....##....##.###..##.###..##......####.....####..#
#.##......##..##....##....##..##..##..##..##......##..........##.#
#.##......##..##....##....##..##...####...######..######...####..#
#................................................................#
#                                                                #
# PlanetaRY spanGLES                                             #
# The bright-side of the light-curve of (ringed) exoplanets      #
#                                                                #
##################################################################
# Jorge I. Zuluaga, Mario Sucerquia, Jaime A. Alvarado (C) 2022  #
##################################################################
#!/usr/bin/env python
# coding: utf-8

# # Pryngles module: Constants

# This module contains the definitions of useful constants.

# ## Pryngles

from pryngles import *

# ## Constants class

class Consts(object):pass
    
#Mathematical constants
import numpy as np
Consts.rad=180/np.pi
Consts.deg=1/Consts.rad
Consts.ppm=1e6 #parts per million
Consts.ppb=1e9 #parts per billion

#Physical constants
from rebound import units
GSI=units.convert_G(["m","s","kg"]) # G constant in SI units
for const in "times","lengths","masses":
    values=eval(f"units.{const}_SI.copy()")
    for key in values:
        exec(f"Consts.{key}=values[key]")

#Size of reference objects
Consts.rearth=6378.137e3 #m, volumetric mean radius
Consts.rsun=695700e3 #m, nominal solar radius
Consts.rjupiter=71492e3 #m, equatorial radius
Consts.rsaturn=60268e3 #m


