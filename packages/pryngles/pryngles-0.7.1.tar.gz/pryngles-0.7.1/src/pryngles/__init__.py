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
##################################################
# PRELIMINARY INIT COMMANDS
##################################################
#--END OF TEMPLATE--#

#!/usr/bin/env python
# coding: utf-8

# # PlanetaRY spanGLES: the bright-side of the light-curve

# This is the initialization file of the `Pryngles` package.

# ## Warnings

import unittest
import warnings
warnings.filterwarnings('ignore')

# ## Jupyter compatibilty

"""
The purpose of the get_ipython class is to provide some response in the python 
script resulting from the conversion of this notebook.

If you want to add another IPyhton function resulting from a magic command to the class, 
please verify in the resulting python script the corresponding IPython command.

For instance, the magic "%matplotlib nbagg" is converted into:

    get_ipython().magic('matplotlib nbagg',globals())

So, the routinge "magic" should be add to the get_ipython() class.        
"""
from IPython.display import HTML, Image
import IPython.core.autocall as autocall
from IPython import get_ipython
import sys

try:
    cfg=get_ipython().config
except AttributeError:
    def Image(url="",filename="",f=""):
        pass
    class get_ipython(object):
        def run_line_magic(self,*args):
            if "timeit" in args[0]:
                command=" ".join(args)
                replaceTimeIt(command)
        def run_cell_magic(self,x,y,z):
            pass
        def magic(self,command,scope=globals()):
            import re
            if "timeit" in command:
                replaceTimeIt(command)

IN_JUPYTER='ipykernel' in sys.modules
get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

# ## Global variables
# 
# All global constants in Pryngles have a capital name and a lowercase version in the class util.

import os
#Root directory
try:
    FILE=__file__
    ROOTDIR=os.path.abspath(os.path.dirname(FILE))
except:
    import IPython
    FILE=""
    ROOTDIR=os.path.abspath('')
    
BODY_KINDS=[]

# ## Util Class

Misc_doc="""
Miscelaneous routines.

This is a set of util routines intended for a diversity of purposes.

Routines included:

    get_data(file)
""";

class Misc(object):
    def get_data(path):
        """
        Get the full path of the `datafile` which is one of the datafiles provided with the package.
        
        Parameters:
            datafile: Name of the data file, string.
            
        Return:
            Full path to package datafile in the python environment.
            
        """
        return os.path.join(ROOTDIR,'data',path);
Misc.__doc__=Misc_doc

# ## PrynglesCommon
# 
# Many of the classes in Pryngles inherite methods of this common class

class PrynglesCommon(object):
    def __str__(self):
        return str(self.__dict__)    

# ## Pryngles modules

from pryngles.version import *
from pryngles.consts import *
from pryngles.props import *
from pryngles.body import *
from pryngles.star import *
from pryngles.planet import *
from pryngles.ring import *
from pryngles.observer import *
from pryngles.system import *
from pryngles.spangler import *
from pryngles.legacy import *


