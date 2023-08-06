'''
rate_eq:
submodule which solves 1st order rate equation and computes
the solution and signal

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''

from typing import Optional, Tuple
import numpy as np
import scipy.linalg as LA  # replace numpy.linalg to scipy.linalg
from .A_matrix import make_A_matrix, make_A_matrix_cauchy
from .A_matrix import make_A_matrix_gau, make_A_matrix_pvoigt


def solve_model(equation: np.ndarray,
                y0: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:

    '''
    Solve system of first order rate equation

    Args:
      equation: matrix corresponding to model
      y0: initial condition

    Returns:
       1. eigenvalues of equation
       2. eigenvectors for equation
       3. coefficient where y0 = Vc
    '''

    eigval, V = LA.eig(equation)
    c = LA.solve(V, y0)

    return eigval.real, V, c
  
def solve_l_model(equation: np.ndarray,
                y0: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:

    '''
    Solve system of first order rate equation where the rate equation matrix is
    lower triangle

    Args:
      equation: matrix corresponding to model
      y0: initial condition

    Returns:
       1. eigenvalues of equation
       2. eigenvectors for equation
       3. coefficient where y0 = Vc
    '''

    eigval = np.diagonal(equation)
    V = np.eye(eigval.size)
    c = np.zeros(eigval.size)
    tmp = np.zeros(eigval.size)

    for i in range(1, eigval.size):
      tmp[:i] = eigval[:i]-eigval[i]
      tmp[:i][tmp[:i] == 0] = 1
      V[i, :i] = equation[i,:i] @ V[:i,:i]/tmp[:i]

    c[0] = y0[0]
    for i in range(1, eigval.size):
      c[i] = y0[i] - np.dot(c[:i], V[i,:i])

    return eigval, V, c

def solve_seq_model(tau: np.ndarray, y0: np.ndarray):
    '''
    Solve sequential decay model
    
    sequential decay model: 
      0 -> 1 -> 2 -> 3 -> ... -> n 

    Args:
      tau: liftime constants for each decay
      y0: initial condition

    Returns:
       1. eigenvalues of equation
       2. eigenvectors for equation
       3. coefficient to match initial condition
    '''
    eigval = np.empty(tau.size+1)
    c = np.empty(eigval.size)
    V = np.eye(eigval.size)
    
    eigval[:-1] = -1/tau
    eigval[-1] = 0

    for i in range(1, eigval.size):
      V[i, :i] = V[i-1,:i]*eigval[i-1]/(eigval[i]-eigval[:i])
    
    c[0] = y0[0]
    for i in range(1, eigval.size):
      c[i] = y0[i]-np.dot(c[:i], V[i,:i])
    return eigval, V, c

def compute_model(t: np.ndarray,
                  eigval: np.ndarray,
                  V: np.ndarray,
                  c: np.ndarray) -> np.ndarray:

    '''
    Compute solution of the system of rate equations solved by solve_model
    Note: eigval, V, c should be obtained from solve_model

    Args:
     t: time
     eigval: eigenvalue for equation
     V: eigenvectors for equation
     c: coefficient

    Returns:
      solution of rate equation

    Note:
      eigval, V, c should be obtained from solve_model.
    '''

    A = make_A_matrix(t, -eigval)
    y = (c * V) @ A
    return y


def compute_signal_gau(t: np.ndarray,
                       fwhm: float,
                       eigval: np.ndarray,
                       V: np.ndarray,
                       c: np.ndarray) -> np.ndarray:

    '''
    Compute solution of the system of rate equations solved by solve_model
    convolved with normalized gaussian distribution

    Args:
     t: time
     fwhm: full width at half maximum of normalized gaussian distribution
     eigval: eigenvalue for equation
     V: eigenvectors for equation
     c: coefficient

    Returns:
      Convolution of solution of rate equation and normalized gaussian
      distribution

    Note:
      eigval, V, c should be obtained from solve_model.
    '''

    A = make_A_matrix_gau(t, fwhm, -eigval)
    y_signal = (c * V) @ A
    return y_signal


def compute_signal_cauchy(t: np.ndarray,
                          fwhm: float,
                          eigval: np.ndarray,
                          V: np.ndarray,
                          c: np.ndarray) -> np.ndarray:

    '''
    Compute solution of the system of rate equations solved by solve_model
    convolved with normalized cauchy distribution

    Args:
     t: time
     fwhm: full width at half maximum of normalized cauchy distribution
     eigval: eigenvalue for equation
     V: eigenvectors for equation
     c: coefficient

    Returns:
      Convolution of solution of rate equation and normalized cauchy
      distribution

    Note:
      eigval, V, c should be obtained from solve_model.
    '''

    A = make_A_matrix_cauchy(t, fwhm, -eigval)
    y_signal = (c * V) @ A
    return y_signal


def compute_signal_pvoigt(t: np.ndarray,
                          fwhm: float,
                          eta: float,
                          eigval: np.ndarray,
                          V: np.ndarray,
                          c: np.ndarray) -> np.ndarray:

    '''
    Compute solution of the system of rate equations solved by solve_model
    convolved with normalized pseudo voigt profile

    .. math::

       \\mathrm{pvoigt}(t) = (1-\\eta) G(t, {fwhm}) + \\eta L(t, {fwhm}),

    G(t) stands for normalized gaussian,
    L(t) stands for normalized cauchy(lorenzian) distribution

    Args:
     t: time
     fwhm: full width at half maximum of instrumental response function
     eta: mixing parameter
     eigval: eigenvalue for equation
     V: eigenvectors for equation
     c: coefficient

    Returns:
      Convolution of solution of rate equation and normalized pseudo
      voigt profile.

    Note:
      eigval, V, c should be obtained from solve_model.
    '''

    A = make_A_matrix_pvoigt(t, fwhm, eta, -eigval)
    y_signal = (c * V) @ A
    return y_signal

def compute_signal_irf(t: np.ndarray, eigval: np.ndarray, V: np.ndarray, c: np.ndarray, 
                       fwhm: float, irf: Optional[str] = 'g', eta: Optional[float] = None):

  if irf == 'g':
    A = make_A_matrix_gau(t, fwhm, -eigval)

  elif irf == 'c':
    A = make_A_matrix_cauchy(t, fwhm, -eigval)

  elif irf == 'pv':
    A = make_A_matrix_pvoigt(t, fwhm, eta, -eigval)

  return (c * V) @ A

def fact_anal_model(model: np.ndarray, exclude: Optional[str] = None, 
intensity: Optional[np.ndarray] = None, eps: Optional[np.ndarray] = None):

  abs = np.zeros(model.shape[0])

  if eps is None:
    eps = np.ones_like(intensity)
  
  y = intensity/eps

  if exclude == 'first':
    B = np.einsum('j,ij->ij', 1/eps, model[1:, :])
  elif exclude == 'last':
    B = np.einsum('j,ij->ij', 1/eps, model[:-1,:])
  elif exclude == 'first_and_last':
    B = np.einsum('j,ij->ij', 1/eps, model[1:-1,:])
  else:
    B = np.einsum('j,ij->ij', 1/eps, model)
  
  coeff, _, _, _  = LA.lstsq(B.T, y, cond=1e-2)

  if exclude == 'first':
    abs[1:] = coeff
  elif exclude == 'last':
    abs[:-1] = coeff
  elif exclude == 'first_and_last':
    abs[1:-1] = coeff
  else:
    abs = coeff

  return abs



