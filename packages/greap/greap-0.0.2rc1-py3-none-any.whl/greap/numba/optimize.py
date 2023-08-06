from numba import njit, prange
from numba.typed import Dict
from numba.core import types


@njit(parallel=True, fastmath=True)
def accumulate_profits(
    times, open_ats, close_ats, open_prices, close_prices, quantites, symbols, prices
):
    signal = Dict.empty(key_type=types.float64, value_type=types.float64)
    T = len(times)
    N = len(open_ats)
    for i in range(T):
        s = 0.0
        t = times[i]
        for j in prange(N):
            if open_ats[j] <= t and (t < close_ats[j]):
                s += (prices[symbols[j]][t] - open_prices[j]) * quantites[j]
            elif open_ats[j] <= t:
                s += (close_prices[j] - open_prices[j]) * quantites[j]
        signal[t] = s
    return signal


@njit(parallel=True, fastmath=True)
def accumulate_investeds(
    times, open_ats, close_ats, open_prices, close_prices, quantites, symbols, prices
):
    signal = Dict.empty(key_type=types.float64, value_type=types.float64)
    N = len(open_ats)

    for t in times:
        s = 0.0
        for j in prange(N):
            # TODO: accomodate short positions as well
            if open_ats[j] <= t and t < close_ats[j]:
                s += prices[symbols[j]][t] * quantites[j]
        signal[t] = s
    return signal
