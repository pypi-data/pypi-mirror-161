# fastSE
# Copyright (C) 2022 Zeyu Mao

import numpy as np
import numba as nb
from numpy import complex128
from numpy import conj, zeros


@nb.njit(fastmath=True)
def dSft_dVa_numba(spVx, spVp, spVi, Yx, Yp, Yi, V, Vft, I):
    n = len(Yp) - 1
    dS_dVa = Yx.copy()
    buffer = Yx.copy()
    for j in range(n):  # for each column ...
        for k in range(Yp[j], Yp[j + 1]):  # for each row ...
            # row index
            dS_dVa[k] = Yx[k] * V[j]
            buffer[k] = spVx[k] * conj(I[j])

    for j in range(n):
        for k in range(Yp[j], Yp[j + 1]):  # for each row ...
            buffer[k] = 1j * buffer[k]
            temp = 1j * Vft[j]
            dS_dVa[k] = conj(dS_dVa[k])
            dS_dVa[k] *= temp
            dS_dVa[k] = buffer[k] - dS_dVa[k]
    return dS_dVa


@nb.njit(fastmath=True)
def dSft_dVm_numba(spVx, spVp, spVi, Yx, Yp, Yi, Vnorm, Vft, I):
    n = len(Yp) - 1
    dS_dVm = Yx.copy()
    buffer = Yx.copy()
    for j in range(n):  # for each column ...
        for k in range(Yp[j], Yp[j + 1]):  # for each row ...
            # row index
            dS_dVm[k] = Yx[k] * Vnorm[j]
            buffer[k] = spVx[k] * conj(I[j])

    for j in range(n):
        for k in range(Yp[j], Yp[j + 1]):  # for each row ...
            dS_dVm[k] = buffer[k] + conj(dS_dVm[k]) * Vft[j]
    return dS_dVm


@nb.njit
def dI_dVa_numba(Yx, Yp, Yi, V):
    n = len(Yp) - 1
    dI_dVa = Yx.copy()
    for j in range(n):  # for each column ...
        for k in range(Yp[j], Yp[j + 1]):  # for each row ...
            # row index
            dI_dVa[k] = Yx[k] * 1j * V[j]
    return dI_dVa


@nb.njit
def dI_dVm_numba(Yx, Yp, Yi, Vnorm):
    n = len(Yp) - 1
    dI_dVm = Yx.copy()
    for j in range(n):  # for each column ...
        for k in range(Yp[j], Yp[j + 1]):  # for each row ...
            # row index
            dI_dVm[k] = Yx[k] * Vnorm[j]
    return dI_dVm


def dSbr_dV_coo(Yf, Yt, V, f, t, *args):
    Vnorm = V / abs(V)

    # compute currents
    If = Yf * V
    It = Yt * V

    diagVf = args[0]
    diagIf = args[1]
    diagVt = args[2]
    diagIt = args[3]
    diagV = args[4]
    diagVnorm = args[5]
    spVf = args[6]
    spVt = args[7]
    spVnf = args[8]
    spVnt = args[9]
    diagVf.data = V[f]

    diagIf.data = If
    diagVt.data = V[t]
    diagIt.data = It
    diagV.data = V
    diagVnorm.data = Vnorm

    # Partial derivative of S w.r.t voltage phase angle.
    spVf.data = V[f]
    spVt.data = V[t]
    spVnf.data = Vnorm[f]
    spVnt.data = Vnorm[t]

    dSf_dVa = dSft_dVa_numba(spVf.data, spVf.indptr, spVf.indices, Yf.data, Yf.indptr, Yf.indices, V, V[f], If)
    dSt_dVa = dSft_dVa_numba(spVt.data, spVt.indptr, spVt.indices, Yt.data, Yt.indptr, Yt.indices, V, V[t], It)

    # Partial derivative of S w.r.t. voltage amplitude.
    dSf_dVm = dSft_dVm_numba(spVnf.data, spVnf.indptr, spVnf.indices, Yf.data, Yf.indptr, Yf.indices, Vnorm, V[f], If)
    dSt_dVm = dSft_dVm_numba(spVnt.data, spVnt.indptr, spVnt.indices, Yt.data, Yt.indptr, Yt.indices, Vnorm, V[t], It)

    # Compute power flow vectors.
    Sf = V[f] * conj(If)
    St = V[t] * conj(It)

    return dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St



def dIbr_dV_coo(Yf, Yt, V, diagV, diagVnorm):
    nb = len(V)
    ib = np.arange(nb)

    Vnorm = V / np.abs(V)

    diagV.data = V
    diagVnorm.data = Vnorm

    dIf_dVa = dI_dVa_numba(Yf.data, Yf.indptr, Yf.indices, V)
    dIt_dVa = dI_dVa_numba(Yt.data, Yt.indptr, Yt.indices, V)
    dIf_dVm = dI_dVm_numba(Yf.data, Yf.indptr, Yf.indices, Vnorm)
    dIt_dVm = dI_dVm_numba(Yt.data, Yt.indptr, Yt.indices, Vnorm)

    # Compute currents.
    If = Yf * V
    It = Yt * V

    return dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It

