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

# # Pryngles module: stars

from pryngles import *

# ## External modules

# ## Star Class

class StarDefaults(object):
    """
    These are the default attributes for bodies of the kind 'Star'.
    
    DEVELOPER:
        You may add new attributes as the model gets more complex.
        Please document properly each attribute.
        
    orbit:
    
        These attributes should be compatible with rebound.
    
        m: float [rebound mass units], default = 1
            Mass of the body.  If m = 0 the body does not produce gravitation.
            
    physics:
    
        radius: float [rebound length units], default = 1
            Radius of the body.
            
        prot: float [rebound time units], default = 1
            Period of rotation
            
    optics:
    
        limb_coeffs: list [adimensional], default = []
            List of limb darkening fit coefficients.
            
        nspangles: int, default = 1000
            Number of spangles on which the object will be discretized.
    """
    orbit=dict(m=1)
    
    physics=dict(radius=1,prot=1)

    optics=dict(limb_coeffs=[],
                nspangles=1000)

BODY_KINDS+=["Star"]
class Star(Body):
    """Class star.
    
    See Body class documentation.
    
    Additional public attributes:
    
        physics.wrot: float
            Rotational angular velocity
    
    Override methods:
    
        update_body(**pars):
            This method compute additional attributes like (see above):
            
                physics.wrot
    """
    def __init__(self,
                 primary=None,
                 orbit=StarDefaults.orbit,
                 physics=StarDefaults.physics,
                 optics=StarDefaults.optics
                ):
        
        
        #Instantiate object with basic properties
        Body.__init__(self,StarDefaults,"Star",primary,orbit,physics,optics)

        #Check primary
        if self.primary is not None:
            if self.primary.kind=="Planet":
                raise ValueError(f"Planet cannot be the primary of a Star")
            #self.primary._update_childs(self)
            #self._update_parent(self.primary)
                
        #Update properties
        self.update_body(**self.__dict__)
        
    def update_body(self,**pars):
        Body.update_body(self,**pars)
        
        #Here place the commands to update this kind of body
        self.physics.wrot=2*np.pi/self.physics.prot


