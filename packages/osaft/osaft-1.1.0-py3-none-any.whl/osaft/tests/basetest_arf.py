from abc import abstractmethod
from enum import auto

from osaft import WaveType
from osaft.core.backgroundfields import WrongWaveTypeError


class HelperARF:
    """Baseclass for testing the ARF computation
    """
    _threshold = 1e-12

    @abstractmethod
    def compute_arf(self):
        pass

    def test_wrong_wave_type_error(self):
        WaveType.WRONGWAVETYPE = auto()
        self.cls.wave_type = WaveType.WRONGWAVETYPE
        self.assertRaises(WrongWaveTypeError, self.cls.compute_arf)

    def test_arf(self) -> None:
        self.do_testing(
            self.compute_arf, self.cls.compute_arf,
            threshold=self._threshold,
            zero=1e-30,
        )


class HelperStandingARF(HelperARF):

    def test_arf(self) -> None:
        self.wave_type = WaveType.STANDING
        self._wave_type.list_of_values = [self.wave_type]
        HelperARF.test_arf(self)


class HelperTravelingARF(HelperARF):

    def test_arf(self) -> None:

        self.wave_type = WaveType.TRAVELLING
        self._wave_type.list_of_values = [self.wave_type]
        HelperARF.test_arf(self)


class HelperCompareARF:
    arf_compare_threshold = 1e-12

    def test_comparison_arf(self):
        self.do_testing(
            self.cls.compute_arf,
            self.compare_cls.compute_arf,
            threshold=self.arf_compare_threshold,
            zero=1e-30,
        )
