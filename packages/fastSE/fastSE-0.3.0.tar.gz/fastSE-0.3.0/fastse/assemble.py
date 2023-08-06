# fastSE
# Copyright (C) 2022 Zeyu Mao

import numpy as np
import numba as nb
from numpy import int32, float64, complex128
from numpy import zeros, conj, empty
from fastse.performance import get_index, csr_to_coo
from kvxopt import spmatrix
# Import corresponding AOT/JIT functions
from os.path import dirname, abspath
import sys
import platform
import warnings
import importlib
PYTHON_VERSION = platform.python_version_tuple()
sys.path.append(abspath(dirname(__file__)))
# print(abspath(dirname(__file__)))
pc = importlib.import_module(f"precompile3{PYTHON_VERSION[1]}")


@nb.njit
def construct_H_full(Yx, Yp, Yj, V, Vnorm, p_inj_idx, q_inj_idx, vm_m_idx, pvpq):
    # Yp = Ybus.indptr
    # Yj = Ybus.indices

    # init buffer vector
    Ibus = zeros(len(V), dtype=complex128)
    buffer = zeros(len(V), dtype=complex128)
    dS_dVm = Yx.copy()
    dS_dVa = Yx.copy()
    length = len(dS_dVm)
    Ybus_row = zeros(length, dtype=int32)
    Ybus_col = zeros(length, dtype=int32)
    nz = 0

    # iterate through sparse matrix
    for r in range(len(Yp) - 1):
        for k in range(Yp[r], Yp[r + 1]):
            # Ibus = Ybus * V
            buffer[r] += Yx[k] * V[Yj[k]]
            # Ybus * diag(Vnorm)
            dS_dVm[k] *= Vnorm[Yj[k]]
            # Ybus * diag(V)
            dS_dVa[k] *= V[Yj[k]]

        Ibus[r] += buffer[r]

        # conj(diagIbus) * diagVnorm
        buffer[r] = conj(buffer[r]) * Vnorm[r]

    for r in range(len(Yp) - 1):
        for k in range(Yp[r], Yp[r + 1]):
            # diag(V) * conj(Ybus * diagVnorm)
            dS_dVm[k] = conj(dS_dVm[k]) * V[r]

            if r == Yj[k]:
                # diagonal elements
                dS_dVa[k] = -Ibus[r] + dS_dVa[k]
                dS_dVm[k] += buffer[r]

            # 1j * diagV * conj(diagIbus - Ybus * diagV)
            dS_dVa[k] = conj(-dS_dVa[k]) * (1j * V[r])

            # save to coo
            Ybus_row[nz] = r
            Ybus_col[nz] = Yj[nz]
            nz += 1

    # now assemble
    if len(p_inj_idx) == len(q_inj_idx):  # assume p_inj and q_inj are identical
        nz = 0
        nzb = 0
        npvpq = len(pvpq)
        npinj = len(p_inj_idx)
        nvm = len(vm_m_idx)
        h21_data = np.empty(length, dtype=float64)
        h22_data = np.empty(length, dtype=float64)
        h21_row = np.empty(length, dtype=int32)
        h22_row = np.empty(length, dtype=int32)
        h21_col = np.empty(length, dtype=int32)
        h22_col = np.empty(length, dtype=int32)
        h41_data = np.empty(length, dtype=float64)
        h42_data = np.empty(length, dtype=float64)
        h41_row = np.empty(length, dtype=int32)
        h42_row = np.empty(length, dtype=int32)
        h41_col = np.empty(length, dtype=int32)
        h42_col = np.empty(length, dtype=int32)
        h6_data = np.empty(nvm, dtype=float64)
        h6_row = np.empty(nvm, dtype=int32)
        h6_col = np.empty(nvm, dtype=int32)

        for i in range(length):
            idxr = get_index(p_inj_idx, Ybus_row[i])
            if idxr >= 0:
                h22_data[nz] = dS_dVm[i].real
                h42_data[nz] = dS_dVm[i].imag
                h22_row[nz] = idxr
                h22_col[nz] = Ybus_col[i]
                h42_row[nz] = idxr
                h42_col[nz] = Ybus_col[i]

                # find the index in pvpq
                idxc = get_index(pvpq, Ybus_col[i])
                if idxc >= 0:
                    h21_data[nzb] = dS_dVa[i].real
                    h41_data[nzb] = dS_dVa[i].imag
                    h21_row[nzb] = idxr
                    h21_col[nzb] = idxc
                    h41_row[nzb] = idxr
                    h41_col[nzb] = idxc
                    nzb += 1
                nz += 1

        for i in range(nvm):
            h6_data[i] = 1
            h6_row[i] = 2 * npinj + i
            h6_col[i] = npvpq + vm_m_idx[i]

        h21_data = h21_data[:nzb]
        h21_row = h21_row[:nzb]
        h21_col = h21_col[:nzb]
        h22_data = h22_data[:nz]
        h22_row = h22_row[:nz]
        h22_col = h22_col[:nz] + npvpq
        h41_data = h41_data[:nzb]
        h41_row = h41_row[:nzb] + npinj
        h41_col = h41_col[:nzb]
        h42_data = h42_data[:nz]
        h42_row = h42_row[:nz] + npinj
        h42_col = h42_col[:nz] + npvpq
        total_length = nzb + nzb + nz + nz

        h_data = np.empty(total_length, dtype=float64)
        h_row = np.empty(total_length, dtype=int32)
        h_col = np.empty(total_length, dtype=int32)
        h_data[:nzb] = h21_data
        h_data[nzb:nzb + nz] = h22_data
        h_data[nzb + nz:nzb + nz + nzb] = h41_data
        h_data[nzb + nz + nzb:total_length] = h42_data
        h_row[:nzb] = h21_row
        h_row[nzb:nzb + nz] = h22_row
        h_row[nzb + nz:nzb + nz + nzb] = h41_row
        h_row[nzb + nz + nzb:total_length] = h42_row
        h_col[:nzb] = h21_col
        h_col[nzb:nzb + nz] = h22_col
        h_col[nzb + nz:nzb + nz + nzb] = h41_col
        h_col[nzb + nz + nzb:total_length] = h42_col
        h_data = np.concatenate((h_data, h6_data))
        h_row = np.concatenate((h_row, h6_row))
        h_col = np.concatenate((h_col, h6_col))
    return h_data, h_row, h_col


