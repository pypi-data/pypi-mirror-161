from __future__ import annotations

from typing import Optional, Union

from osaft import log
from osaft.core.backgroundfields import WaveType
from osaft.core.frequency import Frequency
from osaft.core.geometries import Sphere
from osaft.core.helper import StringFormatter as SF
from osaft.core.solids import RigidSolid
from osaft.core.variable import ActiveVariable
from osaft.solutions.base_solution import BaseSolution
from osaft.solutions.basedoinikov1994.base import BaseDoinikov1994


class BaseDoinikov1994Rigid(BaseDoinikov1994, BaseSolution):
    """Base class for Doinikov (viscous fluid-rigid sphere; 1994)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the fluid-like sphere [kg/m^3]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param eta_f: shear viscosity [Pa s]
    :param zeta_f: bulk viscosity [Pa s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param wave_type: Type of wave, traveling or standing
    :param position: Position in the standing wave field [rad]
    """

    # Supported wave_type for the class
    supported_wavetypes = [WaveType.STANDING, WaveType.TRAVELLING]

    def __init__(
        self, f: Union[Frequency, float],
        R_0: Union[Sphere, float, int],
        rho_s: float,
        rho_f: float, c_f: float,
        eta_f: float, zeta_f: float,
        p_0: float,
        wave_type: Optional[WaveType] = WaveType.STANDING,
        position: Optional[float] = None,
    ) -> None:
        """Constructor method
        """

        # init of parent class
        BaseDoinikov1994.__init__(
            self,
            f=f, R_0=R_0,
            rho_f=rho_f, c_f=c_f, eta_f=eta_f, zeta_f=zeta_f,
            p_0=p_0, wave_type=wave_type, position=position,
        )
        BaseSolution.__init__(self, 'Doinikov1994Rigid')

        # Scatterer
        self.scatterer = RigidSolid(self.f, rho_s)

        # Dependent Variables
        self._rho_t = ActiveVariable(
            self._compute_rho_t,
            'ratio of densities',
        )
        self._rho_t.is_computed_by(self.fluid._rho_f, self.scatterer._rho_s)

        if type(self) == BaseDoinikov1994Rigid:
            log.info(repr(self))  # pragma: no cover

    def __repr__(self):  # pragma: no cover
        return (
            f'BaseDoinikov1994Rigid(f={self.f}, R_0={self.R_0}, '
            f'rho_s={self.rho_s}, rho_f={self.rho_f}, c_f={self.c_f}, '
            f'eta_f={self.eta_f}, zeta_f={self.zeta_f}, '
            f'p_0={self.p_0}, position={self.position}, {self.wave_type}, '
            f'N_max={self.N_max})'
        )

    def __str__(self):  # pragma: no cover
        out = 'Doinikov\'s  (1994) model (viscous fluid-rigid sphere)'
        out += ' with the following properties: \n'
        out += SF.get_str_text('Frequency', 'f', self.f, 'Hz')
        out += SF.get_str_text('Pressure', 'p_0', self.p_0, 'Pa')
        out += SF.get_str_text('Wavetype', 'wave_type', self.wave_type, None)
        out += SF.get_str_text(
            'Position', 'd',
            self.position, 'Pa',
        )
        out += SF.get_str_text(
            'Wavelength', 'lambda',
            self.field.lambda_f, 'm',
        )

        out += 'Fluid\n'
        out += SF.get_str_text(
            'Density', 'rho_f',
            self.rho_f, 'kg/m^3',
        )
        out += SF.get_str_text(
            'Sound Speed', 'c_0',
            self.c_f, 'm/s',
        )
        out += SF.get_str_text(
            'Compressibility', 'kappa_f',
            self.kappa_f, '1/Pa',
        )
        out += SF.get_str_text(
            'Shear viscosity', 'eta_f',
            self.eta_f, '1/Pa',
        )
        out += SF.get_str_text(
            'Bulk viscosity', 'zeta_f',
            self.zeta_f, '1/Pa',
        )

        out += 'Particle\n'
        out += SF.get_str_text(
            'Radius', 'R_0',
            self.R_0, 'm',
        )
        out += SF.get_str_text(
            'Density', 'rho_s',
            self.rho_s, 'kg/m^3',
        )
        return out

    # -------------------------------------------------------------------------
    # Wrappers for Independent Scatterer Attributes
    # -------------------------------------------------------------------------

    @property
    def rho_s(self) -> float:
        """ Wraps to :attr:`osaft.core.solids.RigidSolid.rho_s`
        """
        return self.scatterer.rho_s

    @rho_s.setter
    def rho_s(self, value: float) -> None:
        self.scatterer.rho_s = value


if __name__ == '__main__':
    pass
