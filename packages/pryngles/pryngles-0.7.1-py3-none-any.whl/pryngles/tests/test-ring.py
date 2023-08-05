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
import unittest
from pryngles import *
class Test(unittest.TestCase):
    def test_planet(self):
        S=Star(physics=dict(radius=3.0))

        #Check exception: primary is mandatory for planets
        self.assertRaises(ValueError,lambda:Ring())

        R=Ring(primary=S)
        
        print(R.physics)
        print(R.hash)
        
        print(R.M_equ2ecl)
        print(R.M_ecl2equ)
        
        #Check derived properties
        print(R.M_equ2ecl)
        print(R.M_ecl2equ)
        print(R.nr_ecl)
        print(R.nr_equ)
        """
        self.assertEqual(np.isclose([P.physics.wrot],
                                    [2*np.pi/PlanetDefaults.physics["prot"]],
                                    rtol=1e-7),
                         [True]*1)
        """
        
        R.update_body(physics=dict(fe=3))
        print(R.physics)
        
        #Check exception: primary could not be different from None or Body
        self.assertRaises(AssertionError,lambda:Planet(primary="Nada"))
        

if __name__=="__main__":
        unittest.main(argv=['first-arg-is-ignored'],exit=False)
