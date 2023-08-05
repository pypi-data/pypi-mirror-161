import logging
import numpy as np
from numpy import ndarray
from matplotlib import pyplot as plt
from scipy.signal import savgol_filter, find_peaks
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from collections import namedtuple
import time
import pandas as pd

from sekve.plotting import update_rcParams
from sekve.model import sEKVModel
from sekve.extractor.ss_extractor import extract_ss
from sekve.utils import get_savgol_win_num
from sekve.plotting import update_rcParams

log = logging.getLogger(__name__)


class Base(sEKVModel):
    _progress_figsize = (7, 5)
    _final_figsize = (4, 3)

    def __init__(self, vg: ndarray, i: ndarray, vd: float,
                 width: float = None, length: float = None,
                 temp=300., vs=0.):
        super().__init__(i=i, temp=temp, vs=vs)
        self._VG = vg
        self._W = width
        self._L = length
        self._VD = vd
        self._VG_m = None  # modeled VG

        self._Gm = self.cal_Gm(i=self.ID, vg=self.VG)
        self._Gm_over_ID = self.cal_Gm_over_ID(i=self.ID, vg=self.VG)
        self._n_values = self.cal_n(i=self.ID, vg=self.VG, temp=self.T)

        self._progress_fig = plt.figure(figsize=self.__class__._progress_figsize)
        self._final_fig = plt.figure(figsize=self.__class__._final_figsize)

    @property
    def W(self):
        return self._W

    @property
    def L(self):
        return self._L

    @property
    def VG(self):
        return self._VG

    @property
    def VG_m(self):
        return self._VG_m

    @property
    def VD(self):
        return self._VD

    @property
    def VDS(self):
        return self.VD - self.VS

    @property
    def Gm(self):
        return self._Gm

    @property
    def Gm_over_ID(self):
        return self._Gm_over_ID

    @property
    def n_values(self):
        return self._n_values

    @property
    def progress_fig(self):
        self._progress_fig.tight_layout()
        return self._progress_fig

    @property
    def final_fig(self):
        self._final_fig.tight_layout()
        return self._final_fig

    @classmethod
    def set_progress_figsize(cls, figsize: tuple):
        cls._progress_figsize = figsize

    @classmethod
    def set_final_figsize(cls, figsize: tuple):
        cls._final_figsize = figsize

    @staticmethod
    def cal_Gm(i: ndarray, vg: ndarray) -> ndarray:
        """Calculate transconductance."""
        return np.gradient(i, vg)

    @staticmethod
    def cal_Gm_over_ID(i: ndarray, vg: ndarray) -> ndarray:
        """Calculate transconductance efficiency."""
        ln_id = np.log(i)
        return np.gradient(ln_id, vg)

    @staticmethod
    def cal_n(i: ndarray, vg: ndarray, temp: float):
        ut = sEKVModel.get_thermal_voltage(temp)
        ln_id = np.log(i)
        one_over_n = np.gradient(ln_id, vg) * ut
        return 1./one_over_n

    def show(self):
        self.progress_fig.tight_layout(pad=0.1)
        self.progress_fig.show()
        self.final_fig.tight_layout(pad=0.1)
        self.final_fig.show()

    def save_data(self, output_path: str):
        """Save result into csv file"""
        d = dict(data_vg=self.VG, data_id=self.ID,
                 model_vg=self.VG_m, ic=self.ID / self.Ispec)
        df = pd.DataFrame(d)
        df_csv = df.to_csv(index=False, line_terminator="\n")
        with open(output_path, "w") as file:
            file.write(self.readable_ekv4params)
            file.write("\r\n")
            file.write(df_csv)


