import numpy as np


def remove_log_is_nan(i: np.ndarray, *vs) -> tuple:
    """Remove values that log10(i) is nan from an array."""
    log_i = np.log10(i)
    loc = np.where(~np.isnan(log_i))
    if vs:
        vs = list(vs)
        for index, v in enumerate(vs):
            vs[index] = v[loc]
        return i[loc], vs
    else:
        return i[loc]


def get_savgol_win_num(data_len: int, frac: float) -> int:
    if 0 < frac < 1:
        win = int(data_len * frac)
        if not win % 2:  # len_win is even
            win += 1
        return win
    else:
        raise ValueError('The argument frac must between 0 and 1.')