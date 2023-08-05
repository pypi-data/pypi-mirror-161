import scipy.constants as con
import numpy as np
from numpy import ndarray
from typing import Union
import logging

log = logging.getLogger(__name__)


class sEKVModel:
    def __init__(self,
                 i: ndarray = None,
                 n: float = None,
                 ispec: float = None,
                 vt0: float = None,
                 lambdac: float = None,
                 lambdad: float = None,
                 sigmad: float = None,
                 temp: float = 300.,
                 vs: float = 0.
                 ):
        """ Simplified EKV model.

        :param i: Array. Drain current in A, its elements should be positive values.
        :param n: Optional, float. Slope factor, which should be larger than 1.
        :param ispec: Optional, float. Specific current in A, which should be positive.
        :param vt0: Optional, float. Long-channel threshold voltage.
        :param lambdac: Optional, float. Velocity saturation parameter, which should be between 0 and 1.
        :param lambdad: Optional, float. Similar to `lambdac`, but it becomes the fitting parameter for gds.
        :param sigmad: Optional, float. Output conductance parameter.
        :param temp: Optional, float. Temperature in K.
        :param vs: Optional, float. Source voltage in V.
        """
        self._T = temp
        self._VS = vs
        self._Ut = self.get_thermal_voltage(temp)

        if i is not None:
            self.check_ID(i)
            self._ID = i

        if n is not None:
            self.check_n(n)
            self._n = n

        if ispec is not None:
            self.check_Ispec(ispec)
            self._Ispec = ispec

        if vt0 is not None:
            self.check_Vt0(vt0)
            self._Vt0 = vt0

        if lambdac is not None:
            self.check_lambdac(lambdac)
            self._lambdac = lambdac

        if lambdad is not None:
            self.check_lambdad(lambdad)
            self._lambdad = lambdad

        if sigmad is not None:
            self.check_sigmad(sigmad)
            self._sigmad = sigmad

    @staticmethod
    def check_ID(i: ndarray):
        if not isinstance(i, ndarray):
            raise TypeError('The input `ID` should be a numpy array.')

        if not np.alltrue(i > 0):
            raise ValueError('The drain current `ID` should be an array with elements all positive.')

    @staticmethod
    def check_n(n: float):
        if not isinstance(n, float):
            raise TypeError('The `n` should be float.')
        if n < 1:
            raise ValueError('The `n` should be larger than 1.')

    @staticmethod
    def check_Ispec(ispec: float):
        if not isinstance(ispec, float):
            raise TypeError('The `ispec` should be float.')
        if ispec < 0:
            raise ValueError('The `ispec` should be positive.')

    @staticmethod
    def check_lambdac(lambdac: float):
        if not isinstance(lambdac, float):
            raise TypeError('The `lambdac` should be float.')
        if lambdac < 0:
            raise ValueError('The `lambdac` should be positive.')

    @staticmethod
    def check_lambdad(lambdad: float):
        if not isinstance(lambdad, float):
            raise TypeError('The `lambdad` should be float.')
        if lambdad < 0:
            raise ValueError('The `lambdad` should be positive.')

    @staticmethod
    def check_sigmad(sigmad: float):
        if not isinstance(sigmad, float):
            raise TypeError('The `sigmad` should be float.')
        if sigmad < 0:
            raise ValueError('The `sigmad` should be positive.')

    @staticmethod
    def check_Vt0(vt0: float):
        if not isinstance(vt0, float):
            raise TypeError('The `vt0` should be float.')

    @property
    def ID(self):
        """Drain current."""
        return self._ID

    @property
    def n(self):
        """Slope factor."""
        return self._n

    @property
    def Ispec(self):
        """Specific current."""
        return self._Ispec

    @property
    def Vt0(self):
        """Long-channel threshold voltage."""
        return self._Vt0

    @property
    def lambdac(self):
        """Velocity saturation parameter."""
        return self._lambdac

    @property
    def lambdad(self):
        return self._lambdad

    @property
    def sigmad(self):
        return self._sigmad

    @property
    def IC(self):
        """Inversion coefficient."""
        return self.ID / self.Ispec

    @property
    def Ut(self):
        """Thermal voltage."""
        return self._Ut

    @property
    def T(self):
        """Temperature."""
        return self._T

    @property
    def VS(self):
        """Source voltage."""
        return self._VS

    @property
    def ekv_4params(self) -> dict:
        return {
            "n": self.n,
            "ispec": self.Ispec,
            "lambdac": self.lambdac,
            "vt0": self.Vt0
                }

    @property
    def readable_ekv4params(self) -> str:
        d = self.ekv_4params
        s = "\n".join([
            "n = %.2f" % d['n'],
            "$I_{spec}$ = %.2e A" % d["ispec"],
            "$\lambda_c$ = %.3f" % d["lambdac"],
            "$V_{T0}$ = %.3f V" % d["vt0"],
        ])
        return s

    def set_Ispec(self, ispec: float):
        self.check_Ispec(ispec)
        self._Ispec = ispec

    def set_Vt0(self, vt0: float):
        self.check_Vt0(vt0)
        self._Vt0 = vt0

    def set_n(self, n: float):
        self.check_n(n)
        self._n = n

    def set_lambdac(self, lambdac: float):
        self.check_lambdac(lambdac)
        self._lambdac = lambdac

    def set_lambdad(self, lambdad: float):
        self.check_lambdad(lambdad)
        self._lambdad = lambdad

    def set_sigmad(self, sigmad: float):
        self.check_sigmad(sigmad)
        self._sigmad = sigmad

    def get_sim_normalized_charge(self) -> ndarray:
        """Get normalized charge"""
        return self.model_normalized_charge(i=self.ID, ispec=self.Ispec, lambdac=self.lambdac)

    def get_sim_VG(self):
        """Get modeled VG"""
        return self.model_ID_vs_VG(i=self.ID, n=self.n, ispec=self.Ispec, lambdac=self.lambdac,
                                   vt0=self.Vt0, vs=self.VS, temperature=self.T)

    def get_sim_normalize_current_efficiency(self):
        """Get modeled normalized current efficiency."""
        return self.model_gms_over_IC_vs_IC(i=self.ID, ispec=self.Ispec, lambdac=self.lambdac)

    def get_sim_gms_over_IC(self):
        """Get modeled normalized current efficiency."""
        return self.get_sim_normalize_current_efficiency()

    def get_sim_gms(self):
        """Get modeled normalized transconductance."""
        return self.IC * self.get_sim_gms_over_IC()

    def get_sim_gds(self):
        """Get modeled normalized output conductance."""
        gms_use_lambdad = self.model_gms(i=self.ID, ispec=self.Ispec, lambdac=self.lambdad)
        return gms_use_lambdad * self.sigmad / self.n

    @staticmethod
    def model_normalized_charge(i: ndarray,
                                ispec: float,
                                lambdac: float = 0.) -> ndarray:
        """Calculate normalized charge.

        :param i: current in A.
        :param ispec: specific current in A.
        :param lambdac: velocity saturation parameter.

        :return: the normalized charge in 1-D sequence or array.
        """
        ic = i / ispec
        q = (np.sqrt(4 * ic + (1 + (lambdac * ic)) ** 2) - 1) / 2.0
        return q

    @staticmethod
    def get_thermal_voltage(temperature: float = 300.0) -> float:
        """Calculate thermal voltage.

        :param float temperature: the value of temperature in Kelvin.
        :return: thermal voltage.
        """
        return con.Boltzmann * temperature / con.elementary_charge

    @staticmethod
    def model_gms_over_IC_vs_IC(i: ndarray,
                                lambdac: float,
                                ispec: float) -> ndarray:
        ic = i / ispec
        numerator = ((ic * lambdac + 1.0) ** 2 + 4.0 * ic) ** (1 / 2) - 1.0
        denominator = ic * (lambdac * (lambdac * ic + 1.0) + 2.0)
        return numerator / denominator

    @staticmethod
    def model_ID_vs_VG(i: ndarray,
                       n: float,
                       ispec: float,
                       lambdac: float,
                       vt0: float,
                       vs: float = 0.,
                       temperature: float = 300.0
                       ) -> ndarray:
        """Theoretically calculate VG from given ID via sEKV model.

        :param i: the current in 1-D sequence or array.
        :param n: slope factor.
        :param ispec: specific current in A.
        :param lambdac: velocity saturation parameter
        :param vt0: threshold voltage in V.
        :param vs: source voltage in V.
        :param temperature: temperature in Kelvin.
        :return: 1-D sequence or array gate voltage in V.
        """
        qs = sEKVModel.model_normalized_charge(i, ispec, lambdac)
        ut = sEKVModel.get_thermal_voltage(temperature)
        vp = vs + ut * (2 * qs + np.log(qs))
        vg = n * vp + vt0
        return vg

    @staticmethod
    def model_gms(i: ndarray,
                  lambdac: float,
                  ispec: float) -> ndarray:
        return sEKVModel.model_gms_over_IC_vs_IC(i=i, lambdac=lambdac, ispec=ispec) * (i/ispec)
