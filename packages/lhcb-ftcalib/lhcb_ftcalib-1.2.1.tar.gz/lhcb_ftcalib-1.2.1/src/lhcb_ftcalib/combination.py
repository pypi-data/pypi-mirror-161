import numpy as np
import pandas as pd
from numba import jit


@jit(nopython=True)
def _combine_taggers(decs, omegas, gradients = None, npars=None):
    # events with omega > 0.5 do not contribute with information in combinations
    if gradients is not None:
        assert npars is not None, "A list of parameters numbers per tagger needs to passed as npars argument"

    for t, omega in enumerate(omegas):
        ignore = (omega > 0.5) + (omega < 0)
        omegas[t][ignore] = 0.5
        decs[t][ignore] = 0
        if gradients is not None:
            for i, ign in enumerate(ignore):
                if ign:
                    gradients[t][0][i * npars[t]:(i + 1) * npars[t]] = 0

    # Tagger combination algorithm
    NT = len(omegas)
    Nt = len(omegas[0])
    p_b    = np.array([np.prod((1 + decs[i]) / 2 - decs[i] * (1 - omegas[i])) for i in range(NT)])
    p_bbar = np.array([np.prod((1 - decs[i]) / 2 + decs[i] * (1 - omegas[i])) for i in range(NT)])
    P_b = p_b / (p_b + p_bbar)

    if gradients is not None:
        Jw = gradients
        Jp = np.empty((NT, 2, Nt))
        JP = np.empty((NT, 1, 2))
        JpJw = np.empty((NT, 2, np.sum(npars)))
        JPJpJw = np.empty((NT, 1, np.sum(npars)))
        for i in range(NT):
            for k in range(Nt):
                Jp[i, 0, k] = np.prod(np.array([((1 + decs[i][j]) / 2 - decs[i][j] * (1 - omegas[i][j]) if (k != j) else (+1) * decs[i][j]) for j in range(Nt)]))
                Jp[i, 1, k] = np.prod(np.array([((1 - decs[i][j]) / 2 + decs[i][j] * (1 - omegas[i][j]) if (k != j) else (-1) * decs[i][j]) for j in range(Nt)]))
            JP[i, 0, 0] = p_bbar[i] / (p_b[i] + p_bbar[i])**2
            JP[i, 0, 1] = -  p_b[i] / (p_b[i] + p_bbar[i])**2
            JpJw[i]   = Jp[i] @ Jw[i]
            JPJpJw[i] = JP[i] @ JpJw[i]

    dec_minus = P_b > 1 - P_b
    dec_plus  = P_b < 1 - P_b

    d_combined = np.zeros(len(decs))
    d_combined[dec_minus] = -1
    d_combined[dec_plus]  = +1

    omega_combined = 0.5 * np.ones(len(decs))
    omega_combined[dec_minus] = 1 - P_b[dec_minus]
    omega_combined[dec_plus]  = P_b[dec_plus]

    if gradients is not None:
        grad_combined = JPJpJw
        grad_combined[dec_minus] = -1 * grad_combined[dec_minus]
        grad_combined[dec_plus]  = +1 * grad_combined[dec_plus]
    else:
        grad_combined = None

    return d_combined, omega_combined, grad_combined


def _correlation(taggers, corrtype="dec_weight", selected=True, calibrated=False):
    @jit(nopython=True)
    def corr(X, Y, W):
        Neff = np.sum(W)
        avg_X = np.sum(X * W) / Neff
        avg_Y = np.sum(Y * W) / Neff
        Xres = X - avg_X
        Yres = Y - avg_Y
        covXY = np.sum(W * Xres * Yres) / Neff
        covXX = np.sum(W * Xres * Xres) / Neff
        covYY = np.sum(W * Yres * Yres) / Neff
        return covXY / np.sqrt(covXX * covYY)

    N = len(taggers)
    m_corr = np.ones((N, N)) * -999  # If something is not filled, show -999

    class getter:
        def __init__(self, stats):
            self.stats = stats

        def __call__(self, tagger, attr):
            return np.array(getattr(getattr(tagger, self.stats)._full_data, attr)[getattr(tagger, self.stats)._full_data.selected])

    get = getter("stats")

    for x, TX in enumerate(taggers):
        for y, TY in enumerate(taggers[x:]):
            if TX.name == TY.name:
                m_corr[x][x + y] = 1
                continue
            if calibrated:
                assert TY.is_calibrated()
            if corrtype == "fire":
                try:
                    m_corr[x][x + y] = corr(np.abs(get(TX, "dec")),
                                            np.abs(get(TY, "dec")),
                                            get(TX, "weight"))
                except ZeroDivisionError:
                    m_corr[x][x + y] = np.nan
            elif corrtype == "dec":
                m_corr[x][x + y] = corr(get(TX, "dec"),
                                        get(TY, "dec"),
                                        get(TX, "weight"))
            elif corrtype == "dec_weight":
                m_corr[x][x + y] = corr(get(TX, "dec") * (1 - 2 * get(TX, "eta")),
                                        get(TY, "dec") * (1 - 2 * get(TY, "eta")),
                                        get(TX, "weight"))
            elif corrtype == "both_fire":
                d1 = get(TX, "dec")
                d2 = get(TY, "dec")
                mask = (d1 != 0) & (d2 != 0)
                m_corr[x][x + y] = corr(d1[mask], d2[mask], get(TX, "weight")[mask])

            m_corr[x + y][x] = m_corr[x][x + y]

    names = [tagger.name for tagger in taggers]
    m_corr = pd.DataFrame({name : m_corr[n] for n, name in enumerate(names)}, index = names)
    return m_corr