def AC_jacobian(Ybus, V, pvpq, pq, npv, npq):
    """
    Create the AC Jacobian function with no embedded controls
    :param Ybus: Ybus matrix in CSC format
    :param V: Voltages vector
    :param pvpq: array of pv|pq bus indices
    :param pq: array of pq indices
    :param npv: number of pv buses
    :param npq: number of pq buses
    :return: Jacobian Matrix in COO format
    """

    pvpq_lookup = np.zeros(Ybus.shape[0], dtype=int)
    pvpq_lookup[pvpq] = np.arange(len(pvpq))

    Ibus = zeros(len(V), dtype=complex128)

    # create Jacobian from fast calc of dS_dV
    dS_dVm, dS_dVa = pc.dSbus_dV_numba_sparse(Ybus.data, Ybus.indptr, Ybus.indices, V, V / abs(V), Ibus)

    # data in J, space pre-allocated is bigger than actual Jx -> will be reduced later on
    Jx = empty(len(dS_dVm) * 4, dtype=float)

    # row pointer, dimension = pvpq.shape[0] + pq.shape[0] + 1
    Jp = zeros(pvpq.shape[0] + pq.shape[0] + 1, dtype=int32)

    # indices, same with the pre-allocated space (see Jx)
    Jj = empty(len(dS_dVm) * 4, dtype=int32)

    # create jacobian in COO order
    data, row, col = pc.create_J(dS_dVm, dS_dVa, Ybus.indptr, Ybus.indices, pvpq_lookup, pvpq, pq, Jx, Jj, Jp)

    # generate scipy sparse matrix
    nj = npv + npq + npq

    return spmatrix(data, row, col, size=(nj, nj))


