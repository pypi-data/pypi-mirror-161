'''
A_matrix:
submodule for evaluation of A_matrix

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''
from typing import Optional
import numpy as np
from scipy.linalg import lstsq
from .exp_conv_irf import exp_conv_gau, exp_conv_cauchy
from .exp_conv_irf import exp_mod_gau_cplx, dmp_osc_conv_cauchy_pair


def make_A_matrix(t: np.ndarray, k: np.ndarray) -> np.ndarray:

    A = np.empty((k.size, t.size))
    for i in range(k.size):
        A[i, :] = np.exp(-k[i]*t)
    A = A*np.heaviside(t, 1)
    A[np.isnan(A)] = 0

    return A


def make_A_matrix_gau(t: np.ndarray, fwhm: float,
                      k: np.ndarray) -> np.ndarray:

    A = np.empty((k.size, t.size))
    for i in range(k.size):
        A[i, :] = exp_conv_gau(t, fwhm, k[i])

    return A

def make_A_matrix_cauchy(t: np.ndarray, fwhm: float,
                         k: np.ndarray) -> np.ndarray:

    A = np.empty((k.size, t.size))
    for i in range(k.size):
        A[i, :] = exp_conv_cauchy(t, fwhm, k[i])

    return A


def make_A_matrix_pvoigt(t: np.ndarray,
                         fwhm: float,
                         eta: float,
                         k: np.ndarray) -> np.ndarray:
    
    u = make_A_matrix_gau(t, fwhm, k)
    v = make_A_matrix_cauchy(t, fwhm, k)

    return u + eta*(v-u)

def make_A_matrix_exp(t: np.ndarray,
                      fwhm: float,
                      tau: np.ndarray,
                      base: Optional[bool] = True,
                      irf: Optional[str] = 'g',
                      eta: Optional[float] = None
                      ) -> np.ndarray:
    
    if base:
        k = np.empty(tau.size+1)
        k[-1] = 0; k[:-1] = 1/tau
    else:
        k = 1/tau

    if irf == 'g':
        A = make_A_matrix_gau(t, fwhm, k)
    elif irf == 'c':
        A = make_A_matrix_cauchy(t, fwhm, k)
    else:
        A = make_A_matrix_pvoigt(t, fwhm, eta, k)

    return A

def make_A_matrix_gau_osc(t: np.ndarray, fwhm: float,
k: np.ndarray, T: np.ndarray) -> np.ndarray:

    sigma = fwhm/(2*np.sqrt(2*np.log(2)))
    A = np.empty((2*k.size, t.size))
    for i in range(k.size):
        A[i, :], A[i+k.size, :] = \
            exp_mod_gau_cplx(t, sigma, k[i], 2*np.pi/T[i])
        # cosine, sine
    return A

def make_A_matrix_cauchy_osc(t: np.ndarray, fwhm: float,
k: np.ndarray, T: np.ndarray) -> np.ndarray:

    A = np.empty((2*k.size, t.size))
    for i in range(k.size):
        A[i, :], A[i+k.size, :] = \
            dmp_osc_conv_cauchy_pair(t, fwhm, k[i], T[i])
    return A

def make_A_matrix_pvoigt_osc(t: np.ndarray, fwhm: float, eta: float,
                             k: np.ndarray, 
                             T: np.ndarray) -> np.ndarray:
    
    u = make_A_matrix_gau_osc(t, fwhm, k, T)
    v = make_A_matrix_cauchy_osc(t, fwhm, k, T)

    return u + eta*(v-u)

def make_A_matrix_dmp_osc(t: np.ndarray, fwhm: float,
                      tau: np.ndarray,
                      T: np.ndarray,
                      irf: Optional[str] = 'g',
                      eta: Optional[float] = None
                      ) -> np.ndarray:


    if irf == 'g':
        A = make_A_matrix_gau_osc(t, fwhm, 1/tau, T)
    elif irf == 'c':
        A = make_A_matrix_cauchy_osc(t, fwhm, 1/tau, T)
    elif irf == 'pv':
        A = make_A_matrix_pvoigt_osc(t, fwhm, eta, 1/tau, T)

    return A

def fact_anal_A(A: np.ndarray, 
                intensity: Optional[np.ndarray] = None, 
                eps: Optional[np.ndarray] = None) -> np.ndarray:

    if eps is None:
        eps = np.ones_like(intensity)
    
    B = np.einsum('j,ij->ij', 1/eps, A)
    y = intensity/eps
    
    c, _, _, _ = lstsq(B.T, y, cond=1e-2)
    return c
