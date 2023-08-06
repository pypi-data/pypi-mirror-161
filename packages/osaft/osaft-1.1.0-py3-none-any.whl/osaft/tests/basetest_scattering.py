import unittest
from abc import abstractmethod
from collections.abc import Callable
from random import randint, random

import numpy as np

from osaft import ViscoelasticFluid, ViscousFluid, WaveType
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.functions import LegendreFunctions as Leg
from osaft.core.functions import exp, full_range, pi


class BaseHelperScattering:

    @staticmethod
    def get_random_n():
        return randint(0, 10)

    @staticmethod
    def get_random_r(cls):
        return cls.R_0 * (2 + 20 * random())

    @staticmethod
    def get_random_t():
        return random()

    @staticmethod
    def get_random_theta():
        return random() * pi


class HelperScattering(BaseHelperScattering):

    # -------------------------------------------------------------------------
    # Thresholds
    # -------------------------------------------------------------------------

    _v_particle_threshold = 1e-12
    _v_fluid_threshold = 1e-12
    _v_boundary_conditions = 1e-12

    @property
    def v_particle_threshold(self) -> float:
        return self._v_particle_threshold

    @property
    def v_fluid_threshold(self) -> float:
        return self._v_fluid_threshold

    @property
    def v_boundary_conditions(self) -> float:
        return self._v_boundary_conditions

    # -------------------------------------------------------------------------
    # Acoustic Velocities Methods
    # -------------------------------------------------------------------------

    def V_r_i(self, n, r) -> complex:
        out = self.cls.A_in(n)
        out *= self.cls.k_f
        out *= Bf.d1_besselj(n, self.cls.k_f * r)
        return out

    def V_theta_i(self, n, r) -> complex:
        out = self.cls.A_in(n)
        out *= Bf.besselj(n, self.cls.k_f * r)
        out /= r
        return out

    def V_r_sc(self, n, r) -> complex:
        pass

    def V_theta_sc(self, n, r) -> complex:
        pass

    def radial_acoustic_fluid_velocity(
        self,
        r, theta,
        t,
        scattered,
        incident,
        mode=None,
    ) -> float:
        if scattered and incident:
            def v(l, x):
                return self.V_r_sc(l, x) + self.V_r_i(l, x)
        elif scattered and not incident:
            v = self.V_r_sc
        elif not scattered and incident:
            v = self.V_r_i
        else:
            def v(l, x):
                return 0

        out = exp(-1j * self.cls.omega * t)
        if mode is not None:
            out *= Leg.cos_monomial(mode, theta, v(mode, r))
        else:
            out *= Leg.cos_poly(
                theta, [
                    v(n, r)
                    for n in full_range(self.cls.N_max)
                ],
            )
        return out

    def tangential_acoustic_fluid_velocity(
        self, r, theta, t, scattered, incident, mode=None,
    ) -> float:
        if scattered and incident:
            def v(l, x):
                if l == 0:
                    return 0
                return self.V_theta_sc(l, x) + self.V_theta_i(l, x)
        elif scattered and not incident:
            v = self.V_theta_sc
        elif not scattered and incident:
            v = self.V_theta_i
        else:
            def v(l, x):
                return 0

        out = exp(-1j * self.cls.omega * t)
        if mode is not None:
            out *= Leg.first_cos_monomial(mode, theta, v(mode, r))
        else:
            out *= Leg.first_cos_poly(
                theta,
                [
                    v(n, r) for n in
                    full_range(0, self.cls.N_max)
                ],
            )
        return out

    def radial_particle_displacement(self, r, theta, t, mode):
        velocity = self.radial_particle_velocity(r, theta, t, mode)
        return velocity / (- 1j * self.cls.omega)

    def tangential_particle_displacement(self, r, theta, t, mode):
        velocity = self.tangential_particle_velocity(r, theta, t, mode)
        return velocity / (- 1j * self.cls.omega)

    @abstractmethod
    def radial_particle_velocity(self, r, theta, t, mode) -> float:
        pass

    @abstractmethod
    def tangential_particle_velocity(self, r, theta, t, mode) -> float:
        pass

    # -------------------------------------------------------------------------
    # Acoustic Velocities Tests
    # -------------------------------------------------------------------------

    def test_radial_particle_velocity(self) -> None:
        # skip changing R_0 so the RT.is_inside_sphere does not get triggered
        self.test_variables.remove(self._R_0)
        for n in range(self.n_runs):
            n = self.get_random_n()
            r = self.cls.R_0 * 0.9
            t = self.get_random_t()
            theta = self.get_random_theta()
            self.do_testing(
                func_1=self.radial_particle_velocity,
                args_1=(r, theta, t, n),
                func_2=self.cls.radial_particle_velocity,
                args_2=(r, theta, t, n),
                threshold=self.v_particle_threshold,
            )

    def test_tangential_particle_velocity(self) -> None:
        # skip changing R_0 so the RT.is_inside_sphere does not get triggered
        self.test_variables.remove(self._R_0)
        for _ in range(self.n_runs):
            n = self.get_random_n()
            r = self.cls.R_0 * 0.9
            t = self.get_random_t()
            theta = self.get_random_theta()
            self.do_testing(
                func_1=self.tangential_particle_velocity,
                args_1=(r, theta, t, n),
                func_2=self.cls.tangential_particle_velocity,
                args_2=(r, theta, t, n),
                threshold=self.v_particle_threshold,
            )

    def test_radial_particle_displacement(self) -> None:
        # skip changing R_0 so the RT.is_inside_sphere does not get triggered
        self.test_variables.remove(self._R_0)
        for n in range(self.n_runs):
            n = self.get_random_n()
            r = self.cls.R_0 * 0.9
            t = self.get_random_t()
            theta = self.get_random_theta()
            self.do_testing(
                func_1=self.radial_particle_displacement,
                args_1=(r, theta, t, n),
                func_2=self.cls.radial_particle_displacement,
                args_2=(r, theta, t, n),
                threshold=self.v_particle_threshold,
            )

    def test_tangential_particle_displacement(self) -> None:
        # skip changing R_0 so the RT.is_inside_sphere does not get triggered
        self.test_variables.remove(self._R_0)
        for _ in range(self.n_runs):
            n = self.get_random_n()
            r = self.cls.R_0 * 0.9
            t = self.get_random_t()
            theta = self.get_random_theta()
            self.do_testing(
                func_1=self.tangential_particle_displacement,
                args_1=(r, theta, t, n),
                func_2=self.cls.tangential_particle_displacement,
                args_2=(r, theta, t, n),
                threshold=self.v_particle_threshold,
            )

    def test_fluid_velocities_Error(self) -> None:
        # neither scattering nor incident is selected
        with self.assertRaises(ValueError):
            self.cls.radial_acoustic_fluid_velocity(
                self.cls.R_0, 0, 0, False, False,
            )
        with self.assertRaises(ValueError):
            self.cls.tangential_acoustic_fluid_velocity(
                self.cls.R_0, 0, 0, False, False,
            )

    def test_radial_acoustic_fluid_velocity(self) -> None:
        # skip changing R_0 so the RT.is_outside_sphere does not get triggered
        self.test_variables.remove(self._R_0)
        for incident, scattering in [
            (True, True),
            (True, False),
            (False, True),
        ]:
            for _ in range(5):
                n = self.get_random_n()
                r = self.get_random_r(self.cls)
                t = self.get_random_t()
                theta = self.get_random_theta()

                self.do_testing(
                    func_1=self.radial_acoustic_fluid_velocity,
                    args_1=(r, t, theta, incident, scattering, n),
                    func_2=self.cls.radial_acoustic_fluid_velocity,
                    args_2=(r, t, theta, incident, scattering, n),
                    threshold=self.v_fluid_threshold,
                )
                # test once with mode = None
                self.do_testing(
                    func_1=self.radial_acoustic_fluid_velocity,
                    args_1=(r, t, theta, incident, scattering),
                    func_2=self.cls.radial_acoustic_fluid_velocity,
                    args_2=(r, t, theta, incident, scattering),
                    threshold=self.v_fluid_threshold,
                )

    def test_tangential_acoustic_fluid_velocity(self) -> None:
        # skip changing R_0 so the RT.is_outside_sphere does not get triggered
        self.test_variables.remove(self._R_0)
        for incident, scattering in [
            (True, True),
            (True, False),
            (False, True),
        ]:
            for _ in range(5):
                n = self.get_random_n()
                r = self.get_random_r(self.cls)
                t = self.get_random_t()
                theta = self.get_random_theta()

                self.do_testing(
                    func_1=self.tangential_acoustic_fluid_velocity,
                    args_1=(r, theta, t, incident, scattering, n),
                    func_2=self.cls.tangential_acoustic_fluid_velocity,
                    args_2=(r, theta, t, incident, scattering, n),
                    threshold=self.v_fluid_threshold,
                )

                # test once with mode = None
                self.do_testing(
                    func_1=self.tangential_acoustic_fluid_velocity,
                    args_1=(r, t, theta, incident, scattering),
                    func_2=self.cls.tangential_acoustic_fluid_velocity,
                    args_2=(r, t, theta, incident, scattering),
                    threshold=self.v_fluid_threshold,
                )

    # -------------------------------------------------------------------------
    # Test Input Testers
    # -------------------------------------------------------------------------

    def test_ThetaTester_present(self):
        lst = [1.0, 0.5, 4]

        self.assertRaises(
            ValueError,
            self.cls.radial_particle_velocity,
            0, lst, 0,
        )
        self.assertRaises(
            ValueError,
            self.cls.tangential_particle_velocity,
            0, lst, 0,
        )

        self.assertRaises(
            ValueError,
            self.cls.radial_acoustic_fluid_velocity,
            0, lst, 0, True, True,
        )
        self.assertRaises(
            ValueError,
            self.cls.tangential_acoustic_fluid_velocity,
            0, lst, 0, True, True,
        )

    def test_RadiusTester_present(self):
        lst = 0.99 * self.R_0 * np.random.rand(10)
        lst[0] = -1.0
        lst[-1] = 1.1 * self.R_0

        self.assertRaises(
            ValueError, self.cls.radial_particle_velocity,
            lst, 0, 0,
        )
        self.assertRaises(
            ValueError, self.cls.tangential_particle_velocity,
            lst, 0, 0,
        )

        lst = 1.01 * self.R_0 * (np.random.rand(10) + 1)
        lst[0] = -1.0
        lst[-1] = 0.1 * self.R_0

        self.assertRaises(
            ValueError,
            self.cls.radial_acoustic_fluid_velocity,
            lst, 0, 0, True, True,
        )
        self.assertRaises(
            ValueError,
            self.cls.tangential_acoustic_fluid_velocity,
            lst, 0, 0, True, True,
        )

    # -------------------------------------------------------------------------
    # Test Boundary Conditions
    # -------------------------------------------------------------------------

    def test_boundary_conditions(self) -> None:
        test_tangential = False
        if (
            isinstance(self.cls.fluid, ViscousFluid)
            or isinstance(self.cls.fluid, ViscoelasticFluid)
        ):
            test_tangential = True

        modes_to_test = [0, 1, 2, 3, 4, None]

        thetas = np.random.uniform(size=10)
        # testing radial direction at r=R_0
        for theta in thetas:
            t = self.get_random_t()
            for mode in modes_to_test:
                with self.subTest(
                        msg='Testing radial condition',
                        theta=f'\u03C0 * {theta}', t=t,
                        mode=mode,
                ):
                    v_s = self.cls.radial_acoustic_fluid_velocity(
                        self.R_0, pi * theta, t, True, True, mode=mode,
                    )
                    v_p = self.cls.radial_particle_velocity(
                        self.R_0, pi * theta, t, mode=mode,
                    )
                    self.assertAlmostEqual(
                        v_p, v_s,
                        threshold=self.v_boundary_conditions,
                    )

        if test_tangential:
            # testing tangential direction at r=R_0
            for theta in thetas:
                t = self.get_random_t()
                for mode in modes_to_test:
                    with self.subTest(
                            msg='Testing tangential condition',
                            theta=f'\u03C0 * {theta}', t=t,
                            mode=mode,
                    ):
                        v_s = self.cls.tangential_acoustic_fluid_velocity(
                            self.R_0, pi * theta, t, True, True,
                        )
                        v_p = self.cls.tangential_particle_velocity(
                            self.R_0, pi * theta, t,
                        )
                        self.assertAlmostEqual(
                            v_p, v_s,
                            threshold=self.v_boundary_conditions,
                        )


