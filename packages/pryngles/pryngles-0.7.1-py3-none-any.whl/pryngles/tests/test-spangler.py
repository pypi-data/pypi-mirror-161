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
    def test_sample(self):

        #Generate rings
        S=Spangler(500,seed=10)
        S.gen_ring([[0.0,0.3],[0.5,2*0.05]])
        S.plot()
        S.plot(spangled=dict(color='r'))
        S.ax.set_title(f"N = {S.N}, dmed = {S.dmed:.4f}, deff = {S.deff:.4f}",fontsize=10)
        S.fig.tight_layout()

        #Generate sphere
        S=Spangler(100,seed=10)
        S.gen_sphere()
        S.purge_sample()
        S.plot()
        S.plot(spangled=dict(color='r'))
        S.ax.set_title(f"N = {S.N}, dmed = {S.dmed:.4f}, deff = {S.deff:.4f}",fontsize=10)
        S.fig.tight_layout()
        
        #Generate circle
        S=Spangler(1000,seed=10)
        S.gen_circle()
        S.plot()
        S.plot(c='b',spangled=dict(color='r'))
        S.ax.set_title(f"N = {S.N}, dmed = {S.dmed:.4f}, deff = {S.deff:.4f}",fontsize=10)
        S.fig.tight_layout()
        return
    
        """
        self.assertEqual(np.isclose([P.physics.wrot],
                                    [2*np.pi/PlanetDefaults.physics["prot"]],
                                    rtol=1e-7),
                         [True]*1)
        #Check exception: primary could not be different from None or Body
        self.assertRaises(AssertionError,lambda:Observer(primary="Nada"))
        """
        

if __name__=="__main__":
        unittest.main(argv=['first-arg-is-ignored'],exit=False)