class Params(Base):
    _bbox_style = dict(boxstyle='round', facecolor='white', alpha=0.7)

    def __init__(self, vg: ndarray, i: ndarray, vd: float, *args, **kwargs):
        super().__init__(vg, i, vd, *args, **kwargs)

        # parameters for `_get_Gm_peak`.
        self._savgol_frac_max_Gm = 0.2
        self._savgol_polyorder_max_Gm = 2
        self._find_peak_width = 0.2 * len(self.ID)
        self._offset_vg = 0.05

        # parameters for `_extract_Ispec`.
        self._n_slope_limit = None
        self._savgol_frac_Ispec = 0.2
        self._savgol_polyorder_Ispec = 2
        self._slope_threshold = 0.7

        # parameters for `_extract_Ispec_and_lambdac`.
        self._initial_lambdac = 0.2
        self._ignore_lambdac_threshold = 1e-3

        # parameters for `_extract_Vt0`
        self._initial_vt0 = 0.2

        # parameters for `_refine_Ispec_and_lambdac`
        self._Vt0_offset = 0.05

        # parameters for subthreshold slope extraction
        self._ss_kwargs = dict(frac=0.3, take_val="min")

        # parameters for plotting
        self._insert_ax_loc = [0.1, 0.12, 0.5, 0.4]

        update_rcParams()

    # TODO: add setters

