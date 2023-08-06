'''
ads:
submodule for driver routine of associated difference spectrum

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''

from typing import Optional, Tuple 
import numpy as np
from scipy.linalg import svd
from ..mathfun.A_matrix import make_A_matrix_exp
from ..mathfun.rate_eq import compute_signal_irf

def dads(escan_time: np.ndarray, fwhm: float, tau: np.ndarray, base: Optional[bool] = True,
irf: Optional[str] = 'g', eta: Optional[float] = None,
intensity: Optional[np.ndarray] = None, eps: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    '''
    Calculate decay associated difference spectrum from experimental energy scan data

    Args:
      escan_time: time delay for each energy scan data
      fwhm: full width at half maximum of instrumental response function
      tau: life time for each component
      base: whether or not include baseline [default: True]
      irf: shape of instrumental response function [default: g]

           * 'g': normalized gaussian distribution,
           * 'c': normalized cauchy distribution,
           * 'pv': pseudo voigt profile :math:`(1-\\eta)g(t, {fwhm}) + \\eta c(t, {fwhm})`

      eta: mixing parameter for pseudo voigt profile
           (only needed for pseudo voigt profile)
      intensity: intensity of energy scan dataset
      eps: standard error of dataset
    
    Returns:
     Tuple of calculated decay associated difference spectrum of each component, estimated error and
     retrieved energy scan intensity from dads and decay components
    
    Note:
     To calculate decay associated difference spectrum of n component exponential decay, you should measure at least n+1
     energy scan
    '''
    # initialization
    if base:
      c = np.empty((tau.size+1, intensity.shape[0]))
      dof = escan_time.size - (tau.size+1)
    else:
      c = np.empty((tau.size, intensity.shape[0]))
      dof = escan_time.size - (tau.size)

    if eps is None:
      eps = np.ones_like(intensity)
    
    c_eps = np.empty_like(c)
    
    A = make_A_matrix_exp(escan_time, fwhm, tau, base, irf, eta)
    data_scaled = intensity/eps

    # evaluates dads
    cond = 1e-2
    for i in range(intensity.shape[0]):
      A_scaled = np.einsum('j,ij->ij', 1/eps[i,:], A)
      U, s, Vh = svd(A_scaled.T, full_matrices= False)
      mask = s > cond*s[0]
      U_turn = U[:,mask]; s_turn = s[mask]; Vh_turn = Vh[mask, :]
      c[:,i] = np.einsum('j,ij->ij', 1/s_turn, Vh_turn.T) @ (U_turn.T @ data_scaled[i,:])
      res = data_scaled[i,:] - (c[:,i] @ A_scaled)
      if dof != 0:
        red_chi2 = np.sum(res**2)/dof
        cov = Vh_turn.T @ np.einsum('i,ij->ij', 1/s_turn**2, Vh_turn)
        c_eps[:,i] = np.sqrt(red_chi2*np.diag(cov))


    return c, c_eps, c.T @ A

def sads(escan_time: np.ndarray, fwhm: float, eigval: np.ndarray, V: np.ndarray, c: np.ndarray,
exclude: Optional[str] = None, irf: Optional[str] = 'g', eta: Optional[float] = None,
intensity: Optional[np.ndarray] = None, eps: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    '''
    Calculate species associated difference spectrum from experimental energy scan data

    Args:
      escan_time: time delay for each energy scan data
      fwhm: full width at half maximum of instrumental response function
      eigval: eigenvalue of rate equation matrix 
      V: eigenvector of rate equation matrix 
      c: coefficient to match initial condition of rate equation
      exclude: exclude either 'first' or 'last' element or both 'first' and 'last' element.

               * 'first' : exclude first element
               * 'last' : exclude last element
               * 'first_and_last' : exclude both first and last element  
               * None : Do not exclude any element [default]

      irf: shape of instrumental response function [default: g]

           * 'g': normalized gaussian distribution,
           * 'c': normalized cauchy distribution,
           * 'pv': pseudo voigt profile :math:`(1-\\eta)g(t, {fwhm}) + \\eta c(t, {fwhm})`
           
      eta: mixing parameter for pseudo voigt profile (only needed for pseudo voigt profile)
      intensity: intensity of energy scan dataset
      eps: standard error of data 
    
    Returns:
     Tuple of calculated species associated difference spectrum of each component, estimated error and
     retrieved intensity of energy scan from sads and model excited state components
    
    Note:
     1. eigval, V, c should be obtained from solve_model
     2. To calculate species associated difference spectrum of n excited state species, you should measure at least n+1 energy scan
     3. Difference spectrum of ground state is zero, so ground state species should be excluded from rate equation or via exclude option.
    '''
    # initialization
    if exclude is None:
      abs = np.empty((eigval.size, intensity.shape[0]))
      dof = escan_time.size - eigval.size
    elif exclude in ['first', 'last']:
      abs = np.empty((eigval.size-1, intensity.shape[0]))
      dof = escan_time.size - (eigval.size-1)
    else:
      abs = np.empty((eigval.size-2, intensity.shape[0]))
      dof = escan_time.size - (eigval.size-2)

    if eps is None:
      eps = np.ones_like(intensity)
    
    abs_eps = np.empty_like(abs)
    
    A = compute_signal_irf(escan_time, eigval, V, c, fwhm, irf, eta)
    if exclude == 'first':
      B = A[1:, :]
    elif exclude == 'last':
      B = A[:-1, :]
    elif exclude == 'first_and_last':
      B = A[1:-1, :]
    else:
      B = A

    data_scaled = intensity/eps

    # evaluates sads
    cond = 1e-2
    for i in range(intensity.shape[0]):
      A_scaled = np.einsum('j,ij->ij', 1/eps[i,:], B)
      U, s, Vh = svd(A_scaled.T, full_matrices= False)
      mask = s > cond*s[0]
      U_turn = U[:,mask]; s_turn = s[mask]; Vh_turn = Vh[mask, :]
      cov = Vh_turn.T @ np.einsum('i,ij->ij', 1/s_turn**2, Vh_turn)
      abs[:,i] = np.einsum('j,ij->ij', 1/s_turn, Vh_turn.T) @ (U_turn.T @ data_scaled[i,:])
      res = data_scaled[i,:] - (abs[:,i] @ A_scaled)
      if dof != 0:
        red_chi2 = np.sum(res**2)/dof
        abs_eps[:,i] = np.sqrt(red_chi2*np.diag(cov))


    return abs, abs_eps, abs.T @ B