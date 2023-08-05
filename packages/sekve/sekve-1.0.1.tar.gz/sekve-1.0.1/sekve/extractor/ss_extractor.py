import logging
import numpy as np
from matplotlib.ticker import FormatStrFormatter
from scipy.signal import savgol_filter
from typing import Union
from matplotlib import pyplot as plt

from sekve.model import sEKVModel
from sekve.utils import remove_log_is_nan, get_savgol_win_num


def select_ss(ls: list, t, ss) -> np.ndarray:
    # check ls
    last_t2 = None
    for l in ls:
        t1, next_t2 = l[:2]

        if last_t2 is None:
            last_t2 = next_t2
            continue
        else:
            if t1 != last_t2:
                raise ValueError("Temperature is discontinued.")
            else:
                last_t2 = next_t2

    # Define limitation
    low_ss, up_ss = None, None
    for l in ls:
        t1, t2, low_ss, up_ss = l
        if low_ss == "auto":
            low_ss = sEKVModel.get_thermal_voltage(t) * np.log(10) * 1. * 1e3
        if up_ss == "auto":
            up_ss = sEKVModel.get_thermal_voltage(t) * np.log(10) * 2 * 1e3

        if (t1 is not None) & (t2 is not None):
            if (t1 <= t) & (t < t2):
                break
        if (t1 is None) & (t2 is not None):
            if t < t2:
                break
        if (t1 is not None) & (t2 is None):
            if t1 <= t:
                break

    if (low_ss is None) or (up_ss is None):
        raise ValueError("Limitation is not defined")

    loc = np.where((ss <= up_ss) & (ss >= low_ss))
    return loc


def extract_ss(v: np.ndarray,
               i: np.ndarray,
               t: float,
               exp_val: Union[list, str, None] = "auto",
               method: str = "savgol",
               frac: float = 0.2,
               max_id: float = None,
               min_id: float = None,
               take_val: str = "min",
               show: bool = False,
               return_crit_v: bool = False,
               ylim=(0, 200)
               ) -> Union[float, tuple]:
    """Extract subthreshold swing.

    :param v: gate voltage..
    :param i: drain current.
    :param t: temperature in Kelvin.
    :param exp_val: Optional. Expected value of ss depending on temperature.
        [[t1, t2, ss1, ss2], [], ...]
    :param method: Optional, ['savgol', 'poly']
    :param frac: Optional. Fraction of filter windows data length to entire data length.
        This parameter only attributes to method 'savgol'.
    :param max_id: Optional. Upper limitation of current.
    :param min_id: Optional. Lower limitation of current.
    :param take_val: Optional. ["min", "avg"]
    :param show: If Ture, show the extraction.
    :param return_crit_v: If True, return critical voltage.
    :param ylim: limitation of ss in mV/dec
    """
    i, v = remove_log_is_nan(i, v)
    v = v[0]
    log_i = np.log10(i)
    ss = 1. / np.gradient(log_i, v)
    ss *= 1e3
    if exp_val == "auto":
        exp_val = [
            [None, 50, 0, 20],
            [50, 300, "auto", "auto"],
        ]
        loc = select_ss(exp_val, t, ss)
    elif exp_val is None:
        loc = slice(None, None)
    else:
        loc = select_ss(exp_val, t, ss)

    if method == "savgol":
        x = i[loc]
        y = ss[loc]
        _v = v[loc]
        y, x = remove_log_is_nan(y, x)
        x = x[0]
        if max_id and min_id:
            m = np.where((x <= max_id) & (min_id <= x))
        elif max_id and not min_id:
            m = np.where(x <= max_id)
        elif min_id and not max_id:
            m = np.where(x >= min_id)
        else:
            m = slice(None, None)
        x = x[m]
        y = y[m]
        _v = v[m]

        len_win = get_savgol_win_num(len(x), frac)
        fit_ss = None
        try:
            fit_ss = savgol_filter(y, len_win, 2)
        except ValueError:
            if take_val == "min":
                s = np.min(y)
            elif take_val == "avg":
                s = np.average(y)
            else:
                raise ValueError
            resy = (y - s) ** 2
            wh = np.where(resy == min(resy))
        else:
            if take_val == "min":
                s = np.min(fit_ss)
            elif take_val == "avg":
                s = np.average(fit_ss)
            else:
                raise ValueError
            sq_dev = (fit_ss - s) ** 2
            wh = np.where(sq_dev == min(sq_dev))

        # Define critlcal voltage
        vc = _v[wh]
    else:
        raise ValueError("The n extracting method {} is not recognized.".format(method))

    if show:
        fig, ax = plt.subplots()
        ax.semilogx(i, ss, c="r", marker="o", mfc="none",
                    linestyle="", label="raw data")
        if fit_ss is not None:
            ax.semilogx(x, fit_ss, "b+", label="filtered data")
        else:
            ax.semilogx(x, y, "b+", label="selected data")
        ax.axhline(y=s, c="k", label="extracted SS")
        theo_ss = sEKVModel.get_thermal_voltage(t) * np.log(10) * 1e3
        ax.axhline(y=theo_ss, c="grey", label="Theoretical SS")
        ax.set_xlabel("$I_D$ [A]")
        ax.set_ylabel("SS [mV/dec]")
        ax.set_ylim(*ylim)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        # ax.set_yticks([0, 10, 20, 30, 40, 60, 80, 100])

        txt = [f"T = {t} K",
               "$SS_{ext}$ = %.1f mV/dec" % s,
               "$SS_{theo}$ = %.1f mV/dec" % theo_ss,
               "$n$ = %.2f" % (s / theo_ss)
               ]
        ax.text(0.03, 0.95, s="\n".join(txt),
                transform=ax.transAxes, va="top", ha="left")
        ax.legend(loc=4)
        fig.tight_layout()
        fig.show()
    if return_crit_v:
        return float(s), vc
    else:
        return float(s)
