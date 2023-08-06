import os
import sys
import numpy as np
from numpy import complex128
from numba import njit, config
from collections import namedtuple
from scipy.sparse import csr_matrix
from scipy.optimize import newton
from fastse.pf import nrpf
from fastse.helper import generate_admittance_matrix
from plum import dispatch
# Import corresponding AOT/JIT functions
from os.path import dirname, abspath
import platform
import warnings
import importlib
PYTHON_VERSION = platform.python_version_tuple()
sys.path.append(abspath(dirname(__file__)))
# print(abspath(dirname(__file__)))
pc = importlib.import_module(f"precompile3{PYTHON_VERSION[1]}")


def transformer_temperature_rise_power(S, Smax, Trr=85, n=1):
    """Assume transformers are working in norminal voltage
    :param S: actual S magnitude
    :param Smax: max S
    :param Trr: rated temperature rise
    :param n: 0.7 for sealed transformers, 0.8 for self-cooled transformers, and
        1.0 for forced air-cooled transformers
    :return temperature rise
    """
    return Trr * np.power(S / Smax, n)


@dispatch
def transformer_temperature_rise(I, Ir, Trr=85, n=1):
    """IEEE Std C57.12
    :param I: actual current
    :param Ir: rated current
    :param Trr: rated temperature rise
    :param n: 0.7 for sealed transformers, 0.8 for self-cooled transformers, and
        1.0 for forced air-cooled transformers
    :return temperature rise
    """
    return Trr * np.power(I/Ir, 2*n)


@dispatch
def transformer_temperature_rise(Pll, Pnl, Prll, Trr=85, n=1):
    """IEEE Std C57.110
    :param Pll: load loses
    :param Pnl: no-load losses
    :param Prll: rated losses
    :param Trr: rated temperature rise
    :param n: 0.7 for sealed transformers, 0.8 for self-cooled transformers, and
        1.0 for forced air-cooled transformers
    :return temperature rise
    """
    return Trr * np.power((Pll + Pnl)/(Prll + Pnl), n)


def corrected_transformer_resistance(T, Rref, Tref=25, S=0.1, Tf=225):
    """
    :param T: transformer temperature
    :param Tref: ref temperature
    :param Rref: ref resistance
    :param S:  fraction of transformer resistance attributable to stray loss. NEMA Std. TP-1
        assumes S = 0.10
    :param Tf: temperature constant, 234.5 for copper, 228.1 for hard-drawn aluminum
        and 225 for aluminum transformer windings
    """
    a = T + Tf
    b = Tref + Tf
    return Rref * ((1-S)*a/b + S*b/a)


def air_density(ambient_temperature, conductor_temperature, elevation):

    Tfilm = (conductor_temperature + ambient_temperature) / 2

    return (1.293 - 1.525e-4 * elevation + 6.379e-9 * elevation ** 2) / (
        1 + 0.00367 * Tfilm
    )


def natural_convection(
    ambient_temperature,
    conductor_diameter,
    conductor_temperature,
    elevation,
):
    n = len(conductor_temperature)
    res = np.zeros(n, dtype=float)
    nc = conductor_temperature > ambient_temperature
    res[nc] = 3.645 * np.power(air_density(ambient_temperature[nc], conductor_temperature[nc],
                                           elevation), 0.5) * conductor_diameter ** 0.75 * \
        np.power(conductor_temperature[nc] - ambient_temperature[nc], 1.25)
    return res


def convective_heat_loss(
    ambient_temperature,
    wind_speed,
    angle_of_attack,
    conductor_diameter,
    conductor_temperature,
    elevation,
):
    """The convective heat loss is the bigger of forced and natural convection
    From section 4.4.3 in the standard, page 10.
    """

    forced = pc.forced_convection(
        ambient_temperature,
        wind_speed,
        angle_of_attack,
        conductor_diameter,
        conductor_temperature,
        elevation,
    )

    natural = natural_convection(
        ambient_temperature, conductor_diameter, conductor_temperature, elevation
    )
    return np.maximum(forced, natural)


def heat_balance_equation(x, I, R_ref=2.25e-4, Ta=25, solar_irradiation=1027.7149, wind_speed=2,
                          angle_of_attack=90, elevation=25, D=28.1e-3, emmisivity=0.8, alpha=0.8,
                          R_T_high=8.688e-5, R_T_low=7.283e-5):
    """
    D:                     conductor diameter [m]
    emmisivity:            conductor emissivity
    alpha:                 conductor absortivity
    solar_irradiation:     in [W/m^2]
    """
    return convective_heat_loss(Ta, wind_speed, angle_of_attack, D, x, elevation) + \
        radiated_heat_loss(Ta, D, emmisivity, x) - pc.solar_heat_gain(solar_irradiation, alpha, D) - \
        I ** 2 * pc.corrected_resistance(x, R_ref, R_T_high, R_T_low)


def calculate_temperature_for_given_current(I=100, guess=25, Ta=25, R_ref=7.283e-5,
                                            solar_irradiation=1027.7149, wind_speed=2, tol=1e-5):
    """IEEE738 std and CIGRE601 Conductor resistance"""
    return newton(heat_balance_equation, guess, args=(I, R_ref, Ta, solar_irradiation, wind_speed), tol=tol)


def radiated_heat_loss(ambient_temperature, diameter, emmisivity, conductor_temperature):
    return (
        17.8
        * diameter
        * emmisivity
        * (
            np.power((conductor_temperature + 273) / 100,  4)
            - np.power((ambient_temperature + 273) / 100, 4)
        )
    )


def tdpf_loop(V, npv, npq, Sbus, pv, pq, pvpq, base, Cf, line_indexes, tc, r0, tas, rads, winds, rates, tran_indexes, tr0, r, x, c, tap, shift, f, t, i, nl, nb, Ct, Ysh, tol, maxiter):
    
    Ybus, Yf, Yt = generate_admittance_matrix(r, x, c, tap, shift, f, t, i, nl, nb, Cf, Ct,
                                              Ysh)
    it = 0

    while it < maxiter:

        # run power flow
        Vm, Va, Sbus, normF, itr = nrpf(V, npv, npq, Ybus, Sbus, pv, pq, pvpq,
                                        base)
        # compute line current
        V = Vm * np.exp(1j * Va)
        Vf = Cf * V
        If = Yf * V
        Sf = Vf * np.conj(If)*base
        I_lines = np.abs(If[line_indexes])

        # compute hbe residue
        res_hbe = heat_balance_equation(tc, I_lines, r0[line_indexes], tas[line_indexes], rads,
                                        winds)

        # compute transformer temperature rise residue
        tr = transformer_temperature_rise_power(
            np.abs(Sf[tran_indexes]), rates[tran_indexes])
        res_ttr = tr - tr0

        # check hbe equality
        if pc.converge(res_hbe, res_ttr, tol):
            break

        # compute Tc
        tc = calculate_temperature_for_given_current(I_lines, tc, tas[line_indexes],
                                                     r0[line_indexes], rads, winds)

        # update r
        r[line_indexes] = pc.corrected_resistance(tc, r0[line_indexes], R_T_high=8.688e-5, R_T_low=7.283e-5)

        r[tran_indexes] = corrected_transformer_resistance(
            tas[tran_indexes]+tr, r0[tran_indexes])

        # update Ybus and Yf
        Ybus, Yf, Yt = generate_admittance_matrix(
            r, x, c, tap, shift, f, t, i, nl, nb, Cf, Ct, Ysh)

        tr0 = tr
        it += 1
    return V, tc, tr, r, Yf, Yt, it