class Extractor(Params):
    """Extracting simplified EKV parameters from transfer and output characteristics."""
    def __init__(self, vg: ndarray, i: ndarray, vd: float, vs: float = 0.,
                 width: float = None, length: float = None, temp: float = 300.,
                 remove_mobility_reduction=True, vth_tol=0.02, n_ext_method='ss',
                 force_lambdac_0=False, opt_method="trf", no_refine=False
                 ):
        # TODO: Document the parameters.
        super().__init__(vg, i, vd, width, length, temp, vs)

        self._remove_mobility_reduction = remove_mobility_reduction
        self._vth_tol = vth_tol
        self._n_ext_method = n_ext_method
        self._force_lambdac_0 = force_lambdac_0
        self._opt_method = opt_method
        self._no_refine = no_refine

    def run_extraction(self):
        """Execute the extraction."""
        start = time.time()
        log.info("Start extracting ...")

        self._cleanup()
        self._define_region()
        self._extract_n()
        self._extract_Ispec()
        self._extract_Ispec_and_lambdac()
        self._extract_Vt0()
        self._refine_Ispec_and_lambdac()
        self._refine_Vt0()
        self._plot_final_figure()
        end = time.time()
        spent_time = end - start
        log.info(f"Extraction is finished, spent {spent_time} s")

    def _get_Gm_peak(self, show=False):
        """Get peak Gm."""
        log_gm = np.log(self.Gm)
        non_nan = ~np.isnan(log_gm)
        non_nan_gm = log_gm[non_nan]
        vg = self.VG[non_nan]
        id = self.ID[non_nan]

        win = get_savgol_win_num(data_len=len(self.ID), frac=self._savgol_frac_max_Gm)
        gm_smooth = savgol_filter(non_nan_gm, win, self._savgol_polyorder_max_Gm)
        peaks_loc, _ = find_peaks(gm_smooth, width=self._find_peak_width)

        if len(peaks_loc) == 1:
            peak_loc = peaks_loc[0]
        elif len(peaks_loc) > 1:
            peak_loc = peaks_loc[-1]
        else:
            peak_loc = np.where(gm_smooth == max(gm_smooth))

        peak = np.exp(gm_smooth[peak_loc])
        gm_smooth = np.exp(gm_smooth)
        Out = namedtuple("Out", "peak smoothed_gm vg id crit_vg")
        out = Out(peak=float(peak), smoothed_gm=gm_smooth, vg=vg, id=id, crit_vg=vg[peak_loc])

        if show:
            plt.plot(vg, gm_smooth, "--", label="smooth $G_m$")
            plt.plot(self.VG, self.ID, "-", label="$I_D$")
            plt.plot(self.VG, self.Gm, "+", label="$G_m$")
            plt.axvline(x=out.crit_vg)
            plt.axhline(y=out.peak)
            plt.show()

        return out

    def _cleanup(self):
        """Remove the noisy data and redefine the data range, starting from Ioff."""
        log_id = np.log10(self.ID)
        diff_log_id = np.gradient(log_id, self.VG)
        loc = np.where((~np.isnan(diff_log_id))
                       & (diff_log_id > 0))
        origin_num = len(self.ID)
        self._ID = self._ID[loc]
        self._VG = self._VG[loc]
        self._n_values = self._n_values[loc]
        self._Gm = self._Gm[loc]
        self._Gm_over_ID = self._Gm_over_ID[loc]

        argmin = np.argmin(self.ID)
        loc = slice(argmin, None)
        self._ID = self._ID[loc]
        self._VG = self._VG[loc]
        self._n_values = self._n_values[loc]
        self._Gm = self._Gm[loc]
        self._Gm_over_ID = self._Gm_over_ID[loc]
        new_num = len(self.ID)
        log.info(f"The Id-Vg data is redefined by removing the noise data "
                 f"and accumulation region. Data points is reduced from "
                 f"{origin_num} to {new_num}.")

    def _define_region(self):
        """define the data region for extraction."""
        if self._remove_mobility_reduction:
            peak_gm_inf = self._get_Gm_peak()
            crti_vg = peak_gm_inf.crit_vg
            crti_vg_loc = np.where(self.VG > (crti_vg + self._offset_vg))
            try:
                stop = crti_vg_loc[0][0]
            except IndexError:
                loc = slice(0, None)
            else:
                loc = slice(0, stop)
        else:
            loc = slice(0, None)

        if loc != slice(0, None):
            origin_num = len(self.ID)
            self._ID = self._ID[loc]
            self._VG = self._VG[loc]
            self._n_values = self._n_values[loc]
            self._Gm = self._Gm[loc]
            self._Gm_over_ID = self._Gm_over_ID[loc]
            new_num = len(self.ID)
            log.info(f"The Id-Vg data is redefined by removing the "
                     f"region having mobility reduction due to vertical field. "
                     f"Data points is reduced from {origin_num} to {new_num}.")

        return loc

    def _extract_n(self):
        if self._n_ext_method == "ss":
            ss, vc = extract_ss(
                v=self.VG, i=self.ID, t=self.T,
                return_crit_v=True, **self._ss_kwargs)
            ss /= 1e3  # mV/dec -> V/dec
            n = ss / (self.Ut * np.log(10))
            self.set_n(n)
            log.info(f"The `n` is extracted with the value of {n}")
        else:
            raise ValueError("The n extracting method {} is not recognized.".format(self._n_ext_method))

    def _extract_Ispec(self):
        """Extract specific current."""
        # setup plot
        ax = self.progress_fig.add_subplot(221)
        ax.set_title("(a)", x=-0.1, y=-0.2)
        ax.loglog(self.ID, self._n_values, 'ro', label='Data')
        ax.axhline(y=self.n, color='k', linestyle='--', marker="None")

        slp = np.gradient(np.log(self._n_values), np.log(self.ID))
        loc = ~np.isnan(slp)
        win = get_savgol_win_num(data_len=len(self.ID[loc]), frac=self._savgol_frac_Ispec)
        _y = savgol_filter(slp[loc], win, self._savgol_polyorder_Ispec)
        _x = self.ID[loc]

        if self._n_slope_limit is None:
            self._n_slope_limit = 0.5 if max(_y) < self._slope_threshold else 1.

        diff = (_y - self._n_slope_limit) ** 2
        diff = savgol_filter(diff, window_length=win,
                             polyorder=self._savgol_polyorder_Ispec)
        diff = abs(diff)
        func = lambda ids, ids_c, n_c:\
            self._n_slope_limit * (np.log10(ids) - np.log10(ids_c)) + np.log10(n_c)
        _id = _x[np.where(diff == np.nanmin(diff))]
        loc_exp = np.where(self.ID == _id)
        new_y = 10 ** (func(self.ID, self.ID[loc_exp], self._n_values[loc_exp]))
        ax.loglog(self.ID, new_y, color="k")
        f = interp1d(new_y, self.ID)
        ispec = f(self._n)
        self.set_Ispec(float(ispec))

        ax.axvline(x=ispec, color='k', linestyle='--', marker='None')
        ax.text(0.03, 0.05, 'n = %.3f' % self._n, transform=ax.transAxes,
                ha="left", va="bottom",
                bbox=self.__class__._bbox_style)
        ax.text(0.97, 0.95, '$I_{spec}$=%.2e [A]' % ispec, transform=ax.transAxes,
                ha="right", va="top",
                bbox=self.__class__._bbox_style)
        ax.set_ylabel('n = $I_D$ / ($G_mU_T$) [-]')
        ax.set_xlabel('$I_D$ [A]')
        ax.set_ylim(0.1, None)
        ax.legend(loc=2)

        log.info("The `Ispec` is extracted with the value of %.3e A" % ispec)

    def _extract_Ispec_and_lambdac(self):
        """Get lambdac and specific current via optimizer."""
        # setup plot
        ax = self.progress_fig.add_subplot(222)
        ax.set_title("(b)", x=-0.1, y=-0.2)

        GmnUt_id = self.Gm_over_ID * self.Ut * self.n

        if self._force_lambdac_0:
            fit_func = lambda _id, _ispec: sEKVModel.model_gms_over_IC_vs_IC(
                i=_id, lambdac=0., ispec=self.Ispec
            )
            res = curve_fit(fit_func,
                            xdata=self.ID,
                            ydata=GmnUt_id,
                            p0=[self.Ispec],
                            loss='cauchy',
                            f_scale=0.01,
                            bounds=([0], [np.inf]),
                            method=self._opt_method
                            )
            ispec = res[0][0]
            self.set_Ispec(ispec)
            lambdac = 0
        else:
            fit_func = sEKVModel.model_gms_over_IC_vs_IC
            res = curve_fit(fit_func,
                            xdata=self.ID,
                            ydata=GmnUt_id,
                            p0=[self._initial_lambdac, self.Ispec],
                            loss='cauchy',
                            f_scale=0.01,
                            bounds=([0.0, 0], [1, np.inf]),
                            method=self._opt_method
                            )
            lambdac, ispec = res[0]
        self.set_lambdac(lambdac)
        self.set_Ispec(ispec)
        log.info("The `Ispec` is extracted with the value of %.3e A." % ispec)

        if lambdac < self._ignore_lambdac_threshold:
            self._force_lambdac_0 = True
            self.set_lambdac(0.)
            log.info("The `lambdac` is extracted with the value of %.3f." % lambdac)

        ax.loglog(self.ID / ispec, GmnUt_id, 'ro', label='Data')
        ax.loglog(self.ID / ispec,
                  sEKVModel.model_gms_over_IC_vs_IC(self.ID, self.lambdac, self.Ispec),
                  'k--', label='sEKV')

        ax.text(0.03, 0.03,
                '$\lambda_c$ = %.3f \n$I_{spec}$ = %.3e [A]' % (self.lambdac, self.Ispec),
                transform=ax.transAxes, ha='left', va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
        ax.set_xlabel('IC [-]')
        ax.set_ylabel('$G_mnU_T$ / $I_D$ [-]')
        ax.set_ylim(1e-2, 10)
        ax.legend(loc=1)

    def _extract_Vt0(self):
        # setup plot
        ax = self.progress_fig.add_subplot(223)
        ax.set_title("(c)", x=-0.1, y=-0.2)
        ax2 = ax.twinx()
        if self._force_lambdac_0:
            f = lambda _id, _ispec, _vt0:\
                sEKVModel.model_ID_vs_VG(_id, n=self._n, ispec=_ispec,
                                         lambdac=0.0, vt0=_vt0, temperature=self.T)
            res = curve_fit(f,
                            xdata=self.ID,
                            ydata=self.VG,
                            p0=[self.Ispec, self._initial_vt0],
                            bounds=([0.0, -np.inf], [np.inf, np.inf]),
                            method=self._opt_method
                            )
            lambdac = 0.0
            ispec, vt0 = res[0]
        else:
            f = lambda _id, _ispec, _lc, _vt0:\
                sEKVModel.model_ID_vs_VG(_id, n=self._n, ispec=_ispec,
                                         lambdac=_lc, vt0=_vt0, temperature=self.T)
            res = curve_fit(f,
                            xdata=self.ID,
                            ydata=self.VG,
                            p0=[self.Ispec, self.lambdac, self._initial_vt0],
                            bounds=([0.0, 0.0, -np.inf], [np.inf, 1.0, np.inf]),
                            method=self._opt_method
                            )
            ispec, lambdac, vt0 = res[0]
        self.set_Ispec(ispec)
        self.set_lambdac(lambdac)
        self.set_Vt0(vt0)
        log.info("The `Ispec`, `lambdac`, and `Vt0` have been optimized "
                 "with the value of %.3e A, %.3f, %.3f V." % (self.Ispec, self.lambdac, self.Vt0))

        self._VG_m = self.get_sim_VG()

        ln1 = ax.semilogy(self.VG, self.ID, 'ro', label='Data (log)')
        ln2 = ax2.plot(self.VG, self.ID, 'r>', label='Data (linear)')
        ln3 = ax.semilogy(self.VG_m, self.ID, 'k--', label='EKV')
        ax.set_xlabel('$V_{G}$ [V]')
        ax.set_ylabel('$I_D$ [A]')

        ax.text(0.95, 0.05, self.readable_ekv4params,
                transform=ax.transAxes, ha='right', va='bottom',
                bbox=self.__class__._bbox_style)
        ax2.plot(self.VG_m, self.ID, 'k--')
        lns = ln1 + ln2 + ln3
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc=2)
        ax2.set_ylabel('$I_D$ [A]')

    def _get_bound_of_Ispec_range(self, vth_tol: float, intercept: float):

        vth_dev = vth_tol / (self.n * self.Ut)
        up_it = intercept + abs(vth_dev)
        down_it = intercept - abs(vth_dev)

        up_ispec = np.exp(up_it) * self.n * self.Ut
        down_ispec = np.exp(down_it) * self.n * self.Ut

        return up_ispec, down_ispec

    def _refine_Ispec_and_lambdac(self):
        region = np.where(self.VG < (self._Vt0 - self._Vt0_offset))
        vg_minus_vt0 = self.VG[region] - self.Vt0
        Gm = self.Gm[region]
        c = 1.0 / (self._n * self.Ut)
        y = np.log(Gm)

        intercept = np.nanmean(y - c * vg_minus_vt0)
        ispec = np.exp(intercept) / c
        self.set_Ispec(ispec)
        log.info('The `Ispec` is re-extracted from the subthreshold region with '
                 'the value of %.3e A' % self.Ispec)
        fit_y = c * vg_minus_vt0 + intercept

        # setup plot
        ax = self.progress_fig.add_subplot(224)
        ax.set_title("(d)", x=-0.1, y=-0.2)
        # ax.set_ylim(0.06, 3)
        axs_loc = self._insert_ax_loc
        axs = ax.inset_axes(axs_loc)
        axs.plot(vg_minus_vt0, y, 'ro')
        axs.plot(vg_minus_vt0, fit_y, 'k--', label='Fit with fixed slope')
        axs.text(0.95, 0.05, '$I_{spec}$ = %.3e [A]' % ispec,
                 ha="right", va="bottom",
                 transform=axs.transAxes,
                 # bbox=self.__class__._bbox_style,
                 fontsize=6)
        axs.set_xlabel('$V_{G}$-$V_{T0}$ [V]', fontsize=6)
        axs.set_ylabel('$ln$ $G_m$', fontsize=6)
        axs.set_xticks([])
        axs.set_yticks([])

        GmnUt_id = self.Gm_over_ID * self.Ut * self._n

        # re-optimize lambdac
        if self._force_lambdac_0:
            self.set_lambdac(0.)
            if self._vth_tol > 0.0:
                up_ispec, down_ispec = self._get_bound_of_Ispec_range(
                    vth_tol=self._vth_tol, intercept=float(intercept))
                fit_func = lambda _id, _ispec: sEKVModel.model_gms_over_IC_vs_IC(
                    _id, lambdac=0.0, ispec=_ispec)
                res = curve_fit(fit_func,
                                xdata=self.ID,
                                ydata=GmnUt_id,
                                p0=[self.Ispec],
                                loss='cauchy',
                                f_scale=0.01,
                                bounds=([down_ispec], [up_ispec]),
                                method=self._opt_method)
                ispec = res[0][0]
                self.set_Ispec(ispec)
                log.info("The `Ispec` is re-optimized, resulting in %.3e A" % self.Ispec)
        else:
            x, y = self.ID, GmnUt_id
            x = x[~np.isnan(y)]
            y = y[~np.isnan(y)]
            if self._vth_tol > 0.0:
                up_ispec, down_ispec = self._get_bound_of_Ispec_range(
                    vth_tol=self._vth_tol, intercept=float(intercept))
                fit_func = lambda _id, _lc, _ispec: sEKVModel.model_gms_over_IC_vs_IC(
                    _id, _lc, _ispec)
                res = curve_fit(fit_func,
                                xdata=x,
                                ydata=y,
                                p0=[self.lambdac, self.Ispec],
                                loss='cauchy',
                                f_scale=0.02,
                                bounds=([0.0, down_ispec], [1.0, up_ispec]),
                                method=self._opt_method)
                lambdac, ispec = res[0]
                self.set_Ispec(ispec)
                self.set_lambdac(lambdac)
                log.info("The `Ispec` is re-optimized, resulting in %.3e A" % self.Ispec)
                log.info("The `lambdac` is re-optimized, resulting in %.3f " % self.lambdac)

            elif self._vth_tol == 0.0:
                fit_func = lambda _id, _lc: sEKVModel.model_gms_over_IC_vs_IC(_id, _lc, ispec=ispec)
                res = curve_fit(fit_func,
                                xdata=x,
                                ydata=y,
                                p0=[self._lambdac],
                                loss='cauchy',
                                f_scale=0.02,
                                bounds=([0.0], [1.0]),
                                method=self._opt_method)
                lambdac = res[0][0]
                self.set_lambdac(lambdac)
                log.info("The `lambdac` is re-optimized, resulting in %.3f " % self.lambdac)
            else:
                raise ValueError("Tolerance of threshold voltage must be larger than or equal to 0, instead of {}".format(
                    self._vth_tol))

        ax.loglog(self.IC, GmnUt_id, 'ro', label='Data')
        ax.loglog(self.IC, sEKVModel.model_gms_over_IC_vs_IC(self.ID, self.lambdac, self.Ispec),
                  'k--', label='sEKV')
        ax.text(0.03, 0.97,
                '$\lambda_c$ = %.3f \n$I_{spec}$ = %.3e' % (self.lambdac, self.Ispec),
                transform=ax.transAxes, bbox=self._bbox_style,
                ha='left', va='top'
                )
        ax.set_xlabel('$IC$ [-]')
        ax.set_ylabel('$G_m$n$U_T$ / $I_D$')
        ax.set_ylim(1e-2, 1e1)
        ax.legend(loc=1)

    def _refine_Vt0(self):

        f = lambda _id, _vt0: sEKVModel.model_ID_vs_VG(
            _id, n=self._n, ispec=self.Ispec, lambdac=self.lambdac, vt0=_vt0, temperature=self.T)
        res = curve_fit(f,
                        xdata=self.ID,
                        ydata=self.VG,
                        p0=[self.Vt0],
                        bounds=([-np.inf], [np.inf]),
                        method=self._opt_method
                        )
        vt0 = res[0]
        self.set_Vt0(float(vt0))
        self._VG_m = self.get_sim_VG()
        log.info('The `Vt0` is re-optimized in the final step with the value of %.3f V' % self.Vt0)

    def _plot_final_figure(self):
        ax = self.final_fig.add_subplot(111)
        ln1 = ax.semilogy(self.VG, self.ID, 'ro', mfc="none", label='Data (log)')
        ln2 = ax.semilogy(self.VG_m, self.ID, 'k--', label='sEKV')
        ax.set_xlabel('$V_{G}$ [V]')
        ax.set_ylabel('$I_D$ [A]')

        if self.VDS is not None:
            vds_txt = '\n|$V_{DS}$| = %.2f V' % self.VDS
        else:
            vds_txt = ''
        txt = self.readable_ekv4params + vds_txt
        ax.text(0.03, 0.97, txt,
                transform=ax.transAxes,
                ha='left', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        ax2 = ax.twinx()
        ln3 = ax2.plot(self.VG, self.ID, 'r>', mfc="none", label="Data (linear)")
        ax2.plot(self.VG_m, self.ID, 'k--')

        lns = ln1 + ln3 + ln2
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc=4)
        ax2.set_ylabel('$I_D$ [A]')