class HelperCompareScattering(BaseHelperScattering):
    _scattering_compare_threshold = 1e-12

    @property
    def scattering_compare_threshold(self) -> float:
        return self._scattering_compare_threshold

    def _sc_comparison(
        self,
        func_1: Callable,
        func_2: Callable,
        msg: str,
        inside_sphere: bool,
    ) -> None:

        if inside_sphere:
            test_R = self.R_0 * np.random.uniform(low=0, high=1, size=10)
        else:
            test_R = self.R_0 * np.random.uniform(low=1, high=10, size=10)

        test_theta = np.pi * np.random.uniform(low=0, high=1, size=10)

        t = self.get_random_t()
        for wt in WaveType:
            self.cls.wave_type = wt
            self.compare_cls.wave_type = wt
            for r in np.nditer(test_R):
                for theta in np.nditer(test_theta):
                    if inside_sphere:
                        v1 = func_1(r, theta, t)
                        v2 = func_2(r, theta, t)
                    else:
                        v1 = func_1(r, theta, t, True, True)
                        v2 = func_2(r, theta, t, True, True)

                    subtest_msg = (
                        f'{msg}, '
                        f'theta={theta/np.pi:1.2f}*\u03C0, '
                        f'r={r/self.R_0:1.2f}*R_0 , '
                        f't={t:1.2e}'
                    )

                    with self.subTest(msg=subtest_msg):
                        self.assertAlmostEqual(
                            v1, v2,
                            threshold=self.scattering_compare_threshold,
                        )

    @unittest.skip('Test failing, further investigations in theory needed.')
    def test_sc_comparison_outside(self) -> None:
        msg = 'Tangential fluid velocity'
        func_1 = self.cls.tangential_acoustic_fluid_velocity
        func_2 = self.compare_cls.tangential_acoustic_fluid_velocity
        self._sc_comparison(func_1, func_2, msg, inside_sphere=False)

        msg = 'Radial fluid velocity'
        func_1 = self.cls.radial_acoustic_fluid_velocity
        func_2 = self.compare_cls.radial_acoustic_fluid_velocity
        self._sc_comparison(func_1, func_2, msg, inside_sphere=False)

    @unittest.skip('Test failing, further investigations in theory needed.')
    def test_sc_comparison_inside(self) -> None:
        msg = 'Tangential particle velocity'
        func_1 = self.cls.tangential_particle_velocity
        func_2 = self.compare_cls.tangential_particle_velocity
        self._sc_comparison(func_1, func_2, msg, inside_sphere=True)

        msg = 'Radial particle velocity'
        func_1 = self.cls.radial_particle_velocity
        func_2 = self.compare_cls.radial_particle_velocity
        self._sc_comparison(func_1, func_2, msg, inside_sphere=True)
