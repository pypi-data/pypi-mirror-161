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

# # Pryngles module

from pryngles import *

# ## External modules

# ## Planet class

class PlanetDefaults(object):
    """
    These are the default attributes for bodies of the kind 'Planet'.
    
    DEVELOPER:
        You may add new attributes as the model gets more complex.
        Please document properly each attribute.
        
    orbit:
    
        These attributes should be compatible with rebound.
    
        m: float [rebound mass units], default = 1
            Mass of the body.  If m = 0 the body does not produce gravitation.
            
        a: float [rebound length units], default = 1.0
            Semi major axis of the orbit with respect to primary.
            
        e: float [adimentional], default = 0.0
            Eccentricity of the orbit with respect to primary.
            
    physics:
    
        radius: float [rebound length units], default = 1
            Radius of the body.
            
        prot: float [rebound time units], default = 1
            Period of rotation
            
    optics:
    
        nspangles: int, default = 1000
            Number of spangles on which the object will be discretized.
    """

    orbit=dict(m=1.0,a=1.0,e=0.0)
    
    physics=dict(radius=1.0,prot=1.0)
    
    optics=dict(nspangles=1000)

BODY_KINDS+=["Planet"]

class Planet(Body):
    """Class Planet.
    
    See Body class documentation.
    
    Additional public attributes:
    
        physics.wrot: float
            Rotational angular velocity
    
    Override methods:
    
        update_body(**pars):
            This method compute additional attributes like (see above).
    """
    def __init__(self,
                 primary=None,
                 orbit=PlanetDefaults.orbit,
                 physics=PlanetDefaults.physics,
                 optics=PlanetDefaults.optics
                ):
        
        
        #Instantiate object with basic properties
        Body.__init__(self,PlanetDefaults,"Planet",primary,orbit,physics,optics)
        
        #Check primary
        if self.primary is None:
            raise ValueError(f"Primary not provided and it is mandatory for {self.kind}.")
        #self.primary=primary
        #self.primary._update_childs(self)
        #self._update_parent(self.primary)
        
        #Update properties
        self.update_body(**self.__dict__)
        
    def update_body(self,**pars):
        Body.update_body(self,**pars)
        
        #Here place the commands to update this kind of body
        self.physics.wrot=2*np.pi/self.physics.prot