@nb.njit
def create_J_cpf(dVm_x, dVa_x, Yp, Yj, pvpq_lookup, pvpq, pv, pq, Jx, Jj, Jp, Sxfr, V, lam, Vprv,
                 lamprv):  # pragma: no cover

    # get length of vectors
    npvpq = len(pvpq)
    npq = len(pq)
    npv = npvpq - npq
    size = npvpq + npq + 1

    Va = np.angle(V)
    Vm = np.abs(V)
    Vaprv = np.angle(Vprv)
    Vmprv = np.abs(Vprv)

    if lam == lamprv:  # first step
        dP_dlam = 1.0  # avoid singular Jacobian that would result from [dP_dV, dP_dlam] = 0
    else:
        dP_dlam = 2.0 * (lam - lamprv)

    # nonzeros in J
    nnz = 0

    # iterate rows of J
    # first iterate pvpq (J11 and J12) (dP_dVa, dP_dVm)
    for r in range(npvpq):

        # nnzStar is necessary to calculate nonzeros per row
        nnzStart = nnz

        # iterate columns of J11 = dS_dVa.real at positions in pvpq
        # check entries in row pvpq[r] of dS_dV
        for c in range(Yp[pvpq[r]], Yp[pvpq[r] + 1]):
            # check if column Yj is in pvpq
            cc = pvpq_lookup[Yj[c]]

            # entries for J11 and J12
            if pvpq[cc] == Yj[c]:
                # entry found
                # equals entry of J11: J[r,cc] = dS_dVa[c].real
                Jx[nnz] = dVa_x[c].real
                Jj[nnz] = cc
                nnz += 1

                # if entry is found in the "pq part" of pvpq = add entry of J12
                if cc >= npv:
                    Jx[nnz] = dVm_x[c].real
                    Jj[nnz] = cc + npq
                    nnz += 1

        # Add dF_dlam to the last column
        Jx[nnz] = -Sxfr[pvpq[r]].real
        Jj[nnz] = size - 1
        nnz += 1

        # Jp: number of nonzeros per row = nnz - nnzStart (nnz at begging of loop - nnz at end of loop)
        Jp[r + 1] = nnz - nnzStart + Jp[r]

    # second: iterate pq (J21 and J22) (dQ_dVa, dQ_dVm)
    for r in range(npq):
        nnzStart = nnz
        # iterate columns of J21 = dS_dVa.imag at positions in pvpq
        for c in range(Yp[pq[r]], Yp[pq[r] + 1]):
            cc = pvpq_lookup[Yj[c]]
            if pvpq[cc] == Yj[c]:
                # entry found
                # equals entry of J21: J[r + lpvpq, cc] = dS_dVa[c].imag
                Jx[nnz] = dVa_x[c].imag
                Jj[nnz] = cc
                nnz += 1

                if cc >= npv:
                    # if entry is found in the "pq part" of pvpq = Add entry of J22
                    Jx[nnz] = dVm_x[c].imag
                    Jj[nnz] = cc + npq
                    nnz += 1

        # Add dF_dlam to the last column
        Jx[nnz] = -Sxfr[pq[r]].imag
        Jj[nnz] = size - 1
        nnz += 1

        # Jp: number of nonzeros per row = nnz - nnzStart (nnz at begging of loop - nnz at end of loop)
        Jp[r + npvpq + 1] = nnz - nnzStart + Jp[r + npvpq]

    # thid: add dp_dv to the last row
    for r in range(npvpq):
        Jx[nnz] = 2.0 * (Va[pvpq[r]] - Vaprv[pvpq[r]])
        Jj[nnz] = r
        nnz += 1
    for r in range(npq):
        Jx[nnz] = 2.0 * (Vm[pvpq[r]] - Vmprv[pvpq[r]])
        Jj[nnz] = r + npvpq
        nnz += 1
    Jx[nnz] = dP_dlam
    Jj[nnz] = size - 1
    nnz += 1
    Jp[npq + npvpq + 1] = Jp[npq + npvpq] + size

    # fourth: convert to coo
    row = np.empty(nnz, dtype=int32)
    col = np.empty(nnz, dtype=int32)
    nz = 0
    for i in range(len(Jp) - 1):
        for c in range(Jp[i], Jp[i + 1]):
            row[nz] = i
            col[nz] = Jj[nz]
            nz += 1
    return Jx[:nnz], row, col


def cpf_jacobian(Ybus, V, pvpq, pv, pq, npv, npq, Sxfr, lam, Vprv, lamprv):
    """
    Create the AC Jacobian function with no embedded controls
    :param Ybus: Ybus matrix in CSC format
    :param V: Voltages vector
    :param pvpq: array of pv|pq bus indices
    :param pq: array of pq indices
    :param npv: number of pv buses
    :param npq: number of pq buses
    :return: Jacobian Matrix in COO format
    """

    pvpq_lookup = np.zeros(Ybus.shape[0], dtype=int)
    pvpq_lookup[pvpq] = np.arange(len(pvpq))

    Ibus = zeros(len(V), dtype=complex128)
    nj = npv + npq + npq + 1

    # create Jacobian from fast calc of dS_dV
    dS_dVm, dS_dVa = pc.dSbus_dV_numba_sparse(Ybus.data, Ybus.indptr, Ybus.indices, V, V / abs(V), Ibus)

    # data in J, space pre-allocated is bigger than actual Jx -> will be reduced later on
    Jx = empty(len(dS_dVm) * 4 + 2*nj, dtype=float)

    # row pointer, dimension = pvpq.shape[0] + pq.shape[0] + 1
    Jp = zeros(pvpq.shape[0] + pq.shape[0] + 2, dtype=int32)

    # indices, same with the pre-allocated space (see Jx)
    Jj = empty(len(dS_dVm) * 4 + 2*nj, dtype=int32)

    # fill Jx, Jj and Jp in CSR order
    data, row, col = create_J_cpf(dS_dVm, dS_dVa, Ybus.indptr, Ybus.indices, pvpq_lookup, pvpq, pv, pq, Jx, Jj, Jp,
                                  Sxfr, V, lam, Vprv, lamprv)

    # generate scipy sparse matrix

    return spmatrix(data, row, col, size=(nj, nj))