import unittest

from osaft import WaveType, doinikov1994compressible, yosioka1955
from osaft.core.basecomposite import (
    BaseFrequencyComposite,
    BaseSphereFrequencyComposite,
)
from osaft.core.frequency import Frequency
from osaft.core.functions import pi
from osaft.core.geometries import Sphere
from osaft.core.solids import ElasticSolid
from osaft.tests.basetest import BaseTest


class TestBaseFrequencyComposite(BaseTest):

    def test_types_for_frequency(self):
        cls = BaseFrequencyComposite(10.1)
        self.assertTrue(isinstance(cls, BaseFrequencyComposite))
        cls = BaseFrequencyComposite(10.1)
        self.assertTrue(isinstance(cls, BaseFrequencyComposite))

        F = Frequency(1e6)
        cls = BaseFrequencyComposite(F)
        self.assertTrue(isinstance(cls, BaseFrequencyComposite))

    def test_TypeError(self):

        self.assertRaises(TypeError, BaseFrequencyComposite, 's')

    def test_input_variables(self):

        # Test elastic solid
        solid = ElasticSolid(1e6, 1e6, 0.3, 1e3)
        expected_solid = {'E_s', 'nu_s', 'rho_s', 'f'}
        got_solid = set(solid.input_variables())
        self.assertSetEqual(got_solid, expected_solid)

        # Doinikov Compressible
        doinikov = doinikov1994compressible.ARF(
            1e6, 1e-6, 3e3, 1e3, 1e-3,
            1e-3, 1e3, 1e3, 1e-3, 1e-3,
            1e5, WaveType.STANDING, 0,
            True,
        )

        # Test Doinikov 1994 Compressible
        expected_doinikov = {
            'small_particle_limit',
            'small_viscous_boundary_layer',
            'large_viscous_boundary_layer', 'rho_s', 'c_s',
            'eta_s', 'zeta_s', 'position', 'p_0', 'wave_type',
            'rho_f', 'c_f', 'eta_f', 'zeta_f', 'R_0', 'f',
            'N_max',
        }
        got_doinikov = set(doinikov.input_variables())
        self.assertSetEqual(got_doinikov, expected_doinikov)

        # Test Yosioka & Kawasima (1955)
        yosioka = yosioka1955.ARF(
            1e6, 1e-6, 2e3, 2e3, 1e3, 1.5e3, 1e5,
            WaveType.TRAVELLING,
        )
        expected_yosioka = {
            'small_particle', 'bubble_solution', 'position',
            'p_0', 'wave_type', 'rho_s', 'c_s', 'rho_f', 'c_f',
            'R_0', 'f', 'N_max',
        }
        got_yosioka = set(yosioka.input_variables())
        self.assertSetEqual(got_yosioka, expected_yosioka)


class TestBaseSphereFrequencyComposite(BaseTest):

    def test_types_for_sphere(self):
        cls = BaseSphereFrequencyComposite(10.1, 10)
        self.assertTrue(isinstance(cls, BaseSphereFrequencyComposite))
        cls = BaseSphereFrequencyComposite(10.1, 10.0)
        self.assertTrue(isinstance(cls, BaseSphereFrequencyComposite))

        S = Sphere(1e-6)
        cls = BaseSphereFrequencyComposite(10.1, S)
        self.assertTrue(isinstance(cls, BaseSphereFrequencyComposite))

    def test_properties(self):
        def V(R):
            return 4 / 3 * R**3 * pi

        def A(R):
            return 4 * R**2 * pi

        R = 1e-6
        f = 1e6
        cls = BaseSphereFrequencyComposite(f, R)

        self.assertAlmostEqual(R, cls.R_0)
        self.assertAlmostEqual(V(R), cls.volume)
        self.assertAlmostEqual(A(R), cls.area)

        R = 4.39e-6
        cls.R_0 = R
        self.assertAlmostEqual(R, cls.R_0)
        self.assertAlmostEqual(V(R), cls.volume)
        self.assertAlmostEqual(A(R), cls.area)

    def test_TypeError(self):
        self.assertRaises(
            TypeError, BaseSphereFrequencyComposite,
            10.0, 's',
        )


if __name__ == '__main__':
    unittest.main()
