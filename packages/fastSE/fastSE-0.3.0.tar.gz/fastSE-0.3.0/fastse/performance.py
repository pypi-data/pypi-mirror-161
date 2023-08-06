# fastSE
# Copyright (C) 2022 Zeyu Mao

import numba as nb
import numpy as np
from numpy import int32, float64


@nb.njit(fastmath=True)
def csr_to_coo(data, indices, indptr):
    row = np.empty(len(data), dtype=int32)
    col = np.empty(len(data), dtype=int32)
    nz = 0
    for i in range(len(indptr) - 1):
        for _ in range(indptr[i], indptr[i+1]):
            row[nz] = i
            col[nz] = indices[nz]
            nz += 1
    return row, col


@nb.njit
def get_index(A, k):  # sourcery skip: use-next
    for i in range(len(A)):
        if A[i] == k:
            return i
    return -1


@nb.njit
def nb_concatenate(*args):
    return np.concatenate(args)


@nb.njit
def diagnoal_max(data, row, col, length):
    diag = np.zeros(length, dtype=float64)
    n = len(data)
    nz = 0
    for i in range(n):
        if row[i, 0] == col[i, 0]:
            diag[nz] = data[i, 0]
            nz += 1
    return max(diag)


@nb.njit
def mul_diags(data, col, diags):
    n = len(data)
    new_data = np.zeros(n, dtype=float64)
    for i in range(n):
        new_data[i] = data[i, 0] * diags[col[i, 0], 0]
    return new_data


@nb.njit
def add_diags(data, row, col, diags):
    n = len(data)
    new_data = np.zeros(n, dtype=float64)
    for i in range(n):
        new_data[i] = data[i, 0]
    for i in range(n):
        if row[i, 0] == col[i, 0]:
            new_data[i] += diags[col[i, 0], 0]
    return new_data


@nb.njit
def cpf_p_jit(Va, Vm, Va_prev, Vm_prev, lam, lam_prev, step, pv, pq):
    mis = 0
    npq = len(pq)
    npv = len(pv)
    for i in range(npq):
        index = pq[i]
        Va_mis = Va[index] - Va_prev[index]
        Vm_mis = Vm[index] - Vm_prev[index]
        mis += Va_mis**2 + Vm_mis**2
    for i in range(npv):
        index = pv[i]
        Va_mis = Va[index] - Va_prev[index]
        mis += Va_mis**2
    mis += (lam - lam_prev)**2
    mis -= step**2
    return mis


@nb.njit
def newton_secant(func, x0, args=(), tol=1.48e-8, maxiter=50,
                  disp=True):
    """
    Find a zero from the secant method using the jitted version of
    Scipy's secant method.

    Note that `func` must be jitted via Numba.

    Parameters
    ----------
    func : callable and jitted
        The function whose zero is wanted. It must be a function of a
        single variable of the form f(x,a,b,c...), where a,b,c... are extra
        arguments that can be passed in the `args` parameter.
    x0 : float
        An initial estimate of the zero that should be somewhere near the
        actual zero.
    args : tuple, optional(default=())
        Extra arguments to be used in the function call.
    tol : float, optional(default=1.48e-8)
        The allowable error of the zero value.
    maxiter : int, optional(default=50)
        Maximum number of iterations.
    disp : bool, optional(default=True)
        If True, raise a RuntimeError if the algorithm didn't converge.

    """

    if tol <= 0:
        raise ValueError("tol is too small <= 0")
    if maxiter < 1:
        raise ValueError("maxiter must be greater than 0")

    # Convert to float (don't use float(x0); this works also for complex x0)
    p0 = 1.0 * x0
    status = False

    # Secant method
    p1 = x0 * (1 + 1e-4) + 1e-4 if x0 >= 0 else x0 * (1 + 1e-4) - 1e-4
    q0 = func(p0, *args)
    q1 = func(p1, *args)
    for itr in range(maxiter):
        if q1 == q0:
            p = (p1 + p0) / 2.0
            status = True
            break
        else:
            p = p1 - q1 * (p1 - p0) / (q1 - q0)
        if np.abs(p - p1) < tol:
            status = True
            break
        p0 = p1
        q0 = q1
        p1 = p
        q1 = func(p1, *args)

    if disp and status == False:
        msg = "Failed to converge"
        raise RuntimeError(msg)

    return p, itr + 1, status

